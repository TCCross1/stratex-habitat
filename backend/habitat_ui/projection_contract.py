"""
Passport → Habitat projection contract (field-test).

Core seals mission packages into Passport.
Habitat reads only through this contract shape.
When drones/analytics complete, Core publish should fill these fields;
Habitat UI already binds to them.
"""

from __future__ import annotations

from typing import Any, Dict, List

CONTRACT_ID = "habitat.projection.v1"
CONTRACT_VERSION = "1.0.0"

# Required top-level keys for a field-ready homeowner projection
REQUIRED_KEYS = [
    "property_identity",
    "scores",
    "home_health",
    "awe",
    "twin",
    "openings",
    "timeline",
    "truth_policy",
]


def empty_field_ready_projection(property_id: str = "unknown") -> Dict[str, Any]:
    return {
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
        "property_id": property_id,
        "authoritative": False,
        "property_identity": {
            "address_line": None,
            "city_state_zip": None,
            "geo": None,
        },
        "scores": {
            "certified_score": None,
            "score_scale": 1000,
            "awe_index": None,
            "property_score": None,
            "roof_condition": None,
            "energy_score": None,
            "moisture_score": None,
        },
        "home_health": {
            "overall": None,
            "systems": {
                "structure": None,
                "roofing": None,
                "hvac": None,
                "plumbing": None,
                "electrical": None,
                "exterior": None,
            },
        },
        "awe": {
            "index": None,
            "hotspots": [],
            "brand": "AWE™",
        },
        "twin": {
            "mesh_ref": None,
            "layers": ["finish", "thermal", "moisture", "framing", "energy", "openings", "awe"],
            "plane_count": 0,
            "measurements": {},
        },
        "openings": [],  # {id, kind, label, elevation, unit_w_in, unit_h_in, rough_w_in, rough_h_in, truth}
        "timeline": [],
        "maintenance": {
            "next_12_months_usd": None,
            "actions": [],
        },
        "truth_policy": (
            "VERIFIED findings require sealed Passport evidence. "
            "ESTIMATED may display with labels. WITHHELD geometry never shown."
        ),
        "habitat_role": "read-only",
    }


def validate_projection(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    openings = payload.get("openings") or []
    opening_issues = []
    for i, o in enumerate(openings):
        for req in ("id", "kind", "unit_w_in", "unit_h_in", "truth"):
            if req not in o:
                opening_issues.append(f"openings[{i}].{req}")
    return {
        "ok": not missing and not opening_issues,
        "missing_keys": missing,
        "opening_issues": opening_issues,
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
    }
