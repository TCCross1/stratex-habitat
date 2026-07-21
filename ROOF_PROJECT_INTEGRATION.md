# DESIGN STUDIO ROOF PROJECT
## ARCHITECTURAL PROJECT CREATION AND PREPOPULATION

This document records the integration between the Home Steward AI and **Design Studio 2.0** (Task 7) for roof replacement planning.

---

## 1. PREPOPULATED PROPERTY CONTEXT

Upon action confirmation, a new Design Studio planning scenario is created. To prevent homeowner fatigue, the project is prepopulated with verified details from the Property Twin and DNA databases, with each item clearly labeled with its truth classification:

| Property Detail | Value | Truth Source | Classification |
| :--- | :--- | :--- | :--- |
| **Roof Area** | 3,200 sqft | Property DNA | `VERIFIED` |
| **Roof Pitch** | 6:12 | Digital Twin Geometry | `VERIFIED` |
| **Existing Material** | Asphalt Shingle | Living Timeline | `VERIFIED` |
| **Installation Year** | 2019 (Estimated) | Living Timeline | `ESTIMATED` |
| **Penetrations** | 2 Chimneys, 4 Vents | Digital Twin Geometry | `VERIFIED` |
| **Manufacturer Warranty**| 10-Year Limited | Homeowner Upload | `HOMEOWNER-REPORTED` |
| **Decking Condition** | Unknown | Tactile Field Audit | `UNKNOWN` |

---

## 2. COMPARING ROOFING SYSTEMS

The homeowner can toggle and compare at least three distinct roofing material options. Swapping materials triggers recalculations in the design assembly engine:

1. **Architectural Asphalt Shingles (e.g., GAF Timberline HDZ):**
   * *Description:* High-durability multi-layered asphalt shingles.
   * *Cost Tier:* Standard.
   * *Confidence:* High (standard installation patterns apply).
2. **Premium Standing Seam Metal (e.g., DECRA Standing Seam):**
   * *Description:* Interlocking vertical metal panels. Outstanding thermal reflection.
   * *Cost Tier:* Premium.
   * *Confidence:* High (requires specialized labor rates).
3. **Traditional Spanish Clay Tile:**
   * *Description:* Heavyweight, fireproof traditional clay tiles.
   * *Cost Tier:* Ultra-Premium (requires structural verification due to weight).
   * *Confidence:* Medium (requires physical deck weight limit audit).

---

## 3. DYNAMIC ASSEMBLY PROPAGATION

Modifying the material selection in the Design Studio interface automatically propagates modifications across all downstream modules:
* **Visualization:** Updates the 3D Digital Twin rendering shader to match selected colors and textures.
* **Quantities Takeoff:** Recalculates material square counts, accessory counts (ridge caps, starter strips, flashing lengths), and waste factors (10% standard waste for shingles, 5% for metal).
* **Estimate Calculations:** Triggers immediate cost recalculations in the Project Estimator.
* **Readiness Score:** Adjusts the project's checklist requirements based on structural weight constraints.
