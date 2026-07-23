# H014B Phase 4 — AI Scan Quality Guardian (deterministic)

Backend: `backend/reality/scan_guardian.py` · Mirror: `ios/.../ScanQualityGuardian.swift`
· `guardian_version = 1.0.0`.

## Design
Despite the "AI" name, the Guardian is **deterministic and rule-based**: the same
capture-quality report always yields the same verdict, score, findings and
coverage state. This makes it reproducible, auditable, and safe to run identically
on-device (pre-flight) and on the backend (authoritative gate). It **only
recommends** — the governed scan-session state machine remains the sole authority
for acceptance. It never fabricates geometry.

## Fixed thresholds (PLANNING tolerance)
| Check | PASS | WARN | Direction |
|---|---|---|---|
| Wall coverage | ≥ 0.85 | ≥ 0.60 | higher better |
| Floor coverage | ≥ 0.80 | ≥ 0.50 | higher better |
| Ceiling coverage | ≥ 0.70 | ≥ 0.40 | higher better |
| Tracking mean | ≥ 0.80 | ≥ 0.60 | higher better |
| Tracking limited fraction | ≤ 0.10 | ≤ 0.30 | lower better |
| Drift (m) | ≤ 0.05 | ≤ 0.15 | lower better |
| Low-quality frame fraction | ≤ 0.15 | ≤ 0.35 | lower better |
| Captured/expected area ratio | ≥ 0.90 | ≥ 0.70 | higher better |
| Min captured area | 4.0 m² (else `INSUFFICIENT_AREA` FAIL) | | |
| Frame count | ≥ 240 recommended; < 120 → FAIL | | |

## Finding codes
`WALL/FLOOR/CEILING_COVERAGE_LOW`, `MISSING_WALL`, `TRACKING_DEGRADED`,
`TRACKING_LIMITED_FRACTION`, `DRIFT_EXCEEDED`, `INSUFFICIENT_AREA`,
`AREA_INCOMPLETE`, `LOW_FRAME_QUALITY`, `FRAME_COUNT_LOW`,
`HEIGHT_OUT_OF_RANGE`, `DIMENSION_OUT_OF_RANGE`.

## Aggregation
- Any FAIL → **verdict FAIL**, coverage `INCOMPLETE`, recommendation `RECAPTURE`.
- Else any WARN → **verdict WARN**, coverage `PARTIAL`, recommendation `REVIEW`.
- Else → **verdict PASS**, coverage `COMPLETE`, recommendation `ACCEPT_CANDIDATE`.
- Score = 100 − (WARN×8 + FAIL×25), clamped 0–100.

## API + persistence
`POST /api/reality/v1/scan-sessions/{id}/guardian/evaluate` runs `evaluate(report)`,
stores `guardian_result`, `quality_summary`, `coverage_state`, `missing_areas` on
the scan session, and emits audit `REALITY_SCAN_GUARDIAN_EVALUATED` (sanitized).
It does **not** transition the session.

## Determinism proof
- Backend: `tests/test_h014b_capture.py::TestGuardianDeterminism` (PASS=100,
  FAIL→RECAPTURE with expected finding codes, WARN band, identical outputs).
- iOS: `ScanQualityGuardianTests` asserts the same verdicts/codes (lock-step).
