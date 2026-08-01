"""
Exterior Design Studio service — create/update proposals, place, materials, cost.
Never writes Passport.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .exterior_studio_boundary import evaluate_placement
from .exterior_studio_catalog import SIDING_TEXTURES, ROOF_SYSTEMS, list_catalog
from .exterior_studio_estimator import estimate_proposal
from .exterior_studio_models import (
    DesignProposal,
    MaterialSelection,
    Placement,
    ProjectType,
    PropertyBuildContext,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# In-memory store for field-test; swap for durable store in production
_PROPOSALS: Dict[str, DesignProposal] = {}


def create_proposal(
    property_id: str,
    project_type: ProjectType,
    title: str = "My exterior project",
    baseline_passport_version: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> DesignProposal:
    p = DesignProposal(
        property_id=property_id,
        project_type=project_type,
        title=title,
        baseline_passport_version=baseline_passport_version,
        tenant_id=tenant_id,
        phase="intent",
    )
    _PROPOSALS[p.proposal_id] = p
    return p


def get_proposal(proposal_id: str) -> Optional[DesignProposal]:
    return _PROPOSALS.get(proposal_id)


def set_placement(
    proposal_id: str,
    placement: Placement,
    ctx: PropertyBuildContext,
    override_codes: Optional[List[str]] = None,
) -> DesignProposal:
    p = _PROPOSALS[proposal_id]
    warnings = evaluate_placement(placement, ctx)
    override_codes = override_codes or []
    for code in override_codes:
        p.overrides.append({"code": code, "at": _now()})
    # Filter pure NONE for storage clarity if overrides applied
    p.placement = placement
    p.warnings = warnings
    p.phase = "size_place"
    p.updated_at = _now()
    _PROPOSALS[proposal_id] = p
    return p


def set_materials(proposal_id: str, materials: List[MaterialSelection]) -> DesignProposal:
    p = _PROPOSALS[proposal_id]
    p.materials = materials
    p.phase = "materials"
    p.updated_at = _now()
    _PROPOSALS[proposal_id] = p
    return p


def calculate_cost(proposal_id: str, region: str = "US-NATIONAL") -> DesignProposal:
    p = _PROPOSALS[proposal_id]
    p.cost = estimate_proposal(p, region=region)
    p.phase = "cost"
    p.updated_at = _now()
    _PROPOSALS[proposal_id] = p
    return p


def options_payload() -> Dict[str, Any]:
    return {
        "project_types": [e.value for e in ProjectType],
        "siding_textures": SIDING_TEXTURES,
        "roof_systems": ROOF_SYSTEMS,
        "catalog_zones": [
            "siding_main",
            "siding_accent",
            "roof_main",
            "trim",
            "garage_door",
        ],
        "workflow_phases": ["intent", "size_place", "materials", "cost", "review"],
        "ux_principles": {
            "as_built_twin_location": "habitat_landing_page",
            "studio_role": "design_customize_only",
            "boundary_policy": "soft_warn_with_override",
            "cost_policy": "range_with_truth_classes",
            "devices": ["desktop", "tablet", "phone"],
        },
    }
