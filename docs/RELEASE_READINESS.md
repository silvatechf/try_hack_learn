# Release Readiness Assessment

**Assessment date:** 2026-11-23  
**Repository:** `silvatechf/try_hack_learn`  
**Branch:** `work/release-readiness`  
**Method:** Static source inspection through the GitHub repository. No local Docker runtime was available during this review.

## Executive assessment

The repository contains a coherent learning-product direction: security missions, an orchestrator, an intentionally vulnerable target API, a Python Lab API, a Docker-backed execution adapter, and a React/Vite frontend.

The current implementation must be treated as a **trusted local development/demo baseline**, not as a production-ready or multi-tenant service. The highest-priority concern is the executor's access to the host Docker socket. The public-facing API boundaries also need an explicit trust model, authentication/authorization decisions, input limits, and abuse controls.

This document records source-level findings. It does not claim exploitability, successful runtime validation, or completion of remediation.

## Architecture observed

Docker Compose defines:

- `frontend`: React/Vite UI, published on host port 3001.
- `orchestrator`: mission/control APIs and probe execution, published on host port 8000.
- `target_api`: intentionally vulnerable exercise target, published on host port 8001.
- `python_lab`: exercise catalogue, execution request handling, and pedagogical evaluation, published on host port 8002.
- `python_lab_executor`: internal adapter that invokes Docker to execute learner code.

The Python Lab API and executor share an internal Docker network. The executor also mounts `/var/run/docker.sock`.

## Findings and priorities

### P0 — Docker daemon socket is mounted into the executor

**Evidence:** `docker-compose.yml` mounts `/var/run/docker.sock:/var/run/docker.sock` into `python_lab_executor`. The executor Dockerfile installs the Docker CLI, and `python_lab_executor/sandbox_runner.py` invokes `docker run`.

**Impact:** Access to the Docker daemon socket is effectively a highly privileged host capability. A compromise of the executor process or any path that permits command execution in that container may become a host compromise. Container flags applied to learner workloads do not remove the executor's daemon-level authority.

**Required direction:**
- Keep this deployment explicitly restricted to a trusted local environment until the execution architecture is redesigned.
- Evaluate a dedicated sandbox service/VM boundary or a purpose-built isolated runner with narrowly scoped operations.
- Do not expose the executor API outside its private network.
- Define and test the threat model for malicious learner code, executor compromise, daemon compromise, and host escape.

**Acceptance criteria:**
- No untrusted tenant can reach a Docker daemon API or submit arbitrary Docker CLI operations.
- The executor's host-level authority is removed or isolated behind a separately hardened boundary.
- Adversarial tests verify the intended network, filesystem, process, memory, CPU, and privilege restrictions.

### P1 — API trust boundaries are not explicit

**Evidence:**
- `orchestrator/main.py` configures CORS with `allow_origins=["*"]`, `allow_methods=["*"]`, and `allow_headers=["*"]`.
- `python_lab/main.py` uses the same permissive CORS configuration.
- The inspected route handlers do not show authentication or authorization dependencies.
- `python_lab_executor/main.py` exposes an internal execution route without an authentication dependency.
- Compose publishes the Orchestrator, Target API, and Python Lab ports to the host.

**Impact:** CORS is not authentication. If these services are reachable beyond the intended local environment, unauthenticated callers may be able to invoke mission operations or submit code for execution. The exact exposure depends on network topology and deployment configuration.

**Required direction:**
- Define which endpoints are browser-facing, internal-only, or intentionally public.
- Configure exact allowed browser origins per environment; do not use wildcard CORS as an access-control mechanism.
- Add service-to-service authentication for internal execution requests.
- Define user authentication, authorization, quotas, and rate limits before supporting remote or multi-user access.
- Bind internal-only services to private networks and avoid publishing their ports unnecessarily.

**Acceptance criteria:**
- Unauthorized requests to protected endpoints are rejected.
- Executor calls require authenticated service identity.
- Browser CORS tests cover allowed and disallowed origins.
- Deployment documentation clearly identifies exposed ports and trust zones.

### P1 — Learner code and request payloads need explicit resource and size limits

**Evidence:** `python_lab/main.py` accepts `student_code: str` without a declared maximum length. `python_lab_executor/main.py` accepts a generic list of tests. `sandbox_runner.py` applies a 3-second subprocess timeout and sets memory, CPU, PID, read-only, no-network, and capability restrictions to the spawned container.

**Impact:** Existing sandbox flags are useful, but request-size limits, schema constraints, bounded output, container lifecycle behavior, daemon-level quotas, and concurrent execution limits are not established by the inspected code. Large payloads or concurrent requests may exhaust API, executor, or Docker resources.

**Required direction:**
- Add strict Pydantic constraints for exercise IDs, source length, and test payload shape.
- Enforce bounded stdout/stderr and response sizes.
- Apply concurrency limits and per-user/per-IP quotas at the appropriate trusted boundary.
- Define Docker memory-swap, CPU, PID, process, and execution-time policies.
- Ensure timed-out containers are reliably stopped and removed; test failure paths, including Docker daemon errors.

**Acceptance criteria:**
- Oversized and malformed payloads are rejected before reaching the executor.
- Concurrent and repeated submissions remain within documented resource budgets.
- Timeout, cancellation, daemon-unavailable, and malformed-output paths return stable API errors.
- No learner-controlled output can cause unbounded memory use or log growth.

### P1 — Executor result handling and API error mapping need verification

**Evidence:** `python_lab/main.py` parses the executor response as JSON and evaluates it without first checking the HTTP response status. The exception handler catches `httpx.RequestError`, but not all response parsing or validation failures. The pedagogical evaluator expects technical statuses such as `EXECUTED` and `TIMEOUT`.

**Impact:** Unexpected executor responses can propagate as unhandled server errors or produce inconsistent technical/pedagogical results. The current behavior has not been exercised against a live Docker daemon in this review.

**Required direction:**
- Validate executor HTTP status before parsing the response.
- Define a typed response schema for executor outcomes.
- Map timeout, sandbox/system failure, malformed response, and unavailable executor to stable API responses.
- Keep technical execution outcomes separate from pedagogical feedback.

**Acceptance criteria:**
- Contract tests cover every documented executor status and malformed responses.
- API responses remain stable for timeout, sandbox failure, and executor unavailability.
- Pedagogical evaluation never upgrades a technical failure to a successful learning outcome.

### P2 — Frontend service URLs are hard-coded

**Evidence:** `frontend/src/App.jsx` calls `http://localhost:8000` directly for Orchestrator endpoints. Compose also sets `VITE_API_URL`, but the inspected App component does not use it for those calls.

**Impact:** The frontend is tied to a local development topology and is difficult to deploy behind a reverse proxy or on another host.

**Required direction:**
- Centralize API base URLs in one frontend configuration module.
- Use the existing `VITE_API_URL` configuration consistently or use a same-origin reverse-proxy path.
- Provide a safe development default and fail clearly when required configuration is invalid.

**Acceptance criteria:**
- No production component hard-codes localhost service URLs.
- A non-local API base URL can be configured at build/deployment time.
- Frontend build and browser smoke tests cover the configured API base.

### P2 — Product branding and operational documentation are inconsistent

**Evidence:** The repository is named `try_hack_learn`, but the README title, API titles, frontend package name, translation strings, and some storage keys retain `SentinelForge`.

**Impact:** Inconsistent product identity makes onboarding and release communication less clear. Some identifiers may be persisted in browsers or consumed by integrations, so a broad rename could cause compatibility regressions.

**Required direction:**
- Use Try Hack Learn as the user-facing product identity.
- Inventory legacy identifiers before changing API titles, storage keys, package metadata, or persisted keys.
- Migrate persisted browser data deliberately if storage keys are renamed.

**Acceptance criteria:**
- README and user-facing product surfaces use consistent branding.
- Legacy technical identifiers are either intentionally retained and documented or migrated with compatibility tests.

## Verification gaps

The following must be checked on a real local Docker runtime before a release claim:

- `docker compose config` and clean image builds.
- Container health and startup ordering.
- Mission flows MISSION-001, MISSION-002, and MISSION-003.
- Python Lab normal execution, syntax error, runtime error, timeout, malformed payload, and executor-unavailable paths.
- Sandbox network/filesystem/resource isolation.
- English/Spanish UI and persistence behavior.
- Automated tests, dependency audit, and SAST results from the current commit.

A passing unit-test suite is supporting evidence, not proof of end-to-end or sandbox security.

## Recommended delivery sequence

1. **Contain the current risk:** label and enforce the local trusted-demo boundary; do not expose the Docker socket or executor to untrusted networks.
2. **Define trust zones:** document browser, Orchestrator, Python Lab, executor, Docker daemon, and target API boundaries.
3. **Harden execution:** remove or isolate daemon-level authority; validate payloads; bound resources, output, concurrency, and lifecycle.
4. **Harden APIs:** service authentication, endpoint authorization, explicit CORS, rate limits, and safe error mapping.
5. **Make deployment configurable:** centralize frontend API configuration and add health checks.
6. **Automate evidence:** CI for builds, tests, SAST, dependency auditing, and container configuration checks.
7. **Run end-to-end validation:** capture actual command output and record each verified workflow.

## Scope and limitations

This assessment is based on files available on the GitHub branch at review time. It did not include running containers, probing a live deployment, reviewing every repository file, validating CI, or performing a penetration test. Findings must be confirmed and prioritized against the complete runtime and deployment context.
