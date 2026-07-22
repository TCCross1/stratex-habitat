# REALITY STUDIO ESTIMATING & COST CONFIDENCE (Phase 15)

Version 1.0.0 · Specification only. Estimates update in real time as design/products/geometry
change, and **always** expose quantity basis, price source, and confidence. Estimates are planning
figures — never contractor bids or guaranteed prices.

---

## 1. Quantity basis (must distinguish)
`VERIFIED_QUANTITY` (Core-verified) · `MEASURED_QUANTITY` (good-fit scan) · `ESTIMATED_QUANTITY`
(gap-filled) · `ALLOWANCE` (planning assumption where geometry is unknown). Each line states which.

## 2. Price basis (must distinguish)
`PRODUCT_SPECIFIC_PRICE` · `REGIONAL_PLANNING_PRICE` · `CONTRACTOR_PRICE` · `SUPPLIER_PRICE`.
Plus: `LABOR_ASSUMPTION`, `WASTE_ASSUMPTION`, `O_AND_P_CONFIG`, `TAX`, `PERMIT_ALLOWANCE`,
`UNKNOWN_COST` (explicit line for undetermined scope), `PROFESSIONAL_REVIEW_REQUIRED` flag.

## 3. Estimate line (illustrative)
```jsonc
{
  "line_id":"…","description":"LVP flooring — living room",
  "quantity":{"value":28.4,"unit":"sqft","basis":"MEASURED_QUANTITY","confidence":"MEDIUM"},
  "unit_price":{"value":4.20,"currency":"USD","basis":"REGIONAL_PLANNING_PRICE",
                "source":"pricebook@2.3.0","date":"2026-06-01","region":"US-XX","confidence":"MEDIUM"},
  "labor":{"basis":"LABOR_ASSUMPTION","confidence":"LOW"},
  "waste_pct":10,"o_and_p_pct":15,"tax_pct":7,"permit_allowance":250,
  "assumptions":["Subfloor sound (unverified)"],"exclusions":["Subfloor repair"],
  "unknown_costs":["Concealed damage behind baseboards"],
  "professional_review_required":false,
  "line_confidence":"MEDIUM"
}
```

## 4. Mandatory metadata (every cost)
Source · version · date · region · confidence · assumptions · exclusions · refresh requirement.
A **refresh requirement** marks prices past a freshness window as `STALE` and prompts re-pricing.

## 5. Real-time behavior
- Any change (product, material, geometry, quantity, region) triggers a governed recompute; the
  estimate returns updated totals + a per-line + roll-up confidence + a plain-language summary
  (progressive disclosure reveals line detail/provenance).
- Roll-up confidence is the conservative aggregate (a single `LOW`/`UNKNOWN` driver caps optimism).

## 6. Honesty & boundaries
- Labeled "planning estimate", not a bid. Where scope is unknown, an explicit `UNKNOWN_COST` line is
  shown rather than a fabricated number. Items needing pro review are flagged and can block
  Build-Ready (Phase 16 / readiness policy).

## 7. Relationship to existing code
- Extends `pricebook` (versioned, provenance, `authoritative:false`) and the Steward estimate
  endpoint; aligns with `project_assumptions`. No implementation in this mission.
