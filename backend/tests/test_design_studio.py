"""Backend API tests for STRATEX HABITAT Design Studio module."""
import os
import requests
import pytest


# --- Design data endpoints (zones / library / recommendations / base / scenarios listing) ---
class TestDesignData:
    def test_zones_13(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/design/zones")
        assert r.status_code == 200, r.text
        zones = r.json()
        assert len(zones) == 13, f"Expected 13 zones, got {len(zones)}"
        ids = {z["id"] for z in zones}
        for required in ("roof", "siding_main", "front_door", "garage", "windows", "veneer", "trim"):
            assert required in ids, f"Missing zone {required}"

    def test_library_16(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/design/library")
        assert r.status_code == 200, r.text
        items = r.json()
        assert len(items) == 16, f"Expected 16 products, got {len(items)}"
        # sorted by popularity desc
        pops = [i.get("popularity", 0) for i in items]
        assert pops == sorted(pops, reverse=True), "Library is not sorted by popularity desc"

    def test_library_filter_category(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/design/library", params={"category": "Roofing"})
        assert r.status_code == 200
        items = r.json()
        assert len(items) >= 1
        assert all(p["category"] == "Roofing" for p in items)

    def test_library_filter_tone_warm(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/design/library", params={"tone": "warm"})
        assert r.status_code == 200
        items = r.json()
        # every returned product must have at least one warm color
        for p in items:
            assert any(c.get("tone") == "warm" for c in p["colors"]), f"{p['family']} no warm color"

    def test_library_filter_price_tier(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/design/library", params={"price_tier": "$$$$"})
        assert r.status_code == 200
        items = r.json()
        assert all(p["price_tier"] == "$$$$" for p in items)

    def test_recommendations_6(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/design/recommendations")
        assert r.status_code == 200
        recos = r.json()
        assert len(recos) == 6, f"Expected 6 recommendations, got {len(recos)}"
        assert {"luxury", "modern_contrast", "historic", "energy", "warm_stone", "budget"} <= {r["id"] for r in recos}

    def test_property_base(self, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = next(p["id"] for p in props if p["name"] == "Villa Horizon")
        r = homeowner_session.get(f"{api_url}/design/property/{pid}/base")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["property_id"] == pid
        assert data["base_image"].startswith("http")

    def test_preset_scenarios_6(self, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = next(p["id"] for p in props if p["name"] == "Villa Horizon")
        r = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid})
        assert r.status_code == 200, r.text
        scs = r.json()
        presets = [s for s in scs if s.get("is_preset")]
        assert len(presets) == 6, f"Expected 6 preset scenarios, got {len(presets)}"
        names = {s["name"] for s in presets}
        assert "Classic White Brick" in names
        assert "Premium Renovation Option" in names
        for p in presets:
            assert p.get("preview_url", "").startswith("http")
            assert isinstance(p.get("selections"), list)


# --- Auth gate ---
class TestDesignAuth:
    def test_zones_requires_auth(self, api_url):
        r = requests.get(f"{api_url}/design/zones")
        assert r.status_code == 401


# --- CRUD on user scenarios + favorite/patch ---
class TestScenarioCRUD:
    @pytest.fixture(scope="class")
    def pid(self, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        return next(p["id"] for p in props if p["name"] == "Villa Horizon")

    def test_create_scenario_persists(self, homeowner_session, api_url, pid):
        payload = {
            "property_id": pid,
            "name": "TEST_ My Custom Look",
            "style": "Modern",
            "selections": [{"zone": "siding_main", "product": "HardiePlank", "color": "Iron Gray"}],
            "preview_url": None,
            "base_image": None,
            "lighting": "daylight",
            "notes": "test",
            "est_low": 25000,
            "est_high": 35000,
        }
        r = homeowner_session.post(f"{api_url}/design/scenarios", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "TEST_ My Custom Look"
        assert data["is_preset"] is False
        assert data["favorite"] is False
        assert "id" in data
        sid = data["id"]
        # verify list
        scs = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        assert any(s["id"] == sid for s in scs), "Created scenario not in list"
        pytest.shared_sid = sid

    def test_favorite_patch(self, homeowner_session, api_url, pid):
        sid = getattr(pytest, "shared_sid", None)
        assert sid, "Need create test to run first"
        r = homeowner_session.patch(f"{api_url}/design/scenarios/{sid}", json={"favorite": True})
        assert r.status_code == 200, r.text
        assert r.json()["favorite"] is True
        # verify persistence
        scs = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        match = next(s for s in scs if s["id"] == sid)
        assert match["favorite"] is True
        assert match["version"] >= 2

    def test_delete_scenario(self, homeowner_session, api_url, pid):
        sid = getattr(pytest, "shared_sid", None)
        assert sid
        r = homeowner_session.delete(f"{api_url}/design/scenarios/{sid}")
        assert r.status_code == 200
        scs = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        assert not any(s["id"] == sid for s in scs)

    def test_cannot_delete_preset(self, homeowner_session, api_url, pid):
        scs = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        preset = next(s for s in scs if s.get("is_preset"))
        r = homeowner_session.delete(f"{api_url}/design/scenarios/{preset['id']}")
        # endpoint is filtered by is_preset:False -> safe no-op
        assert r.status_code == 200
        scs2 = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        assert any(s["id"] == preset["id"] for s in scs2), "Preset must remain"

    def test_patch_unknown_scenario_404(self, homeowner_session, api_url):
        r = homeowner_session.patch(f"{api_url}/design/scenarios/does-not-exist", json={"favorite": True})
        assert r.status_code == 404


# --- Request-quote-from-scenario flow ---
class TestScenarioRequestQuote:
    def test_request_quote_from_preset(self, homeowner_session, contractor_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = next(p["id"] for p in props if p["name"] == "Villa Horizon")
        scs = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        preset = next(s for s in scs if s.get("is_preset") and s["name"] == "Modern Charcoal Siding")
        sid = preset["id"]

        payload = {"project_type": "renovation", "seriousness": "medium", "target_timeframe": "3-6 months"}
        r = homeowner_session.post(f"{api_url}/design/scenarios/{sid}/request-quote", json=payload)
        assert r.status_code == 200, r.text
        q = r.json()
        assert q["title"].startswith("Design Studio — ")
        assert q["category"] == "Renovation"
        assert q["design_scenario_id"] == sid
        assert isinstance(q["affected_zones"], list) and len(q["affected_zones"]) >= 1
        assert isinstance(q["selections"], list) and len(q["selections"]) >= 1
        assert q.get("scenario_preview", "").startswith("http")
        assert q["status"] == "open"

        # verify in homeowner /api/quotes
        quotes = homeowner_session.get(f"{api_url}/quotes").json()
        assert any(qq["id"] == q["id"] for qq in quotes), "Design Studio quote missing from homeowner /quotes"

        # verify scenario marked quote_ready
        scs2 = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        s2 = next(s for s in scs2 if s["id"] == sid)
        assert s2["quote_ready"] is True
        assert q["id"] in s2.get("linked_quotes", [])

        # verify contractor marketplace shows lead (fallback: all contractors since no Renovation trade)
        leads = contractor_session.get(f"{api_url}/marketplace/leads").json()
        assert any(l["id"] == q["id"] for l in leads), \
            f"Design Studio quote not routed to contractor leads. Lead ids: {[l['id'] for l in leads]}"

    def test_contractor_cannot_request_design_quote(self, contractor_session, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = next(p["id"] for p in props if p["name"] == "Villa Horizon")
        scs = homeowner_session.get(f"{api_url}/design/scenarios", params={"property_id": pid}).json()
        sid = next(s for s in scs if s.get("is_preset"))["id"]
        r = contractor_session.post(f"{api_url}/design/scenarios/{sid}/request-quote",
                                    json={"project_type": "renovation"})
        assert r.status_code == 403


# --- Render endpoint: optional (skipped by default to save credits) ---
@pytest.mark.skipif(os.environ.get("RUN_RENDER_TEST") != "1",
                    reason="Skip live Gemini render unless RUN_RENDER_TEST=1")
class TestDesignRender:
    def test_render_returns_url(self, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = next(p["id"] for p in props if p["name"] == "Villa Horizon")
        base = homeowner_session.get(f"{api_url}/design/property/{pid}/base").json()
        body = {
            "property_id": pid,
            "base_image": base["base_image"],
            "selections": [{"zone": "front_door", "product": "Pulse Smooth", "color": "Tuscan Red"}],
            "lighting": "daylight",
        }
        r = homeowner_session.post(f"{api_url}/design/render", json=body, timeout=120)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("url", "").startswith("/api/files/")
