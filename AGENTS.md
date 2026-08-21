Read AGENTS.md before doing anything. It is the project governance authority.

# SENTINELFORGE — AGENT GOVERNANCE

This file is authoritative project guidance.

Before modifying code, read this file.

## SOURCE OF TRUTH

The local repository and real Docker runtime are the source of truth.

Source inspection, mocks, simulations, generated reports, or theoretical reasoning
MUST NOT be presented as runtime verification.

## VERIFICATION STATES

IMPLEMENTED = code exists but runtime was not verified.

NOT VERIFIED = insufficient evidence.

BLOCKED = verification could not be performed.

VERIFIED = the real product flow was executed successfully on the local machine.

Never claim VERIFIED, PASS, READY, or COMPLETE without real runtime evidence.

## PRODUCT-FIRST RULE

Priority:

1. Keep the product running.
2. Preserve existing working missions.
3. Preserve existing API contracts.
4. Preserve the SDR contract.
5. Preserve the learning experience.
6. Add complexity only when justified.

Do not modify working functionality merely to make a test pass.

## TESTING

Do not create large test suites by default.

Use the smallest validation necessary.

Prefer real end-to-end validation when appropriate.

Unit tests are supporting evidence, not proof that the product works end-to-end.

## LOCAL VALIDATION

When runtime verification is required, provide the exact command
for the user to execute locally.

Do not invent command output.

Do not assume success.

Wait for the user's actual output before declaring VERIFIED.

If an error occurs:

1. Diagnose the actual error.
2. Explain the likely cause.
3. Provide one concrete next step.
4. Wait for the result.

Do not provide many speculative fixes simultaneously.

## ARCHITECTURAL PROTECTION

Do not change:

- API contracts
- SDR structure
- Probe Engine behavior
- existing working frontend flows
- scenario contracts

without explicit authorization.

## LANGUAGE

Project language is English by default.

Spanish is the only alternative user-selectable language.

Do not introduce other project languages without explicit authorization.

## CURRENT BASELINE

Verified:

- Core Docker environment
- MISSION-001
- MISSION-003
- Frontend
- Learning Map
- Learning persistence
- prerequisites
- EN/ES
- Mission Debrief

Implemented but not currently runtime-verified:

- MISSION-002
- SAST / Bandit

Blocked / not verified:

- SCA / Safety / pip-audit

## STOP RULE

If something cannot be verified in the real local environment:

STOP.

Report:

STATUS: NOT VERIFIED

Do not manufacture a PASS result.

## DELIVERY

When files are changed:

- list every changed file;
- explain the purpose of each change;
- provide generated files when actually available;
- never claim a file was delivered if it was not actually produced.

## IMPORTANT

The goal is not to make the project appear complete.

The goal is to make the product actually work.