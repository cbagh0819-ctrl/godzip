"""GODZIP Adaptive Search: Universal lossless compression across all media and file formats."""

from typing import List, Tuple
from ..common.constants import (
    CompressionMode,
    CODEC_ID_STORE,
    CODEC_ID_ZSTD,
    CODEC_ID_LZMA2,
    CODEC_ID_BROTLI,
    CODEC_ID_DEFLATE,
    CODEC_ID_LZ4,
    CODEC_ID_NEURAL_CONTEXT,
)
from ..codecs.registry import CodecRegistry
from ..analyzer.analyzer import ContentProfile


class AdaptiveSearchEngine:
    """Evaluates data profiles and empirically selects the most compact lossless codec.
    
    Guarantees that files in ANY format (images, audio, video, documents, code, binaries)
    are actively tested for compression, falling back to STORE only if compression would expand the data.
    """

    @staticmethod
    def get_candidate_configurations(profile: ContentProfile, mode: CompressionMode) -> List[Tuple[int, int]]:
        """Returns list of (codec_id, level) to test based on content profile and mode."""
        rec = profile.recommended_class

        if mode == CompressionMode.FAST:
            if rec == "REPETITIVE":
                return [(CODEC_ID_LZ4, 0), (CODEC_ID_ZSTD, 3)]
            elif rec in ("IMAGE", "AUDIO", "VIDEO"):
                return [(CODEC_ID_ZSTD, 3), (CODEC_ID_LZ4, 0)]
            elif rec == "TEXT":
                return [(CODEC_ID_ZSTD, 3)]
            else:
                return [(CODEC_ID_ZSTD, 3), (CODEC_ID_LZ4, 0)]

        elif mode == CompressionMode.BALANCED:
            if rec == "IMAGE":
                # Images: test Zstandard, LZMA2, and Brotli
                return [
                    (CODEC_ID_ZSTD, 9),
                    (CODEC_ID_LZMA2, 6),
                    (CODEC_ID_BROTLI, 6),
                ]
            elif rec == "AUDIO":
                # Audio: PCM/WAV/AIFF compress well with LZMA2/Zstd
                return [
                    (CODEC_ID_ZSTD, 9),
                    (CODEC_ID_LZMA2, 6),
                    (CODEC_ID_DEFLATE, 9),
                ]
            elif rec == "VIDEO":
                # Video containers: Zstd-9 & LZMA2-6 for frames & metadata
                return [
                    (CODEC_ID_ZSTD, 9),
                    (CODEC_ID_LZMA2, 6),
                ]
            elif rec == "TEXT":
                return [
                    (CODEC_ID_ZSTD, 6),
                    (CODEC_ID_BROTLI, 6),
                    (CODEC_ID_LZMA2, 6),
                ]
            elif rec == "REPETITIVE":
                return [
                    (CODEC_ID_LZ4, 3),
                    (CODEC_ID_ZSTD, 6),
                    (CODEC_ID_LZMA2, 6),
                ]
            else:
                return [
                    (CODEC_ID_ZSTD, 9),
                    (CODEC_ID_LZMA2, 6),
                    (CODEC_ID_LZ4, 0),
                ]

        elif mode == CompressionMode.MAXIMUM:
            # In MAXIMUM mode, comprehensively test top high-ratio contenders
            # across ALL formats: images, videos, audio, text, binaries
            if rec in ("IMAGE", "AUDIO", "VIDEO", "BINARY_STRUCTURED", "ARCHIVE", "RANDOM"):
                return [
                    (CODEC_ID_ZSTD, 22),
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_BROTLI, 11),
                    (CODEC_ID_DEFLATE, 9),
                ]
            elif rec == "TEXT":
                return [
                    (CODEC_ID_ZSTD, 22),
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_BROTLI, 11),
                    (CODEC_ID_DEFLATE, 9),
                ]
            elif rec == "REPETITIVE":
                return [
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_ZSTD, 22),
                    (CODEC_ID_LZ4, 9),
                    (CODEC_ID_BROTLI, 11),
                ]
            else:
                return [
                    (CODEC_ID_ZSTD, 22),
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_BROTLI, 11),
                    (CODEC_ID_DEFLATE, 9),
                ]

        elif mode == CompressionMode.RESEARCH:
            candidates = [
                (CODEC_ID_ZSTD, 22),
                (CODEC_ID_LZMA2, 9),
                (CODEC_ID_BROTLI, 11),
            ]
            if rec in ("TEXT", "BINARY_STRUCTURED", "AUDIO", "IMAGE"):
                candidates.append((CODEC_ID_NEURAL_CONTEXT, 1))
            return candidates

        return [(CODEC_ID_ZSTD, 3)]

    @classmethod
    def choose_codec(cls, chunk: bytes, profile: ContentProfile, mode: CompressionMode) -> Tuple[int, int, bytes]:
        """Tests candidate codecs and returns (best_codec_id, best_level, compressed_payload).
        
        Guarantees:
        1. Actively tests compression on all file formats (images, audio, video, text, binary).
        2. Validates exact byte restoration on candidate output.
        3. If no codec compresses the data smaller than original size, falls back to STORE (zero expansion).
        """
        raw_size = len(chunk)
        if raw_size == 0:
            return CODEC_ID_STORE, 0, b""

        candidates = cls.get_candidate_configurations(profile, mode)

        best_size = raw_size
        best_choice = (CODEC_ID_STORE, 0, chunk)

        # In FAST mode, test first candidate quickly
        if mode == CompressionMode.FAST:
            for cid, lvl in candidates:
                try:
                    codec = CodecRegistry.get(cid)
                    comp = codec.compress(chunk, lvl)
                    if len(comp) < best_size:
                        decomp = codec.decompress(comp, raw_size)
                        if decomp == chunk:
                            return cid, lvl, comp
                except Exception:
                    continue
            return CODEC_ID_STORE, 0, chunk

        # In BALANCED, MAXIMUM, or RESEARCH mode, evaluate candidates and pick smallest
        for cid, lvl in candidates:
            try:
                codec = CodecRegistry.get(cid)
                compressed = codec.compress(chunk, lvl)
                
                # Only check if strictly smaller than current best
                if len(compressed) < best_size:
                    # Verify exact round-trip integrity on candidate
                    decompressed = codec.decompress(compressed, raw_size)
                    if decompressed == chunk:
                        best_size = len(compressed)
                        best_choice = (cid, lvl, compressed)
            except Exception:
                continue

        return best_choice
