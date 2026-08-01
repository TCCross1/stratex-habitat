"""
Soft boundary / placement checks for Exterior Design Studio.
Warnings only — homeowner may override.
"""

from __future__ import annotations

from typing import List

from .exterior_studio_models import (
    BoundaryWarning,
    Placement,
    PlacementWarningLevel,
    PropertyBuildContext,
)


def evaluate_placement(
    placement: Placement,
    ctx: PropertyBuildContext,
) -> List[BoundaryWarning]:
    warnings: List[BoundaryWarning] = []
    footprint = max(placement.width_ft, 0) * max(placement.depth_ft, 0)

    # Oversized relative to yard
    if ctx.yard_area_sqft and footprint > 0:
        ratio = footprint / max(ctx.yard_area_sqft, 1.0)
        if ratio > 0.45:
            warnings.append(
                BoundaryWarning(
                    level=PlacementWarningLevel.WARNING,
                    code="FOOTPRINT_LARGE_VS_YARD",
                    message=(
                        f"This structure (~{int(footprint)} sq ft) uses a large share of the "
                        f"visible yard (~{int(ctx.yard_area_sqft)} sq ft). You can continue, "
                        "but confirm clearance, access, and local rules."
                    ),
                )
            )
        elif ratio > 0.25:
            warnings.append(
                BoundaryWarning(
                    level=PlacementWarningLevel.INFO,
                    code="FOOTPRINT_NOTABLE_VS_YARD",
                    message="This is a sizable structure relative to the visible yard area.",
                )
            )

    # Near edge heuristic using setback suggestion + origin magnitude
    # (Simplified: if origin is far from house center beyond half-lot, warn)
    if ctx.apparent_lot_width_ft and abs(placement.origin.x) > (
        ctx.apparent_lot_width_ft / 2 - ctx.setback_suggest_ft
    ):
        warnings.append(
            BoundaryWarning(
                level=PlacementWarningLevel.WARNING,
                code="NEAR_APPARENT_SIDE_BOUNDARY",
                message=(
                    "Placement may be close to an apparent side property edge. "
                    "Boundaries from drone imagery are approximate — verify before building."
                ),
            )
        )

    if ctx.apparent_lot_depth_ft and abs(placement.origin.y) > (
        ctx.apparent_lot_depth_ft / 2 - ctx.setback_suggest_ft
    ):
        warnings.append(
            BoundaryWarning(
                level=PlacementWarningLevel.WARNING,
                code="NEAR_APPARENT_REAR_OR_FRONT_BOUNDARY",
                message=(
                    "Placement may be close to an apparent front or rear property edge. "
                    "Confirm setbacks with local code and a survey if needed."
                ),
            )
        )

    # Attached structures: encourage attachment edge
    if placement.attached_to_house and not placement.attachment_edge:
        warnings.append(
            BoundaryWarning(
                level=PlacementWarningLevel.INFO,
                code="ATTACHMENT_EDGE_UNSPECIFIED",
                message="Choose which side of the house this attaches to for a clearer design.",
            )
        )

    # Extremely small / large dimensions
    if placement.width_ft < 6 or placement.depth_ft < 6:
        warnings.append(
            BoundaryWarning(
                level=PlacementWarningLevel.INFO,
                code="VERY_SMALL_STRUCTURE",
                message="This is smaller than a typical room or garage bay. Intentional?",
            )
        )
    if placement.width_ft > 40 or placement.depth_ft > 40:
        warnings.append(
            BoundaryWarning(
                level=PlacementWarningLevel.WARNING,
                code="VERY_LARGE_STRUCTURE",
                message=(
                    "This is larger than a typical residential garage or room addition. "
                    "You can override and continue."
                ),
            )
        )

    if not warnings:
        warnings.append(
            BoundaryWarning(
                level=PlacementWarningLevel.NONE,
                code="NO_ISSUE_DETECTED",
                message="No placement issues detected from approximate property context.",
                overridable=True,
            )
        )
    return warnings
