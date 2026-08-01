"""Addition workflow endpoints for Exterior Design Studio."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .addition_workflow import (
    HouseSide,
    StructureKind,
    derive_structure_metrics,
    run_roof_phase,
    studio_entry_view,
    connect_points,
)

router = APIRouter(prefix="/habitat/exterior-studio", tags=["exterior-design-studio"])


class PointIn(BaseModel):
    x: float
    y: float


class OutlineBody(BaseModel):
    points: List[PointIn]
    close: bool = True


class StructureMetricsBody(BaseModel):
    points: List[PointIn]
    side: HouseSide = HouseSide.FREE
    structure_kind: StructureKind
    shared_wall_lf: Optional[float] = None


class RoofPhaseBody(BaseModel):
    points: List[PointIn]
    side: HouseSide = HouseSide.SOUTH
    existing_roof: Optional[Dict[str, Any]] = None
    preferred_strategy: Optional[str] = None


@router.get("/entry")
def entry_view():
    return studio_entry_view()


@router.post("/outline/connect")
def outline_connect(body: OutlineBody):
    pts = [p.model_dump() for p in body.points]
    return connect_points(pts, close=body.close)


@router.post("/outline/metrics")
def outline_metrics(body: StructureMetricsBody):
    pts = [p.model_dump() for p in body.points]
    result = derive_structure_metrics(
        pts, side=body.side, kind=body.structure_kind, shared_wall_lf=body.shared_wall_lf
    )
    if not result.get("ok"):
        raise HTTPException(400, result)
    return result


@router.post("/roof/evaluate")
def roof_evaluate(body: RoofPhaseBody):
    pts = [p.model_dump() for p in body.points]
    if len(pts) < 3:
        raise HTTPException(400, "Need at least 3 outline points for roof evaluation")
    return run_roof_phase(
        pts,
        side=body.side,
        existing_roof=body.existing_roof,
        preferred_strategy=body.preferred_strategy,
    )
