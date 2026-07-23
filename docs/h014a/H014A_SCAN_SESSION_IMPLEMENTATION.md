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
- Actor isolation — non-owner, non-privileged actors get `SCAN_ACCESS_DENIED` (403)
  (same-tenant action authz). Cross-tenant scan lookups use uniform **404 NOT_FOUND**
  (H-014A.2 non-disclosure).

## Idempotency (H-014A.2 database-backed)
- **Create:** scoped unique partial index on
  `tenant_id + property_id + actor_id + create_idempotency_key`. Replay returns the original
  session; concurrent duplicates collapse via `DuplicateKeyError`. Another property may reuse
  the same external key safely.
- **Transition:** unique claim in `reality_scan_transition_idempotency`
  (`scan_session_id + idempotency_key`) plus `processed_idempotency_keys` on the session.
  Replay / concurrent duplicate → one state change and **no** duplicate audit event.

## TTL
`expires_at` computed from `expires_in_seconds` (explicit) or `HABITAT_SCAN_TTL_HOURS`
(default 72h) — env-driven, no hard-coded literal in the record path.
**H-014A.2:** `expires_at` is workflow/state invalidation only (ordinary index). It is **not**
a Mongo TTL delete index; physical deletion requires an approved retention policy.

## Endpoints
- `POST /properties/{property_id}/scan-sessions` (201)
- `GET /scan-sessions/{scan_session_id}`
- `POST /scan-sessions/{scan_session_id}/transition`

## Audit
`REALITY_SCAN_SESSION_CREATED`, `REALITY_SCAN_SESSION_TRANSITIONED`,
`REALITY_SCAN_SESSION_REJECTED`, `REALITY_VERSION_CONFLICT`,
`REALITY_CROSS_TENANT_ACCESS_REJECTED`.
