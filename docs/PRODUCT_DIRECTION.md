# Try Hack Learn — Product Direction and Scope

**Status:** Approved product direction  
**Audience:** Product and engineering  
**Language:** English

## 1. Product vision

Try Hack Learn is a personal cybersecurity learning-platform project for creating, validating, publishing, and studying original hands-on learning tracks.

The initial creator is the project owner. Learners can access published tracks without requiring learner accounts in the MVP.

The product is not intended to clone TryHackMe or reproduce third-party protected learning content. Tracks, explanations, scenarios, and challenges must be original or properly licensed.

**Product promise:** Create. Validate. Learn.

## 2. Primary product workflow

1. Define a learning track with a title, description, audience, difficulty, prerequisites, and measurable learning objectives.
2. Organize the track into ordered modules.
3. Add original learning content, references, challenges, hints, and completion criteria.
4. Associate a module or challenge with an existing controlled lab where appropriate.
5. Validate the track definition and its executable challenges.
6. Publish an immutable, versioned track release.
7. Let visitors study the published track and execute supported exercises.
8. Preserve validation results and release provenance.

## 3. MVP scope

The MVP is deliberately single-author and low-complexity.

### In scope

- One trusted track author: the project owner.
- Version-controlled track definitions, preferably declarative YAML or JSON with Markdown content.
- Track, module, challenge, prerequisite, and learning-objective models.
- Reuse of existing missions, Target API scenarios, and Python Lab exercises through explicit adapters/contracts.
- Structural and semantic content validation.
- Automated challenge and lab validation where an executable test contract exists.
- Draft and published track versions.
- A public/read-only learning catalogue for published content.
- Local learner progress without accounts, with its limitations documented.
- Reproducible validation reports with track version, validator version, timestamp, checks, and outcomes.
- English and Spanish UI support consistent with existing project policy.

### Explicitly out of scope

- Learner accounts, authentication, profiles, and multi-device synchronization.
- Multiple authors, teams, roles, and complex permissions.
- Marketplace, payments, subscriptions, comments, chat, and social features.
- Complex gamification or multi-user analytics.
- Kubernetes, event streaming, and additional infrastructure without measured need.
- A generic plugin marketplace or unnecessary microservices.

The content model should avoid assumptions that make future multi-author support impossible, but no multi-author functionality should be implemented in the MVP.

## 4. Product principles

- **Evidence over claims:** distinguish IMPLEMENTED, TESTED, and VERIFIED. A successful content/schema check is not proof of lab security.
- **Original learning:** create original scenarios and explanations; do not copy protected third-party tracks.
- **Security by design:** treat authored lab definitions and learner-submitted code as untrusted inputs at execution boundaries.
- **Reproducibility:** published releases are immutable and identify their content revision and validation evidence.
- **Small architecture:** prefer modular components and explicit contracts over new services.
- **Preserve working behavior:** existing missions, SDR contracts, Arena flows, and Python Lab behavior must not regress without an approved ADR and regression evidence.
- **No premature platform features:** do not add identity, multi-tenancy, or collaboration until a concrete product requirement justifies them.

## 5. Track validation lifecycle

Recommended lifecycle:

- DRAFT
- VALIDATING
- VALIDATION_FAILED
- VALIDATED
- PUBLISHED
- DEPRECATED

A release may be published only when all mandatory checks for its declared content types pass.

Validation should cover, as applicable:

1. Schema and metadata.
2. Required learning objectives and module structure.
3. Internal references and prerequisite consistency.
4. Challenge contract and expected-result definitions.
5. Executable challenge tests, including negative cases.
6. Lab startup, teardown, resource limits, and isolation checks.
7. Content and dependency integrity.
8. Release manifest and provenance.

A VALIDATED status means only that the declared validation suite passed. It must never be represented as a general security certification.

## 6. Architecture direction

Keep the current Docker Compose-based application and its existing services while responsibilities are clarified.

Introduce the track/content domain as modular application code first, not as a new microservice by default:

- Track catalogue and definitions.
- Track validation engine.
- Publication/version manifest.
- Adapters to existing missions and Python Lab contracts.

The frontend should consume stable backend contracts. It must not call the executor or vulnerable Target API directly.

The current Docker-socket-based executor remains restricted to a trusted local development/demo environment. It is not approved for public or untrusted multi-user execution. A separate hardened execution boundary is required before that deployment model is considered.

## 7. Professional demonstration objective

The project should provide a short, reproducible technical demonstration:

1. Inspect an original track definition.
2. Run track validation.
3. Show a deliberately invalid challenge being rejected.
4. Run a valid lab/challenge.
5. Show automated test outcomes and a versioned evidence report.
6. Explain the service boundaries, security controls, CI pipeline, and known limitations.

The project should demonstrate Python Backend, Application Security, testing, architecture, and DevSecOps through working evidence rather than technology count.

## 8. Delivery priorities

1. Reconcile the existing V1.0 completion roadmap with this approved product direction without discarding its verified baseline.
2. Audit the current architecture and runtime behavior; preserve existing mission and SDR contracts.
3. Address mission execution state isolation and failure handling.
4. Strengthen and empirically verify sandbox isolation.
5. Close the existing Python Lab and core platform regression checks.
6. Implement the minimal track content model and validator.
7. Implement versioned publication and the learner-facing catalogue.
8. Complete CI security checks, documentation, and a reproducible demonstration.

## 9. Change control and repository governance

- Do not commit directly to protected `master`.
- Work on task-specific branches and use pull requests.
- Do not merge pull requests without explicit user authorization.
- Inspect README, `AGENTS.md`, roadmap, architecture, and Git state before material changes.
- Preserve untracked/staged local files and user work.
- Do not claim runtime verification without actual runtime evidence.
- Document architectural changes and material trade-offs.

## 10. Relationship to the existing completion roadmap

This document records the newly approved product direction. It does not erase the existing V1.0 baseline or its verification evidence.

Before implementing the Track Engine, reconcile `PROJECT_COMPLETION_ROADMAP.md` with this direction: identify which existing V1.0 closure gates remain mandatory, which product requirements are deferred, and whether the Track Engine is a post-V1.0 milestone or an explicitly approved revision to the release scope. Do not silently treat the prior frozen scope as either cancelled or unchanged.
