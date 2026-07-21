# CENTCOM DIRECTIVE H-010: PROJECT PORTFOLIO DASHBOARD
## CONTROL ROOM GRID SECTORS, READINESS METRICS, & GRAPHICAL DASHBOARD SPEC
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW & COMMAND SHELL

The **Project Portfolio Dashboard (PPD)** is the primary operational workspace of the STRATEX HABITAT™ application. Grounded in the **UX guidelines (the house itself is the interface)**, the PPD provides a multi-panel, high-density, dark control-room view. It is engineered to give homeowners a clean, investor-grade interface to monitor past execution, manage active schedules, and review future capital requirements in real-time.

### 1.1. Physical Layout Integration
The Dashboard integrates into the standard Stratex desktop command shell layout:
*   **Left Icon Rail**: Compact, high-contrast navigation shortcuts.
*   **Central Digital Twin Viewport**: Holds the high-fidelity 3D model of the home, acting as the main interface. Clickable asset hot-spots (e.g., Roof, Windows) highlight corresponding cards on the dashboard.
*   **Bottom Viewport**: The multi-panel portfolio grid.
*   **Right Inspector Panel**: Displays dynamic context-aware S.A.C.U. cost ledgers and contractor bid responses.

---

## 2. THE SIX CORE GRID SECTORS

The dashboard is structured into six high-density telemetry sectors. Each sector presents a distinct aspect of the property’s physical and capital status:

```
+---------------------------------------------------------------------------------+
|                       PORTFOLIO CONTROL ROOM GRID SECTORS                       |
+---------------------------------------------------------------------------------+
|  SECTOR 1: COMPLETED PROJECTS           |  SECTOR 2: PLANNED PROJECTS           |
|  - Historical pedigree ledger.          |  - Scheduled active pipeline.         |
|  - Populates the Digital Passport.      |  - Bound to active budget caps.       |
|                                         |                                       |
|-----------------------------------------+---------------------------------------|
|  SECTOR 3: DEFERRED PROJECTS            |  SECTOR 4: MAINTENANCE PROJECTS       |
|  - Projects outside the 5-Yr horizon.   |  - Preventative care & service cycles.|
|  - Actively monitors wear penalties.    |  - Linked to local service trades.    |
|                                         |                                       |
|-----------------------------------------+---------------------------------------|
|  SECTOR 5: EST. FUTURE INVESTMENT       |  SECTOR 6: PROJECT READINESS          |
|  - 10-Year cumulative cash flow chart.  |  - Checklist indicators per project.  |
|  - Interactive budget sliders.          |  - Permits, Materials, Contractor.    |
+---------------------------------------------------------------------------------+
```

### 2.1. Sector 1: Completed Projects
*   **Objective**: Display the chronological history of verified repairs, upgrades, and audits.
*   **The Experience**: Clicking a completed project expands the "Digital Passport Verification Certificate," showing the completing contractor's license, the building permit sign-off, and the material warranty IDs.
*   **Visual Key**: Neon Green outline (`#39FF14`) indicating verified and completed.

### 2.2. Sector 2: Planned Projects
*   **Objective**: Show capital improvements scheduled in Years 1-5.
*   **The Experience**: Tracks the progression of each scheduled project from "Scribing" to "Contractor Bidding" to "Scheduled."
*   **Visual Key**: Command Teal (`#00F0FF`) indicating active planning.

### 2.3. Sector 3: Deferred Projects
*   **Objective**: Track projects deliberately pushed to Year 6+ or placed on "Stable Monitoring" status.
*   **The Experience**: Displays a live Remaining Useful Life (RUL) bar that slowly shifts color as the component ages, reminding the homeowner that deferral is a temporary capital-preservation tactic, not a permanent fix.
*   **Visual Key**: Muted Slate Gray (`#9CA3AF`).

### 2.4. Sector 4: Maintenance Projects
*   **Objective**: Focus on short-term preventative maintenance (e.g., annual HVAC tuning, gutter cleaning, deck staining).
*   **The Experience**: Linked directly to seasonal weather exposure alerts.
*   **Visual Key**: Subtle dotted Teal outlines.

### 2.5. Sector 5: Estimated Future Investment
*   **Objective**: Render long-term capital cash-flow requirements.
*   **The Experience**: Displays a high-contrast Recharts-based bar chart representing annual capital expenditures over the 10-year horizon.
*   **Interaction**: Adjusting the budget sliders in the Multi-Year Roadmap dynamically updates the height of these bars in real-time, showing which years are over-cap and which projects have cascaded.

### 2.6. Sector 6: Project Readiness Indicators
*   **Objective**: Grade how prepared a planned project is for execution across four critical checkboxes:
    1.  `Budget`: Are funds allocated within the target year's budget cap?
    2.  `Permit`: Is the municipal building permit filed or approved?
    3.  `Materials`: Are specific manufacturer SKUs selected in the Design Studio?
    4.  `Contractor`: Is a contractor bid accepted or under active review?
*   **The Experience**: Rendered as a compact 4-segment indicator. A project is fully "Ready" when all four segments are filled.

---

## 3. UI ARCHITECTURE & MOCKUP

Below is an ASCII representation of the bottom dashboard panel showing the grid layout:

```
+-------------------------------------------------------------------------------------------------------+
|  PORTFOLIO CONTROL PANEL                                                               [x] EXPAND GRID|
+-------------------------------------------------------------------------------------------------------+
| COMPLETED [Y1-Y5]                     | PLANNED PIPELINE [Y1]                 | PROJECT READINESS     |
| > Heat Pump Retrofit ... 2026-06 [v]  | [::] Roof Replacement . $12,500 [Est] | Roof Replacement:     |
| > Attic Air Seal ....... 2026-06 [v]  |      Assigned: Year 1                 | [X] Budget  [X] SKU   |
| > Sewer Scope Audit .... 2026-05 [v]  | [::] French Drain ...... $2,200 [Ver] | [ ] Permit  [X] Cont. |
|                                       |      Assigned: Year 1                 | Status: [ 75% READY ] |
|---------------------------------------+---------------------------------------+-----------------------|
| DEFERRED LINE-ITEMS                   | SEAS. MAINTENANCE                     | 10-YEAR ESTIMATED INVESTMENT  |
| > Solar Array [Y6] ... $14,000 [Sug]  | > HVAC Tune-up ... Jul 2026 ... [Bid] |  Cost                 |
|   RUL Shingle Shielding check: OK     | > Gutter Clean ... Oct 2026 ... [Sch] |   $15k|  __           |
| > Driveway Concrete ... $8,000 [Pre]  | > Deck Seal ...... May 2027 ... [Ver] |   $10k| |  | __       |
|   RUL Shingle Shielding check: OK     |                                       |    $5k| |  | |  | __  |
|                                       |                                       |     +--+--+--+--+--+->|
|                                       |                                       |        Y1 Y2 Y3 Y4 Y5 |
+-------------------------------------------------------------------------------------------------------+
```

---

## 4. INTEGRATION & HANDSHAKE PATHWAYS

The Portfolio Dashboard is not a static view; it functions as a live data-consumer that coordinates with multiple subsystems:

### 4.1. Handshake with Design Studio 2.0
When a homeowner customizes a material scenario in the Design Studio (e.g., swapping vinyl siding for vertical cedar panels) and clicks "Save Scenario to Portfolio," the WSE and PPE trigger immediately. The new siding project is registered as "Planned" on the Dashboard, its priority score is calculated, its readiness checkboxes are initialized, and its cost range updates the 10-Year Estimated Investment chart.

### 4.2. Handshake with STRATEX Core
When a licensed contractor or auditor publishes a new report via the Core API handshake:
1.  A new "Finding" card is generated on the Central Digital Twin.
2.  The PPE evaluates the priority. If it's an envelope hazard, it is classified under "Horizon 1" on the dashboard.
3.  The Home Investment Score is updated on the HUD.

---

## 5. STRATEX COMMAND-CENTER DESIGN TOKENS

To ensure consistency with the STRATEX design system, the dashboard utilizes the following tokens:

### 5.1. UI Fonts & Typography
*   **Grid Headings**: Outfit (medium, lowercase, letter-spacing wide).
*   **Project Line-Items & Metrics**: JetBrains Mono for perfect horizontal alignment and numerical readability.
*   **Status Badges & Descriptions**: IBM Plex Sans.

### 5.2. Color Tokens
*   **Dashboard Canvas**: Darkest Obsidian (`#050505`) with a border-top divider in IBM Plex Gray (`#1E1E1E`).
*   **Completed Nodes**: Neon Green (`#39FF14`).
*   **Planned/Active Nodes**: Electric Teal (`#00F0FF`).
*   **Deferred/Monitoring Nodes**: Slate Gray (`#9CA3AF`).
*   **Urgent Warnings/Over-budget Flags**: Safety Orange (`#FF9E00`) or Neon Red (`#FF3131`) based on severity.
