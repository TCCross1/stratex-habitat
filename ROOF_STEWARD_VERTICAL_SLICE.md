# OPERATION STEWARD VERTICAL SLICE™ (H-012)
## SYSTEM ARCHITECTURE AND JOURNEY DIRECTIVE

This document records the design and engineering implementation of the complete production vertical slice for the **Habitat Home Steward AI™**.

---

## 1. THE USER JOURNEY PIPELINE

The end-to-end journey maps exactly to the Reference User Journey authorized in the CENTCOM Directive H-012:

```
[Homeowner Question: "Do I need a new roof?"]
                        ↓
             [Intent Classification]
                        ↓
     [Minimum Necessary Context Retrieval]
                        ↓
       [Published Explanation Retrieval]
                        ↓
     [Property DNA & Timeline Retrieval]
                        ↓
         [Home Steward Response (4 Levels)]
                        ↓
    [Evidence, Confidence & Assumptions Shown]
                        ↓
          [Recommended Next Action]
                        ↓
     [Homeowner: "Explore Replacement"]
                        ↓
          [Explicit Action Gate]
                        ↓
       [Design Studio Project Created]
                        ↓
       [Verified Geometry Referenced]
                        ↓
         [Material Options Compared]
                        ↓
       [Project Estimator Pricing Ranges]
                        ↓
      [HII: Scenario What-If Comparisons]
                        ↓
      [Homeowner Scenario Selection]
                        ↓
        [Build Ready Checklist Review]
                        ↓
         [Contractor Package Preview]
                        ↓
          [Explicit Homeowner Approval]
                        ↓
       [Project Opportunity Published]
```

Every stage of this journey is implemented to be fully executable, auditable, recoverable, tenant-isolated, and testable.

---

## 2. PRODUCTION IMPLEMENTATION COMPONENTS

The vertical slice is comprised of the following key production components:

1. **Backend Service (`backend/steward.py`):**
   Exposes high-performance, secure FastAPI endpoints running under `steward_router`, connected to a shared MongoDB instance. Handles deterministic fixtures, context orchestrator, estimator pricing multipliers, scenario comparison, and publication.
2. **Frontend UI Page (`frontend/src/pages/HomeSteward.js`):**
   An interactive Stratex Command Center dashboard guiding the homeowner through the 12-stage vertical slice with 3D context visualizers, failure simulators, and a real-time observability log stream.
3. **Automated Test Suite (`backend/tests/test_steward.py`):**
   Full Pytest coverage verifying security boundaries, context limits, calculation logic, action gates, and scenario comparisons.

---

## 3. CORE DESIGN DECISIONS

### Mixed Truth States
We prevent artificial confidence by implementing the **Mixed Truth State** model on all property metrics:
* **VERIFIED**: Sourced directly from certified property surveys or official scans.
* **ESTIMATED**: Derived analytically using regional models (e.g., age from year built).
* **HOMEOWNER-REPORTED**: Unverified assertions stated by the owner.
* **UNKNOWN**: Explicitly categorized gaps where professional inspection or physical audits are required.

### No Promises Policy
The Home Investment Intelligence (HII) scenarios strictly prohibit promethean claims of future resale returns, energy savings, or insurance premium discounts unless backed by localized disclosure frameworks. Unpromised values are clearly marked as assumptions under progressive disclosure.

### Tenant Isolation
Every endpoint strictly validates the authenticated session user against the requested resource's owner ID. Cross-tenant access attempts immediately fail with `403 Forbidden` and record security audit logs.
