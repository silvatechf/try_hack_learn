import json
import os
import selectors
import subprocess
import time


MAX_SANDBOX_OUTPUT_BYTES = 64 * 1024
DOCKER_STOP_TIMEOUT_SECONDS = 5


def _collect_process_output(
    process: subprocess.Popen,
    timeout_sec: int,
    max_output_bytes: int = MAX_SANDBOX_OUTPUT_BYTES,
) -> tuple[bytes, bytes, str]:
    """Drain stdout/stderr concurrently with a combined byte ceiling.

    Returns (stdout, stderr, status), where status is COMPLETED,
    TIMEOUT, or OUTPUT_LIMIT_EXCEEDED.
    """
    stdout = bytearray()
    stderr = bytearray()
    total_bytes = 0
    deadline = time.monotonic() + timeout_sec

    with selectors.DefaultSelector() as selector:
        if process.stdout is not None:
            selector.register(process.stdout, selectors.EVENT_READ, stdout)
        if process.stderr is not None:
            selector.register(process.stderr, selectors.EVENT_READ, stderr)

        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return bytes(stdout), bytes(stderr), "TIMEOUT"

            for key, _ in selector.select(min(remaining, 0.1)):
                chunk = os.read(key.fileobj.fileno(), min(4096, max_output_bytes + 1 - total_bytes))
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue

                total_bytes += len(chunk)
                key.data.extend(chunk)

                if total_bytes > max_output_bytes:
                    return bytes(stdout), bytes(stderr), "OUTPUT_LIMIT_EXCEEDED"

    return bytes(stdout), bytes(stderr), "COMPLETED"


def _stop_container(container_name: str) -> None:
    try:
        subprocess.run(
            ["docker", "stop", "-t", "1", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=DOCKER_STOP_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def _terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def run_in_sandbox(
    student_code: str,
    exercise_tests: list,
    timeout_sec: int = 3,
) -> dict:
    student_code_json = json.dumps(student_code)
    tests_json = json.dumps(exercise_tests)

    harness_code = f"""
import json
import sys

student_code = json.loads({student_code_json!r})
tests = json.loads({tests_json!r})

student_globals = {{}}

try:
    exec(student_code, student_globals)

    if "solve" not in student_globals:
        print(json.dumps({{
            "status": "ERROR",
            "message": "Function 'solve' not defined."
        }}))
        sys.exit(0)

    solve_fn = student_globals["solve"]
    results = []
    passed_all = True

    for i, test in enumerate(tests):
        inp = test["input"]
        expected = test["expected"]

        try:
            res = solve_fn(inp)
            passed = res == expected

            if not passed:
                passed_all = False

            results.append({{
                "test_idx": i,
                "passed": passed,
                "output": res,
                "expected": expected
            }})

        except Exception as e:
            passed_all = False

            results.append({{
                "test_idx": i,
                "passed": False,
                "error": str(e)
            }})

    print(json.dumps({{
        "status": "SUCCESS",
        "passed_all": passed_all,
        "results": results
    }}))

except SyntaxError as e:
    print(json.dumps({{
        "status": "COMPILATION_ERROR",
        "message": str(e)
    }}))

except Exception as e:
    print(json.dumps({{
        "status": "RUNTIME_ERROR",
        "message": str(e)
    }}))
"""

    container_name = f"python_sandbox_{int(time.time() * 1000)}"

    cmd = [
        "docker",
        "run",
        "--name",
        container_name,
        "--rm",
        "-i",
        "--network",
        "none",
        "--read-only",
        "--tmpfs",
        "/var/run:rw,noexec,nosuid,nodev,size=1m",
        "--tmpfs",
        "/run:rw,noexec,nosuid,nodev,size=1m",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=64m",
        "-m",
        "64m",
        "--cpus",
        "0.5",
        "--pids-limit",
        "32",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "python:3.11-slim",
        "python",
        "-c",
        "import sys; exec(sys.stdin.read())",
    ]

    start_time = time.perf_counter()
    process = None

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            process.stdin.write(harness_code.encode("utf-8"))
            process.stdin.close()
        except BrokenPipeError:
            if process.stdin and not process.stdin.closed:
                process.stdin.close()

        stdout, stderr, collection_status = _collect_process_output(
            process,
            timeout_sec=timeout_sec,
        )
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        if collection_status == "OUTPUT_LIMIT_EXCEEDED":
            _stop_container(container_name)
            _terminate_process(process)
            return {
                "status": "OUTPUT_LIMIT_EXCEEDED",
                "message": "Sandbox output exceeded the configured limit.",
                "max_output_bytes": MAX_SANDBOX_OUTPUT_BYTES,
                "duration_ms": duration_ms,
            }

        if collection_status == "TIMEOUT":
            _stop_container(container_name)
            _terminate_process(process)
            return {
                "status": "TIMEOUT",
                "message": (
                    f"Execution exceeded the time limit "
                    f"({timeout_sec} seconds). Possible infinite loop."
                ),
                "duration_ms": duration_ms,
            }

        returncode = process.wait(timeout=2)
        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")

        if returncode != 0:
            return {
                "status": "SANDBOX_ERROR",
                "returncode": returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "duration_ms": duration_ms,
            }

        lines = [line for line in stdout_text.strip().splitlines() if line.strip()]
        if not lines:
            return {
                "status": "PARSING_ERROR",
                "stdout": stdout_text,
                "stderr": stderr_text,
                "duration_ms": duration_ms,
            }

        try:
            output_data = json.loads(lines[-1])
        except json.JSONDecodeError as exc:
            return {
                "status": "PARSING_ERROR",
                "message": str(exc),
                "stdout": stdout_text,
                "stderr": stderr_text,
                "duration_ms": duration_ms,
            }

        return {
            "status": "EXECUTED",
            "evaluation": output_data,
            "duration_ms": duration_ms,
            "stderr": stderr_text,
        }

    except Exception as exc:
        if process is not None:
            _stop_container(container_name)
            _terminate_process(process)
        return {
            "status": "SYSTEM_ERROR",
            "message": str(exc),
        }
