# CENTCOM DIRECTIVE H-010: PROJECT PRIORITY ENGINE
## MULTI-FACTOR MATHEMATICAL PRIORITIZATION & STRATEGIC RANKING SPEC
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW

The **Project Priority Engine (PPE)** is the primary analytical sub-system of the Home Investment Intelligence™ platform. Its responsibility is to answer the homeowner’s most fundamental question:
> *"What should I do first, and what can wait?"*

Rather than relying on arbitrary urgency tiers or simple cost rankings, the PPE executes a multi-factor mathematical assessment of every active, planned, and suggested project. It synthesizes physical property health data, structural degradation telemetry, localized weather vulnerabilities, homeowner life-goals, and financial parameters into a single, explainable **Priority Index Score ($P$)** from `0` (lowest priority) to `100` (critical priority).

```
  [ Physical Property DNA ]           [ Environmental Telemetry ]          [ Homeowner Goals ]
 - Remaining Useful Life (RUL)       - Local Climate Weather Load        - Comfort & Usability
 - Structural Integrity Ratings      - Extreme Exposure Risk             - Efficiency Objectives
             |                                    |                                 |
             +------------------------------------+---------------------------------+
                                                  |
                                                  v
                                    +---------------------------+
                                    |  PROJECT PRIORITY ENGINE  |
                                    +---------------------------+
                                                  |
                                                  v
                                     [ Explainable Priority Score ]
                                     - Index: 0 to 100
                                     - Color-Coded Tiers
                                     - Dependency Lock-Adjustment
```

---

## 2. THE MULTI-FACTOR RANKING MATHEMATICAL FORMULA

Each project $j$ is evaluated across eight distinct, normalized criteria, each rated on a standard scale of `0.0` (no impact/degradation) to `10.0` (maximum impact/imminent failure).

### 2.1. Formula Variables & Inputs

| Variable | Metric Name | Metric Range | Logical Definition |
| :---: | :--- | :---: | :--- |
| $H_j$ | **Property Health Impact** | $0.0 - 10.0$ | Physical consequence of project on surrounding structural/envelope assets if omitted. |
| $S_j$ | **Safety & Hazard Priority** | $0.0 - 10.0$ | Life safety, structural stabilization, fire risk, or hazardous material mitigation. |
| $W_j$ | **Weather Exposure Urgency** | $0.0 - 10.0$ | Urgency relative to seasonal exposure (e.g., roof leak before winter, drainage before spring runoff). |
| $M_j$ | **Maintenance Reduction** | $0.0 - 10.0$ | Elimination of recurring operational costs or emergency service call risks. |
| $E_j$ | **Energy Performance** | $0.0 - 10.0$ | Degree of thermal envelope improvement, HERS-rating impact, or carbon-offset. |
| $D_j$ | **Useful Life Degradation** | $0.0 - 10.0$ | Measures component wear based on remaining useful life: $D_j = 10 \times \left(1 - \frac{\text{RUL}_j}{\text{Useful Life}_j}\right)$. |
| $G_j$ | **Goal & Comfort Alignment** | $0.0 - 10.0$ | Stated homeowner preferences (e.g., comfort, aesthetic appeal, functional space expansion). |
| $B_j$ | **Budget Efficiency Index** | $0.0 - 10.0$ | Cost-effectiveness: ratio of structural/health score benefit to estimated cost. |

### 2.2. The Priority Index Formula

The raw priority index ($P_{\text{raw},j}$) is a weighted linear combination of the eight factor scores:

$$P_{\text{raw},j} = w_H H_j + w_S S_j + w_W W_j + w_M M_j + w_E E_j + w_D D_j + w_G G_j + w_B B_j$$

Where the weights ($w_i$) are calibrated to place the highest priority on structural safety and envelope integrity, totaling exactly $10.0$ to ensure a maximum score of $100.0$:

| Weight | Parameter Name | Value | Percentage of Raw Score |
| :---: | :--- | :---: | :---: |
| $w_S$ | Safety Weight | $2.0$ | $20\%$ |
| $w_H$ | Property Health Weight | $1.5$ | $15\%$ |
| $w_W$ | Weather Exposure Weight | $1.5$ | $15\%$ |
| $w_D$ | Degradation Weight | $1.5$ | $15\%$ |
| $w_M$ | Maintenance Weight | $1.0$ | $10\%$ |
| $w_E$ | Energy Weight | $1.0$ | $10\%$ |
| $w_G$ | Goal Alignment Weight | $1.0$ | $10\%$ |
| $w_B$ | Budget Efficiency Weight | $0.5$ | $5\%$ |

### 2.3. The Dependency-Lock Adjustment ($\beta_{\text{dep}}$)

If project $j$ has predecessor dependencies (e.g., Solar Installation depends on Roof Replacement) that have *not* been marked as Completed or scheduled in the same planning phase, the final priority score ($P_j$) is adjusted by a dependency multiplier:

$$P_j = P_{\text{raw},j} \times \beta_{\text{dep}}$$

Where:
*   $\beta_{\text{dep}} = 1.0$: All physical and logical predecessor projects are completed or scheduled first.
*   $\beta_{\text{dep}} = 0.4$: Project is physically "locked" because a critical predecessor has not been planned, reducing its rank so the homeowner is guided to address the foundational project first.

---

## 3. ENGINE LOGIC & FLOW ALGORITHM

The Priority Engine executes on a recurring background loop and triggers immediately upon any change to the Property DNA database, Design Studio scenarios, or homeowner preference settings.

```
                  +-----------------------------------+
                  |  START: Trigger Evaluation Cycle  |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Fetch active projects & assets  |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Compute RUL Degradation Factor  |
                  |     D_j = 10 * (1 - RUL / UL)     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Evaluate Health, Safety, Weather |
                  |    and Efficiency factor scores   |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Assess dependency status (DAG)  |
                  |     If unresolved: beta = 0.4     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Compute Final Priority Index:   |
                  |      P_j = P_raw,j * beta_dep     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  | Sort Portfolio Queue by Priority  |
                  +-----------------------------------+
```

---

## 4. API & DATA CONTRACT (SAMPLE JSON)

Below is the API payload representing a computed priority score for a roof replacement project.

```json
{
  "project_id": "proj-roof-001",
  "title": "Roof Shingle Replacement (South Slope)",
  "priority_metadata": {
    "raw_priority_score": 86.5,
    "adjusted_priority_score": 86.5,
    "priority_tier": "HIGH",
    "dependency_status": {
      "has_dependencies": false,
      "unresolved_predecessors": [],
      "multiplier_applied": 1.0
    },
    "factor_contributions": [
      { "factor": "Safety & Hazard", "score": 8.0, "weight": 2.0, "contribution": 16.0 },
      { "factor": "Property Health", "score": 9.5, "weight": 1.5, "contribution": 14.25 },
      { "factor": "Weather Urgency", "score": 9.0, "weight": 1.5, "contribution": 13.5 },
      { "factor": "Remaining Life Degradation", "score": 9.2, "weight": 1.5, "contribution": 13.8 },
      { "factor": "Maintenance Reduction", "score": 7.5, "weight": 1.0, "contribution": 7.5 },
      { "factor": "Energy Performance", "score": 6.0, "weight": 1.0, "contribution": 6.0 },
      { "factor": "Goal Alignment", "score": 10.0, "weight": 1.0, "contribution": 10.0 },
      { "factor": "Budget Efficiency", "score": 10.9, "weight": 0.5, "contribution": 5.45 }
    ],
    "explanation": "This project is ranked as High Priority because the south-facing shingles have experienced severe UV-chalking, leaving only 2 years of remaining useful life. Postponing this project threatens the structural deck with water intrusion during winter freeze-thaw cycles."
  }
}
```

---

## 5. STRATEX COMMAND-CENTER UI STANDARDS

To preserve Stratex command-center ergonomics and ensure non-alarmist communication, priority is represented using clean, structured visual indicators rather than red danger flags.

### 5.1. UI Fonts & Typography
*   **Header Labels**: Outfit (semibold/medium) for clear structure.
*   **Quantitative Scores**: JetBrains Mono for a highly precise, technical feel (e.g., `86.5/100`).
*   **Text Descriptions**: IBM Plex Sans for technical and educational readability.

### 5.2. Visual Priority Tiers & Color Tokens
Priority is divided into four structural tiers, styled according to the design system:

*   **TIER 1 — IMMEDIATE (Critical)**:
    *   **Trigger**: $P_j \ge 85.0$
    *   **Color**: Safety Neon Red (`#FF3131`)
    *   **Language Guidelines**: Supportive but firm. Focus on mitigating risk. *"Active wear detected. Scheduled stabilization recommended to protect structural integrity."* (Never say: *"Your roof is going to collapse!"*)
*   **TIER 2 — STRATEGIC (High)**:
    *   **Trigger**: $70.0 \le P_j < 85.0$
    *   **Color**: Electric Orange (`#FF9E00`)
    *   **Language Guidelines**: Focus on timeline optimization. *"Optimal planning window is open. Addressing this project now prevents secondary repair overhead."*
*   **TIER 3 — SCHEDULED (Medium)**:
    *   **Trigger**: $45.0 \le P_j < 70.0$
    *   **Color**: Command Teal (`#00F0FF`)
    *   **Language Guidelines**: Emphasis on long-term stewardship. *"Planned maintenance cycle. Align with secondary upgrades to optimize trade mobilization."*
*   **TIER 4 — DEFERRED (Low)**:
    *   **Trigger**: $P_j < 45.0$
    *   **Color**: Slate Gray (`#9CA3AF`)
    *   **Language Guidelines**: Highlighting stable health. *"In stable monitoring status. Remaining useful life is sufficient; no immediate intervention required."*
