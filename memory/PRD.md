# STRATEX HABITAT™ — Product Requirements & Build Log

## Original Problem Statement
STRATEX HABITAT™ is a separate homeowner + contractor-facing app that handshakes with the STRATEX Core operating engine. It must visually match the uploaded reference image: a premium dark control-room dashboard with neon teal + orange accents, left icon rail + section nav, central 3D digital-twin house, top KPI status cards, bottom analytics, and a right-side Inspector/quote panel. Core publishes approved scans/reports/findings to a shared (AWS) property record; Habitat consumes only published assets. Includes contractor marketplace, dual scoring (public reputation + internal trust grade), authenticity workflow, reviews/ratings, and role-based experiences.

## Architecture (this build)
- **Frontend:** React 19 + Tailwind + shadcn/ui + recharts + framer-motion. Adaptive shell (desktop full sidebars, tablet rail, mobile bottom nav). Design tokens from `design_guidelines.json`.
- **Backend:** FastAPI + MongoDB (motor). JWT auth (httpOnly cookie + Bearer) with bcrypt. Role-based access (homeowner / contractor / broker_admin / reviewer / executive).
- **Storage:** Emergent managed object storage (signed retrieval through backend) for uploads — swap to customer AWS S3 later.
- **STRATEX Core handshake:** MOCKED via `/api/core/status` and `/api/core/publish` (publishes seeded assets to the shared property record + sync log). Real Core API to be wired when URL/keys provided.

## User Personas
- **Homeowner (Alex Morgan / Villa Horizon):** views digital twin, findings, maintenance, requests quotes, compares contractors, reviews.
- **Contractor (Horizon Roofing):** receives routed leads, responds with bids, manages profile, builds reputation.
- **Executive / Broker / Reviewer:** publishes from Core, oversees marketplace.

## Implemented (2026-06-25)
- JWT auth with 5 roles + 5 seeded demo accounts; role-aware navigation & redirects.
- Homeowner Digital Twin dashboard faithfully matching reference (KPIs, layers, analytics, Inspector, Request Quote, Top Contractor Quotes).
- Findings, Systems & Assets, Maintenance, Insights, Live Telemetry, Documents (upload), Reports, Quotes, Marketplace, Contractor Profiles (dual scorecard + reviews), Reviews & Ratings, Project Requests.
- Request Quote → brokerage routing; contractor lead respond; review submission recomputes rating.
- Device-adaptive shell (phone bottom-nav, tablet side rail, desktop dense) + iOS safe-area + PWA meta; official STRATEX HABITAT logo across every window + favicon/app icon.
- **Design Studio (flagship):** real-façade exterior visualization. 13 editable zones with material-family constraints, 16-product structured materials library (mfr/profile/colors/tone/finish/durability/maintenance/energy/price-tier) with filters, 6 curated recommendation packages, 6 photorealistic preset scenarios of the actual home. Live photorealistic re-skin via Gemini Nano Banana image editing (Emergent key) stored to object storage. Before/after slider, save named scenarios with version history, favorite, compare (2-3 side-by-side), lighting modes (daylight/overcast/sunset), quick/advanced modes, and send-scenario-to-quote handoff (property ID, zones, materials, priority, project type) routed to matching contractors. Verified: 45/45 backend pytest + live render + all UI flows.

## Implemented (2026-07-22) — H-013 Wave 1, Batch 1 (production hardening: security + runtime gates)
- **Runtime/CI (#1):** Pinned `cryptography==44.0.1` + `pyOpenSSL==25.1.0` to eliminate the CI/Py3.12 `GEN_EMAIL` crash. Live runtime (py3.11, plain Mongo) never reproduced it; backend verified healthy.
- **Fixture governance (#4):** New `backend/fixture_provider.py` — env-gated (`HABITAT_ENV`/`HABITAT_ENABLE_FIXTURES`), auto-disabled in production (HTTP 409), provenance-tagged (`authoritative:false`). Applied to `/steward/fixture` + `/steward/context`.
- **Governed price-book (#7):** New `backend/pricebook.py` (version `2026.07.0`). All roof price literals removed from Steward; `/steward/estimate` now returns `price_book_version` + governed `price_provenance`.
- **Backend redaction (#9):** New `backend/redaction.py` — allow-list server-side stripping. `/steward/contractor-package` returns no PII/internal fields in preview; `?approved=true` releases contact only. 0 leaks verified.
- **Tests (#10):** `backend/tests/test_h013_security.py` (9 unit tests) + backend testing agent verified 19/19 (security gates + full H-012 regression).
- Docs: `docs/h013/H013_REPOSITORY_VERIFICATION.md`, `H013_RUNTIME_REPAIR.md`, `H013_WAVE1_BATCH1.md`.
- **Deferred to Batch 2:** #5 versioned Passport projection boundary, #6 Build-Ready publication-blocker reconciliation, #8 homeowner workflow persistence.

## Implemented (2026-07-22) — H-013 Wave 1, Batch 2 (projection boundary, publication gates, persistent workflow)
- **Passport projection boundary (#5):** `backend/passport_projection.py` — versioned (`1.0.0`), read-only adapter with production/development/demo/test provider modes. `/steward/context` served via adapter; production fails safe (503) with no fixture fallback. Contract/tenant/property/schema validation + staleness.
- **Build-Ready blocker policy (Phase 5):** `backend/readiness_policy.py` — HARD/CONDITIONAL/WARNING/INFORMATIONAL; `/steward/readiness` policy-driven (deck = conditional blocker; backward-compatible score 65).
- **Persistent workflow (Phases 6-10):** `backend/workflow.py` + `steward_workflows` collection — explicit state machine, backend publication gate (server recomputes readiness; client cannot bypass), optimistic concurrency, idempotency replay, atomic single-publish, immutable `audit_events`, indexes ensured at startup. Router at `/api/steward/workflow/*`.
- **Tests (Phase 11):** 30 new unit tests (projection/readiness/workflow) — total 39 H-013 unit tests pass. Backend testing agent 23/23; frontend regression 9/9.
- **Docs (Phase 12):** `docs/h013/PASSPORT_PROJECTION_ADAPTER.md`, `PROJECTION_CONTRACT_SCHEMA.md`, `READINESS_BLOCKER_POLICY.md`, `STEWARD_WORKFLOW_STATE.md`, `STEWARD_WORKFLOW_SECURITY.md`, `H013_WAVE1_BATCH2.md`, `H013_BATCH2_RECON.md`.
- **Honest status:** no real Passport endpoint wired (production proven fail-safe only); legacy `/steward/publish` remains ungated for H-012 compat (governed path = workflow publish); indexes ensured at startup (no production migration executed). Not production-ready/candidate.

## Implemented (2026-07-22) — H-013 Wave 1, Batch 2A (ATLAS corrective order)
- **Single governed publication path (P0 fix):** Removed a stray `@workflow_router.post("/{wf_id}/publish")` decorator on the `create_prepared_workflow` helper in `backend/workflow.py` that was shadowing the real `publish_workflow` endpoint (governed HTTP publish had been returning 405). Both the governed endpoint and legacy `POST /steward/publish` now route through the ONE `governed_publish_service` (readiness recomputed server-side; client cannot bypass).
- **Deterministic HARD_BLOCKER proof:** `readiness_overrides={RDY-OWNERSHIP:MISSING}` (non-prod hook) → 409 PUBLICATION_BLOCKED, ZERO opportunity created (db.quotes unchanged), audit `HARD_BLOCKER_DETECTED` + `PUBLICATION_BLOCKED` written, no `PROJECT_OPPORTUNITY_PUBLISHED`. Positive path creates exactly one opportunity; legacy replay is idempotent.
- **Browser journey proven governed:** `HomeSteward.js handlePublish()` now sends `acknowledged_blockers` (deck CONDITIONAL) when the Build-Ready acknowledgment switch is ON; publish button unreachable until acknowledged. Frontend E2E captured POST /steward/publish body `acknowledged_blockers=[RDY-DECK-CONDITION]` → 200 published, `workflow.origin=legacy_publish_wrapper`, `audit.publication_path=governed_shared_service`. Added data-testids across the 8-step journey.
- **Repo hygiene:** Deleted root `backend_test.py` + `backend_test_batch2.py` (hard-coded preview URLs); relocated useful scenarios into `backend/tests/test_h013_publication.py` + `test_h013_http_gates.py`; refactored `conftest.py` (config from env/.env, added `db` fixture); fixed `test_projects.py` hard-coded Mongo URL/db. `frontend/yarn.lock` now tracked.
- **Tests:** backend `pytest tests/` = 110 passed, 1 skipped (50 H-013); frontend governed journey + gate control = 2/2. Docs: `docs/h013/H013_BATCH2A_ATLAS_QC.md`.
- **Constraints honored:** No new features, no Batch 3, no Save-to-GitHub, no merge to main. Awaiting Atlas QC approval.

## Implemented (2026-06) — H-014 Property Reality Studio Constitution & Shared Spatial Architecture (SPECIFICATION ONLY)
- Delivered 22 architecture/specification documents + index under `docs/h014/` (Phases 1–22). No code implemented; backend/frontend untouched. Baseline accepted commit `c2fc57e`.
- Core decisions: ONE shared spatial domain model (Interior/Exterior/Systems are views, not separate apps); ONE property coordinate frame with PLANNING tolerance (never survey-grade unless proven); ONE mandatory truth taxonomy (11 classes) on every datum; Room/Property DNA as projections (not canonical); ONE Reality Studio design state machine following accepted H-013 governance (single governed publication, non-overridable HARD blockers).
- Reuses (does not replace) H-013: projection boundary, workflow governance, readiness policy, price book, redaction, fixtures, object storage, projects/PIP, audit/passport events.
- Consistency validation: internally consistent + consistent with H-013 baseline (doc-level only; no runtime/tests/UI). Awaiting General Atlas QC. Not production, not implemented.

## Implemented (2026-06) — H-014A Reality Studio backend foundation (targeted null-fallback correction)
- Fixed 2 reproduced nullable-field defects using explicit `None`-only checks (NOT `or`, to preserve validation of malformed supplied values):
  - `reality/coordinate_service.create_frame`: omitted/null `transform_to_parent`/`transform_to_property` → identity default; supplied invalid matrices still rejected by `validate_transform`.
  - `reality/artifact_service.create_manifest`: omitted/null `storage_object_reference` → governed default key; added `validate_storage_reference` rejecting blank/URL/absolute/signed/traversal refs (no silent fallback); public view still emits only the `<governed-object-store-reference>` token.
- Added 20 focused regression tests (frame + storage-ref, unit + HTTP) in `tests/test_h014a_reality.py`.
- Validation: 2 orig-fail tests PASS; H-014A suite 59 PASS; H-013 security/publication/gates 20 PASS; full backend 169 PASS / 1 skipped (pre-existing live-Gemini render, unrelated). Local commit `5142c0f`. NOT accepted / NOT production-ready — awaiting General Atlas QC. No Save-to-GitHub, no merge to main.

## Implemented (2026-06) — H-014A Final Closure (Phases 1-6)
- **Phase 1 (ownership-safe storage ref):** artifact default = `tenant/{authenticated_tenant}/property/{authorized_property}/reality/{server_artifact_id}` via `server_tenant_id()` + authorized scan property; client tenant/property overrides ignored; cross-tenant 403, cross-property source 422; `public_view` masks raw key to `<governed-object-store-reference>` (no URL/credential/signed-URL/bucket-path leak).
- **Phase 2 (nullable-default sweep):** explicit `is None` fallbacks (never `value or default`) across coordinate transforms, artifact `content_type`/`file_size`/`storage_object_reference`, spatial `label` (→ entity_type), existing-model collections (→ []/{}), design `proposed_entities`/`deltas`. Full field decision table in `docs/h014a/H014A_COMPLETION_REPORT.md`.
- **Phase 3:** transform validator rejects `inf`/`-inf`/`nan` (unit); malformed JSON rejected safely (4xx, never 500).
- **Phase 4:** 12 `docs/h014a/H014A_*.md` documents; PRD + test_result.md updated.
- **Phase 5/6:** 17 routes registered; H-014A 81 PASS / full backend 191 PASS, 1 unrelated skip, 0 fail; measured coverage (coverage 7.15.2, server subprocess + in-process unit, combined) reality package **75% line + branch**, artifact_service 89%.
- Files changed vs `5142c0f`: `reality/artifact_service.py`, `reality/model_version_service.py`, `reality/spatial_service.py`, `reality/fixtures.py`, `tests/test_h014a_reality.py` + docs. NOT accepted / NOT production-ready — awaiting General Atlas QC. No LiDAR, no 3D editor, no Save-to-GitHub, no merge to main.

## Implemented (2026-06) — H-014A.1 post-acceptance hardening (QC-1..QC-4)
- H-014A was ACCEPTED WITH NON-BLOCKING DEBT; H-014A.1 closes all four Atlas QC findings (backend-only, narrow scope).
- **QC-1:** uniform `404 NOT_FOUND` for nonexistent AND existing-but-unauthorized real properties/objects (`authz.not_found_nondisclosure()`); reference-room synthetic public id keeps `403`.
- **QC-2:** `validate_storage_reference(value, *, tenant_id, property_id)` enforces the server-derived `tenant/{tenant}/property/{property}/reality/` prefix; rejects foreign tenant/property, URL/signed-URL, absolute/traversal/repeated-slash/dot-segment/percent/backslash/fragment/whitespace/case tricks. Default stays server-generated.
- **QC-3:** `assemble_view` reads the fixed fixture id set only → deterministic (2 frames / 12 entities) regardless of dev writes.
- **QC-4:** `REALITY_TRUTH_PROMOTION_REJECTED` emitted once on denial (sanitized, tenant/property/actor bound), best-effort (denial survives audit failure).
- Validation: H-014A 111 pass, H-013 20 pass, full backend 221 pass/1 unrelated skip, 17 routes, frontend 100% (`iteration_5.json`), coverage 78% (artifact_service 91%, authz 68%). Writes isolated to `reality_*`+`audit_events`. Docs: `docs/h014a/H014A_1_HARDENING_REPORT.md`. Local-only, not production-ready, H-014B not authorized.

## Backlog
- **P0 (next):** Wire real STRATEX Core API (replace mock publish/sync) once URL/keys provided; swap Emergent storage → customer AWS S3 with signed URLs + version history.
- **P1:** Authenticity review queue UI (metadata/URL/screenshot → pending/verified/rejected) influencing external-proof confidence; award/dispute lifecycle on quotes; LLM-generated AI findings; Design Studio + Scenario Planner interactive modeling.
- **P2:** Real 3D twin (react-three-fiber) with clickable asset hotspots driving the Inspector; historical comparison timeline; contractor job-photo galleries; notifications system.

## Next Tasks
1. Confirm STRATEX Core API contract + AWS credentials with user, then replace mocks.
2. Build the authenticity vetting queue (reviewer role).
