"""Job controller managing asynchronous compression and extraction execution."""

import threading
import time
from typing import Callable, Optional, Dict, Any
from ..common.constants import CompressionMode
from ..common.types import JobProgress
from ..common.exceptions import JobCancelledError
from ..archive.writer import ArchiveWriter
from ..archive.reader import ArchiveReader


class JobController:
    """Coordinates compression/extraction workers, progress dispatch, and cancellation."""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._is_cancelled = False
        self._is_running = False
        self._last_progress: Optional[JobProgress] = None
        self._error: Optional[str] = None
        self._result: Optional[Dict[str, Any]] = None

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    @property
    def last_progress(self) -> Optional[JobProgress]:
        return self._last_progress

    @property
    def error(self) -> Optional[str]:
        return self._error

    @property
    def result(self) -> Optional[Dict[str, Any]]:
        return self._result

    def cancel(self) -> None:
        """Signals active job to abort safely."""
        self._is_cancelled = True

    def _cancel_check(self) -> bool:
        return self._is_cancelled

    def start_compression(
        self,
        source_paths: list,
        output_path: str,
        mode: CompressionMode = CompressionMode.BALANCED,
        enable_dedup: bool = True,
        password: Optional[str] = None,
        split_size: Optional[int] = None,
        on_progress: Optional[Callable[[JobProgress], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        if self._is_running:
            raise RuntimeError("A job is already in progress")

        self._is_cancelled = False
        self._is_running = True
        self._error = None
        self._result = None

        def worker():
            start_time = time.time()
            try:
                def progress_handler(p: JobProgress):
                    self._last_progress = p
                    if on_progress:
                        on_progress(p)

                writer = ArchiveWriter(
                    output_path=output_path,
                    mode=mode,
                    enable_dedup=enable_dedup,
                    password=password,
                    split_size=split_size,
                    progress_callback=progress_handler,
                    cancel_check=self._cancel_check,
                )
                orig_bytes, comp_bytes = writer.add_sources(source_paths)
                elapsed = time.time() - start_time
                ratio = (orig_bytes / comp_bytes) if comp_bytes > 0 else 1.0

                res = {
                    "action": "compress",
                    "output_path": output_path,
                    "original_bytes": orig_bytes,
                    "compressed_bytes": comp_bytes,
                    "ratio": round(ratio, 2),
                    "elapsed_seconds": round(elapsed, 2),
                }
                self._result = res
                if on_complete:
                    on_complete(res)
            except JobCancelledError:
                self._error = "Job cancelled by user"
                if on_error:
                    on_error(self._error)
            except Exception as e:
                self._error = str(e)
                if on_error:
                    on_error(self._error)
            finally:
                self._is_running = False

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def start_extraction(
        self,
        archive_path: str,
        destination_dir: str,
        password: Optional[str] = None,
        on_progress: Optional[Callable[[JobProgress], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        if self._is_running:
            raise RuntimeError("A job is already in progress")

        self._is_cancelled = False
        self._is_running = True
        self._error = None
        self._result = None

        def worker():
            start_time = time.time()
            try:
                def progress_handler(p: JobProgress):
                    self._last_progress = p
                    if on_progress:
                        on_progress(p)

                reader = ArchiveReader(archive_path, password=password)
                bytes_extracted = reader.extract(
                    destination_dir=destination_dir,
                    progress_callback=progress_handler,
                    cancel_check=self._cancel_check,
                )
                elapsed = time.time() - start_time
                res = {
                    "action": "extract",
                    "archive_path": archive_path,
                    "destination": destination_dir,
                    "bytes_extracted": bytes_extracted,
                    "elapsed_seconds": round(elapsed, 2),
                }
                self._result = res
                if on_complete:
                    on_complete(res)
            except JobCancelledError:
                self._error = "Job cancelled by user"
                if on_error:
                    on_error(self._error)
            except Exception as e:
                self._error = str(e)
                if on_error:
                    on_error(self._error)
            finally:
                self._is_running = False

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()
