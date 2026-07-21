# CENTCOM DIRECTIVE H-003: HOMEOWNER COMPARISON WORKSPACE
## TRANSPARENT, MULTI-DIMENSIONAL PROPOSAL EVALUATION DESIGN
**Version:** 1.0  
**Author:** Lead UX/UI Designer  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction & Design Philosophy

Selecting a contractor to perform major structural work on a home is often stressful for homeowners. Traditional portals offer little help, leaving homeowners with fragmented, paper-based bids, hidden fees, and manipulated rankings.

The **Habitat Homeowner Comparison Workspace** is designed to provide complete transparency. It aggregates all submitted contractor proposals into an interactive, side-by-side comparison matrix. **There is absolutely no hidden ranking manipulation.** Proposal sorting, filtering, and scoring are driven entirely by explicit homeowner preferences and verified contractor performance data.

```
+-----------------------------------------------------------------------------------+
|                        THE HOMEOWNER COMPARISON DASHBOARD                         |
+-----------------------------------------------------------------------------------+
|  [ Matrix View ]       [ Proposal Details ]       [ Interactive Chat & Q&A ]      |
|  - Price Breakdown     - Material Sheets          - Message Contractor            |
|  - Trust Grades        - Warranties               - Schedule Site Visits          |
|  - Expected Timelines  - Past Portfolios          - Finalize Contracts            |
+-----------------------------------------------------------------------------------+
```

---

## 2. The 8 Evaluation Dimensions

To provide a complete, well-rounded view of each proposal, Habitat evaluates and ranks bids across eight key dimensions:

| Dimension | Description | Verification Method |
| :--- | :--- | :--- |
| **Price** | Total bottom-line project investment, including itemized materials, labor, and municipal permits. | Extracted from structured contractor bid line items. |
| **Timeline** | Estimated start date, weekly progress schedule, and total project duration. | Automatically compared against the homeowner's required completion date. |
| **Warranty** | Duration and depth of structural, craftsmanship, and manufacturer-backed warranties. | Verified against manufacturer registration databases. |
| **Portfolio** | Authenticated historical projects of similar scale, style, and material choice. | Linked directly to verified work logs in the Digital Passport registry. |
| **Trust Grade** | The contractor's verified rating based on background checks, financial health, and dispute history. | Monitored and calculated daily by Habitat's Trust and Safety system. |
| **Communication** | Responsiveness score, support channel availability, and client satisfaction ratings. | Calculated from real-time platform chat metadata and post-project reviews. |
| **Experience** | Cumulative lifetime volume of successfully completed, verified projects on Habitat. | Immutably logged in the platform's contractor registry database. |
| **Availability** | Real-time scheduling alignment with the homeowner's desired timeline. | Cross-referenced with the contractor's active scheduling calendar. |

---

## 3. Comparison Workspace Layout & Interface Design

The workspace UI is structured as a clear, side-by-side matrix, allowing homeowners to quickly compare bids and filter them based on their specific priorities.

```
+-----------------------------------------------------------------------------------------+
| COMPARISON SYSTEM: Exterior Siding Overhaul                                             |
+-----------------------------------------------------------------------------------------+
| Sort by: [Price (Low-High) | Timeline (Fastest) | Trust Grade (Highest) | Match Score]   |
+------------------------------------+----------------------------+-----------------------+
| EVALUATION METRICS                 | Contractor A (Apex Roof)   | Contractor B (Legacy) |
+------------------------------------+----------------------------+-----------------------+
| Opportunity Match Score (OMS)      | 94.2%                      | 87.5%                 |
| Total Project Bid Price            | $24,800                    | $27,500               |
| Estimated Project Timeline         | Oct 1 - Oct 18 (18 Days)   | Oct 15 - Nov 2 (18 D) |
| Trust Grade                        | A+                         | A                     |
| Craftsmanship Warranty            | 10-Year Labor              | 5-Year Labor          |
| Verified Similar Projects          | 24 Completed               | 12 Completed          |
| Average Customer Rating            | 4.9 Stars (142 Reviews)    | 4.7 Stars (88 Reviews)|
| Direct Communication Access        | Live Chat / SMS / Phone    | Live Chat Only        |
+------------------------------------+----------------------------+-----------------------+
| ACTION MATRIX                      | [ Select for Agreement ]   | [ Send Clarification] |
+------------------------------------+----------------------------+-----------------------+
```

### 3.1. Interactive Comparison Controls
Homeowners can customize their comparison view using several interactive controls:
* **"Highlight Deviations" Toggle:** Highlights areas where a contractor's bid varies significantly from the AI pricing estimate or other bids (e.g., highlighting an unusually high labor cost or an exceptionally fast timeline).
* **"Priority Weighting" Sliders:** Allows the homeowner to adjust the matching algorithm's weights (e.g., increasing the weight of the *Warranty* slider while reducing the importance of *Price* to find premium, long-term options).
* **"Verification Layer" Filter:** Filters out any contractor profiles that have not passed advanced security and insurance vetting checks within the past 30 days.

---

## 4. Anti-Manipulation Safeguards

To protect the integrity of the platform and maintain user trust, the comparison engine incorporates several built-in safeguards:

1. **No Sponsored Placements:** Contractors cannot purchase higher rankings, boost their match scores, or pay to feature their bids.
2. **Double-Blind Bid Shielding:** Contractors cannot see competitor bids while compiling their proposals. This prevents artificial price undercutting or collusion, ensuring homeowners receive honest, competitive pricing.
3. **Structured Review Auditing:** Reviews and ratings can only be submitted after a project is completed and verified by the system. This eliminates fake, purchased, or malicious reviews, ensuring all feedback is 100% authentic.
4. **Transparent Score Breakdowns:** Homeowners can click on any contractor's Opportunity Match Score to view a complete, itemized breakdown of the calculations and factors that produced it.
