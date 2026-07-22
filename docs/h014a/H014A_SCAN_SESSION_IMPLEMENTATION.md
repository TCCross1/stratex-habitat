# H-014A — Scan Session Implementation

Collection: `reality_scan_sessions` (`enums.C_SCANS`).
Source: `backend/reality/scan_session_service.py`.

> **Honest scope:** this is a governed *record + lifecycle state machine only*. There is **no**
> real LiDAR/photogrammetry capture, no device SDK, and no binary ingestion here. `capture_type`
> and `device`/`sensors` are descriptive metadata.

## Capture types (`enums.CAPTURE_TYPES`)
INTERIOR_LIDAR, EXTERIOR_DRONE, EXTERIOR_HANDHELD_LIDAR, PHOTOGRAMMETRY, THERMAL, ROOM_RESCAN,
PARTIAL_AREA, POST_COMPLETION.

## Lifecycle state machine (`SCAN_LEGAL_TRANSITIONS`)
States: CREATED → CAPTURE_READY → CAPTURE_IN_PROGRESS ↔ CAPTURE_PAUSED → UPLOAD_PENDING →
UPLOAD_IN_PROGRESS → UPLOAD_COMPLETE → PROCESSING_PENDING → PROCESSING_IN_PROGRESS →
QUALITY_REVIEW → **ACCEPTED / REJECTED**. Recoverable failures route through
`FAILED_RECOVERABLE`; terminal states = {ACCEPTED, REJECTED, CANCELLED, EXPIRED, FAILED_FINAL}.

`transition_session` enforces:
- `ILLEGAL_TRANSITION` (409) — not in the legal set for the current state.
- `TERMINAL_STATE` (409) — no transitions out of a terminal state.
- `STALE_VERSION` (409) — optimistic-concurrency guard via `expected_version` **and** a
  conditional `update_one({id, version})` (double-checked; conflict audited).
- Actor isolation — non-owner, non-privileged actors get `SCAN_ACCESS_DENIED` (403).

## Idempotency
- **Create:** `idempotency_key` → returns the existing session if already created (no duplicate).
- **Transition:** `idempotency_key` recorded in `processed_idempotency_keys`; a duplicate replay
  returns the current record **without** re-incrementing `version`.

## TTL
`expires_at` computed from `expires_in_seconds` (explicit) or `HABITAT_SCAN_TTL_HOURS`
(default 72h) — env-driven, no hard-coded literal in the record path.

## Endpoints
- `POST /properties/{property_id}/scan-sessions` (201)
- `GET /scan-sessions/{scan_session_id}`
- `POST /scan-sessions/{scan_session_id}/transition`

## Audit
`REALITY_SCAN_SESSION_CREATED`, `REALITY_SCAN_SESSION_TRANSITIONED`,
`REALITY_SCAN_SESSION_REJECTED`, `REALITY_VERSION_CONFLICT`,
`REALITY_CROSS_TENANT_ACCESS_REJECTED`.
