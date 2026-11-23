import subprocess
import sys

from sandbox_runner import _collect_process_output


def test_collects_stdout_and_stderr_within_limit():
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import sys; print('result'); print('warning', file=sys.stderr)",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr, status = _collect_process_output(
        process,
        timeout_sec=2,
        max_output_bytes=1024,
    )

    assert process.wait(timeout=2) == 0
    assert status == "COMPLETED"
    assert b"result" in stdout
    assert b"warning" in stderr


def test_stops_collecting_when_combined_output_exceeds_limit():
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import sys; sys.stdout.write('x' * 8192); sys.stderr.write('y' * 8192)",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    _, _, status = _collect_process_output(
        process,
        timeout_sec=2,
        max_output_bytes=1024,
    )

    assert status == "OUTPUT_LIMIT_EXCEEDED"
    process.wait(timeout=2)


def test_reports_process_timeout():
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    _, _, status = _collect_process_output(
        process,
        timeout_sec=0.05,
        max_output_bytes=1024,
    )

    assert status == "TIMEOUT"
    process.kill()
    process.wait(timeout=2)
