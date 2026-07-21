====================================================================
CENTCOM DIRECTIVE 014: REPORT DESIGN SYSTEM
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# REPORT DESIGN SYSTEM

This document defines the layout grids, structural requirements, printing parameters, and content formats for all analytical, regulatory, insurance, and contractor reports generated within the Stratex ecosystem.

---

## 1. THE REPORT PHILOSOPHY

Reports are Stratex’s physical and portable extensions of truth. Whether viewed on a screen as an **Interactive Report** or printed to paper as a **PDF**, each document must convey institutional-grade authority, clean Swiss structure, and absolute data precision.

```
       +-----------------------------------------------------------+
       |                  REPORT VISUAL ARCHITECTURES              |
       +-----------------------------------------------------------+
       |   Digital/Interactive Reports                             |
       |     - Background: Surface Dark Theme (#111113)            |
       |     - Features: Live sparklines, interactive filters      |
       |                                                           |
       |   Printable/PDF Reports                                   |
       |     - Background: Pure White Canvas (#FFFFFF)             |
       |     - Features: Static tables, cryptographic verify keys  |
       |     - Constraints: Highly optimized ink coverage          |
       +-----------------------------------------------------------+
```

---

## 2. REPORT STRUCTURAL STANDARDS

Every Stratex report must strictly implement a **4-part modular structure**:

1.  **Administrative Header:**
    *   *Stratex Hexagon Logo* left-aligned.
    *   *Metadata Block* right-aligned: Report Reference UUID, Date of Generation, Primary Operator, and Security Classification Level (e.g. FOUNDATIONAL).
2.  **Executive Summary Callout Block:**
    *   A bold, 1-paragraph synthesis of the entire document.
    *   Key scores (e.g., Property Score) rendered as massive display data text using JetBrains Mono.
3.  **Detailed Analytical Findings:**
    *   Granular data tables with right-aligned values.
    *   Clean timelines with chronological event nodes.
4.  **Verification & Signature Footer:**
    *   A cryptographic stamp or audit verification signature block.
    *   Formal legal text or certification disclaimer.

---

## 3. SPECIFIC REPORT SCHEMAS

We apply the premium report visual language across six targeted categories:

### 3.1 Executive Reports
*   **Target Audience:** Investors, hedge funds, board members.
*   **Aesthetic:** Extremely high-level summary grids, minimal text, bold KPI blocks, and quarterly performance charts.
*   **Key Indicator:** The Financial ROI Projection chart (`recharts`) highlighting portfolio valuation changes.

### 3.2 Habitat Reports
*   **Target Audience:** Homeowners.
*   **Aesthetic:** Warm yet technical. Strict adherence to our linguistic constraint (*always explain, never alarm*).
*   **Key Indicator:** The Home Health Score Breakdown + Energy/Water Efficiency trends over the past 12 months.

### 3.3 Insurance Reports
*   **Target Audience:** Underwriters, adjusters.
*   **Aesthetic:** Highly rigorous, dense tables, complete risk audit history, and verified photos with spatial GPS stamps.
*   **Key Indicator:** The Structural Risk & Material Age DNA card readout, proving structural integrity and safety.

### 3.4 Contractor Reports
*   **Target Audience:** Field builders, crews.
*   **Aesthetic:** Ultra-dense spec checklists, detail blueprints, safety requirements, and material shopping lists.
*   **Key Indicator:** Active action steps with checkbox grids and localized damage photos.

### 3.5 PDF Export Specifications (Print-Safe Rules)
When compiling a document to PDF for printing, the rendering engine must swap active themes:
*   **Backgrounds:** Force `#FFFFFF` (Pure white background) and remove dark panel blocks.
*   **Text:** Force `#111113` on primary copy and `#4B5563` on secondary body copy.
*   **Primary Icons/Dividers:** Force dark grey (`#E5E7EB`) borders instead of neon glowing outlines.
*   **Typography:** Maintain the typography scale, but decrease display sizes by **10%** to ensure standard paper bounds (Letter/A4) are perfectly respected without clipping content.

### 3.6 Interactive Digital Reports
*   **Target Audience:** Operations center, active monitor desks.
*   **Aesthetic:** Deep command-center dark mode. Live scrolling data feeds.
*   **Interactive Features:** Hovering over sparklines displays tooltips with raw sensor metrics; click filters instantly toggle material sub-systems (e.g. filtering a report to show only Plumbing alerts).
