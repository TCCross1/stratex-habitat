# STRATEX TECHNICAL VALIDATION REPORT

**Directive:** STRATEX KEYHORSE Technical Validation Directive — investor
diligence audit.
**Audited artifact:** git repository `TCCross1/stratex-habitat`, branch
`copilot/stratex-tech-validation`, commit `6eeb7605a379f5954c7343909eaede57cfc0ea8b`.
**Method:** Direct inspection of source code, direct execution of the
project's own CI-equivalent test suite against a live local MongoDB, and
line-cited reading of the repository's own architecture/status documentation.
No prior status report (including this repo's own `test_result.md`) was
assumed correct; where this audit could independently re-verify a claim, it
did so and reports the reproduced number. Where it could not, that is stated
explicitly. See companion documents for underlying detail:
`STRATEX_REPOSITORY_INVENTORY.md`, `STRATEX_TEST_AND_BUILD_EVIDENCE.md`,
`STRATEX_FIELD_DATA_BLOCKERS.md`.

---

## 1. Scope caveat (critical)

This audit had access to **one** repository — Habitat. ATC, Reality Foundry,
Cortex, Core, Passport, and any standalone "Stratex Pro" codebase were **not
present** in this environment and could not be independently built, tested,
or code-reviewed. All statements below about those systems are limited to
what Habitat's own integration boundary code and documentation claim about
them, clearly marked as such. This is itself a material diligence finding:
**a complete "Stratex platform" audit cannot be performed from this repo
alone.**

## 2. Architecture validation (item 4 of the directive)

Directive claim to validate: *Capture/DJI → ATC → Reality Foundry →
reconstruction interfaces → Cortex → Core → Passport → Comprehensive Property
Intelligence Report → 3D Digital Twin + Layers → standalone Stratex Pro and
Stratex Habitat, with Core embedded in CENTCOM between Cortex and Passport,
and Pro/Habitat standalone.*

**Findings:**
- Habitat is architected, in code, as a **standalone consumer application**
  that never writes canonical property truth and reads it only through one
  versioned adapter, `backend/passport_projection.py` (modes:
  `production|development|demo|test`; `MODE_PRODUCTION` uses
  `HttpProjectionProvider`, which calls `HABITAT_PROJECTION_BASE_URL` and
  **fails closed** with no fallback to seed/demo data if that URL is unset —
  `passport_projection.py:287-297`). This supports the directive's claim that
  Habitat is a standalone application relative to Passport/Core.
- **No configured, reachable Passport/Core/Cortex endpoint exists anywhere in
  this repository or its CI** — `HABITAT_PROJECTION_BASE_URL` is not set in
  `.github/workflows/backend-reality.yml`, not documented with a real value
  anywhere, and the production provider path was never exercised in this
  audit's test run. The claimed upstream chain (Capture/DJI → ATC → Reality
  Foundry → Cortex → Core → Passport) is **not evidenced by this repository**
  in any form beyond documentation prose (`docs/h014/H014_MASTER_ARCHITECTURE_DECISION_RECORD.md`,
  ownership matrix §5) and a function in `backend/server.py:460-476` that is
  explicitly commented **"Mock STRATEX Core publishing"**.
- "CENTCOM" appears in this repo exclusively as a document-header label
  (`# CENTCOM DIRECTIVE H-00N: ...`) prefixing dozens of specification
  markdown files at repo root — it names an authoring/mission-issuing
  convention, not a subsystem with implementation in this codebase. **This
  audit cannot confirm or deny the "Core embedded inside CENTCOM between
  Cortex and Passport" claim** — that architecture, if real, lives outside
  this repository.
- "Reality Foundry" and formal reconstruction-interface terminology do not
  appear in this codebase; the closest analog is Habitat's own `backend/reality/`
  package (scan sessions, artifacts, coordinate frames, scan guardian — 19
  modules), which is a **Habitat-owned capture/ingestion boundary**, not a
  reconstruction engine, and produces only fixed synthetic fixture geometry
  today (see §6, §7).
- **Conclusion:** The directive's high-level pipeline description may be
  accurate as an aspirational/enterprise architecture, but **this repository
  provides no first-hand evidence for the Capture→ATC→Reality
  Foundry→Cortex→Core→Passport chain or for CENTCOM's internal structure**.
  What is verified: Habitat is a standalone app; it treats Passport as an
  external read-only source of truth; and its own "Core" integration point is
  presently a mock function.

## 3. Subsystem classification (item 5 of the directive)

| Subsystem | Classification | Basis |
|---|---|---|
| Home Steward (guided planning journey) | **IMPLEMENTED** | `backend/steward.py`, `frontend/src/pages/HomeSteward.js`; exercised by passing integration tests (`test_h013_workflow.py`, `test_h013_publication.py`) reproduced live (§5). |
| Design Studio (exterior façade re-skin) | **IMPLEMENTED / MOCK DATA** for the AI-render path | Zones/products/recommendations are real, governed logic (`backend/design.py`); the Gemini "Nano Banana" re-skin render depends on the private `emergentintegrations` package and a live external LLM call, gated behind `RUN_RENDER_TEST=1` and skipped in every observed run (§5). |
| Homeowner Architect projects / PIP / contractor matching | **IMPLEMENTED** | `backend/projects.py`; full state machine (`IDEA→…→SAVED_TO_PASSPORT`) covered by `test_projects.py`, passing. |
| Governed price book / estimating | **IMPLEMENTED / MOCK DATA (non-authoritative by design)** | `backend/pricebook.py` is explicitly tagged `authoritative:false`; it is a real, versioned, governed module but its pricing data is a seed/reference data set, not live regional market data. |
| Passport projection boundary | **IMPLEMENTED (client adapter) / no real upstream** | `backend/passport_projection.py` is real, tested, fails-closed code; but its `production` mode has never been exercised against a real Passport endpoint in this repo — the endpoint doesn't exist here. |
| Readiness / Build-Ready policy | **IMPLEMENTED** | `backend/readiness_policy.py`; HARD/CONDITIONAL/WARNING/INFORMATIONAL classes with tests. |
| Redaction (contractor package) | **IMPLEMENTED** | `backend/redaction.py`, allow-list based, unit-tested. |
| Governed workflow + audit/passport events | **IMPLEMENTED** | `backend/workflow.py`; immutable `audit_events`/`passport_events` collections, tested. |
| Reality Studio — shared spatial domain model, coordinate standard, scan sessions, artifact/object storage, Scan Quality Guardian, authz/audit | **IMPLEMENTED / MOCK DATA** | Real service code (`backend/reality/*`, 19 modules) with real governed object storage, checksums, idempotent uploads, and non-disclosure authorization — but all currently exercised only against a fixed, deterministic 12-entity/2-frame **fixture** or a synthetic point-cloud constant (`capture_proof.py:36`); never a real scan. |
| Room DNA / Property DNA, Interior/Exterior/Systems Studio UIs, Living Digital Home layering, Product Graph | **DESIGNED / NOT IMPLEMENTED** | `docs/h014/README.md:1` states outright: *"Specification only. Not implemented."* |
| Native LiDAR capture module (Swift/RoomPlan) | **IMPLEMENTED (source) / BLOCKED BY REAL FIELD DATA (execution)** | `ios/StratexRealityCapture` compiles for the iOS Simulator SDK (per its own CI workflow's intent); its README states plainly: *"Build/Run status in this repository's dev/CI container: BLOCKED... can be compiled, run and used for a real device capture only on macOS + Xcode against a LiDAR device."* No physical capture has ever occurred per any evidence in this repo. |
| Physical device pilot harness (H-014B.3) | **PARTIAL** | Host app, protocols, redaction rules, and manual measurement sheet exist (`docs/h014b3/`), but they are templates/runbooks awaiting an actual pilot; `test_reports/h014b3-device/` is empty/gitignored, confirming no pilot evidence has been produced yet. |
| Central Kentucky demo property (H-014C) | **IMPLEMENTED / MOCK DATA** | Deliberately and explicitly labeled: `is_demo_fixture: true`, `dataOrigin/visualization_data_origin: demo`, `truthStatus: sample_only` (`docs/habitat/H014C_ACCEPTANCE.md`). The commit message for this exact mission states production readiness is **NOT READY**. |
| Passport truth promotion (DRAFT_CANDIDATE → VERIFIED_EXISTING) | **DESIGNED / NOT IMPLEMENTED (intentionally)** | Governed to always reject in this repo; requires an external, unbuilt authorization step (`backend/reality/audit_service.py`, `REALITY_TRUTH_PROMOTION_REJECTED` event). |
| Comprehensive Property Intelligence Report | **PARTIAL** | The PIP/contractor-package generation pipeline is real code (`projects.py`, `redaction.py`) but has only ever been exercised on demo/fixture property data; no report has been produced from a real scan or verified for accuracy against ground truth. |
| Cortex, Core (as standalone systems), ATC, Reality Foundry proper, Stratex Pro | **NOT AUDITABLE — NOT PRESENT IN THIS REPOSITORY** | No code for these exists in this environment; Habitat's only "Core" touchpoint in code is an explicitly-labeled mock (`server.py:460-476`). |

## 4. Mocked / simulated / stubbed / placeholder / synthetic-data inventory (item 6)

Direct grep evidence (`grep -rniE "mock|stub|simulat|synthetic|placeholder|fake_data|dummy"`), confirmed by reading each hit in context:

- `backend/server.py:326` — "Auto-route to matching contractors as leads (**mock brokerage routing**)".
- `backend/server.py:460-476` — function explicitly commented **"Mock STRATEX Core publishing"**.
- `backend/reality/authz.py:6-9,38` — a dedicated **"synthetic property"** (`ref-property-h014a`) used as a public reference/test fixture, separate from real properties.
- `backend/reality/capture_proof.py` (entire file) — "Development/test ONLY... drives the REAL governed capture pipeline with clearly non-authoritative **synthetic data**"; contains a hardcoded synthetic point-cloud byte constant (`_POINTCLOUD`, line 36) and a deterministic "PASS-grade" fake quality report (`GOOD_REPORT`, line 44).
- `backend/seed.py:224-225` — "prices are **sample placeholders** (0 finding price)"; the whole file seeds demo/`sample_only`-tagged records.
- `backend/fixture_provider.py` — env-gated fixture server; unconditionally disabled when `HABITAT_ENV=production`; every payload tagged `is_fixture=true`, `authoritative:false`.
- `backend/demo_property.py` — a single named demo property ("Central Kentucky Demonstration Home") with `truth_status="sample_only"` throughout.
- `frontend/src/propertyVisualization/lidarIndependentFoundations.js:2-3,46-52` — its own header states: *"Mock fixtures for state transitions — not real capture output"*, and tags data with `dataOrigin: "demo"` / `"projection_stub"`.
- `frontend/src/pages/HomeSteward.js` — a built-in **"Task 14 Failure Simulator"** UI (lines ~58-178, 1027-1031) that lets a user simulate Passport/audit/estimator outages for resiliency demos — a real feature, but explicitly simulation-only, not connected to real failure conditions.
- `backend/tests/test_projects.py:271-272` — test comment: "manually transition ... to **simulate** state progression."

No instance was found in this repo of synthetic/mock data being silently presented as verified truth without a label — every mock/fixture path found carries an explicit `is_fixture`, `authoritative:false`, `demo`, `sample_only`, or "non-authoritative" marker in the code or its immediate output. This is a genuine positive finding: **the truth-labeling discipline described in the architecture docs is actually implemented in code**, not just documented.

## 5. Test and build evidence summary (item 3; full detail in `STRATEX_TEST_AND_BUILD_EVIDENCE.md`)

| Check | Result |
|---|---|
| Backend deps (as pinned) | FAIL — 1 private package (`emergentintegrations`) unavailable outside the vendor's own environment |
| Backend deps (CI's own exclusion method) | PASS |
| Backend integration test suite | **PASS — 338 passed, 1 skipped, 0 failed** (independently executed against local MongoDB 7.0, this session) |
| Backend `reality` coverage (process-local) | 49% (informational; CI's authoritative combined-process gate of ≥83% was not reproduced) |
| Frontend install/build/tests | BLOCKED — no network access to required package host in this sandbox; not run |
| Lint/type-check | NOT CONFIGURED (tools installed as deps, never invoked) |
| Security/SAST scanning | NOT CONFIGURED |
| iOS Swift build/test workflow | Requires macOS runner, not reproducible in this sandbox; by design proves compilation only, never physical capture |

## 6. Field-data blockers (item 7; full detail in `STRATEX_FIELD_DATA_BLOCKERS.md`)

Everything touching real DJI/RTK/thermal capture, semantic object extraction,
measurement-tolerance validation, and Passport truth-promotion is either
unimplemented or backed only by a fixed synthetic fixture (12 entities, 2
frames, one demo room, one hardcoded point-cloud byte string). No M4E/M4T,
RTK, point-cloud, mesh, orthomosaic, or R-JPEG thermal ingestion code exists
in this repository at all.

## 7. Non-field-dependent remaining work (item 8; full detail in `STRATEX_FIELD_DATA_BLOCKERS.md` §2)

Frontend build-pipeline verification, lint/type-check/security CI gates,
reconciling the two duplicate state machines (`workflow.py` vs `projects.py`),
building out the "specification only" H-014 Reality Studio UI layers against
existing fixture data, fixing the unconditional external storage-init network
call at backend startup, and rotating hardcoded demo credentials are all
ordinary engineering work that does not require field data and should not be
deferred until real scans arrive.

## 8. Audit of cross-cutting concerns (item 9)

- **Evidence lineage / audit history:** Real and reasonably strong. Immutable `audit_events` + `passport_events` collections (`backend/workflow.py`, `backend/reality/audit_service.py`); the latter explicitly redacts secrets/PII before writing (`audit_service.py:12`: forbidden-field set includes `password`, `password_hash`, `authorization`, `secret`) and guarantees `REALITY_TRUTH_PROMOTION_REJECTED` is emitted even if the audit write itself fails (best-effort, per `test_result.md:510-511`, verified against `audit_service.py`).
- **Property isolation:** `backend/reality/authz.py` implements uniform 404 non-disclosure for both nonexistent and existing-but-unauthorized properties (verified in code, not just documentation) — a genuinely good security pattern (prevents property-existence enumeration).
- **Security controls:** JWT (httpOnly cookie + bearer) with bcrypt password hashing (`server.py` imports, `bcrypt==4.1.3` pinned); storage-reference validation rejects path traversal, foreign tenant/property prefixes, URLs, and encoding tricks (`backend/reality/geometry_reference.py`). No SAST/dependency-vulnerability scanning is wired into CI (gap, noted above).
- **Data contracts / API boundaries:** `backend/passport_projection.py` enforces a versioned contract (`CONTRACT_VERSION`) with explicit mismatch errors (`ContractVersionError`, `TenantMismatchError`, `PropertyMismatchError`) — a real, tested contract-boundary discipline, though only ever tested against `development`/`demo`/`test` providers, never a live production counterpart.
- **Failure handling:** Circuit breaker on the HTTP projection provider (`_CB`, 3-failure threshold, 30s cooldown, `passport_projection.py:281-284`); fail-closed (never falls back to fixture data) in production mode. Good pattern, but again never exercised against a real endpoint.
- **Persistence:** MongoDB via Motor/PyMongo; the `reality` package explicitly documents "MongoDB stores metadata only — never binary chunk bytes" (`capture_upload_service.py:21`), with binary payloads routed to governed object storage — a sound separation, verified in code, including a dedicated cleanup CLI (`cleanup_binary_chunk_docs.py`) that refuses to run without an explicit `--confirm-database` match.
- **Report generation:** PIP/contractor-package generation (`projects.py`, `redaction.py`) is real and allow-list redacted, but has only ever run against demo/fixture property data — no real-report accuracy evidence exists.
- **Deployment/configuration assumptions:** Backend hard-requires `MONGO_URL`, `DB_NAME`, `JWT_SECRET` env vars at import time (`server.py:23-25,34`) and will crash without them — reasonable fail-fast behavior, but it also unconditionally attempts to reach a specific external vendor endpoint (`integrations.emergentagent.com`) at startup regardless of configured storage provider, which this session directly observed failing (DNS resolution error) yet not crashing the app — a soft-fail that should be tightened (either honor `HABITAT_OBJECT_STORE_PROVIDER=fake` fully, or make the failure visible/alertable).
- **Third-party dependency risk:** One hard dependency (`emergentintegrations==0.2.0`) is a private, non-PyPI package not installable outside its vendor's environment — a supply-chain/portability risk flagged by the project's own CI comments. No CVE/dependency-scanning process is in place to monitor the ~30 other pinned dependencies.

## 9. Final investor-diligence conclusion (item 10)

**A. What is demonstrably built today?**
A real, working FastAPI + MongoDB backend and React frontend implementing a
homeowner planning/estimating/contractor-matching product ("Home Steward",
"Design Studio", "Homeowner Architect"), a governed publication/audit/redaction
framework, and a substantial `reality/` capture-and-storage service layer with
real authorization, checksum, coordinate-frame, and idempotent-upload logic.
338 backend integration tests pass against a real MongoDB in this audit's own
independent re-run. A Swift capture module and thin host app exist as
reviewable, CI-compilable (on macOS) source for iPhone/iPad LiDAR capture.

**B. What works using synthetic/mock data?**
The entire Reality Studio / spatial-geometry path (fixed 12-entity/2-frame
fixture), the Passport projection boundary's non-production modes, the
"Core" publish handshake (explicitly labeled mock), the governed price book
(explicitly `authoritative:false`), and the one demo property/finding set used
throughout QA and the H-014C mission. This is consistently and explicitly
labeled in code and API responses as non-authoritative — a genuine strength.

**C. What remains conventional software engineering work (no field data needed)?**
Fixing/verifying the frontend build pipeline in a network-enabled environment;
wiring the already-installed lint/type-check tools into CI; adding
security/dependency scanning; reconciling the two duplicate design-state
machines; implementing the "specification only" H-014 Reality Studio UI
layers (Room DNA, Living Digital Home, Product Graph) against existing fixture
data; fixing the unconditional external network call at backend startup; and
rotating hardcoded demo credentials.

**D. What specifically cannot be responsibly completed or validated without real property scans?**
Any claim about measurement accuracy/tolerance, semantic object extraction,
real point-cloud/mesh/orthomosaic handling, radiometric thermal data,
Property Object Graph extraction from real geometry, Passport truth-promotion
in practice, before/after verification workflows, and any real cross-app
Pro/Habitat property synchronization (no such counterpart app exists in this
audit's scope to synchronize with).

**E. Is it technically reasonable to state: "Stratex has reached the
pre-field-validation boundary, where the next meaningful development stage
requires real-world property capture data"?**
For the Habitat repository specifically: **yes, with conditions.** The
governed data model, truth-labeling discipline, storage/authz/audit machinery,
and native capture module source are genuinely built and tested against a
strict synthetic-data boundary that the project itself refuses to promote to
"verified" truth. The gating next step for the *spatial/scan* parts of this
product line is indeed real captures. However, this statement **cannot be
extended to the full Stratex platform** (ATC, Reality Foundry, Cortex, Core,
Passport, Stratex Pro, CENTCOM) on the basis of this audit, because none of
those systems' code was available to inspect. Any investor-facing claim that
covers those systems must be validated against their own repositories before
being asserted as fact.

### Final determination — "Ready to enter funded field-validation phase"

## PASS WITH CONDITIONS

Conditions:
1. Independently audit ATC/Reality Foundry/Cortex/Core/Passport/Stratex Pro
   repositories with the same rigor before making any platform-wide readiness
   claim — this report only covers Habitat.
2. Resolve the frontend build/dependency install failure in a network-enabled
   environment and obtain a real green build + test run before relying on
   frontend functionality claims.
3. Wire lint/type-check/security scanning into CI (tools are already pinned
   as dependencies but unused).
4. Fix the unconditional external network call at backend startup and replace
   the private, non-PyPI `emergentintegrations` dependency with a supply-chain
   -safe equivalent or documented vendoring strategy.
5. Complete the H-014 "specification only" Reality Studio UI/data layers so
   that, the moment real captures are available, there is a working ingestion
   path to receive them — do not wait for field data to start this work.
6. Execute the H-014B.3 physical device pilot (protocol already authored,
   `docs/h014b3/`) to produce the first real measurement-tolerance evidence
   before any accuracy claim is made publicly.
