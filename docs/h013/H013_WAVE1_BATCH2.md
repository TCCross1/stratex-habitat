# H-013 Wave 1 — Batch 2 Summary

**Repository:** TCCross1/Habitat · **Branch:** copilot/tcc-1-update-documentation
**Starting commit:** `07fd2b0` (Batch 1, accepted by General Atlas)
**Scope:** Phases 1-12. Extends the accepted Batch 1 architecture. No new repo/branch/PR, no `main` merge, roof-reference workflow only.

> Git writes are performed by the operator via "Save to GitHub" after review. All changes are staged in the working tree.

## Delivered
| Phase | Capability | Status |
|---|---|---|
| 1 | Recon + Batch 1 preservation | `docs/h013/H013_BATCH2_RECON.md` |
| 2-3 | Versioned read-only Passport projection adapter + provider modes | `backend/passport_projection.py` |
| 4 | Steward context served via adapter (fail-safe in production) | `backend/steward.py` `/context` |
| 5 | Build-Ready blocker policy (4 levels) | `backend/readiness_policy.py`, `/readiness` |
| 6 | Backend publication-gate enforcement | `backend/workflow.py` |
| 7 | Persistent `steward_workflows` state machine | `backend/workflow.py` |
| 8 | Resume / retry / idempotency / concurrency / expiry | `backend/workflow.py` |
| 9 | Immutable audit events | `backend/workflow.py` -> `audit_events` |
| 10 | Indexes ensured at startup | `backend/workflow.py`, `backend/server.py` |
| 11 | Executable tests (projection/readiness/workflow/security/regression) | `backend/tests/test_h013_*.py` |
| 12 | Documentation | `docs/h013/*.md` |

## New backend modules
- `passport_projection.py` — adapter, providers (production HTTP / dev seed / demo / test fixture), validation, staleness, circuit breaker.
- `readiness_policy.py` — HARD / CONDITIONAL / WARNING / INFORMATIONAL classification + `assess()`.
- `workflow.py` — state machine, publication gate, idempotency, audit, indexes, router.

## Config (backend/.env; additive)
`HABITAT_PROJECTION_MODE=development`, `HABITAT_PROJECTION_CONTRACT_VERSION=1.0.0`, `HABITAT_WORKFLOW_TTL_HOURS=72`. `HABITAT_PROJECTION_BASE_URL` intentionally UNSET so production fails safe. Protected URL vars untouched.

## Verification (this environment)
- Unit tests: `pytest tests/test_h013_security.py tests/test_h013_projection.py tests/test_h013_readiness.py tests/test_h013_workflow.py` -> **39 passed**.
- Backend testing agent (HTTP): **23/23 passed** (projection, readiness, full workflow lifecycle, security/anti-bypass, regression).
- Frontend testing agent (Steward wizard regression): **9/9 passed**, fully backward-compatible.

## Known limitations / honest status
- **No real Passport/Core projection endpoint** is wired (none available here); production mode is proven to **fail safe (503)**, not proven against a live service. This remains a **MOCK-free but unwired** production boundary.
- Legacy `POST /api/steward/publish` (H-012) remains for backward compatibility and is **not** behind the new workflow publication gate; the governed path is `POST /api/steward/workflow/{id}/publish`.
- Indexes are ensured at startup; a production deploy should run an explicit index migration (not executed against any production cluster here).
- No coverage instrumentation, benchmark suite, observability, or deployment was performed (out of scope per STOP CONDITION).
- `backend_test.py` remains a Batch 1 agent artifact (hard-coded preview URL) pending cleanup; not the Batch 2 authoritative suite.

## NOT started (per mission)
Interior/Exterior Reality Studio, additional project types, coverage instrumentation, benchmarks, observability, deployment/rollback, pilot execution.
