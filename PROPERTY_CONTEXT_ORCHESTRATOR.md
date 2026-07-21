# CENTCOM DIRECTIVE H-011: PROPERTY CONTEXT ORCHESTRATOR
## MINIMUM NECESSARY PROGRESSIVE CONTEXT INTEGRATION SPECIFICATION
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Objectives

Injecting an entire, unstructured property record into an LLM context window for every conversational turn is highly inefficient, insecure, and error-prone. It leads to increased retrieval latency, soaring token costs, and a high risk of "attention distraction" or hallucination.

The **Property Context Orchestrator** is a specialized context assembly service. It retrieves **only the information necessary** to address the homeowner’s active request, converting complex multi-database schemas into a clean, unified, and strictly structured JSON payload.

---

## 2. Supported Context Sources & Metadata Schema

The Orchestrator pulls from 14 distinct data streams across both canonical registries and active planning databases. To ensure auditability and security, every context item retrieved must be wrapped in a metadata header detailing its provenance:

```json
{
  "context_item_id": "ctx_item_9812",
  "source_system": "PROPERTY_PASSPORT | STRATEX_CORE | HABITAT_PLANNING | METEOROLOGICAL_SERVICE",
  "classification": "CANONICAL | PLANNING | REVENUE",
  "version": "v1.4.2",
  "confidence_score": 1.00,
  "timestamp": "2026-07-21T14:15:00Z",
  "authorization_scope": "homeowner | contractor_restricted | admin_only",
  "payload": { ... }
}
```

### 2.1. Supported Data Streams

1. **Approved Property Identity:** Location, parcel boundaries, baseline building dimensions, primary envelope materials (from Property Passport).
2. **Property DNA Projections:** High-level material, envelope, and system classification matrices (from Property DNA).
3. **Published Explanations:** Pre-compiled, verified structural or mechanical assessments published from Stratex Core.
4. **Living Timeline Events:** Chronological environmental exposures, inspection milestones, and historical projects.
5. **Document Metadata:** Titles, categories, dates, and parsed legal/warranty parameters from the Document Vault.
6. **Maintenance Records:** Current status of recurring checks, completion logs, and active repair backlogs.
7. **Homeowner-Confirmed Information:** Manually asserted details (e.g., self-reported shingle repairs or filter changes).
8. **Active Design Studio Projects:** User-saved remodeling configurations, selected materials, and zone overrides.
9. **Project Estimates:** Itemized quantity takeoffs, regional labor costs, and contractor proposal figures.
10. **Investment Roadmaps:** Multi-year cash flow projections, capital reserves, and sequencing plans from HII.
11. **Project Opportunity Status:** Standardized contractor packages, active bidding statuses, and review pipelines.
12. **Home Modes:** Current active system operational mode (e.g., Today's Home, Severe Storm, Vacation Mode).
13. **Seasonal & Weather Context:** Current environmental season, immediate weather forecasts, and historical storm indexes.
14. **User Preferences & Goals:** Preferred communication styles, financial planning limits, and active homeownership objectives.

---

## 3. Dynamic Context Pruning & Allocation Algorithm

The Orchestrator operates with a strict **Token Budget**. By default, context compilation is capped at **4,000 tokens** per turn to preserve response speed and accuracy.

```
       +---------------------------------------------------------------+
       |                   INCOMING HOMEOWNER QUERY                    |
       |  "I have water pool near the foundation. Is my pump okay?"   |
       +-------------------------------+-------------------------------+
                                       |
                                       v
                       +-------------------------------+
                       |      INTENT EXTRACTION        |
                       |  - Primary: Sump Pump, Water  |
                       |  - Secondary: Sump Pump Doc   |
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |   CONTEXT MATRIX SCORING      |
                       |  - Mechanical (Sump Pump) = 10|
                       |  - Weather (Heavy Rain) = 9   |
                       |  - Foundation Siding = 8      |
                       |  - Financial Roadmap = 0      |
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |    RELEVANCY FILTER & PRUNE   |
                       |  Select top-ranked payloads.   |
                       |  Format to strict JSON.       |
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |      CONTEXT ASSEMBLER        |
                       |  Inject system schemas, metadata|
                       |  and enforce 4k token ceiling.  |
                       +-------------------------------+
```

### 3.1. Relevancy Weight Matrix

Intents extracted from the user's message are mapped to domain-specific weights. The Orchestrator queries only sources with a score exceeding a threshold of $T \ge 5.0$:

| Context Source | Intent: Mechanical / Sump Pump | Intent: Remodeling / Design | Intent: Financial / Roadmap | Intent: Document Search |
| :--- | :---: | :---: | :---: | :---: |
| **Property Identity & DNA** | **8.5** | **9.0** | 4.0 | 5.0 |
| **Published Explanations** | **9.0** | 3.0 | 3.0 | **8.0** |
| **Living Timeline** | **7.5** | 6.0 | 6.5 | **8.5** |
| **Document Metadata** | 6.0 | 3.0 | 3.0 | **10.0** |
| **Maintenance Records** | **10.0** | 4.0 | 5.0 | 6.0 |
| **Design Studio Projects** | 2.0 | **10.0** | 5.0 | 4.0 |
| **Project Estimates** | 3.0 | **8.0** | **9.0** | 5.0 |
| **Investment Roadmaps** | 1.0 | 5.0 | **10.0** | 3.0 |
| **Home Modes & Weather** | **9.0** | 5.0 | 2.0 | 2.0 |
| **User Preferences** | 5.0 | 6.0 | **7.0** | 4.0 |

---

## 4. Minimum Context Assembly Pipeline (Step-by-Step)

1. **Query Intent Extraction:** The gateway parses the incoming text utilizing an ultra-fast local classifier (e.g., small BERT or structured LLM call) to output a set of semantic weights.
2. **Domain Resource Allocation:** The Orchestrator calculates the relevancy score for each context source. It generates database query threads only for systems with scores above the threshold.
3. **Parallel Retrieval:** Queries are dispatched in parallel via non-blocking async DB connectors (MongoDB, Postgres, vector database).
4. **Metadata Wrapping:** Retrieved rows are structured as JSON and wrapped with canonical metadata headers.
5. **Token Truncation (The Guardrail):**
   * If total compiled JSON size exceeds 4,000 tokens, the Orchestrator executes **pruning**.
   * It preserves all items with `confidence_score == 1.0` (Verified Canonical facts).
   * It drops historical timeline events older than 365 days unless explicitly flagged as a parent asset dependency.
   * It truncates long text fields, replacing them with a signed URI for full-text lookup if the conversational model decides it is required.
6. **Context Serialization:** The final pruned payload is passed to the Conversation Engine.

---

## 5. Security & Isolation Controls

* **Scope Compliance:** If a context item has `authorization_scope == "admin_only"`, and the active user JWT has the role `homeowner`, the Context Orchestrator silently drops the payload during assembly to prevent privilege escalation.
* **Temporal Leak Protection:** To avoid "future leaking" during what-if simulations, any planning or projected document must carry a distinct `timestamp` and be isolated from the current physical state description of the home.
