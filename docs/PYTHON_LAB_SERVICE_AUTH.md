# Python Lab service-to-service authentication

## Scope

The internal executor endpoint now requires a bearer token shared only by the Python Lab API and executor services.

- The Python Lab API reads `PYTHON_LAB_EXECUTOR_TOKEN` from its environment and sends it in the `Authorization: Bearer` header.
- The executor validates the header through a FastAPI dependency.
- Token comparison uses `hmac.compare_digest`.
- Missing executor configuration fails closed with HTTP 503.
- Missing or incorrect credentials receive HTTP 401 and a `WWW-Authenticate: Bearer` challenge.
- Tokens shorter than 32 characters are rejected by the executor at startup.
- The token is not returned in API responses or written to logs.

Compose requires the token variable for both services. The `.env.example` file is a template only; generate a unique token in the local ignored `.env` file.

## CORS boundary

The Python Lab API no longer allows every browser origin by default. It allows only the configured `PYTHON_LAB_ALLOWED_ORIGINS` values. The local default is:

- `http://localhost:3001`
- `http://127.0.0.1:3001`

Allowed methods are GET and POST; allowed headers are limited to Content-Type. CORS is a browser policy, not authentication.

## Local configuration

From the repository root, generate the token using the PowerShell instructions in the README. Do not paste the token into chat, issue comments, terminal transcripts, or source control.

Then run:

```powershell
docker compose config
docker compose up -d --build python_lab python_lab_executor
docker compose ps
```

## Verification status

**IMPLEMENTED; LOCAL DOCKER VERIFICATION NOT YET COMPLETED.**

Required checks:

1. Python Lab execution succeeds with the configured token.
2. A direct request to the internal executor without a bearer token returns HTTP 401.
3. A request with an incorrect token returns HTTP 401.
4. A request with the configured token reaches the executor and preserves normal execution behavior.
5. A browser origin outside `PYTHON_LAB_ALLOWED_ORIGINS` does not receive an `Access-Control-Allow-Origin` response header.
6. The allowed local frontend origin can still load exercises and execute `PY-001`.

## Remaining limitations

- This authenticates the Python Lab service to the executor; it does not authenticate individual learners to the Python Lab API.
- The Python Lab API remains reachable through its published local host port.
- The Orchestrator CORS policy and authentication remain separate outstanding work.
- The executor still mounts the host Docker socket. Service authentication does not remove that host-level authority.
- Rotate the shared token in both services together; Compose restart/rebuild is required after changing it.
