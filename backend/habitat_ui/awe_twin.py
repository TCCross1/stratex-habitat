"""
AWE (Air · Water · Energy) overlays and report cards bound to the Habitat twin.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def awe_index_card(
    score: int,
    label: str = "Good",
    air: Optional[int] = None,
    water: Optional[int] = None,
    energy: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "awe_index": score,
        "label": label,
        "components": {
            "air": air,
            "water": water,
            "energy": energy,
        },
        "brand": "AWE™",
        "truth": "ESTIMATED",
    }


def twin_layer_set() -> List[Dict[str, Any]]:
    """Landing-page twin layers matching product rules."""
    return [
        {"id": "finish", "label": "Finish", "default": True, "studio_default": True},
        {"id": "thermal", "label": "Thermal", "default": False, "studio_default": False},
        {"id": "moisture", "label": "Moisture", "default": False, "studio_default": False},
        {"id": "framing", "label": "Framing", "default": False, "studio_default": False},
        {"id": "energy", "label": "Energy", "default": False, "studio_default": False},
        {"id": "openings", "label": "Openings", "default": False, "studio_default": False},
        {"id": "awe", "label": "AWE", "default": False, "studio_default": False},
    ]


def awe_findings_on_twin() -> List[Dict[str, Any]]:
    """Hotspots that appear on the 3D twin when AWE layer is active."""
    return [
        {
            "id": "awe-attic-heat",
            "title": "Attic heat loss",
            "domain": "energy",
            "severity": "high",
            "summary": "Elevated thermal signature at ridge / attic plane.",
            "report_ref": "awe/energy/attic-heat",
        },
        {
            "id": "awe-window-seal",
            "title": "Window seal anomaly",
            "domain": "air",
            "severity": "medium",
            "summary": "Possible air leakage at upper-floor glazing.",
            "report_ref": "awe/air/window-seal",
        },
        {
            "id": "awe-moisture-eave",
            "title": "Eave moisture risk",
            "domain": "water",
            "severity": "medium",
            "summary": "Moisture pattern near eave / gutter line.",
            "report_ref": "awe/water/eave",
        },
    ]


def habitat_dashboard_projection_stub(address: str = "1234 Appalachian Way") -> Dict[str, Any]:
    """Shape of Passport → Habitat dashboard projection for UI binding."""
    return {
        "property": {
            "address_line": address,
            "city_state_zip": "London, KY 40741",
            "certified_score": 87,
            "score_scale": 1000,
            "rank_label": "TOP 15% of Homes in KY",
        },
        "home_health": {
            "overall": 72,
            "label": "Good",
            "systems": {
                "structure": 76,
                "roofing": 68,
                "hvac": 74,
                "plumbing": 71,
                "electrical": 78,
                "exterior": 69,
            },
        },
        "predictive_maintenance": {
            "next_12_months_usd": 2840,
            "recommended_actions": 5,
        },
        "awe": awe_index_card(82, "Good"),
        "twin_layers": twin_layer_set(),
        "awe_hotspots": awe_findings_on_twin(),
        "tagline": "CORE PERFORMS THE WORK. PASSPORT REMEMBERS THE HOME. HABITAT SUSTAINS THE RELATIONSHIP.",
    }
