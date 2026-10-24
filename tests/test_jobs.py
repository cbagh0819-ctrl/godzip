"""Tests verifying JobController background thread handling, cancellation, and callbacks."""

import os
import time
from godzip.common.constants import CompressionMode
from godzip.jobs.controller import JobController


def test_job_controller_compress_and_extract(temp_dir):
    src_file = os.path.join(temp_dir, "input.txt")
    with open(src_file, "wb") as fp:
        fp.write(b"Background worker test content\n" * 500)

    god_file = os.path.join(temp_dir, "output.god")
    dest_dir = os.path.join(temp_dir, "dest")

    controller = JobController()
    completed = []
    errors = []

    controller.start_compression(
        source_paths=[src_file],
        output_path=god_file,
        mode=CompressionMode.FAST,
        on_complete=lambda res: completed.append(res),
        on_error=lambda err: errors.append(err),
    )

    # Wait for completion
    timeout = 10.0
    start = time.time()
    while controller.is_running and (time.time() - start < timeout):
        time.sleep(0.05)

    assert not controller.is_running
    assert len(errors) == 0
    assert len(completed) == 1
    assert os.path.exists(god_file)

    # Test extraction
    completed.clear()
    controller.start_extraction(
        archive_path=god_file,
        destination_dir=dest_dir,
        on_complete=lambda res: completed.append(res),
        on_error=lambda err: errors.append(err),
    )

    start = time.time()
    while controller.is_running and (time.time() - start < timeout):
        time.sleep(0.05)

    assert not controller.is_running
    assert len(errors) == 0
    assert len(completed) == 1
