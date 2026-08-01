"""
Real-time / on-demand cost estimation for Exterior Design Studio.
Uses design geometry + catalog + regional labor bands.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .exterior_studio_catalog import LABOR_RATE_BANDS, get_sku
from .exterior_studio_models import (
    CostLine,
    CostSummary,
    DesignProposal,
    MaterialSelection,
    Placement,
    TruthClass,
)


def _structure_shell_costs(placement: Optional[Placement], project_type: str) -> List[CostLine]:
    if not placement:
        return []
    area = max(placement.width_ft, 0) * max(placement.depth_ft, 0)
    if area <= 0:
        return []

    # Rough shell allowances by project type ($/sqft bands)
    shell = {
        "room_addition": (120.0, 280.0),
        "attached_garage": (55.0, 120.0),
        "detached_garage": (50.0, 110.0),
        "detached_workshop": (45.0, 100.0),
        "exterior_refresh": (0.0, 0.0),
        "mixed": (80.0, 200.0),
    }
    low_u, high_u = shell.get(project_type, (80.0, 200.0))
    if low_u == 0 and high_u == 0:
        return []

    return [
        CostLine(
            label="Structure shell (framing, foundation allowance, basic enclosure)",
            category="materials",
            quantity=round(area, 1),
            unit="sqft",
            unit_cost_low=low_u * 0.55,
            unit_cost_high=high_u * 0.55,
            total_low=round(area * low_u * 0.55, 2),
            total_high=round(area * high_u * 0.55, 2),
            truth=TruthClass.PROJECTED,
            notes="Allowance band until engineered plans exist",
        ),
        CostLine(
            label="Structural & finish labor (shell)",
            category="labor",
            quantity=round(area, 1),
            unit="sqft",
            unit_cost_low=low_u * 0.45,
            unit_cost_high=high_u * 0.45,
            total_low=round(area * low_u * 0.45, 2),
            total_high=round(area * high_u * 0.45, 2),
            truth=TruthClass.PROJECTED,
        ),
    ]


def _material_lines(
    materials: List[MaterialSelection],
    placement: Optional[Placement],
) -> tuple[List[CostLine], float, float]:
    lines: List[CostLine] = []
    hours_low = 0.0
    hours_high = 0.0
    wall_area = 0.0
    roof_sq = 0.0
    if placement:
        # rough wall area: perimeter * 9 ft
        peri = 2 * (placement.width_ft + placement.depth_ft)
        wall_area = peri * 9.0
        roof_sq = (placement.width_ft * placement.depth_ft) / 100.0 * 1.15

    for sel in materials:
        sku = get_sku(sel.sku_id) if sel.sku_id else None
        if not sku:
            lines.append(
                CostLine(
                    label=sel.product_name or sel.material_class or sel.zone,
                    category="materials",
                    truth=TruthClass.UNKNOWN,
                    notes="Select a catalog product for priced estimate",
                )
            )
            continue

        qty = None
        unit = sku["unit"]
        if unit == "sqft":
            qty = wall_area if wall_area else None
        elif unit == "sq":
            qty = roof_sq if roof_sq else None
        elif unit == "lf":
            qty = 2 * (placement.width_ft + placement.depth_ft) if placement else None

        low_u = float(sku["cost_per_unit_low"])
        high_u = float(sku["cost_per_unit_high"])
        labor_h = float(sku.get("labor_hours_per_unit") or 0)

        total_low = round(qty * low_u, 2) if qty is not None else None
        total_high = round(qty * high_u, 2) if qty is not None else None
        if qty is not None:
            hours_low += qty * labor_h * 0.85
            hours_high += qty * labor_h * 1.15

        texture = sel.texture_profile or (sku.get("textures") or [None])[0]
        color = sel.color_name or ""
        lines.append(
            CostLine(
                label=f"{sku['label']}" + (f" — {color}" if color else "") + (f" ({texture})" if texture else ""),
                category="materials",
                quantity=round(qty, 2) if qty is not None else None,
                unit=unit,
                unit_cost_low=low_u,
                unit_cost_high=high_u,
                total_low=total_low,
                total_high=total_high,
                truth=TruthClass.ESTIMATED if qty is not None else TruthClass.SUGGESTED,
            )
        )
    return lines, hours_low, hours_high


def estimate_proposal(
    proposal: DesignProposal,
    region: str = "US-NATIONAL",
) -> CostSummary:
    rates = LABOR_RATE_BANDS.get(region) or LABOR_RATE_BANDS["US-NATIONAL"]
    lines: List[CostLine] = []
    lines.extend(_structure_shell_costs(proposal.placement, proposal.project_type.value))
    mat_lines, hours_low, hours_high = _material_lines(proposal.materials, proposal.placement)
    lines.extend(mat_lines)

    # Labor from material install hours
    if hours_high > 0:
        lines.append(
            CostLine(
                label="Installation labor (selected materials)",
                category="labor",
                quantity=round(hours_high, 1),
                unit="hours",
                unit_cost_low=rates["low"],
                unit_cost_high=rates["high"],
                total_low=round(hours_low * rates["low"], 2),
                total_high=round(hours_high * rates["high"], 2),
                truth=TruthClass.PROJECTED,
            )
        )

    mat_low = sum(l.total_low or 0 for l in lines if l.category == "materials")
    mat_high = sum(l.total_high or 0 for l in lines if l.category == "materials")
    lab_low = sum(l.total_low or 0 for l in lines if l.category == "labor")
    lab_high = sum(l.total_high or 0 for l in lines if l.category == "labor")

    return CostSummary(
        materials_low=round(mat_low, 2),
        materials_high=round(mat_high, 2),
        labor_low=round(lab_low, 2),
        labor_high=round(lab_high, 2),
        total_low=round(mat_low + lab_low, 2),
        total_high=round(mat_high + lab_high, 2),
        labor_hours_low=round(hours_low, 1) if hours_low else None,
        labor_hours_high=round(hours_high, 1) if hours_high else None,
        region=region,
        lines=lines,
    )
