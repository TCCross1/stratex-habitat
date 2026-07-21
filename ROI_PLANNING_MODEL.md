# CENTCOM DIRECTIVE H-010: ROI PLANNING MODEL
## MULTI-DIMENSIONAL INVESTMENT RETURN RANGE & S.A.C.U. SPECIFICATION
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW & INVESTMENT LAWS

The **Return-On-Investment (ROI) Planning Model** is the financial analysis engine of the Home Investment Intelligence™ platform. Traditional property tools use simplistic financial calculators that make definitive claims about cost savings and property appreciation. 

In strict compliance with **Engineering Law 1 (No Guaranteed Returns)** and **Engineering Law 2 (No Guaranteed Property Value Predictions)**, Habitat rejects single-point financial predictions. Instead, the ROI Planning Model operates on a **probabilistic range-based architecture**. It computes performance bands and qualitative value scores grounded in physical building science, local climate records, regional cost databases, and historical utility rates.

```
       [ Input Project Parameters ]              [ Estimate Confidence Tier (ECF) ]
                    |                                            |
                    +--------------------+-----------------------+
                                         |
                                         v
                            +--------------------------+
                            |    ROI PLANNING MODEL    |
                            +--------------------------+
                                         |
                                         v
                            [ Probabilistic Ranges ]
                            - Cost Band: Low / Target / High
                            - Maintenance Reduction Range
                            - Energy Savings Range
                                         |
                                         v
                            [ Qualitative Assessments ]
                            - Comfort Index (0 to 10)
                            - Durability Extension Years
                            - Resale Appeal & Insurance Allowances
```

---

## 2. THE SEVEN VALUE DIMENSIONS OF PLANNING INSIGHTS

Every project evaluation is mapped across seven discrete, rigorous value dimensions:

```
+---------------------------------------------------------------------------------+
|                       THE 7 DIMENSIONS OF STAGE-GATE ROI                        |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  1. ESTIMATED PROJECT COST (Range-Based)                                        |
|     - Calculates Low, Target, and High range bands.                             |
|     - Range width is dynamically scaled by the Estimate Confidence Tier (ECF).  |
|                                                                                 |
|  2. POTENTIAL MAINTENANCE REDUCTION (Operational savings)                       |
|     - Models the reduction in annual recurring maintenance overhead.            |
|     - Formulated by tracking the physical asset's current failure risk.         |
|                                                                                 |
|  3. POTENTIAL ENERGY SAVINGS (Thermal/HVAC efficiency)                          |
|     - Quantified using thermodynamic R-values, HERS-ratings, climate zone       |
|       multipliers, local utility tariffs, and heating/cooling system fuel types. |
|                                                                                 |
|  4. POTENTIAL COMFORT BENEFITS (Non-financial UX)                               |
|     - Qualitative scaling (0-10) of draft reduction, temperature leveling,       |
|       acoustic dampening, and relative humidity control.                        |
|                                                                                 |
|  5. POTENTIAL DURABILITY & PHYSICAL RESILIENCE                                  |
|     - Calculates the extension of the home envelope's useful life and           |
|       the structural stabilization timeline.                                    |
|                                                                                 |
|  6. POTENTIAL RESALE CONSIDERATIONS (Market context)                            |
|     - Qualitative market-attractiveness scoring.                                |
|     - Regional Cost-vs-Value percentage recovery indices (no dollar guarantees).|
|                                                                                 |
|  7. POTENTIAL INSURANCE CONSIDERATIONS (Mitigation discounts)                   |
|     - Detects qualification for local underwriting discounts (e.g., wind       |
|       mitigation, Class 4 hail-resistant shingles, wildfire buffer zones).      |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

---

## 3. DYNAMIC RANGE CALCULATIONS (ECF COGNITIVE TUNING)

To reflect real-world construction risks, the cost range width is directly scaled by the **Estimate Confidence Framework (ECF)** score of the project. High-uncertainty projects (e.g., Tier 4) present wide ranges, while fully verified plans (e.g., Tier 1) present narrow, tight bands.

### 3.1. Cost Range Formulas
Given a baseline target estimate cost $C_{\text{target}}$ and its ECF score $S_{\text{proj}} \in [0, 100]$:

$$\text{Low Bound } (C_{\text{low}}) = C_{\text{target}} \times \left(1 - \delta_{\text{low}}\right)$$

$$\text{High Bound } (C_{\text{high}}) = C_{\text{target}} \times \left(1 + \delta_{\text{high}}\right)$$

The variance spreads ($\delta_{\text{low}}, \delta_{\text{high}}$) are determined by the confidence score:

$$\delta_{\text{high}} = 0.40 - \left(0.35 \times \frac{S_{\text{proj}}}{100}\right)$$

$$\delta_{\text{low}} = 0.15 \times \frac{S_{\text{proj}}}{100}$$

*   **Verified (ECF 95)**: Spread of $-14.2\%$ to $+6.75\%$. Cost numbers are highly precise.
*   **Preliminary (ECF 30)**: Spread of $-4.5\%$ to $+29.5\%$. Reflects high risk of unforeseen site conditions.

---

## 4. FORMULATOR FOR ENERGY & MAINTENANCE CALCULATIONS

### 4.1. Thermal Energy Savings Model
Annual HVAC heating/cooling energy cost reduction ($\Delta E$) is computed as:

$$\Delta E = \left( \left(\frac{1}{R_{\text{old}}} - \frac{1}{R_{\text{new}}}\right) \times A \times \text{HDD} \times 24 \times \frac{\text{Rate}_{\text{fuel}}}{\eta_{\text{HVAC}}} \right) \times \psi_{\text{climate}}$$

Where:
*   $R_{\text{old}}, R_{\text{new}}$: Thermal resistance values of the envelope assembly before and after.
*   $A$: Total surface area of the assembly (square feet).
*   $\text{HDD}$: Heating Degree Days of the property’s metropolitan climate zone.
*   $\text{Rate}_{\text{fuel}}$: Local cost per thermal unit of fuel (natural gas, electricity, heating oil).
*   $\eta_{\text{HVAC}}$: Efficiency rating of the active HVAC plant.
*   $\psi_{\text{climate}}$: Local micro-climate shielding coefficient (topography, tree canopy).

### 4.2. Maintenance Cost Reduction Model
Annualized maintenance cost reduction ($\Delta M$) models the elimination of emergency and preventative service overhead:

$$\Delta M = \sum_{a} \left[ \left(\text{Rate}_{\text{service}} \times F_{\text{failure}}(t)\right)_{\text{old}} - \left(\text{Rate}_{\text{service}} \times F_{\text{failure}}(t)\right)_{\text{new}} \right]$$

Where $F_{\text{failure}}(t)$ represents the Weibull wear/reliability curve of the assembly over time:

$$F_{\text{failure}}(t) = \frac{\beta}{\eta} \left(\frac{t}{\eta}\right)^{\beta-1}$$

---

## 5. API DATA CONTRACT & THE S.A.C.U. DATA BLOCK

To comply with **Engineering Law 3 (Mandatory S.A.C.U. Disclosure)**, every ROI data model returned by the backend must serialize a complete S.A.C.U. block.

```json
{
  "project_id": "proj-hvac-heatpump",
  "title": "Cold-Climate Air-Source Heat Pump Retrofit",
  "roi_dimensions": {
    "estimated_cost": {
      "low": 14200.00,
      "target": 15000.00,
      "high": 18500.00,
      "ecf_score": 74.5,
      "confidence_tier": "ESTIMATED"
    },
    "annual_maintenance_reduction": {
      "low": 150.00,
      "high": 400.00,
      "confidence": "HIGH",
      "basis": "Eliminates combustion service cycles, annual chimney flues, and recurring furnace filter blower wear."
    },
    "annual_energy_savings": {
      "low": 650.00,
      "high": 980.00,
      "heating_season_savings_est": 820.00,
      "cooling_season_savings_est": 110.00,
      "fuel_source_transition": "Natural Gas to Electric Heat Pump"
    },
    "qualitative_metrics": {
      "comfort_index": { "score": 8.5, "basis": "Eliminates room-to-room temperature stratification and short-cycling thermal shocks through multi-stage variable air flow." },
      "durability_years_extension": { "years": 15, "basis": "Eliminates high-temperature gas heat-exchanger cracks; updates baseline mechanical asset age to year zero." },
      "resale_appeal": { "score": 7.0, "regional_cost_vs_value": 0.68, "basis": "Highly attractive to energy-conscious buyers in ZIP 80202; classified as premium mechanical infrastructure." },
      "insurance_discount_eligibility": { "qualified": true, "estimated_annual_discount_range": [50.00, 120.00], "basis": "Elimination of open gas flames and carbon monoxide combustion pathways reduces basic household fire and life safety risk profiles." }
    }
  },
  "sacu_disclosure": {
    "supporting_evidence": [
      "Property DNA HVAC thermal camera ventilation air-flow registers logging (2026-06-15).",
      "Utility electricity rate index Level 3 metropolitan data ($0.145 per kWh).",
      "Manufacturer coefficient of performance (COP 3.2) ratings for model AHRI-90210."
    ],
    "assumptions": [
      "Assumes baseline heating load of 55,000 BTU/hr at 10°F outdoor temperature.",
      "Assumes historical standard winter heating load profile over 5,200 Heating Degree Days.",
      "Assumes annual utility rate inflation factor of 3.5% over the 10-year planning model."
    ],
    "confidence_level": {
      "numerical_score": 74.5,
      "tier": "ESTIMATED",
      "narrative": "Based on solid geometric and mechanical records. Cost ranges represent regional average quotes. Unforeseen electrical panel load-service upgrade charges represent a moderate cost variability risk."
    },
    "unknowns": [
      "Exact current structural R-value of interior wall cavities without physical insulation core boring.",
      "Actual electrical conductor wiring insulation condition inside closed drywall bays."
    ]
  }
}
```

---

## 6. STRATEX COMMAND-CENTER UI STANDARDS

ROI dimensions are presented as an "Investor-Grade Ledger" inside the Design Studio right Inspector panel.

### 5.1. Typography & Grid Structure
*   All planning ranges must use a strict parallel layout with double dotted lines (`===` or `...`) for alignment.
*   Financial ranges are rendered in JetBrains Mono, styled in Command Teal (`#00F0FF`).
*   Qualitative value sliders are rendered as standard Stratex high-contrast linear scales (`[----o-----]`).

### 5.2. Mandatory Legal Warning Block
Every ROI panel must present a standard footer in IBM Plex Sans (small, medium gray `#9CA3AF`) with clean uppercase tracking:

> `* PLANNING INSIGHT ONLY. EST. RANGES ARE NON-BINDING ESTIMATES CONFORMING TO THE STRATEX HABITAT ESTIMATE CONFIDENCE FRAMEWORK. NOT AN OFFER, GUARANTEE, OR CERTIFIED FINANCIAL REAL ESTATE APPRAISAL.`
