#!/usr/bin/env python3
"""
STRATEX HABITAT H-013 Batch 2 Test Suite

Tests Passport projection boundary, Build-Ready blocker policy, and persistent
Steward workflow with publication gates + idempotency.
"""
import os
import sys
import json
import requests
from typing import Optional, Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://exciting-torvalds-7.preview.emergentagent.com/api"

# Test credentials
HOMEOWNER_EMAIL = "alex@stratexhabitat.com"
HOMEOWNER_PASSWORD = "Demo123!"
CONTRACTOR_EMAIL = "horizon@stratexhabitat.com"
CONTRACTOR_PASSWORD = "Demo123!"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class TestSession:
    """Manages authentication and session for testing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user = None
    
    def login(self, email: str, password: str) -> bool:
        """Login and store session cookie/token."""
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                self.user = data
                if "token" in data:
                    self.token = data["token"]
                print(f"{GREEN}✓{RESET} Logged in as {email}")
                return True
            else:
                print(f"{RED}✗{RESET} Login failed for {email}: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"{RED}✗{RESET} Login exception for {email}: {e}")
            return False
    
    def get(self, path: str, **kwargs) -> requests.Response:
        """GET request with session."""
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return self.session.get(f"{BACKEND_URL}{path}", headers=headers, timeout=30, **kwargs)
    
    def post(self, path: str, **kwargs) -> requests.Response:
        """POST request with session."""
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return self.session.post(f"{BACKEND_URL}{path}", headers=headers, timeout=30, **kwargs)
    
    def logout(self):
        """Clear session."""
        try:
            self.session.post(f"{BACKEND_URL}/auth/logout", timeout=10)
        except:
            pass
        self.session = requests.Session()
        self.token = None
        self.user = None


def print_section(title: str):
    """Print a test section header."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")


def print_test(name: str):
    """Print a test name."""
    print(f"\n{YELLOW}Testing:{RESET} {name}")


def print_pass(message: str):
    """Print a pass message."""
    print(f"  {GREEN}✓ PASS:{RESET} {message}")


def print_fail(message: str):
    """Print a fail message."""
    print(f"  {RED}✗ FAIL:{RESET} {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"  {BLUE}ℹ INFO:{RESET} {message}")


def test_passport_projection_boundary(session: TestSession) -> dict:
    """Test A: PASSPORT PROJECTION BOUNDARY."""
    print_section("A) PASSPORT PROJECTION BOUNDARY")
    results = {"passed": 0, "failed": 0, "details": [], "property_id": None}
    
    print_test("GET /api/steward/context -> 200 with _projection envelope")
    try:
        resp = session.get("/steward/context")
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Context returned {resp.status_code}")
            return results
        
        data = resp.json()
        checks = []
        
        # Check _projection envelope
        if "_projection" not in data:
            print_fail("Missing '_projection' envelope")
            results["failed"] += 1
            results["details"].append("Missing _projection envelope")
            return results
        
        proj = data["_projection"]
        print_pass("Contains '_projection' envelope")
        
        # Check provider_mode == "development"
        if proj.get("provider_mode") == "development":
            print_pass("_projection.provider_mode == 'development'")
            checks.append(True)
        else:
            print_fail(f"provider_mode != 'development': {proj.get('provider_mode')}")
            checks.append(False)
        
        # Check authoritative == false
        if proj.get("authoritative") == False:
            print_pass("_projection.authoritative == false")
            checks.append(True)
        else:
            print_fail(f"authoritative != false: {proj.get('authoritative')}")
            checks.append(False)
        
        # Check contract_version == "1.0.0"
        if proj.get("contract_version") == "1.0.0":
            print_pass("_projection.contract_version == '1.0.0'")
            checks.append(True)
        else:
            print_fail(f"contract_version != '1.0.0': {proj.get('contract_version')}")
            checks.append(False)
        
        # Check fixture_or_seed_identifier is non-null
        if proj.get("fixture_or_seed_identifier"):
            print_pass(f"_projection.fixture_or_seed_identifier present: {proj.get('fixture_or_seed_identifier')}")
            checks.append(True)
        else:
            print_fail("fixture_or_seed_identifier is null")
            checks.append(False)
        
        # Check generated_at is non-null
        if proj.get("generated_at"):
            print_pass(f"_projection.generated_at present: {proj.get('generated_at')}")
            checks.append(True)
        else:
            print_fail("generated_at is null")
            checks.append(False)
        
        # Check top-level keys
        required_keys = ["property_identity", "published_explanation", "property_dna_projection", "seasonal_context"]
        for key in required_keys:
            if key in data:
                print_pass(f"Top-level key '{key}' present")
                checks.append(True)
            else:
                print_fail(f"Missing top-level key '{key}'")
                checks.append(False)
        
        # Capture property_identity.id
        if "property_identity" in data and "id" in data["property_identity"]:
            pid = data["property_identity"]["id"]
            results["property_id"] = pid
            print_info(f"Captured property_identity.id: {pid}")
        else:
            print_fail("Could not capture property_identity.id")
            checks.append(False)
        
        if all(checks):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["details"].append("Projection boundary validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Projection boundary exception: {e}")
    
    return results


def test_build_ready_blocker_policy(session: TestSession) -> dict:
    """Test B: BUILD-READY BLOCKER POLICY."""
    print_section("B) BUILD-READY BLOCKER POLICY")
    results = {"passed": 0, "failed": 0, "details": []}
    
    print_test("GET /api/steward/readiness -> 200 with deck condition as CONDITIONAL_BLOCKER")
    try:
        resp = session.get("/steward/readiness")
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Readiness returned {resp.status_code}")
            return results
        
        data = resp.json()
        checks = []
        
        # Check project_readiness_score == 65
        if data.get("project_readiness_score") == 65:
            print_pass("project_readiness_score == 65")
            checks.append(True)
        else:
            print_fail(f"project_readiness_score != 65: {data.get('project_readiness_score')}")
            checks.append(False)
        
        # Find the deck condition item
        checklist = data.get("priority_checklist", [])
        deck_item = None
        for item in checklist:
            if item.get("item") == "Existing Deck & Underlayment Condition":
                deck_item = item
                break
        
        if not deck_item:
            print_fail("Could not find 'Existing Deck & Underlayment Condition' item")
            results["failed"] += 1
            results["details"].append("Deck condition item not found")
            return results
        
        print_pass("Found 'Existing Deck & Underlayment Condition' item")
        
        # Check classification == "CONDITIONAL_BLOCKER"
        if deck_item.get("classification") == "CONDITIONAL_BLOCKER":
            print_pass("classification == 'CONDITIONAL_BLOCKER'")
            checks.append(True)
        else:
            print_fail(f"classification != 'CONDITIONAL_BLOCKER': {deck_item.get('classification')}")
            checks.append(False)
        
        # Check status == "MISSING"
        if deck_item.get("status") == "MISSING":
            print_pass("status == 'MISSING'")
            checks.append(True)
        else:
            print_fail(f"status != 'MISSING': {deck_item.get('status')}")
            checks.append(False)
        
        # Check blocks_publication == true
        if deck_item.get("blocks_publication") == True:
            print_pass("blocks_publication == true")
            checks.append(True)
        else:
            print_fail(f"blocks_publication != true: {deck_item.get('blocks_publication')}")
            checks.append(False)
        
        if all(checks):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["details"].append("Build-Ready blocker policy validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Build-Ready exception: {e}")
    
    return results


def test_workflow_lifecycle(session: TestSession, property_id: str) -> dict:
    """Test C: WORKFLOW LIFECYCLE (11 steps)."""
    print_section("C) WORKFLOW LIFECYCLE")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Step 1: Create workflow
    print_test("C.1: POST /api/steward/workflow -> 200, current_state==QUESTION_RECEIVED, version==1")
    try:
        resp = session.post("/steward/workflow", json={"property_id": property_id})
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}: {resp.text}")
            results["failed"] += 1
            results["details"].append(f"Create workflow returned {resp.status_code}")
            return results
        
        wf = resp.json()
        wf_id = wf.get("id")
        
        if wf.get("current_state") == "QUESTION_RECEIVED" and wf.get("version") == 1:
            print_pass(f"Workflow created: id={wf_id}, state=QUESTION_RECEIVED, version=1")
            results["passed"] += 1
        else:
            print_fail(f"State or version incorrect: state={wf.get('current_state')}, version={wf.get('version')}")
            results["failed"] += 1
            results["details"].append("Create workflow state/version incorrect")
            return results
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Create workflow exception: {e}")
        return results
    
    # Step 2: Advance through states
    print_test("C.2: Advance through states in order")
    states = [
        "CONTEXT_RESOLVED",
        "ANSWER_PRESENTED",
        "ACTION_RECOMMENDED",
        "ACTION_CONFIRMED",
        "PROJECT_CREATED",
        "ESTIMATE_CREATED",
        "SCENARIOS_REVIEWED",
        "READINESS_REVIEWED",
        "PACKAGE_PREVIEWED"
    ]
    
    try:
        for state in states:
            body = {"to_state": state}
            if state == "ESTIMATE_CREATED":
                body["material"] = "GAF Timberline HDZ"
            
            resp = session.post(f"/steward/workflow/{wf_id}/transition", json=body)
            if resp.status_code != 200:
                print_fail(f"Transition to {state} failed: {resp.status_code}: {resp.text}")
                results["failed"] += 1
                results["details"].append(f"Transition to {state} failed")
                return results
            
            wf = resp.json()
            if wf.get("current_state") == state:
                print_pass(f"Transitioned to {state}")
            else:
                print_fail(f"Expected state {state}, got {wf.get('current_state')}")
                results["failed"] += 1
                results["details"].append(f"State mismatch at {state}")
                return results
        
        # Check estimate_snapshot.price_book_version after ESTIMATE_CREATED
        if wf.get("estimate_snapshot", {}).get("price_book_version") == "2026.07.0":
            print_pass("estimate_snapshot.price_book_version == '2026.07.0'")
        else:
            print_fail(f"price_book_version incorrect: {wf.get('estimate_snapshot', {}).get('price_book_version')}")
            results["failed"] += 1
            results["details"].append("Price book version incorrect")
        
        # Check contractor_package_version and redaction_settings after PACKAGE_PREVIEWED
        if wf.get("contractor_package_version"):
            print_pass(f"contractor_package_version present: {wf.get('contractor_package_version')}")
        else:
            print_fail("contractor_package_version missing")
            results["failed"] += 1
            results["details"].append("Contractor package version missing")
        
        if wf.get("redaction_settings", {}).get("remove_personal_info") == True:
            print_pass("redaction_settings.remove_personal_info == true")
        else:
            print_fail(f"redaction_settings incorrect: {wf.get('redaction_settings')}")
            results["failed"] += 1
            results["details"].append("Redaction settings incorrect")
        
        results["passed"] += 1
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"State transition exception: {e}")
        return results
    
    # Step 3: Illegal transition
    print_test("C.3: Illegal transition to QUESTION_RECEIVED -> 409 ILLEGAL_TRANSITION")
    try:
        resp = session.post(f"/steward/workflow/{wf_id}/transition", json={"to_state": "QUESTION_RECEIVED"})
        if resp.status_code == 409:
            data = resp.json()
            if data.get("detail", {}).get("error_code") == "ILLEGAL_TRANSITION":
                print_pass("Illegal transition correctly blocked with ILLEGAL_TRANSITION")
                results["passed"] += 1
            else:
                print_fail(f"Wrong error code: {data.get('detail', {}).get('error_code')}")
                results["failed"] += 1
                results["details"].append("Illegal transition wrong error code")
        else:
            print_fail(f"Expected 409, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Illegal transition returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Illegal transition exception: {e}")
    
    # Step 4: Premature publish (without acknowledging deck)
    print_test("C.4: Premature publish without acknowledging deck -> 409 PUBLICATION_BLOCKED")
    try:
        resp = session.post(f"/steward/workflow/{wf_id}/publish", json={
            "approval": True,
            "property_id": property_id,
            "idempotency_key": "k1"
        })
        if resp.status_code == 409:
            data = resp.json()
            detail = data.get("detail", {})
            if detail.get("error_code") == "PUBLICATION_BLOCKED":
                print_pass("Publication correctly blocked with PUBLICATION_BLOCKED")
                if "RDY-DECK-CONDITION" in detail.get("blocking_item_ids", []):
                    print_pass("blocking_item_ids contains 'RDY-DECK-CONDITION'")
                    results["passed"] += 1
                else:
                    print_fail(f"RDY-DECK-CONDITION not in blocking_item_ids: {detail.get('blocking_item_ids')}")
                    results["failed"] += 1
                    results["details"].append("Blocking item ID incorrect")
            else:
                print_fail(f"Wrong error code: {detail.get('error_code')}")
                results["failed"] += 1
                results["details"].append("Premature publish wrong error code")
        else:
            print_fail(f"Expected 409, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Premature publish returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Premature publish exception: {e}")
    
    # Step 5: Acknowledge deck condition
    print_test("C.5: POST /api/steward/workflow/{id}/acknowledge -> 200")
    try:
        resp = session.post(f"/steward/workflow/{wf_id}/acknowledge", json={"item_id": "RDY-DECK-CONDITION"})
        if resp.status_code == 200:
            wf = resp.json()
            if "RDY-DECK-CONDITION" in wf.get("acknowledged_blockers", []):
                print_pass("RDY-DECK-CONDITION acknowledged")
                results["passed"] += 1
            else:
                print_fail(f"RDY-DECK-CONDITION not in acknowledged_blockers: {wf.get('acknowledged_blockers')}")
                results["failed"] += 1
                results["details"].append("Acknowledgment not recorded")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Acknowledge returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Acknowledge exception: {e}")
    
    # Step 6: Transition to PUBLICATION_APPROVED
    print_test("C.6: POST /transition to PUBLICATION_APPROVED -> 200")
    try:
        resp = session.post(f"/steward/workflow/{wf_id}/transition", json={"to_state": "PUBLICATION_APPROVED"})
        if resp.status_code == 200:
            wf = resp.json()
            if wf.get("current_state") == "PUBLICATION_APPROVED":
                print_pass("Transitioned to PUBLICATION_APPROVED")
                results["passed"] += 1
            else:
                print_fail(f"State incorrect: {wf.get('current_state')}")
                results["failed"] += 1
                results["details"].append("PUBLICATION_APPROVED state incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"PUBLICATION_APPROVED transition returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"PUBLICATION_APPROVED exception: {e}")
    
    # Step 7: Publish
    print_test("C.7: POST /publish with approval -> 200, status=='published'")
    try:
        resp = session.post(f"/steward/workflow/{wf_id}/publish", json={
            "approval": True,
            "property_id": property_id,
            "idempotency_key": "k1"
        })
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "published":
                print_pass("status == 'published'")
                opp_id = data.get("opportunity_id")
                if opp_id:
                    print_info(f"Captured opportunity_id: {opp_id}")
                    results["passed"] += 1
                else:
                    print_fail("opportunity_id missing")
                    results["failed"] += 1
                    results["details"].append("opportunity_id missing")
            else:
                print_fail(f"status != 'published': {data.get('status')}")
                results["failed"] += 1
                results["details"].append("Publish status incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}: {resp.text}")
            results["failed"] += 1
            results["details"].append(f"Publish returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Publish exception: {e}")
    
    # Step 8: Idempotent replay
    print_test("C.8: Idempotent replay with same idempotency_key -> 200, idempotent_replay==true")
    try:
        resp = session.post(f"/steward/workflow/{wf_id}/publish", json={
            "approval": True,
            "property_id": property_id,
            "idempotency_key": "k1"
        })
        if resp.status_code == 200:
            data = resp.json()
            if data.get("idempotent_replay") == True:
                print_pass("idempotent_replay == true")
                if data.get("opportunity_id") == opp_id:
                    print_pass(f"opportunity_id matches: {opp_id}")
                    results["passed"] += 1
                else:
                    print_fail(f"opportunity_id mismatch: {data.get('opportunity_id')} != {opp_id}")
                    results["failed"] += 1
                    results["details"].append("Idempotent replay opportunity_id mismatch")
            else:
                print_fail(f"idempotent_replay != true: {data.get('idempotent_replay')}")
                results["failed"] += 1
                results["details"].append("Idempotent replay flag incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Idempotent replay returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Idempotent replay exception: {e}")
    
    # Step 9: Resume (GET workflow)
    print_test("C.9: GET /api/steward/workflow/{id} -> 200, current_state==OPPORTUNITY_PUBLISHED")
    try:
        resp = session.get(f"/steward/workflow/{wf_id}")
        if resp.status_code == 200:
            wf = resp.json()
            if wf.get("current_state") == "OPPORTUNITY_PUBLISHED":
                print_pass("current_state == 'OPPORTUNITY_PUBLISHED'")
                results["passed"] += 1
            else:
                print_fail(f"current_state != 'OPPORTUNITY_PUBLISHED': {wf.get('current_state')}")
                results["failed"] += 1
                results["details"].append("Resume state incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Resume returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Resume exception: {e}")
    
    # Step 10: Cancel a new workflow
    print_test("C.10: Create new workflow and cancel -> 200, current_state==CANCELLED")
    try:
        resp = session.post("/steward/workflow", json={"property_id": property_id})
        if resp.status_code != 200:
            print_fail(f"Create new workflow failed: {resp.status_code}")
            results["failed"] += 1
            results["details"].append("Create new workflow for cancel failed")
        else:
            new_wf = resp.json()
            new_wf_id = new_wf.get("id")
            
            resp = session.post(f"/steward/workflow/{new_wf_id}/cancel", json={"reason": "test"})
            if resp.status_code == 200:
                wf = resp.json()
                if wf.get("current_state") == "CANCELLED":
                    print_pass("current_state == 'CANCELLED'")
                    results["passed"] += 1
                else:
                    print_fail(f"current_state != 'CANCELLED': {wf.get('current_state')}")
                    results["failed"] += 1
                    results["details"].append("Cancel state incorrect")
            else:
                print_fail(f"Expected 200, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Cancel returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Cancel exception: {e}")
    
    # Step 11: Expiry
    print_test("C.11: Create workflow with expires_in_seconds=0 -> 200, current_state==EXPIRED")
    try:
        resp = session.post("/steward/workflow", json={"property_id": property_id, "expires_in_seconds": 0})
        if resp.status_code != 200:
            print_fail(f"Create expiring workflow failed: {resp.status_code}")
            results["failed"] += 1
            results["details"].append("Create expiring workflow failed")
        else:
            exp_wf = resp.json()
            exp_wf_id = exp_wf.get("id")
            
            resp = session.get(f"/steward/workflow/{exp_wf_id}")
            if resp.status_code == 200:
                wf = resp.json()
                if wf.get("current_state") == "EXPIRED":
                    print_pass("current_state == 'EXPIRED'")
                    results["passed"] += 1
                else:
                    print_fail(f"current_state != 'EXPIRED': {wf.get('current_state')}")
                    results["failed"] += 1
                    results["details"].append("Expiry state incorrect")
            else:
                print_fail(f"Expected 200, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Expiry GET returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Expiry exception: {e}")
    
    return results


def test_security_isolation(session: TestSession, wf_id: str) -> dict:
    """Test D: SECURITY / ISOLATION."""
    print_section("D) SECURITY / ISOLATION")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test D.1: Contractor access
    print_test("D.1: Contractor access to workflow endpoints -> 403")
    contractor_session = TestSession()
    if contractor_session.login(CONTRACTOR_EMAIL, CONTRACTOR_PASSWORD):
        try:
            # GET /api/steward/workflow
            resp = contractor_session.get("/steward/workflow")
            if resp.status_code == 403:
                print_pass("Contractor GET /steward/workflow returns 403")
                results["passed"] += 1
            else:
                print_fail(f"Expected 403, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Contractor workflow list returned {resp.status_code}")
            
            # GET /api/steward/workflow/{id}
            resp = contractor_session.get(f"/steward/workflow/{wf_id}")
            if resp.status_code in (403, 404):
                print_pass(f"Contractor GET /steward/workflow/{{id}} returns {resp.status_code}")
                results["passed"] += 1
            else:
                print_fail(f"Expected 403 or 404, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Contractor workflow get returned {resp.status_code}")
        
        except Exception as e:
            print_fail(f"Exception: {e}")
            results["failed"] += 1
            results["details"].append(f"Contractor access exception: {e}")
        finally:
            contractor_session.logout()
    else:
        print_fail("Could not login as contractor")
        results["failed"] += 1
        results["details"].append("Contractor login failed")
    
    # Test D.2: Unauthenticated access
    print_test("D.2: Unauthenticated access -> 401")
    unauth_session = requests.Session()
    try:
        endpoints = [
            "/steward/workflow",
            "/steward/context"
        ]
        
        for endpoint in endpoints:
            resp = unauth_session.get(f"{BACKEND_URL}{endpoint}", timeout=30)
            if resp.status_code == 401:
                print_pass(f"Unauthenticated GET {endpoint} returns 401")
                results["passed"] += 1
            else:
                print_fail(f"Expected 401 for {endpoint}, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Unauth {endpoint} returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Unauth access exception: {e}")
    
    # Test D.3: Anti-bypass (client cannot bypass readiness check)
    print_test("D.3: Anti-bypass - client cannot bypass readiness with fabricated fields")
    try:
        # Create a fresh workflow
        resp = session.post("/steward/workflow", json={"property_id": "test-prop"})
        if resp.status_code != 200:
            print_fail(f"Create workflow failed: {resp.status_code}")
            results["failed"] += 1
            results["details"].append("Anti-bypass workflow creation failed")
            return results
        
        bypass_wf = resp.json()
        bypass_wf_id = bypass_wf.get("id")
        
        # Advance to PACKAGE_PREVIEWED without acknowledging deck
        states = [
            "CONTEXT_RESOLVED", "ANSWER_PRESENTED", "ACTION_RECOMMENDED",
            "ACTION_CONFIRMED", "PROJECT_CREATED", "ESTIMATE_CREATED",
            "SCENARIOS_REVIEWED", "READINESS_REVIEWED", "PACKAGE_PREVIEWED"
        ]
        
        for state in states:
            body = {"to_state": state}
            if state == "ESTIMATE_CREATED":
                body["material"] = "GAF Timberline HDZ"
            resp = session.post(f"/steward/workflow/{bypass_wf_id}/transition", json=body)
            if resp.status_code != 200:
                print_fail(f"Transition to {state} failed: {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Anti-bypass transition to {state} failed")
                return results
        
        # Try to publish with fabricated readiness field
        resp = session.post(f"/steward/workflow/{bypass_wf_id}/publish", json={
            "approval": True,
            "property_id": "test-prop",
            "idempotency_key": "bypass-test",
            "readiness": {"can_publish": True}  # Fabricated field
        })
        
        if resp.status_code == 409:
            data = resp.json()
            if data.get("detail", {}).get("error_code") == "PUBLICATION_BLOCKED":
                print_pass("Anti-bypass: server recomputes readiness, still blocks with PUBLICATION_BLOCKED")
                results["passed"] += 1
            else:
                print_fail(f"Wrong error code: {data.get('detail', {}).get('error_code')}")
                results["failed"] += 1
                results["details"].append("Anti-bypass wrong error code")
        else:
            print_fail(f"Expected 409, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Anti-bypass returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Anti-bypass exception: {e}")
    
    return results


def test_regression(session: TestSession) -> dict:
    """Test E: REGRESSION (Batch 1 + H-012)."""
    print_section("E) REGRESSION (Batch 1 + H-012)")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # E.1: GET /api/steward/fixture
    print_test("E.1: GET /api/steward/fixture -> 200, is_fixture==true")
    try:
        resp = session.get("/steward/fixture")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("is_fixture") == True:
                print_pass("is_fixture == true")
                results["passed"] += 1
            else:
                print_fail(f"is_fixture != true: {data.get('is_fixture')}")
                results["failed"] += 1
                results["details"].append("Fixture is_fixture incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Fixture returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Fixture exception: {e}")
    
    # E.2: POST /api/steward/estimate
    print_test("E.2: POST /api/steward/estimate -> 200, price_book_version=='2026.07.0'")
    try:
        resp = session.post("/steward/estimate", json={"material": "GAF Timberline HDZ"})
        if resp.status_code == 200:
            data = resp.json()
            if data.get("price_book_version") == "2026.07.0":
                print_pass("price_book_version == '2026.07.0'")
                if data.get("price_provenance", {}).get("price_source") == "HABITAT_GOVERNED_PRICE_BOOK":
                    print_pass("price_provenance.price_source == 'HABITAT_GOVERNED_PRICE_BOOK'")
                    results["passed"] += 1
                else:
                    print_fail(f"price_source incorrect: {data.get('price_provenance', {}).get('price_source')}")
                    results["failed"] += 1
                    results["details"].append("Estimate price_source incorrect")
            else:
                print_fail(f"price_book_version != '2026.07.0': {data.get('price_book_version')}")
                results["failed"] += 1
                results["details"].append("Estimate price_book_version incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Estimate returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Estimate exception: {e}")
    
    # E.3: GET /api/steward/contractor-package
    print_test("E.3: GET /api/steward/contractor-package -> 200, no raw PII, only doc_01")
    try:
        resp = session.get("/steward/contractor-package")
        if resp.status_code == 200:
            data = resp.json()
            payload_str = json.dumps(data)
            
            # Check no raw PII
            forbidden = ["Morgan", "alex@stratexhabitat.com", "(512) 555-0101"]
            leaks = [val for val in forbidden if val in payload_str]
            
            if not leaks:
                print_pass("No raw PII leaked")
                
                # Check shared_documents only has doc_01
                docs = data.get("shared_documents", [])
                doc_ids = [d.get("id") for d in docs]
                if "doc_01" in doc_ids and "doc_02" not in doc_ids:
                    print_pass("shared_documents only contains doc_01")
                    results["passed"] += 1
                else:
                    print_fail(f"Document filtering incorrect: {doc_ids}")
                    results["failed"] += 1
                    results["details"].append("Contractor package document filtering incorrect")
            else:
                print_fail(f"PII leaked: {leaks}")
                results["failed"] += 1
                results["details"].append(f"Contractor package PII leaked: {leaks}")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Contractor package returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Contractor package exception: {e}")
    
    # E.4: POST /api/steward/ask
    print_test("E.4: POST /api/steward/ask")
    try:
        # Valid question
        resp = session.post("/steward/ask", json={"question": "Do I need a new roof?"})
        if resp.status_code == 200:
            data = resp.json()
            if all(k in data for k in ["level_1_direct_answer", "level_2_why_this_matters", "level_3_supporting_information", "level_4_trace"]):
                print_pass("Valid roof question returns 200 with all levels")
                results["passed"] += 1
            else:
                print_fail(f"Missing required keys: {list(data.keys())}")
                results["failed"] += 1
                results["details"].append("Ask missing required keys")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Ask valid question returned {resp.status_code}")
        
        # Invalid question
        resp = session.post("/steward/ask", json={"question": "What is the weather?"})
        if resp.status_code == 400:
            print_pass("Non-roof question returns 400")
            results["passed"] += 1
        else:
            print_fail(f"Expected 400, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Ask invalid question returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Ask exception: {e}")
    
    return results


def main():
    """Main test runner."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}STRATEX HABITAT H-013 Batch 2 Test Suite{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Homeowner: {HOMEOWNER_EMAIL}")
    print(f"Contractor: {CONTRACTOR_EMAIL}")
    
    # Login as homeowner
    homeowner_session = TestSession()
    if not homeowner_session.login(HOMEOWNER_EMAIL, HOMEOWNER_PASSWORD):
        print(f"\n{RED}FATAL: Could not login as homeowner. Aborting tests.{RESET}")
        return 1
    
    # Run all tests
    all_results = {}
    property_id = None
    wf_id = None
    
    try:
        # Test A: Passport projection boundary
        proj_results = test_passport_projection_boundary(homeowner_session)
        all_results["projection_boundary"] = proj_results
        property_id = proj_results.get("property_id")
        
        # Test B: Build-Ready blocker policy
        all_results["build_ready"] = test_build_ready_blocker_policy(homeowner_session)
        
        # Test C: Workflow lifecycle (only if we have property_id)
        if property_id:
            workflow_results = test_workflow_lifecycle(homeowner_session, property_id)
            all_results["workflow_lifecycle"] = workflow_results
            
            # Get a workflow ID for security tests (create a simple one)
            resp = homeowner_session.post("/steward/workflow", json={"property_id": property_id})
            if resp.status_code == 200:
                wf_id = resp.json().get("id")
        else:
            print(f"{RED}Skipping workflow lifecycle tests - no property_id{RESET}")
            all_results["workflow_lifecycle"] = {"passed": 0, "failed": 1, "details": ["No property_id"]}
        
        # Test D: Security / Isolation
        if wf_id:
            all_results["security_isolation"] = test_security_isolation(homeowner_session, wf_id)
        else:
            print(f"{RED}Skipping security tests - no workflow_id{RESET}")
            all_results["security_isolation"] = {"passed": 0, "failed": 1, "details": ["No workflow_id"]}
        
        # Test E: Regression
        all_results["regression"] = test_regression(homeowner_session)
    
    finally:
        homeowner_session.logout()
    
    # Print summary
    print_section("TEST SUMMARY")
    total_passed = 0
    total_failed = 0
    
    for test_name, results in all_results.items():
        passed = results["passed"]
        failed = results["failed"]
        total_passed += passed
        total_failed += failed
        
        status = f"{GREEN}✓{RESET}" if failed == 0 else f"{RED}✗{RESET}"
        print(f"{status} {test_name}: {passed} passed, {failed} failed")
        
        if results["details"]:
            for detail in results["details"]:
                print(f"    - {detail}")
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"Total: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print(f"{GREEN}ALL TESTS PASSED ✓{RESET}")
        return 0
    else:
        print(f"{RED}SOME TESTS FAILED ✗{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
