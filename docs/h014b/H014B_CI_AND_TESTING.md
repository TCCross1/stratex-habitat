# H014B Phases 12–13 — CI & Testing

## Backend tests (`backend/tests/test_h014b_capture.py`, 22 tests)
Run against the live backend + MongoDB + real Emergent object storage via the
shared `conftest.py` fixtures.

**Pure unit (no infra):**
- `TestGuardianDeterminism` — PASS=100 & identical outputs; FAIL→RECAPTURE with
  expected finding codes; WARN band; missing areas surfaced.
- `TestNativeStateMapping` — full/spot mappings; unknown state → 422.

**HTTP integration:**
- `TestCaptureProofHTTP` — full pipeline (Guardian PASS, checksum-verified upload,
  `DRAFT_CANDIDATE` with 12 `MEASURED_EXISTING` entities), idempotency, storage-ref
  masked, authorized content round-trip (downloaded sha256 == declared).
- `TestResumableUploadHTTP` — happy path, **resume-missing-chunk**, checksum
  mismatch (422), chunk-size mismatch (422), invalid chunk-size at init (422).
- `TestGuardianAndCandidateHTTP` — guardian evaluate persists; candidate requires
  QUALITY_REVIEW (409); capture-progress records mapped state.
- `TestCaptureAuthorizationHTTP` — 401 unauthenticated; 403 contractor;
  404 non-disclosure on a missing scan.

**Results:** `pytest tests/test_h014b_capture.py` → **22 passed**.
Full backend suite (`pytest tests/`) → **243 passed, 1 skipped** (pre-existing
unrelated live-Gemini render skip). H-014A remains green (no regression).

## Native tests (`ios/.../ScanQualityGuardianTests.swift`)
Mirror the backend Guardian determinism + native→backend mapping. Run on macOS:
`cd ios/StratexRealityCapture && swift test`.

## GitHub Actions
- **`.github/workflows/backend-reality.yml`** (`ubuntu-latest`): byte-compiles the
  `reality` package and runs the **deterministic unit subset** (Guardian, native
  mapping, coordinate/spatial validators, storage-ref, reference-room determinism)
  with placeholder config — **44 tests, no external infra** → reliably green.
- **`.github/workflows/ios-capture.yml`** (`macos-latest`): `swift build` +
  `swift test` — the designated place a real Apple toolchain compiles the native
  module (RoomPlan/ARKit excluded via `#if canImport`) and runs the Guardian tests.

## Not covered by basic CI (by design)
The full governed HTTP integration suite needs a running backend + MongoDB +
object storage (`EMERGENT_LLM_KEY`); it runs in the deployment/preview environment
rather than the basic CI runner. Real physical iOS LiDAR capture is **BLOCKED** in
this environment (no macOS/Xcode/device).
