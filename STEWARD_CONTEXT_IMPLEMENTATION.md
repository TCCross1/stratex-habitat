# PROPERTY CONTEXT ORCHESTRATOR
## SYSTEM CONTEXT PIPELINE IMPLEMENTATION

This document outlines the design and behavior of the **Minimum Necessary Property Context Orchestrator** implemented under Task 3.

---

## 1. PIPELINE WORKFLOW

The orchestrator operates as a strict secure-query gate. It queries the local property assets and Passport databases to compile authorized, relevant context only, avoiding bloating the LLM prompt size and preventing cross-tenant leakage.

```
                  [Request: Context Retrieval]
                               ↓
                 [JWT Authentication Verified]
                               ↓
              [Tenant Property Boundary Verified]
                               ↓
          [Select Minimum Context for "Roofing"]
                               ↓
        [Attach Certification Metadata & Truth States]
                               ↓
             [Output Isolated Context JSON Structure]
```

---

## 2. INVENTORIED CONTEXT STRUCTURE

The context payload retrieved by `/api/steward/context` contains:

1. **Property Identity:** Base name, location, stories, area, and year built.
2. **Published Roof Explanation:** Narrative summarizing the roof's general state from Passport.
3. **Property DNA Roof Projection:** Certified material types and geometry.
4. **Timeline Entries:** History of installations, cleanings, and localized inspects.
5. **Warranty Metadata:** Active material manufacturer warranties.
6. **Active Roof Projects:** Open design scenarios or requests.
7. **Seasonal Context:** Local climate factors (e.g., Texas hot summers, hail risk).

---

## 3. SECURITY AND RESILIENCY ENFORCEMENT

### Metadata Schemas
To ensure complete auditable traceability, every retrieved item contains:
* `source_system`: Sourced origin system (e.g., `Passport`, `PropertyDNA`, `LivingTimeline`).
* `source_id`: Immutable record ID.
* `version`: Version counter (e.g., `v1.0`).
* `truth_classification`: One of `VERIFIED`, `ESTIMATED`, `HOMEOWNER-REPORTED`, `UNKNOWN`.
* `confidence_score`: Numeric classification where applicable.
* `timestamp`: Explicit ISO-8601 generation date.
* `authorization_scope`: Authenticated scope (e.g., `homeowner:alex`).

### Context Limits and Fallbacks
* **Size Limits:** Retained context is capped at 10KB to prevent context dilution.
* **Duplicate Suppression:** Duplicate findings are merged using primary keys.
* **Stale Indicators:** Context records older than 180 days automatically display `stale: true` and prompt recalculation.
* **Safe Fallback:** If any downstream Passport or DNA system is offline, the context gracefully degrades to local cache with a warning instead of fabricating facts.
