# Python Lab request admission and concurrency limits

## Scope

The Python Lab execution path now has two additional admission controls:

- A 64 KiB HTTP request-body limit on `POST /api/v1/python-lab/execute`.
- A bounded executor concurrency budget, configured by `PYTHON_LAB_MAX_CONCURRENT_EXECUTIONS` and set to `2` in the local Compose environment.

The body-size middleware rejects oversized requests with HTTP 413 before FastAPI/Pydantic parses the payload. It checks a declared `Content-Length` early and also counts streamed body bytes when the length is absent.

The executor uses a process-local bounded semaphore. When all execution slots are occupied, it rejects a new submission with HTTP 429 and `Retry-After: 2`. The Python Lab API preserves that 429 response rather than converting it into a generic upstream 502. The frontend displays a localized capacity message.

## Configuration and limits

| Control | Limit | Enforcement point |
|---|---:|---|
| HTTP execution request body | 65,536 bytes | Python Lab ASGI middleware |
| Student code | 10,000 characters | Pydantic API model, executor model, frontend editor/client |
| Concurrent sandbox executions | 2 by default in Compose | Executor process |
| Queue behavior | No queue; fail fast with HTTP 429 | Executor |

The executor configuration accepts values from 1 through 16. Invalid values stop the executor from starting rather than silently disabling the limit.

## Important concurrency boundary

The semaphore is process-local, not distributed. The effective concurrency budget is multiplied by the number of executor processes/replicas. The current Compose deployment runs one executor service and uses the configured limit of two. If the deployment topology changes, recalculate the aggregate host resource budget.

This is backpressure, not per-user rate limiting or authentication. The internal executor still relies on the private Compose network and does not yet authenticate the calling service.

## Local validation

From the repository root:

```powershell
docker compose build python_lab python_lab_executor
docker compose run --rm python_lab python -m unittest discover -s . -p "test_*.py"
docker compose run --rm python_lab_executor pytest -q test_request_validation.py test_sandbox_output_limits.py
docker compose up -d python_lab python_lab_executor frontend
```

Verify the HTTP body limit by submitting a request body larger than 65,536 bytes directly to the Python Lab execution endpoint; expect HTTP 413.

Verify backpressure by submitting three requests concurrently, each running a solution that sleeps for approximately two seconds before returning. With two execution slots, the expected behavior is two admitted executions and one HTTP 429 response with `Retry-After: 2`. Repeat with normal `PY-001` after the test to confirm capacity is released.

## Verification status

**IMPLEMENTED; LOCAL DOCKER RUNTIME VERIFICATION NOT YET COMPLETED.**

Unit tests cover middleware size enforcement, semaphore saturation, and semaphore release after runner failure. Actual concurrent HTTP behavior and the configured Docker Compose service still require local validation.

## Remaining limitations

- No per-user identity, quota, or rate limit exists.
- No distributed concurrency coordinator exists.
- Request-body size and code-length limits do not replace a total ingress/proxy request limit.
- Docker daemon authority remains mounted into the executor.
- Service-to-service authentication and restrictive CORS remain outstanding.
