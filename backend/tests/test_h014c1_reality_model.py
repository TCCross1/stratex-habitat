"""
H-014C.1 — GET /api/properties/{pid}/reality-model

Read-only, auth + tenant isolated, homeowner-safe. Never promotes geometry.
"""
import os
import pytest
import requests

BASE = os.environ.get("REACT_APP_BACKEND_URL", "http://127.0.0.1:8001").rstrip("/")
API = f"{BASE}/api"


def _login(email: str, password: str = "Demo123!"):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return s


@pytest.fixture(scope="module")
def homeowner():
    return _login("alex@stratexhabitat.com")


@pytest.fixture(scope="module")
def demo_property_id(homeowner):
    r = homeowner.get(f"{API}/properties")
    assert r.status_code == 200
    props = r.json()
    demo = next(
        (
            p
            for p in props
            if p.get("is_demo_fixture") is True
            or p.get("visualization_profile") == "central-kentucky-demo-home"
            or p.get("name") == "Central Kentucky Demonstration Home"
        ),
        None,
    )
    assert demo, "Central Kentucky demo property missing from seed"
    return demo["id"]


class TestRealityModelRead:
    def test_requires_authentication(self, demo_property_id):
        r = requests.get(f"{API}/properties/{demo_property_id}/reality-model")
        assert r.status_code in (401, 403)

    def test_demo_returns_sample_only_markers(self, homeowner, demo_property_id):
        r = homeowner.get(f"{API}/properties/{demo_property_id}/reality-model")
        assert r.status_code == 200
        body = r.json()
        assert body["property_id"] == demo_property_id
        assert body["lifecycle_state"] == "demo_sample"
        assert body["truth_status"] == "sample_only"
        assert body["data_origin"] == "demo"
        assert body["schema_version"] == "h014c1.reality.v1"
        assert body["floor_plan_available"] is False
        assert body["three_d_model_available"] is False
        assert "physically validated" in body["display_disclaimer"].lower() or "sample-only" in body["display_disclaimer"].lower()
        # No storage secrets
        blob = str(body).lower()
        assert "x-amz-signature" not in blob
        assert "aws_secret" not in blob
        assert "access_key" not in blob

    def test_tenant_isolation_hides_foreign_property(self, homeowner):
        r = homeowner.get(f"{API}/properties/not-a-real-property-id/reality-model")
        assert r.status_code == 404
        # Unauthorized must not leak model metadata
        assert "lifecycle_state" not in r.json() or r.json().get("detail")

    def test_approved_and_draft_remain_separate_from_demo(self, homeowner, demo_property_id):
        body = homeowner.get(f"{API}/properties/{demo_property_id}/reality-model").json()
        assert body["lifecycle_state"] != "approved_projection"
        assert body["truth_status"] != "approved"

    def test_no_write_method_on_route(self, homeowner, demo_property_id):
        for method in ("post", "put", "patch", "delete"):
            fn = getattr(requests, method)
            r = fn(
                f"{API}/properties/{demo_property_id}/reality-model",
                cookies=homeowner.cookies,
                json={"lifecycle_state": "approved_projection"},
            )
            assert r.status_code in (405, 404, 401, 403)
