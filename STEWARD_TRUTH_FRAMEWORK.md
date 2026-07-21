# CENTCOM DIRECTIVE H-011: STEWARD TRUTH FRAMEWORK
## TRUTH CLASSIFICATION, RECOMMENDATION RUNTIMES & EXPLAINABILITY
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Purpose

An AI companion advising on a home must distinguish between a hard, professionally audited physical fact (e.g., *"Your home has a 200-amp electrical service panel"*), a mathematical projection (e.g., *"Your heat pump is projected to reach its performance limit in 2029"*), and a self-reported assertion (e.g., *"You noted that you replaced the water heater filter last month"*).

The **Steward Truth Framework** is an analytical system that evaluates every material property statement and recommendation before it is presented to the user. It assigns a strict **Truth Classification**, exposes the underlying assumptions, and provides clear, evidence-based recommendations.

---

## 2. Truth Classification Matrix

The system classifies all physical, structural, and mechanical statements into one of six distinct truth tiers:

| Truth Class | Definition | Primary Source Systems | Confidence | UI Visual Treatment |
| :--- | :--- | :--- | :---: | :--- |
| **VERIFIED** | Certified by a licensed inspector, verified through engineering reports, or proven via cryptographic sensor telemetry. | Stratex Core, Property Passport, municipal permit logs. | **1.00** | Glowing neon teal badge with an immutable security seal icon. |
| **ESTIMATED** | Calculated using precise physical measurements, product library catalogs, or regional labor and material databases. | Habitat Project Estimator, Regional Cost Engine. | **0.80** | Solid green badge with a calculator icon. |
| **PROJECTED** | Derived from mathematical modeling, decay simulations, or financial trend projections. | HII Engine, Multi-Year Roadmap, weathering models. | **0.70** | Dashed blue-teal badge with a timeline trend icon. |
| **HOMEOWNER-REPORTED** | Declared manually by the homeowner without professional verification or receipt matching. | Habitat App User Portal, manual checklist completions. | **0.50** | Hollow orange badge with an avatar icon. |
| **SUGGESTED** | Generated through AI pattern-matching, local climate averages, or general residential heuristics. | Home Steward AI, generic building models. | **0.40** | Dotted purple badge with a lightbulb icon. |
| **UNKNOWN** | Missing, unrecorded, or contradictory data parameters. | Null database entries, failed sensor diagnostic feeds. | **0.00** | Hollow gray badge with a question mark icon. |

---

## 3. Grounded Recommendation Structure

To satisfy the primary experience promise and prevent ungrounded AI recommendations, every action or upgrade suggested by the Steward must expose its underlying logic and trace details using a standardized, structured framework:

```
+---------------------------------------------------------------------------------+
| STEWARD RECOMMENDATION SCHEMA                                                   |
+---------------------------------------------------------------------------------+
| RECOMMENDATION | "We suggest replacing the furnace filter this week."           |
+----------------+----------------------------------------------------------------+
| WHY RECOMMENDED| "Maintains indoor air freshness and protects your heat pump    |
|                | fan blower motor from dust accumulation and strain."           |
+----------------+----------------------------------------------------------------+
| SUPPORTING INFO| "Your fan blower motor was installed in 2021. It represents    |
|                | a critical mechanical sheathing asset."                         |
+----------------+----------------------------------------------------------------+
| CONFIDENCE     | 0.85 (Based on local filter life models)                      |
+----------------+----------------------------------------------------------------+
| ASSUMPTIONS    | "Assumes continuous winter fan operation of 8 hours per day."  |
+----------------+----------------------------------------------------------------+
| UNKNOWNS       | "We do not know if the home has pet dander or high dust loads."|
+----------------+----------------------------------------------------------------+
| NEXT ACTION    | "Order a merv-11 filter and slide open the filter housing."    |
+----------------+----------------------------------------------------------------+
| PRO-VETTING    | "Not required. This is a simple DIY task."                     |
+---------------------------------------------------------------------------------+
```

### 3.1. Recommendation Attributes

* **Why Recommended:** The environmental, structural, safety, or financial rationale.
* **Supporting Information:** Contextual facts (e.g., equipment age, material classes) extracted by the Orchestrator.
* **Confidence Rating:** Numeric value ($0.0$ to $1.0$) indicating the strength of the grounding data.
* **Assumptions:** Explicitly lists what the system assumed about the property, climate, or usage patterns.
* **Unknowns:** Transparently lists any missing variables that could affect the accuracy of the recommendation.
* **Recommended Next Action:** A clear, step-by-step physical or digital action (e.g., "Add task to checklist" or "Open Design Studio").
* **Professional Vetting Option:** Specifies if the task requires certified verification (e.g., "A licensed electrician should verify your service panel load before upgrading").

---

## 4. Semantic Reusability of Core & Passport Explanations

To ensure linguistic consistency and prevent "hallucinatory drift" across the platform:

* **Rule:** The Home Steward AI must reuse pre-approved explanation strings and diagnostics generated by Stratex Core and Property Passport systems.
* **Mechanism:** When a user queries a finding (e.g., *"Why did the inspector flag my chimney?"*), the Steward matches the intent, queries the Core Registry, retrieves the exact `finding_explanation` block, and displays it inside the progressive disclosure Level 1-4 fields, rather than synthesizing a new explanation.
