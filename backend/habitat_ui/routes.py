"""API: Habitat dashboard projection, openings, AWE twin layers (mockup-locked)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from habitat_ui.openings import demo_openings_for_property
from habitat_ui.awe_twin import (
    build_dashboard_projection,
    habitat_dashboard_projection_stub,
    twin_layer_set,
    awe_findings_on_twin,
)

router = APIRouter(prefix="/habitat", tags=["habitat-ui"])


@router.get("/dashboard/projection")
def dashboard_projection(
    tenant_id: str = Query("demo"),
    property_id: str = Query("demo-property"),
    stub_only: bool = Query(False),
):
    """
    Passport-shaped projection for Habitat dashboard.
    Tries Passport adapter merge; falls back to mockup demo stub.
    """
    if stub_only:
        return habitat_dashboard_projection_stub()
    return build_dashboard_projection(tenant_id, property_id)


@router.get("/twin/layers")
def layers():
    return {"layers": twin_layer_set()}


@router.get("/twin/awe-hotspots")
def awe_hotspots():
    return {"hotspots": awe_findings_on_twin(), "brand": "AWE™"}


@router.get("/openings")
def list_openings():
    return {"openings": demo_openings_for_property()}


@router.get("/openings/{opening_id}")
def get_opening(opening_id: str):
    items = demo_openings_for_property()
    for o in items:
        if o["id"] == opening_id:
            return o
    return items[0] if items else {"error": "not_found"}


@router.get("/projection/contract")
def projection_contract():
    """Field-ready Passport→Habitat contract schema for Core publishers."""
    from habitat_ui.projection_contract import (
        empty_field_ready_projection,
        validate_projection,
        CONTRACT_ID,
        CONTRACT_VERSION,
    )
    sample = empty_field_ready_projection("example")
    return {
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
        "sample": sample,
        "validation_example": validate_projection(sample),
    }


@router.get("/projection/from_sample_mission")
def projection_from_sample_mission():
    """
    Field-test: build habitat.projection.v1-shaped dashboard using the same
    rules Core will use after seal (local sample geometry/AWE/openings).
    Does not call Core; mirrors export_habitat_projection defaults.
    """
    from habitat_ui.hydrate_from_contract import dashboard_from_contract, openings_ui_from_contract
    from habitat_ui.projection_contract import empty_field_ready_projection

    # Local mirror of Core sample export (no cross-repo import at runtime)
    sample = empty_field_ready_projection("prop-field-test-ky")
    sample["authoritative"] = False
    sample["property_identity"] = {
        "address_line": "1234 Appalachian Way",
        "city_state_zip": "London, KY 40741",
        "geo": None,
    }
    sample["scores"] = {
        "certified_score": 87,
        "score_scale": 1000,
        "awe_index": 82,
        "property_score": 87,
        "roof_condition": 68,
        "energy_score": 71,
        "moisture_score": 70,
    }
    sample["home_health"] = {
        "overall": 72,
        "systems": {
            "structure": 76,
            "roofing": 68,
            "hvac": 74,
            "plumbing": 71,
            "electrical": 78,
            "exterior": 69,
        },
    }
    sample["awe"] = {
        "index": 82,
        "brand": "AWE™",
        "hotspots": [
            {
                "id": "awe-attic-heat",
                "title": "Attic heat loss",
                "domain": "energy",
                "severity": "high",
                "summary": "Elevated thermal signature at ridge / attic plane.",
                "report_ref": "awe/energy/attic-heat",
                "truth": "ESTIMATED",
            }
        ],
    }
    sample["twin"] = {
        "mesh_ref": None,
        "layers": ["finish", "thermal", "moisture", "framing", "energy", "openings", "awe"],
        "plane_count": 4,
        "withheld_plane_count": 1,
        "measurements": {
            "total_roof_area_sqft": 2015,
            "pitch_primary": "6/12",
        },
    }
    sample["openings"] = [
        {
            "id": "win-front-lr",
            "kind": "window",
            "label": "Front — Living Room Picture",
            "elevation": "front",
            "unit_w_in": 72,
            "unit_h_in": 48,
            "rough_w_in": 74,
            "rough_h_in": 50.5,
            "material": "vinyl",
            "condition": "fair",
            "truth": "ESTIMATED",
        },
        {
            "id": "door-front",
            "kind": "door",
            "label": "Front Entry",
            "elevation": "front",
            "unit_w_in": 36,
            "unit_h_in": 80,
            "rough_w_in": 38,
            "rough_h_in": 82.5,
            "material": "fiberglass",
            "condition": "good",
            "truth": "ESTIMATED",
        },
    ]
    sample["maintenance"] = {
        "next_12_months_usd": 2840,
        "actions": [{"title": "Attic heat loss", "severity": "high"}],
    }
    dash = dashboard_from_contract(sample)
    return {
        "dashboard": dash,
        "openings": openings_ui_from_contract(sample["openings"]),
        "contract": sample,
    }

