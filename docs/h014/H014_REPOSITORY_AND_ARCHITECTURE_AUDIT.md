# H-014 — Repository & Architecture Audit (Phase 1)

Status: **Architecture/specification only.** No code changed. Baseline accepted commit
`c2fc57eae2f30eefb23c676a8279852ef9478285` (HEAD of `copilot/tcc-1-update-documentation`).

Purpose: inventory the proven, accepted Habitat architecture so H-014 **extends** it rather
than rebuilding it. Every H-014 concept below maps to an existing owner where one exists.

---

## 1. Backend modules inspected

| Module | Role today | H-014 disposition |
|---|---|---|
| `backend/server.py` | FastAPI app, JWT (httpOnly cookie + bearer, bcrypt), route mounting, object-storage client (Emergent managed), `/upload` + signed retrieval, Design Studio endpoints, startup seed + index init | **Reuse.** Add H-014 routers later under `/api/reality/*`; reuse auth, storage, startup pattern. |
| `backend/passport_projection.py` | Versioned, read-only Passport projection adapter (modes production/development/demo/test), envelope + provenance + truth classification + validation + circuit breaker; production fails safe (503) | **Reuse + extend.** H-014 spatial projections (geometry, Room DNA) become new projection categories behind the SAME adapter/boundary. |
| `backend/workflow.py` | Persistent Steward workflow state machine, optimistic concurrency, idempotency, single governed publication service, immutable audit events, index init | **Reuse as pattern.** The H-014 Design State Machine (Phase 16) follows this exact governance shape; publication continues through the ONE governed service. |
| `backend/readiness_policy.py` | Server-owned Build-Ready blocker policy (HARD / CONDITIONAL / WARNING / INFORMATIONAL) | **Reuse + extend.** Reality Studio Build-Ready gates add spatial/scan/systems readiness items to this policy. |
| `backend/pricebook.py` | Governed, versioned price book (roof assemblies) with provenance `authoritative:false` | **Reuse + extend.** Estimating (Phase 15) generalizes this to a governed regional planning allowance across categories. |
| `backend/redaction.py` | Allow-list, server-side contractor-package redaction | **Reuse + extend.** Add raw-imagery/interior-scan restrictions (Phase 19). |
| `backend/fixture_provider.py` | Env-gated deterministic fixtures, production-disabled, provenance-tagged | **Reuse.** Scan/geometry demo data must route through this gate; never served silently as truth. |
| `backend/steward.py` | H-012 Home Steward slice (context via projection, ask, recommend, confirm→creates design_scenario, estimate, readiness, contractor-package, publish wrapper, memory) | **Reuse.** Reality Studio is the spatial evolution of this planning surface; the Steward remains the conversational entry. |
| `backend/design.py` | Design Studio (exterior façade) — zones, product library, recommendations, preset scenarios, seed; Gemini Nano Banana re-skin render → object storage | **Reuse + subsume.** Becomes the seed of **Exterior Reality Studio** (Phase 10). Zones/products/recommendations feed the Product Graph (Phase 14). |
| `backend/projects.py` | Homeowner Architect projects: state machine (IDEA→…→SAVED_TO_PASSPORT), design_concepts, product_selections, project_assumptions, PIP generation, contractor matching, quotes, Passport event mapping | **Reuse + extend.** This is the existing design→contractor→completion spine; H-014 aligns its state machine (Phase 16) and PIP → contractor package. |

## 2. Frontend inspected
- Routing (`frontend/src/App.js`): `/twin`, `/steward`, `/systems`, `/design-studio`, `/quotes`, `/marketplace`, `/contractors`, `/reviews`, `/documents`, `/reports`, etc.
- Adaptive shell: `components/layout/{AppShell,IconRail,SectionNav,MobileNav,TopNav}.js` (desktop rail + mobile bottom nav). `Inspector.js`, `Primitives.js`, `Brand.js`.
- `pages/HomeSteward.js` — the guided 8-step planning journey (now governed-publish wired, data-testids added in H-013 Batch 2A).
- Design system: deep-black `#0a0a0b`, teal `#14f1d9`, orange `#ff6b00`, mono/technical type.

## 3. Data collections in use (MongoDB)
`users, properties, analytics, assets, findings, maintenance, insights, quotes, contractors,
reviews, documents, reports, files, sync_log, design_products, design_bases, design_scenarios,
habitat_projects, design_concepts, product_selections, project_assumptions,
project_intent_packages, steward_memories, steward_workflows, audit_events, passport_events`.

## 4. Existing truth / classification concepts (to unify, not duplicate)
- Projection truth classes: `VERIFIED, ESTIMATED, PROJECTED, HOMEOWNER_REPORTED, SUGGESTED, UNKNOWN` (`passport_projection.TRUTH_CLASSES`).
- Product compatibility: `VERIFIED_FIT, LIKELY_COMPATIBLE, REQUIRES_FIELD_VERIFICATION, CONCEPT_VISUALIZATION_ONLY, UNAVAILABLE, PRICE_NEEDS_CONFIRMATION` (`projects.py`).
- Readiness classes: `HARD_BLOCKER, CONDITIONAL_BLOCKER, WARNING, INFORMATIONAL_GAP` (`readiness_policy.py`).
- Passport event vocabulary: `DESIGN_CONCEPT_SELECTED … INSTALLED_PRODUCTS_RECORDED` (`projects.py`).

**Finding:** truth vocabulary is fragmented across three modules. Phase 7 defines ONE spatial
truth taxonomy and maps the legacy vocabularies onto it (no breaking rename in H-014 docs).

## 5. Reusable architecture (explicit)
1. **Projection boundary** (`passport_projection`) — the ONLY read path to canonical truth. Extend with spatial categories.
2. **Governed state machine + single publication service** (`workflow`) — template for the Design State Machine.
3. **Server-owned readiness policy** (`readiness_policy`) — extend for scan/spatial/systems Build-Ready.
4. **Governed price book + provenance** (`pricebook`) — generalize for estimating/cost confidence.
5. **Allow-list redaction** (`redaction`) — extend for raw imagery / interior scans.
6. **Env-gated fixtures** (`fixture_provider`) — for scan/geometry demo data.
7. **Object storage + signed retrieval** (`server.py` `/upload`) — basis for the spatial asset/artifact store.
8. **Projects spine + PIP + contractor matching** (`projects`) — basis for contractor handoff.
9. **Immutable `audit_events` + `passport_events`** — basis for auditability + completion write-back.

## 6. Gaps / missing boundaries (what H-014 adds, as spec only)
- No shared **spatial domain model** (property → building → level → room → surface → opening …). ➜ Phase 3.
- No **coordinate/alignment standard** unifying interior LiDAR + exterior drone frames. ➜ Phase 4.
- No **scan-session** model or **scan-quality guardian**. ➜ Phases 5–6.
- No **Room DNA** projection concept. ➜ Phase 8.
- No editable interior 2D/3D model concept. ➜ Phase 9 (Interior), Phase 10 (Exterior).
- No layered **Living Digital Home** contract. ➜ Phase 12.
- No spatial **asset/artifact lineage** (raw vs derived, checksums, retention). ➜ Phase 13.

## 7. Duplicate / conflicting concepts to reconcile (docs only)
- Two design state machines: Steward `workflow.py` (planning/publication) and `projects.py`
  (IDEA→…→SAVED_TO_PASSPORT). Phase 16 defines ONE canonical Reality Studio state machine and
  documents how the existing two map into it — **without rewriting either in this mission**.
- Two "design scenario" stores: `design_scenarios` (façade) and `design_concepts` (kitchen).
  Phase 8/14 treat both as Design Elements / alternatives under the shared model.

## 8. Non-goals confirmed
No implementation, no LiDAR app, no 3D editor, no Exterior Studio build, no new production
integrations, no storage-vendor lock-in beyond the existing Emergent object store abstraction.
