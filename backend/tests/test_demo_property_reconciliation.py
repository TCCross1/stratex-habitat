"""Unit tests for Central Kentucky demo property reconciliation safety."""
from demo_property import (
    DEMO_PROPERTY_NAME,
    is_explicit_demo_record,
    reconcile_demo_findings,
    reconcile_demo_properties,
    finding_demo_fields,
)


def test_unmarked_property_is_refused():
    props = [{"id": "real-1", "name": "Real Family Home", "owner_id": "u1", "location": "Louisville, KY"}]
    report = reconcile_demo_properties(props, dry_run=True)
    assert report["updated"] == []
    assert report["refused"][0]["id"] == "real-1"
    assert report["refused"][0]["reason"] == "missing_explicit_demo_marker"
    assert props[0]["name"] == "Real Family Home"


def test_unmarked_property_not_mutated_on_apply():
    props = [{"id": "real-2", "name": "Production Home", "owner_id": "u2"}]
    before = dict(props[0])
    report = reconcile_demo_properties(props, dry_run=False)
    assert report["refused"]
    assert props[0] == before


def test_explicit_demo_property_is_updated():
    props = [{
        "id": "demo-1",
        "name": "Villa Horizon",
        "owner_id": "alex",
        "is_demo_fixture": True,
        "visualization_data_origin": "demo",
        "twin_image": "https://example.com/flat-roof.png",
    }]
    report = reconcile_demo_properties(props, dry_run=False)
    assert len(report["updated"]) == 1
    assert props[0]["name"] == DEMO_PROPERTY_NAME
    assert props[0]["location"] == "Lexington, Kentucky"
    assert "/property-visualizations/habitat-central-kentucky-demo-home" in props[0]["twin_image"]
    assert "emergentagent.com" not in props[0]["twin_image"]


def test_legacy_seed_requires_explicit_allow():
    props = [{"id": "legacy-1", "name": "Villa Horizon", "owner_id": "alex-id"}]
    emails = {"alex-id": "alex@stratexhabitat.com"}
    refused = reconcile_demo_properties(props, dry_run=True, owner_email_by_id=emails)
    assert refused["refused"]
    allowed = reconcile_demo_properties(
        props,
        dry_run=False,
        allow_legacy_seed_email="alex@stratexhabitat.com",
        owner_email_by_id=emails,
    )
    assert allowed["updated"]
    assert props[0]["is_demo_fixture"] is True
    assert props[0]["name"] == DEMO_PROPERTY_NAME


def test_finding_demo_fields_never_approved():
    fields = finding_demo_fields()
    assert fields["truth_status"] == "sample_only"
    assert fields["is_approved_finding"] is False
    assert fields["is_lidar_detected"] is False
    assert fields["passport_approved"] is False


def test_findings_for_non_demo_property_refused():
    findings = [{"id": "f1", "property_id": "real-prop", "title": "Something"}]
    report = reconcile_demo_findings(findings, demo_property_ids={"demo-only"}, dry_run=False)
    assert report["refused"]
    assert "truth_status" not in findings[0]


def test_is_explicit_demo_record():
    assert is_explicit_demo_record({"is_demo_fixture": True})
    assert is_explicit_demo_record({"visualization_data_origin": "demo"})
    assert not is_explicit_demo_record({"name": "Villa Horizon"})
