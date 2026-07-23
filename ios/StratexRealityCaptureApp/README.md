# StratexRealityCaptureApp (H-014B.3)

Thin SwiftUI **host application** for physical LiDAR device validation.

It **references** the local Swift package `../StratexRealityCapture` and does not
copy package sources. Reused types:

- `RoomCaptureCoordinator`
- `CaptureFlowController`
- `HabitatAPIClient`
- `ResumableUploader`
- `SecureLocalStore`
- `ScanQualityGuardian` + `GuardianCoaching`
- `ValidationEvidence` / `ValidationEvidenceRedactor`
- `DeviceCapability`

## Open in Xcode

```bash
open StratexRealityCaptureApp.xcodeproj
```

See `docs/h014b3/H014B3_XCODE_DEVICE_RUNBOOK.md` for signing, device install,
and pilot execution.

## Truth boundary

The app may display **DRAFT_CANDIDATE** status after governed upload. It must not
approve VERIFIED_EXISTING, write Passport/Core property truth, or expose Build Ready /
Publish actions.

## Simulator vs device

- **iOS Simulator SDK compile** (CI): proves RoomPlan/ARKit source paths build.
- **Physical LiDAR capture**: UNEXECUTED until an operator follows the runbook.
