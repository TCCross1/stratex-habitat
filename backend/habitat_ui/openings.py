"""
Exterior openings (windows & doors) for Habitat twin + reports.
Rough opening and unit measurements with truth classification.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class OpeningKind(str, Enum):
    WINDOW = "window"
    DOOR = "door"
    SLIDING_DOOR = "sliding_door"
    GARAGE_DOOR = "garage_door"
    OTHER = "other"


class TruthClass(str, Enum):
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    PROJECTED = "PROJECTED"
    UNKNOWN = "UNKNOWN"


class Elevation(str, Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    UNKNOWN = "unknown"


def rough_opening_from_unit(
    unit_width_in: float,
    unit_height_in: float,
    kind: OpeningKind,
) -> Dict[str, float]:
    """
    Standard rough-opening allowances (inches) — planning guidance, not stamped framing.
    Windows: typically +2" width, +2.5" height (shims + sill).
    Doors: typically +2" width, +2.5" height.
    """
    if kind in (OpeningKind.DOOR, OpeningKind.SLIDING_DOOR):
        return {
            "width_in": round(unit_width_in + 2.0, 2),
            "height_in": round(unit_height_in + 2.5, 2),
        }
    if kind == OpeningKind.GARAGE_DOOR:
        return {
            "width_in": round(unit_width_in + 3.0, 2),
            "height_in": round(unit_height_in + 3.0, 2),
        }
    # window default
    return {
        "width_in": round(unit_width_in + 2.0, 2),
        "height_in": round(unit_height_in + 2.5, 2),
    }


def opening_record(
    *,
    kind: OpeningKind,
    label: str,
    elevation: Elevation,
    unit_width_in: float,
    unit_height_in: float,
    material: str = "unknown",
    condition: str = "unknown",
    truth: TruthClass = TruthClass.ESTIMATED,
    twin_hotspot_id: Optional[str] = None,
    notes: str = "",
) -> Dict[str, Any]:
    ro = rough_opening_from_unit(unit_width_in, unit_height_in, kind)
    return {
        "id": str(uuid4()),
        "kind": kind.value,
        "label": label,
        "elevation": elevation.value,
        "unit_size_in": {"width": unit_width_in, "height": unit_height_in},
        "rough_opening_in": ro,
        "rough_opening_display": f"{ro['width_in']}\" × {ro['height_in']}\"",
        "unit_display": f"{unit_width_in}\" × {unit_height_in}\"",
        "material": material,
        "condition": condition,
        "truth": truth.value,
        "twin_hotspot_id": twin_hotspot_id,
        "notes": notes,
        "disclaimer": (
            "Rough openings are standard planning allowances from measured/estimated unit size. "
            "Field verification required before ordering or framing."
        ),
    }


def demo_openings_for_property() -> List[Dict[str, Any]]:
    """Sample set matching a typical suburban elevation for field-test UI."""
    return [
        opening_record(
            kind=OpeningKind.WINDOW,
            label="Front — Living Room Picture",
            elevation=Elevation.FRONT,
            unit_width_in=72,
            unit_height_in=48,
            material="vinyl",
            condition="fair",
            truth=TruthClass.ESTIMATED,
        ),
        opening_record(
            kind=OpeningKind.WINDOW,
            label="Front — Bedroom Left",
            elevation=Elevation.FRONT,
            unit_width_in=36,
            unit_height_in=48,
            material="vinyl",
            condition="good",
            truth=TruthClass.ESTIMATED,
        ),
        opening_record(
            kind=OpeningKind.DOOR,
            label="Front Entry",
            elevation=Elevation.FRONT,
            unit_width_in=36,
            unit_height_in=80,
            material="fiberglass",
            condition="good",
            truth=TruthClass.ESTIMATED,
        ),
        opening_record(
            kind=OpeningKind.GARAGE_DOOR,
            label="Garage — Double",
            elevation=Elevation.FRONT,
            unit_width_in=192,
            unit_height_in=84,
            material="steel",
            condition="fair",
            truth=TruthClass.ESTIMATED,
        ),
        opening_record(
            kind=OpeningKind.SLIDING_DOOR,
            label="Rear — Patio Slider",
            elevation=Elevation.BACK,
            unit_width_in=72,
            unit_height_in=80,
            material="vinyl",
            condition="good",
            truth=TruthClass.ESTIMATED,
        ),
    ]
