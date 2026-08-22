# SentinelForge — Project Completion Roadmap

**Status:** DRAFT FOR APPROVAL  
**Target:** V1.0 Complete / Scope Frozen  
**Baseline Reference:** `56551b8`  
**Validated Checkpoint:** `v1.1-phase4-validated`

---

## 1. Purpose

This document is the authoritative roadmap for taking SentinelForge from its current validated state to a finished V1.0.

Its purpose is not to add architecture or features. Its purpose is to define exactly what remains, how completion is proved, and when the project is considered finished.

### Scope rule

After this roadmap is approved, no new feature, mission, subsystem, refactor, or architectural expansion is added unless it is explicitly classified as **V1.0 required** or approved as a separate post-V1.0 project.

---

## 2. Engineering Method

The project continues to use the established method:

**Hypothesis → Contract → Implementation → Real Runtime → Evidence → Analysis → Decision → Checkpoint**

### Authority model

- **User:** architecture authority, final approver, local runtime operator.
- **Gemini:** implementation agent.
- **ChatGPT:** architecture/review/validation copilot.
- **Local Docker runtime:** source of truth for behavioral verification.

No AI claim of readiness replaces real runtime evidence.

---

## 3. Frozen Baseline

The following behavior is protected unless a separate architectural decision authorizes a change:

- MISSION-001
- MISSION-002
- MISSION-003
- scenario registry
- control registry
- SDR generation
- Arena deployment flow
- target API behavior
- Learning Map
- persistence
- i18n behavior
- existing frontend behavior
- existing orchestrator behavior
- Phase 4 isolation architecture

Reference tags:

- `v1.0-baseline`
- `v1.1-phase4-validated`

---

## 4. Current Verified State

### Core security missions

| Area | Current status | Evidence |
|---|---|---|
| MISSION-001 — SQL Injection | VERIFIED | `parameterized_queries`, 100% mitigation, constraints passed |
| MISSION-002 — PII Exposure | VERIFIED | `data_masking` + SCA, 100% mitigation, constraints passed |
| MISSION-003 — AI Prompt/Tool Boundary | VERIFIED | `semantic_guardrails`, 100% mitigation, constraints passed |

### DevSecOps

| Capability | Status |
|---|---|
| SAST / Bandit | VERIFIED |
| SCA / `pip-audit` 2.10.1 | VERIFIED |
| SCA report in SDR | VERIFIED |

### Phase 4 — Python Lab

| Capability | Status |
|---|---|
| Python Lab API | VERIFIED basic runtime flow |
| Exercise registry / `PY-001` | VERIFIED |
| API → Executor → Sandbox | VERIFIED |
| Normal execution | VERIFIED |
| Incorrect solution handling | VERIFIED |
| Syntax error handling | VERIFIED |
| Timeout protection | VERIFIED |
| Network isolation | VERIFIED |
| Project filesystem isolation | VERIFIED |
| Docker socket isolation | VERIFIED |
| `python_lab` without Docker socket | VERIFIED |
| `python_lab_executor` with Docker socket | VERIFIED |

Phase 4 isolation suite result:

`7 passed`

---

## 5. Definition of V1.0 Complete

V1.0 is complete only when all mandatory tracks below are either **VERIFIED** or explicitly marked **NOT REQUIRED FOR V1.0**.

No item may remain ambiguous.

---

# Track A — Core Platform Closure

### A1. Core runtime stability

Confirm the standard Docker Compose stack starts cleanly and exposes the expected services.

Acceptance:

- orchestrator UP
- target_api UP
- frontend UP
- python_lab UP
- python_lab_executor UP
- no application startup errors

### A2. Existing mission regression

Re-run the minimum regression set for MISSION-001, 002 and 003 after all V1.0 changes.

Acceptance:

- all three remain `VALIDATED`
- no protected behavior regresses

### A3. SDR integrity

Confirm all mission executions continue to emit a valid SDR containing the required fields.

Acceptance:

- mission_id
- status
- controls
- baseline
- observed
- latency
- constraints
- architectural_rationale
- pedagogical_feedback
- DevSecOps reports when applicable

---

# Track B — Learning Experience Closure

### B1. Learning Map

Verify that the Learning Map correctly exposes the current missions and prerequisite behavior.

Acceptance:

- MISSION-001 available as root mission
- MISSION-002 and MISSION-003 respect prerequisites
- no regressions in mission state presentation

### B2. Mission debrief

Verify the frontend displays the outcome and relevant pedagogical feedback from mission execution.

Acceptance:

- successful mission result visible
- failed/constraint-violation result represented correctly
- security rationale visible when applicable

### B3. i18n

Verify that current supported UI text follows the existing EN/ES language policy.

Acceptance:

- English remains default
- Spanish option remains functional
- no newly introduced untranslated mandatory UI text

---

# Track C — Python Lab V1 Closure

### C1. Frontend integration

Validate the complete user-facing flow:

Frontend → Python Lab API → Executor → Sandbox → Result → Frontend

This is distinct from the already-verified backend API flow.

Acceptance:

- user can open the Python Lab
- select an exercise
- submit code
- receive evaluation result
- see test outcomes
- see pedagogical result

### C2. Exercise coverage

Decide the minimum V1.0 exercise set.

Recommended V1.0 starting set:

- `PY-001`
- a basic control-flow exercise
- a basic function/data-processing exercise
- one security-focused Python exercise

The exact set must be explicitly approved before implementation.

### C3. Sandbox security remains protected

The already-verified isolation properties remain mandatory:

- no external network
- no project filesystem access
- no Docker socket
- ephemeral execution
- timeout enforcement
- resource limits
- legitimate execution still works

Any change to sandbox behavior requires re-running the isolation suite.

---

# Track D — Security and DevSecOps Closure

### D1. SAST

Keep the existing Bandit integration stable.

Acceptance:

- existing SAST path still executes
- report remains available in SDR when requested

### D2. SCA

Keep `pip-audit` integration stable.

Acceptance:

- scan executes in the real orchestrator container
- valid JSON is retained
- assessment is available in SDR
- `returncode=0` with no vulnerabilities is represented correctly
- vulnerability exit status is not confused with execution failure

### D3. Security boundaries

No V1.0 change may weaken:

- student-code isolation
- Docker socket separation
- target API isolation
- protected mission contracts

---

# Track E — Operational Closure

### E1. Reproducible startup

Document the minimum commands required to start the project from a clean local checkout.

Acceptance:

- documented commands succeed on the local machine
- no undocumented manual steps are required for V1.0 operation

### E2. Verification runbook

Create a concise verification procedure containing only the commands that materially prove V1.0 health.

The runbook must avoid redundant testing.

### E3. Final evidence snapshot

Capture the final verified state:

- Docker service status
- mission validation results
- Python Lab functional result
- isolation suite result
- Git commit/tag reference

---

# Track F — Versioning and Release

### F1. Release checkpoint

Create a final V1.0 commit after all mandatory tracks pass.

### F2. Release tag

Create:

`v1.0.0`

### F3. Working tree

Acceptance:

`git status --short` returns no unexpected source changes.

Temporary operational documents such as `Deepseek.md` remain outside the release unless explicitly approved.

---

## 6. Explicitly Out of Scope for V1.0

Unless separately approved, do not add these merely because they are possible:

- a new MISSION-004
- new architectural subsystems
- a persistent decision cache
- a new dry-run engine
- broad refactoring
- speculative plugin systems
- new AI agents
- unnecessary database adoption
- new security controls without a mission requirement
- new learning systems without an approved learning objective
- performance optimization without measured evidence of a bottleneck

These may become V2 or separate projects.

---

## 7. Completion Gates

SentinelForge V1.0 passes through four gates.

### Gate 1 — Functional

All mandatory user-facing flows work in the real runtime.

### Gate 2 — Security

All mandatory isolation/security controls are empirically verified.

### Gate 3 — Regression

MISSION-001/002/003 and protected core behavior remain verified.

### Gate 4 — Release

Documentation, runbook, Git state, and release tag are complete.

Only after Gate 4 is the project declared:

**V1.0 COMPLETE**

---

## 8. Working Rule From This Point Forward

For every future task, ask one question first:

> **Is this required to satisfy a V1.0 completion gate?**

If the answer is no, it does not enter the V1.0 implementation queue.

This rule exists to prevent the project from growing indefinitely while implementation progress slows.

---

## 9. Next Immediate Objective

The next implementation target is **Track B/C closure, starting with the user-facing Python Lab integration**, because backend execution and sandbox security are already verified.

Do not modify the core missions to advance this track.

The next cycle is:

**Frontend integration contract → minimal implementation → real browser/runtime validation → regression of protected missions → checkpoint**

---

## 10. Final Success Condition

The project is finished when:

1. every mandatory V1.0 item has objective evidence;
2. no protected core behavior has regressed;
3. no critical security gap remains unverified;
4. the complete user-facing learning flow works;
5. the release is reproducible from the final Git state;
6. no open V1.0 requirement remains.

At that point, further work is explicitly V2 or maintenance—not unfinished V1.0 work.
