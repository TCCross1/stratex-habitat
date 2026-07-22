#!/usr/bin/env python3
"""
STRATEX HABITAT H-013 Batch 1 Security Gates Test Suite

Tests all security gates and regression endpoints for the Home Steward vertical slice.
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
                # Check if token is returned in response
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


def check_no_leaks(payload: Any, forbidden_values: list, test_name: str) -> bool:
    """Check that none of the forbidden values appear in the payload."""
    payload_str = json.dumps(payload, default=str)
    leaks = []
    for val in forbidden_values:
        if val and val in payload_str:
            leaks.append(val)
    
    if leaks:
        print_fail(f"{test_name}: PII/internal values leaked: {leaks}")
        return False
    else:
        print_pass(f"{test_name}: No PII/internal leaks detected")
        return True


def test_contractor_package_redaction(session: TestSession) -> dict:
    """Test security gate #9: Contractor-package redaction."""
    print_section("1. CONTRACTOR-PACKAGE REDACTION (Security Gate #9)")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test 1a: Preview mode (no query params)
    print_test("1a. GET /api/steward/contractor-package (preview mode)")
    try:
        resp = session.get("/steward/contractor-package")
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Preview mode returned {resp.status_code}")
        else:
            data = resp.json()
            print_info(f"Response keys: {list(data.keys())}")
            
            # Check for forbidden values
            forbidden = [
                "Morgan",
                "alex@stratexhabitat.com",
                "(512) 555-0101",
                "1420 Vista Ridge",
                "correlation_id",
            ]
            # Also check for owner_id if we can get it
            if session.user and "id" in session.user:
                forbidden.append(session.user["id"])
            
            # Check no raw PII leaks
            no_leaks = check_no_leaks(data, forbidden, "Preview mode PII check")
            
            # Check for required fields
            checks = []
            if "redacted_personal_info" in data:
                print_pass("Contains 'redacted_personal_info' mask block")
                checks.append(True)
                # Verify it's actually masked
                rpi = data["redacted_personal_info"]
                if rpi.get("email") == "REDACTED" and rpi.get("phone") == "REDACTED":
                    print_pass("Personal info is properly masked to 'REDACTED'")
                    checks.append(True)
                else:
                    print_fail(f"Personal info not properly masked: {rpi}")
                    checks.append(False)
            else:
                print_fail("Missing 'redacted_personal_info' block")
                checks.append(False)
            
            if "quantity_takeoff" in data:
                print_pass("Contains 'quantity_takeoff'")
                checks.append(True)
            else:
                print_fail("Missing 'quantity_takeoff'")
                checks.append(False)
            
            if "shared_documents" in data:
                print_pass("Contains 'shared_documents'")
                docs = data["shared_documents"]
                # Should only contain doc_01
                doc_ids = [d.get("id") for d in docs]
                if "doc_01" in doc_ids and "doc_02" not in doc_ids:
                    print_pass("Only shared document (doc_01) is present, unshared (doc_02) is absent")
                    checks.append(True)
                else:
                    print_fail(f"Document filtering incorrect. Found: {doc_ids}")
                    checks.append(False)
            else:
                print_fail("Missing 'shared_documents'")
                checks.append(False)
            
            if "redaction" in data:
                redaction = data["redaction"]
                if redaction.get("redaction_enforced") == True:
                    print_pass("redaction.redaction_enforced == true")
                    checks.append(True)
                else:
                    print_fail(f"redaction.redaction_enforced != true: {redaction.get('redaction_enforced')}")
                    checks.append(False)
                
                if redaction.get("tier") == "preview":
                    print_pass("redaction.tier == 'preview'")
                    checks.append(True)
                else:
                    print_fail(f"redaction.tier != 'preview': {redaction.get('tier')}")
                    checks.append(False)
            else:
                print_fail("Missing 'redaction' block")
                checks.append(False)
            
            # Check that homeowner_contact is NOT present
            if "homeowner_contact" not in data:
                print_pass("homeowner_contact is NOT present (correctly withheld)")
                checks.append(True)
            else:
                print_fail("homeowner_contact should not be present in preview mode")
                checks.append(False)
            
            if all(checks) and no_leaks:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append("Preview mode validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Preview mode exception: {e}")
    
    # Test 1b: Approved mode
    print_test("1b. GET /api/steward/contractor-package?approved=true")
    try:
        resp = session.get("/steward/contractor-package", params={"approved": "true"})
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Approved mode returned {resp.status_code}")
        else:
            data = resp.json()
            print_info(f"Response keys: {list(data.keys())}")
            
            checks = []
            
            # homeowner_contact SHOULD be present now
            if "homeowner_contact" in data:
                print_pass("homeowner_contact IS present")
                contact = data["homeowner_contact"]
                if contact.get("email") == "alex@stratexhabitat.com":
                    print_pass("homeowner_contact.email == 'alex@stratexhabitat.com'")
                    checks.append(True)
                else:
                    print_fail(f"homeowner_contact.email incorrect: {contact.get('email')}")
                    checks.append(False)
            else:
                print_fail("homeowner_contact should be present in approved mode")
                checks.append(False)
            
            # Check redaction tier
            if "redaction" in data:
                tier = data["redaction"].get("tier")
                if tier == "contractor":
                    print_pass("redaction.tier == 'contractor'")
                    checks.append(True)
                else:
                    print_fail(f"redaction.tier != 'contractor': {tier}")
                    checks.append(False)
            else:
                print_fail("Missing 'redaction' block")
                checks.append(False)
            
            # Internal fields must STILL be stripped
            forbidden_internal = [
                "1420 Vista Ridge",  # exact address
                "correlation_id",
            ]
            no_internal_leaks = check_no_leaks(data, forbidden_internal, "Approved mode internal field check")
            
            if all(checks) and no_internal_leaks:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append("Approved mode validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Approved mode exception: {e}")
    
    return results


def test_governed_pricebook(session: TestSession) -> dict:
    """Test security gate #7: Governed price-book."""
    print_section("2. GOVERNED PRICE-BOOK (Security Gate #7)")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test 2a: GAF Timberline HDZ
    print_test("2a. POST /api/steward/estimate with GAF Timberline HDZ")
    try:
        resp = session.post("/steward/estimate", json={"material": "GAF Timberline HDZ"})
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"GAF estimate returned {resp.status_code}")
        else:
            data = resp.json()
            checks = []
            
            # Check price_book_version
            if "price_book_version" in data:
                version = data["price_book_version"]
                if version == "2026.07.0":
                    print_pass(f"price_book_version == '2026.07.0'")
                    checks.append(True)
                else:
                    print_fail(f"price_book_version != '2026.07.0': {version}")
                    checks.append(False)
            else:
                print_fail("Missing 'price_book_version'")
                checks.append(False)
            
            # Check price_provenance
            if "price_provenance" in data:
                prov = data["price_provenance"]
                print_pass("Contains 'price_provenance'")
                
                if prov.get("price_source") == "HABITAT_GOVERNED_PRICE_BOOK":
                    print_pass("price_provenance.price_source == 'HABITAT_GOVERNED_PRICE_BOOK'")
                    checks.append(True)
                else:
                    print_fail(f"price_source incorrect: {prov.get('price_source')}")
                    checks.append(False)
                
                if prov.get("governed") == True:
                    print_pass("price_provenance.governed == true")
                    checks.append(True)
                else:
                    print_fail(f"governed != true: {prov.get('governed')}")
                    checks.append(False)
                
                if prov.get("authoritative") == False:
                    print_pass("price_provenance.authoritative == false")
                    checks.append(True)
                else:
                    print_fail(f"authoritative != false: {prov.get('authoritative')}")
                    checks.append(False)
            else:
                print_fail("Missing 'price_provenance'")
                checks.append(False)
            
            # Check legacy fields
            legacy_fields = ["pricing_date", "geographic_basis", "scenarios", "breakdown", "cost_delta_explanation"]
            for field in legacy_fields:
                if field in data:
                    print_pass(f"Legacy field '{field}' present")
                    checks.append(True)
                else:
                    print_fail(f"Missing legacy field '{field}'")
                    checks.append(False)
            
            # Verify pricing_date
            if data.get("pricing_date") == "July 2026":
                print_pass("pricing_date == 'July 2026'")
                checks.append(True)
            else:
                print_fail(f"pricing_date incorrect: {data.get('pricing_date')}")
                checks.append(False)
            
            # Verify geographic_basis contains "Austin"
            geo = data.get("geographic_basis", "")
            if "Austin" in geo:
                print_pass("geographic_basis contains 'Austin'")
                checks.append(True)
            else:
                print_fail(f"geographic_basis doesn't contain 'Austin': {geo}")
                checks.append(False)
            
            if all(checks):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append("GAF estimate validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"GAF estimate exception: {e}")
    
    # Test 2b: DECRA Standing Seam
    print_test("2b. POST /api/steward/estimate with DECRA Standing Seam")
    try:
        resp = session.post("/steward/estimate", json={"material": "DECRA Standing Seam"})
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"DECRA estimate returned {resp.status_code}")
        else:
            data = resp.json()
            
            # Check cost_delta_explanation contains "premium materials"
            delta_exp = data.get("cost_delta_explanation", "")
            if "premium materials" in delta_exp.lower():
                print_pass("cost_delta_explanation contains 'premium materials'")
                results["passed"] += 1
            else:
                print_fail(f"cost_delta_explanation doesn't contain 'premium materials': {delta_exp}")
                results["failed"] += 1
                results["details"].append("DECRA cost delta explanation incorrect")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"DECRA estimate exception: {e}")
    
    return results


def test_fixture_gate(session: TestSession) -> dict:
    """Test security gate #4: Fixture gate + provenance."""
    print_section("3. FIXTURE GATE + PROVENANCE (Security Gate #4)")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test 3a: GET /api/steward/fixture
    print_test("3a. GET /api/steward/fixture")
    try:
        resp = session.get("/steward/fixture")
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Fixture endpoint returned {resp.status_code}")
        else:
            data = resp.json()
            checks = []
            
            # Check is_fixture
            if data.get("is_fixture") == True:
                print_pass("is_fixture == true")
                checks.append(True)
            else:
                print_fail(f"is_fixture != true: {data.get('is_fixture')}")
                checks.append(False)
            
            # Check _provenance
            if "_provenance" in data:
                prov = data["_provenance"]
                print_pass("Contains '_provenance'")
                
                if prov.get("authoritative") == False:
                    print_pass("_provenance.authoritative == false")
                    checks.append(True)
                else:
                    print_fail(f"authoritative != false: {prov.get('authoritative')}")
                    checks.append(False)
            else:
                print_fail("Missing '_provenance'")
                checks.append(False)
            
            # Check legacy keys preserved
            legacy_keys = ["passport_explanation", "truth_states", "unresolved_gap", "authorized_owner"]
            for key in legacy_keys:
                if key in data:
                    print_pass(f"Legacy key '{key}' present")
                    checks.append(True)
                else:
                    print_fail(f"Missing legacy key '{key}'")
                    checks.append(False)
            
            # Check authorized_owner
            if data.get("authorized_owner") == "alex@stratexhabitat.com":
                print_pass("authorized_owner == 'alex@stratexhabitat.com'")
                checks.append(True)
            else:
                print_fail(f"authorized_owner incorrect: {data.get('authorized_owner')}")
                checks.append(False)
            
            if all(checks):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append("Fixture endpoint validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Fixture endpoint exception: {e}")
    
    # Test 3b: GET /api/steward/context
    print_test("3b. GET /api/steward/context")
    try:
        resp = session.get("/steward/context")
        if resp.status_code != 200:
            print_fail(f"Expected HTTP 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Context endpoint returned {resp.status_code}")
        else:
            data = resp.json()
            checks = []
            
            # Check is_fixture
            if data.get("is_fixture") == True:
                print_pass("is_fixture == true")
                checks.append(True)
            else:
                print_fail(f"is_fixture != true: {data.get('is_fixture')}")
                checks.append(False)
            
            # Check published_explanation has required provenance fields
            if "published_explanation" in data:
                pub_exp = data["published_explanation"]
                prov_fields = ["source_system", "source_id", "version", "truth_classification", "timestamp", "authorization_scope"]
                for field in prov_fields:
                    if field in pub_exp:
                        print_pass(f"published_explanation.{field} present")
                        checks.append(True)
                    else:
                        print_fail(f"published_explanation missing '{field}'")
                        checks.append(False)
            else:
                print_fail("Missing 'published_explanation'")
                checks.append(False)
            
            if all(checks):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append("Context endpoint validation failed")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Context endpoint exception: {e}")
    
    return results


def test_tenant_isolation(homeowner_session: TestSession) -> dict:
    """Test security gate: Tenant isolation / Auth."""
    print_section("4. TENANT ISOLATION / AUTH")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test 4a: Contractor access (should be 403)
    print_test("4a. Contractor access to steward endpoints (should be 403)")
    contractor_session = TestSession()
    if contractor_session.login(CONTRACTOR_EMAIL, CONTRACTOR_PASSWORD):
        try:
            # Test contractor-package
            resp = contractor_session.get("/steward/contractor-package")
            if resp.status_code == 403:
                print_pass("Contractor GET /steward/contractor-package returns 403")
                results["passed"] += 1
            else:
                print_fail(f"Expected 403, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Contractor contractor-package returned {resp.status_code}")
            
            # Test fixture
            resp = contractor_session.get("/steward/fixture")
            if resp.status_code == 403:
                print_pass("Contractor GET /steward/fixture returns 403")
                results["passed"] += 1
            else:
                print_fail(f"Expected 403, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"Contractor fixture returned {resp.status_code}")
        
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
    
    # Test 4b: Unauthenticated access (should be 401)
    print_test("4b. Unauthenticated access (should be 401)")
    unauth_session = requests.Session()
    try:
        endpoints = [
            "/steward/fixture",
            "/steward/context",
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
        
        # Test POST /steward/ask
        resp = unauth_session.post(f"{BACKEND_URL}/steward/ask", json={"question": "test"}, timeout=30)
        if resp.status_code == 401:
            print_pass("Unauthenticated POST /steward/ask returns 401")
            results["passed"] += 1
        else:
            print_fail(f"Expected 401 for POST /steward/ask, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Unauth POST /steward/ask returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Unauth access exception: {e}")
    
    return results


def test_regression(session: TestSession) -> dict:
    """Test regression: Existing H-012 endpoints."""
    print_section("5. REGRESSION (Existing H-012 Endpoints)")
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test 5a: POST /api/steward/ask
    print_test("5a. POST /api/steward/ask")
    try:
        # Valid question
        resp = session.post("/steward/ask", json={"question": "Do I need a new roof?"})
        if resp.status_code == 200:
            data = resp.json()
            required_keys = ["level_1_direct_answer", "level_2_why_this_matters", "level_3_supporting_information", "level_4_trace"]
            if all(k in data for k in required_keys):
                print_pass("Valid roof question returns 200 with all required levels")
                results["passed"] += 1
            else:
                print_fail(f"Missing required keys. Got: {list(data.keys())}")
                results["failed"] += 1
                results["details"].append("Ask endpoint missing required keys")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Ask valid question returned {resp.status_code}")
        
        # Invalid question (no "roof")
        resp = session.post("/steward/ask", json={"question": "What is the weather?"})
        if resp.status_code == 400:
            print_pass("Non-roof question returns 400")
            results["passed"] += 1
        else:
            print_fail(f"Expected 400 for non-roof question, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Ask invalid question returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Ask endpoint exception: {e}")
    
    # Test 5b: GET /api/steward/recommendation
    print_test("5b. GET /api/steward/recommendation")
    try:
        resp = session.get("/steward/recommendation")
        if resp.status_code == 200:
            data = resp.json()
            if "primary" in data and data["primary"].get("type") == "Schedule a focused roof inspection":
                print_pass("Recommendation returns 200 with correct primary type")
                results["passed"] += 1
            else:
                print_fail(f"Primary recommendation incorrect: {data.get('primary', {}).get('type')}")
                results["failed"] += 1
                results["details"].append("Recommendation primary type incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Recommendation returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Recommendation exception: {e}")
    
    # Test 5c: GET /api/steward/scenarios
    print_test("5c. GET /api/steward/scenarios")
    try:
        resp = session.get("/steward/scenarios")
        if resp.status_code == 200:
            data = resp.json()
            if "scenario_a" in data and "scenario_b" in data and "scenario_c" in data:
                print_pass("Scenarios returns 200 with scenario_a/b/c")
                # Check for unpromised_disclosures
                if "unpromised_disclosures" in data.get("scenario_a", {}):
                    print_pass("scenario_a contains unpromised_disclosures")
                    results["passed"] += 1
                else:
                    print_fail("scenario_a missing unpromised_disclosures")
                    results["failed"] += 1
                    results["details"].append("Scenarios missing unpromised_disclosures")
            else:
                print_fail(f"Missing scenarios. Got: {list(data.keys())}")
                results["failed"] += 1
                results["details"].append("Scenarios missing a/b/c")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Scenarios returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Scenarios exception: {e}")
    
    # Test 5d: GET /api/steward/readiness
    print_test("5d. GET /api/steward/readiness")
    try:
        resp = session.get("/steward/readiness")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("project_readiness_score") == 65:
                print_pass("Readiness returns 200 with score == 65")
                # Check for blocking item
                checklist = data.get("priority_checklist", [])
                blocking_item = next((item for item in checklist if item.get("blocks_publication") == True), None)
                if blocking_item and "Existing Deck & Underlayment Condition" in blocking_item.get("item", ""):
                    print_pass("Found blocking item 'Existing Deck & Underlayment Condition'")
                    results["passed"] += 1
                else:
                    print_fail("Blocking item not found or incorrect")
                    results["failed"] += 1
                    results["details"].append("Readiness blocking item incorrect")
            else:
                print_fail(f"Readiness score incorrect: {data.get('project_readiness_score')}")
                results["failed"] += 1
                results["details"].append("Readiness score incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Readiness returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Readiness exception: {e}")
    
    # Test 5e: POST /api/steward/confirm
    print_test("5e. POST /api/steward/confirm")
    try:
        # First get fixture to get property_id
        fixture_resp = session.get("/steward/fixture")
        if fixture_resp.status_code == 200:
            property_id = fixture_resp.json().get("property_id", "villa-horizon-uuid")
        else:
            property_id = "villa-horizon-uuid"
        
        resp = session.post("/steward/confirm", json={
            "property_id": property_id,
            "action": "Explore Roof Replacement"
        })
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "confirmed":
                print_pass("Confirm returns 200 with status 'confirmed'")
                results["passed"] += 1
            else:
                print_fail(f"Status incorrect: {data.get('status')}")
                results["failed"] += 1
                results["details"].append("Confirm status incorrect")
        else:
            print_fail(f"Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"Confirm returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Confirm exception: {e}")
    
    # Test 5f: POST /api/steward/publish
    print_test("5f. POST /api/steward/publish")
    try:
        # Get property_id from fixture
        fixture_resp = session.get("/steward/fixture")
        if fixture_resp.status_code == 200:
            property_id = fixture_resp.json().get("property_id", "villa-horizon-uuid")
        else:
            property_id = "villa-horizon-uuid"
        
        # Get scenario_id from design scenarios
        scenarios_resp = session.get("/design/scenarios", params={"property_id": property_id})
        scenario_id = None
        if scenarios_resp.status_code == 200:
            scenarios = scenarios_resp.json()
            # Find "Project: Roof Replacement" scenario
            for sc in scenarios:
                if sc.get("name") == "Project: Roof Replacement":
                    scenario_id = sc.get("id")
                    break
        
        if not scenario_id:
            print_info("No 'Project: Roof Replacement' scenario found, using placeholder")
            scenario_id = "test-scenario-id"
        
        resp = session.post("/steward/publish", json={
            "property_id": property_id,
            "scenario_id": scenario_id,
            "timeline_preference": "30 days",
            "budget_preference": "Premium",
            "shared_document_ids": ["doc_01"],
            "remove_personal_info": True
        })
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "published":
                print_pass("Publish returns 200 with status 'published'")
                results["passed"] += 1
            else:
                print_fail(f"Status incorrect: {data.get('status')}")
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
    
    # Test 5g: GET and POST /api/steward/memory
    print_test("5g. GET and POST /api/steward/memory")
    try:
        # GET memory
        resp = session.get("/steward/memory")
        if resp.status_code == 200:
            data = resp.json()
            print_pass("GET /steward/memory returns 200")
            
            # POST memory update
            resp = session.post("/steward/memory", json={
                "project_memories": {"test_key": "test_value"}
            })
            if resp.status_code == 200:
                print_pass("POST /steward/memory returns 200 (memory round-trip successful)")
                results["passed"] += 1
            else:
                print_fail(f"POST memory expected 200, got {resp.status_code}")
                results["failed"] += 1
                results["details"].append(f"POST memory returned {resp.status_code}")
        else:
            print_fail(f"GET memory expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["details"].append(f"GET memory returned {resp.status_code}")
    
    except Exception as e:
        print_fail(f"Exception: {e}")
        results["failed"] += 1
        results["details"].append(f"Memory exception: {e}")
    
    return results


def main():
    """Main test runner."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}STRATEX HABITAT H-013 Batch 1 Security Gates Test Suite{RESET}")
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
    
    try:
        all_results["contractor_package"] = test_contractor_package_redaction(homeowner_session)
        all_results["pricebook"] = test_governed_pricebook(homeowner_session)
        all_results["fixture"] = test_fixture_gate(homeowner_session)
        all_results["tenant_isolation"] = test_tenant_isolation(homeowner_session)
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
