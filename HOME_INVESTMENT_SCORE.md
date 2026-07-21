# CENTCOM DIRECTIVE H-010: HOME INVESTMENT SCORE
## SYSTEM STATUS ALGORITHM, TRANSPARENT INDEXING, & SCORE TIERS SPEC
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW & ETHICAL SCORES

Traditional real estate and home maintenance platforms use opaque, proprietary, black-box scoring systems. Homeowners are shown a letter grade or a flat number with zero explanation of how it was calculated. This creates confusion, erodes trust, and prevents homeowners from taking actionable steps to improve their property's standing.

In strict compliance with the **Home Investment Intelligence™ Core Mandates**, Habitat establishes the **Home Investment Score (HIS)** ($S_{\text{inv}}$). The HIS is a completely transparent, explainable, and mathematically decomposable metric from `0` to `100` that evaluates how well-planned, well-maintained, and physically resilient the property is. Every contributing factor is fully visible, and any score adjustment is backed by structural or financial evidence.

```
       [ 1. Planned Coverage ]                [ 2. Envelope Resilience ]
         - Active vs. Deferred                  - Roof, Siding, Windows
                    \                                      /
                     \                                    /
                      v                                  v
                    +--------------------------------------+
                    |      HOME INVESTMENT SCORE (S_inv)   |
                    |            Scale: 0 to 100           |
                    +--------------------------------------+
                      ^                                  ^
                     /                                    \
                    /                                      \
       [ 3. Mechanical Health ]               [ 4. Financial Readiness ]
         - HVAC, Electric, Water                - Budget & Saving Caps
```

---

## 2. THE EXPLAINABLE MATHEMATICAL FORMULA

The overall Home Investment Score ($S_{\text{inv}}$) is a weighted aggregation of four independent, normalized sub-indexes, each scoring from `0.0` to `100.0`:

$$S_{\text{inv}} = w_P P_C + w_E E_R + w_M M_H + w_F F_R$$

Where the weights ($w_i$) reflect the structural priority of envelope shielding and physical preservation, summing to exactly $1.0$:

| Weight | Index Name | Weight Value | Percentage of Score |
| :---: | :--- | :---: | :---: |
| $w_E$ | **Envelope Resilience Index ($E_R$)** | $0.35$ | $35\%$ |
| $w_P$ | **Planned Project Coverage ($P_C$)** | $0.25$ | $25\%$ |
| $w_M$ | **Mechanical & Systems Health ($M_H$)** | $0.25$ | $25\%$ |
| $w_F$ | **Financial Readiness Score ($F_R$)** | $0.15$ | $15\%$ |

---

## 3. SUB-INDEX MATHEMATICAL DEFINITIONS

### 3.1. Envelope Resilience Index ($E_R$)
Measures the physical integrity and wear of the home’s primary protective barrier (Roof, Windows, Siding, Foundation) using Remaining Useful Life (RUL) ratios from the Property DNA database.

$$E_R = 0.40 \times \left(\frac{\text{RUL}_{\text{roof}}}{\text{UL}_{\text{roof}}}\right) + 0.25 \times \left(\frac{\text{RUL}_{\text{siding}}}{\text{UL}_{\text{siding}}}\right) + 0.20 \times \left(\frac{\text{RUL}_{\text{windows}}}{\text{UL}_{\text{windows}}}\right) + 0.15 \times \left(\frac{\text{RUL}_{\text{found}}}{\text{UL}_{\text{found}}}\right)$$

*   If any critical envelope finding (e.g., active water leak) is published, the $E_R$ index is automatically docked by $30.0$ penalty points to reflect active exposure.

### 3.2. Planned Project Coverage ($P_C$)
Measures the homeowner’s proactive strategic planning. It is the percentage of identified maintenance, hazard, or necessary upgrade projects ($J_{\text{req}}$) that have been assigned to an active planning phase in Years 1-5 of the Multi-Year Roadmap.

$$P_C = \left( \frac{\sum_{j \in J_{\text{req}}} \text{Cost}_j \times \mathbb{I}(\text{Year}_j \le 5)}{\sum_{j \in J_{\text{req}}} \text{Cost}_j} \right) \times 100$$

Where $\mathbb{I}(\text{Year}_j \le 5)$ is an indicator function that equals $1$ if project $j$ is scheduled in Years 1 to 5, and $0$ if it is deferred to Year 6+ or remains unscheduled.

### 3.3. Mechanical & Systems Health ($M_H$)
Evaluates the mechanical, heating, cooling, plumbing, and electrical subsystems of the house.

$$M_H = \frac{1}{|A_{\text{sys}}|} \sum_{a \in A_{\text{sys}}} \left( \text{HealthRating}_a \times \text{EfficiencyModifier}_a \right)$$

*   $A_{\text{sys}}$: Set of active mechanical assets (HVAC compressor, furnace heat-exchanger, electrical service panel, water main).
*   $\text{HealthRating}_a$: Core health score ($0-100$) compiled from physical inspection and asset age.
*   $\text{EfficiencyModifier}_a$: Multiplier ($0.8$ to $1.0$) reflecting carbon emission and energy performance ratios.

### 3.4. Financial Readiness Score ($F_R$)
Measures how well the scheduled roadmap costs align with the homeowner’s yearly budget caps, evaluating whether the plan is realistic and financially executable.

$$F_R = 100 \times \left( 1 - \frac{\sum_{t=1}^{5} \max\left(0, \text{ProjectCost}_t - \text{BudgetCap}_t\right)}{\sum_{t=1}^{5} \text{BudgetCap}_t} \right)$$

*   If the scheduled cost in any single year exceeds the budget cap by more than $50\%$, $F_R$ caps out at a maximum of $50.0$ to signal high budget execution risk.

---

## 4. SYSTEM STATUS TIERS & COLOR SYSTEM

The Home Investment Score is mapped into four distinct status tiers designed in accordance with the Stratex high-contrast command-center design system.

```
+---------------------------------------------------------------------------------+
|                       HOME INVESTMENT SCORE STATUS TIERS                        |
+---------------------------------------------------------------------------------+
|  TIER 1 — ELITE STATUS (Green)          --->  Score: 90 - 100                   |
|                                               Token: #39FF14                    |
|                                                                                 |
|  TIER 2 — MANAGED STATUS (Teal)         --->  Score: 70 - 89                    |
|                                               Token: #00F0FF                    |
|                                                                                 |
|  TIER 3 — VULNERABLE STATUS (Orange)     --->  Score: 45 - 69                    |
|                                               Token: #FF9E00                    |
|                                                                                 |
|  TIER 4 — AT-RISK STATUS (Red)          --->  Score: < 45                       |
|                                               Token: #FF3131                    |
+---------------------------------------------------------------------------------+
```

### 4.1. Visual Language Guidelines
*   **Elite Status (`#39FF14`)**: Used when the home is physically secure, and all upcoming capital cycles are fully funded. *"Property envelope is resilient and strategic maintenance is fully phased and funded."*
*   **Managed Status (`#00F0FF`)**: Standard operational target. *"Property is in stable condition. Preventive upgrades are planned; minor budget alignment recommended in Year 3."*
*   **Vulnerable Status (`#FF9E00`)**: Indicates deferred maintenance or budget misalignment. *"Subgrade thermal or mechanical wear detected. Action recommended on Horizon 1-2 projects to preserve envelope integrity."*
*   **At-Risk Status (`#FF3131`)**: Significant envelope damage or extreme budget mismatch. *"Unaddressed envelope exposure. Immediate stabilization recommended in Horizon 1 to avoid secondary structural overhead."*

---

## 5. API DATA CONTRACT (SCORING TRANSPARENCY BLOCK)

The scoring endpoint returns every variable, weight, and component calculation, ensuring there are no black boxes.

```json
{
  "property_id": "villa-horizon-80202",
  "overall_score": 78.4,
  "score_tier": "MANAGED",
  "timestamp": "2026-07-21T12:00:00Z",
  "score_composition": {
    "envelope_resilience": {
      "raw_index": 82.5,
      "weight": 0.35,
      "weighted_contribution": 28.87,
      "components": {
        "roof_rul_ratio": 0.70,
        "siding_rul_ratio": 0.90,
        "windows_rul_ratio": 0.85,
        "foundation_rul_ratio": 0.95
      },
      "active_penalties": []
    },
    "planned_project_coverage": {
      "raw_index": 70.0,
      "weight": 0.25,
      "weighted_contribution": 17.50,
      "total_required_cost": 25000.0,
      "cost_scheduled_within_5_years": 17500.0
    },
    "mechanical_health": {
      "raw_index": 85.0,
      "weight": 0.25,
      "weighted_contribution": 21.25,
      "components": [
        { "name": "HVAC Compressor", "rating": 80.0, "efficiency_mod": 0.95 },
        { "name": "Electrical Panel", "rating": 95.0, "efficiency_mod": 1.0 },
        { "name": "Gas Furnace", "rating": 75.0, "efficiency_mod": 0.90 }
      ]
    },
    "financial_readiness": {
      "raw_index": 72.0,
      "weight": 0.15,
      "weighted_contribution": 10.80,
      "budget_violations": [
        { "year": 4, "overage": 9000.00 }
      ]
    }
  },
  "improvement_pathways": [
    {
      "action_project_id": "proj-roof-202",
      "impact_type": "ENVELOPE_RESILIENCE",
      "score_increase_potential": 8.5,
      "description": "Executing the Roof Shingle Replacement will eliminate south slope exposure penalties and raise your Envelope Resilience index from 82.5 to 91.0."
    },
    {
      "action_project_id": "proj-solar-101",
      "impact_type": "FINANCIAL_READINESS",
      "score_increase_potential": 4.2,
      "description": "Dragging Solar Installation from Year 4 to Year 6 resolves the Year 4 budget cap violation, immediately increasing your Financial Readiness score."
    }
  ]
}
```

---

## 6. STRATEX COMMAND-CENTER SCORING UI

The Home Investment Score is displayed as a prominent telemetry dial in the upper left quadrant of the orbital dashboard.

*   **Digital Gauge**: A thin, segmented circle that fills up to match the score. The active segment glows with the target status tier color.
*   **Fonts**: Outfit (medium, lowercase, tracking-wide) for the `"home investment score"` header. JetBrains Mono (bold, `#FFFFFF`) for the large score digits (e.g., `78`).
*   **Hover/Tap Interaction**: Selecting the score dial flips the central 3D Twin viewport to show a diagnostic breakdown layout, highlighting the Envelope, Planned, Mechanical, and Financial scores as four glowing structural orbital rings.
