# PROJECT BUDGET ENGINE & FINANCIAL MODELER
## ESTIMATE CONFIDENCE TIERS, REGIONAL COST TUNING, & FINANCING SCENARIOS
**Version:** 2.0  
**Classification:** HABITAT-CONFIDENTIAL

This specification defines the localized cost-estimation framework, budget confidence tiers, and financing integration systems that power transparent financial planning within the Habitat Design Studio 2.0.

---

## 1. THE 4 ESTIMATE CONFIDENCE TIERS

To build homeowner trust, Design Studio 2.0 uses a highly transparent cost-estimation model. Costs are never aggregated into a single black-box estimate. Instead, every line-item budget entry is categorized across **Four Confidence Tiers**.

```
+---------------------------------------------------------------------------------+
|                         THE COGNITIVE ESTIMATION FRAMEWORK                      |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [ VERIFIED (GREEN) ]        --->  Binding quotes or SKU manufacturer pricing.  |
|                                    Confidence: 100%                            |
|                                                                                 |
|  [ ESTIMATED (TEAL) ]        --->  Regional averages tuned by ZIP code.         |
|                                    Confidence: 85% - 95%                       |
|                                                                                 |
|  [ SUGGESTED (ORANGE) ]      --->  General material allowances for loose specs.  |
|                                    Confidence: 60% - 80%                       |
|                                                                                 |
|  [ FUTURE CAPABILITY (GRAY) ] --->  Requires onsite engineering / unbuilt module|
|                                    Confidence: <50%                            |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### UI & UX Representation
- **Verified**: Green solid outline, check badge, JetBrains Mono font (`#39FF14`).
- **Estimated**: Teal solid border, calculator icon, JetBrains Mono font (`#00F0FF`).
- **Suggested**: Orange solid border, warning icon, JetBrains Mono font (`#FF9E00`).
- **Future capability**: Gray dashed border, placeholder question mark, JetBrains Mono font (`#9CA3AF`).

---

## 2. REGIONAL COST TUNING & ESTIMATION LOGIC

The Dynamic Estimator API adjusts raw material and labor costs using localized geographic variables.

### Localized Estimation Formula

Project line-item estimation is calculated using the following formula:

$$\text{Line Item Cost} = \left( (\text{Material SKU Cost} \times Q) + (\text{Base Labor Rate} \times \text{Est Hours} \times \mathcal{L}_{zip}) \right) \times (1 + \mathcal{T}_{local}) + \mathcal{P}_{permit}$$

Where:
- $Q$: Quantity required (square feet, linear feet, or units).
- $\mathcal{L}_{zip}$: Local Labor Cost Multiplier for the target ZIP code.
- $\mathcal{T}_{local}$: Local and state sales tax rate index.
- $\mathcal{P}_{permit}$: Municipal building/utility permit fee allowance.

### Local Labor Multipliers ($\mathcal{L}_{zip}$) Examples
- **Denver, CO (80202)**: `1.12` (Moderate-high labor market)
- **San Francisco, CA (94103)**: `1.45` (Extreme-high labor market)
- **Dallas, TX (75201)**: `0.94` (Moderate-low labor market)
- **Indianapolis, IN (46204)**: `0.88` (Low labor market)

---

## 3. LIVE COST ESTIMATION BREAKDOWN GRID

Every active design produces an itemized cost ledger rendered using high-contrast data visualization.

```
+---------------------------------------------------------------------------------+
|  PROJECT COST LEDGER: Detached ADU Build                                        |
+---------------------------------------------------------------------------------+
|  [Verified]   GAF Timberline HDZ Roofing (Materials)            $3,420.00       |
|               (Locked SKU-level manufacturer cart price)                       |
|                                                                                 |
|  [Estimated]  Concrete Slab Pour & Grading (Denver, CO)         $12,800.00      |
|               (1.12 Local Labor Multiplier applied to 160 hrs)                  |
|                                                                                 |
|  [Suggested]  Interior Bathroom Fixtures Allowance              $4,500.00       |
|               (Standard medium-tier design allowance)                          |
|                                                                                 |
|  [Future]     Excavation & Geotechnical Soil Boring             $3,200.00       |
|               (Requires professional structural engineer site check)            |
+---------------------------------------------------------------------------------+
|  SUBTOTAL:                                                     $23,920.00       |
|  LOCAL SALES TAX (Denver 8.81% on Materials):                  $301.30          |
|  MUNICIPAL ADU PERMIT ALLOWANCE:                               $1,200.00        |
|  STRUCTURAL CONTINGENCY BUFFER (10%):                          $2,392.00        |
+---------------------------------------------------------------------------------+
|  TOTAL DESIGN SCENARIO COST RANGE:                 $27,150.00 - $28,450.00      |
+---------------------------------------------------------------------------------+
```

---

## 4. INTEGRATED FINANCING SCENARIOS

To convert homeowner dreams into operational construction reality, the Budget Engine includes an interactive **Financing Scenarios Modeler**. This system analyzes monthly affordability, interest costs, and amortization curves across three standard payment channels.

```
                      +------------------------------------+
                      |    FINANCING SCENARIO GENERATOR    |
                      +------------------------------------+
                      |                                    |
                      |  1. CASH RESERVES (0% Interest)    |
                      |                                    |
                      |  2. HOME IMPROVEMENT LOAN (Fixed)  |
                      |                                    |
                      |  3. HELOC (Variable/Revolving)     |
                      |                                    |
                      +------------------------------------+
```

### Amortization & Monthly Payment Formula

Monthly loan payments ($M$) are calculated using the standard fixed amortization formula:

$$M = P \times \frac{r(1 + r)^n}{(1 + r)^n - 1}$$

Where:
- $P$: Total Principal Loan Amount (Project Cost minus Down Payment).
- $r$: Monthly Interest Rate (Annual Rate / 12).
- $n$: Total Number of Payments (Loan Term in Months).

---

## 5. COMPARATIVE FINANCING OPTIONS (EXAMPLE SIMULATION)

For a designed **Attached Garage & Solar System project** totaling **$45,000** (with a $10,000 user down payment), the Financing Modeler compares options:

### Option A: Home Improvement Loan (Unsecured Fixed-Rate)
- **Principal ($P$)**: $35,000
- **Annual Interest Rate**: 7.25%
- **Term ($n$)**: 60 months (5 Years)
- **Monthly Payment ($M$)**: **$697.28**
- **Total Interest Paid**: $6,836.80
- **Total Lifetime Cost**: $51,836.80

### Option B: HELOC (Home Equity Line of Credit)
- **Principal ($P$)**: $35,000
- **Annual Interest Rate**: 8.50% (Variable index)
- **Term ($n$)**: 120 months (10 Years)
- **Monthly Payment ($M$)**: **$433.82**
- **Total Interest Paid**: $17,058.40
- **Total Lifetime Cost**: $62,058.40

### Option C: Milestone Cash Schedule (0% Interest)
- **Principal ($P$)**: $35,000
- **Milestone 1 (Mobilization)**: $11,666.66 (Due at Signing)
- **Milestone 2 (Dry-In/Framing)**: $11,666.66 (Due at Inspections)
- **Milestone 3 (Completion)**: $11,666.68 (Due at Final sign-off)
- **Monthly Cost / Debt**: **$0.00**
- **Total Interest Paid**: $0.00
- **Total Lifetime Cost**: $45,000.00

---

## 6. SYSTEM BUDGET METRICS INTEGRATION

The results of the financial simulator are bound directly to the homeowner's project model. If a monthly budget threshold is exceeded (e.g. user set a max of $500/month, but the chosen deck design costs $700/month), the system displays helpful, non-alarmist warnings and suggests material compromises (e.g. switching from composite back to pressure-treated timber, or scaling down the deck footprint by 2 feet to bring payments into alignment).
