# H-014B.3 Physical Device Test Protocol

**Scope:** One ordinary living room. Three independent scans. Non-production Habitat only.
**Not in scope:** H-014C, design editor, Passport publication, production authorization.

## Preconditions

1. Accepted main baseline includes H-014B capture architecture.
2. Host app `StratexRealityCaptureApp` installed on a LiDAR-equipped iPhone/iPad.
3. Non-production API endpoint configured; operator authenticated.
4. Pseudonymous property ID and room ID assigned (never real street addresses).
5. Manual measurement sheet completed **before** scanning (see `H014B3_MANUAL_MEASUREMENT_SHEET.md`).
6. Camera permission granted; LiDAR + RoomPlan reported available on the readiness screen.

## Chain under test

LiDAR device → RoomPlan capture → live Guardian coaching → interruption/recovery →
resumable upload → checksum verification → DRAFT_CANDIDATE → read-only Habitat review →
comparison to manual measurements.

## Three-scan procedure

For **scan index 1, 2, and 3** of the **same** room:

1. Confirm readiness card: LiDAR available, RoomPlan available, camera authorized.
2. Start a new validation evidence run (or increment `scanIndex`).
3. Start capture. Follow live coaching. Do **not** finish until the operator judges coverage adequate.
4. Explicitly tap **Finish** (coaching must never auto-complete).
5. Upload → confirm checksum declared/verified match.
6. Confirm candidate state is **DRAFT_CANDIDATE** only (never VERIFIED_EXISTING).
7. Open Habitat Capture Review (read-only) and verify Guardian verdict / unknowns remain visible.
8. Export redacted evidence JSON + Markdown to the device Documents folder, then copy to the local
   `test_reports/h014b3-device/` workspace path on the Mac (gitignored).
9. Record absolute and percentage errors vs the manual sheet.

Between scans: leave the room undisturbed; do not rearrange large furniture if avoidable.

## Required interruption drills (at least once across the three scans)

See runbook § interruption matrix. Minimum coverage:

- Background the app mid-capture (incoming call simulation / Home gesture)
- Kill app after capture, before upload; relaunch and recover pending upload if staged
- Kill app during chunk upload; relaunch and resume missing chunks
- Toggle Wi-Fi off during upload; restore and resume
- Replay completion; confirm idempotent
- Replay abort on a disposable session; confirm idempotent

## Pass recording

Preserve **actual** results even when gates fail. Use `H014B3_ACCEPTANCE_GATES.md`.
Do not alter thresholds post-hoc to force a pass.
