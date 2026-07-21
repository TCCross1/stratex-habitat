# CENTCOM DIRECTIVE H-009: OVERHEAD AND PROFIT MODEL
## TRANSPARENT OPERATIONAL MARGINS, WARRANTY RESERVES, & HOMEOWNER EDUCATION
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Philosophical Framework

A frequent source of tension between homeowners and residential builders is the presentation of Overhead and Profit (OH&P). Traditional estimates often bury these numbers inside material margins or, conversely, present them as flat, unexplained "markup" line items, which leads homeowners to view them as arbitrary or unnecessary.

The **Overhead and Profit Model (OPM)** establishes a paradigm of absolute transparency:
*   **Always explain, never conceal**: All operational costs, supervision, administrative fees, insurance, and profit margins are clearly itemized as planning allowances.
*   **Professional solvent contractors**: OPM uses supportive, educational framing to explain that reasonable overhead and profit is not "bloat." It is the exact buffer that guarantees a contractor remains solvent, licensed, insured, and physically capable of returning to honor warranties years after construction.
*   **Homeowner-Facing Interface Grouping**: To prevent information overload while retaining complete transparency, the UI groups these elements under the cohesive block **"Contractor Operations and Profit"**, with an interactive, high-contrast, expandable drawer revealing the exact breakdown.

---

## 2. Standard Allocation Formulas & Percentages

The OPM applies a default operational matrix calibrated to the project's complexity and overall cost.

```
                            [ ESTIMATED SELLING PRICE ]
                                         |
     +-----------------------------------+-----------------------------------+
     v                                                                       v
[ Contractor Operations: ~15% - 20% ]                      [ Contractor Profit: ~8% - 12% ]
- General Overhead (Rent, utilities, admin)                - Risk compensation
- Project-Specific Overhead (Supervision, PM, site toilets)- Capital reinvestment
- Insurance & Licensing (General liability, surety bond)   - Solvent business operations
- Warranty Reserves (Post-completion service backing)
```

### 2.1. Standard Matrix Breakdown (Default Settings)

| OPM Category | Allocation Rate (Default) | Calculating Base | Purpose & Underwriting Logic |
| :--- | :--- | :--- | :--- |
| **General Overhead** | `10.0%` | Direct Costs | Covers brick-and-mortar office lease, administrative assistants, legal compliance, and estimating tools. |
| **Project Supervision**| `4.0%` | Direct Costs | Covers the physical presence of a site superintendent or lead carpenter overseeing safety, quality, and material deliveries. |
| **Project Management** | `2.5%` | Direct Costs | Covers offsite coordination, scheduling subcontractors, permitting submissions, and homeowner communication. |
| **Liability & Insurance**| `1.5%` | Direct Costs | Underwrites general liability insurance ($2M limit typical), municipal business licenses, and contractor bonds. |
| **Warranty Reserves** | `2.0%` | Direct Costs | Escrowed to fund post-completion callbacks, structural adjustments, and material defect replacements during the coverage term. |
| **Contractor Profit** | `10.0%` | Subtotal Cost | Billed compensation for structural risk and capital deployment. Ensures the contractor remains a thriving business. |

---

## 3. Mathematical Integration (Calculating the Cumulative Surcharge)

To calculate the absolute "Contractor Operations and Profit" surcharge ($S_{\text{op}}$), the OPM aggregates direct overhead percentages and compounds profit:

$$\text{Direct Cost Subtotal } (DC) = \sum \text{Materials} + \sum \text{Labor} + \sum \text{Equipment} + \sum \text{Subcontractors}$$

$$\text{Contractor Operations Subtotal } (S_{\text{ops}}) = DC \times \left( OH_{\text{gen}} + OH_{\text{super}} + OH_{\text{pm}} + OH_{\text{ins}} + OH_{\text{war}} \right)$$

$$\text{Contractor Cost Base } (CC) = DC + S_{\text{ops}}$$

$$\text{Contractor Profit Allowance } (P_{\text{profit}}) = CC \times P_{\text{rate}}$$

$$\text{Total Contractor Operations & Profit } (S_{\text{op\_total}}) = S_{\text{ops}} + P_{\text{profit}}$$

### 3.1. Compound Surcharge Example ($25,000 Project)
If a stamped concrete patio has total direct costs of **$25,000**:
1.  **Contractor Operations Surcharges**:
    *   *General Overhead (10.0%)*: `$2,500`
    *   *Supervision (4.0%)*: `$1,000`
    *   *Project Management (2.5%)*: `$625`
    *   *Insurance & Licensing (1.5%)*: `$375`
    *   *Warranty Reserves (2.0%)*: `$500`
    *   *Subtotal Operations ($S_{\text{ops}})$*: **`$5,000`** (20.0% cumulative)
2.  **Contractor Cost Base ($CC$)**: `$25,000 + $5,000 = $30,000`
3.  **Contractor Profit (10.0%)**: `$30,000 \times 10.0\% = $3,000`
4.  **Final Selling Price**: `$30,000 + $3,000 = $33,000`
5.  **Presented "Contractor Operations and Profit" Drawer Total**: **`$8,000`** (Consisting of $5,000 operations + $3,000 profit).

---

## 4. UI Copy & Homeowner-Facing Explanations

The OPM database maintains a library of educational definitions dynamically rendered when a homeowner hovers or taps on any OPM line-item component:

### 4.1. General Overhead
> *"This allocation covers the builder's fundamental business expenses—such as office staff, local facilities, safety equipment, and software licensing. Maintaining strong business operations ensures your builder is organized and responds promptly throughout your project."*

### 4.2. Supervision & Project Management
> *"Dedicated time for a site supervisor to direct work, check quality, organize material deliveries, and schedule inspectors. Consistent on-site management prevents mistakes, ensures safety, and keeps construction on schedule."*

### 4.3. Liability, Insurance & Licensing
> *"Underwrites the high-value general liability insurance, municipal worker protections, builder's risk coverages, and specialized contractor bonds required by local building departments to protect your property and home passport."*

### 4.4. Warranty Reserves
> *"A dedicated quality reserve fund set aside by the contractor. This backing guarantees that if any adjustments are needed or if a material component experiences issues years down the line, your contractor has pre-funded capital allocated to perform the service without friction."*

### 4.5. Contractor Profit
> *"The essential return on business risk, skilled labor, and capital investment. A profitable, healthy builder is a permanent asset to your local community, ensuring they remain solvent and fully available to back your home's multi-year warranty obligations."*

By transforming "markup" from a mysterious, hostile surcharge into a logical, educational operational breakdown, the OPM fosters mutual respect and transparency between Habitat homeowners and building partners.
