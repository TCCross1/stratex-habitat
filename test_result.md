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

  - task: "H-013 Batch 2 #5 Versioned read-only Passport projection boundary (adapter + provider modes)"
    implemented: true
    working: true
    file: "backend/passport_projection.py, backend/steward.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "GET /steward/context now served ONLY via PassportProjectionAdapter. Dev mode returns authoritative:false + provider_mode + contract_version 1.0.0 + seed id, preserving legacy keys. Production fails safe (503) when HABITAT_PROJECTION_BASE_URL unset (no fixture fallback) - proven by 14 unit tests. Contract/tenant/property/schema validation + stale detection."
        - working: true
          agent: "testing"
          comment: "✓ VERIFIED: GET /api/steward/context returns HTTP 200 with complete _projection envelope: provider_mode=='development', authoritative==false, contract_version=='1.0.0', fixture_or_seed_identifier=='dev-seed-roof-2026.07', generated_at present. All required top-level keys present: property_identity (with id captured), published_explanation, property_dna_projection, seasonal_context. Passport projection boundary working correctly."

  - task: "H-013 Batch 2 Phase 5 Build-Ready blocker policy (HARD/CONDITIONAL/WARNING/INFORMATIONAL)"
    implemented: true
    working: true
    file: "backend/readiness_policy.py, backend/steward.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "GET /steward/readiness now policy-driven. Deck condition = CONDITIONAL_BLOCKER (blocks until acknowledged). Backward-compatible: score 65, deck status MISSING, blocks_publication true. 6 unit tests."
        - working: true
          agent: "testing"
          comment: "✓ VERIFIED: GET /api/steward/readiness returns HTTP 200 with project_readiness_score==65. 'Existing Deck & Underlayment Condition' item found with classification=='CONDITIONAL_BLOCKER', status=='MISSING', blocks_publication==true. Build-Ready blocker policy working correctly."

  - task: "H-013 Batch 2 Phases 6-10 Persistent Steward workflow + publication gate + idempotency + audit + indexes"
    implemented: true
    working: true
    file: "backend/workflow.py, backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "steward_workflows collection + explicit state machine + optimistic concurrency (version) + idempotency replay. Publish gate recomputes readiness server-side (client cannot bypass), blocks on unresolved hard/unacknowledged conditional, requires approval+project+estimate+package+redaction; atomic single-publish claim prevents double publish; compensating rollback if audit/opportunity persistence fails. Immutable audit_events. Indexes ensured at startup. 10 unit tests + full HTTP smoke (create->journey->blocked->ack->publish->idempotent replay->resume->cancel->expiry->contractor 403) PASS."
        - working: true
          agent: "testing"
          comment: "✓ VERIFIED ALL 11 WORKFLOW LIFECYCLE STEPS: (1) POST /api/steward/workflow creates workflow with current_state==QUESTION_RECEIVED, version==1. (2) Successfully transitioned through all 9 states (CONTEXT_RESOLVED, ANSWER_PRESENTED, ACTION_RECOMMENDED, ACTION_CONFIRMED, PROJECT_CREATED, ESTIMATE_CREATED with material 'GAF Timberline HDZ', SCENARIOS_REVIEWED, READINESS_REVIEWED, PACKAGE_PREVIEWED). After ESTIMATE_CREATED: estimate_snapshot.price_book_version=='2026.07.0'. After PACKAGE_PREVIEWED: contractor_package_version present, redaction_settings.remove_personal_info==true. (3) Illegal transition to QUESTION_RECEIVED correctly blocked with 409 ILLEGAL_TRANSITION. (4) Premature publish without acknowledging deck correctly blocked with 409 PUBLICATION_BLOCKED, blocking_item_ids contains 'RDY-DECK-CONDITION'. (5) POST /acknowledge with item_id 'RDY-DECK-CONDITION' returns 200, acknowledged_blockers contains it. (6) POST /transition to PUBLICATION_APPROVED returns 200. (7) POST /publish with approval:true returns 200, status=='published', opportunity_id captured. (8) Idempotent replay with same idempotency_key 'k1' returns 200, idempotent_replay==true, same opportunity_id (no duplicate). (9) GET /workflow/{id} returns 200, current_state==OPPORTUNITY_PUBLISHED. (10) New workflow cancelled returns 200, current_state==CANCELLED. (11) Workflow with expires_in_seconds=0 returns 200, current_state==EXPIRED. SECURITY: Contractor GET /steward/workflow returns 403, GET /steward/workflow/{id} returns 403. Unauthenticated requests return 401. Anti-bypass test: client cannot bypass readiness with fabricated fields - server recomputes readiness and still blocks with 409 PUBLICATION_BLOCKED. REGRESSION: All Batch 1 + H-012 endpoints working (fixture, estimate, contractor-package, ask). Complete workflow lifecycle with publication gates, idempotency, and security isolation working perfectly."

frontend:
  - task: "H-013 Batch 1 regression — Home Steward UI (/steward) still works after backend security-gate changes"
    implemented: true
    working: true
    file: "frontend/src/pages/HomeSteward.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Backend responses kept backward-compatible. UI reads contractorPreview.summary + .shared_documents (unshared doc_02 now correctly hidden). Needs UI regression run through the Steward wizard."
        - working: true
          agent: "testing"
          comment: "✅ COMPLETE UI REGRESSION PASSED (9/9 verification items): (1) Page loads without crash, title 'Habitat Home Steward™' visible. (2) Ask flow: 'Do I need a new roof?' triggers structured 4-level answer (Direct Answer, Why This Matters, Supporting Information, Trace/References). (3) Recommendation renders with primary action 'Schedule a focused roof inspection' and secondary progressive disclosure options. (4) Confirm action 'Explore Roof Replacement' succeeds, advances through confirmation gate to Design Studio. (5) Estimate renders with Austin local cost range ($26,000-$38,000 for DECRA Standing Seam), breakdown (materials/labor/permits/contingency), material selection updates estimate correctly. (6) Investment scenarios A/B/C render with cost text and maintenance implications. (7) Build Ready: readiness score 65 displays, checklist shows 'Existing Deck & Underlayment Condition' flagged as MISSING with 'BLOCKS PUB' indicator. (8) Contractor Package Preview renders with 'Redact personal contact details' toggle (enabled by default), shared documents list shows ONLY drone inspection doc (doc_02 correctly filtered by backend), NO homeowner PII visible in contractor package content (no last name, no email, no phone, no exact address - redaction working correctly). (9) Publish succeeds: 'Project Opportunity Published!' confirmation displays with Correlation ID and 'ACTIVE (Redacted)' status. All wizard steps advance correctly, no console errors, no critical network failures. H-013 Batch 1 security changes fully functional in UI."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 3
  run_ui: false

test_plan:
  current_focus:
    - "H-013 Batch 2 Phases 6-10 Persistent Steward workflow + publication gate + idempotency + audit + indexes"
    - "H-013 Batch 2 #5 Versioned read-only Passport projection boundary (adapter + provider modes)"
    - "H-013 Batch 2 Phase 5 Build-Ready blocker policy (HARD/CONDITIONAL/WARNING/INFORMATIONAL)"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: >
        H-013 BATCH 2 backend complete — verify over HTTP as homeowner alex@stratexhabitat.com / Demo123!.
        DO NOT modify env vars (do not toggle HABITAT_PROJECTION_MODE / HABITAT_ENV / HABITAT_ENABLE_FIXTURES on the live server).
        (A) PROJECTION BOUNDARY: GET /api/steward/context -> 200 with _projection.provider_mode=='development',
        _projection.authoritative==false, _projection.contract_version=='1.0.0', and still contains property_identity,
        published_explanation, property_dna_projection, seasonal_context.
        (B) READINESS POLICY: GET /api/steward/readiness -> 200, project_readiness_score==65, item 'Existing Deck & Underlayment
        Condition' classification=='CONDITIONAL_BLOCKER', status=='MISSING', blocks_publication==true.
        (C) WORKFLOW LIFECYCLE (base path /api/steward/workflow):
          1. POST {} (or {"property_id":<pid from /context property_identity.id>}) -> 200 current_state QUESTION_RECEIVED, version 1.
          2. POST /{id}/transition advancing in order: CONTEXT_RESOLVED, ANSWER_PRESENTED, ACTION_RECOMMENDED,
             ACTION_CONFIRMED, PROJECT_CREATED, ESTIMATE_CREATED (body material 'GAF Timberline HDZ'),
             SCENARIOS_REVIEWED, READINESS_REVIEWED, PACKAGE_PREVIEWED -> each 200 with matching current_state.
          3. Illegal transition (e.g. to_state 'QUESTION_RECEIVED' now) -> 409 error_code ILLEGAL_TRANSITION.
          4. POST /{id}/publish {approval:true, property_id:pid, idempotency_key:'k1'} BEFORE acknowledging deck
             -> 409 error_code PUBLICATION_BLOCKED with 'RDY-DECK-CONDITION' in blocking_item_ids.
          5. POST /{id}/acknowledge {item_id:'RDY-DECK-CONDITION'} -> 200.
          6. POST /{id}/transition to_state PUBLICATION_APPROVED -> 200.
          7. POST /{id}/publish {approval:true, property_id:pid, idempotency_key:'k1'} -> 200 status 'published' with opportunity_id.
          8. Repeat publish with same idempotency_key -> 200 idempotent_replay true, SAME opportunity_id (no duplicate).
          9. GET /{id} -> 200 current_state OPPORTUNITY_PUBLISHED (resume).
          10. Create another workflow, POST /{id}/cancel -> 200 current_state CANCELLED.
          11. Create workflow with body {"property_id":pid,"expires_in_seconds":0} then GET /{id} -> 200 current_state EXPIRED.
        (D) SECURITY: contractor horizon@stratexhabitat.com GET /api/steward/workflow and GET /api/steward/workflow/{homeowner_id}
            -> 403 (or 404). Unauthenticated -> 401. Frontend-supplied readiness cannot bypass: publish gate recomputes readiness
            from server-side acknowledged_blockers only.
        (E) REGRESSION: Batch 1 still works - GET /api/steward/fixture (is_fixture true), POST /api/steward/estimate
            (price_book_version 2026.07.0), GET /api/steward/contractor-package (no PII in preview), plus H-012 ask/recommendation/
            scenarios/confirm/publish/memory.
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
    - agent: "testing"
      message: >
        ✅ UI REGRESSION COMPLETE - ALL 9 ITEMS VERIFIED:
        
        Full end-to-end Home Steward wizard tested (alex@stratexhabitat.com):
        1. ✅ Page loads without crash, title visible
        2. ✅ Ask flow: "Do I need a new roof?" renders 4-level structured answer
        3. ✅ Recommendation with primary + secondary options renders
        4. ✅ Confirm action succeeds, advances to Design Studio
        5. ✅ Estimate with cost range/breakdown renders, material selection updates estimate
        6. ✅ Investment scenarios A/B/C render
        7. ✅ Build Ready: score 65, blocking checklist item present
        8. ✅ Contractor Package Preview: redaction toggle present, shared docs (doc_01 only), NO PII visible in package content
        9. ✅ Publish succeeds with opportunity ID and "ACTIVE (Redacted)" status
        
        No console errors, no critical network failures. H-013 Batch 1 UI fully functional.


    - agent: "testing"
      message: >
        ✅ H-013 BATCH 2 COMPLETE - ALL TESTS PASSED (23/23):
        
        A) PASSPORT PROJECTION BOUNDARY: ✓ PASS
        - GET /api/steward/context returns 200 with complete _projection envelope
        - provider_mode=='development', authoritative==false, contract_version=='1.0.0'
        - fixture_or_seed_identifier=='dev-seed-roof-2026.07', generated_at present
        - All required top-level keys present: property_identity, published_explanation, property_dna_projection, seasonal_context
        
        B) BUILD-READY BLOCKER POLICY: ✓ PASS
        - GET /api/steward/readiness returns 200 with project_readiness_score==65
        - 'Existing Deck & Underlayment Condition' item: classification=='CONDITIONAL_BLOCKER', status=='MISSING', blocks_publication==true
        
        C) WORKFLOW LIFECYCLE (11 steps): ✓ PASS
        - C.1: Workflow creation with QUESTION_RECEIVED state, version 1
        - C.2: All 9 state transitions successful (CONTEXT_RESOLVED → ANSWER_PRESENTED → ACTION_RECOMMENDED → ACTION_CONFIRMED → PROJECT_CREATED → ESTIMATE_CREATED → SCENARIOS_REVIEWED → READINESS_REVIEWED → PACKAGE_PREVIEWED)
        - C.2: estimate_snapshot.price_book_version=='2026.07.0', contractor_package_version present, redaction_settings.remove_personal_info==true
        - C.3: Illegal transition correctly blocked with 409 ILLEGAL_TRANSITION
        - C.4: Premature publish correctly blocked with 409 PUBLICATION_BLOCKED, blocking_item_ids contains 'RDY-DECK-CONDITION'
        - C.5: Acknowledgment of RDY-DECK-CONDITION successful
        - C.6: Transition to PUBLICATION_APPROVED successful
        - C.7: Publish with approval successful, status=='published', opportunity_id captured
        - C.8: Idempotent replay with same idempotency_key returns idempotent_replay==true, same opportunity_id (no duplicate)
        - C.9: Resume workflow returns current_state==OPPORTUNITY_PUBLISHED
        - C.10: Cancel workflow returns current_state==CANCELLED
        - C.11: Expiry workflow returns current_state==EXPIRED
        
        D) SECURITY / ISOLATION: ✓ PASS
        - Contractor GET /steward/workflow returns 403
        - Contractor GET /steward/workflow/{id} returns 403
        - Unauthenticated requests return 401
        - Anti-bypass: client cannot bypass readiness with fabricated fields - server recomputes and blocks with 409 PUBLICATION_BLOCKED
        
        E) REGRESSION (Batch 1 + H-012): ✓ PASS
        - GET /api/steward/fixture returns 200, is_fixture==true
        - POST /api/steward/estimate returns 200, price_book_version=='2026.07.0', price_provenance.price_source=='HABITAT_GOVERNED_PRICE_BOOK'
        - GET /api/steward/contractor-package returns 200, no raw PII leaked, shared_documents only contains doc_01
        - POST /api/steward/ask: valid roof question returns 200 with all levels, non-roof question returns 400
        
        Backend is production-ready for H-013 Batch 2 deployment. All Passport projection boundary, Build-Ready blocker policy, persistent workflow lifecycle with publication gates, idempotency, security isolation, and regression tests passed.
