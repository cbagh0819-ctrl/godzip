"""Statistical content analysis and entropy estimation."""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
from .signatures import detect_signature, is_likely_precompressed


@dataclass
class ContentProfile:
    shannon_entropy: float        # Bits per byte (0.0 to 8.0)
    ascii_ratio: float            # Fraction of printable ASCII characters
    zero_ratio: float             # Fraction of zero (0x00) bytes
    unique_byte_count: int        # Number of unique byte values (1 to 256)
    detected_format: str          # Detected magic file format or 'unknown'
    likely_precompressed: bool    # True if known compressed format or near-maximum entropy
    recommended_class: str        # 'TEXT', 'BINARY_STRUCTURED', 'REPETITIVE', 'RANDOM', 'PRECOMPRESSED'


class ContentAnalyzer:
    """Analyzes data characteristics to guide adaptive codec selection."""

    @staticmethod
    def analyze(data: bytes, sample_limit: int = 131072) -> ContentProfile:
        """Examines up to sample_limit bytes of input data and computes statistical metrics."""
        if not data:
            return ContentProfile(
                shannon_entropy=0.0,
                ascii_ratio=0.0,
                zero_ratio=0.0,
                unique_byte_count=0,
                detected_format="empty",
                likely_precompressed=False,
                recommended_class="REPETITIVE"
            )

        sample = data[:sample_limit]
        n = len(sample)

        # Count byte frequencies
        freq: Dict[int, int] = {}
        zero_count = 0
        printable_ascii = 0

        for b in sample:
            freq[b] = freq.get(b, 0) + 1
            if b == 0:
                zero_count += 1
            # Printable ASCII: 0x20..0x7E, plus tab (0x09), newline (0x0A), carriage return (0x0D)
            if (0x20 <= b <= 0x7E) or b in (0x09, 0x0A, 0x0D):
                printable_ascii += 1

        # Calculate Shannon entropy: H = -sum(p * log2(p))
        entropy = 0.0
        for count in freq.values():
            p = count / n
            entropy -= p * math.log2(p)

        ascii_ratio = printable_ascii / n
        zero_ratio = zero_count / n
        unique_bytes = len(freq)

        detected_fmt = detect_signature(data) or "unknown"
        is_precompressed = is_likely_precompressed(data)

        # Classify data
        if is_precompressed or (entropy > 7.96 and unique_bytes >= 250):
            recommended_class = "PRECOMPRESSED"
        elif entropy > 7.92 and ascii_ratio < 0.15:
            recommended_class = "RANDOM"
        elif ascii_ratio > 0.82:
            recommended_class = "TEXT"
        elif zero_ratio > 0.35 or entropy < 4.0:
            recommended_class = "REPETITIVE"
        else:
            recommended_class = "BINARY_STRUCTURED"

        return ContentProfile(
            shannon_entropy=round(entropy, 4),
            ascii_ratio=round(ascii_ratio, 4),
            zero_ratio=round(zero_ratio, 4),
            unique_byte_count=unique_bytes,
            detected_format=detected_fmt,
            likely_precompressed=is_precompressed or recommended_class in ("PRECOMPRESSED", "RANDOM"),
            recommended_class=recommended_class
        )
