"""Nacrith neural compression research adapter and reproducibility evaluation."""

import os
import shutil
from typing import Dict, Any, Optional

class NacrithAdapter:
    """Interfaces with external or local Nacrith neural compressor implementations."""

    def __init__(self, binary_path: Optional[str] = None):
        self.binary_path = binary_path or shutil.which("nacrith")

    def is_available(self) -> bool:
        """Checks if Nacrith GPU binary is present in path or configured location."""
        return self.binary_path is not None and os.path.exists(self.binary_path)

    def evaluate_model_overhead(self, raw_data_size: int, model_weights_size: int = 25 * 1024 * 1024) -> Dict[str, Any]:
        """Calculates effective compression ratio taking standalone model distribution into account."""
        return {
            "raw_size_bytes": raw_data_size,
            "model_overhead_bytes": model_weights_size,
            "requires_standalone_model": True,
            "amortization_threshold_bytes": model_weights_size * 5, # Requires at least 125 MB file to amortize
            "notes": "Without pre-distributed weights, neural compression yields net negative compression on small/medium files."
        }
