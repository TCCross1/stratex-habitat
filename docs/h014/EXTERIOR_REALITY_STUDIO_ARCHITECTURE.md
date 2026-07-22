# EXTERIOR REALITY STUDIO ARCHITECTURE (Phase 10)

Version 1.0.0 · Specification only. Exterior Studio is a **view + editor over the same shared
spatial model** (Phase 3) as Interior Studio — the exterior of the very building whose interior
was scanned. **This mission does not implement Exterior Studio** (roadmap H-014H+); this defines
its architecture and its shared-model contract so it cannot become a disconnected 3D app.

---

## 1. Ingest sources
| Source | Produces | Frame |
|---|---|---|
| Drone reconstruction | Orthomosaic, mesh, roof planes, elevations | `DRONE_FRAME` → `PROPERTY_FRAME` |
| Exterior LiDAR / handheld | Mesh/point cloud | `SCAN_LOCAL` → `PROPERTY_FRAME` |
| Photogrammetry | Mesh + textures | `SCAN_LOCAL` → `PROPERTY_FRAME` |
| Thermal | Thermal overlay (AWE) | Registered to RGB/mesh |

All ingest is governed by Scan Session (Phase 5), aligned via Phase 4, classified via Phase 7.

## 2. Editable exterior entities (shared model)
Roof geometry (`ROOF_PLANE`) · elevations (`EXTERIOR_ELEVATION`) · windows/doors (`OPENING`) ·
siding & trim (`SURFACE`) · decks/porches · driveways · patios · walkways · concrete pads ·
retaining walls · pools · pool houses (`BUILDING`) · landscaping zones · drainage · site features
(`SITE_FEATURE`) · exterior additions (`PROPOSED_ADDITION`).

## 3. Capabilities
- Product & material replacement (siding, roofing, trim, doors, windows, gutters) — this **subsumes
  the existing Design Studio façade re-skin** (`design.py`, Gemini Nano Banana render) as a labeled
  `AI_SUGGESTED_DESIGN`/`PROPOSED_DESIGN` visualization over the real exterior model.
- Maintenance & damage layers; thermal/AWE overlay; historical scan comparison; proposed improvement
  visualization; whole-property additions.

## 4. Interior ↔ exterior registration (anti-fragmentation)
- Because exterior elevations and interior perimeter walls attach to the same `BUILDING`/`LEVEL`
  nodes and are aligned to one `PROPERTY_FRAME` (Phase 4), an exterior window and its interior
  opening are the **same** logical `OPENING` viewed from two sides. Changing one is reflected as a
  linked change (with truth labeling) — the two studios cannot diverge into separate homes.

## 5. Truth & overlays
- Roof/elevation geometry from drone is `MEASURED_EXISTING` (or `ESTIMATED_EXISTING` for gaps);
  canonical roof facts remain Passport/Core-owned and are referenced.
- Damage/thermal are overlays (Phase 12) with their own source, version, and truth class; they never
  assert structural conclusions.

## 6. Existing Design Studio migration (documented, not executed)
- `design_scenarios`, `design_products`, `design_bases`, ZONES, recommendations, preset scenarios,
  and the render pipeline map onto Exterior Studio DESIGN_ELEMENTs + Product Graph (Phase 14). The
  current 2D façade image re-skin remains valid as a `VISUALIZATION`-tolerance preview until the 3D
  exterior model exists. No migration is performed in this mission.

## 7. Boundaries
- No structural/drainage/engineering claims; site/grading/drainage are advisory and flagged for
  professional verification.

## 8. Relationship to existing code
- Reuses `design.py` assets, object storage renders, and the projection boundary. Foundation only.
