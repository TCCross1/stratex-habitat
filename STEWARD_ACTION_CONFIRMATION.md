# RECOMMENDED ACTION & CONFIRMATION ENGINE
## EXPLICIT ACTION GATE DESIGN

This document describes the design of the **Recommended Action Engine** (Task 5) and the **Explicit Confirmation Gate** (Task 6) required before entering the Design Studio project lifecycle.

---

## 1. THE RECOMMENDATION ENGINE

Based on the mixed-truth roof-condition fixture, the system evaluates all possible outcomes and selects exactly **one primary recommendation** to guide the homeowner safely.

### Primary Recommended Action:
* **Action:** **Schedule a focused roof inspection.**
* **Why:** Necessary because while materials appear sound under thermal imaging, the underlying structural deck health remains completely `UNKNOWN`.
* **Supporting Information:** Underlayment tactile inspection blocks safe long-term planning.
* **Expected Effort:** 1–2 hours onsite.
* **Professional Verification:** Required (requires a physical certified inspector).

### Secondary Actions (Progressive Disclosure):
* Begin replacement planning (long-term scenario preparation).
* Review shingle manufacturer warranty coverage.
* Upload missing historic roof installation documents.

---

## 2. THE EXPLICIT CONFIRMATION GATE

Before a planning project is created inside Design Studio, the homeowner must explicitly review and confirm the action. This step prevents accidental project generation or premature contractor outreach.

```
          [Homeowner clicks: "Explore Roof Replacement"]
                                ↓
               [Display Confirmation Modal / Screen]
                                ↓
    [Explicit Disclosures: What will change vs What will not]
                                ↓
             [Homeowner clicks: "Confirm & Create"]
                                ↓
        [Emit: HOMEOWNER_ACTION_CONFIRMED (Audit Event)]
                                ↓
         [Design Studio Roof Replacement Project Created]
```

### Displayed Confirmation Disclosures:
1. **Design Studio Project:** A temporary planning project named *"Project: Roof Replacement"* will be created to explore options.
2. **Referenced Data:** Property geometry and age will be imported from your Property DNA.
3. **Information Gaps:** Decking and underlayment structural health remain `UNKNOWN` and will be marked as planning risks.
4. **No Contractor Outreach:** No external roofing contractors or professionals will be notified, contacted, or sent your information.
5. **No Passport Alterations:** No certified property or Passport records will be modified or overwritten.

---

## 3. SECURITY AUDIT EVENT SCHEMA

Upon homeowner confirmation, an immutable audit record is published to the `audit_events` database:

* `event_id`: Unique transaction UUID.
* `event_type`: `HOMEOWNER_ACTION_CONFIRMED`.
* `timestamp`: Precise ISO-8601 server time.
* `homeowner_id`: Authenticated user ID (e.g., `alex-morgan-uuid`).
* `confirmed_action`: `"Explore Roof Replacement"`.
* `context_version`: Version token of the source context.
* `correlation_id`: Distributed transaction tracing ID.
