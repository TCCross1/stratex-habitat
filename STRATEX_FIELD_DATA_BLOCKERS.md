# STRATEX FIELD DATA BLOCKERS

What in this repository genuinely requires real DJI/LiDAR property-scan data
to complete or validate, versus what is conventional software work that does
not depend on field data. Evidence is cited to specific files.

## 1. What requires real property scans (cannot be responsibly completed with synthetic data alone)

| Item | Current state | Why it needs real capture data | Evidence |
|---|---|---|---|
| **M4E/M4T drone imagery ingestion** | Not present in this repository at all. | No ingestion, parsing, or validation code for DJI M4E/M4T imagery exists here; this repo only consumes a hypothetical downstream "Passport" projection. | Absence confirmed by full-repo search; no `dji`, `m4e`, `m4t` references found anywhere in `backend/` or `frontend/`. |
| **RTK metadata** | Not present. | Same as above — no RTK/GPS-metadata parsing exists in this codebase. | Absence confirmed. |
| **Reconstruction outputs (point clouds, meshes, orthomosaics)** | Only a deterministic **synthetic** placeholder point cloud exists: `_POINTCLOUD = b"STRATEX-H014B-PROOF-POINTCLOUD;x,y,z,r,g,b\n" * 900` (`backend/reality/capture_proof.py:35-36`). No mesh or orthomosaic generation/consumption code exists. | The upload/storage/checksum "machinery" around point clouds is real, but it has never ingested a real point cloud. Only real capture will prove the artifact/checksum/upload pipeline against real payload sizes, formats, and error modes. | `backend/reality/capture_proof.py`, `backend/reality/capture_upload_service.py` |
| **Radiometric R-JPEG thermal data** | Not present. No thermal-specific parsing, calibration, or radiometric conversion code exists anywhere in the repo. | Cannot be validated without real thermal captures; there is currently nothing to validate. | Absence confirmed by search. |
| **Semantic geometry (rooms/openings/surfaces classification)** | Backend has a `spatial_service.py` and `SHARED_SPATIAL_DOMAIN_MODEL.md` spec, but the only populated instance data is the fixed **12-entity, 2-frame deterministic fixture** described in `docs/h014a/H014A_REFERENCE_ROOM_CONTRACT.md` and reproduced verbatim in `test_result.md:463-465` (width 4.88 m, length 6.10 m, floor area 29.768 m², entity_count 12). | The data model/contract exists, but semantic accuracy, edge cases (irregular rooms, occlusion, multi-story), and classification reliability are entirely unproven against real scan variability. | `backend/reality/spatial_service.py`, `backend/reality/fixtures.py` |
| **Property Object Graph / object extraction** | `docs/h014/PRODUCT_GRAPH_AND_MATERIAL_SELECTION.md` is a specification. `design.py`'s "Product Graph" concepts operate on a hand-authored product library, not extracted objects from any scan. | No object-detection/extraction pipeline exists in this repo to extract real objects from any capture. | `docs/h014/PRODUCT_GRAPH_AND_MATERIAL_SELECTION.md` (spec only, per `docs/h014/README.md:1`: *"Specification only. Not implemented."*) |
| **Real-world measurement tolerances** | `docs/h014/PROPERTY_COORDINATE_AND_ALIGNMENT_STANDARD.md` defines tolerance *classes* (spec), but H-014's own architecture record lists as an open "known unknown": *"LiDAR device/SDK capability envelope and achievable PLANNING-tolerance residuals on real homes"* (`docs/h014/H014_MASTER_ARCHITECTURE_DECISION_RECORD.md:69`). | Tolerance claims are policy/labels today, not measured accuracy. Only real scans compared against ground truth (tape measure, per `docs/h014b3/H014B3_MANUAL_MEASUREMENT_SHEET.md`) can validate them. | `docs/h014/H014_MASTER_ARCHITECTURE_DECISION_RECORD.md`, `docs/h014b3/H014B3_MANUAL_MEASUREMENT_SHEET.md` |
| **Cortex findings/confidence** | Not present in this repo; Cortex is an external system referenced only conceptually. | Cannot validate a system whose code is not in this repository at all. | N/A — out of repo scope |
| **Core quantity/estimate validation** | `backend/pricebook.py` is a governed **price book** with explicit `authoritative:false` provenance (per `docs/h014/H014_REPOSITORY_AND_ARCHITECTURE_AUDIT.md:19`); quantities come from user/homeowner inputs and design selections, not from measured/extracted geometry. | Estimate accuracy against real quantities/measurements from a real scan has never been tested. | `backend/pricebook.py` |
| **Passport truth promotion** | Explicitly and deliberately blocked in code: a completed capture yields only `DRAFT_CANDIDATE` + `MEASURED_EXISTING`; promotion to `VERIFIED_EXISTING` requires "a separate authorized Core/Passport/professional review" not implemented here (`docs/h014b/H014B_INDEX.md`, "Truth boundary" section). `backend/reality/audit_service.py` emits `REALITY_TRUTH_PROMOTION_REJECTED` audit events specifically to prevent silent promotion. | By design, promotion is deferred to a real, externally-authorized review step that doesn't exist in this repo — inherently requires real captures and an external authority to exercise. | `backend/reality/audit_service.py`, `docs/h014b/H014B_INDEX.md` |
| **Report accuracy (Comprehensive Property Intelligence Report)** | `backend/redaction.py` and `projects.py` produce a "PIP" (Project Intent Package)/contractor package from homeowner-entered and demo/fixture data; no report in this repo has ever been generated from a real scan. | Report correctness against ground truth is unproven. | `backend/projects.py`, `backend/redaction.py` |
| **Pro/Habitat real property synchronization** | No "Stratex Pro" application exists in this environment/repo to synchronize with; Habitat's only sync-adjacent code is the demo `sync_log` collection (`docs/h014/H014_REPOSITORY_AND_ARCHITECTURE_AUDIT.md:33-36`) and the mocked "Core handshake" in `backend/server.py:460-476`. | Cannot validate a cross-app sync that has no real counterpart app and only a mock handshake function in code. | `backend/server.py:460-476` |
| **Before/after verification workflows** | `docs/habitat/H014C_ACCEPTANCE.md` explicitly states Habitat prefers an "empty verified-finding state" for the demo and asserts "No fake meshes, rooms, dimensions, or LiDAR results." No before/after comparison against a real completed job has been run. | Requires two real captures of the same property (before/after a completed project) — cannot exist without field data by definition. | `docs/habitat/H014C_ACCEPTANCE.md` |

## 2. What does NOT depend on field data and should still be finished

These items are ordinary software-engineering work, independent of drone/LiDAR
capture, that this audit found incomplete or unverified:

1. **Frontend build/dependency pipeline is not verifiable at all in this audit** (network-blocked `yarn install`) — this needs to be fixed/verified in a network-enabled environment regardless of any field data. See `STRATEX_TEST_AND_BUILD_EVIDENCE.md` §4.
2. **No lint/type-check enforcement**, despite `black`/`isort`/`flake8`/`mypy` being pinned dependencies (`backend/requirements.txt:22-25`) — wiring these into CI is pure engineering hygiene work.
3. **No security/SAST scanning workflow** exists (`.github/workflows/` has only functional test workflows) — independent of field data.
4. **Backend `reality` package coverage gaps** unrelated to hardware: `router.py`, `schemas.py`, `indexes.py`, `capture_proof.py` show 0% in isolated process-local coverage (`STRATEX_TEST_AND_BUILD_EVIDENCE.md` §3) — closing this requires better test harnessing, not real scans.
5. **The two duplicate/unreconciled state machines** (`workflow.py`'s Steward workflow vs. `projects.py`'s `IDEA→…→SAVED_TO_PASSPORT`) are explicitly flagged as unreconciled in `docs/h014/H014_REPOSITORY_AND_ARCHITECTURE_AUDIT.md:67-70` ("Phase 16 defines ONE canonical... state machine... without rewriting either in this mission") — this is deferred design/refactoring work, not a field-data blocker.
6. **The entire H-014 Reality Studio architecture beyond H-014A/B is "specification only"** (`docs/h014/README.md:1`) — Interior/Exterior/Systems studio UIs, Room DNA/Property DNA projections, Living Digital Home layering, and the Product Graph are undesigned-in-code; these can and should be implemented against the existing fixture/demo data model before any real scan is required, so that the moment real captures arrive there is a working UI/data path to receive them.
7. **`backend/server.py`'s unconditional external storage-init call** at startup (network call to `integrations.emergentagent.com` even when `HABITAT_OBJECT_STORE_PROVIDER=fake`) is a configuration/robustness bug independent of field data — see `STRATEX_TEST_AND_BUILD_EVIDENCE.md` §2.
8. **Hardcoded demo credentials in `backend/seed.py`** should be parameterized/rotated as a config-hygiene practice before any real-property pilot, regardless of scan data.
9. **The native Swift capture module and host app are authored but never compiled/run in any CI observed by this audit** in a real macOS/Xcode environment from this session (workflow exists but requires a macOS runner not available here) — verifying that workflow actually runs green is engineering validation independent of having a physical LiDAR device in hand.

## 3. Bottom line

Everything that touches **real optical/RTK/thermal capture data, semantic
object extraction from that data, measurement-tolerance validation, or
Passport truth-promotion** is either unimplemented, spec-only, or backed
exclusively by a small, fixed, deterministic synthetic fixture
(12 entities / 2 frames / one demo room). Everything else — build pipeline
health, lint/security gates, state-machine reconciliation, UI completion for
already-modeled data, and fixing the mock external Core handshake — is
ordinary software work that can and should proceed without waiting for field
data.
