"""
Roof-to-existing attachment logic for Exterior Design Studio additions.

Expert framing rules distilled for homeowner-safe options:
- Validate whether a chosen join strategy can work given existing pitch/edge and addition outline
- Suggest alternatives or outline shape changes when geometry is hostile
- Never claims structural engineering stamp — planning guidance only
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ExistingRoofForm(str, Enum):
    GABLE = "gable"
    HIP = "hip"
    FLAT = "flat"
    SHED = "shed"
    MANSARD = "mansard"
    GAMBREL = "gambrel"
    UNKNOWN = "unknown"


class AttachmentStrategy(str, Enum):
    """How the new roof meets the existing roof / wall."""
    SAME_PITCH_CONTINUATION = "same_pitch_continuation"  # extend plane
    LOWER_LEAN_TO_SHED = "lower_lean_to_shed"  # shed against wall under eave
    VALLEY_INTO_EXISTING = "valley_into_existing"  # intersecting planes + valley
    HIP_RETURN = "hip_return"
    FLAT_OR_LOW_SLOPE = "flat_or_low_slope"
    CRICKET_AGAINST_WALL = "cricket_against_wall"
    MATCHING_GABLE_END = "matching_gable_end"  # addition continues ridge direction


class Feasibility(str, Enum):
    WORKS = "works"
    WORKS_WITH_CONDITIONS = "works_with_conditions"
    UNLIKELY = "unlikely"
    NOT_RECOMMENDED = "not_recommended"


@dataclass
class ExistingRoofContext:
    form: ExistingRoofForm = ExistingRoofForm.UNKNOWN
    primary_pitch_rise: float = 6.0  # rise in inches per 12 run
    primary_pitch_run: float = 12.0
    eave_height_ft: float = 9.0
    ridge_height_ft: Optional[float] = None
    attachment_wall: str = "unknown"  # north|south|east|west
    wall_is_gable_end: bool = False
    wall_is_eave_side: bool = True
    existing_overhang_ft: float = 1.0


@dataclass
class AdditionOutline:
    """Closed polygon in plan feet; points in order."""
    points: List[Tuple[float, float]]  # (x, y)
    attached_edge: Optional[str] = None

    def perimeter_ft(self) -> float:
        if len(self.points) < 2:
            return 0.0
        total = 0.0
        pts = self.points + [self.points[0]]
        for i in range(len(pts) - 1):
            dx = pts[i + 1][0] - pts[i][0]
            dy = pts[i + 1][1] - pts[i][1]
            total += math.hypot(dx, dy)
        return total

    def area_sqft(self) -> float:
        # Shoelace
        if len(self.points) < 3:
            return 0.0
        pts = self.points
        n = len(pts)
        a = 0.0
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            a += x1 * y2 - x2 * y1
        return abs(a) / 2.0

    def bbox(self) -> Tuple[float, float, float, float]:
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return min(xs), min(ys), max(xs), max(ys)

    def span_along_wall_ft(self) -> float:
        """Rough width of addition along attached wall."""
        if len(self.points) < 2:
            return 0.0
        minx, miny, maxx, maxy = self.bbox()
        w = maxx - minx
        d = maxy - miny
        # Prefer longer dimension as wall span if attached
        return max(w, d)

    def depth_from_wall_ft(self) -> float:
        minx, miny, maxx, maxy = self.bbox()
        w = maxx - minx
        d = maxy - miny
        return min(w, d) if min(w, d) > 0 else max(w, d)


@dataclass
class RoofOptionResult:
    strategy: AttachmentStrategy
    feasibility: Feasibility
    title: str
    homeowner_explanation: str
    conditions: List[str] = field(default_factory=list)
    suggested_pitch: Optional[str] = None  # e.g. "4/12"
    outline_suggestions: List[str] = field(default_factory=list)
    framing_notes: List[str] = field(default_factory=list)


def _pitch_label(rise: float, run: float = 12.0) -> str:
    return f"{int(round(rise))}/{int(run)}"


def evaluate_roof_attachment(
    existing: ExistingRoofContext,
    outline: AdditionOutline,
    preferred: Optional[AttachmentStrategy] = None,
) -> Dict[str, Any]:
    """
    Return ranked options for joining new roof to existing.
    """
    options: List[RoofOptionResult] = []
    depth = outline.depth_from_wall_ft()
    span = outline.span_along_wall_ft()
    area = outline.area_sqft()
    pitch = existing.primary_pitch_rise

    # 1) Same-pitch continuation (best when gable end or matching ridge direction)
    cont = RoofOptionResult(
        strategy=AttachmentStrategy.SAME_PITCH_CONTINUATION,
        feasibility=Feasibility.WORKS_WITH_CONDITIONS,
        title="Continue the same roof pitch",
        homeowner_explanation=(
            "The new roof keeps the same slope as your existing roof and reads as one continuous form."
        ),
        suggested_pitch=_pitch_label(pitch),
        framing_notes=[
            "New rafters or trusses match existing pitch",
            "Ridge alignment preferred when extending a gable",
            "Flashing at any unavoidable break in plane",
        ],
    )
    if existing.wall_is_gable_end or existing.form == ExistingRoofForm.GABLE:
        cont.feasibility = Feasibility.WORKS
        cont.conditions.append("Works best when the addition continues the main ridge direction.")
    elif existing.form == ExistingRoofForm.HIP:
        cont.feasibility = Feasibility.WORKS_WITH_CONDITIONS
        cont.conditions.append("Hip roofs rarely allow a pure plane continuation; expect new hips/valleys.")
        cont.outline_suggestions.append(
            "Square the addition so new hips can resolve cleanly to the existing hip."
        )
    elif existing.form == ExistingRoofForm.FLAT:
        cont.feasibility = Feasibility.UNLIKELY
        cont.homeowner_explanation = "Your existing roof is flat/low-slope; matching a steep continuation is not typical."
        cont.outline_suggestions.append("Use a low-slope or flat addition roof instead.")
    options.append(cont)

    # 2) Lean-to / shed against wall under eave
    shed = RoofOptionResult(
        strategy=AttachmentStrategy.LOWER_LEAN_TO_SHED,
        feasibility=Feasibility.WORKS,
        title="Lower shed (lean-to) roof against the house",
        homeowner_explanation=(
            "A single-slope roof starts lower than your main roof and ties into the wall or under the existing eave. "
            "Common for garages, porches, and modest additions."
        ),
        suggested_pitch=_pitch_label(min(pitch, 4.0) if pitch >= 4 else max(pitch, 3.0)),
        conditions=[
            "Ledger or wall connection below existing eave/roofline",
            "Keep slope ≥ about 3/12 for asphalt unless membrane specified",
        ],
        framing_notes=[
            "Shed rafters from outer wall/beam to house ledger",
            "Step flashing at wall; kickout at ends",
        ],
    )
    if depth > 24:
        shed.feasibility = Feasibility.WORKS_WITH_CONDITIONS
        shed.conditions.append("Deep sheds need intermediate beams or posts — budget for structure.")
        shed.outline_suggestions.append("Reduce depth or add posts/beam lines if the span is large.")
    if existing.form == ExistingRoofForm.FLAT:
        shed.suggested_pitch = "1/4:12 to 2/12 (membrane)"
    options.append(shed)

    # 3) Valley into existing (T or L intersection)
    valley = RoofOptionResult(
        strategy=AttachmentStrategy.VALLEY_INTO_EXISTING,
        feasibility=Feasibility.WORKS_WITH_CONDITIONS,
        title="Intersect with valleys (T or L addition)",
        homeowner_explanation=(
            "The new roof cuts into the existing roof with valleys. Flexible for side additions, "
            "but flashing and water management must be done carefully."
        ),
        suggested_pitch=_pitch_label(pitch),
        conditions=[
            "Valley metal and ice/water shield in cold climates",
            "Avoid valley discharge onto walls without gutters/kickouts",
        ],
        framing_notes=[
            "Valley rafters transfer load to supporting walls/beams",
            "May require sistering or opening existing roof plane",
        ],
    )
    if existing.form == ExistingRoofForm.FLAT:
        valley.feasibility = Feasibility.NOT_RECOMMENDED
        valley.homeowner_explanation = "Valleys into a flat roof are unusual; prefer continuous low-slope detailing."
    if span < 8:
        valley.outline_suggestions.append("Widen the addition along the wall so valleys have room to resolve.")
    options.append(valley)

    # 4) Matching gable end
    gable = RoofOptionResult(
        strategy=AttachmentStrategy.MATCHING_GABLE_END,
        feasibility=Feasibility.WORKS if existing.wall_is_gable_end else Feasibility.WORKS_WITH_CONDITIONS,
        title="Matching gable (mini gable on the addition)",
        homeowner_explanation=(
            "The addition gets its own gable end, often matching the main house style."
        ),
        suggested_pitch=_pitch_label(pitch),
        framing_notes=["Common rafters to a new ridge board or truss set"],
    )
    if not existing.wall_is_gable_end and existing.wall_is_eave_side:
        gable.conditions.append("On an eave wall this creates a cross-gable — expect valleys.")
    options.append(gable)

    # 5) Flat / low slope
    flat = RoofOptionResult(
        strategy=AttachmentStrategy.FLAT_OR_LOW_SLOPE,
        feasibility=Feasibility.WORKS,
        title="Flat or low-slope roof on the addition",
        homeowner_explanation=(
            "A nearly flat roof keeps the addition under existing windows and eave lines. "
            "Uses membrane systems rather than steep-slope shingles."
        ),
        suggested_pitch="1/4:12 to 2/12",
        conditions=["Membrane roofing", "Positive drainage away from house"],
        framing_notes=["Joist framing with slight slope to drains or scuppers"],
    )
    if pitch >= 8 and existing.wall_is_eave_side:
        flat.conditions.append("Steep main roofs often look best with a clearly lower flat/lean-to addition.")
    options.append(flat)

    # 6) Cricket if against tall wall / chimney-like condition (rare for full addition)
    cricket = RoofOptionResult(
        strategy=AttachmentStrategy.CRICKET_AGAINST_WALL,
        feasibility=Feasibility.WORKS_WITH_CONDITIONS,
        title="Cricket / saddle for drainage behind a tall wall",
        homeowner_explanation=(
            "A small peaked saddle diverts water around a wall penetration or high back wall."
        ),
        conditions=["Usually a detail, not the whole addition roof"],
        framing_notes=["Small framed saddle with metal flashing"],
    )
    options.append(cricket)

    # Rank: preferred first if feasible, then WORKS, WORKS_WITH_CONDITIONS, etc.
    order = {
        Feasibility.WORKS: 0,
        Feasibility.WORKS_WITH_CONDITIONS: 1,
        Feasibility.UNLIKELY: 2,
        Feasibility.NOT_RECOMMENDED: 3,
    }
    options.sort(key=lambda o: order[o.feasibility])
    if preferred:
        options.sort(key=lambda o: 0 if o.strategy == preferred else 1)

    # Global outline geometry warnings
    shape_advice: List[str] = []
    if area < 40 and depth > 0:
        shape_advice.append("Very small footprint — confirm this is intentional (e.g. mudroom vs full room).")
    if depth > 30:
        shape_advice.append(
            "Deep addition (over ~30 ft): roof spans and structure get expensive; "
            "consider a shallower depth or an L-shape."
        )
    # Non-rectangular detection (simple: more than 4 points)
    if len(outline.points) > 4:
        shape_advice.append(
            "Complex outline: roof planes will need multiple hips/valleys. "
            "A simpler rectangle is cheaper and easier to waterproof."
        )
        shape_advice.append(
            "If a roof option is struggling, try squaring two corners so the addition is rectangular against the house."
        )

    recommended = [o for o in options if o.feasibility in (Feasibility.WORKS, Feasibility.WORKS_WITH_CONDITIONS)]

    return {
        "existing": {
            "form": existing.form.value,
            "pitch": _pitch_label(existing.primary_pitch_rise),
            "attachment_wall": existing.attachment_wall,
            "wall_is_gable_end": existing.wall_is_gable_end,
            "wall_is_eave_side": existing.wall_is_eave_side,
        },
        "outline_metrics": {
            "perimeter_ft": round(outline.perimeter_ft(), 2),
            "area_sqft": round(outline.area_sqft(), 2),
            "span_along_wall_ft": round(span, 2),
            "depth_from_wall_ft": round(depth, 2),
            "point_count": len(outline.points),
        },
        "recommended_strategies": [o.strategy.value for o in recommended[:3]],
        "options": [
            {
                "strategy": o.strategy.value,
                "feasibility": o.feasibility.value,
                "title": o.title,
                "explanation": o.homeowner_explanation,
                "conditions": o.conditions,
                "suggested_pitch": o.suggested_pitch,
                "outline_suggestions": o.outline_suggestions,
                "framing_notes": o.framing_notes,
            }
            for o in options
        ],
        "shape_advice": shape_advice,
        "disclaimer": (
            "Roof guidance is planning logic for homeowners, not stamped structural engineering. "
            "Final framing must be designed/approved by a qualified professional and local code."
        ),
    }
