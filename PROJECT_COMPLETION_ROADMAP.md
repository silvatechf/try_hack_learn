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

The Python Lab frontend already contains the guided, assisted, and free-code learning flow. The frontend integration hardening now separates API transport handling from the React view, makes the API base URL configurable, enforces the documented code-length limit in the client, and presents technical execution status separately from pedagogical feedback.

The next objective is **real browser/runtime verification of Track C1**, not another frontend subsystem.

Do not modify the core missions to advance this track.

The next cycle is:

**Frontend API client tests → production build → browser execution and failure-path checks → regression of protected missions → checkpoint**

The frontend implementation remains **IMPLEMENTED; NOT VERIFIED** until the local build and browser flow are executed and their actual outputs are recorded.

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


---

# 11. Product-direction reconciliation — 2026-11-24

**Authority:** This section reconciles the existing V1.0 closure plan with `docs/PRODUCT_DIRECTION.md`. It does not retroactively upgrade historical verification claims.

## 11.1 Product identity

The repository's current product identity is **Try Hack Learn**. Legacy SentinelForge identifiers in API titles, storage keys, package metadata, and internal names are technical debt. Do not perform a broad rename as part of this reconciliation; inventory compatibility impact first.

The approved product direction is a single-author cybersecurity learning platform:
- The project owner is the only author in the MVP.
- Published tracks are available to learners without learner accounts.
- No multi-author, identity, marketplace, payment, collaboration, or multi-tenant features are included.
- Original or properly licensed learning content only.

## 11.2 Release sequencing decision

The existing V1.0 scope remains a stabilization and evidence-closure milestone for the current platform. The Track Engine and Creator Workflow are **post-V1.0 product evolution (provisionally V1.1)**, not silently added to the frozen V1.0 release.

This sequencing avoids expanding a release whose existing functional, security, and runtime gates are not yet closed. It also preserves the current mission, SDR, Learning Map, and Python Lab baseline.

V1.0 closure does not mean production or public multi-user readiness. The Docker-socket executor remains a trusted-local-demo constraint. Remote or untrusted code execution requires a separately designed and verified execution boundary.

## 11.3 V1.0 closure — retained scope

The following remain the V1.0 closure priorities:
1. Reconcile historical verification claims with current branch evidence and the current runtime.
2. Complete the current frontend-to-Python-Lab user flow and failure-path checks.
3. Re-run regression for MISSION-001, MISSION-002, and MISSION-003 without changing their contracts.
4. Verify SDR structure and persistence behavior.
5. Strengthen sandbox isolation evidence using actual runtime/container configuration; existing smoke tests are not sufficient by themselves.
6. Close service-boundary issues required for the documented trusted-local-demo deployment.
7. Complete reproducible startup, verification runbook, CI evidence, and release documentation.

A status in the historical table above is a recorded baseline claim, not proof that the current PR stack has revalidated it. Current branch/runtime evidence takes precedence.

## 11.4 Post-V1.0 — Track Engine MVP

After V1.0 closure, implement the smallest useful Track Engine:
- Declarative track definitions in version-controlled YAML/JSON with Markdown learning content.
- Track, module, learning-objective, prerequisite, and challenge contracts.
- Reuse existing mission and Python Lab capabilities through explicit adapters; do not duplicate their execution engines.
- Structural/content/reference validation.
- Executable challenge validation only where a deterministic test contract exists.
- Draft and immutable versioned published releases.
- A read-only catalogue for published tracks.
- Local learner progress without accounts, with browser-local limitations documented.
- Validation reports that identify track revision, validator version, checks, timestamps, and results.

The validation result must describe exactly which checks ran. `VALIDATED` is not a general security certification and must not imply that sandbox isolation is proven.

## 11.5 Explicitly deferred

No implementation of learner accounts, multi-author support, roles, complex authorization, marketplace, payments, comments, chat, multi-tenant analytics, Kubernetes, event streaming, or speculative microservices is authorized by this product direction.

## 11.6 Next engineering decision

Before changing mission execution state, document the concurrency model and select a minimal safe strategy for the current single-instance Compose runtime. The current Target API uses shared mutable global runtime state. Concurrent mission runs can overwrite each other's controls between baseline and observed probe campaigns. Any fix must preserve mission and SDR contracts and include a regression test for overlapping executions.

Do not claim this risk is resolved until the chosen implementation has passed tests and a real local runtime check.
