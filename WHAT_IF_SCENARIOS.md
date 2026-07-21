# CENTCOM DIRECTIVE H-010: WHAT-IF SCENARIOS
## PATH COMPARISON, DEFERRAL RISK ANALYSIS, & MULTI-TRADE BUNDLING SPEC
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW

Homeowners are constantly forced to weigh the financial and physical trade-offs of timing their home investments. 
*   *"Should I spend the money to replace my roof today, or can I safely wait three years?"*
*   *"Is it cheaper in the long run to tackle my roof and windows at the same time to save on contractor labor?"*

The **What-If Scenario Engine (WSE)** is Habitat’s path comparison module. It allows homeowners to model and compare multiple independent investment paths side-by-side. The WSE evaluates compounding maintenance risks, deferred wear penalties, thermal envelope integration benefits, and multi-trade mobilizing discounts to deliver objective, non-guaranteed trade-off intelligence.

```
                      +-----------------------------------+
                      |   HOMEOWNER SELECTED SCENARIOS    |
                      |   - Scenario A: Replace Roof Now  |
                      |   - Scenario B: Wait 3 Years      |
                      |   - Scenario C: Roof & Windows    |
                      +-----------------------------------+
                                        |
                                        v
                      +-----------------------------------+
                      |      WHAT-IF SCENARIO ENGINE      |
                      |     - Evaluates Deferral Risk     |
                      |     - Calculates Bundle Discounts |
                      |     - Runs NLG Template Resolver  |
                      +-----------------------------------+
                                        |
                                        v
                      +-----------------------------------+
                      |   MULTI-SCENARIO COMPARE MATRIX   |
                      |   - Initial Cost & 10-Yr Cash Flow|
                      |   - Cumulative Maintenance Risk   |
                      |   - Comfort & Envelope Integ Score|
                      +-----------------------------------+
```

---

## 2. THE THREE STANDARDIZED SEED SCENARIOS

To ground the homeowner’s comparison, the WSE automatically seeds every comparison sandbox with three standard investment paths representing distinct financial and physical strategic paradigms.

### Scenario A — Replace Roof Now (The Immediate Stabilization Path)
*   **Tactical Action**: Execute the $12,500 Roof Shingle Replacement immediately in Year 1.
*   **Physical Consequence**: Instantly resets shingle remaining useful life (RUL) to 30 years. Eliminates wind and rain exposure risks. 
*   **Financial Impact**: High immediate cash outflow. Immediate, moderate annual energy bill savings (~$150/year) from updated modern shingles. Eliminates Year 1-3 failure/leak patch costs ($350 average per repair).

### Scenario B — Wait Three Years (The Deferred Capital Path)
*   **Tactical Action**: Defer the Roof Shingle Replacement to Year 4.
*   **Physical Consequence**: The shingle RUL remains under 2 years. Compounding wear from UV exposure and freeze-thaw cycles increases water intrusion probability. 
*   **Financial Impact**: Zero capital outlay in Years 1-3. High probability of emergency service patch calls ($1,050 cumulative over 3 years). High risk of compounding structural attic damage ($2,500 to $6,000 risk range). Zero energy efficiency improvements in Years 1-3.

### Scenario C — Replace Roof and Windows Together (The Optimized Bundled Path)
*   **Tactical Action**: Execute both the Roof Shingle Replacement ($12,500) and the Window Frame Retrofits ($10,000) simultaneously in Year 1.
*   **Physical Consequence**: Complete envelope sealing. The physical boundary of the home achieves high-efficiency thermal integrity and maximum water shedding capacity.
*   **Financial Impact**: Extreme Year 1 capital outlay ($22,500). However, the engine applies a **Multi-Trade Bundling Discount of 12%** ($2,700 savings on shared scaffolding, single municipal permit routing, and combined contractor mobilization overhead). Delivers maximum compounding annual energy savings (~$450/year combined) and peak Comfort Index ratings.

---

## 3. MULTI-SCENARIO TRADE-OFF MATRIX

The WSE aggregates these three pathways into a high-contrast comparison matrix for the homeowner:

```
+---------------------------------------------------------------------------------+
|                       MULTI-SCENARIO INVESTMENT COMPARISON                      |
+---------------------------------------------------------------------------------+
| METRIC                       | SCENARIO A (Now)  | SCENARIO B (Wait) | SCENARIO C (Bundle) |
+------------------------------+-------------------+-------------------+------------------+
| Immediate Capital Outlay     | $12,500 [Est]     | $0                | $19,800 [Est]*   |
| Multi-Trade Bundle Savings   | $0                | $0                | $2,700 (12% Disc)|
| 10-Year Est. Energy Savings  | $1,500 Range      | $1,050 Range      | $4,500 Range     |
| 10-Year Est. Maint. Expense  | $400 (Low Risk)   | $3,900 (High Risk)| $600 (Low Risk)  |
| Safety & Hazard Index        | Stable (10/10)    | High Risk (3/10)  | Stable (10/10)   |
| Envelope Integrity Rating    | Managed (92%)     | Vulnerable (55%)  | Elite (98%)      |
| Comfort Experience Rating    | Improved (+1.5)   | No Change         | Maximum (+4.5)   |
| Net 10-Yr Cost (Plan-Orient) | $11,400 Range     | $15,350 Range     | $15,900 Range    |
+---------------------------------------------------------------------------------+
* Includes 12% bundled trade discount on shared mobilizations.
```

---

## 4. NATURAL LANGUAGE GENERATION (NLG) TRADE-OFF EXPLANATOR

To comply with **Engineering Law 4 (Educational and Planning-Oriented Only)** and the "always explain, never alarm" UX directive, the WSE uses a deterministic Natural Language Generation (NLG) template engine. This translates raw numeric matrices into a structured, educational strategic explanation.

### 4.1. NLG Rule-Based Routing
*   *If Deferral Risk is High*: Compute estimated compounding damage and explain the structural physics.
*   *If Bundled Savings is Available*: Detail the overlapping overheads (e.g., scaffolding, dumpster hire, permits) to illustrate the logical value.

### 4.2. Example NLG Generated Text
> **"Comparing Your Envelope Options: Strategic Trade-Off Analysis"**
> 
> *   **The Cost of Deferral (Scenario A vs. Scenario B)**:  
>     *"While waiting three years to replace your roof (Scenario B) preserves $12,500 in near-term capital, it introduces significant structural risks. Shingles on the south slope have entered their final wear phase. Deferring replacement raises the risk of water intrusion into the attic drywall by 65%. Over three years, average patch repairs and potential mold remediation are projected to cost between $2,500 and $6,000, which exceeds the cost of acting today. Additionally, you forego $450 in cumulative energy savings."*
> 
> *   **The Value of Bundling (Scenario A vs. Scenario C)**:  
>     *"If you execute both the roof and window projects together in Year 1 (Scenario C), the initial capital requirement is high ($19,800). However, because both trades share exterior scaffolding and dumpster overhead, you capture a **$2,700 multi-trade bundling discount**. Furthermore, sealing the roof and window boundaries simultaneously maximizes your thermal envelope, driving annual energy costs down by an estimated $450 starting in Year 1, while elevating your indoor comfort index to Elite."*

---

## 5. API DATA CONTRACT (SAMPLE COMPARISON JSON)

```json
{
  "scenario_comparison_id": "scen-compare-roof-windows",
  "scenarios": [
    {
      "scenario_id": "scen-a-immediate",
      "name": "Replace Roof Now",
      "immediate_capital_outlay": 12500.0,
      "bundle_discount_applied": 0.0,
      "ten_year_cumulative_maintenance": 400.0,
      "ten_year_cumulative_energy_savings": 1500.0,
      "safety_hazard_score": 10.0,
      "envelope_integrity_score": 92.0,
      "comfort_increment": 1.5,
      "project_ids": ["proj-roof-202"]
    },
    {
      "scenario_id": "scen-b-wait",
      "name": "Wait Three Years",
      "immediate_capital_outlay": 0.0,
      "bundle_discount_applied": 0.0,
      "ten_year_cumulative_maintenance": 3900.0,
      "ten_year_cumulative_energy_savings": 1050.0,
      "safety_hazard_score": 3.0,
      "envelope_integrity_score": 55.0,
      "comfort_increment": 0.0,
      "project_ids": ["proj-roof-deferred-202"]
    },
    {
      "scenario_id": "scen-c-bundled",
      "name": "Replace Roof & Windows Together",
      "immediate_capital_outlay": 19800.0,
      "bundle_discount_applied": 2700.0,
      "ten_year_cumulative_maintenance": 600.0,
      "ten_year_cumulative_energy_savings": 4500.0,
      "safety_hazard_score": 10.0,
      "envelope_integrity_score": 98.0,
      "comfort_increment": 4.5,
      "project_ids": ["proj-roof-202", "proj-windows-104"]
    }
  ],
  "nlg_analysis": {
    "deferral_narrative": "While waiting three years (Scenario B) delays capital spend, it increases failure probability to 65%, risking water damage that exceeds the cost of near-term stabilization.",
    "bundling_narrative": "Bundling the projects (Scenario C) captures $2,700 in combined contractor mobilizations, lowering your effective average cost per project and delivering immediate, peak thermal envelope insulation."
  }
}
```

---

## 6. STRATEX COMMAND-CENTER WHAT-IF STYLING

The Scenario Sandbox operates as a side-by-side comparative grid in the central viewport of the Habitat platform.

### 5.1. UI Fonts & Typography
*   **Scenario Names**: Outfit (medium, tracking-wide).
*   **Financial Metrics**: JetBrains Mono for clean columnar data alignment.
*   **NLG Strategy Narratives**: IBM Plex Sans with leading-relaxed sizing for comfortable long-form reading.

### 5.2. Visual Styling Tokens
*   **Best Value Path Highlight**: Thin solid border in Electric Teal (`#00F0FF`) with a faint, translucent teal background panel.
*   **Deferred Risk Indicators**: Safety Orange (`#FF9E00`) text highlights on high cumulative maintenance metrics.
*   **Bundled Discount Banner**: Solid black banner with Neon Green (`#39FF14`) JetBrains Mono text: `[ BUNDLE UNLOCKED: SAVES $2,700 ]`.
