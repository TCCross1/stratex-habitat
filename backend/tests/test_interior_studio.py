"""Field-test smoke: interior studio scan, catalog, remodel estimates."""

from interior_studio.lidar_scan import demo_kitchen_bath_scan, polygon_area_sqft, perimeter_lf
from interior_studio.catalog import find_item, region_labor_rate, catalog_tree
from interior_studio.remodel_ops import (
    kitchen_proposal,
    bath_proposal,
    open_concept_proposal,
    studio_entry,
)
from interior_studio.estimator import estimate_proposal, estimate_selections


def test_demo_scan_areas():
    scan = demo_kitchen_bath_scan("p1")
    assert len(scan["rooms"]) == 3
    kitchen = next(r for r in scan["rooms"] if r["name"] == "Kitchen")
    assert kitchen["floor_area_sqft"] == 168.0  # 14x12
    assert kitchen["truth"] == "HOMEOWNER_REPORTED"


def test_polygon_helpers():
    pts = [{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}, {"x": 0, "y": 10}]
    assert polygon_area_sqft(pts) == 100.0
    assert perimeter_lf(pts) == 40.0


def test_catalog_and_labor():
    assert find_item("quartz") is not None
    assert find_item("lvl_beam") is not None
    assert region_labor_rate("US-KY") == 55
    assert len(catalog_tree()["categories"]) >= 5


def test_kitchen_estimate_positive():
    prop = kitchen_proposal()
    out = estimate_proposal(prop, region="US-KY")
    s = out["estimate"]["summary"]
    assert s["total_planning_estimate"] > 1000
    assert s["labor_hours"] > 0
    assert out["estimate"]["truth"] == "ESTIMATED"


def test_bath_and_open_concept():
    bath = estimate_proposal(bath_proposal(), region="US-KY")
    assert bath["estimate"]["summary"]["total_planning_estimate"] > 500
    oc = estimate_proposal(
        open_concept_proposal(wall_length_lf=12, is_bearing=True), region="US-KY"
    )
    assert any("bearing" in w.lower() or "structural" in w.lower() for w in oc["warnings"])
    assert oc["estimate"]["summary"]["total_planning_estimate"] > 0


def test_studio_entry():
    e = studio_entry()
    assert e["promise"]
    assert len(e["project_options"]) >= 4


def test_raw_selections():
    est = estimate_selections(
        [{"item_id": "lvp_prem", "qty": 100}, {"item_id": "paint_walls", "qty": 400}],
        region="US-KY",
    )
    assert est["summary"]["materials"] > 0
    assert len(est["lines"]) == 2
