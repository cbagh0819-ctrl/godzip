"""GODZIP Adaptive Search: Intelligent candidate selection and trial evaluation."""

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
    """Evaluates data profiles and empirically selects the most compact lossless codec."""

    @staticmethod
    def get_candidate_configurations(profile: ContentProfile, mode: CompressionMode) -> List[Tuple[int, int]]:
        """Returns list of (codec_id, level) to test based on content profile and mode."""
        # If precompressed or high entropy random binary, always prefer STORE or fast Zstd-1
        if profile.likely_precompressed or profile.recommended_class in ("PRECOMPRESSED", "RANDOM"):
            if mode == CompressionMode.FAST:
                return [(CODEC_ID_STORE, 0)]
            elif mode == CompressionMode.BALANCED:
                return [(CODEC_ID_STORE, 0), (CODEC_ID_ZSTD, 1)]
            else:
                return [(CODEC_ID_STORE, 0), (CODEC_ID_ZSTD, 1), (CODEC_ID_LZ4, 0)]

        if mode == CompressionMode.FAST:
            if profile.recommended_class == "REPETITIVE":
                return [(CODEC_ID_LZ4, 0)]
            return [(CODEC_ID_ZSTD, 3)]

        elif mode == CompressionMode.BALANCED:
            if profile.recommended_class == "TEXT":
                return [(CODEC_ID_ZSTD, 6), (CODEC_ID_BROTLI, 6)]
            elif profile.recommended_class == "REPETITIVE":
                return [(CODEC_ID_LZ4, 3), (CODEC_ID_ZSTD, 3)]
            else:
                return [(CODEC_ID_ZSTD, 9), (CODEC_ID_LZMA2, 4)]

        elif mode == CompressionMode.MAXIMUM:
            # In MAXIMUM mode, comprehensively test top contenders
            if profile.recommended_class == "TEXT":
                return [
                    (CODEC_ID_ZSTD, 19),
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_BROTLI, 11),
                    (CODEC_ID_DEFLATE, 9),
                ]
            elif profile.recommended_class == "REPETITIVE":
                return [
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_ZSTD, 19),
                    (CODEC_ID_LZ4, 9),
                ]
            else:
                return [
                    (CODEC_ID_ZSTD, 19),
                    (CODEC_ID_LZMA2, 9),
                    (CODEC_ID_DEFLATE, 9),
                ]

        elif mode == CompressionMode.RESEARCH:
            candidates = [
                (CODEC_ID_ZSTD, 19),
                (CODEC_ID_LZMA2, 9),
                (CODEC_ID_BROTLI, 11),
            ]
            if profile.recommended_class in ("TEXT", "BINARY_STRUCTURED"):
                candidates.append((CODEC_ID_NEURAL_CONTEXT, 1))
            return candidates

        return [(CODEC_ID_ZSTD, 3)]

    @classmethod
    def choose_codec(cls, chunk: bytes, profile: ContentProfile, mode: CompressionMode) -> Tuple[int, int, bytes]:
        """Tests candidate codecs and returns (best_codec_id, best_level, compressed_payload).
        
        Guarantees that if no candidate compresses data smaller than raw size,
        returns (CODEC_ID_STORE, 0, chunk).
        """
        raw_size = len(chunk)
        if raw_size == 0:
            return CODEC_ID_STORE, 0, b""

        # In FAST mode, immediately compress with single chosen candidate
        if mode == CompressionMode.FAST:
            candidates = cls.get_candidate_configurations(profile, mode)
            cid, lvl = candidates[0]
            if cid == CODEC_ID_STORE:
                return CODEC_ID_STORE, 0, chunk
            codec = CodecRegistry.get(cid)
            try:
                compressed = codec.compress(chunk, lvl)
                if len(compressed) < raw_size:
                    return cid, lvl, compressed
            except Exception:
                pass
            return CODEC_ID_STORE, 0, chunk

        candidates = cls.get_candidate_configurations(profile, mode)
        best_size = raw_size
        best_choice = (CODEC_ID_STORE, 0, chunk)

        # In MAXIMUM / BALANCED mode, evaluate candidates
        for cid, lvl in candidates:
            if cid == CODEC_ID_STORE:
                continue
            try:
                codec = CodecRegistry.get(cid)
                compressed = codec.compress(chunk, lvl)
                # Verify exact round-trip integrity on candidate
                decompressed = codec.decompress(compressed, raw_size)
                if decompressed != chunk:
                    continue # Discard if not byte-exact!
                
                # Check if it strictly beats current best
                if len(compressed) < best_size:
                    best_size = len(compressed)
                    best_choice = (cid, lvl, compressed)
            except Exception:
                continue

        return best_choice
