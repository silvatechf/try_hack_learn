
import json
import subprocess
import time


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

        # Isolate runtime directories.
        "--tmpfs",
        "/var/run:rw,noexec,nosuid,nodev,size=1m",

        "--tmpfs",
        "/run:rw,noexec,nosuid,nodev,size=1m",

        # Temporary writable area for Python.
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=64m",

        # Resource limits.
        "-m",
        "64m",
        "--cpus",
        "0.5",
        "--pids-limit",
        "32",

        # Privilege restrictions.
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

    try:
        res = subprocess.run(
            cmd,
            input=harness_code,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000.0

        if res.returncode != 0:
            return {
                "status": "SANDBOX_ERROR",
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_ms": duration_ms,
            }

        lines = [
            line
            for line in res.stdout.strip().splitlines()
            if line.strip()
        ]

        if not lines:
            return {
                "status": "PARSING_ERROR",
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_ms": duration_ms,
            }

        try:
            output_data = json.loads(lines[-1])
        except json.JSONDecodeError as e:
            return {
                "status": "PARSING_ERROR",
                "message": str(e),
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_ms": duration_ms,
            }

        return {
            "status": "EXECUTED",
            "evaluation": output_data,
            "duration_ms": duration_ms,
            "stderr": res.stderr,
        }

    except subprocess.TimeoutExpired:
        subprocess.run(
            [
                "docker",
                "stop",
                "-t",
                "1",
                container_name,
            ],
            capture_output=True,
            text=True,
        )

        return {
            "status": "TIMEOUT",
            "message": (
                f"Execution exceeded the time limit "
                f"({timeout_sec} seconds). Possible infinite loop."
            ),
            "duration_ms": (
                time.perf_counter() - start_time
            ) * 1000.0,
        }

    except Exception as e:
        return {
            "status": "SYSTEM_ERROR",
            "message": str(e),
        }
