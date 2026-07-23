# StratexRealityCapture (iOS/iPadOS native LiDAR capture client)

Thin native capture module for **STRATEX Habitat** — H-014B "Real iPhone/iPad
LiDAR Capture Proof". It captures ONE real room with Apple **RoomPlan + ARKit
(LiDAR)**, runs a deterministic **Scan Quality Guardian** pre-flight, and safely
delivers the governed scan data into the accepted H-014A backend foundation via
a **resumable, checksum-verified chunked upload**.

> ⚠️ **Build/Run status in this repository's dev/CI container: BLOCKED.**
> The Emergent development/CI container is **Linux (aarch64)** with **no macOS,
> Xcode, Swift toolchain, or iOS Simulator**. This module therefore ships as
> **reviewable source only**; it can be compiled, run and used for a real device
> capture **only on macOS + Xcode against a LiDAR device**. Physical capture is
> classified BLOCKED (not faked). See
> `docs/h014b/H014B_ENVIRONMENT_AND_REPOSITORY_RECON.md`.

## Device requirements
- iOS/iPadOS **16.0+** (RoomPlan).
- **LiDAR** sensor: iPhone 12 Pro / 13 Pro / 14 Pro / 15 Pro (and Pro Max), or
  iPad Pro (2020+) LiDAR models.
- Camera permission (`NSCameraUsageDescription`).

## Modules (`Sources/StratexRealityCapture/`)
| File | Responsibility |
|---|---|
| `CaptureModels.swift` | Codable contracts matching `backend/reality/schemas.py`; native capture state machine (`CaptureState`) + `backendScanState` mapping. |
| `CaptureStateMachine.swift` | (see `CaptureModels.swift`) legal client-side transitions. |
| `ScanQualityGuardian.swift` | **Deterministic** on-device mirror of `backend/reality/scan_guardian.py` (identical thresholds & verdicts). |
| `RoomCaptureCoordinator.swift` | RoomPlan `RoomCaptureSession` + ARKit LiDAR; builds `QualityReport` + `DerivedStructure`. |
| `HabitatAPIClient.swift` | Async client for `/api/reality/v1` (auth, scan sessions, upload, guardian, candidate). |
| `ResumableUploader.swift` | Chunked, retryable, resume-from-missing uploader with per-chunk + whole-file SHA-256. |
| `SecureLocalStore.swift` | `.completeFileProtection` staging, backup-excluded, purge-after-upload. |
| `CaptureFlowController.swift` | End-to-end governed orchestration (never promotes truth beyond DRAFT_CANDIDATE). |

## Truth boundary (non-negotiable)
A completed capture yields a **`DRAFT_CANDIDATE`** existing-model with
`MEASURED_EXISTING` geometry. The client **never** claims `VERIFIED_EXISTING`;
promotion requires a separate authorized Core/Passport/professional review.

## Info.plist keys required (host app)
```xml
<key>NSCameraUsageDescription</key>
<string>STRATEX Habitat uses the camera and LiDAR sensor to capture your room.</string>
```

## Build & test (on macOS)
```bash
cd ios/StratexRealityCapture
swift build            # library only (RoomPlan symbols resolve on the iOS SDK)
swift test             # runs ScanQualityGuardianTests (Guardian determinism)
```
On the Linux dev/CI container these commands are unavailable by design; the
GitHub Actions `ios-capture` job runs them on a `macos-latest` runner.
