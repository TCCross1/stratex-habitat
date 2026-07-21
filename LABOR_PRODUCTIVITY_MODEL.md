# CENTCOM DIRECTIVE H-009: LABOR PRODUCTIVITY MODEL
## MULTIDIMENSIONAL LABOR BURDENS, TRADE CLASSIFICATIONS, & ACCESS MULTIPLIERS
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Labor Modeling Philosophy

A common point of failure in residential estimating is calculating labor as a flat percentage of materials or using direct employee wage rates instead of fully burdened contractor billing rates. 

The **Labor Productivity Model (LPM)** decouples raw wages from final billed labor, calculating real-world production hours by modeling trades, crew composition, and specialized complexity modifiers ($M_{\text{comp}}$) such as heights, poor site access, seasonal constraints, and occupied-home rules.

---

## 2. Decoupling Wage Rates vs. Contractor Billing Rates

The LPM enforces a strict financial barrier between **Employee Wage** (the direct pay rate) and **Contractor Billing Rate** (the final hourly price billed to the homeowner).

```
[ Direct Employee Wage ]
           |
           +---> + Taxes & Insurance (FICA, FUTA, SUTA, Workers' Comp: ~20%)
           +---> + Labor Burden (Benefits, retirement, paid time off: ~15%)
           |
[ Fully Burdened Labor Rate ]
           |
           +---> + Operating Overhead Surcharges (Vehicles, small tools, safety: ~15%)
           +---> + Contractor Corporate Markup (Office admin, licensing, liability: ~20%)
           |
[ CONTRACTOR HOURLY BILLING RATE ]
```

### 2.1. Labor Multiplier Formula

$$\text{Contractor Hourly Billing Rate } (R_{\text{bill}}) = \text{Wage Rate } (R_{\text{wage}}) \times \mathcal{M}_{\text{burden}} \times \mathcal{M}_{\text{admin}}$$

Where:
*   $\mathcal{M}_{\text{burden}}$: Direct payroll burdens (typically `1.30` to `1.45` depending on trade risk/workers' comp rates).
*   $\mathcal{M}_{\text{admin}}$: Operational overhead and supervision markup (typically `1.25` to `1.35`).

---

## 3. Standard Trade Classification Directory

The LPM manages distinct productivity coefficients and billing rates for eight core residential trades.

| Trade Classification | Base Wage (Nat Avg) | Burden Multiplier ($\mathcal{M}_{\text{burden}}$) | Contractor Billing Rate | Typical Crew Units | Standard Production Basis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lead Carpenter** | `$38.00 / Hour` | `1.45` (Medium risk) | `$75.00 / Hour` | 1 Lead + 1 Apprentice | Deck framing, framing stairs, pergolas. |
| **Framing Carpenter** | `$28.00 / Hour` | `1.40` (Medium risk) | `$58.00 / Hour` | 2 Framers | Addition wall plates, roof rafters. |
| **Skilled Roofer** | `$26.00 / Hour` | `1.55` (High risk) | `$62.00 / Hour` | 1 Lead + 2 Roofers | Shingling, underlayments, ridge vents. |
| **Concrete Finisher** | `$32.00 / Hour` | `1.38` (Medium risk) | `$65.00 / Hour` | 1 Finisher + 2 Laborers | Stamped concrete, grading, screeding. |
| **Siding Installer** | `$24.00 / Hour` | `1.48` (High risk) | `$52.00 / Hour` | 2 Installers | Lap siding, flashing, housewrap. |
| **Specialist Mason** | `$42.00 / Hour` | `1.35` (Medium risk) | `$88.00 / Hour` | 1 Mason + 1 Tender | Brick veneer, stone retaining walls. |
| **Licensed Electrician**| `$46.00 / Hour` | `1.32` (Low risk) | `$95.00 / Hour` | 1 Electrician | Solar tie-ins, service panels. |
| **Skilled Laborer** | `$18.00 / Hour` | `1.35` (Medium risk) | `$38.00 / Hour` | N/A | Excavation, clean-up, demo. |

---

## 4. Labor Complexity Multipliers ($C_k$)

Base production rates represent optimal working environments (flat ground, easy staging, mild weather, unoccupied home). When conditions deviate, the LPM applies cumulative complexity multipliers:

$$\text{Adjusted Production Hours} (H_{\text{adj}}) = H_{\text{base}} \times \left( C_{\text{access}} \times C_{\text{height}} \times C_{\text{occupancy}} \times C_{\text{seasonal}} \times C_{\text{demo}} \right)$$

### 4.1. Site Access Modifier ($C_{\text{access}}$)
*   **Easy Access (`1.00`)**: Double gate, flat lot, concrete mixing trucks can drive directly to the pour site.
*   **Restricted Access (`1.15`)**: Backyard accessible only through standard single gate (width $< 36$ inches). Wheelbarrows or compact motorized dinkies required for material moving.
*   **Severe Obstruction (`1.30`)**: Townhome or zero-lot-line property. No side yard. All debris and new materials must be carted through garage or lifted over retaining walls.

### 4.2. Height / Elevation Modifier ($C_{\text{height}}$)
*   **Grade Level (`1.00`)**: Single-story work (0 to 10 feet).
*   **Second Story (`1.12`)**: Roof or siding installations between 10 to 22 feet. Ladder and harness work required. Material lifting takes longer.
*   **Third Story+ (`1.25`)**: High elevations ( $> 22$ feet). Scaffolding or boom lift rental required. Productivity drops due to extreme safety protocols.

### 4.3. Occupied-Home Constraint ($C_{\text{occupancy}}$)
*   **New Build / Vacant (`1.00`)**: Zero restrictions on noise, working hours, or site workspace containment.
*   **Occupied Home (`1.10`)**: Homeowner actively residing. Imposes dust barrier walls (HEPA air scrubbers), strict working hour limitations (8:00 AM to 5:00 PM), daily site sweeps, and pet containment coordination.

### 4.4. Seasonal Productivity Modifier ($C_{\text{seasonal}}$)
*   **Temperate (`1.00`)**: Daily high temperatures between $50^{\circ}\text{F}$ and $85^{\circ}\text{F}$. No active mud conditions.
*   **Extreme Heat / Summer (`1.15`)**: Temperatures $> 95^{\circ}\text{F}$. Requires frequent safety water breaks, shaded rest tents, and concrete chemical retarders.
*   **Extreme Cold / Winter (`1.25`)**: Temperatures $< 35^{\circ}\text{F}$. Shoveling snow, frozen ground digging, concrete heating blankets, and workers restricted by heavy thermal clothing.

---

## 5. Union & Prevailing Wage Classifications

The LPM integrates localized federal and municipal wage classifications for commercial or public projects when prompted:

*   **Davis-Bacon Act (DBA) Compliance**: When a project is flagged as "Prevailing Wage" (e.g. municipal solar, public-private additions), the engine disables private contractor average labor models. It locks the wage rates directly to the current published county-level DBA general decision schedule.
*   **Union Rate Tables**: If the project's geographic ZIP is flagged as a strong union market (e.g. San Francisco local plumbing/electrical), labor billing rates are automatically adjusted to reflect active collective bargaining agreements, including mandatory apprentice-to-journeyperson ratios.
