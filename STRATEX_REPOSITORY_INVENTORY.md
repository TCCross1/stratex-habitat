# STRATEX REPOSITORY INVENTORY

Prepared as part of the STRATEX KEYHORSE Technical Validation Directive.
Evidence-based. No prior status report was assumed correct; every claim below
was checked directly against this repository's working tree, git history,
CI configuration, and a live local test execution.

## 1. Scope limitation (read first)

This sandboxed audit environment provides **exactly one** git repository:

| Field | Value |
|---|---|
| Local path | `/home/runner/work/stratex-habitat/stratex-habitat` |
| Remote (origin) | `TCCross1/stratex-habitat` (formerly `TCCross1/Habitat` — see `docs/h013/H013_REPOSITORY_VERIFICATION.md:14`, confirming a prior rename) |
| Active branch | `copilot/stratex-tech-validation` |
| HEAD commit | `6eeb7605a379f5954c7343909eaede57cfc0ea8b` |
| HEAD subject | `H-014C.0 reconcile Central Kentucky demo truth and visualization` |
| HEAD author date | 2026-07-23 |
| Parent commit | `28e2119` — `H-014B.3 prepare physical LiDAR device validation harness` |

**No other Stratex repository (ATC, Reality Foundry, Cortex, Core, Passport,
CENTCOM, Stratex Pro) is present, cloned, or reachable from this environment.**
This inventory therefore cannot independently validate those systems' code,
tests, or build health — only what this repository claims/implements about
them. Any statement about ATC/Cortex/Core/Passport/Pro below is an inference
from this repo's documentation and integration boundary code
(`backend/passport_projection.py`), not a first-hand audit of those systems.
This is itself a diligence finding: **the "platform" as described in the
directive is not fully co-located in one auditable codebase from this vantage
point.**

## 2. Repository identity and purpose

- **Name:** `stratex-habitat` (application title inside the code: `STRATEX HABITAT API`, `backend/server.py:182`).
- **Purpose:** A homeowner-facing web application ("Habitat") for property stewardship — home system tracking, project/estimate planning ("Home Steward", "Design Studio", "Homeowner Architect"), contractor matching/quoting, and (in progress) a scan-based "Reality Studio" for interior/exterior digital-twin capture. It positions itself as consuming — never owning — canonical property truth from an external "Passport"/"Core" system via a read-only projection boundary (`backend/passport_projection.py`).
- **Stack:** FastAPI + MongoDB (Motor/PyMongo) backend (`backend/`), Create-React-App/CRACO + Radix UI frontend (`frontend/`), a Swift Package + thin SwiftUI host app for iPhone/iPad LiDAR capture (`ios/`), and two GitHub Actions workflows (`.github/workflows/backend-reality.yml`, `.github/workflows/ios-capture.yml`).
- **Not present in this repo:** any ATC ingestion service, DJI/M4E/M4T ingestion pipeline, Reality Foundry reconstruction engine, Cortex analysis engine, Core, Passport, CENTCOM orchestration service, or a standalone "Stratex Pro" application. The repo only contains a **client-side integration boundary** (`passport_projection.py`) that expects such systems to exist elsewhere and fails closed if they don't.

## 3. Last meaningful development status (self-reported, verified against code)

The repository carries an internal "mission" log naming convention (`H-013`, `H-014`, `H-014A/B/B.3/C`). The most recent completed mission, per the HEAD commit message and `docs/habitat/H014C_ACCEPTANCE.md`, is:

> **H-014C.0** — reconciliation of a single fixture-marked "Central Kentucky Demonstration Home" so its visualization and finding copy are clearly labeled `demo` / `sample_only`, plus a guarded dry-run reconciliation CLI (`backend/scripts/reconcile_ky_demo.py`). The commit message itself states: *"Does not complete H-014C real existing-room twin. Physical LiDAR, RoomPlan, real-device upload, and approved Passport geometry projection remain unexecuted. Production readiness: NOT READY."*

This is a **first-party admission that the platform is pre-field-validation**, consistent with the rest of this audit's findings (Section 6 of the technical report).

## 4. Directory map (what actually exists)

| Path | Contents |
|---|---|
| `backend/` | FastAPI app (`server.py`), Home Steward (`steward.py`), Design Studio (`design.py`), Homeowner Architect projects/PIP (`projects.py`), governed price book (`pricebook.py`), redaction (`redaction.py`), readiness/Build-Ready policy (`readiness_policy.py`), Passport projection adapter (`passport_projection.py`), demo/fixture governance (`fixture_provider.py`, `demo_property.py`, `seed.py`), governed workflow/publication (`workflow.py`), and the `reality/` package (19 modules: capture, scan sessions, artifacts, object storage, coordinate frames, scan guardian, authz, audit). 16 pytest files under `backend/tests/`. |
| `frontend/` | React 19 SPA; routes for `/twin`, `/steward`, `/design-studio`, `/quotes`, `/marketplace`, `/contractors`, `/reviews`, `/documents`, `/reports`, plus a dev-only `/reality-foundation` screen. 2 Jest test files. |
| `ios/` | `StratexRealityCapture` (Swift Package: LiDAR/RoomPlan capture module, reviewable source, **not built/run in this environment** — no macOS/Xcode) and `StratexRealityCaptureApp` (thin SwiftUI host app for the H-014B.3 physical device pilot). |
| `docs/h013/` … `docs/habitat/` | ~70 markdown specification/implementation/evidence documents describing each mission (H-013 hardening, H-014 Reality Studio architecture spec, H-014A backend foundation, H-014B LiDAR capture proof, H-014B.3 physical device protocol, H-014C Kentucky demo reconciliation). |
| Repository root | ~90 additional product/design specification markdown files (`HOME_STEWARD_*`, `PROJECT_*`, `DESIGN_STUDIO_*`, `ESTIMATE_*`, etc.) — these are product/spec documents, not verified implementation status. |
| `test_result.md` | A 559-line running YAML-in-markdown test/status ledger maintained by prior agent sessions (self-reported; partially reproduced independently — see `STRATEX_TEST_AND_BUILD_EVIDENCE.md`). |
| `test_reports/` | JSON/screenshot artifacts from prior frontend UI test iterations; a `.gitkeep`'d directory for future device-pilot evidence. |

## 5. CENTCOM / Cortex / ATC / Reality Foundry / Core / Passport / Pro — what is and isn't evidenced here

- The string `CENTCOM` appears **only** as a document-header prefix ("CENTCOM DIRECTIVE H-00N: …") on dozens of root-level spec markdown files (e.g. `PROJECT_OPPORTUNITY_SPEC.md:1`). It is a mission-issuing label in documentation, not a subsystem with code in this repository.
- `Cortex`, `Core`, and `Passport` appear as **named upstream systems this app talks about or defers to** — never as code owned by this repo:
  - `backend/passport_projection.py` implements a **client-side adapter** with four provider modes (`development`, `demo`, `test`, `production`). The `production` provider (`HttpProjectionProvider`, line 287) calls an external URL from `HABITAT_PROJECTION_BASE_URL`; if that env var is unset — which it is, everywhere in this repo, including CI — it **fails closed** with `ProjectionUnavailable` (`passport_projection.py:291-297`). No real Passport/Core/Cortex endpoint is configured, called successfully, or verified reachable anywhere in this codebase.
  - `backend/server.py:475` contains a function literally named/commented `Mock STRATEX Core publishing approved scans/reports into the shared property record` (`server.py:460-476`) — i.e. the "Core" integration in the running app is explicitly a mock.
- **Conclusion on the directive's architecture claim** ("Core is embedded inside CENTCOM between Cortex and Passport; Pro and Habitat are standalone"): this repository provides **no evidence to confirm or deny** the internal CENTCOM/Cortex/Core/Passport topology, because none of those systems' code is present here. What this repo **does** confirm is that Habitat is architected as a standalone consumer of a Passport-shaped projection API and does not itself implement Cortex/Core/Passport. Whether "Stratex Pro" is genuinely a separate standalone codebase cannot be assessed — it is not present in this environment and is only mentioned in passing in product-spec markdown, never as a build target or integration in code.

## 6. Test credentials note

`backend/seed.py` seeds fixed demo accounts (`alex@stratexhabitat.com`, `admin@stratexhabitat.com`, `horizon@stratexhabitat.com`, `peakbuild@stratexhabitat.com`, `lonestar@stratexhabitat.com`) with the password `Demo123!`/`Admin123!` hardcoded in source and reused by the pytest integration suite (`backend/tests/conftest.py:31-33`). These are non-production, seed-only, low-entropy demo credentials — acceptable for a dev/demo seed, but they must never be reused for any real deployment, and their presence in source is a configuration-hygiene item (see `STRATEX_TECHNICAL_VALIDATION_REPORT.md` §9).
