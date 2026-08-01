"""
Exterior Design Studio — addition outline, foundation, and phase workflow.
Studio canvas: finish layer + yards/driveways only (no framing/thermal layers).
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from .roof_attachment import (
    AdditionOutline,
    AttachmentStrategy,
    ExistingRoofContext,
    ExistingRoofForm,
    evaluate_roof_attachment,
)


class StudioCanvasMode(str, Enum):
    """What the 3D stage shows inside Exterior Design Studio."""
    FINISH_PLUS_GROUNDS = "finish_plus_grounds"  # default on entry
    # Landing page (not studio) owns: finish + thermal/moisture + framing


class StructureKind(str, Enum):
    ROOM_ADDITION = "room_addition"
    ATTACHED_GARAGE = "attached_garage"
    STANDALONE_GARAGE = "standalone_garage"
    CUSTOM_DECK = "custom_deck"
    COVERED_PATIO = "covered_patio"
    CUSTOM_PATIO = "custom_patio"
    INGROUND_POOL = "inground_pool"


class FoundationType(str, Enum):
    SLAB = "slab"
    CRAWLSPACE = "crawlspace"
    BASEMENT_WALLS = "basement_walls"
    PIER_BEAM = "pier_beam"  # decks
    GRADE_BEAM = "grade_beam"
    NONE_HARDSCAPE = "none_hardscape"  # patio / pool shell separate


class HouseSide(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    FREE = "free"  # detached in yard


ADD_OPTIONS = [
    {"id": StructureKind.ROOM_ADDITION.value, "label": "Room addition", "roofed": True, "attached": True},
    {"id": StructureKind.ATTACHED_GARAGE.value, "label": "Attached garage", "roofed": True, "attached": True},
    {"id": StructureKind.STANDALONE_GARAGE.value, "label": "Standalone garage", "roofed": True, "attached": False},
    {"id": StructureKind.CUSTOM_DECK.value, "label": "Custom deck", "roofed": False, "attached": True},
    {"id": StructureKind.COVERED_PATIO.value, "label": "Covered patio", "roofed": True, "attached": True},
    {"id": StructureKind.CUSTOM_PATIO.value, "label": "Custom patio", "roofed": False, "attached": False},
    {"id": StructureKind.INGROUND_POOL.value, "label": "In-ground pool", "roofed": False, "attached": False},
]


def studio_entry_view() -> Dict[str, Any]:
    return {
        "canvas_mode": StudioCanvasMode.FINISH_PLUS_GROUNDS.value,
        "show_layers": {
            "finish_exterior": True,
            "yards_front_back_sides": True,
            "driveways": True,
            "thermal_moisture_decking": False,
            "framing": False,
        },
        "note": (
            "Studio shows the house as seen from the street, sky, or backyard (finish only), "
            "plus yards and driveways. Framing and thermal/moisture layers stay on the Habitat landing page."
        ),
        "split_screen": {
            "primary": "3d_finish_plus_grounds",
            "secondary": "2d_top_down_plan",
        },
        "chrome": ["add", "remove"],
        "add_options": ADD_OPTIONS,
    }


def connect_points(points: List[Dict[str, float]], close: bool = True) -> Dict[str, Any]:
    """
    Homeowner plots corners; we connect sequentially and optionally close the polygon.
    points: [{x, y}, ...] in plan feet.
    """
    if len(points) < 2:
        return {"ok": False, "error": "Plot at least two points", "segments": [], "closed": False}

    pts = [(float(p["x"]), float(p["y"])) for p in points]
    segments = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        segments.append({
            "from": {"x": a[0], "y": a[1]},
            "to": {"x": b[0], "y": b[1]},
            "length_ft": round(math.hypot(b[0] - a[0], b[1] - a[1]), 2),
        })
    closed = False
    if close and len(pts) >= 3:
        a, b = pts[-1], pts[0]
        segments.append({
            "from": {"x": a[0], "y": a[1]},
            "to": {"x": b[0], "y": b[1]},
            "length_ft": round(math.hypot(b[0] - a[0], b[1] - a[1]), 2),
            "closing_edge": True,
        })
        closed = True

    outline = AdditionOutline(points=pts)
    perimeter = outline.perimeter_ft() if closed else sum(s["length_ft"] for s in segments)
    area = outline.area_sqft() if closed else 0.0

    return {
        "ok": True,
        "closed": closed,
        "points": [{"x": x, "y": y} for x, y in pts],
        "segments": segments,
        "perimeter_ft": round(perimeter, 2),
        "area_sqft": round(area, 2),
        "prompt_next": "Choose foundation type" if closed else "Plot at least 3 points and close the outline",
    }


def exterior_wall_lf(outline: AdditionOutline, shared_with_house_lf: float = 0.0) -> float:
    """New exterior wall = full perimeter minus shared attachment to existing house."""
    return max(outline.perimeter_ft() - max(shared_with_house_lf, 0.0), 0.0)


def foundation_options_for(kind: StructureKind) -> List[Dict[str, Any]]:
    if kind in (StructureKind.CUSTOM_DECK,):
        return [
            {"id": FoundationType.PIER_BEAM.value, "label": "Pier & beam (typical deck)", "recommended": True},
            {"id": FoundationType.SLAB.value, "label": "Concrete pad", "recommended": False},
        ]
    if kind in (StructureKind.CUSTOM_PATIO,):
        return [
            {"id": FoundationType.NONE_HARDSCAPE.value, "label": "Slab-on-grade patio", "recommended": True},
            {"id": FoundationType.SLAB.value, "label": "Structural slab", "recommended": False},
        ]
    if kind == StructureKind.INGROUND_POOL:
        return [
            {"id": FoundationType.NONE_HARDSCAPE.value, "label": "Pool shell / engineered excavation", "recommended": True},
        ]
    # Roofed living / garage
    return [
        {"id": FoundationType.SLAB.value, "label": "Slab-on-grade", "recommended": True},
        {"id": FoundationType.CRAWLSPACE.value, "label": "Crawlspace", "recommended": True},
        {"id": FoundationType.BASEMENT_WALLS.value, "label": "Basement walls", "recommended": False},
    ]


def derive_structure_metrics(
    points: List[Dict[str, float]],
    side: HouseSide,
    kind: StructureKind,
    shared_wall_lf: Optional[float] = None,
) -> Dict[str, Any]:
    connected = connect_points(points, close=True)
    if not connected.get("ok") or not connected.get("closed"):
        return connected

    pts = [(p["x"], p["y"]) for p in connected["points"]]
    outline = AdditionOutline(points=pts, attached_edge=side.value if side != HouseSide.FREE else None)

    # Estimate shared wall: longest edge if attached, else 0
    if shared_wall_lf is None:
        shared_wall_lf = 0.0
        if side != HouseSide.FREE and connected["segments"]:
            shared_wall_lf = max(s["length_ft"] for s in connected["segments"])

    wall_lf = exterior_wall_lf(outline, shared_wall_lf)
    return {
        **connected,
        "structure_kind": kind.value,
        "house_side": side.value,
        "foundation_perimeter_ft": connected["perimeter_ft"],
        "shared_with_existing_house_lf": round(shared_wall_lf, 2),
        "new_exterior_wall_lf": round(wall_lf, 2),
        "footprint_sqft": connected["area_sqft"],
        "foundation_options": foundation_options_for(kind),
        "needs_roof": next(o["roofed"] for o in ADD_OPTIONS if o["id"] == kind.value),
    }


def run_roof_phase(
    points: List[Dict[str, float]],
    side: HouseSide,
    existing_roof: Optional[Dict[str, Any]] = None,
    preferred_strategy: Optional[str] = None,
) -> Dict[str, Any]:
    pts = [(float(p["x"]), float(p["y"])) for p in points]
    outline = AdditionOutline(points=pts, attached_edge=side.value)
    er = existing_roof or {}
    ctx = ExistingRoofContext(
        form=ExistingRoofForm(er.get("form", "unknown")),
        primary_pitch_rise=float(er.get("pitch_rise", 6)),
        eave_height_ft=float(er.get("eave_height_ft", 9)),
        attachment_wall=side.value,
        wall_is_gable_end=bool(er.get("wall_is_gable_end", False)),
        wall_is_eave_side=bool(er.get("wall_is_eave_side", True)),
    )
    preferred = AttachmentStrategy(preferred_strategy) if preferred_strategy else None
    return evaluate_roof_attachment(ctx, outline, preferred=preferred)
