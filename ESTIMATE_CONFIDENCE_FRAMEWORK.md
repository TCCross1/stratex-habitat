# CENTCOM DIRECTIVE H-009: ESTIMATE CONFIDENCE FRAMEWORK
## MULTI-LEVEL COGNITIVE RELIABILITY GRADING & CLARIFYING METADATA
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Overview & Objectives

In Design Studio 2.0, cost estimates are never presented as simple, flat figures of mysterious origins. To establish absolute confidence, the **Estimate Confidence Framework (ECF)** scores reliability at three independent levels:
*   **The Line-Item Level**: The individual material SKU or trade activity.
*   **The Assembly Level**: The structural system (e.g. concrete patio).
*   **The Project Level**: The aggregate project-wide planning scope.

By transparently signaling the reliability of every cost number, we teach homeowners how to improve their estimate's precision, transforming a vague, high-uncertainty planning range into a high-confidence, build-ready budget.

---

## 2. The 4 ECF Reliability Tiers

Each component, assembly, and project is assigned to one of four ECF confidence tiers based on the source of its quantities and pricing.

```
+---------------------------------------------------------------------------------+
|                       ESTIMATE CONFIDENCE TIER MATRIX                           |
+---------------------------------------------------------------------------------+
|  TIER 1 — VERIFIED (Green)       --->  Verified measurements + active local SKUs. |
|                                       Weight: 1.0  | Score: 90 - 100            |
|                                                                                 |
|  TIER 2 — ESTIMATED (Teal)       --->  Reliable spatial data + regional averages. |
|                                       Weight: 0.8  | Score: 70 - 89             |
|                                                                                 |
|  TIER 3 — SUGGESTED (Orange)     --->  Template allowances or homeowner inputs. |
|                                       Weight: 0.5  | Score: 40 - 69             |
|                                                                                 |
|  TIER 4 — PRELIMINARY (Gray)     --->  Assumptions / Missing critical inputs.   |
|                                       Weight: 0.1  | Score: <40                 |
+---------------------------------------------------------------------------------+
```

### 2.1. Tier 1 — Verified (Green: `#39FF14`)
*   **Basis**: Quantities derived from *Verified Property Data* (Passport records or professional laser surveys). Pricing based on current, active, local SKU catalog records with guaranteed availability.
*   **Confidence**: $90\%$ to $100\%$ precision. Ready for purchase-order generation.

### 2.2. Tier 2 — Estimated (Teal: `#00F0FF`)
*   **Basis**: Quantities resolved from *Digital Twin Measurements* (3D mesh geometry calculations) or *AI-Derived Measurements* (2D segmented photo analyses). Pricing calibrated by RCE Level 3 Metropolitan Cost Indices.
*   **Confidence**: $70\%$ to $89\%$ precision. Highly reliable planning benchmark.

### 2.3. Tier 3 — Suggested (Orange: `#FF9E00`)
*   **Basis**: Quantities based on *Homeowner Inputs* (manual overrides) or standard *Template Allowances* from the Project Library. Pricing represents RCE Level 2 broad regional averages.
*   **Confidence**: $40\%$ to $69\%$ precision. Good for conceptual scaling.

### 2.4. Tier 4 — Preliminary (Gray: `#9CA3AF`)
*   **Basis**: Vital dimensional layers are missing (classified as *Unknown*). Cost figures rely on broad Level 1 National averages, placeholders, or statistical assumptions.
*   **Confidence**: $<40\%$ precision. Significant risk of scope drift.

---

## 3. Mathematical Scoring Engine (Weighted Aggregation)

The aggregate confidence score ($S_{\text{proj}}$) of a project is a cost-weighted average of its constituent assemblies. This ensures that a highly uncertain $500 mailbox does not drag down the rating of a highly accurate $15,000 roof installation.

### 3.1. Confidence Score Formula

The numerical score ($s_c$) of an individual component $c$ is determined by its sourcing:

$$s_c = \text{Source Score} \times \text{Pricing Score}$$

Where:
*   **Source Score**: Verified (10.0), Digital Twin (8.5), AI-Derived (7.5), Homeowner (6.0), Template (4.5), Unknown (2.0).
*   **Pricing Score**: SKU-Level (10.0), Local Indiced (8.5), Regional Indiced (7.0), National Indiced (5.0), Assumption-based (3.0).

The aggregate assembly score ($S_{\text{asb}}$) is the sum of component scores weighted by their proportional cost:

$$S_{\text{asb}} = \frac{\sum_{c} \left( s_c \times \text{Cost}_c \right)}{\sum_{c} \text{Cost}_c}$$

The project-level confidence score ($S_{\text{proj}}$) is:

$$S_{\text{proj}} = \frac{\sum_{a} \left( S_{\text{asb},a} \times \text{Cost}_a \right)}{\sum_{a} \text{Cost}_a}$$

---

## 4. Mandatory ECF Metadata Block

Every generated estimate is legally bound to present a standardized metadata block at the header. Under no circumstances can these parameters be hidden or omitted.

```json
{
  "confidence_metadata": {
    "overall_confidence_tier": "ESTIMATED",
    "numerical_score": 82.4,
    "pricing_effective_date": "2026-07-21T12:00:00Z",
    "geographic_basis": "ZIP 80202 (Denver, CO)",
    "major_assumptions": [
      {
        "category": "Subgrade Soil",
        "detail": "Assumes standard class 3 dry sandy clay. No rock excavation or heavy water-table dewatering included."
      },
      {
        "category": "Site Access",
        "detail": "Assumes minimum 48-inch side gate clearance. No manual crane-over or narrow zero-lot penalties applied."
      }
    ],
    "known_exclusions": [
      "Municipal setback zoning variance fees",
      "Utility secondary lateral gas line hookups",
      "Post-concrete custom landscape turf repairs"
    ],
    "missing_information": [
      {
        "field": "patio_soil_bearing_capacity",
        "impact": "Required to confirm if gravel subbase needs a 4-inch increase. Affects concrete longevity."
      }
    ],
    "recommended_verification_action": {
      "action_type": "Onsite Field Measurement",
      "description": "Invite a participating contractor to confirm subgrade soil stability and verify side gate clearance.",
      "estimated_cost": 0.00
    }
  }
}
```

---

## 5. Recommended Actions to Improve Accuracy

To guide the homeowner toward structural readiness, the ECF engine automatically generates prioritized "Clarification Actions" when Tier 3 or Tier 4 elements are present:

### 5.1. Siding Assembly is Suggested (Tier 3)
*   **Trigger**: Siding area based on broad template averages.
*   **ECF Action**: *"Upload 3 high-quality smartphone photos of your home's exterior to allow our AI-Derived Measurement engine to map your facade walls. This will increase your confidence score from 55 to 82."*

### 5.2. Patio Excavation is Preliminary (Tier 4)
*   **Trigger**: Subgrade conditions are flagged as "Unknown".
*   **ECF Action**: *"Review your Home Passport's historical excavation logs, or schedule a 15-minute site assessment to confirm soil conditions. This will eliminate a $1,500 rock-contingency buffer."*

By contextualizing risk and showing homeowners *exactly* how to refine their budget, the ECF builds agency and financial literacy directly into the design process.
