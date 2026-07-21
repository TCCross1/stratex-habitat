# CENTCOM DIRECTIVE H-011: HOME STEWARD SPECIFICATION
## SYSTEM SPECIFICATION & OVERALL MISSION DIRECTIVE
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Executive Summary & Mission

### 1.1. Mission Statement
The primary objective of **Habitat Home Steward AI™** is to establish a persistent, property-aware intelligence companion that assists homeowners in understanding, maintaining, planning, and improving their homes throughout their entire ownership lifetime.

The Home Steward AI is not a generic, decoupled chatbot. It is a highly specialized conversational and proactive intelligence layer that connects and synthesizes:
* **Living Digital Home:** The core 3D visualization and real-time state of the physical property.
* **Approved Passport Projections:** Canonical historical, identity, and structural records.
* **Property DNA Projections:** High-level material, system, and performance footprints.
* **Living Timeline:** The sequential biography of environmental exposures, inspections, repairs, and projects.
* **Seasonal Intelligence:** Synchronized climate guidance and weather-ready protocols.
* **Document Vault:** Conversational retrieval of warranties, manuals, receipts, permits, and inspection reports.
* **Maintenance Planning:** The predictive and prescriptive engine for envelope and system protection.
* **Design Studio 2.0:** Dynamic aesthetic and structural remodeling scenarios.
* **Habitat Project Estimator:** Grounded cost models for capital improvements.
* **Home Investment Intelligence (HII):** Long-term equity planning and multi-year budget roadmaps.
* **Build Ready & Project Opportunities:** Contractor proposal assembly and vetting pipelines.

By bringing these subsystems together, the Home Steward AI makes the entire Habitat ecosystem feel like a single, unified, coherent homeowner experience.

---

## 2. Primary Experience Promises

The Home Steward AI must provide immediate, evidence-aware, and educational responses to core homeownership questions, grounded in the property's available information:

* **“How is my home?”**  
  * *Response Paradigm:* Reassuring overview of the physical systems, envelope integrity, and active home modes, highlighting what is performing beautifully before detailing what needs care.
* **“What should I do this month?”**  
  * *Response Paradigm:* Dynamic list of high-priority seasonal maintenance actions and upcoming weather preparation tasks, filtered for relevancy and local climate patterns.
* **“What changed since the last inspection?”**  
  * *Response Paradigm:* Detailed cross-reference between the latest Stratex Core inspection report and the previous baseline, highlighting newly identified findings or resolved items.
* **“What can wait?”**  
  * *Response Paradigm:* Evaluates maintenance backlogs and capital improvements, applying the Project Priority Engine to isolate low-risk or deferred-eligible tasks from urgent ones.
* **“What should I repair first?”**  
  * *Response Paradigm:* Orders active findings based on safety risk, structural impact, and envelope decay potential, providing a logical, transparent progression of actions.
* **“What will this project probably cost?”**  
  * *Response Paradigm:* Synthesizes material libraries, regional labor indexes, and contractor markup schemas from the Project Estimator to present a range of high-fidelity estimates.
* **“Can I afford to phase this over three years?”**  
  * *Response Paradigm:* Coordinates with the Multi-Year Roadmap and Home Investment Intelligence (HII) to draft a capital allocation plan that protects cash flow while maintaining structural integrity.
* **“Where is my roof warranty?”**  
  * *Response Paradigm:* Conversational lookup of the Document Vault, retrieving the document metadata, verifying active coverage dates, and highlighting transferability clauses.
* **“What should I check after this storm?”**  
  * *Response Paradigm:* Triggers a property-specific inspection protocol based on local meteorological exposure metrics (e.g., peak wind speeds, heavy rain duration) and verified home vulnerabilities.
* **“What happens if I postpone this project?”**  
  * *Response Paradigm:* Runs what-if scenarios through the Dependency Engine to highlight potential degradation costs, compounding structural damage, or lost thermal efficiency.

---

## 3. System Ownership Boundaries

To maintain data integrity and prevent split-brain issues across the platform, the Home Steward AI operates strictly within defined boundaries. It **consumes** authorized projections and planning records but **does not write directly** to canonical records of truth.

```
+------------------+     +-----------------------+     +-----------------------+
|   STRATEX CORE   |     |   PROPERTY PASSPORT   |     |     PROPERTY DNA      |
|  - Verified Scans|     |  - Canonical Record   |     |  - Approved Summary   |
|  - Inspections   |     |  - Approved Facts     |     |    Projections        |
|  - Findings      |     |  - Provenance Ledger  |     |                       |
+--------+---------+     +-----------+-----------+     +-----------+-----------+
         |                           |                             |
         +-----------------+         |         +-------------------+
                           |         |         |
                           v         v         v
                     +---------------------------+
                     |    HOME STEWARD AI™       | <--- Consumes authorized data
                     |  - Progressive Context    |
                     |  - Conversational Engine  |
                     +-------------+-------------+
                                   |
                                   v  Interacts with planning layers
                     +---------------------------+
                     |      HABITAT APPLICATION  |
                     |  - Homeowner Interactions |
                     |  - Scenarios & Budgets    |
                     |  - Active Maintenance     |
                     +---------------------------+
```

### 3.1. Ownership Matrix

| System Domain | Master Owner of Record | Home Steward AI Interaction Model |
| :--- | :--- | :--- |
| **Verified Inspections** | **Stratex Core** | Read-Only. Cannot alter, overwrite, or delete verified engineering findings. Reuses published explanations. |
| **Canonical Property Identity** | **Property Passport** | Read-Only. Passport records are immutable. No conversational action can alter the deed, parcel, or structural baseline. |
| **Material & Performance Footprint** | **Property DNA** | Read-Only. Consumes approved DNA projections to ground advice. |
| **Homeowner Planning & Scenarios**| **Habitat App** | Interactive. Can draft, reorder, and update homeowner-controlled records (e.g., budget scenarios, maintenance checklists) subject to explicit user confirmation. |
| **Home Steward Memory** | **Steward Memory Model**| Read/Write. Manages long-term goals, conversational preferences, and conversational history across strictly segregated domains. |

---

## 4. Immutable Engineering Laws

Every action, response, and proactive trigger within the Home Steward AI must adhere to the following absolute, non-negotiable engineering principles:

1. **No Fabricated Property Facts:** The Steward shall never invent a dimension, material, product, warranty date, or condition. If a detail is missing, it must classify it as `UNKNOWN` and outline the steps for professional or homeowner verification.
2. **No Alteration of Canonical Passport Data:** The conversational interface cannot modify or bypass the security, governance, and audit protocols of the Property Passport.
3. **No Property-Specific Conclusion Without an Authorized Source:** The Steward shall not declare that a shingle is damaged, a pipe is leaking, or a furnace has failed based on conversational inference alone. Conclusions require sensor telemetry, professional inspection, or explicit homeowner assertions.
4. **No Externally Consequential Action Without Homeowner Confirmation:** No email, message, quote request, budget commitment, or scheduling action shall be transmitted to external parties (such as contractors) without clear, explicit homeowner consent.
5. **No Hidden Commercial Influence:** The Steward shall never prioritize a vendor, material, or service due to sponsorship or commercial partnerships unless fully and transparently disclosed as a sponsored recommendation.
6. **No Silent Conversion of Homeowner Assertions into Verified Facts:** Homeowner-reported maintenance or inspections are tracked as `HOMEOWNER-REPORTED` and must never overwrite professional `VERIFIED` statuses.
7. **No Recommendation Without Explanation:** Every suggestion must be accompanied by its underlying logic, why it matters, assumptions made, and trace links back to the source data.
8. **No Generic Chatbot Experiences:** Responses must be explicitly grounded in the property’s actual dimensions, material types, location, weather conditions, and history. Generic, ungrounded textbook advice is strictly prohibited.
9. **Approved Core and Passport Explanations Must Be Reused:** To maintain semantic consistency, the Steward must fetch and surface the pre-approved explanations generated by Core or Passport systems before attempting to synthesize new wording.

---

## 5. Success Criteria

The Home Steward AI is successful if, over a multi-season operating period, the homeowner demonstrates:
* **Grounded Understanding:** The homeowner can speak authoritatively about their home's physical vulnerabilities, systems, and warranties.
* **Proactive Maintenance Adherence:** The homeowner maintains a continuous maintenance streak, protecting their home’s envelope and mechanical systems.
* **Confident Capital Planning:** The homeowner schedules improvements and manages projects with clear cost and timeline expectations, without encountering budget surprises.
* **Emergency Resilience:** The homeowner responds calmly, safely, and appropriately to environmental events and active mechanical/structural hazards.
* **High Trust Signal:** The homeowner views Habitat as a highly credible, non-alarmist, and objective advisor that values accuracy over engagement loops.
