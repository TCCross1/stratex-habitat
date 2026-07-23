# H014B Phases 2–3 — Native iOS/iPadOS Capture Module

Source: `ios/StratexRealityCapture/` (Swift Package). **Build/run BLOCKED** in the
Linux dev container; compiles on macOS/Xcode and runs on a LiDAR device.

## Device & framework requirements
- iOS/iPadOS **16.0+** (RoomPlan).
- **LiDAR** sensor (iPhone 12 Pro → 15 Pro / Pro Max; iPad Pro LiDAR models).
- `NSCameraUsageDescription` in the host app Info.plist.

## Module layout
| File | Responsibility |
|---|---|
| `CaptureModels.swift` | Codable contracts matching `backend/reality/schemas.py`; `CaptureState` native state machine + `backendScanState` mapping; `QualityReport`, `DerivedStructure`. |
| `ScanQualityGuardian.swift` | Deterministic on-device mirror of the backend Guardian (identical thresholds/verdicts). |
| `RoomCaptureCoordinator.swift` | `RoomCaptureSession` (RoomPlan) + ARKit LiDAR; emits `QualityReport` + `DerivedStructure`; guarded by `#if canImport(RoomPlan)`. |
| `HabitatAPIClient.swift` | Async client for `/api/reality/v1` (auth, scan session, capture-progress, guardian, resumable upload, candidate). |
| `ResumableUploader.swift` | Chunked, retryable, **resume-from-missing** uploader; per-chunk + whole-file SHA-256. |
| `SecureLocalStore.swift` | `.completeFileProtection` staging, backup-excluded, purge-after-upload. |
| `CaptureFlowController.swift` | End-to-end governed orchestration. |
| `Tests/…/ScanQualityGuardianTests.swift` | Guardian determinism + state-map tests (mirror backend). |

## Capture flow (on device)
1. **Auth** to Habitat (`HabitatAPIClient.login`).
2. **Property selection** (homeowner's authorized property id).
3. **Capture** with `RoomCaptureCoordinator` (RoomPlan coaching + ARKit LiDAR mesh).
   State machine: `idle → authorized → ready → capturing (↔ paused) → finalizing`.
4. **On-device Guardian pre-flight** — instant PASS/WARN/FAIL feedback before upload.
5. **Secure-stage** the exported artifact; **resumable upload** into governed
   object storage; **backend Guardian** re-evaluates authoritatively.
6. **DRAFT_CANDIDATE** generation (never VERIFIED_EXISTING).

## Portability guards
RoomPlan/ARKit/UIKit/CryptoKit are wrapped in `#if canImport(...)`. On non-iOS
compilers (e.g. the macOS CI runner) the RoomPlan branch is replaced by an
explicit stub so the portable code (models, Guardian, uploader, API client) still
compiles and its tests run. This is what the `ios-capture` GitHub Actions job
exercises.
