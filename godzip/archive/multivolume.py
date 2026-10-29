"""Multi-volume archive splitting and concatenation engine for GODZIP.

Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)
"""

import os
import re
import io
from typing import List, Optional, Tuple


PART_REGEX = re.compile(r"^(.*?)\.part(\d+)\.god$", re.IGNORECASE)


def get_part_filename(base_path: str, part_index: int, total_parts: int = 99) -> str:
    """Generate part filename like archive.part01.god.
    
    Args:
        base_path: Original path, e.g. /path/to/backup.god
        part_index: 1-based part index (1, 2, 3...)
        total_parts: Expected max parts for zero-padding
    """
    clean_base = base_path
    if clean_base.lower().endswith(".god"):
        clean_base = clean_base[:-4]
    
    # Strip any existing .partXX if present
    m = PART_REGEX.match(base_path)
    if m:
        clean_base = m.group(1)

    digits = 3 if total_parts > 99 else 2
    return f"{clean_base}.part{part_index:0{digits}d}.god"


def find_volume_parts(path: str) -> List[str]:
    """Find all ordered parts for a given archive path.
    
    If path is 'backup.part01.god' or 'backup.god', looks for all existing parts:
    ['backup.part01.god', 'backup.part02.god', ...]
    """
    path = os.path.abspath(path)
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)

    m = PART_REGEX.match(basename)
    if m:
        prefix = m.group(1).lower()
    else:
        prefix = basename[:-4].lower() if basename.lower().endswith(".god") else basename.lower()

    if not os.path.isdir(dirname):
        return [path] if os.path.exists(path) else []

    parts = []
    for f in os.listdir(dirname):
        fm = PART_REGEX.match(f)
        if fm and fm.group(1).lower() == prefix:
            part_num = int(fm.group(2))
            full_p = os.path.join(dirname, f)
            parts.append((part_num, full_p))

    if parts:
        parts.sort(key=lambda x: x[0])
        # Verify continuity starting from 1
        return [p[1] for p in parts]

    # Single archive fallback
    if os.path.exists(path):
        return [path]

    # Check if path.part01.god exists
    cand = get_part_filename(path, 1)
    if os.path.exists(cand):
        return find_volume_parts(cand)

    return []


class MultiVolumeStream(io.RawIOBase):
    """Unified seekable, readable stream spanning across multiple volume files."""

    def __init__(self, part_paths: List[str]):
        super().__init__()
        if not part_paths:
            raise ValueError("Part paths list cannot be empty")
        self.part_paths = [os.path.abspath(p) for p in part_paths]
        self.part_sizes = [os.path.getsize(p) for p in self.part_paths]
        self.total_size = sum(self.part_sizes)

        # Build cumulative start offsets
        self.part_offsets = []
        cur = 0
        for s in self.part_sizes:
            self.part_offsets.append(cur)
            cur += s

        self._pos = 0
        self._current_handle: Optional[io.BufferedReader] = None
        self._current_part_idx: int = -1

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def tell(self) -> int:
        return self._pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new_pos = offset
        elif whence == io.SEEK_CUR:
            new_pos = self._pos + offset
        elif whence == io.SEEK_END:
            new_pos = self.total_size + offset
        else:
            raise ValueError(f"Invalid whence value: {whence}")

        if new_pos < 0:
            raise ValueError("Cannot seek before start of stream")
        self._pos = new_pos
        return self._pos

    def _locate_part(self, pos: int) -> Tuple[int, int]:
        """Locate which part index and offset within that part corresponds to global pos."""
        if pos >= self.total_size:
            return len(self.part_paths) - 1, (self.part_sizes[-1] if self.part_sizes else 0)

        for i, (start, size) in enumerate(zip(self.part_offsets, self.part_sizes)):
            if start <= pos < start + size:
                return i, pos - start
        return len(self.part_paths) - 1, 0

    def _ensure_handle(self, part_idx: int, local_offset: int):
        if self._current_part_idx != part_idx:
            if self._current_handle:
                self._current_handle.close()
            self._current_handle = open(self.part_paths[part_idx], "rb")
            self._current_part_idx = part_idx
        self._current_handle.seek(local_offset)

    def read(self, size: int = -1) -> bytes:
        if self._pos >= self.total_size:
            return b""

        if size is None or size < 0:
            to_read = self.total_size - self._pos
        else:
            to_read = min(size, self.total_size - self._pos)

        if to_read <= 0:
            return b""

        chunks = []
        bytes_left = to_read

        while bytes_left > 0 and self._pos < self.total_size:
            part_idx, local_off = self._locate_part(self._pos)
            part_avail = self.part_sizes[part_idx] - local_off
            read_len = min(bytes_left, part_avail)

            self._ensure_handle(part_idx, local_off)
            buf = self._current_handle.read(read_len)
            if not buf:
                break

            chunks.append(buf)
            actual = len(buf)
            self._pos += actual
            bytes_left -= actual

        return b"".join(chunks)

    def close(self):
        if self._current_handle:
            self._current_handle.close()
            self._current_handle = None
            self._current_part_idx = -1
        super().close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MultiVolumeWriter:
    """Writes a continuous stream across split volume files with a size threshold."""

    def __init__(self, base_path: str, split_size: Optional[int] = None):
        self.base_path = os.path.abspath(base_path)
        self.split_size = split_size  # None or <=0 means single file
        self.part_paths: List[str] = []
        self.part_handles: List[io.BufferedWriter] = []
        self.current_part_index = 0
        self.total_bytes_written = 0
        self._is_closed = False

        if not self.split_size or self.split_size <= 0:
            # Single file mode
            self.temp_path = self.base_path + f".tmp.godzip.{os.getpid()}"
            self._active_fp = open(self.temp_path, "wb")
        else:
            # Multi-part mode
            self._active_fp = None
            self._open_next_part()

    def _open_next_part(self):
        if self._active_fp is not None:
            self._active_fp.flush()
            self._active_fp.close()

        self.current_part_index += 1
        part_name = get_part_filename(self.base_path, self.current_part_index)
        temp_part = part_name + f".tmp.godzip.{os.getpid()}"
        self.part_paths.append(part_name)
        self.part_handles.append(temp_part)
        self._active_fp = open(temp_part, "wb")
        self._current_part_bytes = 0

    def write(self, data: bytes) -> int:
        if self._is_closed:
            raise ValueError("I/O operation on closed MultiVolumeWriter")

        if not self.split_size or self.split_size <= 0:
            written = self._active_fp.write(data)
            self.total_bytes_written += written
            return written

        # Splitting mode
        total_len = len(data)
        offset = 0

        while offset < total_len:
            space_left = self.split_size - self._current_part_bytes
            if space_left <= 0:
                self._open_next_part()
                space_left = self.split_size

            to_write = min(total_len - offset, space_left)
            chunk = data[offset : offset + to_write]
            w = self._active_fp.write(chunk)
            self._current_part_bytes += w
            self.total_bytes_written += w
            offset += w

        return total_len

    def tell(self) -> int:
        return self.total_bytes_written

    def seek(self, pos: int, whence: int = io.SEEK_SET):
        """Allows seeking back to offset 0 to write the header into Part 1."""
        if whence != io.SEEK_SET:
            raise NotImplementedError("MultiVolumeWriter only supports SEEK_SET seek")

        if pos == 0:
            # Flush and close active part if needed
            if self._active_fp:
                self._active_fp.flush()
                self._active_fp.close()

            # If multi-volume, re-open part 1 in r+b
            if self.split_size and self.split_size > 0:
                part1_temp = self.part_handles[0]
                self._active_fp = open(part1_temp, "r+b")
                self._active_fp.seek(0)
            else:
                self._active_fp = open(self.temp_path, "r+b")
                self._active_fp.seek(0)
        else:
            raise NotImplementedError("Arbitrary non-zero seek on MultiVolumeWriter not required")

    def close(self):
        if self._is_closed:
            return
        if self._active_fp:
            self._active_fp.flush()
            self._active_fp.close()
            self._active_fp = None
        self._is_closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.cleanup_temps()
        else:
            self.close()

    def commit(self) -> List[str]:
        """Atomically rename all temp files to their final destination names."""
        self.close()
        final_files: List[str] = []

        if not self.split_size or self.split_size <= 0:
            if os.path.exists(self.base_path):
                os.remove(self.base_path)
            os.replace(self.temp_path, self.base_path)
            final_files.append(self.base_path)
        else:
            for temp_p, final_p in zip(self.part_handles, self.part_paths):
                if os.path.exists(final_p):
                    os.remove(final_p)
                os.replace(temp_p, final_p)
                final_files.append(final_p)

        return final_files

    def cleanup_temps(self):
        """Remove any dangling temp files on error or cancellation."""
        self.close()
        if not self.split_size or self.split_size <= 0:
            if hasattr(self, "temp_path") and os.path.exists(self.temp_path):
                try:
                    os.remove(self.temp_path)
                except OSError:
                    pass
        else:
            for temp_p in self.part_handles:
                if os.path.exists(temp_p):
                    try:
                        os.remove(temp_p)
                    except OSError:
                        pass
