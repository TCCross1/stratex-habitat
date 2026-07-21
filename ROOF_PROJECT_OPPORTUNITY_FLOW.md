# PROJECT OPPORTUNITY FLOW
## CONTRACTOR PREVIEW AND PUBLICATION LIFECYCLE

This document describes the **Contractor Package Preview** (Task 11) and the **Project Opportunity Publication** pipeline (Task 12).

---

## 1. THE CONTRACTOR PACKAGE PREVIEW

Before publishing the project to the contractor marketplace, the homeowner is presented with a complete preview package of exactly what information will be shared.

### Package Contents:
1. **Homeowner-Approved Project Summary:** "Villa Horizon - Roof Replacement Planning".
2. **Property Context:** City, state, stories, and age (no street address or owner name).
3. **Digital Twin View:** 3D orthographic roof rendering URL.
4. **Proposed Materials:** GAF Timberline HDZ Asphalt Shingles.
5. **Quantity Takeoff:** 3,200 sqft / 32 Squares surface area.
6. **Planning Estimate:** $14,515.20 (Expected scenario).
7. **Assumptions & Exclusions:** Excludes solar panels uninstallation.
8. **Timeline & Budget Preferences:** "30 days" / "Premium".
9. **Questions Requiring Onsite Verification:** Attic decking health, chimney flashing.
10. **Shared Documents & Warranties:** Certified structural thermal scans only.
11. **Project Readiness Score:** 65/100.

### Homeowner Privacy Controls:
* **Edit Eligible Fields:** Modify timeline or material preferences.
* **Remove Personal Info:** A toggle to remove the owner's real name and street address, replacing them with a secure generic nickname (e.g., *"Homeowner in Austin, TX"*).
* **Control Shared Documents:** Selectively check/uncheck document attachments (e.g., sharing a thermal report but hiding homeowners insurance papers).
* **Approve / Cancel:** One-click confirmation buttons to authorize publication or completely abort without saving.

---

## 2. PROJECT OPPORTUNITY PUBLICATION LIFECYCLE

Once the homeowner clicks **"Approve & Publish"**, the system executes a strict multi-stage publication pipeline:

```
           [Homeowner clicks: "Approve & Publish"]
                              ↓
        [Validate: Explicit Homeowner Approval Toggle]
                              ↓
   [Map References: Reference Passport/DNA without copying]
                              ↓
     [Seal Versions: Freeze Estimate & Scenario IDs]
                              ↓
    [Write Audit Log: Emit PROJECT_OPPORTUNITY_PUBLISHED]
                              ↓
    [Expose to Marketplace: Initial State = 'published']
```

### Publication Safeguards:
* **No Fact Duplication:** The opportunity refers to canonical Passport and DNA records by ID. It does not write or duplicate these facts into the opportunity database to prevent data drift.
* **Freeze Versioning:** Seals the design scenario and estimate calculation versions at the moment of approval. Any subsequent backend price adjustments do not retroactively alter the approved estimate.
* **Immutable Audit Entry:** Emits a `PROJECT_OPPORTUNITY_PUBLISHED` transaction log to the audit database containing the approval timestamp, shared-document permissions, and owner identity.
* **Lifecycle State Security:** The opportunity begins in the `'published'` state. Homeowner contact details (email/phone) remain completely encrypted and hidden from contractors until a bid is matched and explicitly accepted.
