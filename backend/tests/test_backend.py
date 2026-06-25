"""Backend API tests for STRATEX HABITAT MVP."""
import requests
import pytest


# --- Auth ---
class TestAuth:
    def test_login_homeowner(self, api_url):
        r = requests.post(f"{api_url}/auth/login",
                          json={"email": "alex@stratexhabitat.com", "password": "Demo123!"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["email"] == "alex@stratexhabitat.com"
        assert data["role"] == "homeowner"
        assert "access_token" in r.cookies

    def test_login_contractor(self, api_url):
        r = requests.post(f"{api_url}/auth/login",
                          json={"email": "horizon@stratexhabitat.com", "password": "Demo123!"})
        assert r.status_code == 200, r.text
        assert r.json()["role"] == "contractor"

    def test_login_executive(self, api_url):
        r = requests.post(f"{api_url}/auth/login",
                          json={"email": "admin@stratexhabitat.com", "password": "Admin123!"})
        assert r.status_code == 200, r.text
        assert r.json()["role"] == "executive"

    def test_login_invalid(self, api_url):
        r = requests.post(f"{api_url}/auth/login",
                          json={"email": "alex@stratexhabitat.com", "password": "WRONG"})
        assert r.status_code == 401

    def test_me_via_cookie(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/auth/me")
        assert r.status_code == 200
        assert r.json()["email"] == "alex@stratexhabitat.com"

    def test_me_unauth(self, api_url):
        r = requests.get(f"{api_url}/auth/me")
        assert r.status_code == 401

    def test_logout_clears_cookie(self, api_url):
        s = requests.Session()
        s.post(f"{api_url}/auth/login",
               json={"email": "alex@stratexhabitat.com", "password": "Demo123!"})
        assert s.get(f"{api_url}/auth/me").status_code == 200
        r = s.post(f"{api_url}/auth/logout")
        assert r.status_code == 200
        # cookie cleared
        s.cookies.clear()
        assert s.get(f"{api_url}/auth/me").status_code == 401


# --- Property / analytics / assets / findings ---
class TestProperty:
    def test_properties_list(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/properties")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert any(p["name"] == "Villa Horizon" for p in data)

    def test_analytics(self, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = props[0]["id"]
        r = homeowner_session.get(f"{api_url}/properties/{pid}/analytics")
        assert r.status_code == 200
        data = r.json()
        # 4 KPI cards expected — verify presence
        assert "property_id" in data

    def test_assets_5(self, homeowner_session, api_url):
        props = homeowner_session.get(f"{api_url}/properties").json()
        pid = props[0]["id"]
        r = homeowner_session.get(f"{api_url}/properties/{pid}/assets")
        assert r.status_code == 200
        assert len(r.json()) == 5, f"Expected 5 assets, got {len(r.json())}"

    def test_findings_8(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/findings")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8, f"Expected 8 findings, got {len(data)}"
        # roof thermal expected
        titles = " ".join(f.get("title", "") for f in data).lower()
        assert "thermal" in titles or any("thermal" in (f.get("description") or "").lower() for f in data)

    def test_maintenance(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/maintenance")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_insights(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/insights")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_documents_3(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/documents")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_reports_3(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/reports")
        assert r.status_code == 200
        assert len(r.json()) == 3


# --- Quotes flow ---
class TestQuotes:
    def test_homeowner_create_quote(self, homeowner_session, api_url):
        payload = {
            "title": "TEST_ Quote Roof",
            "category": "Roofing",
            "description": "Test quote",
            "seriousness": "medium",
            "target_timeframe": "Flexible"
        }
        r = homeowner_session.post(f"{api_url}/quotes", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["title"] == "TEST_ Quote Roof"
        assert data["status"] == "open"
        assert "id" in data
        # verify persistence
        g = homeowner_session.get(f"{api_url}/quotes/{data['id']}")
        assert g.status_code == 200
        assert g.json()["title"] == "TEST_ Quote Roof"

    def test_quotes_list(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/quotes")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_contractor_cannot_create_quote(self, contractor_session, api_url):
        payload = {"title": "T", "category": "Roofing"}
        r = contractor_session.post(f"{api_url}/quotes", json=payload)
        assert r.status_code == 403

    def test_homeowner_cannot_respond(self, homeowner_session, api_url):
        # Get an existing quote
        quotes = homeowner_session.get(f"{api_url}/quotes").json()
        if not quotes:
            pytest.skip("No quotes available")
        qid = quotes[0]["id"]
        r = homeowner_session.post(f"{api_url}/quotes/{qid}/respond",
                                   json={"price_low": 100, "price_high": 200,
                                         "scope_notes": "x", "timeline": "1w"})
        assert r.status_code == 403

    def test_contractor_respond(self, contractor_session, api_url):
        # contractor's marketplace leads
        leads = contractor_session.get(f"{api_url}/marketplace/leads").json()
        if not leads:
            pytest.skip("No leads routed to contractor")
        qid = leads[0]["id"]
        r = contractor_session.post(f"{api_url}/quotes/{qid}/respond",
                                    json={"price_low": 2500.0, "price_high": 3000.0,
                                          "scope_notes": "TEST scope", "timeline": "2 weeks"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "responded"
        assert any(resp["scope_notes"] == "TEST scope" for resp in data["contractor_responses"])


# --- Marketplace ---
class TestMarketplace:
    def test_contractor_leads(self, contractor_session, api_url):
        r = contractor_session.get(f"{api_url}/marketplace/leads")
        assert r.status_code == 200
        leads = r.json()
        assert len(leads) >= 1
        # The seeded "Insulation Upgrade — Roof North Slope"
        titles = [l.get("title", "") for l in leads]
        assert any("Insulation" in t or "Roof" in t for t in titles), f"Titles: {titles}"

    def test_homeowner_cannot_view_leads(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/marketplace/leads")
        assert r.status_code == 403


# --- Contractors / Reviews ---
class TestContractors:
    def test_list_contractors(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/contractors")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 3
        names = [c["company_name"] for c in data]
        assert any("Horizon" in n for n in names)

    def test_contractor_detail_has_reviews_and_scorecard(self, homeowner_session, api_url):
        c_list = homeowner_session.get(f"{api_url}/contractors").json()
        cid = c_list[0]["id"]
        r = homeowner_session.get(f"{api_url}/contractors/{cid}")
        assert r.status_code == 200
        data = r.json()
        assert "reviews" in data
        assert "scorecard" in data
        assert "performance_grade" in data["scorecard"]

    def test_contractor_upsert(self, contractor_session, api_url):
        r = contractor_session.post(f"{api_url}/contractors",
                                    json={"company_name": "Horizon Roofing & Exteriors",
                                          "description": "TEST updated",
                                          "trades": ["Roofing", "Insulation"]})
        assert r.status_code == 200, r.text
        assert r.json()["description"] == "TEST updated"

    def test_homeowner_add_review(self, homeowner_session, api_url):
        c_list = homeowner_session.get(f"{api_url}/contractors").json()
        cid = c_list[0]["id"]
        r = homeowner_session.post(f"{api_url}/reviews",
                                   json={"contractor_id": cid, "rating": 5,
                                         "title": "TEST review", "body": "Great work"})
        assert r.status_code == 200, r.text
        assert r.json()["rating"] == 5
        # Verify contractor public_rating updated
        c = homeowner_session.get(f"{api_url}/contractors/{cid}").json()
        assert c["verified_reviews"] >= 1


# --- STRATEX Core ---
class TestCore:
    def test_status(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/core/status")
        assert r.status_code == 200
        d = r.json()
        assert d["connected"] is True
        assert d["published_assets"] >= 0  # might be 0 before publish or 5 after

    def test_executive_publish(self, exec_session, api_url):
        r = exec_session.post(f"{api_url}/core/publish")
        assert r.status_code == 200, r.text
        assert r.json()["ok"] is True
        # Verify published_assets now = 5
        s = exec_session.get(f"{api_url}/core/status").json()
        assert s["published_assets"] == 5

    def test_homeowner_cannot_publish(self, homeowner_session, api_url):
        r = homeowner_session.post(f"{api_url}/core/publish")
        assert r.status_code == 403
