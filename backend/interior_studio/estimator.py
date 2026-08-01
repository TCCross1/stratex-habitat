"""
Real-time interior remodel estimator — demo + new work, materials, man-hours, regional labor.
Planning estimate only (not a bid).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .catalog import find_item, region_labor_rate


def estimate_selections(
    selections: List[Dict[str, Any]],
    *,
    region: str = "US-KY",
    waste_pct: float = 10.0,
    o_and_p_pct: float = 15.0,
    tax_pct: float = 6.0,
    demo_factor: float = 1.0,
) -> Dict[str, Any]:
    labor_rate = region_labor_rate(region)
    lines: List[Dict[str, Any]] = []
    mat_sub = 0.0
    labor_hrs = 0.0

    for sel in selections:
        item = find_item(sel["item_id"])
        if not item:
            lines.append(
                {
                    "item_id": sel["item_id"],
                    "error": "unknown_catalog_item",
                    "qty": sel.get("qty"),
                }
            )
            continue
        qty = float(sel.get("qty") or 0)
        mat = qty * float(item["material"])
        hrs = qty * float(item["labor_hrs_per_unit"]) * demo_factor
        # Structural demo items already encode demo labor
        line = {
            "item_id": item["id"],
            "label": item["label"],
            "category": item["category_label"],
            "qty": qty,
            "unit": item["unit"],
            "material_unit": item["material"],
            "material_ext": round(mat, 2),
            "labor_hours": round(hrs, 2),
            "labor_ext": round(hrs * labor_rate, 2),
            "tier": item.get("tier"),
            "quantity_basis": sel.get("quantity_basis", "ESTIMATED_QUANTITY"),
            "price_basis": "REGIONAL_PLANNING_PRICE",
            "note": sel.get("note"),
        }
        lines.append(line)
        mat_sub += mat
        labor_hrs += hrs

    waste = mat_sub * (waste_pct / 100.0)
    labor_sub = labor_hrs * labor_rate
    direct = mat_sub + waste + labor_sub
    o_and_p = direct * (o_and_p_pct / 100.0)
    pretax = direct + o_and_p
    tax = pretax * (tax_pct / 100.0)
    total = pretax + tax

    return {
        "region": region,
        "labor_rate_per_hr": labor_rate,
        "lines": lines,
        "summary": {
            "materials": round(mat_sub, 2),
            "waste": round(waste, 2),
            "labor_hours": round(labor_hrs, 2),
            "labor_cost": round(labor_sub, 2),
            "o_and_p": round(o_and_p, 2),
            "tax": round(tax, 2),
            "total_planning_estimate": round(total, 2),
            "low_range": round(total * 0.85, 2),
            "high_range": round(total * 1.25, 2),
        },
        "disclaimer": (
            "Planning estimate only — not a contractor bid. Ranges reflect typical "
            "variation in site conditions, hidden damage, and finish upgrades. "
            "Demo of unknown conditions may increase cost."
        ),
        "confidence": "MEDIUM",
        "truth": "ESTIMATED",
    }


def estimate_proposal(proposal: Dict[str, Any], region: str = "US-KY") -> Dict[str, Any]:
    est = estimate_selections(proposal.get("selections") or [], region=region)
    return {
        "proposal_id": proposal.get("id"),
        "kind": proposal.get("kind"),
        "label": proposal.get("label"),
        "warnings": proposal.get("warnings") or [],
        "estimate": est,
    }
