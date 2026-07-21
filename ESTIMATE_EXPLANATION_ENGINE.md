# CENTCOM DIRECTIVE H-009: ESTIMATE EXPLANATION ENGINE
## EVENT-DRIVEN STATE RECONCILIATION & NATURAL LANGUAGE COST EXPLANATION
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Overview & Architectural Mission

When cost estimates update dynamically inside Design Studio 2.0, homeowners often feel disoriented if prices swing without explicit context. A sudden $2,500 budget increase must not be a black-box surprise. 

The **Estimate Explanation Engine (EEE)** is an event-driven analysis system. It intercepts state changes (material swaps, dimension shifts, location updates, environmental overrides) between Estimate Version $V_{n-1}$ and Version $V_n$, executes a differential analysis (Delta Engine), and renders precise, natural-language, educational explanations detailing the "Why" behind the financial shift.

```
       [ Estimate Version V_n-1 ]       [ Estimate Version V_n ]
                   |                               |
                   +--------------+----------------+
                                  |
                                  v
                       [ Delta Reconciliation ]
                     - Quantities, SKUs, Taxes, etc.
                                  |
                                  v
                      [ NLG Template Resolver ]
                     - Always explain, never alarm
                                  |
                                  v
                    "Patio cost increased by $2,420
                     because area expanded by 190 SQFT."
```

---

## 2. Event-Driven State Change Audit Loop

The EEE acts as a reactive listener bound to the Design Studio's state store. The system compares the active calculation state against the immediately preceding immutable estimate record.

```typescript
export interface EstimateDelta {
  field_path: string;                    // e.g. "assemblies[0].components[1].quantity"
  delta_type: 'dimension' | 'sku_swap' | 'location' | 'multiplier_shift' | 'contingency_addition';
  old_value: any;
  new_value: any;
  financial_impact: number;              // Positive (cost increase) or Negative (savings)
}
```

### 2.1. Audit Vectors Analyzed
1.  **Dimensional Delta**: Changes in geometric takeoffs (e.g., roof pitch, patio square footage, siding area).
2.  **SKU/Material Delta**: Changes in manufacturer, product line, grade, finish, or performance tier.
3.  **Geographic/Pricing Delta**: Changing ZIP code, which re-calibrates labor and tax indexes.
4.  **Assumptions/Contingency Delta**: Ingesting new property DNA, which flags subgrade or wind risk adjustments.

---

## 3. Natural Language Generation (NLG) Templates

The EEE resolves delta objects into highly structured, friendly, and informative descriptions, adhering strictly to the **"always explain, never alarm"** UX mandate.

### 3.1. Dimension Changes (NLG Template)
*   **Formula**:

$$\text{Delta Quantity } (\Delta Q) = Q_{\text{new}} - Q_{\text{old}}$$

$$\text{Delta Financial } (\Delta F) = (\Delta Q \times \text{Unit Cost}) \times \mathcal{M}_{\text{operations\_profit}}$$

*   **NLG Pattern**:
    *   *"[Assembly Name] cost [increased/decreased] by $[Delta Financial] because the [dimension name] changed from [old value] to [new value] [unit]."*
*   **NLG Example**:
    *   *"Patio cost increased because the area changed from 420 to 610 square feet."*

### 3.2. Material Grade Swap (NLG Template)
*   **Formula**:

$$\Delta F = \left( (Q \times \text{SKU}_{\text{new}} \times (1 + \mathcal{W}_{\text{new}})) - (Q \times \text{SKU}_{\text{old}} \times (1 + \mathcal{W}_{\text{old}})) \right) + \Delta \text{Labor}_{\text{installation}}$$

*   **NLG Pattern**:
    *   *"Selecting [Product Line New] instead of [Product Line Old] [increased/decreased] materials by $[Delta Material] and installation labor by $[Delta Labor]."*
*   **NLG Example**:
    *   *"Selecting porcelain pavers instead of standard clay pavers increased material cost by $1,850 and installation labor by $420."*

### 3.3. Contingency / Unknown Condition Appended (NLG Template)
*   **NLG Pattern**:
    *   *"The current estimate includes an allowance of $[allowance] for [contingency name] because of [detected condition]."*
*   **NLG Example**:
    *   *"The current estimate includes an allowance of $1,200 for retaining-wall drainage because of the proposed grade change detected on your property topography scan."*

### 3.4. Geographic Precision Fallback (NLG Template)
*   **NLG Pattern**:
    *   *"Local pricing is [status] for [ZIP code], so the displayed range uses the [fallback level] benchmark."*
*   **NLG Example**:
    *   *"Local pricing is currently unavailable for ZIP 59001, so the displayed range uses the regional Montana mountain-logistics benchmark."*

---

## 4. Multi-Variant Material Library Recalculation Flow

When a homeowner interacts with the "Good / Better / Best / Premium" comparative matrix, the material, installation labor, accessories, waste, and final selling price must immediately update and explain the divergence.

```
       +---------------------------------------------------------------+
       |                   MATERIAL SWAP DECISION TREE                 |
       +---------------------------------------------------------------+
       |                                                               |
       |   [ GOOD: Architectural Shingles ] -> Base labor: $55/SQ      |
       |   - Waste: 10% | SKU: $115/SQ | Warranty: 15 Yr standard      |
       |                                                               |
       |   [ BETTER: Standing Seam Metal ]  -> Skilled labor: $92/SQ   |
       |   - Waste: 5%  | SKU: $285/SQ | Warranty: 40 Yr transferable  |
       |                                                               |
       |   [ BEST: Solar Glass Shingles ]   -> Specialized: $165/SQ    |
       |   - Waste: 12% | SKU: $620/SQ | Warranty: 25 Yr electric      |
       |                                                               |
       +---------------------------------------------------------------+
```

### 4.1. Underhood Recalculation Flow
1.  **Read Target Product SKU Attributes**: The system pulls the target row from the Material SKU Database Schema (including `base_cost_per_unit`, `pbr_parameters`, and `warranty_details`).
2.  **Retrieve Labor Complexity Multipliers**: Evaluates if the material class changes the trade hours (e.g. shifting from lap siding to heavy brick veneer requires moving from Siding Installers to Specialist Masons, shifting billing rates from `$52/hr` to `$88/hr`).
3.  **Adjust Accessory Assemblies**: Shifting from composite decking back to pressure-treated wood automatically removes hidden clip fasteners and replaces them with corrosion-resistant framing screws.
4.  **Compute Waste Delta**: Updates the active waste factor ($\mathcal{W}$) based on material rigidity and geometric nesting layout.
5.  **Output Comparative Reconciliation**:
    *   *“Upgrading your roof selection to Standing Seam Metal (Better Tier) increases material costs by $4,200 but extends your warranty coverage from 15 to 40 years. It also decreases waste overhead from 10% to 5% due to precise roll-forming on site.”*
