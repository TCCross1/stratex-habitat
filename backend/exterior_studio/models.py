"""
Exterior Design Studio — data models
Design proposals are non-canonical. As-built twin remains Passport-only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectType(str, Enum):
    EXTERIOR_REFRESH = "exterior_refresh"
    ROOM_ADDITION = "room_addition"
    ATTACHED_GARAGE = "attached_garage"
    DETACHED_GARAGE = "detached_garage"
    DETACHED_WORKSHOP = "detached_workshop"
    MIXED = "mixed"


class TruthClass(str, Enum):
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    PROJECTED = "PROJECTED"
    SUGGESTED = "SUGGESTED"
    UNKNOWN = "UNKNOWN"


class PlacementWarningLevel(str, Enum):
    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    CRITICAL_SUGGEST = "critical_suggest"  # still overridable


class Vec2(BaseModel):
    x: float
    y: float


class Placement(BaseModel):
    """Placement on property plan (local meters, origin at house centroid or survey approx)."""
    origin: Vec2
    width_ft: float
    depth_ft: float
    height_ft: Optional[float] = None
    rotation_deg: float = 0.0
    attached_to_house: bool = False
    attachment_edge: Optional[str] = None  # north|south|east|west


class MaterialSelection(BaseModel):
    zone: str  # e.g. siding_main, roof_main, trim, garage_door
    sku_id: Optional[str] = None
    material_class: str
    product_name: Optional[str] = None
    color_name: Optional[str] = None
    hex_value: Optional[str] = None
    texture_profile: Optional[str] = None  # cedar_grain|smooth|wood_lap|board_batten|...
    options: Dict[str, Any] = Field(default_factory=dict)


class CostLine(BaseModel):
    label: str
    category: str  # materials|labor|equipment|allowance
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_cost_low: Optional[float] = None
    unit_cost_high: Optional[float] = None
    total_low: Optional[float] = None
    total_high: Optional[float] = None
    truth: TruthClass = TruthClass.ESTIMATED
    notes: Optional[str] = None


class CostSummary(BaseModel):
    materials_low: float = 0.0
    materials_high: float = 0.0
    labor_low: float = 0.0
    labor_high: float = 0.0
    total_low: float = 0.0
    total_high: float = 0.0
    labor_hours_low: Optional[float] = None
    labor_hours_high: Optional[float] = None
    region: Optional[str] = None
    calculated_at: str = Field(default_factory=_now)
    lines: List[CostLine] = Field(default_factory=list)
    confidence_note: str = (
        "Ranges are planning estimates. Not a contractor bid. "
        "Final price requires local quotes and permits."
    )


class BoundaryWarning(BaseModel):
    level: PlacementWarningLevel
    code: str
    message: str
    overridable: bool = True


class DesignProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: Optional[str] = None
    property_id: str
    project_type: ProjectType
    title: str = "My exterior project"
    phase: str = "intent"  # intent|size_place|materials|cost|review
    baseline_passport_version: Optional[str] = None
    placement: Optional[Placement] = None
    materials: List[MaterialSelection] = Field(default_factory=list)
    cost: Optional[CostSummary] = None
    warnings: List[BoundaryWarning] = Field(default_factory=list)
    overrides: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)
    authority: Dict[str, str] = Field(
        default_factory=lambda: {
            "as_built_source": "passport_projection",
            "design_status": "non_canonical_proposal",
            "habitat_role": "design_only_never_writes_passport",
        }
    )


class PropertyBuildContext(BaseModel):
    """Approximate context from capture — not a legal survey."""
    property_id: str
    house_footprint_sqft: Optional[float] = None
    yard_area_sqft: Optional[float] = None
    apparent_lot_width_ft: Optional[float] = None
    apparent_lot_depth_ft: Optional[float] = None
    fence_detected: bool = False
    buildable_polygon: Optional[List[Vec2]] = None  # simplified
    setback_suggest_ft: float = 5.0
    context_truth: TruthClass = TruthClass.ESTIMATED
    disclaimer: str = (
        "Property edges and setbacks are approximate from aerial capture. "
        "Not a boundary survey. Confirm with survey, HOA, and local code before building."
    )
