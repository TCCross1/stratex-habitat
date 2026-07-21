# CENTCOM DIRECTIVE H-009: REGIONAL COST ENGINE
## GEOGRAPHIC COST INTELLIGENCE & MULTI-TIER PRECISION RESOLUTION
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Executive Summary & Geographic Philosophy

Construction costs do not adhere to national averages. A stamped patio or a roofing replacement can cost up to $150\%$ more in San Francisco than in Indianapolis due to labor union agreements, extreme seismic structural codes, transport logistics, and localized sales taxes.

The **Regional Cost Engine (RCE)** resolves this by applying progressive geographic precision. It dynamically calculates regional multipliers ($I_{\text{mat}}, I_{\text{lab}}, F_{\text{clim}}$) based on the project's ZIP code, while enforcing the **Fourth Engineering Law**: *No false precision. Never display local precision unsupported by available data.*

---

## 2. Progressive Precision Levels (The 4 Levels)

The estimating dashboard scales its cost accuracy dynamically based on the freshness and density of local construction records.

```
+---------------------------------------------------------------------------------+
|                       GEOGRAPHIC COST PRECISION LEVEL PIPELINE                  |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [ LEVEL 4: CONTRACTOR-VALIDATED ] ---> Bids submitted by active contractors.  |
|                                         Fidelity: 100%                          |
|                                                                                 |
|  [ LEVEL 3: METROPOLITAN/LOCAL ]    ---> Local zip code data (Fresh <=90 days).  |
|                                         Fidelity: 90% - 95%                     |
|                                                                                 |
|  [ LEVEL 2: REGIONAL BENCHMARK ]    ---> Regional indices & climate factors.    |
|                                         Fidelity: 75% - 85%                     |
|                                                                                 |
|  [ LEVEL 1: NATIONAL AVERAGE ]      ---> Baseline material SKU & labor models.  |
|                                         Fidelity: <70%                          |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### 2.1. Level 1 — National Planning Baseline
*   **Description**: Baseline cost data derived directly from national supplier catalogs and raw trade wages.
*   **Trigger**: Project location has zero local cost data points, or GIS spatial query is unavailable.
*   **Accuracy Presentation**: Rounded to the nearest $10\%$, marked as "National Average Planning Baseline" with a warning that local conditions may vary significantly.

### 2.2. Level 2 — Regional Adjustments
*   **Description**: Modulates the national baseline using statewide and regional economic indices.
*   **Trigger**: ZIP code resolved to a region with broad index records but no metropolitan pricing.
*   **Multipliers**: Broad statewide labor burden, transport access indexes, and standard state sales taxes are applied.

### 2.3. Level 3 — Metropolitan or Local Precision
*   **Description**: Micro-localized pricing representing exact municipality datasets.
*   **Trigger**: ZIP code has $\ge 3$ verified local contractor transactions or material SKU receipts updated within the last **90 days**.
*   **Fidelity**: Integrates local building permit fees, specific city sales taxes, local union/prevailing wage scales, and precise terrain/wind-load factors.

### 2.4. Level 4 — Contractor-Validated
*   **Description**: Real-world construction pricing.
*   **Trigger**: Homeowner submits the design as an RFP and receives active, binding contractor proposals via the Contractor Experience portal.
*   **Fidelity**: Absolute. Replaces all statistical cost curves with actual proposed contracts.

---

## 3. Cost Multiplier Indices (The RCE Formula)

The localized cost for an assembly is resolved using the following formula:

$$\mathcal{C}_{\text{local}} = \left( \mathcal{C}_{\text{mat}} \times I_{\text{mat}} \times F_{\text{clim}} \times F_{\text{log}} \right) + \left( \mathcal{C}_{\text{lab}} \times I_{\text{lab}} \times (1 + T_{\text{tax}}) \right) + P_{\text{permit}}$$

Where:
*   $\mathcal{C}_{\text{mat}}$: National baseline Material SKU Cost.
*   $\mathcal{C}_{\text{lab}}$: National baseline Labor Cost.
*   $I_{\text{mat}}$: Material Price Index for the target ZIP code.
*   $I_{\text{lab}}$: Local Labor Cost Multiplier.
*   $F_{\text{clim}}$: Climate & Code Structural Adjustment Factor.
*   $F_{\text{log}}$: Site Logistics / Remote Access Multiplier.
*   $T_{\text{tax}}$: Municipal Sales Tax Rate.
*   $P_{\text{permit}}$: Flat municipal permitting fees.

---

## 4. Regional Indexes: Metropolitan Calibration Examples

Below is the active lookup table used by the RCE to calibrate regional estimations across four target metropolitan areas:

| Metropolitan Area | ZIP Code Basis | Labor Index ($I_{\text{lab}}$) | Material Index ($I_{\text{mat}}$) | Climate Factor ($F_{\text{clim}}$) | Sales Tax ($T_{\text{tax}}$) | Permits Allowance ($P_{\text{permit}}$) | Code / Structural Drivers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **San Francisco, CA**| `94103` | `1.45` | `1.18` | `1.20` | `8.63%` | `$2,450` | Seismic Category E framing, Title 24 Energy mandates, mandatory union labor. |
| **Denver, CO** | `80202` | `1.12` | `1.04` | `1.15` | `8.81%` | `$1,200` | Snow-load structure framing (50 PSF), concrete freeze-thaw subbase prep. |
| **Dallas, TX** | `75201` | `0.94` | `0.98` | `1.05` | `8.25%` | `$850` | Wind-uplift framing clips (115 MPH), expansive clay soil deep-footing rules. |
| **Indianapolis, IN** | `46204` | `0.88` | `0.95` | `1.00` | `7.00%` | `$450` | Standard IRC building codes, low labor burden, easy highway delivery access. |

---

## 5. Unknown Conditions & Risk Allowance Algorithm

When the RCE cannot resolve site data (e.g. soil composition, bedrock depth, or municipal setback constraints), it does not pretend they do not exist. Instead, it dynamically injects **Risk Allowances** into the estimate.

### 5.1. Risk Allowance Multiplier Calculation
The risk factor ($F_{\text{risk}}$) scales inversely with geographic data reliability:

$$F_{\text{risk}} = 1.0 + \left( \frac{\mathcal{U}_{\text{info}}}{100} \times \mathcal{M}_{\text{geo}} \right)$$

Where:
*   $\mathcal{U}_{\text{info}}$: Information missingness index (0 to 10, where 10 means zero verified measurements).
*   $\mathcal{M}_{\text{geo}}$: Geographic uncertainty penalty (`0.02` for Level 3, `0.05` for Level 2, and `0.08` for Level 1).

### 5.2. Example Mitigation Logic
If a homeowner designs an **In-Ground Pool** in a ZIP code with known limestone bedrock anomalies:
1. **Bedrock Scan Lookup**: The RCE checks historic GIS drill records.
2. **Bedrock Probable**: If probability of hitting bedrock is $>40\%$, the RCE automatically appends a **$3,500 rock excavation allowance** to the "High Planning Range" scenario.
3. **Verification Prompt**: The UX panel displays:
   * *"Risk Allowance Included: Local geologic records indicate high probability of subgrade limestone. We recommend a professional geotech soil boring ($500 value) to remove this $3,500 contingency."*

By explicitly quantifying what is unknown, the RCE preserves the transparency and integrity of the planning record, preventing contractors from encountering expensive, unpredicted change-orders during construction.
