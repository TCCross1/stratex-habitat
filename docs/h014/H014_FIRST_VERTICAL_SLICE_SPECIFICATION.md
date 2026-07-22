# H-014 FIRST VERTICAL SLICE SPECIFICATION (Phase 17)

Version 1.0.0 · **Specification only — do not fully implement.** Defines the first controlled
implementation slice so a future wave (H-014A→E) can build it incrementally with clear acceptance
gates. Nothing here is built in this mission.

---

## 1. Reference scenario
A homeowner scans an existing **living room** with an iPhone/iPad (LiDAR). The system: (1) guides
the scan, (2) detects missing coverage, (3) builds the existing room model, (4) identifies walls,
floor, ceiling, doors, windows, openings, (5) allows review/correction, (6) lets the homeowner
describe a connected **family-room addition**, (7) generates editable design alternatives, (8)
allows changes to flooring, paint, trim, windows, lighting, (9) provides 2D + 3D views, (10)
provides a walkthrough, (11) updates the planning estimate, (12) saves design versions, (13) runs
preliminary Build-Ready checks, (14) produces a contractor-package preview.

## 2. Screens (slice subset — Phase 18 for full system)
Property overview → Reality Studio launch → Scan preparation → Guided scan (live coverage) →
Scan-quality review (Guardian) → Existing model review (2D/3D, correct segmentation) → Design draft
(describe addition + alternatives) → Materials/products (flooring, paint, trim, windows, lighting) →
Walkthrough → Estimate → Build-Ready review → Contractor-package preview → Version history.

## 3. APIs (proposed, `/api/reality/*` — not implemented)
| Method/Path | Purpose |
|---|---|
| `POST /api/reality/scan-sessions` | Create scan session (Phase 5) |
| `POST /api/reality/scan-sessions/{id}/artifacts` | Chunked/resumable artifact upload (Phase 13) |
| `POST /api/reality/scan-sessions/{id}/complete` | Mark capture complete → processing |
| `GET  /api/reality/scan-sessions/{id}/guardian` | Guardian verdict (Phase 6) |
| `POST /api/reality/scan-sessions/{id}/accept` | Accept scan → build existing model |
| `GET  /api/reality/rooms/{id}/model` | Existing room model (shared spatial nodes) |
| `PATCH /api/reality/rooms/{id}/segmentation` | Homeowner corrections |
| `POST /api/reality/designs` | Create design project (state machine, Phase 16) |
| `POST /api/reality/designs/{id}/additions` | Add PROPOSED_ADDITION (family room) |
| `POST /api/reality/designs/{id}/alternatives` | Generate/compare alternatives (governed AI) |
| `PATCH /api/reality/designs/{id}/elements` | Change flooring/paint/trim/windows/lighting |
| `GET  /api/reality/designs/{id}/estimate` | Live estimate (Phase 15) |
| `POST /api/reality/designs/{id}/versions` | Save version |
| `GET  /api/reality/designs/{id}/build-ready` | Readiness policy result |
| `POST /api/reality/designs/{id}/contractor-package/preview` | Redacted package preview |

All read paths that touch canonical truth go through the projection boundary; publication uses the
single governed service.

## 4. Domain models (reuse Phases 3/5/7/16)
Scan session · spatial nodes (ROOM/SURFACE/OPENING/PROPOSED_ADDITION/DESIGN_ELEMENT/PRODUCT_INSTANCE)
· design project (state machine) · estimate lines · artifact records. New collections (documented):
`scan_sessions`, `spatial_nodes`, `reality_designs`, `spatial_artifacts`.

## 5. State transitions exercised
`IDEA_CAPTURED → SCAN_REQUIRED → SCAN_IN_PROGRESS → SCAN_QUALITY_REVIEW → SCAN_ACCEPTED →
EXISTING_MODEL_CREATED → EXISTING_MODEL_REVIEWED → DESIGN_DRAFT → AI_SUGGESTION_READY →
HOMEOWNER_EDITING → ALTERNATIVES_REVIEWED → PRODUCTS_SELECTED → ESTIMATE_READY →
BUILD_READY_REVIEW → CONTRACTOR_PACKAGE_READY` (stops at package **preview**; no publish in slice).

## 6. Storage artifacts
Raw LiDAR + RGB (immutable, RESTRICTED_IMAGERY), processed mesh, floor plan, preview model,
thumbnails, design versions, report render — all via signed access (Phase 13).

## 7. Validation rules
- No existing dimension shown without truth class + confidence; unknown regions rendered as gaps.
- Proposed addition always labeled PROPOSED_DESIGN; alternatives are AI_SUGGESTED_DESIGN until edited.
- Estimate labeled planning-only; allowances flagged; `UNKNOWN_COST` where scope undetermined.
- Build-Ready uses the server-owned policy; HARD blockers cannot be overridden.

## 8. Security rules
Tenant + property authorization on every call; interior imagery restricted; signed artifact access;
audit events on every state change and package preview.

## 9. Test plan (for the future build wave)
- Unit: state-machine guards, truth-classification labeling, estimate confidence roll-up.
- Integration: scan-session lifecycle (create→upload→complete→guardian→accept), model build,
  edit→estimate recompute, build-ready gate, package preview redaction.
- E2E (browser): the 14-step reference journey with data-testids; assert governed paths + labels.
- Negative/anti-fabrication: gaps stay UNKNOWN; proposed never shown as existing; HARD blocker blocks
  package readiness.

## 10. Acceptance criteria
- The reference journey completes to `CONTRACTOR_PACKAGE_READY` preview with correct truth labeling,
  live estimate + confidence, saved versions, and a redacted package preview — with full audit trail
  and no fabricated data. LiDAR capture may be simulated/fixture-gated in early waves (clearly labeled).

## 11. Implementation waves
H-014A (foundations) → H-014B (capture + Guardian) → H-014C (existing 2D/3D twin) → H-014D (addition +
alternatives) → H-014E (products + walkthrough + estimate sync). See Roadmap (Phase 20).
