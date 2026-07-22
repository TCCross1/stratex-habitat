"""
STRATEX HABITAT — Home Steward Vertical Slice Integration & Security Tests (H-012)
"""
import pytest
import requests
import uuid

class TestHomeSteward:
    
    # --- Task 2: Fixture Tests ---
    def test_get_fixture(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/steward/fixture")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "passport_explanation" in data
        assert "truth_states" in data
        assert "unresolved_gap" in data
        assert data["authorized_owner"] == "alex@stratexhabitat.com"
        
        # Verify mixed truth states
        states = {item["item"]: item["state"] for item in data["truth_states"]}
        assert states["Roof Material"] == "VERIFIED"
        assert states["Roof Installation Year"] == "ESTIMATED"
        assert states["Deck Structural Health"] == "UNKNOWN"
        assert states["Shingle Warranty Status"] == "HOMEOWNER-REPORTED"
        
    def test_get_fixture_tenant_isolation(self, contractor_session, api_url):
        # Contractor is horizon@stratexhabitat.com, not authorized to view alex's fixture
        r = contractor_session.get(f"{api_url}/steward/fixture")
        assert r.status_code == 403
        
    # --- Task 3: Context Orchestrator Tests ---
    def test_get_context(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/steward/context")
        assert r.status_code == 200
        data = r.json()
        assert "property_identity" in data
        assert "published_explanation" in data
        assert "property_dna_projection" in data
        assert "seasonal_context" in data
        
        # Verify metadata schemas are attached to every context item
        for key in ["property_identity", "published_explanation", "property_dna_projection"]:
            item = data[key]
            assert "source_system" in item
            assert "source_id" in item
            assert "version" in item
            assert "truth_classification" in item
            assert "timestamp" in item
            assert "authorization_scope" in item
            
    # --- Task 4: Homeowner Question Experience ---
    def test_ask_question_new_roof(self, homeowner_session, api_url):
        r = homeowner_session.post(f"{api_url}/steward/ask", json={"question": "Do I need a new roof?"})
        assert r.status_code == 200
        data = r.json()
        assert "level_1_direct_answer" in data
        assert "level_2_why_this_matters" in data
        assert "level_3_supporting_information" in data
        assert "level_4_trace" in data
        
        # Verify Level 1 answers are truthful
        assert "do not confirm" in data["level_1_direct_answer"]
        assert "deflection" in data["level_1_direct_answer"]
        
    def test_ask_question_invalid(self, homeowner_session, api_url):
        r = homeowner_session.post(f"{api_url}/steward/ask", json={"question": "What is the weather?"})
        assert r.status_code == 400 # vertical slice constraint
        
    # --- Task 5: Recommended Action Engine ---
    def test_recommendation_engine(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/steward/recommendation")
        assert r.status_code == 200
        data = r.json()
        assert "primary" in data
        assert "secondary_progressive_disclosure" in data
        assert data["primary"]["type"] == "Schedule a focused roof inspection"
        assert len(data["secondary_progressive_disclosure"]) >= 3
        
    # --- Task 6 & 7: Confirmation and Project Creation ---
    def test_confirmation_and_project_creation(self, homeowner_session, api_url):
        # 1. Fetch fixture to get property_id
        fix_r = homeowner_session.get(f"{api_url}/steward/fixture")
        pid = fix_r.json()["property_id"]
        
        # 2. Post confirmation
        confirm_r = homeowner_session.post(f"{api_url}/steward/confirm", json={
            "property_id": pid,
            "action": "Explore Roof Replacement"
        })
        assert confirm_r.status_code == 200
        confirm_data = confirm_r.json()
        assert confirm_data["status"] == "confirmed"
        assert "correlation_id" in confirm_data
        
        # Check audit event
        audit = confirm_data["audit_event"]
        assert audit["event_type"] == "HOMEOWNER_ACTION_CONFIRMED"
        assert audit["confirmed_action"] == "Explore Roof Replacement"
        
        # 3. Verify Design Studio project was pre-populated
        sc_r = homeowner_session.get(f"{api_url}/design/scenarios?property_id={pid}")
        assert sc_r.status_code == 200
        scenarios = sc_r.json()
        projects = [s for s in scenarios if s.get("name") == "Project: Roof Replacement"]
        assert len(projects) >= 1
        proj = projects[0]
        assert proj["is_project"] is True
        assert proj["imported_geometry"]["approx_area_sqft"] == 3200
        
    # --- Task 8: Project Estimator Integration ---
    def test_project_estimator(self, homeowner_session, api_url):
        # Shingles estimate
        r = homeowner_session.post(f"{api_url}/steward/estimate", json={"material": "GAF Timberline HDZ"})
        assert r.status_code == 200
        data = r.json()
        assert data["pricing_date"] == "July 2026"
        assert "Austin" in data["geographic_basis"]
        assert "scenarios" in data
        assert "breakdown" in data
        assert "cost_delta_explanation" in data
        
        # Metal estimate
        r_metal = homeowner_session.post(f"{api_url}/steward/estimate", json={"material": "DECRA Standing Seam"})
        assert r_metal.status_code == 200
        data_metal = r_metal.json()
        assert "premium materials" in data_metal["cost_delta_explanation"]
        
    # --- Task 9: Home Investment Intelligence ---
    def test_investment_scenarios(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/steward/scenarios")
        assert r.status_code == 200
        data = r.json()
        assert "scenario_a" in data
        assert "scenario_b" in data
        assert "scenario_c" in data
        assert "resale_return" in data["scenario_a"]["unpromised_disclosures"]
        assert "energy_savings" in data["scenario_a"]["unpromised_disclosures"]
        
    # --- Task 10: Build Ready Review ---
    def test_readiness_review(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/steward/readiness")
        assert r.status_code == 200
        data = r.json()
        assert data["project_readiness_score"] == 65
        items = {item["item"]: item for item in data["priority_checklist"]}
        assert items["Existing Deck & Underlayment Condition"]["status"] == "MISSING"
        assert items["Existing Deck & Underlayment Condition"]["blocks_publication"] is True
        
    # --- Task 11: Contractor Package Preview ---
    def test_contractor_package_preview(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}/steward/contractor-package")
        assert r.status_code == 200
        data = r.json()
        assert "quantity_takeoff" in data
        assert "redacted_personal_info" in data
        assert "shared_documents" in data
        
    # --- Task 12: Project Opportunity Publication (H-013 Batch 2A: governed path) ---
    def test_publish_opportunity(self, homeowner_session, api_url):
        # Get property_id
        fix_r = homeowner_session.get(f"{api_url}/steward/fixture")
        pid = fix_r.json()["property_id"]
        
        # Get design scenario ID
        sc_r = homeowner_session.get(f"{api_url}/design/scenarios?property_id={pid}")
        scenarios = sc_r.json()
        proj_sc = [s for s in scenarios if s.get("name") == "Project: Roof Replacement"][0]
        
        # H-013 Batch 2A: the legacy route now routes through the single governed
        # publication service, which enforces the deck CONDITIONAL blocker. Without
        # acknowledgment the publication is correctly blocked (409); acknowledging
        # RDY-DECK-CONDITION permits the governed publication to proceed.
        blocked_r = homeowner_session.post(f"{api_url}/steward/publish", json={
            "property_id": pid,
            "scenario_id": proj_sc["id"],
            "remove_personal_info": True,
        })
        assert blocked_r.status_code == 409, blocked_r.text
        assert blocked_r.json()["detail"]["error_code"] == "PUBLICATION_BLOCKED"
        assert "RDY-DECK-CONDITION" in blocked_r.json()["detail"]["blocking_item_ids"]

        # Publish with the homeowner acknowledgment of the site-verification blocker
        pub_r = homeowner_session.post(f"{api_url}/steward/publish", json={
            "property_id": pid,
            "scenario_id": proj_sc["id"],
            "timeline_preference": "30 days",
            "budget_preference": "Premium",
            "shared_document_ids": ["doc_01"],
            "remove_personal_info": True,
            "acknowledged_blockers": ["RDY-DECK-CONDITION"],
        })
        assert pub_r.status_code == 200
        pub_data = pub_r.json()
        assert pub_data["status"] == "published"
        assert "opportunity_id" in pub_data
        
        # Check audit event
        audit = pub_data["audit"]
        assert audit["event_type"] == "PROJECT_OPPORTUNITY_PUBLISHED"
        assert audit["details"]["referenced_passport_and_dna"] is True
        
    # --- Task 13: Home Memory Behavior ---
    def test_home_memory(self, homeowner_session, api_url):
        # 1. Get memory
        r_get = homeowner_session.get(f"{api_url}/steward/memory")
        assert r_get.status_code == 200
        mem = r_get.json()
        assert "project_memory" in mem
        assert "homeowner_memory" in mem
        
        # 2. Update memory
        r_post = homeowner_session.post(f"{api_url}/steward/memory", json={
            "project_memories": {"preferred_roof_material": "DECRA Standing Seam"},
            "homeowner_memories": {"communication_preference": "In-app notifications"}
        })
        assert r_post.status_code == 200
        new_mem = r_post.json()
        assert new_mem["project_memory"]["preferred_roof_material"] == "DECRA Standing Seam"
        assert new_mem["homeowner_memory"]["communication_preference"] == "In-app notifications"
        
    # --- Security & Privacy Tests ---
    def test_security_unauthorized_endpoints(self, api_url):
        # No session session (unauthorized)
        r = requests.get(f"{api_url}/steward/fixture")
        assert r.status_code == 401
        
        r_context = requests.get(f"{api_url}/steward/context")
        assert r_context.status_code == 401
        
        r_post = requests.post(f"{api_url}/steward/ask", json={"question": "Do I need a new roof?"})
        assert r_post.status_code == 401
