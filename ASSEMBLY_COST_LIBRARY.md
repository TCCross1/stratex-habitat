# CENTCOM DIRECTIVE H-009: ASSEMBLY COST LIBRARY
## REUSABLE ASSEMBLY TEMPLATES, COMPONENT SCHEMAS, & TRADE SEQUENCES
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Assembly-Based Estimating Philosophy

The Habitat Project Estimator™ rejects flat-rate square-foot calculations for complex residential projects. Estimating a deck as a simple "$60 per square foot" hides critical structural differences (e.g., footings, elevation, stairs, soil types). 

Instead, the platform builds every estimate using **Reusable Assemblies**. An Assembly is an intelligent container mapping physical materials, labor activities, specialized equipment, trade dependencies, and waste factors to a specific structural system.

```
                         [ MASTER ASSEMBLY BLOCK ]
                                    |
     +-----------------+------------+------------+-----------------+
     |                 |                         |                 |
     v                 v                         v                 v
[ Materials ]    [ Labor Hours ]           [ Equipment ]     [ Dependencies ]
- Raw SKUs       - Trades & burden         - Machinery       - Sequenced
- Waste %        - Production rate         - Day/Week rates  - Pre-requisites
```

---

## 2. Assembly Schema Definition

Each assembly represented in the library adheres to the following structural metadata:

*   **Assembly ID**: Unique system identifier (`ASB-[CAT]-[TYPE]`).
*   **Base Unit of Measure**: The standard unit of pricing (e.g., `CY`, `SQFT`, `SQ`, `LF`).
*   **Production Basis**: The standard quantity output for a standardized trade crew working one 8-hour shift.
*   **Trade Dependencies**: Prerequisite assemblies or preparation steps.
*   **Dynamic Modifiers**: Adjustment rules for climate, soil, or site accessibility.

---

## 3. Core Assembly Catalogs

Below are the detailed component breakups for four standard structural assemblies in the library.

### 3.1. Stamped Concrete Patio Assembly (`ASB-CONC-STAMPED`)
*   **Base Unit**: `SQFT`
*   **Crew Composition**: 1 Finisher Foreperson, 2 Concrete Laborers, 1 Equipment Operator.
*   **Production Rate**: 350 SQFT per 8-hour shift.

```
Component Breakdown (per 100 SQFT):
├── 1. Excavation & Grading (Labor + Equipment)
│   ├── Operator + Laborer: 1.5 Hours
│   └── Skid Steer / Bobcat: 0.187 Days (Daily rate: $350)
├── 2. Gravel Subbase (Material + Labor)
│   ├── Crusher Run Gravel: 2.5 Tons ($42/Ton)
│   └── Compaction Roller: 0.187 Days (Daily rate: $110)
├── 3. Formwork & Reinforcement (Material + Labor)
│   ├── 2x4 SPF Lumber & Stakes: 35 LF ($2.20/LF)
│   ├── #4 Steel Rebar (12" Grid): 110 LF ($1.15/LF)
│   └── Tie Wire & Dobies: 1 Lot ($15.00)
├── 4. Concrete Pouring & Finishing (Material)
│   ├── 4000 PSI Ready-Mix Concrete: 1.6 CY ($145/CY)
│   └── Chute/Pump Surcharge Allowance: 1 Lot ($35.00)
├── 5. Color & Stamping System (Material + Labor)
│   ├── Integral Color Dye (Deep Charcoal): 4 Bags ($28/Bag)
│   ├── Powder Release Agent (Contrast Amber): 1 Pail ($45/Pail)
│   └── Polyurethane Concrete Sealer: 1.2 Gallons ($38/Gal)
└── 6. Operations & Cleanup
    └── Disposal/Dumpster Surcharge: 1 Lot ($45.00)
```

---

### 3.2. Premium Architectural Shingle Roof Assembly (`ASB-ROOF-ARCH`)
*   **Base Unit**: `SQ` (100 SQFT)
*   **Crew Composition**: 1 Roofing Lead, 3 Roofers.
*   **Production Rate**: 4.0 SQ per 8-hour shift (Tear-off + Re-roof).

```
Component Breakdown (per 1.0 SQ):
├── 1. Demolition & Tear-Off (Labor + Disposal)
│   ├── Shingle Tear-Off & Pull Nails: 2.0 Labor Hours
│   └── Shingle Disposal Dumpster Surcharge: 0.05 Tons ($110/Ton)
├── 2. Underlayment & Deck Protection (Material)
│   ├── Ice & Water Shield (Valleys & Eaves): 30 SQFT ($1.25/SQFT)
│   └── Synthetic Roofing Underlayment: 105 SQFT ($0.18/SQFT)
├── 3. Architectural Shingles (Material + Waste)
│   ├── GAF Timberline HDZ Shingles (SKU-Level): 1.10 SQ ($115/SQ) (Includes 10% Waste)
│   └── Coil Nails & Staples: 1 Lot ($6.00)
├── 4. Accessories & Trim (Material)
│   ├── Starter Strips & Ridge Caps: 15 LF ($3.10/LF)
│   └── Drip Edge (Aluminum): 20 LF ($2.20/LF)
├── 5. Ventilation (Material + Labor)
│   └── Cobra Rigid Ridge Vent: 10 LF ($6.50/LF)
└── 6. Labor Installation
    └── Skilled Roofer Hourly Allocation: 4.5 Hours
```

---

### 3.3. Fiber Cement Siding Assembly (`ASB-WALL-FIBERCEMENT`)
*   **Base Unit**: `SQFT`
*   **Crew Composition**: 1 Carpenter Lead, 1 Siding Installer, 1 Apprentice.
*   **Production Rate**: 240 SQFT per 8-hour shift.

```
Component Breakdown (per 100 SQFT):
├── 1. Weather Barrier & Flashings (Material)
│   ├── Tyvek HomeWrap Housewrap: 110 SQFT ($0.18/SQFT) (10% overlap)
│   ├── Flashing Tape & Window Pan flashing: 15 LF ($1.45/LF)
│   └── Seam Sealing Tape: 1 Roll Allocation ($12.00)
├── 2. Fiber Cement Siding Boards (Material + Waste)
│   ├── James Hardie Select Cedarmill Lap Siding (SKU JHM-8041-FC): 108 SQFT ($3.85/SQFT)
│   └── Hot-Dipped Galvanized Blind Nails: 1 Box Allocation ($18.00)
├── 3. Joint Sealants & Corner Trim (Material)
│   ├── HardieTrim Corner Boards (Color-Matched): 12 LF ($4.50/LF)
│   └── Elastomeric Siding Caulk (Color-Matched): 2 Tubes ($9.50/Tube)
├── 4. Access Equipment Surcharge (Equipment)
│   └── Pump Jack & Scaffolding Weekly Surcharge Pro-Rata: 0.125 Weeks ($45.00)
└── 5. Labor Installation
    └── Siding Installer Crew Hours: 3.33 Hours
```

---

### 3.4. Composite Deck Assembly (`ASB-DECK-COMPOSITE`)
*   **Base Unit**: `SQFT`
*   **Crew Composition**: 1 Lead Carpenter, 2 Framing Carpenters.
*   **Production Rate**: 80 SQFT per 8-hour shift.

```
Component Breakdown (per 100 SQFT):
├── 1. Concrete Footings (Material + Labor)
│   ├── 12" Sonotube Concrete Forms: 3 LF ($8.50/LF)
│   ├── Pre-mixed Concrete bags (80lb): 8 Bags ($7.50/Bag)
│   └── 2-Man Power Auger Rental: 0.125 Days (Daily rate: $110)
├── 2. Structural Framing Lumber (Material)
│   ├── 2x10 Pressure Treated Joists & Ledgers: 125 LF ($3.15/LF)
│   └── 6x6 Pressure Treated Support Posts: 12 LF ($8.20/LF)
├── 3. Connection Hardware (Material)
│   ├── Simpson Strong-Tie Joist Hangers & Fasteners: 12 Units ($4.25/Unit)
│   └── 1/2" x 8" Ledger Tension Bolts: 6 Units ($7.50/Unit)
├── 4. Composite Decking Surface (Material + Waste)
│   ├── Trex Transcend Decking (SKU TRX-4492-CD): 105 SQFT ($7.50/SQFT)
│   └── Trex Hideaway Hidden Fasteners (Box): 1 Box Allocation ($38.00)
├── 5. Railing & Post Caps (Material)
│   └── Composite Railing Kit (Classic Black): 12 LF ($42.00/LF)
└── 6. Labor Installation
    └── Carpenter Crew Framing & Decking Installation: 3.75 Crew Hours
```

---

## 4. Trade Dependency & Sequence Logic

Estimates must respect structural reality. The system restricts parallel installation loops, validating sequences against a **Trade Dependency Tree**. If a homeowner schedules "Siding" and "Framing Addition" in the Project Timeline, the system enforces the chronological structural flow:

```
               [ EXCAVATION & FOOTINGS ]
                          |
                          v
                 [ CONCRETE POURING ]
                          |
                          v
                 [ STRUCTURAL FRAMING ]
                          |
       +------------------+------------------+
       |                                     |
       v                                     v
[ ROOF DECK SHEATHING ]               [ EXTERIOR SIDING ]
       |                                     |
       v                                     v
[ SHINGLE INSTALLATION ]              [ TRIM & SEALING ]
```

### 4.1. Sequence Validation Rules
*   **Rule 1 (Concrete Curing)**: Framers cannot start framing until Concrete Footings or Slabs have cured for a minimum of 48 hours in warm seasons, and 72 hours in winter.
*   **Rule 2 (Dry-In Enclosure)**: Siding panels and roofing shingles cannot be installed until structural wall/roof sheathing and weather barriers (Tyvek/Underlayment) have been validated as complete.
*   **Rule 3 (Electrical/Mechanical Prep)**: Outdoor kitchens or ADU walls cannot be dry-walled or sealed until plumbing, gas line pressure-checks, and electrical rough-ins are certified as completed.

The estimating API verifies the sequence array and applies mobilization multipliers ($M_{\text{mobil}})$ if a disorganized timeline forces subcontractors to make multiple site visits.
