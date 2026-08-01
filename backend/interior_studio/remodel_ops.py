"""
Remodel operations — proposed design only (never merges into as-built silently).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class ProjectKind(str, Enum):
    KITCHEN = "kitchen_remodel"
    BATH = "bath_remodel"
    OPEN_CONCEPT = "open_concept"
    ROOM_REFRESH = "room_refresh"
    WHOLE_FLOOR = "whole_floor_finishes"


PROJECT_OPTIONS = [
    {
        "id": ProjectKind.KITCHEN.value,
        "label": "Kitchen remodel",
        "blurb": "Cabinets, counters, island, appliances, lighting — walk the new kitchen before you buy.",
    },
    {
        "id": ProjectKind.BATH.value,
        "label": "Bathroom remodel",
        "blurb": "Vanity, shower, tile height, doors, fixtures — design every finish simply.",
    },
    {
        "id": ProjectKind.OPEN_CONCEPT.value,
        "label": "Open concept (remove wall)",
        "blurb": "Remove a wall, size an LVL if needed, see the combined space in 3D.",
    },
    {
        "id": ProjectKind.ROOM_REFRESH.value,
        "label": "Room refresh",
        "blurb": "Flooring, paint, trim, doors — one room at a time.",
    },
    {
        "id": ProjectKind.WHOLE_FLOOR.value,
        "label": "Whole-floor finishes",
        "blurb": "Consistent flooring and paint across connected rooms.",
    },
]


def studio_entry() -> Dict[str, Any]:
    return {
        "title": "Interior Design Studio",
        "promise": "Scan it. Walk it. Redesign it. Price it.",
        "steps": [
            {"id": "scan", "label": "Scan / floor plan"},
            {"id": "project", "label": "Choose project"},
            {"id": "design", "label": "Pick finishes & products"},
            {"id": "estimate", "label": "Live estimate"},
            {"id": "walkthrough", "label": "3D walkthrough"},
        ],
        "project_options": PROJECT_OPTIONS,
        "truth_policy": (
            "LiDAR floor plans are HOMEOWNER_REPORTED. Design changes are PROPOSED_DESIGN. "
            "Estimates are planning figures — not contractor bids."
        ),
        "as_built_rule": "Existing scanned geometry stays intact; proposals toggle on a separate layer.",
    }


def open_concept_proposal(
    *,
    wall_length_lf: float,
    is_bearing: bool,
    beam_length_lf: Optional[float] = None,
) -> Dict[str, Any]:
    beam_lf = beam_length_lf if beam_length_lf is not None else wall_length_lf + 1.0
    selections = [
        {"item_id": "demo_bearing" if is_bearing else "demo_wall", "qty": wall_length_lf},
    ]
    if is_bearing:
        selections.extend(
            [
                {"item_id": "lvl_beam", "qty": beam_lf},
                {"item_id": "post_jack", "qty": 2},
                {"item_id": "eng_letter", "qty": 1},
            ]
        )
    return {
        "id": str(uuid4()),
        "kind": ProjectKind.OPEN_CONCEPT.value,
        "label": "Open concept wall removal",
        "is_bearing": is_bearing,
        "wall_length_lf": wall_length_lf,
        "beam_length_lf": beam_lf if is_bearing else None,
        "selections": selections,
        "warnings": (
            [
                "Bearing wall removal requires structural engineering and permits.",
                "Temporary shoring required during construction.",
            ]
            if is_bearing
            else ["Confirm wall is non-bearing before demo."]
        ),
        "truth": "PROPOSED_DESIGN",
    }


def kitchen_proposal(
    *,
    base_cab_lf: float = 18,
    upper_cab_lf: float = 14,
    island_lf: float = 8,
    counter_sqft: float = 45,
    cab_item: str = "cab_sc",
    counter_item: str = "quartz",
    floor_item: str = "lvp_prem",
    floor_sqft: float = 168,
) -> Dict[str, Any]:
    return {
        "id": str(uuid4()),
        "kind": ProjectKind.KITCHEN.value,
        "label": "Kitchen remodel",
        "selections": [
            {"item_id": cab_item, "qty": base_cab_lf + upper_cab_lf, "note": "base + upper LF"},
            {"item_id": "island_base", "qty": island_lf},
            {"item_id": counter_item, "qty": counter_sqft},
            {"item_id": floor_item, "qty": floor_sqft},
            {"item_id": "hw_pull", "qty": int((base_cab_lf + upper_cab_lf) * 1.2)},
            {"item_id": "under_cab", "qty": upper_cab_lf},
            {"item_id": "pendant", "qty": 3},
            {"item_id": "recessed", "qty": 6},
            {"item_id": "paint_walls", "qty": 400},
        ],
        "truth": "PROPOSED_DESIGN",
    }


def bath_proposal(
    *,
    double_vanity: bool = True,
    frameless_door: bool = True,
    tile_wall_sqft: float = 120,
    tile_floor_sqft: float = 40,
    dual_showerheads: bool = True,
    niche: bool = True,
    bench: bool = True,
) -> Dict[str, Any]:
    selections = [
        {"item_id": "van_double" if double_vanity else "van_single", "qty": 1},
        {"item_id": "toilet_std", "qty": 1},
        {"item_id": "shower_tile", "qty": tile_wall_sqft},
        {"item_id": "tile_porc", "qty": tile_floor_sqft},
        {"item_id": "door_frameLESS" if frameless_door else "door_frame", "qty": 1},
        {"item_id": "head_rain" if dual_showerheads else "head_std", "qty": 1},
        {"item_id": "mirror_std", "qty": 2 if double_vanity else 1},
        {"item_id": "towel_bar", "qty": 2},
        {"item_id": "paint_walls", "qty": 180},
    ]
    if niche:
        selections.append({"item_id": "shower_niche", "qty": 1})
    if bench:
        selections.append({"item_id": "shower_bench", "qty": 1})
    return {
        "id": str(uuid4()),
        "kind": ProjectKind.BATH.value,
        "label": "Bathroom remodel",
        "selections": selections,
        "truth": "PROPOSED_DESIGN",
    }
