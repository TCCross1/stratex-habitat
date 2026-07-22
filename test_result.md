#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: >
  Habitat H-013 Production Hardening — Wave 1. Recover backend runtime and advance the
  existing H-012 Home Steward vertical slice. Batch 1 delivers critical runtime + security
  gates: CI dependency repair, fixture governance, governed price-book, and backend-enforced
  contractor-package redaction. (Passport projection / Build-Ready / persistence deferred to Batch 2.)

backend:
  - task: "H-013 #1 Backend runtime / dependency pin (cryptography + pyOpenSSL GEN_EMAIL fix)"
    implemented: true
    working: true
    file: "backend/requirements.txt"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "Pinned cryptography==44.0.1 + pyOpenSSL==25.1.0. Live runtime (py3.11, plain mongodb) never reproduced the crash; backend healthy HTTP 200 after restart. Crash was CI/py3.12 only."

  - task: "H-013 #4 Deterministic fixture env-gate + provenance"
    implemented: true
    working: true
    file: "backend/fixture_provider.py, backend/steward.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "/steward/fixture and /steward/context gated + tagged (is_fixture, _provenance authoritative=False). Disabled in production -> 409. Default dev keeps 200 (legacy keys preserved). Unit tests + HTTP smoke pass."
        - working: true
          agent: "testing"
          comment: "✓ VERIFIED: GET /api/steward/fixture returns HTTP 200 with is_fixture==true, _provenance.authoritative==false, and all legacy keys (passport_explanation, truth_states, unresolved_gap, authorized_owner=='alex@stratexhabitat.com') present. GET /api/steward/context returns HTTP 200 with is_fixture==true and published_explanation contains all required provenance fields (source_system, source_id, version, truth_classification, timestamp, authorization_scope). Fixture gate working correctly in development environment."

  - task: "H-013 #7 Governed versioned price-book provider"
    implemented: true
    working: true
    file: "backend/pricebook.py, backend/steward.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "All roof price literals moved out of steward EST_DATA into pricebook.py (version 2026.07.0). /steward/estimate now returns price_book_version + price_provenance (governed, authoritative=False) while preserving legacy fields (pricing_date, scenarios, breakdown, cost_delta_explanation)."
        - working: true
          agent: "testing"
          comment: "✓ VERIFIED: POST /api/steward/estimate with 'GAF Timberline HDZ' returns HTTP 200 with price_book_version=='2026.07.0', price_provenance.price_source=='HABITAT_GOVERNED_PRICE_BOOK', governed==true, authoritative==false. All legacy fields present: pricing_date=='July 2026', geographic_basis contains 'Austin', scenarios, breakdown, cost_delta_explanation. POST with 'DECRA Standing Seam' returns cost_delta_explanation containing 'premium materials'. Governed price-book working correctly."

  - task: "H-013 #9 Backend-enforced contractor-package redaction"
    implemented: true
    working: true
    file: "backend/redaction.py, backend/steward.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "GET /steward/contractor-package builds internal package (real PII + internal fields) then returns redaction.redact_contractor_package(). Preview strips ALL PII/internal (email/last name/phone/exact address/owner_id/correlation_id) and exposes only shared=True docs. ?approved=true releases homeowner_contact only; internal fields still stripped. Backward-compat keys (redacted_personal_info, quantity_takeoff, shared_documents) retained as masks. HTTP smoke: 0 leaks."
        - working: true
          agent: "testing"
          comment: "✓ VERIFIED: GET /api/steward/contractor-package (preview mode) returns HTTP 200 with ZERO PII leaks - no 'Morgan', 'alex@stratexhabitat.com', '(512) 555-0101', '1420 Vista Ridge', owner_id, or correlation_id found in response. Contains redacted_personal_info mask block (values=='REDACTED'), quantity_takeoff, shared_documents with ONLY doc_01 (doc_02 correctly filtered). redaction.redaction_enforced==true, tier=='preview'. homeowner_contact correctly withheld. GET with ?approved=true returns HTTP 200 with homeowner_contact.email=='alex@stratexhabitat.com', tier=='contractor', but internal fields ('1420 Vista Ridge', correlation_id) still correctly stripped. Backend redaction security gate working perfectly."

  - task: "H-013 #10 Executable security-gate tests"
    implemented: true
    working: true
    file: "backend/tests/test_h013_security.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "9 unit tests (price-book provenance, fixture gate incl production-disabled, redaction preview/approved) all pass."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "H-013 #9 Backend-enforced contractor-package redaction"
    - "H-013 #4 Deterministic fixture env-gate + provenance"
    - "H-013 #7 Governed versioned price-book provider"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: >
        Batch 1 backend changes complete. Please verify (homeowner alex@stratexhabitat.com / Demo123!):
        (1) GET /api/steward/contractor-package (no query) returns NO homeowner PII (no 'Morgan',
        no email 'alex@stratexhabitat.com', no phone '(512) 555-0101', no exact address '1420 Vista Ridge',
        no owner_id/correlation_id) and shared_documents contains ONLY doc_01; redaction.redaction_enforced==true, tier=='preview'.
        (2) GET /api/steward/contractor-package?approved=true DOES return homeowner_contact.email but STILL no
        exact address / correlation_id (internal fields stripped); tier=='contractor'.
        (3) POST /api/steward/estimate {"material":"GAF Timberline HDZ"} returns price_book_version and
        price_provenance.price_source=='HABITAT_GOVERNED_PRICE_BOOK' with governed==true, authoritative==false,
        while still returning pricing_date 'July 2026', scenarios, breakdown, cost_delta_explanation.
        (4) GET /api/steward/fixture and /api/steward/context are 200 with is_fixture==true and
        _provenance.authoritative==false (default dev env). Tenant isolation: contractor (horizon@stratexhabitat.com)
        gets 403; unauthenticated gets 401.
        (5) Regression: existing Home Steward endpoints (ask/recommendation/confirm/scenarios/readiness/publish/memory)
        still behave as before. Do NOT toggle HABITAT_ENABLE_FIXTURES on the live server.
    - agent: "testing"
      message: >
        ✅ ALL H-013 BATCH 1 SECURITY GATES VERIFIED (19/19 tests passed):
        
        SECURITY GATE #9 (Contractor-Package Redaction): ✓ PASS
        - Preview mode: Zero PII leaks, all sensitive data redacted, only shared documents exposed
        - Approved mode: Contact info released but internal fields still protected
        
        SECURITY GATE #7 (Governed Price-Book): ✓ PASS
        - Price-book version 2026.07.0 with full provenance metadata
        - Legacy fields preserved, cost delta explanations working
        
        SECURITY GATE #4 (Fixture Gate + Provenance): ✓ PASS
        - Fixtures properly tagged as non-authoritative demo data
        - All provenance fields present and correct
        
        TENANT ISOLATION / AUTH: ✓ PASS
        - Contractor correctly blocked (403) from steward endpoints
        - Unauthenticated requests correctly rejected (401)
        
        REGRESSION (H-012 Endpoints): ✓ PASS
        - All 8 existing endpoints working: ask, recommendation, scenarios, readiness, confirm, publish, memory
        
        Backend is production-ready for H-013 Batch 1 deployment.

