"""
Exterior Design Studio API — Habitat
Design proposals only. Does not write Passport.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .exterior_studio_catalog import list_catalog
from .exterior_studio_models import (
    MaterialSelection,
    Placement,
    ProjectType,
    PropertyBuildContext,
    Vec2,
)
from .exterior_studio_service import (
    calculate_cost,
    create_proposal,
    get_proposal,
    options_payload,
    set_materials,
    set_placement,
)

router = APIRouter(prefix="/api/habitat/exterior-studio", tags=["exterior-design-studio"])


class CreateBody(BaseModel):
    property_id: str
    project_type: ProjectType
    title: str = "My exterior project"
    baseline_passport_version: Optional[str] = None
    tenant_id: Optional[str] = None


class PlacementBody(BaseModel):
    origin_x: float
    origin_y: float
    width_ft: float
    depth_ft: float
    height_ft: Optional[float] = None
    rotation_deg: float = 0.0
    attached_to_house: bool = False
    attachment_edge: Optional[str] = None
    override_codes: List[str] = Field(default_factory=list)
    # Approximate property context (from projection / capture)
    yard_area_sqft: Optional[float] = None
    house_footprint_sqft: Optional[float] = None
    apparent_lot_width_ft: Optional[float] = None
    apparent_lot_depth_ft: Optional[float] = None
    fence_detected: bool = False
    setback_suggest_ft: float = 5.0


class MaterialsBody(BaseModel):
    materials: List[MaterialSelection]


class CostBody(BaseModel):
    region: str = "US-NATIONAL"


@router.get("/options")
def get_options():
    """Catalog textures, roof systems, phases — for simple homeowner UI."""
    return options_payload()


@router.get("/catalog")
def catalog(zone: Optional[str] = None):
    return {"items": list_catalog(zone)}


@router.post("/proposals")
def create(body: CreateBody):
    p = create_proposal(
        property_id=body.property_id,
        project_type=body.project_type,
        title=body.title,
        baseline_passport_version=body.baseline_passport_version,
        tenant_id=body.tenant_id,
    )
    return p.model_dump()


@router.get("/proposals/{proposal_id}")
def read(proposal_id: str):
    p = get_proposal(proposal_id)
    if not p:
        raise HTTPException(404, "Proposal not found")
    return p.model_dump()


@router.post("/proposals/{proposal_id}/placement")
def placement(proposal_id: str, body: PlacementBody):
    if not get_proposal(proposal_id):
        raise HTTPException(404, "Proposal not found")
    pl = Placement(
        origin=Vec2(x=body.origin_x, y=body.origin_y),
        width_ft=body.width_ft,
        depth_ft=body.depth_ft,
        height_ft=body.height_ft,
        rotation_deg=body.rotation_deg,
        attached_to_house=body.attached_to_house,
        attachment_edge=body.attachment_edge,
    )
    ctx = PropertyBuildContext(
        property_id=get_proposal(proposal_id).property_id,
        yard_area_sqft=body.yard_area_sqft,
        house_footprint_sqft=body.house_footprint_sqft,
        apparent_lot_width_ft=body.apparent_lot_width_ft,
        apparent_lot_depth_ft=body.apparent_lot_depth_ft,
        fence_detected=body.fence_detected,
        setback_suggest_ft=body.setback_suggest_ft,
    )
    p = set_placement(proposal_id, pl, ctx, override_codes=body.override_codes)
    return p.model_dump()


@router.post("/proposals/{proposal_id}/materials")
def materials(proposal_id: str, body: MaterialsBody):
    if not get_proposal(proposal_id):
        raise HTTPException(404, "Proposal not found")
    p = set_materials(proposal_id, body.materials)
    return p.model_dump()


@router.post("/proposals/{proposal_id}/calculate-cost")
def cost(proposal_id: str, body: CostBody = CostBody()):
    if not get_proposal(proposal_id):
        raise HTTPException(404, "Proposal not found")
    p = calculate_cost(proposal_id, region=body.region)
    return p.model_dump()
