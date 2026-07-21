# CENTCOM DIRECTIVE H-011: MAINTENANCE COACH
## MAINTENANCE INTELLIGENCE LAYER & RECORD VALIDATION SPECIFICATION
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Executive Summary & Objective

The **Maintenance Coach** is Habitat's core intelligence layer for ongoing property preservation. Rather than offering static checklist templates, the Maintenance Coach synthesizes real-time sensor telemetry, property material parameters, regional weather conditions, and seasonal guidelines to create a **dynamic, prioritized preservation ledger**.

---

## 2. Dynamic Prioritization Framework

The Coach calculates the priority score $P$ for every maintenance action utilizing three primary variables:

$$P = (\text{System Criticality} \times 0.40) + (\text{Time-to-Decay} \times 0.35) + (\text{Environmental Risk} \times 0.25)$$

### 2.1. Criticality Matrix

| Subsystem Class | Description | System Weight ($W_{\text{sys}}$) |
| :--- | :--- | :---: |
| **Life Safety & Structural** | Fire detection, gas, structural foundation, active load pathways. | **10.0** |
| **Envelope Protection** | Roof deck, exterior siding, window flashings, basement sheathing. | **9.0** |
| **Primary Mechanicals** | Main HVAC heating, electrical service panels, sewer lines, water heating. | **8.0** |
| **Secondary Amenities** | Comfort ventilation, water filtration, irrigation, decking surfaces. | **5.0** |
| **Aesthetic / Minor** | Interior paint, molding trim, pathway pavers. | **2.0** |

### 2.2. Scoring Definitions
* **System Criticality:** Evaluates the impact of failure on life safety, structural decay, or cascading envelope damage.
* **Time-to-Decay ($T_{\text{decay}}$):** Tracks the interval since the last recorded maintenance or inspection relative to the manufacturer’s recommended service interval.
* **Environmental Risk ($E_{\text{risk}}$):** Evaluates weather conditions (e.g., cold waves, heavy rain, wind storms) and local climate exposures that accelerate system failure.

---

## 3. Preservation Action Structure

Every maintenance recommendation must present the homeowner with clear, actionable, and non-alarmist data across four core areas:

```
+---------------------------------------------------------------------------------+
| MAINTENANCE ACTION: Sump Pump Operational Test                                  |
+---------------------------------------------------------------------------------+
| NARRATIVE      | "Your sump pump has performed beautifully over the years.     |
|                | Testing it today ensures it is ready for spring rains."        |
+---------------------------------------------------------------------------------+
| WHY IT MATTERS | "Keeps rising groundwater out of your lower crawlspace,        |
|                | maintaining structural framing and dry soil conditions."       |
+---------------------------------------------------------------------------------+
| SPECS & GUIDES | - Est. Time: 15 mins | Planning Cost: $0                      |
|                | - Class: DIY (Simple)                                          |
|                | - Manual Link: [AO Smith Sump Manual (2021)]                   |
|                | - Warranty Link: [10-Yr Sump Pump Warranty]                     |
+---------------------------------------------------------------------------------+
```

### 3.1. DIY versus Professional (Pro) Determination

To maintain home safety and property preservation standards, tasks are categorized based on risk and tool requirements:

* **DIY (Simple):** Tasks requiring basic tools and minimal safety hazards (e.g., swapping furnace filters, testing smoke detectors, flushing water heaters).
* **DIY (Advanced):** Tasks requiring intermediate skills and specialty equipment (e.g., minor shingle patch, weatherstripping application, wood deck sealing).
* **Professional (Pro):** Tasks involving high-voltage electrical, gas lines, refrigerant handling, structural joists, or high ladder work (e.g., service panel upgrades, heat pump service, structural crawlspace shoring).

---

## 4. Maintenance Completion & Verification Lifecycle

A key vulnerability of digital properties is the accumulation of unverified maintenance assertions. Habitat implements a dual-ledger status protocol to track completion states accurately without diluting canonical truth:

```
[Task Initiated] ---> [Homeowner Completes Task] ---> [Status: HOMEOWNER-REPORTED]
                                                               |
                                                               v (Requires validation)
                                                    [Stratex Core Inspection]
                                                               |
                                                               v
                                                    [Status: VERIFIED (Core)]
```

### 4.2. Status Lifecycle Protocol

1. **Pending/Overdue:** The maintenance task is active and needs attention.
2. **Completed (Homeowner Assertion):**
   * The homeowner clicks "Complete" in the interface.
   * **Rule:** The system marks this task as `HOMEOWNER-REPORTED` (Planning Classification).
   * **Requirement:** The homeowner is prompted to enter:
     * Completion date.
     * Material receipts or product barcodes (optional).
     * High-resolution photo of the finished work (highly recommended).
3. **Verified (Professional Audit):**
   * **Rule:** This status is granted **only** when a Stratex Core certified inspector or connected IoT sensor telemetry verifies the completed state of the system during a formal review.
   * **Execution:** Once verified, the task status transitions to `VERIFIED` (Canonical Classification) and is written to the immutable timeline ledger.

---

## 5. System Interfacing & Timeline Synced History

When a maintenance task is completed, the Maintenance Coach issues an update thread to the Living Timeline. This ensures the home's narrative reflects the home's active care history, which is critical for retaining property valuation during future title transfers.
