# Steward Workflow Security & Recovery (H-013 Batch 2, Phases 6, 8, 9)

**Module:** `backend/workflow.py`

## Authorization / isolation
- All `/api/steward/workflow/*` routes require the authenticated **homeowner** tenant; other roles (e.g. contractor) receive **403**; unauthenticated -> **401**.
- `_load()` enforces `homeowner_id` + `tenant_id` match on every read/write -> cross-tenant / cross-owner access returns **403**.
- Publish verifies the request `property_id` matches the workflow's property (else `PROPERTY_MISMATCH`).

## Publication gate (Phase 6) — backend-authoritative
`evaluate_publication_gate()` (pure, unit-tested) requires ALL of:
- state in {PACKAGE_PREVIEWED, PUBLICATION_APPROVED}
- explicit `approval == true`
- present `design_project_ref`, `estimate_snapshot`, `contractor_package_version`, `redaction_settings`
- property match
- **no unresolved HARD blockers** and **all required CONDITIONAL acknowledgments** — readiness is **recomputed on the server** from `acknowledged_blockers`; a frontend-supplied readiness/`can_publish` payload is ignored and cannot bypass the gate.

Blocked publication returns **409** with `{error_code:"PUBLICATION_BLOCKED", blocking_item_ids, reason, remediation_actions, correlation_id}` and writes a `PUBLICATION_BLOCKED` audit event.

## Idempotency & concurrency (Phase 8)
- **Optimistic concurrency:** every mutating write is a conditional update on `{id, version}`; a lost race returns **409 `STALE_VERSION`**. Optional `expected_version` in the request is enforced when supplied.
- **Idempotent replay:** `processed_idempotency_keys` short-circuits repeated transitions; `create_idempotency_key` de-dupes creation; `publication_idempotency_key` returns the SAME opportunity on replay.
- **Single-publish guarantee:** publication is an atomic conditional claim `{id, version, opportunity_ref:null, state in [...]}` -> only one concurrent request wins; the loser returns the existing opportunity (no duplicate).
- **Expiry:** `expires_at` (TTL `HABITAT_WORKFLOW_TTL_HOURS`, default 72h); accessing an expired non-terminal workflow transitions it to `EXPIRED` + audit. (Dev/test may pass `expires_in_seconds` on create to exercise expiry.)
- **Recovery:** projection failure and publish-persistence failure move the workflow to `FAILED_RECOVERABLE` for retry.

## Transactional integrity
On publish, the atomic state claim happens first; then audit + opportunity are persisted. If that persistence raises, a **compensating update** reverts the workflow to `FAILED_RECOVERABLE` and clears `opportunity_ref` (no published opportunity is left without its audit/opportunity record). Note: MongoDB single-document updates are atomic; this is a compensating pattern, not a multi-document ACID transaction.

## Audit events (Phase 9) — collection `audit_events`
`STEWARD_WORKFLOW_CREATED, STEWARD_CONTEXT_RESOLVED, HOMEOWNER_ACTION_CONFIRMED, DESIGN_PROJECT_CREATED, ESTIMATE_SNAPSHOT_CREATED, READINESS_ASSESSED, HARD_BLOCKER_DETECTED, CONDITIONAL_BLOCKER_ACKNOWLEDGED, CONTRACTOR_PACKAGE_PREVIEWED, PUBLICATION_APPROVED, PROJECT_OPPORTUNITY_PUBLISHED, PUBLICATION_BLOCKED, WORKFLOW_CANCELLED, WORKFLOW_EXPIRED`.
Each event stores tenant, property, actor, workflow id, correlation id, timestamp, event version, entity references, and before/after state. **No secrets, full documents, or raw evidence are logged.**
