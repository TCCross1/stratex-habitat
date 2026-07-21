# CENTCOM DIRECTIVE H-009: ESTIMATE TEST & VALIDATION PLAN
## STRATEX REGRESSION MATRIX, BOUNDARY CHECKS, & REPRODUCIBILITY TEST SUITE
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Quality Assurance Mission

Estimating accuracy dictates homeowner confidence and contractor trust. A systemic bug that shifts a calculation by even a fraction can cause tens of thousands of dollars in real-world planning errors.

The **Estimate Test & Validation Plan (ETVP)** outlines the comprehensive automated test suite required to validate the calculating pipeline. 

Every release of the Habitat Design Studio 2.0 must pass $100\%$ of the tests in this matrix, verifying:
1.  **Mathematical Precision**: Verification of individual takeoff and compounding surcharge formulas.
2.  **Deterministic Reproducibility**: Guaranteeing that loading historic snapshots yields identical cost ranges.
3.  **Dynamic Recalculation Speed**: Validating that any UI parameter change recalculates the entire ledger within $<200$ milliseconds under load.
4.  **Security Boundaries**: Ensuring no homeowner can access or modify another user's estimates, and that private planning records never leak to bidding contractors.

---

## 2. Testing Levels & Strategies

```
+---------------------------------------------------------------------------------+
|                        ESTIMATOR QUALITY ASSURANCE LAYERS                       |
+---------------------------------------------------------------------------------+
|  LAYER 4: COMPLIANCE REGRESSION  ---> Verification of Reproducibility Snapshot.  |
|                                       Success rate: 100%                        |
|                                                                                 |
|  LAYER 3: API END-TO-END CHECK   ---> FastAPI routes, JSON validation, error responses. |
|                                       Response budget: <200ms                   |
|                                                                                 |
|  LAYER 2: SYSTEM INTEGRATION     ---> Cascading flow: QTE -> RCE -> LPM -> OPM. |
|                                       No dangling parameters allowed.           |
|                                                                                 |
|  LAYER 1: ISOLATED UNIT TESTS    ---> Mathematical correctness of formulas.     |
|                                       Target coverage: 100% of mathematical paths.|
+---------------------------------------------------------------------------------+
```

---

## 3. Unit Test Specifications (Layer 1)

Unit tests run in isolation using `pytest` inside the Python backend service.

### 3.1. Test Case: Takeoff Mathematical Correctness (`test_takeoff_formulas.py`)
*   **Target Function**: `QuantityTakeoffEngine.calculate_roof_squares(footprint_sqft, pitch_ratio, waste_factor)`
*   **Test Inputs**:
    *   `footprint_sqft`: `1200`
    *   `pitch_ratio`: `"6:12"` (Pitch factor = `1.11803`)
    *   `waste_factor`: `0.10` (10%)
*   **Expected Calculation**:

$$\text{Roof Area} = 1200 \times 1.11803 = 1341.636 \text{ SQFT}$$

$$\text{Squares of Shingles} = \text{ceil}\left( \frac{1341.636}{100} \times (1 + 0.10) \right) = \text{ceil}(14.75799) = 15 \text{ SQ}$$

*   **Assertion Check**: Assert output is exactly `15` SQ, with a source declaration category of `Digital Twin Measurement`.

### 3.2. Test Case: Burden Compounding (`test_labor_billing.py`)
*   **Target Function**: `LaborProductivityModel.calculate_billing_rate(wage_rate, trade)`
*   **Test Inputs**:
    *   `wage_rate`: `38.00`
    *   `trade`: `"Lead Carpenter"`
    *   `burden_multiplier`: `1.45`
    *   `admin_multiplier`: `1.35`
*   **Expected Calculation**:

$$R_{\text{bill}} = 38.00 \times 1.45 \times 1.35 = 74.385 \approx 74.39$$

*   **Assertion Check**: Assert computed billing rate is equal to `$74.39` per hour within standard floating point tolerances.

---

## 4. Integration Test Specifications (Layer 2)

Integration tests verify the connective tissue between engines, checking that a change on one end propagates smoothly to the other.

### 4.1. Test Case: Material Grade Swapping Propagation (`test_material_swap_flow.py`)
*   **Scenario**: Shifting siding selection from "Good" (Pine lap) to "Best" (James Hardie Select Cedarmill).
*   **Validation Steps**:
    1.  Initialize standard 2,000 SQFT siding design.
    2.  Invoke `POST /api/v1/estimates/calculate` with Pine lap SKU. Record subtotal.
    3.  Trigger material update event replacing Pine lap with James Hardie SKU (SKU `JHM-8041-FC`).
    4.  Verify that:
        *   Material unit cost shifts from `$1.25` to `$3.85` SQFT.
        *   Waste factor shifts from `0.10` to `0.08` due to product composition differences.
        *   Labor trade allocation is re-run ( Pine uses general handymen, Hardie requires Siding Installers with a higher billing rate).
        *   Total estimate expected range recalculates instantly and the Delta Explanation Engine appends: *"Selecting James Hardie Select Cedarmill instead of Pine lap siding increased material costs by $5,200 and installation labor by $1,150."*

---

## 5. Reproducibility Regression Tests (Layer 4)

To guarantee that old estimations do not experience drift due to database updates, the ETVP establishes a strict regression baseline:

### 5.1. The Historical Reproduction Test Suite (`test_reproducibility.py`)
*   **Methodology**:
    1.  The test harness loads a static mock database containing a archived design from July 2026 (`reproducibility_snapshot`).
    2.  The snapshot contains frozen, hardcoded variables: `dimensions`, `selected_skus`, and `price_book_version: "v2026.1.1"`.
    3.  The estimating engine processes the payload.
    4.  **Success Threshold**: The calculated `selling_price_expected` must match the archived value of exactly `$42,850.00` down to the penny. 
    5.  If future code changes to the math pipeline alter this result by even one cent, the build fails, ensuring the system remains completely deterministic and stable.

---

## 6. Edge Case & Stress Testing Matrix

The system must handle non-ideal conditions and corrupt inputs gracefully, returning clear diagnostic notifications rather than crash dumps.

| Test Scenario | Action / Input State | Expected Failure Mitigation | Stratex Visual / API Outcome |
| :--- | :--- | :--- | :--- |
| **Zero Spatial Inputs** | Homeowner passes empty `dimensions` object to API. | QTE detects missing layers and falls back to Project Template averages. | Alert badge in panel: *"Confidence: Preliminary. Using standard template averages due to missing property dimensions."* |
| **Unresolvable ZIP Code**| Homeowner inputs ZIP `00000`. | RCE fails local resolution, throws a soft error, and falls back to RCE Level 1 National average. | API response: `200 OK` with warning flag `geographic_basis_fallback: "NATIONAL"`. Panel displays: *"Local prices unavailable, using National base."* |
| **Extreme Heights** | Height parameter set to `45.0` feet (4-story building). | LPM triggers extreme height hazard multiplier ($C_{\text{height}} = 1.35$) and flags scaffolding requirement. | Cost ledger appends specialized equipment allowance for Scaffolding Tower Rental (`$1,200`). |
| **Corrupt SKU Request** | Homeowner designs with deleted or corrupt material SKU ID. | Material Library intercepts, falls back to the default basic tier SKU of that material class. | UI Toast notification: *"Swatch updated: Selected product line is currently out of stock. Temproarily using standard base line selection."* |
| **Concurrent Load Stress**| 100 requests per second simulating peak spring design season. | API Router leverages redis cache layer for static SKU and regional index lookups. | Response latency must remain below **185ms** at 95th percentile. |
