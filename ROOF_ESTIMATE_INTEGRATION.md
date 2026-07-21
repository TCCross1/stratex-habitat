# PROJECT ESTIMATOR INTEGRATION
## PLANNING ESTIMATES AND COST BREAKDOWNS

This document details the integration with the **Project Estimator** (Task 8) used to generate localized, structured planning cost estimates for roof replacement.

---

## 1. GEOGRAPHIC PRICING BASIS

The system calculates costs using national baseline indexes combined with regional and localized multipliers:
* **Geographic Basis:** Austin Metro, Texas (Regional Multiplier: **1.08x**).
* **Pricing Date:** July 2026.
* **Quantity Sources:** Property Geometry (3,200 sqft / 32 Squares).
* **Confidence Tier:** High for surface area, Low for underlying deck condition.

---

## 2. STRUCTURAL COST BREAKDOWN

Estimates are divided into transparent line-item categories rather than lumped sum numbers:

```
[Total Project Estimate]
   ├── Materials (GAF Timberline HDZ or DECRA Metal)
   ├── Labor (Regional certified roofing crew rates)
   ├── Equipment (Safety harnesses, roof brackets, debris chutes)
   ├── Tear-off & Disposal (Removing old shingles, landfill fees)
   ├── Permits & Municipal Fees (Austin city building permits)
   ├── Contractor Operations & Profit (O&P) (Management overhead)
   ├── Contingency (Reserved for unknown deck repair factors)
   └── Applicable Sales Taxes (State & local material taxes)
```

### Pricing Scenarios:

| Material | Scenario | Cost | Description / Assumptions |
| :--- | :--- | :--- | :--- |
| **Asphalt Shingles** | **Low (Best Case)** | **$12,441.60** | Minimal deck repair, standard waste. |
| **Asphalt Shingles** | **Expected (Base Case)** | **$14,515.20** | Standard 10% waste, minor flashing replacement. |
| **Asphalt Shingles** | **High (Worst Case)**| **$18,144.00** | Extent of decking repairs required, complex geometry. |
| **Standing Seam Metal**| **Expected (Base Case)** | **$29,030.40** | Premium materials, highly skilled specialized crew. |

---

## 3. COST DELTA EXPLANATION ENGINE

When the homeowner switches from Architectural Shingles to Standing Seam Metal, the system generates a human-readable explanation of the cost delta:

> *"The cost increase of **$14,515.20** (+100.0%) reflects the transition from Standard Asphalt Shingles to Premium Standing Seam Metal. Premium metal materials have a 2.5x higher cost factor, require highly specialized interlocking metal installation crews (+40% labor premium), and include safety bracket equipment. However, Standing Seam has a lifetime warranty and outstanding heat reflection suited for the Texas hot summers."*

---

## 4. ESTIMATE ASSUMPTIONS, EXCLUSIONS AND GAPS

* **Assumptions:** Capped at 3,200 sqft. Standard roof access. Double stories access premium included.
* **Exclusions:** Does not include solar panel uninstallation/re-installation fees.
* **Unknowns:** Any dry rot repair required on the roof deck.
* **Verification Checklist:**
  * [ ] Verify chimney flashing seal integrity.
  * [ ] Inspect ventilation exhaust hoods.
  * [ ] Physically audit wood deck rot.
