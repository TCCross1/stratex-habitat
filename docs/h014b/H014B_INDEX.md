# H-014B — Real iPhone/iPad LiDAR Capture Proof & AI Scan Quality Guardian

**Mission:** Prove a supported LiDAR-equipped iPhone/iPad can capture ONE real
room and safely deliver governed scan data into the accepted H-014A foundation —
with a deterministic Scan Quality Guardian and strict truth boundaries.

**Branch:** `emergent/h014b-lidar-capture-proof` (local; see recon doc for the
remote/baseline note). **Baseline foundation:** accepted H-014A + H-014A.1.

## Document index (Phases 1–15)
| # | Document | Phase |
|---|---|---|
| 1 | [H014B_ENVIRONMENT_AND_REPOSITORY_RECON.md](./H014B_ENVIRONMENT_AND_REPOSITORY_RECON.md) | 1 |
| 2 | [H014B_NATIVE_CAPTURE_MODULE.md](./H014B_NATIVE_CAPTURE_MODULE.md) | 2–3 |
| 3 | [H014B_SCAN_QUALITY_GUARDIAN.md](./H014B_SCAN_QUALITY_GUARDIAN.md) | 4 |
| 4 | [H014B_CAPTURE_STATE_MAPPING.md](./H014B_CAPTURE_STATE_MAPPING.md) | 5 |
| 5 | [H014B_RESUMABLE_UPLOAD_PROTOCOL.md](./H014B_RESUMABLE_UPLOAD_PROTOCOL.md) | 6 |
| 6 | [H014B_BACKEND_CAPTURE_API.md](./H014B_BACKEND_CAPTURE_API.md) | 7 |
| 7 | [H014B_CANDIDATE_MODEL_GENERATION.md](./H014B_CANDIDATE_MODEL_GENERATION.md) | 8 |
| 8 | [H014B_REVIEW_EXPERIENCE.md](./H014B_REVIEW_EXPERIENCE.md) | 9 |
| 9 | [H014B_SECURITY_AND_LOCAL_DATA.md](./H014B_SECURITY_AND_LOCAL_DATA.md) | 10–11 |
| 10 | [H014B_CI_AND_TESTING.md](./H014B_CI_AND_TESTING.md) | 12–13 |
| 11 | [H014B_EXECUTION_REPORT.md](./H014B_EXECUTION_REPORT.md) | 14–15 |

## Truth boundary (applies everywhere)
A completed capture yields ONLY a **`DRAFT_CANDIDATE`** existing-model with
`MEASURED_EXISTING` geometry. It is **never** auto-promoted to `VERIFIED_EXISTING`
(that requires a separate authorized Core/Passport/professional review). The
Habitat review experience is **read-only** — no unrestricted design editing.

## Honest status headline
- Backend capture APIs, deterministic Guardian, resumable governed upload,
  candidate generation, and the read-only review UI are **implemented and tested**
  (Linux dev container + real Emergent object storage).
- The native Swift capture module is **authored as reviewable source**; its
  **build/run and real physical room capture are BLOCKED** in this environment
  (no macOS/Xcode/Swift). Not production-ready; not merged to `main`.
