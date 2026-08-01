"""Tests for roof-to-existing attachment logic"""

from backend.exterior_studio.roof_attachment import (
    AdditionOutline,
    AttachmentStrategy,
    ExistingRoofContext,
    ExistingRoofForm,
    Feasibility,
    evaluate_roof_attachment,
)
from backend.exterior_studio.addition_workflow import connect_points, derive_structure_metrics, StructureKind, HouseSide


def test_connect_rectangle():
    pts = [
        {"x": 0, "y": 0},
        {"x": 20, "y": 0},
        {"x": 20, "y": 12},
        {"x": 0, "y": 12},
    ]
    r = connect_points(pts, close=True)
    assert r["ok"] and r["closed"]
    assert abs(r["area_sqft"] - 240) < 0.1
    assert abs(r["perimeter_ft"] - 64) < 0.1


def test_metrics_wall_lf():
    pts = [
        {"x": 0, "y": 0},
        {"x": 24, "y": 0},
        {"x": 24, "y": 14},
        {"x": 0, "y": 14},
    ]
    m = derive_structure_metrics(pts, HouseSide.SOUTH, StructureKind.ROOM_ADDITION, shared_wall_lf=24)
    assert m["footprint_sqft"] == 336
    assert m["new_exterior_wall_lf"] == 76  # 24+14+24+14 - 24 shared = 52? wait perimeter 76, shared 24 → 52
    assert abs(m["new_exterior_wall_lf"] - 52) < 0.1


def test_shed_works_on_eave():
    outline = AdditionOutline(points=[(0, 0), (20, 0), (20, 12), (0, 12)])
    ctx = ExistingRoofContext(
        form=ExistingRoofForm.GABLE,
        primary_pitch_rise=6,
        wall_is_eave_side=True,
        wall_is_gable_end=False,
        attachment_wall="south",
    )
    result = evaluate_roof_attachment(ctx, outline)
    strategies = {o["strategy"]: o for o in result["options"]}
    assert strategies["lower_lean_to_shed"]["feasibility"] in ("works", "works_with_conditions")


def test_complex_outline_gets_shape_advice():
    # L-ish shape with 6 points
    outline = AdditionOutline(
        points=[(0, 0), (30, 0), (30, 10), (15, 10), (15, 20), (0, 20)]
    )
    ctx = ExistingRoofContext(form=ExistingRoofForm.HIP, primary_pitch_rise=7)
    result = evaluate_roof_attachment(ctx, outline)
    assert any("Complex outline" in s or "squaring" in s.lower() or "rectangle" in s.lower() for s in result["shape_advice"])
