# H014B Phase 5 — Native Capture → Backend Scan-State Mapping

Native states live only on the device for UX; the **backend scan-session state
machine (H-014A) is the single source of truth**. Each native state maps to
exactly one canonical backend state.

Backend: `backend/reality/enums.py::NATIVE_TO_SCAN_STATE` + `capture.map_native_state`.
iOS: `CaptureState.backendScanState`. Reference endpoint:
`GET /api/reality/v1/native-state-map`.

| Native (`CaptureState`) | Canonical backend scan state |
|---|---|
| `IDLE` | `CREATED` |
| `AUTHORIZED` | `CREATED` |
| `READY` | `CAPTURE_READY` |
| `CAPTURING` | `CAPTURE_IN_PROGRESS` |
| `PAUSED` | `CAPTURE_PAUSED` |
| `FINALIZING` | `UPLOAD_PENDING` |
| `UPLOADING` | `UPLOAD_IN_PROGRESS` |
| `UPLOADED` | `UPLOAD_COMPLETE` |
| `PROCESSING` | `PROCESSING_IN_PROGRESS` |
| `COMPLETE` | `QUALITY_REVIEW` |
| `FAILED` | `FAILED_RECOVERABLE` |
| `CANCELLED` | `CANCELLED` |

## Enforcement
- The device may pre-check local transitions (`CaptureState.allowedNext`), but the
  backend independently enforces `SCAN_LEGAL_TRANSITIONS` with optimistic
  concurrency + idempotency. An illegal transition returns `409 ILLEGAL_TRANSITION`.
- `map_native_state("<unknown>")` → `422 UNKNOWN_NATIVE_STATE`.
- Acceptance (`QUALITY_REVIEW → ACCEPTED/REJECTED`) is a **governed** action; the
  Guardian only recommends. There is **no native→VERIFIED_EXISTING path**.

## Capture progress
`POST /api/reality/v1/scan-sessions/{id}/capture-progress` records live telemetry
(`native_state`, `mapped_scan_state`, coverage, tracking, frame count) on the scan
session and audits `REALITY_CAPTURE_PROGRESS_RECORDED`. It does not itself
transition state.

Tests: `TestNativeStateMapping` (backend), `testNativeStateMappingMatchesBackend`
(iOS), `TestGuardianAndCandidateHTTP::test_capture_progress_records_state`.
