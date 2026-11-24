# Python Lab sandbox output limits

## Scope

The executor now collects the Docker CLI process output through concurrently drained stdout and stderr pipes. The combined output budget is 64 KiB per sandbox execution.

When the combined stream exceeds the configured budget, the runner:

1. Returns the technical status `OUTPUT_LIMIT_EXCEEDED`.
2. Requests that the named learner container be stopped.
3. Terminates the Docker CLI process if it is still running.
4. Does not return the captured learner output in the API response.

The output ceiling applies to the bytes collected from the Docker CLI stdout/stderr pipes. It is not a complete limit on all Docker daemon logging, host logging, or other resource consumption.

## Timeout and lifecycle behavior

The same bounded collector enforces the existing execution timeout while draining both streams. On timeout or output overflow, the runner asks Docker to stop the named sandbox container and then terminates the local Docker CLI process if necessary.

Cleanup is best-effort if the Docker daemon is unavailable or does not respond within the stop timeout.

## Focused tests

`python_lab_executor/test_sandbox_output_limits.py` covers:

- Concurrent stdout/stderr collection below the limit.
- Detection of combined output above the configured limit.
- Collector timeout reporting.

These tests exercise the output collector; they do not independently prove Docker container cleanup or daemon behavior.

## Local Docker verification

**VERIFIED ON THE LOCAL DOCKER RUNTIME — 2026-11-24.**

Commands executed from the repository root:

```powershell
docker compose build python_lab_executor
docker compose run --rm python_lab_executor pytest -q test_request_validation.py test_sandbox_output_limits.py
docker compose up -d python_lab_executor python_lab
```

Observed results:

- Executor image build completed successfully.
- Focused test suite: `10 passed in 0.49s`.
- Normal `PY-001` execution returned `EXECUTED`, with `evaluation.status = SUCCESS`, `passed_all = true`, all 4/4 cases passing, and pedagogical outcome `MASTERED`.
- Overflow probe using `print('X' * 70000)` returned `OUTPUT_LIMIT_EXCEEDED`, with `max_output_bytes = 65536`.
- Immediately after the overflow probe, `docker ps -a --filter "name=python_sandbox_" --format "{{.Names}} | {{.Status}}"` returned no matching containers.

The runtime evidence confirms the expected API behavior and that no matching sandbox container remained listed after the overflow test. It does not prove cleanup under Docker daemon failure or every possible race condition.

## Remaining limitations

- The Docker socket remains mounted into the executor and is a high-privilege host capability.
- Request-body limits, concurrency/rate limits, service authentication, and a typed executor response contract remain outstanding.
- The output cap does not replace CPU, memory, PID, wall-clock, or daemon-level resource controls.
