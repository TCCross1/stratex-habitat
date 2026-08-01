"""API: exterior openings + AWE twin layers for Habitat."""

from __future__ import annotations

from fastapi import APIRouter

from .openings import demo_openings_for_property
from .awe_twin import habitat_dashboard_projection_stub, twin_layer_set, awe_findings_on_twin

router = APIRouter(prefix="/api/habitat", tags=["habitat-ui"])


@router.get("/dashboard/projection")
def dashboard_projection():
    """Passport-shaped projection driving the mockup-locked Habitat dashboard."""
    return habitat_dashboard_projection_stub()


@router.get("/twin/layers")
def layers():
    return {"layers": twin_layer_set()}


@router.get("/twin/awe-hotspots")
def awe_hotspots():
    return {"hotspots": awe_findings_on_twin(), "brand": "AWE™"}


@router.get("/openings")
def list_openings():
    """Windows, doors, rough openings for twin hotspots + detail panel."""
    return {"openings": demo_openings_for_property()}


@router.get("/openings/{opening_id}")
def get_opening(opening_id: str):
    for o in demo_openings_for_property():
        if o["id"] == opening_id:
            return o
    # demo ids are random; return first for field-test wiring
    items = demo_openings_for_property()
    return items[0] if items else {"error": "not_found"}
