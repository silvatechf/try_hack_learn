# Try Hack Learn

**Interactive security engineering and Python learning laboratory.**

Try Hack Learn is a hands-on learning environment for exploring application security, defensive architecture, controlled adversarial scenarios, and Python programming. Learners configure defensive controls, run predefined security missions, inspect evidence-oriented results, and practice Python through guided exercises.

> **Project status:** Development / release-readiness work in progress. This repository review is based on source inspection. It is not a production security assessment and does not establish that the application has been validated in a live runtime.

## Product capabilities

- **Security missions:** predefined scenarios for SQL injection, excessive personal-data exposure, and unsafe prompt/tool boundaries.
- **Defensive architecture exercise:** select and combine controls, then compare baseline and observed probe results.
- **Security Decision Record (SDR):** persist mission execution evidence and architectural rationale.
- **Python Lab:** guided, assisted, and free-code exercises with test feedback and a separate pedagogical evaluation.
- **English and Spanish interface:** English is the default language; Spanish is selectable.

Some names and storage keys in the current implementation still use the legacy `SentinelForge` identifier. This is technical legacy, not the current product name.

## Architecture

The Docker Compose application currently defines five services:

| Service | Responsibility | Host port |
|---|---|---:|
| `frontend` | React/Vite learning interface | 3001 |
| `orchestrator` | Missions, controls, probes, and SDR workflow | 8000 |
| `target_api` | Intentionally vulnerable target application for exercises | 8001 |
| `python_lab` | Python Lab API and pedagogical evaluation | 8002 |
| `python_lab_executor` | Internal execution adapter that starts isolated Docker containers | Not published |

The executor communicates with the Docker daemon through the mounted Docker socket. This is a highly privileged host interface. Treat the current Compose setup as a **trusted local development/demo environment only**; do not expose it to untrusted users or deploy it to production as-is.

## Prerequisites

- Docker Desktop (or Docker Engine) with the Docker Compose plugin.
- Git.

The Python Lab executor requires access to a Docker daemon and pulls/uses the `python:3.11-slim` execution image.

## Configure local service authentication

The Python Lab API and internal executor share a local service-to-service bearer token. Generate a unique token before starting Compose; keep `.env` local and never commit it.

PowerShell (run from the repository root):

```powershell
$existing = if (Test-Path .env) { @(Get-Content .env) } else { @() }
if ($existing | Where-Object { $_ -match '^PYTHON_LAB_EXECUTOR_TOKEN=\S+' }) {
    throw "PYTHON_LAB_EXECUTOR_TOKEN is already configured; refusing to replace it."
}
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
$token = [Convert]::ToBase64String($bytes)
$existing = @($existing | Where-Object { $_ -notmatch '^PYTHON_LAB_EXECUTOR_TOKEN=' })
$existing += "PYTHON_LAB_EXECUTOR_TOKEN=$token"
if (-not ($existing | Where-Object { $_ -match '^PYTHON_LAB_ALLOWED_ORIGINS=' })) {
    $existing += "PYTHON_LAB_ALLOWED_ORIGINS=http://localhost:3001,http://127.0.0.1:3001"
}
Set-Content -Path .env -Value $existing -Encoding ascii
Remove-Variable token, bytes, rng
```

The token is not printed. See [Python Lab service authentication](docs/PYTHON_LAB_SERVICE_AUTH.md) for the trust boundary and rotation notes.

## Start locally

From the repository root:

```powershell
docker compose up -d --build
docker compose ps
```

Open:

- Frontend: http://localhost:3001
- Orchestrator API: http://localhost:8000
- Target API sandbox: http://localhost:8001
- Python Lab API: http://localhost:8002

## Minimum exploration workflow

1. Open the frontend and inspect the Learning Map.
2. Select a mission and review its threat context, learning objective, and constraints.
3. Add defensive controls to the architecture stack.
4. Run the mission and inspect the resulting debrief and SDR evidence.
5. Open the Python Lab, select `PY-001`, complete the exercise, and inspect technical test results and pedagogical feedback.

## Useful local checks

```bash
docker compose config
docker compose ps
```

These commands check Compose configuration and container state. They do **not** prove that mission execution, sandbox isolation, or the complete learning flow works correctly. End-to-end verification must be performed against the running application.

## Security and deployment boundary

The current implementation contains security-sensitive development choices that are being tracked for release readiness:

- The executor container mounts `/var/run/docker.sock`. Control of this socket can provide host-level control; it must not be exposed to untrusted workloads.
- The Orchestrator and Python Lab configure permissive CORS.
- The Python Lab and executor request paths require a documented and tested trust boundary, including authentication, input limits, abuse controls, and failure handling.
- Sandbox flags such as `--network none`, `--read-only`, dropped Linux capabilities, and resource limits are useful controls, but do not by themselves establish a hardened multi-tenant sandbox.

See [Release Readiness](docs/RELEASE_READINESS.md) for the source-inspection findings and acceptance criteria.

## Project language

The product documentation and default interface language are English. Spanish is the only alternative user-selectable language.

## Contribution and verification principles

- Preserve existing mission, SDR, probe, and frontend contracts unless a change is explicitly designed and validated.
- Do not describe a feature as verified based only on source inspection or unit tests.
- Record the exact commands and actual outputs used for local runtime verification.
- Keep secrets out of source control and use environment-specific configuration for deployment.

