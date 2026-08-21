# Phase 4 — Interactive Python Security Lab

## Architecture Specification

**Status:** ARCHITECTURE APPROVED WITH SECURITY CORRECTION  
**Project:** SentinelForge  
**Baseline:** FROZEN  
**Document:** `PHASE_4_ARCHITECTURE.md`

---

## 1. Purpose

Phase 4 introduces an Interactive Python Security Lab inside SentinelForge.

The objective is to allow students to learn Python programming and security concepts directly through the SentinelForge platform without requiring:

- local Python installation;
- Linux;
- virtual machines;
- local development environments;
- manual Docker setup;
- direct access to the SentinelForge host environment.

The feature must preserve the existing SentinelForge baseline and introduce the Python Lab as a modular, isolated subsystem.

The primary educational flow is:

```text
Student
  ↓
SentinelForge Frontend
  ↓
Python Lab API
  ↓
Python Lab Executor
  ↓
Ephemeral Sandbox Container
  ↓
Execution + Validation
  ↓
Pedagogical Result
  ↓
Frontend
```

---

## 2. Architectural Principles

1. Student code is treated as hostile input.
2. Student code must never execute inside the main application process.
3. The public Python Lab API must not possess Docker socket access.
4. Only the isolated executor may interact with the Docker daemon.
5. Every student execution occurs in an ephemeral container.
6. The sandbox container must have no access to the host filesystem, SentinelForge project files, secrets, Docker socket, or external network.
7. Existing SentinelForge functionality remains protected.
8. Phase 4 must be implemented incrementally.
9. Each stage requires real local validation.
10. No feature is considered VERIFIED without runtime evidence.

---

## 3. Protected FROZEN Baseline

Phase 4 must not modify the behavior of the existing core system.

Protected components:

```text
MISSION-001
MISSION-002
MISSION-003
scenario_registry
control_registry
SDR generation
execution contracts
target_api
Arena deployment
Learning Map
persistence
i18n
existing frontend behavior
existing orchestrator behavior
```

Any change to these components requires explicit authorization and a separate architectural decision.

---

## 4. Approved Architecture

The Python Lab consists of two distinct services.

```text
                         ┌─────────────────────┐
                         │      FRONTEND       │
                         │   React / Vite      │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌─────────────────────┐
                         │   PYTHON LAB API    │
                         │                     │
                         │ Public API          │
                         │ Port 8002           │
                         │                     │
                         │ NO Docker socket    │
                         └──────────┬──────────┘
                                    │
                                    │ Internal request
                                    ▼
                         ┌─────────────────────┐
                         │   LAB EXECUTOR      │
                         │                     │
                         │ Internal worker     │
                         │ Docker access       │
                         └──────────┬──────────┘
                                    │
                                    │ docker run
                                    ▼
                    ┌──────────────────────────────┐
                    │     EPHEMERAL SANDBOX        │
                    │                              │
                    │ python:3.11-slim             │
                    │ --network none               │
                    │ --read-only                  │
                    │ --cap-drop ALL               │
                    │ --no-new-privileges          │
                    │ --memory 64m                  │
                    │ --cpus 0.5                    │
                    │ --pids-limit 32               │
                    │                              │
                    │ Student code                 │
                    └──────────────────────────────┘
```

---

## 5. Critical Security Boundary

The most important architectural rule of Phase 4 is:

> No HTTP endpoint exposed to the student or frontend may execute in a process that has access to the Docker socket.

The public API service:

```text
python_lab
```

must not mount:

```text
/var/run/docker.sock
```

The Docker socket may exist only in:

```text
python_lab_executor
```

The executor must not expose a public port to the frontend.

---

## 6. Python Lab API

### Responsibility

The Python Lab API is responsible for:

- listing exercises;
- validating exercise identifiers;
- validating request size;
- accepting student code;
- forwarding execution requests;
- receiving execution results;
- returning structured results to the frontend.

It must not:

- execute student code directly;
- call `docker run`;
- mount the Docker socket;
- access the SentinelForge host filesystem;
- manage sandbox containers directly.

### API

```http
GET /api/v1/python-lab/exercises
```

```http
POST /api/v1/python-lab/execute
```

Request:

```json
{
  "exercise_id": "PY-001",
  "student_code": "def solve(data):\n    return sum(x for x in data if x > 0)"
}
```

---

## 7. Python Lab Executor

The executor is an internal service responsible for creating and destroying ephemeral execution environments.

It is the only component authorized to interact with Docker.

Responsibilities:

- receive execution requests from the Python Lab API;
- create ephemeral sandbox containers;
- enforce resource restrictions;
- execute the evaluation harness;
- capture stdout/stderr;
- enforce execution timeout;
- return structured results;
- guarantee cleanup.

The executor must not expose an endpoint directly to the frontend.

---

## 8. Ephemeral Sandbox

Each student execution must occur inside a new ephemeral container.

Recommended baseline:

```text
python:3.11-slim
```

Required restrictions:

```text
--network none
--read-only
--cap-drop ALL
--security-opt no-new-privileges:true
--memory 64m
--cpus 0.5
--pids-limit 32
```

Temporary writable storage may be provided through:

```text
--tmpfs /tmp
```

The sandbox must not receive:

```text
Docker socket
SentinelForge project directories
Host filesystem mounts
application secrets
credentials
API keys
sensitive environment variables
```

---

## 9. Filesystem Isolation

The sandbox root filesystem must be isolated from the host.

A read-only root filesystem is preferred.

Temporary writes required by Python execution may use an ephemeral `/tmp`.

The sandbox must never mount host/project paths such as:

```text
.
./sentinelforge
/app
/var/run/docker.sock
```

The objective is:

```text
Student code
    ↓
Sandbox filesystem only
    ↓
Destroyed after execution
```

---

## 10. Network Isolation

The sandbox must use:

```text
--network none
```

Student code must not be able to reach:

- the Internet;
- SentinelForge APIs;
- the orchestrator;
- target_api;
- other containers;
- internal network services.

Network isolation is a mandatory security property.

---

## 11. Resource Limits

Recommended initial values:

| Resource | Limit |
|---|---:|
| CPU | 0.5 CPU |
| Memory | 64 MB |
| PIDs | 32 |
| Execution timeout | 3 seconds |

These values are starting points and may be tuned based on real runtime evidence.

Changing them must be documented.

---

## 12. Execution Timeout

Student code must never be allowed to run indefinitely.

```text
Student code
    ↓
Sandbox
    ↓
3-second limit
    ↓
Timeout
    ↓
Container termination
    ↓
Cleanup
```

An infinite loop must produce a controlled result such as:

```json
{
  "status": "TIMEOUT"
}
```

---

## 13. Student Code Execution

Student code may be evaluated using an ephemeral harness.

For example:

```python
exec(student_code, student_globals)
```

This mechanism is not considered the security boundary.

The security boundary is the isolated sandbox container.

Python-level restrictions may be used as defense-in-depth, but must not be treated as the primary sandbox.

---

## 14. Exercise Registry

Exercises must be declarative.

Recommended file:

```text
python_lab/exercises_registry.py
```

Example:

```python
EXERCISES = {
    "PY-001": {
        "exercise_id": "PY-001",
        "title": "Trace the Signal",
        "difficulty": "beginner",
        "description": "...",
        "starter_code": "...",
        "tests": [],
        "learning_objectives": [
            "Basic iteration",
            "Conditional aggregation"
        ]
    }
}
```

The registry should define:

- exercise ID;
- title;
- difficulty;
- description;
- starter code;
- tests;
- learning objectives.

---

## 15. Initial Exercise

The first exercise remains intentionally simple:

```text
PY-001 — Trace the Signal
```

Learning objectives:

- Python function definition;
- list iteration;
- conditional logic;
- aggregation;
- basic testing.

The first exercise exists to prove the complete product pipeline, not to represent the final curriculum.

---

## 16. Validation Strategy

Validation must prove both functionality and isolation.

Required categories:

```text
1. Normal execution
2. Incorrect answer
3. Syntax error
4. Runtime error
5. Infinite loop
6. Network isolation
7. Filesystem isolation
8. Secret/environment isolation
9. Container cleanup
10. Basic concurrency behavior
```

---

## 17. Normal Execution Test

Example:

```python
def solve(data):
    return sum(x for x in data if x > 0)
```

Expected:

```text
Execution completes.
Tests execute.
Correct tests pass.
Status indicates successful evaluation.
```

---

## 18. Incorrect Answer Test

Example:

```python
def solve(data):
    return 999
```

Expected:

```text
Execution completes.
Sandbox remains healthy.
Tests fail.
Result reports failed evaluation.
```

This is an educational failure, not necessarily a product defect.

---

## 19. Syntax Error Test

Example:

```python
def solve(data)
    return 1
```

Expected:

```text
Execution terminates.
Syntax error is captured.
Container is destroyed.
API remains available.
```

---

## 20. Runtime Error Test

Example:

```python
def solve(data):
    return data[999999]
```

Expected:

```text
Execution terminates.
Runtime exception is captured.
Container is destroyed.
API remains available.
```

---

## 21. Infinite Loop Test

Example:

```python
def solve(data):
    while True:
        pass
```

Expected:

```text
Execution terminates at timeout.
Result status = TIMEOUT.
Container is destroyed.
Host remains healthy.
API remains available.
```

---

## 22. Network Isolation Test

Example:

```python
import urllib.request

def solve(data):
    return urllib.request.urlopen("http://example.com").read()
```

Expected:

```text
Network access is unavailable.
Execution does not reach the external service.
The failure is captured as an execution/test failure.
```

The test should distinguish network isolation from unrelated Python errors whenever possible.

---

## 23. Filesystem Isolation Test

The test must not assume that `/` is empty.

Instead, it must verify that the sandbox cannot access known host/project resources.

Objective:

```text
Sandbox
  X
  ↓
Host filesystem
  X
  ↓
SentinelForge project
  X
  ↓
Docker socket
```

The test must avoid exposing sensitive host paths as part of normal student-facing output.

---

## 24. Secret Isolation Test

The sandbox must not inherit sensitive environment variables.

The executor must explicitly control environment inheritance rather than assuming the container runtime will always provide a safe environment.

---

## 25. Docker Socket Isolation Test

Student code must not have access to:

```text
/var/run/docker.sock
```

This is mandatory.

The ephemeral sandbox must never mount the Docker socket.

---

## 26. Container Cleanup

Every execution must result in container cleanup.

Normal completion:

```text
run
↓
exit
↓
--rm
↓
container removed
```

Timeout:

```text
run
↓
timeout
↓
stop
↓
remove
```

The executor must have defensive cleanup logic for abnormal failures.

---

## 27. Concurrency

The MVP may initially process executions sequentially or with tightly controlled concurrency.

Known risk:

```text
many students
     ↓
many docker run
     ↓
daemon pressure
     ↓
CPU / memory / disk pressure
```

Future mitigation may include:

- worker pool;
- execution queue;
- concurrency semaphore;
- rate limiting;
- pre-warmed workers.

These are not required for the first MVP unless real testing demonstrates the need.

---

## 28. Docker Compose

The root `docker-compose.yml` must add the new services without altering existing service behavior.

Conceptually:

```yaml
python_lab:
  build: ./python_lab
  ports:
    - "8002:8002"
  networks:
    - python_lab_net

python_lab_executor:
  build: ./python_lab_executor
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  networks:
    - python_lab_net
```

The exact Compose implementation must be audited against the actual existing project before modification.

Do not blindly replace the current Compose file.

---

## 29. Proposed Directory Structure

```text
sentinelforge/
│
├── docker-compose.yml
│
├── python_lab/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── exercises_registry.py
│
├── python_lab_executor/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── sandbox_runner.py
│
├── orchestrator/
├── target_api/
└── frontend/
```

Additional tests may be introduced where they provide meaningful validation.

---

## 30. Files Protected

Initial Phase 4 must not modify the existing mission, control, SDR, Arena, Learning Map, persistence, or i18n behavior unless explicitly authorized.

---

## 31. Files Expected to Change

Initial Phase 4 changes should be limited to:

```text
docker-compose.yml
python_lab/
python_lab_executor/
```

Frontend integration should occur only after the backend execution pipeline has been validated.

---

## 32. Incremental Implementation Plan

### Phase 4.1 — API Foundation

Implement:

```text
python_lab/main.py
python_lab/exercises_registry.py
```

Provide:

```text
GET /api/v1/python-lab/exercises
```

Stop condition:

> The API lists `PY-001` correctly.

### Phase 4.2 — Executor

Implement:

```text
python_lab_executor/main.py
python_lab_executor/sandbox_runner.py
```

Stop condition:

> The executor can create and destroy one sandbox successfully.

### Phase 4.3 — Sandbox Security

Implement:

```text
network none
read-only filesystem
tmpfs
CPU limit
memory limit
PID limit
cap-drop ALL
no-new-privileges
no Docker socket
no host mounts
controlled environment
```

Stop condition:

> Security isolation tests provide real evidence.

### Phase 4.4 — API → Executor Integration

Connect:

```text
python_lab
   ↓
python_lab_executor
   ↓
sandbox
```

Stop condition:

> A real HTTP request can execute `PY-001`.

### Phase 4.5 — Educational Result

Return:

```text
status
exercise_id
evaluation
test results
duration
pedagogical feedback
```

Stop condition:

> Frontend-compatible structured response is demonstrated.

### Phase 4.6 — Frontend

Only after backend validation:

```text
Learning Map
    ↓
Python Lab
    ↓
Exercise
    ↓
Editor
    ↓
Run
    ↓
Result
    ↓
Feedback
```

---

## 33. Educational Evolution

After the MVP is proven, the Lab can evolve into a progressive curriculum:

```text
PY-001  Python basics
   ↓
PY-002  Conditions
   ↓
PY-003  Loops
   ↓
PY-004  Functions
   ↓
PY-005  Lists / dictionaries
   ↓
PY-006  Exceptions
   ↓
PY-007  File handling
   ↓
PY-008  HTTP / API concepts
   ↓
PY-009  Secure coding
   ↓
PY-010  Security challenge
```

The educational progression should eventually connect Python knowledge with SentinelForge security missions.

---

## 34. Future Cybersecurity Integration

The long-term differentiator is:

```text
Python learning
       +
programming logic
       +
security engineering
       +
defensive thinking
       +
hands-on challenges
```

Example:

```text
Learn Python loop
       ↓
Learn input validation
       ↓
Learn HTTP
       ↓
Analyze vulnerable endpoint
       ↓
Understand attack
       ↓
Implement defense
       ↓
Observe mitigation
```

---

## 35. Mandatory Security Boundary Rules

### Rule 1

Student code never executes in:

```text
orchestrator
python_lab API
frontend
target_api
```

### Rule 2

Student code executes only inside ephemeral sandbox containers.

### Rule 3

The public API never possesses Docker socket access.

### Rule 4

The executor is the only component authorized to create sandbox containers.

### Rule 5

Sandbox containers never possess Docker socket access.

### Rule 6

Sandbox containers have no external network.

### Rule 7

Sandbox containers have no host filesystem mounts.

### Rule 8

Sandbox containers do not inherit application secrets.

### Rule 9

Sandbox containers have strict resource limits.

### Rule 10

Every execution must terminate or be forcibly terminated.

---

## 36. Risks

### Docker socket compromise

The executor is a privileged infrastructure component because it requires Docker daemon access.

Therefore:

```text
executor compromise
    =
high-impact security event
```

The executor must remain internal, minimal, small in scope, and free of student-facing functionality.

### Concurrent execution pressure

Large numbers of executions may pressure:

- Docker daemon;
- CPU;
- memory;
- disk;
- process limits.

Mitigation may be added after real evidence demonstrates the requirement.

### Sandbox escape

No containerization approach should be described as mathematically impossible to escape.

The objective is defense in depth.

Future hardening options may include:

- stronger container profiles;
- seccomp restrictions;
- AppArmor/SELinux where available;
- rootless execution;
- dedicated worker hosts;
- microVM-based isolation.

These are future options, not automatic MVP requirements.

---

## 37. Validation Commands

Initial build:

```powershell
docker compose up -d --build python_lab python_lab_executor
```

Check services:

```powershell
docker compose ps
```

Check Python Lab:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8002/api/v1/python-lab/exercises" `
    -Method Get
```

Execute a simple exercise:

```powershell
$body = @{
    exercise_id = "PY-001"
    student_code = @"
def solve(data):
    return sum(x for x in data if x > 0)
"@
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8002/api/v1/python-lab/execute" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

These commands are validation procedures, not evidence of successful execution until the human provides the actual output.

---

## 38. Required Evidence

A Phase 4 checkpoint must contain actual evidence for:

```text
Service build
Service startup
Exercise listing
Successful execution
Incorrect solution
Syntax error
Runtime error
Timeout
Network isolation
Filesystem isolation
Secret isolation
Docker socket isolation
Container cleanup
```

---

## 39. Checkpoint Format

```text
PROJECT STATE CHECKPOINT

Current phase:

Verified functionality:

Implemented but runtime-unverified:

Failed:

Blocked:

Known issues:

Files modified:

Files protected:

Contracts preserved:

Validation commands executed:

Observed results:

Security evidence:

Educational behavior:

Next recommended action:

Status:
```

Allowed status values:

```text
VERIFIED
IMPLEMENTED / NOT VERIFIED
FAILED
BLOCKED
UNKNOWN
```

Do not use `READY`, `COMPLETE`, or `PRODUCTION READY` without corresponding evidence.

---

## 40. Stop Conditions

The implementation process must stop when:

- the requested stage is implemented;
- critical validation is complete;
- the next step requires human runtime observation;
- evidence contradicts expectations;
- the environment prevents reliable validation;
- scope begins expanding beyond Phase 4.

When stopping:

```text
STOP — HUMAN VALIDATION REQUIRED
```

The implementation AI must not fabricate the result of the next validation step.

---

## 41. Governance

Phase 4 follows the SentinelForge engineering method:

```text
CURRENT STATE
      ↓
AUDIT
      ↓
MINIMUM CHANGE
      ↓
HUMAN AUTHORIZATION
      ↓
IMPLEMENTATION
      ↓
LOCAL VALIDATION
      ↓
OBSERVED EVIDENCE
      ↓
ANALYSIS
      ↓
FIX
      ↓
RE-VALIDATE
      ↓
CHECKPOINT
      ↓
NEXT CHANGE
```

No AI-generated report overrides real local evidence.

---

## 42. Architectural Decision

The Python Lab architecture is approved under the following condition:

```text
APPROVED:

Python Lab API
        ↓
Internal Executor
        ↓
Ephemeral Sandbox
```

Explicitly rejected:

```text
Public Python Lab API
        +
Docker socket
        +
Student execution
        =
NOT APPROVED
```

The Docker socket must never be exposed to the public-facing Python Lab API.

---

## 43. Final Objective

The objective of Phase 4 is not simply to create an online Python interpreter.

The objective is to create a secure educational environment where the student progresses from:

```text
Python logic
      ↓
Programming
      ↓
Debugging
      ↓
Secure coding
      ↓
Security concepts
      ↓
Security engineering
      ↓
SentinelForge missions
```

without requiring local infrastructure.

The platform becomes the laboratory.

The student interacts with the laboratory.

The host environment remains protected.

---

## 44. Golden Rule

> DO NOT OPTIMIZE FOR A SUCCESSFUL REPORT. OPTIMIZE FOR A WORKING PRODUCT THAT CAN BE VERIFIED BY THE HUMAN.

A green report without runtime evidence is not success.

A failed isolation test is valuable evidence.

A security failure must be investigated rather than hidden.

A simpler verified architecture is preferable to a complex unverified architecture.

---

## Current Status

```text
PHASE 4 ARCHITECTURE REVIEW

Concept:
APPROVED

Security boundary:
APPROVED WITH CORRECTION

Public API:
NO DOCKER SOCKET

Executor:
INTERNAL + DOCKER ACCESS

Sandbox:
EPHEMERAL + RESTRICTED

Existing SentinelForge baseline:
FROZEN / PROTECTED

Implementation:
NOT YET VERIFIED

Next step:
IMPLEMENT PHASE 4.1 ONLY

STOP CONDITION:
HUMAN VALIDATION REQUIRED
```
