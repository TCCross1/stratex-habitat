# ROOM DNA & PROPERTY DNA ARCHITECTURE (Phase 8)

Version 1.0.0 · Specification only. Room DNA is a **Habitat + Passport projection concept**, not a
competing canonical database. It is a versioned, read-optimized **summary** assembled from the
shared spatial model (Phase 3) + Passport projections (H-013 boundary) + Habitat planning state.

---

## 1. Positioning (boundary)
- **Canonical truth** lives in Passport/Core. Room DNA **references** it (via `canonical_passport_ref`
  and projection envelopes) — it never becomes the source of truth.
- Room DNA is produced by the same projection adapter family as H-013 `passport_projection`
  (new category `room_dna`), so it inherits versioning, provenance, staleness, and fail-safe rules.
- Every field in Room DNA carries a truth classification (Phase 7) and confidence.

## 2. Room DNA contents (summary)
```jsonc
{
  "_projection": { "contract_version":"1.0.0","provider_mode":"…","authoritative":false,
                   "tenant_id":"…","property_id":"…","room_id":"spx-…","generated_at":"…","stale":false },
  "identity": { "name":"Living Room","level":"L1","zone":"Main","room_id":"spx-…" },
  "dimensions": { "area_m2": {"value":28.4,"class":"MEASURED_EXISTING","confidence":"MEDIUM"},
                  "ceiling_height_m": {"value":2.7,"class":"ESTIMATED_EXISTING","confidence":"LOW"} },
  "geometry_ref": "art-mesh-…",
  "openings": [ {"type":"WINDOW","class":"MEASURED_EXISTING"}, {"type":"DOOR","class":"MEASURED_EXISTING"} ],
  "finishes": [ {"surface":"FLOOR","material":"oak","class":"HOMEOWNER_REPORTED"} ],
  "fixtures": [ … ], "systems": [ {"type":"ELECTRICAL","detail":"UNKNOWN"} ],
  "materials": [ … ], "conditions": [ … ], "findings": [ {"ref":"PASSPORT-…","class":"VERIFIED_EXISTING"} ],
  "maintenance": [ … ], "products": [ {"product_instance_ref":"…"} ],
  "project_history": [ {"project_id":"…","state":"COMPLETED_AS_BUILT"} ],
  "design_alternatives": [ {"design_element_ref":"…","class":"PROPOSED_DESIGN"} ],
  "confidence": "MEDIUM",
  "unknowns": [ "Concealed wall systems", "Ceiling height (estimated)" ]
}
```
Room DNA summarizes: identity · dimensions · geometry · openings · finishes · fixtures · systems ·
materials · conditions · findings · maintenance · products · project history · design alternatives ·
confidence · unknowns.

## 3. Composition upward
```
ROOM_DNA → (aggregate) LEVEL_MODEL → (aggregate) BUILDING_MODEL → PROPERTY_DNA
```
- **Property DNA** is the property-level projection (extends the existing Steward
  `property_dna_projection` category) aggregating rooms, levels, buildings, exterior, systems, and
  site into a whole-property summary with rolled-up confidence and unknowns.

## 4. Contribution to products/experiences
| Consumer | Uses Room DNA for |
|---|---|
| Living Digital Home | Layer content + per-room drill-down |
| Interior/Exterior Design Studio | Existing baseline to edit against |
| Estimating | Quantities/takeoff with confidence & unknowns |
| Build Ready | Readiness inputs (what's known vs unknown) |
| Contractor packages | Redacted, scoped room summaries |
| Completed-project updates | Diff of proposed vs completed as-built |

## 5. Versioning, provenance, staleness
- Each Room DNA is versioned; regenerated when underlying scan/projection/design changes; carries
  `generated_at` + staleness (reuses `passport_projection` staleness).
- Provenance records which sources contributed (Passport refs, scan session, design elements).

## 6. Anti-duplication rules
- Room DNA does not persist a second copy of canonical geometry; it references artifact + canonical
  IDs. Habitat-authored planning fields are clearly Habitat-owned and `authoritative:false`.

## 7. Relationship to existing code
- Extends `passport_projection` (new `room_dna` category) and the existing
  `property_dna_projection`. Aggregates the shared spatial graph (Phase 3). No new canonical store.
