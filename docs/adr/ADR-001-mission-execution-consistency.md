# ADR-001: Mission execution consistency in the current Compose runtime

- **Status:** Proposed for implementation
- **Date:** 2026-11-24
- **Scope:** Current single-instance trusted local demo
- **Related:** `PROJECT_COMPLETION_ROADMAP.md`, `docs/PRODUCT_DIRECTION.md`

## Context

The Target API stores the active mission and controls in a process-global mutable object:

```python
RUNTIME_STATE = {
    "mission_id": "NONE",
    "active_controls": []
}
```

The Orchestrator deploy flow applies an empty control set, runs a baseline probe campaign, applies the selected controls, and runs an observed campaign. Both probe campaigns read the same Target API global state.

Two overlapping deploy requests can interleave these operations. One request may therefore run probes using controls applied by another request. The resulting SDR can be internally consistent in shape while representing the wrong experiment.

The current Compose Dockerfiles start Uvicorn with its default single worker. This is relevant to a process-local lock but must not be treated as a permanent distributed-concurrency guarantee. The Target API also publishes host port 8001, exposing its internal control-application endpoint to the host network.

## Decision for the current MVP

Use a deliberately constrained single-instance execution model until mission state is made request-scoped:

1. Serialize complete mission deployments in the Orchestrator with an asynchronous process-local lock. The critical section must include reset, baseline, control application, observed probes, and SDR construction.
2. Keep the Orchestrator at one worker while using this lock. Document that multiple workers or replicas invalidate the guarantee.
3. Apply explicit HTTPX timeouts and call `raise_for_status()` after every control-application request. A failed control application must abort the mission and must never produce a normal validated SDR.
4. Remove the Target API host port publication if repository/runtime usage confirms no supported user-facing workflow depends on direct host access. The Orchestrator should remain its only caller through the private Compose network.
5. Add a focused regression test that forces two deploy requests to overlap and proves their reset/apply/probe sequences cannot interleave.
6. Preserve mission IDs, execution contracts, response shape, and SDR schema.

This is an MVP containment measure, not the final scalable architecture.

## Alternatives considered

### Request-scoped mission context

Pass an explicit immutable execution context or run identifier through the Orchestrator, probe requests, and Target API handlers. This is the preferred long-term design because it permits safe concurrency, but it changes internal request contracts and requires broader integration coverage.

### Distributed lock

A Redis/database lock would add infrastructure and operational complexity. It is not justified for the current single-instance local MVP.

### Leave the global state unchanged

Rejected. Concurrent runs can corrupt experimental correctness without producing an obvious error.

## Consequences and limitations

- Mission executions become serialized and may wait behind another run.
- A process-local lock only coordinates requests handled by the same Orchestrator process.
- One worker/one replica is an explicit deployment constraint.
- The host-published Target API port is an unnecessary attack surface if no supported workflow requires it.
- The long-term request-scoped context design should be reconsidered before multi-instance deployment.

## Acceptance criteria

- A deterministic concurrency regression test demonstrates no interleaving of mission execution phases.
- HTTP failures during reset or control application abort the mission.
- Timeout and upstream failure paths return stable API errors and do not create a misleading successful SDR.
- Existing mission regression tests pass.
- Local Docker runtime verifies at least two overlapping requests and the normal sequential mission flow.
- No claim of distributed concurrency safety is made.

## Verification status

**NOT IMPLEMENTED. NOT VERIFIED.**

This ADR records the proposed containment decision. Implementation must be reviewed against existing tests and local runtime behavior before it is treated as accepted architecture.
