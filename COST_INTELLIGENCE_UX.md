# CENTCOM DIRECTIVE H-009: COST INTELLIGENCE UX SPECIFICATION
## STRATEX-COMPLIANT INTERFACE, TYPOGRAPHY, & INTERACTIVE COST CONTROLS
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. UX Mission & Principles

In the Stratex Design System (SDS), **the house itself is the interface**. The **Cost Intelligence Panel** is a primary sidebar or persistent floating drawer embedded directly inside the **Design Studio 2.0** 3D canvas workspace. It is the financial cockpit of the homeowner’s journey.

All interface elements, copy, and interactions must adhere to three foundational UX rules:
1.  **Always Explain, Never Alarm**: Use supportive, educational language. If a cost jumps, explain the direct physical driver (e.g. "composite cladding requires specialized hidden clips") rather than displaying a raw, unexplained warning.
2.  **Visual Hierarchy & High-Contrast**: Use the Swiss / Command-Center theme (Outfit display, IBM Plex Sans body, and JetBrains Mono for data numbers).
3.  **Progression of Complexity**: Present a clean, high-level cost summary by default, with instant click-to-expand capabilities revealing a complete, itemized line-item ledger.

---

## 2. Cost Intelligence Panel Layout

Below is the ASCII wireframe for the Stratex-compliant Cost Intelligence sidebar.

```
+-------------------------------------------------------------+
| [OUTFIT] COST INTELLIGENCE                             [X]  |
| GEO BASIS: ZIP 80202 (Denver) | PRICE DATE: 2026-07-21      |
+-------------------------------------------------------------+
| EXPECTED PROJECT RANGE (Outfit Display, Bold, #00F0FF)      |
| $31,250 - $34,800                                           |
+-------------------------------------------------------------+
| CONFIDENCE: [ESTIMATED] (Teal solid border, #00F0FF)        |
| Reliability Score: 84/100                                   |
+-------------------------------------------------------------+
| COST SUMMARY BREAKDOWN (Click any row to expand)            |
|                                                             |
| [>] Materials ................................ $12,420.00   |
| [>] Labor .................................... $8,200.00    |
| [>] Equipment & Subcontractors ............... $2,150.00    |
| [>] Permits & Fees ........................... $1,200.00    |
| [>] Contractor Operations & Profit ........... $6,200.00    |
| [>] Contingency Buffer (10%) ................. $3,015.00    |
+-------------------------------------------------------------+
| ACTIVE COST DRIVERS (Hover for physical details)            |
| * Slope Terrain: 1.12x access labor multiplier applied      |
| * Premium James Hardie Iron Gray: +$1,850 material offset   |
+-------------------------------------------------------------+
| INFORMATION NEEDED TO IMPROVE ACCURACY                      |
| [!] Confirm Side Gate Width (Removes 1.15x access risk)     |
| [!] Confirm Soil Compaction (Removes $1,500 rock allowance) |
+-------------------------------------------------------------+
| [ DOWNLOAD PDF BUDGET PACKAGE ]   [ DISPATCH CONTRACTOR RFP]|
+-------------------------------------------------------------+
```

---

## 3. Typography & Styling Tokens

To maintain cohesive branding across the Habitat Design Studio ecosystem, all CSS declarations must map directly to Stratex design tokens:

### 3.1. Fonts
*   **Headers & Titles**: `font-family: 'Outfit', sans-serif;`
*   **Body Copy**: `font-family: 'IBM Plex Sans', sans-serif;`
*   **Currency & Financial Data**: `font-family: 'JetBrains Mono', monospace;`

### 3.2. Color Palettes & States
*   **Background (Surface Primary)**: Dark Obsidian (`#111113`)
*   **Background (Surface Secondary)**: Dark Slate Charcoal (`#1A1A1E`)
*   **Primary Accent / Highlights**: Electric Teal (`#00F0FF`)
*   **Verified Cost Border / Badge**: Electric Green (`#39FF14`)
*   **Suggested Cost Border / Badge**: Safety Neon Orange (`#FF9E00`)
*   **Preliminary / Excluded Border**: Cool Gray (`#9CA3AF`)
*   **Borders & Dividers**: Subdued Zinc (`#27272A`)

---

## 4. Interactive Micro-Interactions

### 4.1. The Click-to-Expand Ledger
When a homeowner clicks the **"Materials"** row, the summary collapses downward, and an itemized ledger slides open with sub-component lines styled in subdued typography.

```
[-] Materials .................................. $12,420.00
    ├── GAF Timberline shingles (SKU: SMC-9) .. $3,420.00 [Ver]
    ├── Synthetic Underlayment ................. $450.00  [Est]
    ├── Ice & Water Barrier (Eaves) ............ $350.00  [Est]
    └── Wood Sheathing panels .................. $8,200.00 [Sug]
```

### 4.2. Hover Tooltips & Explanations
Hovering over any cost-driver line item triggers a tooltip showing the physical reason and the exact logic:

*   **Hover Event**: `Hover (Labor row)`
*   **Tooltip Content (rendered in JetBrains Mono / IBM Plex Sans)**:
    *   *“Baseline labor of 100 hours increased to 112 hours because of a 1.12x height modifier applied to your second-story design. Material lifting takes longer at elevations above 10 feet.”*

### 4.3. Interactive Confidence Actions
Homeowners can click on any item inside the **"Information Needed to Improve Accuracy"** list to resolve variables inside the workspace:

*   **Action Event**: `Click ("Confirm Side Gate Width")`
*   **Interaction**: A slide-out panel asks the homeowner to select:
    *   `[ ] Over 36" (Double gate / Truck access)`
    *   `[ ] Under 36" (Standard single gate)`
    *   `[ ] I'm not sure (Schedule a free local field measure)`
*   **Resolution**: Selecting "Over 36"" instantly recalculates the estimate, drops the $420 access multiplier, removes the item from the checklist, and raises the project confidence score by 5 points.

By providing a responsive, educational, and high-fidelity interface, the Cost Intelligence UX panel transforms cost tracking from a chore into an interactive design exploration.
