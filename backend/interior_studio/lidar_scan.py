"""
Homeowner LiDAR / room-scan model (MagicPlan-class).

Truth: HOMEOWNER_REPORTED until a contractor / Core verifies.
Does not mutate Passport as-built exterior twin.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class ScanSource(str, Enum):
    IPHONE_LIDAR = "iphone_lidar"
    IPAD_LIDAR = "ipad_lidar"
    MANUAL_TRACE = "manual_trace"
    IMPORTED = "imported"


class RoomType(str, Enum):
    KITCHEN = "kitchen"
    BATH_FULL = "bath_full"
    BATH_HALF = "bath_half"
    LIVING = "living"
    DINING = "dining"
    BEDROOM = "bedroom"
    HALL = "hall"
    LAUNDRY = "laundry"
    OTHER = "other"


class OpeningType(str, Enum):
    DOOR = "door"
    WINDOW = "window"
    PASS_THROUGH = "pass_through"
    ARCHWAY = "archway"
    Cased_OPENING = "cased_opening"


def polygon_area_sqft(points: List[Dict[str, float]]) -> float:
    """Shoelace formula; points in feet, closed or open."""
    if len(points) < 3:
        return 0.0
    pts = points + [points[0]]
    a = 0.0
    for i in range(len(pts) - 1):
        a += pts[i]["x"] * pts[i + 1]["y"] - pts[i + 1]["x"] * pts[i]["y"]
    return abs(a) / 2.0


def perimeter_lf(points: List[Dict[str, float]]) -> float:
    if len(points) < 2:
        return 0.0
    pts = points + [points[0]]
    total = 0.0
    for i in range(len(pts) - 1):
        dx = pts[i + 1]["x"] - pts[i]["x"]
        dy = pts[i + 1]["y"] - pts[i]["y"]
        total += (dx * dx + dy * dy) ** 0.5
    return round(total, 2)


def create_room(
    *,
    name: str,
    room_type: RoomType,
    wall_points_ft: List[Dict[str, float]],
    ceiling_height_ft: float = 8.0,
    openings: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    area = round(polygon_area_sqft(wall_points_ft), 2)
    perim = perimeter_lf(wall_points_ft)
    return {
        "id": str(uuid4()),
        "name": name,
        "room_type": room_type.value,
        "wall_polygon_ft": wall_points_ft,
        "ceiling_height_ft": ceiling_height_ft,
        "floor_area_sqft": area,
        "wall_perimeter_lf": perim,
        # Approx wall area excluding openings (refined when openings sized)
        "wall_area_sqft_gross": round(perim * ceiling_height_ft, 2),
        "openings": openings or [],
        "truth": "HOMEOWNER_REPORTED",
        "source": "lidar_or_trace",
    }


def create_scan_session(
    *,
    property_id: str,
    source: ScanSource = ScanSource.IPHONE_LIDAR,
    rooms: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "scan_id": str(uuid4()),
        "property_id": property_id,
        "source": source.value,
        "rooms": rooms or [],
        "truth": "HOMEOWNER_REPORTED",
        "status": "draft",
        "notes": (
            "Interior scan is homeowner-captured. Dimensions support design and planning "
            "estimates only until professionally verified."
        ),
        "canvas": {
            "show_2d_plan": True,
            "show_3d_walkthrough": True,
            "as_built_vs_proposed": "toggle",
        },
    }


def demo_kitchen_bath_scan(property_id: str = "demo-property") -> Dict[str, Any]:
    """Field-test sample: kitchen + adjacent bath + living for open-concept demo."""
    kitchen = create_room(
        name="Kitchen",
        room_type=RoomType.KITCHEN,
        wall_points_ft=[
            {"x": 0, "y": 0},
            {"x": 14, "y": 0},
            {"x": 14, "y": 12},
            {"x": 0, "y": 12},
        ],
        ceiling_height_ft=9.0,
        openings=[
            {
                "id": "k-win-1",
                "type": OpeningType.WINDOW.value,
                "width_in": 48,
                "height_in": 48,
                "wall_index": 0,
            },
            {
                "id": "k-door-1",
                "type": OpeningType.DOOR.value,
                "width_in": 32,
                "height_in": 80,
                "wall_index": 1,
            },
        ],
    )
    living = create_room(
        name="Living Room",
        room_type=RoomType.LIVING,
        wall_points_ft=[
            {"x": 14, "y": 0},
            {"x": 28, "y": 0},
            {"x": 28, "y": 16},
            {"x": 14, "y": 16},
        ],
        ceiling_height_ft=9.0,
        openings=[
            {
                "id": "shared-wall",
                "type": OpeningType.PASS_THROUGH.value,
                "width_in": 0,
                "height_in": 0,
                "wall_index": 3,
                "note": "Shared with kitchen — candidate for open concept",
            }
        ],
    )
    bath = create_room(
        name="Hall Bath",
        room_type=RoomType.BATH_FULL,
        wall_points_ft=[
            {"x": 0, "y": 12},
            {"x": 8, "y": 12},
            {"x": 8, "y": 17},
            {"x": 0, "y": 17},
        ],
        ceiling_height_ft=8.0,
        openings=[
            {
                "id": "bath-door",
                "type": OpeningType.DOOR.value,
                "width_in": 28,
                "height_in": 80,
                "wall_index": 1,
            }
        ],
    )
    session = create_scan_session(
        property_id=property_id,
        source=ScanSource.IPHONE_LIDAR,
        rooms=[kitchen, living, bath],
    )
    session["status"] = "ready_for_design"
    session["demo"] = True
    return session
