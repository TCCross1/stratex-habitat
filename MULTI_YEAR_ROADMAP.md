# CENTCOM DIRECTIVE H-010: MULTI-YEAR ROADMAP
## TIMELINE HORIZONS, DYNAMIC RE-PHASING, & BUDGET OPTIMIZATION SPEC
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW & THE 4 HORIZONS

A home is not static; its physical envelope and mechanical subsystems degrade along distinct, multi-decade wear curves. The **Multi-Year Roadmap (MYR)** engine is Habitat's planning interface. It translates individual capital projects into a coherent, phased timeline structured across four strict chronological planning horizons:

```
+---------------------------------------------------------------------------------+
|                       THE 4 TIMELINE STEWARDSHIP HORIZONS                       |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  HORIZON 1: THE 1-YEAR EMERGENCY & STABILIZATION PLAN (Immediate)               |
|  - Focus: Imminent life safety, active water intrusion, and code violations.    |
|  - Targets: Roof leaks, structural cracks, main panel failures.                 |
|                                                                                 |
|  HORIZON 2: THE 3-YEAR ACTIVE PREVENTION & UTILITY RETROFIT (Near-Term)         |
|  - Focus: Secondary envelope wear, insulation, and high-ROI heating/cooling.    |
|  - Targets: Attics, siding wear, window replacements, air sealing.              |
|                                                                                 |
|  HORIZON 3: THE 5-YEAR STRATEGIC CAPITAL IMPROVEMENT (Medium-Term)              |
|  - Focus: Secondary mechanical systems, hardscaping, energy expansions.         |
|  - Targets: Solar array addition, deck framing, heat pump retrofits.            |
|                                                                                 |
|  HORIZON 4: THE 10-YEAR PRESERVATION & STEWARDSHIP PLAN (Long-Term)             |
|  - Focus: Cosmetic aging, major structural replacements, and legacy handoffs.  |
|  - Targets: Master bath remodeling, driveway concrete, exterior paint cycles.   |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

---

## 2. THE DYNAMIC RE-PHASING ALGORITHM

A roadmap is only useful if it can adapt to the homeowner’s financial reality. The MYR engine implements a **Dynamic Re-Phasing & Budget-Cap Algorithm** that automatically shifts projects across horizons when annual budget caps are modified, while strictly preserving dependency paths.

### 2.1. Mathematical Optimization Model
Given:
*   A set of candidate projects $J$.
*   A Priority Index Score $P_j$ for each project $j \in J$ (computed by the Priority Engine).
*   Estimated costs $C_j$ (computed by the ROI Model).
*   A set of chronological years $t \in \{1, 2, 3, ..., 10\}$.
*   Homeowner-defined annual capital budgets $B_t$ for each year.
*   Dependency constraints $u \to v$ indicating project $u$ must occur before project $v$ (i.e., $t_u < t_v$ or $t_u = t_v$ in separate trades).

### 2.2. Algorithmic Steps for Budget-Cap Re-phasing

```
  [ Fetch All Active Projects ]
                |
                v
  [ Sort by Raw Priority Index Score ]
                |
                v
  [ For Year t = 1 to 10 ]:
        - Identify projects scheduled in year t.
        - Calculate Sum(Cost_j) for scheduled projects.
        - While Sum(Cost_j) > Budget_t:
                - Find the lowest priority project (j_low) in year t with no active successors in year t.
                - Defer j_low to year t + 1.
                - If j_low has downstream successors (j_succ) in years <= t + 1:
                        - Recursively shift j_succ to t + 2 or later to maintain DAG order.
                - Recalculate Sum(Cost_j) for year t.
```

If a high-priority project is pushed past its physical threshold (e.g., deferring an active roof leak beyond Year 1), the engine issues a **Critical Stewardship Warning** explaining the physical consequences and secondary damage risks (such as attic mold or framing rot).

---

## 3. INTERACTIVE HOMEOWNER CONTROLS

The user interface of the Multi-Year Roadmap is designed as an interactive, tactile ledger. It gives homeowners full agency over their planning path without sacrificing physical accuracy.

```
+---------------------------------------------------------------------------------+
|                       10-YEAR ROADMAP STEWARDSHIP CONSOLE                       |
+---------------------------------------------------------------------------------+
| ANNUAL BUDGET: [ Y1: $15k ] [ Y2: $10k ] [ Y3: $10k ] [ Y4: $5k ] [ Y5+: $5k ]  |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [ HORIZON 1: YEAR 1 ] ----------------------------- Budget: $15,000 / Cap: $15k |
|  [::] #1. Roof Shingle Replacement (P: 86.5) ......... [ $12,400 ] [ Verified ] |
|  [::] #2. French Drain Installation (P: 72.1) ........ [  $2,200 ] [ Estimated]|
|                                                                                 |
|  [ HORIZON 2: YEAR 2-3 ] --------------------------- Budget: $8,500  / Cap: $10k |
|  [::] #3. Attic Cellulose Air Sealing (P: 64.0) ...... [  $3,500 ] [ Estimated]|
|  [::] #4. Window Trim Stabilization (P: 48.2) ........ [  $5,000 ] [ Suggested]|
|                                                                                 |
|  [ HORIZON 3: YEAR 4-5 ] --------------------------- Budget: $14,000 / Cap: $5k  |
|  [!!] #5. Solar Array Installation (P: 61.2) ......... [ $14,000 ] [ Suggested] |
|       >>> WARNING: Budget exceeded by $9,000. Drag solar to Year 6 to resolve.  |
|                                                                                 |
|  [ HORIZON 4: YEAR 6-10 ] -------------------------- Budget: $7,200  / Cap: $5k  |
|  [::] #6. Deck Wood Stain & Seal (P: 32.5) ........... [  $1,200 ] [ Verified ] |
|  [::] #7. Bathroom Vanity Upgrade (P: 28.0) .......... [  $6,000 ] [ Preliminary] |
+---------------------------------------------------------------------------------+
```

### 3.1. Tactile Mechanics
*   **Drag-and-Drop Handles `[::]`**: Homeowners can click and drag project cards between horizons.
*   **Budget Sliders**: Sliding scales allow immediate, real-time adjustments of Year-by-Year budget caps.
*   **Downstream Re-sequencing Toggles**: A toggle choice allowing the user to select:
    *   *Automatic Cascade*: Moving a predecessor automatically slides all successors.
    *   *Prompt to Resolve*: Keep the move, but display Orange Dependency Warning cards with "Fix Sequence" shortcuts.

---

## 4. API & STATE PERSISTENCE CONTRACT (SAMPLE JSON)

When a homeowner saves a customized roadmap configuration, the UI sends the serialized order back to the API.

```json
{
  "roadmap_id": "road-morgan-01",
  "last_updated": "2026-07-21T12:15:00Z",
  "yearly_budget_caps": {
    "year_1": 15000.0,
    "year_2": 10000.0,
    "year_3": 10000.0,
    "year_4": 5000.0,
    "year_5": 5000.0,
    "year_6_10_annual": 5000.0
  },
  "allocations": [
    { "project_id": "proj-roof-202", "assigned_year": 1, "priority_override_locked": false },
    { "project_id": "proj-drain-101", "assigned_year": 1, "priority_override_locked": false },
    { "project_id": "proj-airseal-301", "assigned_year": 2, "priority_override_locked": false },
    { "project_id": "proj-trim-104", "assigned_year": 3, "priority_override_locked": false },
    { "project_id": "proj-solar-101", "assigned_year": 4, "priority_override_locked": false },
    { "project_id": "proj-stain-202", "assigned_year": 6, "priority_override_locked": false },
    { "project_id": "proj-bath-401", "assigned_year": 8, "priority_override_locked": false }
  ]
}
```

---

## 5. STRATEX COMMAND-CENTER ROADMAP STYLING

To integrate the Multi-Year Roadmap seamlessly with the Stratex Design System, the interface utilizes the following design tokens:

### 5.1. Color Tokens
*   **Timeline Track**: Deep Obsidian grid lines (`#121212`) over Carbon canvas (`#0A0A0A`).
*   **Active Project Nodes**: Electric Teal (`#00F0FF`) borders with JetBrains Mono numbers.
*   **Over-Budget Violations**: Electric Orange (`#FF9E00`) text overlays with subtle dotted underlines.
*   **Emergency Horizon Indicators**: Safety Neon Red (`#FF3131`) vertical accent bar on the left edge of Horizon 1.

### 5.2. UI Fonts & Typography
*   **Years & Chronological Dividers**: IBM Plex Mono (semibold, lowercase, tracking-wide).
*   **Project Cost Metrics**: JetBrains Mono (high-contrast green `#39FF14` or white `#FFFFFF` based on verification tier).
*   **Stewardship Explanations**: IBM Plex Sans (regular weight, leading-relaxed).
