# CENTCOM DIRECTIVE H-003: PROJECT MATCHING ENGINE
## ALGORITHMIC SPECIFICATION & TRUST-BASED SCORING MECHANICAL DESIGN
**Version:** 1.0  
**Author:** Lead Algorithms Engineer  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction

The **Habitat Matching Engine™** is a multi-criteria decision-making scoring engine. Its primary objective is to match homeowners’ detailed Project Opportunity Packages (POPs) with the most qualified, capable, and reliable local contractors.

Unlike traditional marketplace algorithms that prioritize paid placements, advertising tiers, or hidden platform fees (which lead to manipulative rankings and poor matches), **the Habitat Matching Engine is completely transparent, deterministic, and objective.** There are no hidden ranking manipulations. Both contractors and homeowners can inspect the factors and scores driving matches.

---

## 2. Core Scoring Architecture

The engine calculates a composite **Opportunity Match Score (OMS)** for each contractor-project pair. The score is a normalized value between `0.00` and `100.00`, calculated using eleven distinct weighted ranking factors.

```
                  +----------------------------------------------+
                  |           Habitat Matching Engine            |
                  +----------------------------------------------+
                                         |
     +-----------------+-----------------+-----------------+-----------------+
     |                 |                 |                 |                 |
     v                 v                 v                 v                 v
+----------+      +----------+      +----------+      +----------+      +----------+
|  Trade   |      |  Trust   |      | Physical |      | Capacity |      | Past Per-|
| Alignment|      |  Grade   |      | Proximity|      | & Sched. |      | formance |
+----------+      +----------+      +----------+      +----------+      +----------+
     |                 |                 |                 |                 |
     +-----------------+-----------------+-----------------+-----------------+
                                         |
                                         v
                         +--------------------------------+
                         | Opportunity Match Score (OMS)  |
                         |        Range: 0 - 100          |
                         +--------------------------------+
```

### 2.1. Mathematical Formula
For any given project $P$ and contractor $C$, the Opportunity Match Score $OMS(P, C)$ is expressed as:

$$OMS(P, C) = \sum_{i=1}^{11} \left( F_i(P, C) \times W_i \right) \times G_{\text{critical}}(P, C)$$

Where:
* $F_i(P, C)$ is the normalized score $(0.0 \text{ to } 10.0)$ for factor $i$.
* $W_i$ is the weight assigned to factor $i$, where $\sum W_i = 10.0$.
* $G_{\text{critical}}(P, C)$ is the **Critical Gatekeeper Multiplier** $(0 \text{ or } 1)$, which immediately disqualifies any contractor who fails to meet non-negotiable legal, license, or structural insurance requirements.

---

## 3. The 11 Weighted Ranking Factors

The weights and scoring criteria for the eleven ranking factors are detailed below.

### Factor 1: Trade Specialty ($W_1 = 1.50$) - Gatekeeper Component
* **Description:** Measures the alignment between the project type (e.g., Roof, Solar, Pool) and the contractor’s registered primary and secondary trade specialties in their profile.
* **Scoring Logic:**
  * *Primary Match:* 10.0 (e.g., roofing contractor matching a Roof project).
  * *Secondary Match:* 6.0 (e.g., general builder matching a Roof project).
  * *No Match / Cross-Disciplinary Match:* 0.0 (and triggers a Critical Gatekeeper failure if the project requires a specialized trade).

### Factor 2: Active & Verified Licenses ($W_2 = 1.50$) - Critical Gatekeeper
* **Description:** Checks if the contractor possesses valid, active municipal and state licenses required to perform the specified project type within the property’s local jurisdiction.
* **Scoring Logic:**
  * *Fully Verified & Active:* 10.0.
  * *Any Expired, Suspended, or Missing Required License:* 0.0 (Triggers $G_{\text{critical}} = 0$).

### Factor 3: Physical Distance & Travel ($W_3 = 1.00$)
* **Description:** Calculates the driving distance between the contractor’s operating base (or service boundary) and the property address.
* **Scoring Logic:**
  * Distance $D \le 10 \text{ miles}$: 10.0.
  * $10 \text{ miles} < D \le 25 \text{ miles}$: $10.0 - 0.4 \times (D - 10)$.
  * $25 \text{ miles} < D \le 50 \text{ miles}$: $4.0 - 0.16 \times (D - 25)$.
  * $D > 50 \text{ miles}$: 0.0.
  * *Note:* If $D$ exceeds the homeowner’s *Preferred Contractor Distance*, the score is capped at a maximum of 3.0.

### Factor 4: Real-time Availability ($W_4 = 1.00$)
* **Description:** Compares the homeowner's *Desired Timeline* against the contractor’s active crew schedules, backlog pipeline, and seasonal availability declared in the portal.
* **Scoring Logic:**
  * *Perfect Match (Crew open during requested start date):* 10.0.
  * *Minor Shift (Available within $\pm 2$ weeks of desired start):* 7.0.
  * *Major Shift (Available within $\pm 4$ weeks of desired start):* 4.0.
  * *No overlap / Overbooked:* 0.0 (Disqualifies the contractor from automatic routing).

### Factor 5: Trust Grade ($W_5 = 1.20$)
* **Description:** Habitat's internal integrity metric. It is calculated based on background checks, financial stability reviews, unresolved homeowner disputes, and years of registered platform service.
* **Scoring Logic:**
  * *Trust Grade A+ / A:* 10.0.
  * *Trust Grade B:* 7.5.
  * *Trust Grade C:* 4.0.
  * *Trust Grade D / F:* 0.0 (Triggers $G_{\text{critical}} = 0$, removing them from the ecosystem).

### Factor 6: Project Experience & Complexity Matching ($W_6 = 0.80$)
* **Description:** Evaluates the contractor's historical experience with the specific scale and complexity level of the opportunity.
* **Scoring Logic:**
  * Evaluates the contractor's lifetime volume of completed projects on Habitat within the same budget tier and complexity category.
  * *Over 20 projects at equal/greater complexity:* 10.0.
  * *5 to 19 projects:* 7.5.
  * *1 to 4 projects:* 4.0.
  * *0 projects (New contractor or scaling up):* 2.0 (To allow new, highly qualified contractors to onboard, we assign a baseline score and combine it with a "Mentorship" tag).

### Factor 7: Response Time & Engagement ($W_7 = 0.80$)
* **Description:** Measures the contractor's historical responsiveness to inquiries, clarifications, and quote requests over the past 90 days.
* **Scoring Logic:**
  * *Average response under 2 hours:* 10.0.
  * *Average response 2 to 12 hours:* 8.0.
  * *Average response 12 to 24 hours:* 5.0.
  * *Average response over 24 hours:* 1.0.

### Factor 8: Customer Rating ($W_8 = 0.80$)
* **Description:** The normalized, verified review score submitted by homeowners upon project verification and sign-off.
* **Scoring Logic:**
  * Average rating $R$ (from 1.0 to 5.0 stars): Score $= 2.0 \times R$.
  * *Example:* A 4.8-star contractor receives a score of 9.6.
  * *Zero Reviews:* Deaults to 7.0 to prevent penalizing new contractors, but displays a "New Provider" badge.

### Factor 9: Insurance Coverage ($W_9 = 0.50$) - Gatekeeper Component
* **Description:** Verifies that the contractor carries active General Liability and Workers' Compensation insurance policies that meet or exceed the values required for the project's complexity.
* **Scoring Logic:**
  * *Active coverage exceeding required limits:* 10.0.
  * *Active coverage meeting exact limits:* 8.0.
  * *Inadequate or Expired Coverage:* 0.0 (Triggers $G_{\text{critical}} = 0$).

### Factor 10: Warranty Programs ($W_{10} = 0.40$)
* **Description:** Evaluates the quality and duration of the contractor's labor warranty and their certification level with material manufacturers (allowing them to offer extended material warranties).
* **Scoring Logic:**
  * *Lifetime Labor Warranty + Certified Manufacturer Installer:* 10.0.
  * *5-10 Year Labor Warranty + Certified Installer:* 8.0.
  * *1-4 Year Standard Labor Warranty:* 5.0.
  * *No written labor warranty:* 0.0.

### Factor 11: Previous Similar Projects ($W_{11} = 0.50$)
* **Description:** Analyzes the physical and materials similarity of the contractor's past portfolios against the selected materials and design of the current POP.
* **Scoring Logic:**
  * Uses vector embeddings of material SKUs, architectural styles, and square footage to check historical alignment.
  * *High material/style overlap (>80% similarity):* 10.0.
  * *Moderate overlap (50-79% similarity):* 6.0.
  * *Low/No direct overlap (<50% similarity):* 2.0.

---

## 4. The Critical Gatekeepers ($G_{\text{critical}}$)

The gatekeepers protect homeowners from risk. If any of the following mandatory checks fail, $G_{\text{critical}}$ is set to `0`, which immediately forces $OMS = 0.00$, making the contractor ineligible to view, receive, or bid on the opportunity:

1. **Licensing Failure:** Lacking an active license matching the required classification for the municipal ZIP code of the property.
2. **Insurance Failure:** Lacking active general liability or worker's compensation insurance.
3. **Severe Trust Failure:** A current Trust Grade of D or F, or any active platform suspensions.
4. **Safety Failure:** Undisclosed safety violations or active legal stop-work orders.

---

## 5. Matchmaking & Lead Routing Workflow

The Matching Engine operates in a dual-phase routing sequence:

```
+--------------------------------------------------------------------------+
|  PHASE 1: FILTER & IDENTIFY                                              |
|  - System parses Project Opportunity Package (POP)                       |
|  - Queries database for active contractors within service area           |
|  - Evaluates Critical Gatekeepers (G_critical = 1)                       |
|  - Computes OMS for all eligible contractors                             |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|  PHASE 2: MATCH & DISPATCH                                               |
|  - Ranks contractors by OMS                                              |
|  - Identifies "Top 3 Optimal Matches" (OMS >= 85.00)                     |
|  - Delivers secure, anonymized Project summaries to matched profiles     |
|  - Contractors review full scope and accept/decline bidding              |
+--------------------------------------------------------------------------+
```

### 5.1. Transparent Pricing Assurance
Contractors do **not** pay to access specific opportunities. Instead, matching is based purely on the algorithmic alignment of their capabilities with the homeowner's project. This ensures contractors only receive opportunities they are highly qualified to execute, reducing wasted overhead and bidding costs.
