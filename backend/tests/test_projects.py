"""
STRATEX HABITAT — Homeowner Architect Phase 1 Integration & Unit Tests
"""
import pytest
import requests
import uuid
import pymongo

# Helpers for testing
def get_user_session(api_url, email, password):
    s = requests.Session()
    r = s.post(f"{api_url}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return s

def register_user(api_url, name, email, password, role="homeowner"):
    r = requests.post(f"{api_url}/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": role
    })
    return r.status_code in (200, 400) # 200 if created, 400 if already exists

class TestProjectsUnitAndIntegration:

    @pytest.fixture(autouse=True)
    def setup_class(self, api_url):
        self.api = api_url
        
        # Connect to MongoDB to seed test-specific isolated records
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.mongo["habitat_test"]

        # Register test users
        register_user(self.api, "Alice Homeowner", "alice_test@stratexhabitat.com", "Demo123!", "homeowner")
        register_user(self.api, "Bob Renovator", "bob_contractor@stratexhabitat.com", "Demo123!", "contractor")
        register_user(self.api, "Charlie Roofer", "charlie_roofing@stratexhabitat.com", "Demo123!", "contractor")
        register_user(self.api, "Mallory Hacker", "mallory_test@stratexhabitat.com", "Demo123!", "homeowner")

        # Session creation
        self.alice = get_user_session(self.api, "alice_test@stratexhabitat.com", "Demo123!")
        self.bob = get_user_session(self.api, "bob_contractor@stratexhabitat.com", "Demo123!")
        self.charlie = get_user_session(self.api, "charlie_roofing@stratexhabitat.com", "Demo123!")
        self.mallory = get_user_session(self.api, "mallory_test@stratexhabitat.com", "Demo123!")

        # Retrieve user IDs from the DB to seed isolated properties and contractor profiles
        alice_user = self.db.users.find_one({"email": "alice_test@stratexhabitat.com"})
        bob_user = self.db.users.find_one({"email": "bob_contractor@stratexhabitat.com"})
        charlie_user = self.db.users.find_one({"email": "charlie_roofing@stratexhabitat.com"})
        mallory_user = self.db.users.find_one({"email": "mallory_test@stratexhabitat.com"})

        self.alice_id = alice_user["id"]
        self.bob_id = bob_user["id"]
        self.charlie_id = charlie_user["id"]
        self.mallory_id = mallory_user["id"]

        # Ensure isolated property exists for Alice
        self.db.properties.delete_many({"owner_id": self.alice_id})
        self.alice_prop_id = "alice_test_property_uuid"
        self.db.properties.insert_one({
            "id": self.alice_prop_id,
            "owner_id": self.alice_id,
            "name": "Alice's Oasis",
            "location": "Austin, TX",
            "status": "Connected"
        })

        # Ensure isolated property exists for Mallory (to prevent Mallory's endpoints from returning empty)
        self.db.properties.delete_many({"owner_id": self.mallory_id})
        self.db.properties.insert_one({
            "id": "mallory_test_property_uuid",
            "owner_id": self.mallory_id,
            "name": "Mallory's Den",
            "location": "San Antonio, TX",
            "status": "Connected"
        })

        # Ensure isolated contractor profiles exist
        self.db.contractors.delete_many({"owner_user_id": {"$in": [self.bob_id, self.charlie_id]}})
        
        self.bob_contractor_id = "bob_contractor_uuid"
        self.db.contractors.insert_one({
            "id": self.bob_contractor_id,
            "owner_user_id": self.bob_id,
            "company_name": "Bob's Premium Renovations",
            "description": "Specialized residential contractor serving Central Texas",
            "service_area": "Austin Metro, TX",
            "trades": ["Renovation"],
            "public_rating": 4.8
        })

        self.charlie_contractor_id = "charlie_contractor_uuid"
        self.db.contractors.insert_one({
            "id": self.charlie_contractor_id,
            "owner_user_id": self.charlie_id,
            "company_name": "Charlie's Roofs Only",
            "description": "Exclusively roofing solutions",
            "service_area": "Austin Metro, TX",
            "trades": ["Roofing"],
            "public_rating": 4.5
        })

    def test_project_lifecycle_e2e(self):
        # 1. Fetch properties for Alice
        props_r = self.alice.get(f"{self.api}/properties")
        assert props_r.status_code == 200
        props = props_r.json()
        assert len(props) >= 1
        pid = props[0]["id"]
        assert pid == self.alice_prop_id

        # 2. Create Kitchen Transformation project
        proj_payload = {
            "property_id": pid,
            "title": "Kitchen Expansion",
            "project_type": "Kitchen Transformation",
            "category": "Renovation",
            "space_type": "Kitchen",
            "description": "Full kitchen expansion and custom island installation",
            "homeowner_goal": "improve storage and add a premium transformation",
            "budget_min": 50000.0,
            "budget_max": 95000.0,
            "target_timeline": "90 days"
        }
        create_r = self.alice.post(f"{self.api}/projects", json=proj_payload)
        assert create_r.status_code == 200, create_r.text
        proj = create_r.json()
        proj_id = proj["id"]
        assert proj["current_state"] == "IDEA"

        # 3. Read Authorized Project
        get_r = self.alice.get(f"{self.api}/projects/{proj_id}")
        assert get_r.status_code == 200
        assert get_r.json()["title"] == "Kitchen Expansion"

        # 4. Verify separate tenant (Mallory) cannot access Alice's project
        mal_get = self.mallory.get(f"{self.api}/projects/{proj_id}")
        assert mal_get.status_code == 403

        # 5. Fetch Seeded Concepts
        concepts_r = self.alice.get(f"{self.api}/projects/{proj_id}/concepts")
        assert concepts_r.status_code == 200
        concepts = concepts_r.json()
        assert len(concepts) == 3
        # Pricing confidence labels and details
        assert any(c["design_direction"] == "Transform" and c["cost_confidence"] == "medium" for c in concepts)

        # 6. Select Concept (should auto transition IDEA -> CONCEPT_DESIGN)
        transform_concept = [c for c in concepts if c["design_direction"] == "Transform"][0]
        sel_r = self.alice.post(f"{self.api}/projects/{proj_id}/concepts/{transform_concept['id']}/select")
        assert sel_r.status_code == 200

        state_r = self.alice.get(f"{self.api}/projects/{proj_id}")
        assert state_r.json()["current_state"] == "CONCEPT_DESIGN"

        # 7. Add product preferences
        prod_payload = {
            "category": "cabinets",
            "manufacturer": "IKEA",
            "product_name": "Sektion Modular Cabinets",
            "model_or_sku": "SEK-MOD-101",
            "finish": "Matt White",
            "quantity": 12,
            "unit_price": 450.0,
            "price_source": "homeowner_estimate",
            "compatibility_status": "LIKELY_COMPATIBLE",
            "verification_required": True,
            "notes": "Homeowner selected choice"
        }
        add_prod_r = self.alice.post(f"{self.api}/projects/{proj_id}/products", json=prod_payload)
        assert add_prod_r.status_code == 200, add_prod_r.text

        # Verify product compatibility states
        prods = self.alice.get(f"{self.api}/projects/{proj_id}/products").json()
        assert len(prods) >= 1
        assert prods[-1]["compatibility_status"] == "LIKELY_COMPATIBLE"

        # 8. Verify project cannot request quotes before PIP is generated or readiness is not PLAN_REVIEW/READY_FOR_QUOTES
        quote_err_r = self.alice.post(f"{self.api}/projects/{proj_id}/request-quotes")
        assert quote_err_r.status_code == 400

        # 9. Verify invalid project state change is rejected
        invalid_trans_r = self.alice.post(f"{self.api}/projects/{proj_id}/transition", json={
            "new_state": "READY_FOR_QUOTES",
            "reason": "Skip steps"
        })
        assert invalid_trans_r.status_code == 400

        # Transition CONCEPT_DESIGN -> PRODUCT_SELECTION -> PLAN_REVIEW
        t1 = self.alice.post(f"{self.api}/projects/{proj_id}/transition", json={"new_state": "PRODUCT_SELECTION"})
        assert t1.status_code == 200
        t2 = self.alice.post(f"{self.api}/projects/{proj_id}/transition", json={"new_state": "PLAN_REVIEW"})
        assert t2.status_code == 200

        # 10. Generate Project Intent Package (PIP)
        pip_r = self.alice.post(f"{self.api}/projects/{proj_id}/generate-pip")
        assert pip_r.status_code == 200
        pip = pip_r.json()
        assert pip["package_status"] == "issued"
        assert "immutable_digest" in pip

        # Should be READY_FOR_QUOTES now
        state_r2 = self.alice.get(f"{self.api}/projects/{proj_id}")
        assert state_r2.json()["current_state"] == "READY_FOR_QUOTES"

        # 11. Request quotes
        quotes_r = self.alice.post(f"{self.api}/projects/{proj_id}/request-quotes")
        assert quotes_r.status_code == 200
        quote = quotes_r.json()
        qid = quote["id"]
        assert quote["status"] == "open"

        # Project state is now QUOTES_REQUESTED
        state_r3 = self.alice.get(f"{self.api}/projects/{proj_id}")
        assert state_r3.json()["current_state"] == "QUOTES_REQUESTED"

        # 12. Check contractor lead isolation and matching:
        # Renovation-capable contractor (Bob) should receive the lead
        bob_leads_r = self.bob.get(f"{self.api}/marketplace/leads")
        assert bob_leads_r.status_code == 200
        bob_leads = bob_leads_r.json()
        assert any(l["id"] == qid for l in bob_leads)

        # Ineligible roofing-only contractor (Charlie) does NOT receive the lead
        charlie_leads_r = self.charlie.get(f"{self.api}/marketplace/leads")
        assert charlie_leads_r.status_code == 200
        charlie_leads = charlie_leads_r.json()
        assert not any(l["id"] == qid for l in charlie_leads)

        # Contractor (Bob) can read authorized opportunity details
        bob_get_r = self.bob.get(f"{self.api}/projects/{proj_id}")
        assert bob_get_r.status_code == 200
        assert bob_get_r.json()["title"] == "Kitchen Expansion"

        # Unrelated contractor (Charlie) cannot access project details
        charlie_get_r = self.charlie.get(f"{self.api}/projects/{proj_id}")
        assert charlie_get_r.status_code == 403

        # 13. Contractor responds to quote request
        respond_payload = {
            "price_low": 48000.0,
            "price_high": 52000.0,
            "scope_notes": "We will provide complete cabinets and framing replacement",
            "timeline": "4 weeks",
            "estimated_start": "2026-09-01"
        }
        resp_r = self.bob.post(f"{self.api}/quotes/{qid}/respond", json=respond_payload)
        assert resp_r.status_code == 200

        # Contractor response appears in Habitat
        alice_quote_r = self.alice.get(f"{self.api}/quotes/{qid}")
        assert alice_quote_r.status_code == 200
        responses = alice_quote_r.json()["contractor_responses"]
        assert len(responses) >= 1
        assert responses[0]["scope_notes"] == "We will provide complete cabinets and framing replacement"

        # 14. Project State Transitions (Contractor Selected -> Field Verification -> Field Verified -> Quoted -> Approved -> In Progress -> Completed)
        transition_steps = [
            ("CONTRACTOR_RESPONDED", "Quotes are received from contractors."),
            ("CONTRACTOR_SELECTED", "Selected Bob's Premium Renovations."),
            ("FIELD_VERIFICATION_REQUIRED", "Need on-site inspection for partition walls."),
            ("FIELD_VERIFIED", "Bob confirmed wall is non-load-bearing."),
            ("QUOTED", "Bob supplied binding contract pricing."),
            ("APPROVED_FOR_CONSTRUCTION", "Approved contract and secured deposit."),
            ("IN_PROGRESS", "Demolition has commenced."),
            ("COMPLETED", "Final inspection passed successfully.")
        ]

        # First we need to manually transition to CONTRACTOR_RESPONDED to simulate state progression
        # (Though technically bob's response might auto-set state if implemented, let's transition)
        for next_state, rsn in transition_steps:
            tx_r = self.alice.post(f"{self.api}/projects/{proj_id}/transition", json={
                "new_state": next_state,
                "reason": rsn
            })
            assert tx_r.status_code == 200, f"Failed state transition to {next_state}: {tx_r.text}"

        # 15. Completed project cannot save to Passport without required evidence
        no_ev_r = self.alice.post(f"{self.api}/projects/{proj_id}/transition", json={
            "new_state": "SAVED_TO_PASSPORT",
            "reason": "Saving results."
        })
        assert no_ev_r.status_code == 400

        # 16. Valid completion updates Passport correctly
        ok_ev_r = self.alice.post(f"{self.api}/projects/{proj_id}/transition", json={
            "new_state": "SAVED_TO_PASSPORT",
            "reason": "Saving with certificate of completion",
            "completion_evidence_doc_id": "doc_cert_101"
        })
        assert ok_ev_r.status_code == 200
        assert ok_ev_r.json()["current_state"] == "SAVED_TO_PASSPORT"

        # Verify audit timeline matches
        timeline_r = self.alice.get(f"{self.api}/projects/{proj_id}/timeline")
        assert timeline_r.status_code == 200
        timeline = timeline_r.json()
        assert len(timeline) >= 5
        assert any(t.get("new_state") == "SAVED_TO_PASSPORT" for t in timeline)
