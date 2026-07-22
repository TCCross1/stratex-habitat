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

## Backlog
- **P0 (next):** Wire real STRATEX Core API (replace mock publish/sync) once URL/keys provided; swap Emergent storage → customer AWS S3 with signed URLs + version history.
- **P1:** Authenticity review queue UI (metadata/URL/screenshot → pending/verified/rejected) influencing external-proof confidence; award/dispute lifecycle on quotes; LLM-generated AI findings; Design Studio + Scenario Planner interactive modeling.
- **P2:** Real 3D twin (react-three-fiber) with clickable asset hotspots driving the Inspector; historical comparison timeline; contractor job-photo galleries; notifications system.

## Next Tasks
1. Confirm STRATEX Core API contract + AWS credentials with user, then replace mocks.
2. Build the authenticity vetting queue (reviewer role).
