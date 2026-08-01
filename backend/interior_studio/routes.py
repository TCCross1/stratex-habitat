"""API routes — Interior Design Studio."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .lidar_scan import demo_kitchen_bath_scan, create_scan_session, ScanSource
from .catalog import catalog_tree, region_labor_rate
from .remodel_ops import (
    studio_entry,
    open_concept_proposal,
    kitchen_proposal,
    bath_proposal,
    room_refresh_proposal,
    ProjectKind,
)
from .estimator import estimate_proposal, estimate_selections

router = APIRouter(prefix="/habitat/interior-studio", tags=["interior-design-studio"])


class EstimateBody(BaseModel):
    selections: List[Dict[str, Any]]
    region: str = "US-KY"


class OpenConceptBody(BaseModel):
    wall_length_lf: float = Field(gt=0)
    is_bearing: bool = False
    beam_length_lf: Optional[float] = None
    region: str = "US-KY"


class KitchenBody(BaseModel):
    base_cab_lf: float = 18
    upper_cab_lf: float = 14
    island_lf: float = 8
    counter_sqft: float = 45
    cab_item: str = "cab_sc"
    counter_item: str = "quartz"
    floor_item: str = "lvp_prem"
    floor_sqft: float = 168
    region: str = "US-KY"


class BathBody(BaseModel):
    double_vanity: bool = True
    frameless_door: bool = True
    tile_wall_sqft: float = 120
    tile_floor_sqft: float = 40
    dual_showerheads: bool = True
    niche: bool = True
    bench: bool = True
    region: str = "US-KY"


@router.get("/entry")
def entry():
    return studio_entry()


@router.get("/catalog")
def catalog():
    return catalog_tree()


@router.get("/scan/demo")
def scan_demo(property_id: str = "demo-property"):
    return demo_kitchen_bath_scan(property_id)


@router.post("/scan/session")
def scan_session(property_id: str = "demo-property", source: str = "iphone_lidar"):
    try:
        src = ScanSource(source)
    except ValueError:
        src = ScanSource.IPHONE_LIDAR
    return create_scan_session(property_id=property_id, source=src)


@router.post("/estimate")
def estimate(body: EstimateBody):
    return estimate_selections(body.selections, region=body.region)


@router.post("/projects/open-concept")
def project_open_concept(body: OpenConceptBody):
    prop = open_concept_proposal(
        wall_length_lf=body.wall_length_lf,
        is_bearing=body.is_bearing,
        beam_length_lf=body.beam_length_lf,
    )
    return estimate_proposal(prop, region=body.region)


@router.post("/projects/kitchen")
def project_kitchen(body: KitchenBody):
    prop = kitchen_proposal(
        base_cab_lf=body.base_cab_lf,
        upper_cab_lf=body.upper_cab_lf,
        island_lf=body.island_lf,
        counter_sqft=body.counter_sqft,
        cab_item=body.cab_item,
        counter_item=body.counter_item,
        floor_item=body.floor_item,
        floor_sqft=body.floor_sqft,
    )
    return estimate_proposal(prop, region=body.region)


@router.post("/projects/bath")
def project_bath(body: BathBody):
    prop = bath_proposal(
        double_vanity=body.double_vanity,
        frameless_door=body.frameless_door,
        tile_wall_sqft=body.tile_wall_sqft,
        tile_floor_sqft=body.tile_floor_sqft,
        dual_showerheads=body.dual_showerheads,
        niche=body.niche,
        bench=body.bench,
    )
    return estimate_proposal(prop, region=body.region)


@router.get("/labor-rate")
def labor_rate(region: str = "US-KY"):
    return {"region": region, "rate_per_hr": region_labor_rate(region)}


class RoomRefreshBody(BaseModel):
    floor_sqft: float = 200
    wall_sqft: float = 450
    perimeter_lf: float = 60
    floor_item: str = "lvp_prem"
    paint: bool = True
    baseboard: bool = True
    doors: int = 1
    region: str = "US-KY"


@router.post("/projects/room-refresh")
def project_room_refresh(body: RoomRefreshBody):
    prop = room_refresh_proposal(
        floor_sqft=body.floor_sqft,
        wall_sqft=body.wall_sqft,
        perimeter_lf=body.perimeter_lf,
        floor_item=body.floor_item,
        paint=body.paint,
        baseboard=body.baseboard,
        doors=body.doors,
    )
    return estimate_proposal(prop, region=body.region)

