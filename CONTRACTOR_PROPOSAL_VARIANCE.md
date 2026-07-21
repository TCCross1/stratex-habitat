# CENTCOM DIRECTIVE H-009: CONTRACTOR PROPOSAL VARIANCE
## BID EVALUATION HARMONIZATION & SYSTEMIC VARIANCE ANALYSIS MODEL
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Overview & Core Philosophy

When a homeowner transitions from Design Studio planning to real-world execution, they request contractor bids via the Contractor Experience portal. However, choosing a contractor based purely on the "lowest price" is a leading cause of construction failure, resulting in mid-project bankruptcies, low-grade material substitutions, surprise change-orders, and legal disputes.

The **Contractor Proposal Variance (CPV)** system is designed to programmatically normalize, compare, and grade incoming contractor proposals against the baseline Habitat planning estimate. 

### 1.1. Core Ethics & Regulatory Rules
*   **The Lowest is Not the Best**: The CPV does *not* rank proposals by price. It evaluates them based on completeness, quality, risk exposure, and structural equivalency.
*   **No Pressure Tactics**: The planning estimate is a private planning tool. It must **never** be used to squeeze contractor profit margins or pressure them into matching an unsupported target price. It is an educational reference point to help homeowners identify missing line items or high-risk bids.

---

## 2. Bid Evaluation Vectors (The 10-Point Analysis Matrix)

Every incoming proposal is dissected across ten standardized vector checks:

```
                          [ INCOMING BID PROPOSAL ]
                                      |
         +----------------------------+----------------------------+
         v                                                         v
[ Scope Completeness ]                                    [ Risk & Warranty ]
- Material SKU Checks                                     - Change-Order Exposure
- Excluded Line Items                                     - Labor Burden Checks
- Underfunded Allowances                                  - Warranty Length & Type
```

1.  **Scope Completeness**: Checks if the contractor bid includes all necessary stages (e.g. did they include the municipal permit fees, dumpsters, and post-project site cleanup?).
2.  **Material Equivalency**: Verifies whether the contractor is quoting the exact physical SKUs designed in the workspace or substituting them with unbranded, builder-grade generics.
3.  **Allowance Realism**: Evaluates if the contractor is using unrealistically low "allowances" (e.g. quoting a $1,500 fixture allowance on a project where the homeowner specified premium $4,500 finishes) to artificially lower their face bid.
4.  **Exclusions Audit**: Cross-references contractor-declared exclusions (such as "excludes subgrade rock excavation" or "excludes utility trenching") against known property DNA risk indices.
5.  **Labor & Schedule Assumptions**: Compositions of crew size and estimated working days. Extremely fast schedules are flagged for quality risk; extremely slow schedules are flagged for overhead bloat.
6.  **Warranty Coverage**: Distinguishes between the manufacturer's material warranty and the contractor's specific labor installation warranty (typically 1 to 5 years).
7.  **Change-Order Exposure**: Evaluates the contract type (Fixed Price vs. Time & Materials). Time and Materials models are flagged with "High Change-Order Exposure."
8.  **Overhead & Profit Presentation**: Analyzes how the contractor structures their operational margins. Builders who present transparent operations are favored over those who lump all margins into black-box markups.
9.  **Missing Line Items**: Scans for specific assembly components (e.g. flashing, ridge vents, concrete formwork lumber) that are omitted from the bid sheet but physically required.
10. **Variance From Planning Range**: Calculates the mathematical deviation from the ECF's "Expected Planning Range."

---

## 3. High-Contrast Proposal Comparison Matrix

When rendered in the homeowner dashboard, proposals are presented side-by-side with the Habitat planning baseline. Colors, borders, and layouts strictly adhere to the Stratex design guidelines.

```
+-----------------------------------------------------------------------------------+
|  CONTRACTOR PROPOSAL COMPARISON MATRIX                                            |
|  Project: Detached 20x24 Garage Build                                              |
+--------------------------+-----------------------+--------------------------------+
|  Vector                  | Habitat Planning Base | Bidder A: Peak Custom Builders |
+--------------------------+-----------------------+--------------------------------+
|  Total Proposed Price    | $45,000 - $49,000     | $48,200 (Fixed Price)          |
|  Status/Deviation        | Baseline Range        | +1.5% from Expected            |
|                          |                       |                                |
|  Scope Completeness      | 100% (All stages)     | 92% (Excludes permit submittal)|
|                          |                       |                                |
|  Material Equivalency    | James Hardie Siding   | MATCHED (SKU JHM-8041-FC)      |
|                          |                       |                                |
|  Fixture Allowances      | $4,500 (Verified)     | UNDERFUNDED ($2,000 allowance) |
|                          |                       |                                |
|  Exclusions              | None                  | Excludes landscaping repairs   |
|                          |                       |                                |
|  Labor Schedule          | 120 Crew Hours        | 80 Crew Hours (High Risk)      |
|                          |                       |                                |
|  Warranty                | Lifetime Material     | 5-Year Labor Warranty          |
|                          |                       |                                |
|  Change-Order Exposure   | Standard Contingency  | Low (Fixed Price contract)     |
|                          |                       |                                |
|  Risk & Omissions        | Baseline Reference    | Missing concrete pump fee line |
+--------------------------+-----------------------+--------------------------------+
```

---

## 4. Variance Scoring & Recommendation Logic

The CPV engine generates an automated narrative report for the homeowner, highlighting structural differences without bias:

### 4.1. Underfunded Allowance Warning
*   **Detection**: Contractor fixture allowance is $>30\%$ below the homeowner's designed SKU value.
*   **CPV Output**:
    *   *“Warning: Peak Custom Builders included a $2,000 lighting allowance. However, your active design uses premium Gilded-Bronze fixtures totaling $4,500. Choosing this contractor will likely result in a $2,500 out-of-pocket upgrade charge during construction.”*

### 4.2. Unrealistic Schedule Warning
*   **Detection**: Proposed labor hours are $>25\%$ below the Ebase production threshold.
*   **CPV Output**:
    *   *“Risk Alert: The proposed 80 crew hours is significantly below our engineering baseline of 120 hours for a stucco application. This suggests the contractor may be rushing the drying and curing process, increasing the long-term risk of stucco cracking.”*

### 4.3. Excluded Stage Alert
*   **Detection**: Municipal permit fees are omitted from the bid.
*   **CPV Output**:
    *   *“Omission Detected: Peak Custom Builders' bid excludes local building permit filing. You will need to file these permits independently with the Denver Building Department ($1,200 fee) or negotiate their inclusion before signing the contract.”*

By focusing on risk management, structural completeness, and financial transparency, the CPV protects the homeowner from bad contracts while promoting ethical, quality-focused construction partners.
