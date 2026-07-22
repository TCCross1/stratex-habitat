# SHARED SPATIAL DOMAIN MODEL (Phase 3)

Version 1.0.0 · Specification only. This is the anti-fragmentation core: **one** spatial hierarchy
consumed by Interior Studio, Exterior Studio, Home Systems Studio, Property Passport projections,
and the Living Digital Home. Interior and Exterior are **views over the same model**, never
separate 3D apps.

---

## 1. Single source of spatial truth (rule)
- There is exactly **one** spatial graph per property. Interior, exterior, systems, findings,
  designs, and products all attach to nodes in this one graph.
- Habitat persists **planning** spatial state; canonical/approved spatial truth is read from
  Passport via the projection boundary (Phase 8 / H-013 `passport_projection`).
- No studio may invent its own parallel geometry store.

## 2. Entity hierarchy
```
PROPERTY
└─ BUILDING (1..n: house, garage, ADU, pool house)
   ├─ EXTERIOR_ELEVATION (N/E/S/W + obliques)
   │  └─ SURFACE (siding field, trim, veneer) → OPENING(DOOR|WINDOW)
   ├─ ROOF_PLANE (per slope) → SURFACE
   └─ LEVEL (floor: basement, L1, L2, attic)
      └─ ZONE (open-plan area / functional group)
         └─ ROOM
            ├─ SURFACE (WALL | FLOOR | CEILING)
            │  └─ OPENING (DOOR | WINDOW | passthrough) ── STAIR (spans levels)
            ├─ STRUCTURAL_ELEMENT (column, beam, header) [truth-gated]
            ├─ SYSTEM (electrical/plumbing/HVAC/…) → EQUIPMENT / FIXTURE
            ├─ PRODUCT_INSTANCE (installed or proposed product)
            ├─ ANNOTATION / FINDING_LOCATION
            ├─ DESIGN_ELEMENT / PROPOSED_ADDITION
            └─ (site) SITE_FEATURE attaches at PROPERTY/BUILDING
```
Cross-cutting: `SYSTEM`, `FINDING_LOCATION`, `PRODUCT_INSTANCE`, `DESIGN_ELEMENT`,
`PROPOSED_ADDITION`, `SITE_FEATURE`, `ANNOTATION` may attach at multiple levels.

## 3. Entity catalogue
| Entity | Meaning | Typical parent |
|---|---|---|
| PROPERTY | The parcel + all buildings | — |
| BUILDING | A distinct structure | PROPERTY |
| LEVEL | A floor/story | BUILDING |
| ZONE | Functional grouping of rooms/areas | LEVEL |
| ROOM | Enclosed interior space | ZONE/LEVEL |
| EXTERIOR_ELEVATION | A façade orientation | BUILDING |
| ROOF_PLANE | A roof slope/facet | BUILDING |
| SURFACE | Wall/floor/ceiling/siding/roof face | ROOM / ELEVATION / ROOF_PLANE |
| OPENING | Generic aperture | SURFACE |
| DOOR / WINDOW | Specialized openings | SURFACE |
| STAIR | Vertical circulation | LEVEL/ROOM |
| CEILING / FLOOR / WALL | Specialized SURFACE roles | ROOM |
| STRUCTURAL_ELEMENT | Load-bearing member (truth-gated) | ROOM/LEVEL |
| SYSTEM | Electrical/plumbing/HVAC/etc. network | ROOM/LEVEL/BUILDING |
| FIXTURE | Terminal system device (sink, outlet) | ROOM/SYSTEM |
| EQUIPMENT | System plant (furnace, panel) | ROOM/SYSTEM |
| PRODUCT_INSTANCE | A chosen/installed product occurrence | SURFACE/ROOM/OPENING |
| ANNOTATION | Homeowner/AI/pro note | any |
| FINDING_LOCATION | Anchor of a Core finding | SURFACE/ROOM/ROOF_PLANE |
| DESIGN_ELEMENT | A proposed change | any |
| PROPOSED_ADDITION | New room/structure proposal | LEVEL/BUILDING |
| SITE_FEATURE | Driveway, deck, pool, landscape zone | PROPERTY/BUILDING |

## 4. Mandatory attributes (every entity)
Each node carries this envelope (illustrative, non-binding shapes — not runtime code):
```jsonc
{
  "id": "spx-<uuid>",                 // stable ID
  "tenant_id": "stratex-habitat",
  "property_id": "<uuid>",
  "type": "ROOM",
  "parent_id": "spx-...",             // parent relationship
  "child_ids": ["spx-..."],           // child relationships
  "coordinate_ref": "PROPERTY_FRAME|LEVEL_LOCAL|SCAN_LOCAL",  // Phase 4
  "geometry_type": "MESH|PLANE|POLYGON|POLYLINE|POINT|BBOX|PARAMETRIC",
  "geometry_version": "3",
  "geometry_ref": "art-<uuid>",       // asset/artifact pointer (Phase 13), not inline blobs
  "source": "PASSPORT|CORE|INTERIOR_LIDAR|EXTERIOR_DRONE|PHOTOGRAMMETRY|HOMEOWNER|AI|DERIVED",
  "truth_classification": "MEASURED_EXISTING",   // Phase 7 (mandatory)
  "confidence": "HIGH|MEDIUM|LOW|UNKNOWN",
  "units": "METRIC_M",                // Phase 4 canonical; display may convert
  "state": "EXISTING|PROPOSED|COMPLETED",
  "effective_at": "2026-06-01T00:00:00Z",
  "created_at": "…", "updated_at": "…",
  "provenance": { "producer": "…", "method": "…", "session_id": "scan-…", "version": "…" },
  "canonical_passport_ref": "PASSPORT-…|null",   // where applicable
  "audit_refs": ["evt-…"],
  "access_classification": "HOMEOWNER|CONTRACTOR|PROFESSIONAL|INTERNAL|RESTRICTED_IMAGERY"
}
```

## 5. State & truth rules
- `state ∈ {EXISTING, PROPOSED, COMPLETED}` is orthogonal to `truth_classification` (Phase 7):
  e.g. an EXISTING wall may be `MEASURED_EXISTING` or `ESTIMATED_EXISTING`; a PROPOSED wall is
  `PROPOSED_DESIGN` or `AI_SUGGESTED_DESIGN`; a COMPLETED wall becomes `COMPLETED_AS_BUILT` only
  after approved completion.
- `canonical_passport_ref` is set only for entities projected from Passport; Habitat-authored
  planning nodes have it null and can never be presented as canonical.

## 6. Ownership boundaries (who may write what)
| Field group | Writer |
|---|---|
| Canonical existing geometry, approved findings, `COMPLETED_AS_BUILT` | Passport/Core (via approved write-back) |
| Planning geometry, PROPOSED/AI design, homeowner edits, preferences | Habitat |
| Scan-derived existing model (pre-approval) | Habitat (labeled MEASURED/ESTIMATED, not canonical) |
Habitat surfaces canonical data **by reference/projection**; it never mutates it.

## 7. Consumption by each studio (proof of shared model)
- **Interior Studio** edits ROOM/SURFACE/OPENING/PRODUCT_INSTANCE/DESIGN_ELEMENT under LEVELs.
- **Exterior Studio** edits EXTERIOR_ELEVATION/ROOF_PLANE/SURFACE/OPENING/SITE_FEATURE under BUILDING.
- **Home Systems Studio** edits SYSTEM/EQUIPMENT/FIXTURE anchored to the same ROOM/LEVEL/BUILDING.
- **Living Digital Home** renders all of the above as layers (Phase 12).
- Because all four attach to one graph keyed by `property_id` + node `id`, an interior wall and the
  exterior elevation behind it reference the same building/level, enabling interior↔exterior
  registration (Phase 4) and whole-property transformation.

## 8. Relationship to existing code
- Extends (does not replace) `passport_projection` categories with spatial nodes.
- `design_scenarios` (façade) and `design_concepts` (kitchen) become DESIGN_ELEMENT collections
  attached to spatial nodes; `product_selections`/`design_products` become PRODUCT_INSTANCE sources
  (Phase 14). No rename is performed in this mission — mapping is documented only.
