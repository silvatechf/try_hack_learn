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

Cleanup is best-effort if the Docker daemon is unavailable or does not respond within the stop timeout. This behavior must be exercised against the actual local Docker daemon before being treated as verified.

## Focused tests

`python_lab_executor/test_sandbox_output_limits.py` covers:

- Concurrent stdout/stderr collection below the limit.
- Detection of combined output above the configured limit.
- Collector timeout reporting.

These tests exercise the output collector; they do not prove Docker container cleanup, daemon behavior, or end-to-end API mapping.

## Verification status

**IMPLEMENTED; NOT YET VERIFIED ON THE LOCAL DOCKER RUNTIME.**

Required local checks:

```powershell
docker compose build python_lab_executor
docker compose run --rm python_lab_executor pytest -q test_request_validation.py test_sandbox_output_limits.py
docker compose up -d python_lab_executor python_lab
```

Then submit a Python Lab solution that writes more than 64 KiB to stdout and confirm that the API returns a stable technical failure, the learner container is stopped/removed, and the normal PY-001 solution still returns the existing technical and pedagogical result.

## Remaining limitations

- The Docker socket remains mounted into the executor and is a high-privilege host capability.
- Request-body limits, concurrency/rate limits, service authentication, and a typed executor response contract remain outstanding.
- The output cap does not replace CPU, memory, PID, wall-clock, or daemon-level resource controls.
