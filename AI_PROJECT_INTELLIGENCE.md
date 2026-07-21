# CENTCOM DIRECTIVE H-003: AI PROJECT INTELLIGENCE
## ARTIFICIAL REASONING, COMPATIBILITY, AND CONFIDENCE SPECIFICATION
**Version:** 1.0  
**Author:** Director of Artificial Intelligence  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction

The **Habitat AI Project Intelligence Engine™** is a retrieval-augmented generation and reasoning system. Its objective is to analyze homeowner designs, evaluate them against physical property constraints, and produce actionable intelligence for homeowners and contractors.

To maintain complete transparency and user trust, the AI Project Intelligence Engine operates under two strict engineering rules:
1. **Every recommendation must explain WHY:** The AI is prohibited from presenting unsupported or subjective design advice. Every suggestion must be accompanied by a logical explanation grounded in Property DNA data, manufacturer specifications, or local building regulations.
2. **Every estimate must identify its confidence level:** All cost estimates, material quantities, and schedule predictions must be labeled with one of the four defined confidence tiers. This prevents misleading assumptions and ensures budget transparency.

```
                     +---------------------------------------+
                     |         AI Reasoning Engine           |
                     +---------------------------------------+
                                         |
            +----------------------------+----------------------------+
            |                                                         |
            v                                                         v
+-----------------------+                                 +-----------------------+
|  Input Grounding      |                                 |  Intelligence Outputs |
|  - Property DNA       |                                 |  - Compatibility      |
|  - Digital Passport   |                                 |  - Architectural Harm.|
|  - Material Specs     |                                 |  - Budget Confidence  |
+-----------------------+                                 +-----------------------+
```

---

## 2. Core Intelligent Sub-Systems

The AI Project Intelligence Engine executes six specialized analytical checks on every design:

### 2.1. Compatibility Review
* **Objective:** Verify that selected materials and structural designs comply with local building codes, HOA guidelines, regional wind/snow loads, and physical property characteristics.
* **Grounding Source:** Local municipal zoning databases, HOA bylaws, and Property DNA wind/thermal data layers.
* **Required Output Format:**
  * `passed`: Boolean.
  * `checks`: Array of itemized check evaluations.
  * `why`: Clear explanation citing specific code clauses or physical constraints.

### 2.2. Architectural Harmony Analysis
* **Objective:** Assess the visual alignment between the proposed design and the home's original architectural style (e.g., ensuring a modern horizontal cedar panel design complements a Mid-Century Modern home, or flags potential conflicts on a Victorian home).
* **Grounding Source:** Spatial point clouds, 3D mesh layers, and architectural classification models in the Property DNA.
* **Required Output Format:**
  * `harmony_score`: Normalized value (0–100).
  * `style_detected`: Detected architectural style (e.g., *Craftsman Bungalow*).
  * `why`: Detailed architectural explanation analyzing line, texture, color, and historic style precedents.

### 2.3. Material Recommendations
* **Objective:** Suggest alternative or complementary products to maximize thermal efficiency, improve weather resistance, lower long-term maintenance costs, or optimize the homeowner’s budget.
* **Grounding Source:** Active product specifications in the Module Registry, manufacturer warranty databases, and local climate exposure logs.
* **Required Output Format:**
  * `target_zone`: The design surface (e.g., *Siding Accent*).
  * `recommended_sku`: The suggested replacement product SKU.
  * `why`: Detailed explanation comparing efficiency, durability, and cost metrics of the original selection against the suggested option.

### 2.4. Suggested Improvements
* **Objective:** Identify high-value, pro-active upgrades that can be performed during the active project to extend system life or prepare the home for future renovations.
* **Grounding Source:** Historical maintenance records in the Digital Passport and active energy performance profiles.
* **Required Output Format:**
  * `improvement_type`: Category of suggestion (e.g., *Soffit Ventilation*, *Solar Pre-wire*).
  * `description`: Overview of the proposed work.
  * `why`: Technical justification showing why performing this upgrade now reduces total long-term costs.

### 2.5. Estimated Complexity Evaluation
* **Objective:** Classify the physical and technical difficulty of the proposed project. This helps contractors allocate the right resources and prepare accurate bids.
* **Grounding Source:** Site accessibility logs, utility location data, and structural load calculations.
* **Required Output Format:**
  * `level`: Complexity tier (`low`, `medium`, `high`, `extreme`).
  * `why`: Clear explanation identifying specific physical or technical obstacles (e.g., *high roof pitch, utility line conflicts, limited backyard access for excavation machinery*).

### 2.6. Budget Assumptions
* **Objective:** Calculate localized estimates for material, labor, permits, and contingencies.
* **Grounding Source:** Regional material pricing indices, historic labor rates, and local permit schedules.
* **Required Output Format:** Complete cost line items with mandatory `confidence_level` labels and detailed calculation reasoning.

---

## 3. The 4-Tier Estimate Confidence Framework

To maintain complete transparency and protect both homeowners and contractors, all pricing and schedule estimates are classified across four official confidence tiers:

```
+-------------------------------------------------------------------------------+
|  ESTIMATE CONFIDENCE TIERS                                                    |
+-------------------------------------------------------------------------------+
|  VERIFIED (100% Confidence)                                                   |
|  - Binding pricing from active contractor bids or manufacturer lists.          |
|                                                                               |
|  ESTIMATED (85% - 95% Confidence)                                             |
|  - Localized material pricing and regional average labor rates.               |
|                                                                               |
|  SUGGESTED (60% - 80% Confidence)                                             |
|  - Standard allowances for areas where specific products are not yet locked.  |
|                                                                               |
|  FUTURE ( < 50% Confidence)                                                   |
|  - Conceptual placeholders for items requiring site visits or engineering.    |
+-------------------------------------------------------------------------------+
```

### 3.1. Verified Tier (Green / 100%)
* **Definition:** Binding pricing from active contractor proposals or locked-in manufacturer price sheets.
* **Trigger:** An active contractor proposal is submitted, or a direct-to-consumer material purchase is completed.
* **UI Representation:** Solid green border with check badge.

### 3.2. Estimated Tier (Teal / 85-95%)
* **Definition:** Localized material pricing combined with regional average labor rates calculated based on verified property dimensions.
* **Trigger:** Exact products are selected and property dimensions are verified via 3D spatial scan.
* **UI Representation:** Teal text with calculator icon.

### 3.3. Suggested Tier (Orange / 60-80%)
* **Definition:** General allowances for design surfaces or features where specific products have not yet been selected, calculated using average regional sizing.
* **Trigger:** General project scope is defined, but specific product SKUs or finishes are not yet locked in.
* **UI Representation:** Orange text with warning icon.

### 3.4. Future Tier (Gray / <50%)
* **Definition:** Rough, conceptual placeholders for complex items requiring professional structural engineering, onsite evaluations, or modules that are not yet active in the Design Studio.
* **Trigger:** Structural or mechanical elements are requested that cannot be verified without physical inspection.
* **UI Representation:** Dotted gray border with placeholder badge.

---

## 4. Grounding and Prompt Engineering Strategy

To prevent hallucinations and guarantee accurate, context-aware analysis, the AI Orchestrator uses a strict **Retrieval-Augmented Grounding Context Block** before sending prompts to the underlying LLM.

### 4.1. Grounding Schema Example
When evaluating a design, the AI system compiles the following structured data payload:

```json
{
  "grounding_context": {
    "property_dna": {
      "architectural_style": "mid_century_modern",
      "wind_exposure_category": "c",
      "roof_pitch": "4:12",
      "exterior_cladding_base": "vertical_cedar_siding"
    },
    "digital_passport": {
      "last_roof_replacement": "2012-05-15",
      "active_moisture_alerts": false,
      "insulation_r_value_attic": 38
    },
    "module_registry_rules": {
      "siding_constraints": {
        "allowed_materials": ["engineered_wood", "natural_cedar", "fiber_cement"],
        "hoa_color_restrictions": ["neutral_earth_tones", "cool_grays"]
      }
    }
  }
}
```

### 4.2. Analytical Prompt Template
The compiler injects this grounding context into a structured prompt template:

```
[SYSTEM INSTRUCTION]
You are the Habitat AI Project Intelligence Engine. You evaluate homeowner design scenarios.
You must adhere to two absolute rules:
1. Every recommendation or evaluation must explain its logical "WHY", citing specific facts from the Grounding Context.
2. Every cost or scope estimation must be classified under one of the four Confidence Tiers: Verified, Estimated, Suggested, or Future. Do not invent pricing without attaching a clear confidence rating.

[GROUNDING CONTEXT]
{{grounding_context}}

[USER DESIGN SELECTION]
{{user_design_selection}}

[REASONING OBJECTIVE]
Analyze the user's design selection against the provided grounding context. Highlight any structural, code, or style compatibility concerns. Generate localized cost estimates and suggest structural improvements. Explain your reasoning for each output clearly.
```
