# LIVING DIGITAL HOME — LAYER ARCHITECTURE (Phase 12)

Version 1.0.0 · Specification only. The Living Digital Home is the unified, layered visualization of
the shared spatial model (Phase 3). Every layer is a governed view with an explicit owner, source,
version, truth class, and homeowner-safe display rules. Layers stack over ONE property — this is
what keeps Interior, Exterior, and Systems a single home.

---

## 1. Layer catalogue
| Layer | Content | Primary owner |
|---|---|---|
| RGB reality mesh | Textured photorealistic mesh | Habitat (from scan) / Core |
| LiDAR geometry | Structured surfaces/openings | Habitat (from scan) |
| Point cloud | Raw/decimated points | Habitat (scan artifact) |
| Floor plan | 2D plan | Habitat (derived) |
| Structural | Load-bearing elements | Core/Passport (verified) |
| Roof | Roof planes | Habitat (drone) / Core |
| Exterior elevations | Façades | Habitat (drone) / Core |
| Materials | Finishes/products | Habitat (design) |
| Windows & doors | Openings | Habitat / Core |
| Systems | Electrical/plumbing/HVAC/etc. | Core-verified where known, else Habitat/UNKNOWN |
| Thermal / AWE | Thermal & anomaly overlay | Core/Habitat (evidence) |
| Moisture | Moisture signals | Core (evidence) |
| Damage | Damage annotations | Core/Habitat |
| Maintenance | Tasks/schedules | Habitat + Passport |
| Warranty | Warranty coverage | Passport/Core |
| Findings | Inspection findings | Passport/Core |
| Measurements | Dimensions | Habitat (measured/estimated) |
| Historical scans | Prior captures | Habitat (versioned) |
| Proposed design | Proposed changes | Habitat (planning) |
| Products | Selected/installed products | Habitat |
| Cost | Estimates/allowances | Habitat |
| Build Ready | Readiness state | Habitat (policy) |
| Completed work | As-built | Core/Passport |

## 2. Mandatory per-layer contract (illustrative)
```jsonc
{
  "layer": "PROPOSED_DESIGN",
  "data_owner": "HABITAT",
  "source": "DESIGN_EDITOR",
  "version": "7",
  "truth_classification": "PROPOSED_DESIGN",     // Phase 7 (dominant class for the layer)
  "visibility_permissions": ["HOMEOWNER","PROFESSIONAL"],   // Phase 19
  "staleness": { "generated_at":"…","stale": false, "reason": null },
  "relationship_to_passport": "REFERENCES_CANONICAL|NONE|WRITE_BACK_CANDIDATE",
  "relationship_to_core": "CONSUMES_EVIDENCE|NONE|SUBMITS_FOR_REVIEW",
  "relationship_to_habitat": "AUTHORED_HERE|RENDERS",
  "homeowner_safe_display": {
     "label": "Proposed design", "must_label": true,
     "never_present_as": "existing verified condition",
     "color_plus_icon": true }
}
```

## 3. Homeowner-safe display rules (all layers)
- Verified-existing, estimated-existing, homeowner-reported, AI-suggested, proposed, professionally
  reviewed, and completed layers are always visually distinct (icon + label + color; never color
  alone — Phase 7 §4).
- Proposed/AI layers can be toggled against existing; they are never blended into existing without a
  visible label.
- Stale layers show a staleness indicator; `UNKNOWN` regions render as explicit gaps, not filled.

## 4. Ownership & boundary invariants
- Canonical layers (structural, findings, warranty, completed) are **read-only projections** from
  Passport/Core; Habitat renders them and cannot edit them.
- Habitat-owned layers (proposed design, products, cost, measurements, build-ready) are clearly
  `authoritative:false`.

## 5. Composition
- All layers share the property's `PROPERTY_FRAME` and node IDs, so any layer can be spatially cross
  -referenced (e.g., a moisture anomaly on the exact wall a homeowner is refinishing).

## 6. Relationship to existing code
- Extends the Digital Twin page (`/twin`) and the projection boundary. Each layer's data owner maps
  to Core/Passport/Habitat per the operating model. No implementation in this mission.
