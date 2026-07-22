# PRODUCT GRAPH & MATERIAL SELECTION (Phase 14)

Version 1.0.0 · Specification only. Defines the governed product-selection hierarchy and how a
homeowner "point-and-change" selection propagates through appearance, quantities, estimate,
warranty, contractor package, and readiness.

---

## 1. Selection hierarchy (priority order)
1. **Job-specific contractor selections** (highest authority for a real job)
2. Contractor **preferred-material catalog**
3. Contractor **supplier relationships & pricing**
4. **Property/homeowner requirements** (constraints, preferences)
5. **Regional supplier & material-yard catalog**
6. **Big-box vendor catalog**
7. **Governed regional planning allowance** (lowest; fallback when nothing specific is chosen)

Resolution walks top→down; the first level with an authoritative match wins, and the chosen level is
recorded as the price/selection **source** with its confidence.

## 2. Product selection record (illustrative)
```jsonc
{
  "product_instance_ref": "spx-…",      // attaches to a spatial node (Phase 3)
  "manufacturer": "…", "product_line": "…", "sku": "…|UNKNOWN",
  "supplier": "…", "pricing_source": "CONTRACTOR|SUPPLIER|REGIONAL|BIG_BOX|PLANNING_ALLOWANCE",
  "price": { "value": 4.20, "unit":"sqft","currency":"USD","date":"2026-06-01","region":"…",
             "class":"ESTIMATED", "confidence":"MEDIUM" },
  "availability_state": "IN_STOCK|LEAD_TIME|BACKORDER|UNKNOWN",
  "warranty": { "term":"…","source":"MANUFACTURER" },
  "compatibility": "VERIFIED_FIT|LIKELY_COMPATIBLE|REQUIRES_FIELD_VERIFICATION|CONCEPT_VISUALIZATION_ONLY",
  "contractor_preference": true,
  "selection_vs_allowance": "ACTUAL_SELECTION|ALLOWANCE",
  "substitution_rules": ["equivalent-grade-or-better","match-color-family"],
  "truth_classification": "PROPOSED_DESIGN",
  "provenance": {"selected_by":"homeowner","at":"…"}, "audit_refs":["evt-…"]
}
```
Every selection identifies: manufacturer · product line · SKU (when known) · supplier · pricing
source · price date · availability · warranty · compatibility · contractor preference · actual vs
allowance · substitution rules. Missing data ⇒ `UNKNOWN`, never fabricated.

## 3. Point-and-change propagation
A selection/change updates, in one governed transaction:
1. **3D appearance** — swap material/product on the PRODUCT_INSTANCE / SURFACE.
2. **Product graph** — record selection + source + provenance.
3. **Quantity takeoff** — recompute quantities from the spatial model (labeled by tolerance).
4. **Estimate** — recompute cost + confidence + assumptions (Phase 15).
5. **Warranty info** — attach product warranty.
6. **Contractor package** — mark package stale / regenerate on next gate.
7. **Project readiness** — re-run readiness (allowance vs actual selection affects Build-Ready).

## 4. Allowance vs actual selection
- An **allowance** (governed regional planning number) is clearly labeled and lower-confidence; an
  **actual selection** (real SKU/supplier/contractor) raises confidence. Contractor package flags
  any remaining allowances as items requiring confirmation.

## 5. Governance & anti-fabrication
- The **governed regional planning allowance** extends the existing `pricebook` (versioned,
  `authoritative:false`, provenance-stamped). No price appears without source + date + region +
  confidence. No invented SKUs.

## 6. Relationship to existing code
- Generalizes `design_products` / `product_selections` / `design.py` product library into the
  Product Graph; reuses `pricebook` for allowances and the projects compatibility vocabulary. No
  implementation in this mission.
