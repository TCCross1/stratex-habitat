# INTERIOR REALITY STUDIO ARCHITECTURE (Phase 9)

Version 1.0.0 · Specification only. Interior Studio is a **view + editor over the shared spatial
model** (Phase 3), not a standalone 3D app. It fulfills the promise: *Scan it. Walk it. Redesign
it. Price it. Build it.*

---

## 1. Capability map
| Capability | Description | Backing |
|---|---|---|
| Guided LiDAR capture | Room-by-room capture with Guardian coaching | Phase 5 + 6 |
| Editable 2D plan | Top-down plan; drag walls/openings | Shared model + PLANNING tolerance |
| Editable 3D model | Same data in 3D; consistent with 2D | Shared model |
| Room segmentation | Auto-detect rooms/surfaces; homeowner corrects | Scan processing + Guardian |
| Openings | Doors/windows/passthroughs as OPENING nodes | Phase 3 |
| Adjoining-room relationships | Shared walls/openings link rooms | Phase 4 alignment |
| Wall movement | Move/add/remove walls (PROPOSED_DESIGN) | Phase 7 labeling |
| Room additions | PROPOSED_ADDITION nodes | Phase 3 |
| Product placement | Place PRODUCT_INSTANCE (fixtures, cabinetry) | Phase 14 |
| Material replacement | Change finishes/paint/trim/flooring | Phase 14 |
| Lighting placement | Fixtures + lighting modes | Phase 14 |
| Cabinetry & built-ins | Parametric/product-based elements | Phase 14 |
| Fixtures & equipment | System-linked devices | Phase 11 |
| Walkthrough | First-person navigation of proposal | Client render |
| AR preview | On-device overlay (later wave) | Roadmap H-014E |
| Design alternatives | Multiple DESIGN_ELEMENT sets to compare | Phase 16 |
| Undo/redo | Per-edit reversible ops | Editor session |
| Version history | Named, versioned design snapshots | Phase 16 |
| Collaboration | Shared view with roles | Phase 19 access |
| Professional review | Gated review of a design | Phase 16 states |
| Estimate synchronization | Live cost/confidence on edit | Phase 15 |
| Contractor-ready package | Redacted package from gated state | Phase 14/19 + projects PIP |

## 2. Existing vs proposed (hard rule)
- The existing scanned/canonical model and the proposed edits are separate layers (Phase 12) with
  distinct truth classes (Phase 7). Proposed geometry is always labeled and can be toggled on/off
  against existing. They are never merged silently.

## 3. Editing model
- Edits create/modify DESIGN_ELEMENT / PROPOSED_ADDITION nodes referencing the existing node they
  change (`base_ref`), preserving the existing node untouched.
- Each edit is an auditable op with actor + timestamp; undo/redo operates on the op log.
- Moving a wall recomputes affected room areas as PLANNING-tolerance estimates (never survey-grade).

## 4. Estimate synchronization
- Any product/material/geometry change emits a recompute request to the estimating service
  (Phase 15); cost + confidence + assumptions update live and are labeled by source.

## 5. Walkthrough & alternatives
- Walkthrough renders the currently selected alternative; homeowner can switch alternatives and
  compare side-by-side; cost/confidence shown per alternative.

## 6. Handoff
- When a design reaches the gated `CONTRACTOR_PACKAGE_READY` state (Phase 16), a redacted contractor
  package is generated (reusing projects PIP + `redaction`), carrying labeled truth states,
  assumptions, unknowns, and required verifications.

## 7. Boundaries
- No structural/code assertions; wall changes flagged for professional/field verification when they
  imply structural impact (`STRUCTURAL_ELEMENT` remains `UNKNOWN` unless Core-verified).
- Interior imagery is sensitive (Phase 19).

## 8. Relationship to existing code
- The Home Steward journey (`HomeSteward.js`) and `projects.py` provide the planning/handoff spine;
  Interior Studio adds the spatial capture + editor surface over the shared model. No implementation here.
