# CENTCOM DIRECTIVE H-011: HOME STEWARD ARCHITECTURE
## SYSTEM ARCHITECTURE, INTEGRATION LAYER & DATA FLOWS
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. System Overview & Core Components

The **Habitat Home Steward AI™** is designed as an orchestration layer rather than a standalone service. It acts as an intelligent router and synthesizer, consuming authorized data from core systems and projecting information directly into the Habitat user interface. 

The architecture consists of nine primary technical components:

```
+-----------------------------------------------------------------------------------+
|                                 HABITAT CLIENT SURFACE                            |
|    [Command Center Rail]  [Design Studio Coach]  [Maintenance Panel]  [Mobile UX] |
+-----------------------------------------+-----------------------------------------+
                                          ^
                                          | JSON/gRPC API (Steward Gateway)
                                          v
+-----------------------------------------------------------------------------------+
|                              STEWARD GATEWAY & CONTROLLER                         |
+-----------------------------------------+-----------------------------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
        v                                 v                                 v
+-------------------+             +-------------------+             +-------------------+
| PROPERTY CONTEXT  |             |    HOMEOWNER      |             |     PROACTIVE     |
|   ORCHESTRATOR    |             |  CONVERSATION     |             |    STEWARDSHIP    |
|  Dynamic Context  |             |     ENGINE        |             |      ENGINE       |
|  Builder & Filter |             | Progressive Query |             | Event-Driven Alert|
+--------+----------+             +--------+----------+             +--------+----------+
         |                                 |                                 |
         |                                 v                                 |
         |                        +-------------------+                      |
         +----------------------->|    LLM ROUTER     |<---------------------+
                                  | (Claude Sonnet/   |
                                  |   Haiku Engine)   |
                                  +--------+----------+
                                           |
        +----------------------------------+---------------------------------+
        |                                  |                                 |
        v                                  v                                 v
+-------------------+              +------------------+              +-------------------+
|    MAINTENANCE    |              |     PROJECT      |              |   DOCUMENT &      |
|    & PRO-COACH    |              |    COACH / DS2   |              | WARRANTY ASSISTANT|
| Adherence & DIY   |              | Scenarios & HII  |              | Semantic Search   |
+-------------------+              +------------------+              +-------------------+
        |                                  |                                 |
        +----------------------------------+---------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                                STEWARD MEMORY ENGINE                              |
|   [Property Domain]      [Homeowner Domain]      [Conversation]      [Project]    |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                             TRUTH & EXPLAINABILITY ENGINE                         |
|   [Fact Classification]    [Approved Explanations]    [Safety & Escalation]       |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                              STEWARD ACTION EXECUTOR                              |
|   [Task Insertion]     [Document Queue]     [Estimate Sync]     [Reminders]       |
+-----------------------------------------------------------------------------------+
```

---

## 2. Technical Component Breakdown

### 2.1. Property Context Orchestrator
The Context Orchestrator is responsible for compiling the minimum necessary context required to answer a homeowner's query. It coordinates query extraction, vector lookups, and direct relational database reads across various databases, injecting metadata attributes to support traceability.

### 2.2. Homeowner Conversation Engine
An orchestration engine that processes inbound homeowner messages, determines user intent, coordinates execution across sub-coaches, and structures the response using a strict **4-Level Progressive Disclosure** framework.

### 2.3. Proactive Stewardship Engine
An event-driven monitoring service that listens to system events (e.g., severe weather alerts, sensor telemetry changes, document uploads, warranty expirations) and evaluates them against homeowner preferences, safety rules, and quiet-hours policies to generate non-intrusive notifications.

### 2.4. Maintenance Coach
An intelligence layer that links physical assets (such as water heaters, heat pumps, and roofs) to maintenance tasks. It calculates time-to-decay, identifies DIY vs. professional pathways, and tracks completion states.

### 2.5. Project Coach
A connector component that bridges the conversational experience with Design Studio 2.0, the Project Estimator, and Home Investment Intelligence (HII). It enables interactive "what-if" scenario modeling, sequencing, and contractor proposal comparison.

### 2.6. Document & Warranty Assistant
A semantic retrieval service integrated with the Document Vault. It performs vector searches across scanned PDFs and parses key document clauses (dates, coverage types, limits, contractor profiles).

### 2.7. Steward Memory Engine
A segregated memory router that ensures canonical property metrics, homeowner goals/preferences, and project-specific iterations are held in distinct databases to prevent data pollution.

### 2.8. Truth & Explainability Engine
The analytical validation layer. It assigns a truth classification to every outbound statement, coordinates fallback logic to prevent LLM hallucinations, and provides deep trace logs back to source systems.

### 2.9. Steward Action Executor
An execution interface that handles safe side-effects. It implements an action-permission taxonomy that allows the Steward to draft or prepare actions but blocks any externally consequential tasks without explicit, verified homeowner authentication.

---

## 3. Core Data Flow & Communication Sequences

The following sequence details how the system handles a multi-domain homeowner question: **"My roof is 15 years old. What will it cost to replace, and does my warranty cover active wear?"**

```
 Homeowner Client            Steward Gateway          Context Orchestrator           LLM / Truth Engine       Document Vault / Estimator
       |                            |                         |                           |                          |
       |--- Conversational Query -->|                         |                           |                          |
       |                            |--- Extract Intents ---->|                           |                          |
       |                            |    ("roof age", "cost", |                           |                          |
       |                            |     "warranty retrieval")                           |                          |
       |                            |                         |-- Query Asset & DNA ----->|                          | (Roof: 15 yrs old, Asphalt)
       |                            |                         |-- Find Warranty Documents |------------------------->| (Retrieve Roof_Warranty.pdf)
       |                            |                         |-- Pull Regional Labor --->|                          | (Retrieve $450-$700/sq index)
       |                            |<-- Structured Context --|                           |                          |
       |                            |    (Meta-tagged JSON)   |                           |                          |
       |                            |                                                     |                          |
       |                            |------------------- Build Response Payload --------->|                          |
       |                            |                                                     |-- Run Grounding Check -->|
       |                            |                                                     |-- Apply Truth Rating ----| (Output: PROJECTED / VERIFIED)
       |                            |<------------------ Structured Level 1-4 Output -----|                          |
       |<-- UI Rendered Response ---|                                                     |                          |
       |    (Highlighting 3D Roof)  |                                                     |                          |
```

---

## 4. Architectural Interfaces & API Contracts

To prevent the Steward from becoming a parallel system of record, it interfaces with existing services through highly structured API contracts.

### 4.1. Steward API Gateway: Post Chat Message
* **Endpoint:** `POST /api/steward/chat`
* **Request Schema:**
```json
{
  "session_id": "conv_98765",
  "homeowner_id": "usr_44321",
  "property_id": "prop_11098",
  "message": "My roof is 15 years old. What will it cost to replace, and does my warranty cover active wear?",
  "active_surface": {
    "module": "DESIGN_STUDIO",
    "selected_zone_id": "zone_roof",
    "selected_material_id": "mat_shingle_01"
  },
  "client_metadata": {
    "timezone": "America/Los_Angeles",
    "interface_mode": "DARK_DENSE",
    "voice_enabled": false
  }
}
```
* **Response Schema:**
```json
{
  "session_id": "conv_98765",
  "response_id": "resp_00123",
  "timestamp": "2026-07-21T14:15:00Z",
  "active_mode": "TODAYS_HOME",
  "progressive_disclosure": {
    "level_1_direct": "Replacing your 1,500 sq. ft. asphalt shingle roof is estimated to cost between $7,500 and $10,500 based on local rates. Your current shingle warranty does not cover normal wear and tear past 10 years.",
    "level_2_why_matters": "Active wear on a 15-year asphalt shingle envelope reduces its water-shedding performance, increasing the likelihood of attic moisture intrusion during winter storm patterns.",
    "level_3_assumptions": {
      "text": "Estimates assume standard architectural shingle removal, disposal, underlayment replacement, and local labor rates. The warranty review assumes the retrieved 'CertainTeed 2011' document matches your actual shingle model.",
      "metrics": {
        "square_footage": 1500,
        "material_class": "Asphalt Shingle (Architectural)",
        "regional_labor_tier": "B"
      }
    },
    "level_4_evidence": [
      {
        "source": "PROPERTY_PASSPORT",
        "entity_id": "doc_warranty_roof_2011",
        "title": "CertainTeed Shingle Limited Warranty (2011)",
        "url": "/api/vault/documents/doc_warranty_roof_2011/view",
        "confidence": 0.95,
        "truth_class": "VERIFIED"
      },
      {
        "source": "PROJECT_ESTIMATOR",
        "entity_id": "est_roof_2026_regional",
        "title": "Regional Shingle Replacement Cost Index",
        "confidence": 0.85,
        "truth_class": "ESTIMATED"
      }
    ]
  },
  "twin_visual_commands": {
    "camera_focus": {
      "target_asset": "roof_envelope",
      "fov": 45,
      "pitch": -30,
      "yaw": 45
    },
    "ui_highlights": [
      {
        "asset_id": "roof_shingles",
        "glow_color": "#FF6B00",
        "pulse": true
      }
    ]
  },
  "suggested_follow_ups": [
    {
      "label": "Run a what-if scenario for a metal roof upgrade",
      "action_type": "START_DESIGN_SCENARIO",
      "payload": { "material_family": "Metal Standing Seam" }
    },
    {
      "label": "Schedule an envelope safety check",
      "action_type": "PREPARE_MAINTENANCE_TASK",
      "payload": { "task_template_id": "envelope_roof_check" }
    }
  ]
}
```

---

## 5. Deployment, Scaling & Resiliency

1. **State Isolation:** The Steward runtime must remain stateless. Every request carries the session ID, allowing the gateway to pull relevant conversation memory, homeowner settings, and property variables in a single parallel step.
2. **LLM Fallback & Caching:** A response cache intercepts frequent queries (such as seasonal checklists). If an LLM call fails, the Steward falls back to pre-authored Passport explanations corresponding to the detected intent.
3. **Strict Timeout Budgets:** To prevent UI lag on the Command Center rail:
   * **Context Orchestration:** < 150ms
   * **Vector Document Lookup:** < 200ms
   * **LLM Synthesis (Streaming):** < 800ms first-token latency
   * **Total Lifecycle Budget:** < 1500ms
4. **Access Control:** The API gateway validates JWT scopes. Under no circumstances can a user without the role `homeowner` execute a Steward action that modifies Habitat planning records or retrieves high-value Document Vault items.
