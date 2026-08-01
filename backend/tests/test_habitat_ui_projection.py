"""Field-test smoke: dashboard projection + openings + exterior studio entry."""

from habitat_ui.awe_twin import build_dashboard_projection, habitat_dashboard_projection_stub
from habitat_ui.openings import demo_openings_for_property, rough_opening_from_unit, OpeningKind
from exterior_studio.addition_workflow import studio_entry_view, connect_points, derive_structure_metrics, StructureKind, HouseSide


def test_stub_dashboard_shape():
    d = habitat_dashboard_projection_stub()
    assert d["property"]["certified_score"] > 0
    assert "structure" in d["home_health"]["systems"]
    assert d["awe"]["awe_index"] > 0
    assert d["authoritative"] is False


def test_build_dashboard_never_raises():
    d = build_dashboard_projection("demo", "demo-property")
    assert "property" in d
    assert "passport_status" in d or d.get("property")


def test_openings_rough_opening():
    ro = rough_opening_from_unit(36, 48, OpeningKind.WINDOW)
    assert ro["width_in"] == 38.0
    assert ro["height_in"] == 50.5
    items = demo_openings_for_property()
    assert len(items) >= 3
    assert "rough_opening_display" in items[0]


def test_exterior_studio_demo_outline():
    entry = studio_entry_view()
    assert entry["canvas_mode"] == "finish_plus_grounds"
    pts = [{"x": 10, "y": 28}, {"x": 30, "y": 28}, {"x": 30, "y": 42}, {"x": 10, "y": 42}]
    c = connect_points(pts, close=True)
    assert c["ok"] and c["closed"]
    m = derive_structure_metrics(pts, HouseSide.SOUTH, StructureKind.ROOM_ADDITION, shared_wall_lf=20)
    assert m["ok"]
    assert m["footprint_sqft"] == 280
