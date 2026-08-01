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

