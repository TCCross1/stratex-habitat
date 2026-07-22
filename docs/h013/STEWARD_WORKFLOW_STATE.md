# Steward Workflow State (H-013 Batch 2, Phases 7-10)

**Module:** `backend/workflow.py` · **Collection:** `steward_workflows`
**Tested:** 10 unit tests + full HTTP lifecycle (backend testing agent 23/23).

## States
`QUESTION_RECEIVED, CONTEXT_RESOLVED, ANSWER_PRESENTED, ACTION_RECOMMENDED, ACTION_CONFIRMED, PROJECT_CREATED, ESTIMATE_CREATED, SCENARIOS_REVIEWED, READINESS_REVIEWED, PACKAGE_PREVIEWED, PUBLICATION_APPROVED, OPPORTUNITY_PUBLISHED, CANCELLED, EXPIRED, FAILED_RECOVERABLE, FAILED_FINAL`.

Terminal: `OPPORTUNITY_PUBLISHED, CANCELLED, EXPIRED, FAILED_FINAL`.

## Legal transitions (`LEGAL_TRANSITIONS`)
Forward chain QUESTION_RECEIVED -> ... -> PACKAGE_PREVIEWED -> PUBLICATION_APPROVED -> OPPORTUNITY_PUBLISHED. Every active state also permits `CANCELLED` and `EXPIRED`; several permit `FAILED_RECOVERABLE`, which can retry to selected forward states. Illegal transitions return **409 `ILLEGAL_TRANSITION`**. Publication is NOT reachable via the generic transition endpoint (`OPPORTUNITY_PUBLISHED` requires `POST /publish`).

## Persisted fields (per Phase 7)
`id, tenant_id, property_id, homeowner_id, current_state, version, correlation_id, question, context_projection_ref/version, steward_response_ref, recommended_action, confirmation_event_id, confirmation_idempotency_key, design_project_ref, estimate_snapshot, investment_scenario_ref, readiness_ref, readiness_assessment, acknowledged_blockers[], contractor_package_version, redaction_settings, publication_approval, publication_idempotency_key, opportunity_ref, create_idempotency_key, processed_idempotency_keys[], cancelled, cancel_reason, created_at, updated_at, expires_at, state_history[]`.

## Endpoints (base `/api/steward/workflow`)
| Method | Path | Purpose |
|---|---|---|
| POST | `` | Create (idempotent via `idempotency_key`) |
| GET | `` | List homeowner workflows |
| GET | `/{id}` | Resume/reload |
| POST | `/{id}/transition` | Advance state (server computes context/estimate/readiness/package refs) |
| POST | `/{id}/acknowledge` | Acknowledge a conditional blocker |
| POST | `/{id}/publish` | Gated publication |
| POST | `/{id}/cancel` | Safe cancellation |

## Server-computed step data
- CONTEXT_RESOLVED -> projection adapter (fails safe to `FAILED_RECOVERABLE` + 503 if unavailable).
- ESTIMATE_CREATED -> `pricebook.planning_estimate` snapshot (`price_book_version 2026.07.0`).
- READINESS_REVIEWED -> `readiness_policy.assess(acknowledged_blockers)` snapshot.
- PACKAGE_PREVIEWED -> generated `contractor_package_version` + `redaction_settings`.

## Indexes (Phase 10 — created at startup, `init_indexes`)
Unique `id`; `tenant+property`; `tenant+homeowner`; `current_state`; `updated_at`; `expires_at`; sparse `publication_idempotency_key`; sparse `confirmation_idempotency_key`.

**Production migration note:** indexes are ensured on application startup in this environment via `init_indexes`. A production rollout should run an explicit migration/`createIndexes` step during deploy rather than relying solely on startup; this has **not** been executed against any production cluster here.
