# HOME MEMORY BEHAVIOR
## SEGREGATED PRIVACY AND PREFERENCE MEMORY ENGINE

This document records the implementation of the **Segregated Home Memory Storage** (Task 13).

---

## 1. SEGREGATED STORAGE SCHEMAS

To prevent user chat preferences from polluting the certified physical state of the home, we enforce strict segregation of memories into three distinct silos:

```
                      [Home Steward Chat Memory]
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
  [Project Memory]       [Homeowner Memory]        [Property Memory]
  * preferred material   * communication preference * references only
  * budget target        * explanation depth       * no local writes
  * timeline preference  * project priorities      * immutable pointers
```

### A. Project Memory (Volatile / Planning-centric)
This silo stores specific homeowner choices made for active or planned projects. It is cleared once a project completes or is cancelled:
* `preferred_roof_material` (e.g., `"DECRA Standing Seam"`)
* `budget_target` (e.g., `"$15,000"`)
* `timeline_preference` (e.g., `"30 days"`)
* `selected_scenario_id` (e.g., `"scenario_b_inspection"`)
* `unresolved_project_questions` (e.g., `"Does warranty cover decking rots?"`)

### B. Homeowner Memory (Personal / Persistent)
This silo stores user-specific interaction preferences across all properties they own. It is persistent and adheres to GDPR privacy policies:
* `communication_preference` (e.g., `"In-app notifications"`)
* `explanation_depth_preference` (e.g., `"Detailed - level 4 traces shown"`)
* `project_priorities` (e.g., `["structural safety", "thermal efficiency"]`)

### C. Property Memory (Immutable / Certified)
This silo **ONLY** references certified databases and projections. Under no circumstances may conversational statements or homeowner assertions write into this memory:
* `passport_projection_references` (pointers to `#PASS-RF-904`)
* `property_dna_references` (pointers to `#DNA-GEOM-3200`)
* **Rule:** Conversational statements (e.g., "I repaired the chimney flashing myself") **NEVER** write into this database as a verified truth. They remain labeled as `HOMEOWNER-REPORTED` or general notes.

---

## 2. PRIVACY AND DELETION CONTROLS

We provide full homeowner observability and control over stored memories directly from the Home Steward interface:
1. **Memory Inventory Grid:** A clear UI panel showing all stored facts, labeled by Category and Source.
2. **"Delete Fact" Controls:** Quick trash icons allowing homeowners to wipe individual facts (e.g., clearing the preferred material choice).
3. **"Edit Fact" Controls:** Allows inline correction of misheard chat preferences.
4. **No Secrets Policy:** Memory storage is scanned on-write to ensure no sensitive personal data (e.g., passwords, SSNs, credit cards) is stored in conversational vectors.
