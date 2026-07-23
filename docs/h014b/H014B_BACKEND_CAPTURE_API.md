# H014B Phase 7 — Backend Capture API (extends `/api/reality/v1`)

All routes reuse the H-014A auth (`get_steward_user`) + property authorization
(`authorize_property`, uniform 404 non-disclosure). New modules:
`scan_guardian.py`, `capture_upload_service.py`, `capture.py`, `capture_proof.py`,
`object_store.py`. Router: `backend/reality/router.py` (29 routes total; 12 new).

## New endpoints
| Method | Path | Notes |
|---|---|---|
| GET | `/native-state-map` | Native→canonical mapping reference. |
| POST | `/scan-sessions/{id}/capture-progress` | Record live telemetry. |
| POST | `/scan-sessions/{id}/guardian/evaluate` | Deterministic Guardian; persists result. |
| POST | `/scan-sessions/{id}/uploads` | Init resumable upload. |
| GET | `/uploads/{uid}` | Upload status (resume). |
| PUT | `/uploads/{uid}/chunks/{index}` | Stream a chunk (raw body). |
| POST | `/uploads/{uid}/complete` | Assemble + verify + store + manifest. |
| POST | `/uploads/{uid}/abort` | Discard staged chunks. |
| POST | `/scan-sessions/{id}/candidate` | Generate DRAFT_CANDIDATE. |
| GET | `/artifacts/{aid}/content` | Authorized backend-mediated download. |
| POST | `/development/capture-proof/bootstrap` | Dev/test end-to-end proof (fixture-gated). |
| GET | `/development/capture-proof` | Dev/test proof review payload. |

## New collections + indexes
- `reality_upload_sessions` (`ux_upload_id`, `ix_upload_scan`, `ix_upload_state`, `ix_upload_expires`).
- `reality_upload_chunks` (`ux_chunk_session_index` unique on `(upload_session_id, index)`).

## New audit events
`REALITY_CAPTURE_PROGRESS_RECORDED`, `REALITY_UPLOAD_INITIATED`,
`REALITY_UPLOAD_COMPLETED`, `REALITY_UPLOAD_CHECKSUM_MISMATCH`,
`REALITY_UPLOAD_ABORTED`, `REALITY_SCAN_GUARDIAN_EVALUATED`,
`REALITY_CANDIDATE_MODEL_GENERATED`, `REALITY_CAPTURE_PROOF_BOOTSTRAPPED`.
All sanitized (no bytes/tokens/signed URLs/PII), tenant/property/actor-bound.

## Isolation & non-regression
- The dev capture proof writes to a **separate synthetic property**
  `ref-property-h014b-capture` so it never perturbs the H-014A reference room
  (`ref-property-h014a`).
- Additive only: no accepted H-014A model/route/test changed. Full backend suite
  **243 passed, 1 skipped** (pre-existing unrelated live-render skip).

## Fail-closed in production
`/development/*` capture-proof endpoints are fixture-gated (`fixture_provider`);
they return `403 FIXTURES_DISABLED` when fixtures are disabled/production.
