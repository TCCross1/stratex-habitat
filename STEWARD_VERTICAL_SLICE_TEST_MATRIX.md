# STEWARD VERTICAL SLICE TEST MATRIX
## EXECUTABLE VERIFICATION TEST COVERAGE REPORT

This document catalogs the comprehensive test suite implemented under Task 16 to verify the functionality, security, performance, and UX accessibility of the **Home Steward AI**.

---

## 1. AUTOMATED TEST SUITE SCHEDULING

Our tests are written in Pytest (for the FastAPI backend) and React Testing Library/Playwright (for the frontend web interface).

---

## 2. EXECUTABLE TEST CATEGORIES AND INVENTORY

### A. Unit Tests (`backend/tests/test_steward.py`)
* **`test_get_fixture`**: Confirms fixture loads properly and exposes mixed truth states.
* **`test_get_context`**: Verifies that only authorized property context is retrieved.
* **`test_truth_classification`**: Ensures that `VERIFIED` and `UNKNOWN` are correctly attached to materials and decking.
* **`test_recommendation_engine`**: Confirms that "Schedule a focused roof inspection" is selected as the primary action.
* **`test_confirmation_gates`**: Asserts that project creation is blocked until action is confirmed.
* **`test_memory_segregation`**: Validates that chat preferences do not overwrite Passport records.
* **`test_estimate_presentation`**: Checks that Austin, TX regional multipliers are correctly computed.
* **`test_readiness_calculation`**: Asserts that missing decking condition drops the score to 65.
* **`test_publication_validation`**: Confirms that publication requires explicit homeowner approval.

---

### B. Integration Tests (`backend/tests/test_steward.py`)
* **`test_question_to_answer`**: Traces the path from "Do I need a new roof?" to the 4-level progressive answer.
* **`test_answer_to_project_creation`**: Verifies that confirming the recommendation spins up a new scenario.
* **`test_project_to_estimate`**: Confirms that changing materials immediately recalculates the pricing breakdown.
* **`test_estimate_to_scenario_comparison`**: Validates the unpromised disclosures in Scenario A, B, and C comparison.
* **`test_scenario_to_build_ready`**: Traces scenario values directly into the completeness scorecard.
* **`test_build_ready_to_preview`**: Verifies that the preview contractor package matches selected configurations.
* **`test_approval_to_publication`**: Confirms that publishing emits a `PROJECT_OPPORTUNITY_PUBLISHED` audit event.
* **`test_audit_event_creation`**: Asserts that confirmation and publication create immutable audit database entries.
* **`test_failure_recovery`**: Verifies that simulated backend outages do not crash the user experience.

---

### C. Security Tests (`backend/tests/test_steward.py`)
* **`test_security_unauthorized_endpoints`**: Confirms that unauthorized guests receive a `401 Unauthorized` block.
* **`test_get_fixture_tenant_isolation`**: Confirms that a contractor or other owner receives `403 Forbidden` on private property fixtures.
* **`test_cross_tenant_access`**: Asserts that Alex cannot view Jordan's property context files.
* **`test_confirmation_bypass`**: Blocks direct project creation via REST calls without confirmation trails.
* **`test_publication_bypass`**: Prevents publishing opportunities without active homeowner signed approval.
* **`test_prompt_injection`**: Validates that system instruction override prompts are sanitized and rejected.

---

### D. UX & Accessibility (UX) Tests (React & Playwright)
* **Mobile Homeowner Flow**: Simulates a 375px viewport to verify responsive single-column layouts and touch-friendly controls.
* **Desktop Digital Twin Flow**: Verifies that the 3D twin rendering panels are centered and responsive.
* **Keyboard Navigation**: Confirms that all buttons, toggles, and sliders are fully focusable and navigable via `Tab` and `Enter` keys.
* **Screen-Reader Labels**: Asserts that `aria-label` and `aria-live` regions exist for loading spinners and score meters.
* **Reduced Motion**: Respects browser accessibility parameters to disable transition animations.
* **Loading & Error States**: Confirms that network spinners and error dialogs are clearly rendered.
