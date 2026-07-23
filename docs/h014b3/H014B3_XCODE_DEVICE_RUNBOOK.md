# H-014B.3 Xcode Device Runbook

Physical installation is performed by the operator on a Mac with Xcode.
Cursor/Linux CI cannot install to a personal device — report that status as
**UNEXECUTED** unless the operator completes these steps.

## 1. Open the project

```bash
cd ios/StratexRealityCaptureApp
open StratexRealityCaptureApp.xcodeproj
```

The project references the local package `../StratexRealityCapture` — do **not**
copy package sources into the app target.

## 2. Xcode / signing

1. Install a supported Xcode (16+ recommended; RoomPlan requires iOS 16 SDK).
2. Select the **StratexRealityCaptureApp** target.
3. Signing & Capabilities → choose **your** Apple Development Team.
4. Set a **unique** development bundle identifier (default template:
   `com.stratex.habitat.capture.pilot` — change the suffix for your team).
5. Do **not** commit team IDs, profiles, or certificates.

## 3. Device

1. Connect a LiDAR-equipped iPhone or iPad (12 Pro / 13 Pro / 14 Pro / 15 Pro /
   16 Pro class, or iPad Pro with LiDAR).
2. Trust the computer; enable **Developer Mode** if prompted (iOS 16+).
3. Select the **physical device** as the run destination (not a simulator for the pilot).

## 4. Configure non-production Habitat

1. Launch the app.
2. Enter the non-production API base URL (HTTPS).
3. Sign in with an approved development account.
4. Enter **pseudonymous** property and room IDs.
5. Paste the git commit SHA under test into the Commit SHA field.

Passwords remain in memory only and are cleared from the UI field after login.
Tokens are never written into evidence exports.

## 5. Build / install / permission

1. Product → Run (⌘R).
2. Grant **camera** permission when prompted.
3. Confirm readiness: LiDAR available, RoomPlan available, camera authorized.

## 6. Execute the pilot

Follow `H014B3_PHYSICAL_DEVICE_TEST_PROTOCOL.md` (three scans + interruption drills).

## 7. Export evidence

1. Tap **Export redacted evidence**.
2. On the Mac, use Xcode Devices window / Finder sharing / `idevicefs` to copy
   Documents/`h014b3-evidence/` JSON+Markdown into local
   `test_reports/h014b3-device/` (gitignored).
3. Preserve screenshots/screen recordings as basename-only references.

## 8. Cleanup

1. Sign out / delete the app if required by your security policy.
2. Remove any local development tokens from Keychain/files.
3. Do not commit signing material or real room media.

## Simulator note

CI compiles the package and host app for **iOS Simulator SDK** to prove the
RoomPlan source path type-checks. Simulator compile is **not** physical LiDAR
validation.
