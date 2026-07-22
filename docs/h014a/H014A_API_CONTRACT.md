# H-014A — API Contract

Base prefix: `/api/reality/v1` (`enums.API_PREFIX`). Router: `backend/reality/router.py`.
All routes require authentication via `steward.get_steward_user` and property authorization via
`authz.authorize_property`. Errors use a structured body: `{"detail": {"error_code", "message"}}`.

## Endpoints (17 registered — verified against `app.routes`)
### Spatial graph
- `GET  /properties/{property_id}/spatial-graph` — counts + entities.
- `POST /properties/{property_id}/spatial-entities` (201) — truth-guarded create.

### Coordinate frames
- `POST /properties/{property_id}/coordinate-frames` (201)
- `GET  /properties/{property_id}/coordinate-frames`
- `GET  /coordinate-frames/{coordinate_frame_id}`

### Scan sessions
- `POST /properties/{property_id}/scan-sessions` (201)
- `GET  /scan-sessions/{scan_session_id}`
- `POST /scan-sessions/{scan_session_id}/transition`

### Artifact manifests
- `POST /scan-sessions/{scan_session_id}/artifacts` (201)
- `GET  /artifacts/{artifact_id}` (metadata-only public view)

### Existing model versions
- `POST /properties/{property_id}/existing-models` (201)
- `GET  /existing-models/{existing_model_version_id}`
- `POST /existing-models/{existing_model_version_id}/transition`

### Design model versions
- `POST /properties/{property_id}/design-models` (201)
- `GET  /design-models/{design_model_version_id}`

### Reference room (dev/test; fail-closed in production)
- `POST /development/reference-room/bootstrap`
- `GET  /development/reference-room`

## Representative error codes
| HTTP | error_code |
|---|---|
| 401 | (unauthenticated) |
| 403 | PROPERTY_ACCESS_DENIED, SCAN_ACCESS_DENIED, MODEL_ACCESS_DENIED, TRUTH_PROMOTION_FORBIDDEN, FIXTURES_DISABLED |
| 404 | resource not found (non-disclosure) |
| 409 | ILLEGAL_TRANSITION, TERMINAL_STATE, STALE_VERSION, MODEL_IMMUTABLE, BASE_MODEL_NOT_ACCEPTED |
| 422 | INVALID_MATRIX, NON_FINITE_MATRIX, INVALID_HOMOGENEOUS_ROW, INVALID_CHECKSUM, INVALID_STORAGE_REFERENCE, INVALID_ARTIFACT_TYPE, CROSS_PROPERTY_ARTIFACT, INVALID_DESIGN_TRUTH, BASE_MODEL_NOT_FOUND, INVALID_ENTITY_TYPE, ORPHAN_OPENING, ENTITY_CYCLE |

## Request schemas
`backend/reality/schemas.py` — Pydantic v2 models with `extra='ignore'` (default), so
client-supplied `tenant_id`/`property_id` overrides are silently dropped (never reach the service).
