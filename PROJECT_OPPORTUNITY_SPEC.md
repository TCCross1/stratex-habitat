# CENTCOM DIRECTIVE H-003: PROJECT OPPORTUNITY SPECIFICATION
## SYSTEM ARCHITECTURE FOR THE PROJECT OPPORTUNITY ENGINE™
**Version:** 1.0  
**Author:** Lead Software Architect  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Executive Summary & Core Philosophy

The **Project Opportunity Engine™** is the architectural gateway transforming raw, subjective homeowner ideas into objective, contractor-ready **Project Opportunities**. 

### 1.1. Core Mission
Unlike legacy residential contractor platforms, **the goal of this engine is NOT lead generation.** Traditional lead generation relies on selling high-volume, low-quality contact information (leads) to contractors, which leads to homeowner fatigue from spam and contractor frustration from unvetted scopes.

Instead, the Project Opportunity Engine™ is engineered to deliver **fully informed, high-quality, pre-scoped project packages.** Homeowners should never need to start from scratch when describing their needs. Every Project Opportunity contains comprehensive property intelligence, 3D visual concepts, a canonical physical model, localized pricing breakdowns, and an AI-driven compatibility review. This provides contractors with all the intelligence necessary to prepare precise, binding, and meaningful proposals.

```
+--------------------------------------------------------------------------------+
|                        PROJECT OPPORTUNITY CONVERSION PIPELINE                 |
+--------------------------------------------------------------------------------+
|  HOMEOWNER SANDBOX                                                             |
|  - Raw Ideas & Material Experiments                                            |
|  - Volatile Selections (Before/After Slider)                                   |
|                                                                                |
|                                     | (Ingested & Processed)                   |
|                                     v                                          |
|                                                                                |
|  PROJECT OPPORTUNITY ENGINE™                                                   |
|  - Resolves Canonical Property DNA (No Duplication)                            |
|  - Runs AI Compatibility & Structural Harmony Solvers                          |
|  - Compiles Complete Contractor Opportunity Package                            |
|                                                                                |
|                                     | (Enriched & Published)                   |
|                                     v                                          |
|                                                                                |
|  CONTRACTOR PORTAL                                                             |
|  - Receives Full Scope, Concepts & Digital Twin Reference                      |
|  - Evaluates Verified Measurements & Passport Evidence                         |
|  - Submits High-Precision, Low-Risk Proposals                                  |
+--------------------------------------------------------------------------------+
```

---

## 2. The Project Opportunity Package (POP)

The Project Opportunity Package is a structured, canonical, and self-contained data container that aggregates property, design, preference, and AI intelligence blocks. To enforce system-wide data integrity, all blocks reference shared, canonical resources in the Habitat ecosystem (e.g., the Property DNA Registry and the Digital Home Passport) rather than duplicating them.

### 2.1. Property Block
The property block establishes the physical and structural context of the project. It references the canonical, immutable property record.

* **Property Name:** The designated name of the property (e.g., *Villa Horizon*).
* **Address:** The verified physical and postal address of the property, including latitude, longitude, and municipal boundaries.
* **Property DNA Snapshot:** A semantic representation of the physical home. It contains structural dimensions, historical architectural styles, structural materials, foundation types, wind exposure classifications, and thermal envelope metrics.
* **Overall Home Health:** A score (0–100) representing the current physical integrity of the property based on the latest physical scans and sensor readings stored in the Digital Home Passport.
* **Aesthetic, Weatherization, & Efficiency (AWE) Index:** A composite index detailing the home's performance across three key vectors:
  * *Aesthetic (0.0-1.0):* Architectural alignment and curb appeal.
  * *Weatherization (0.0-1.0):* Resistance to local climate conditions (e.g., wind, seismic, snow load).
  * *Efficiency (0.0-1.0):* Thermal envelope rating, R-values, and solar potential.
* **Existing Materials:** A queryable catalog of active materials on the structure (e.g., *Siding: 3-coat Portland Cement Stucco, Trim: Cedar Wood, Glazing: Double-pane Low-E Vinyl*).
* **Digital Twin Reference:** A secure, cryptographically signed URI pointing to the active 3D model, PBR textures, and spatial point cloud of the home in the Habitat Object Storage system.

### 2.2. Project Block
The project block defines the functional classification of the renovation. The platform officially supports 16 distinct project types, each governed by its own validation rules and physical constraints in the Module Registry.

| Project Type | Primary Focus | Structural Consideration |
| :--- | :--- | :--- |
| **Garage** | Vehicular storage, accessory workshops | Slab loads, overhead door clearances, firewalls |
| **Deck** | Elevated exterior wooden/composite platforms | Post footings, ledger connections, dead/live loads |
| **Patio** | Grade-level outdoor concrete or stone spaces | Subgrade drainage, soil compaction, slope runoff |
| **Pool** | Below-grade/above-grade water recreation systems | Excavation limits, utility lines, structural shells |
| **Room Addition** | Expanding the existing home envelope | Foundation expansion, tie-ins, thermal envelopment |
| **Concrete** | Foundation work, retaining walls, walkways | Rebar specifications, curing PSI, frost depth |
| **Pergola** | Open-roof shade structures | Wind-uplift calculations, beam-span capacities |
| **Fence** | Boundary demarcations and privacy screens | Wind-load windage, post depth, property lines |
| **Landscape** | Plantings, turf, softscape grading | Irrigation requirements, regional soil profiles, runoff |
| **Outdoor Kitchen** | Exterior cooking and dining spaces | Exterior gas lines, sanitary drains, fire-rated framing |
| **ADU** | Standalone accessory dwelling units | Multi-trade utilities, municipal zoning setbacks |
| **Roof** | Weather-shedding roof coverings | Pitch limits, ventilation ratios, snow loads |
| **Windows** | Aperture glazing and frames | Header spans, egress codes, energy R-values |
| **Doors** | Entryways, secondary egress, security portals | Framing sizes, weatherstripping, thermal bridges |
| **Solar** | Photovoltaic generation and storage arrays | Roof-load capacities, electrical service panel amps |
| **Custom** | Bespoke exterior/interior structural alterations | Multi-disciplinary review, custom engineering |

### 2.3. Design Block
This block captures the aesthetic and material selections designed by the homeowner within the Habitat Design Studio workspace.

* **Saved Concept:** The active design state representing the selected design schema.
* **AI Renderings:** A collection of high-resolution, photorealistic design scenes generated by the AI Orchestrator showing material and structural configurations under varying lighting presets.
* **Before/After Views:** Side-by-side or sliding overlay comparisons showing the original façade (Before) and the proposed AI rendering (After) from identical camera angles.
* **Selected Materials:** A precise list of materials, including manufacturer, product line, colorway, SKU, and performance characteristics (e.g., *Siding: James Hardie HardiePlank Lap Siding, Select Cedarmill, Iron Gray*).
* **Color Palette:** A curated, harmonized color palette containing exact Hex/RGB codes and material sheen metadata used in the design.
* **Version History:** An immutable changelog containing previous iterations of the design, allowing the homeowner to compare and restore past configurations (e.g., `v1`, `v2`, `v3`).

### 2.4. AI Project Intelligence Block
The AI Project Intelligence Block is the reasoning engine of the opportunity. It automatically parses the property DNA and selected designs to produce professional, context-grounded evaluations. **Crucially, every recommendation in this block must explicitly explain the logical "WHY" and every estimate must identify its "CONFIDENCE LEVEL".**

* **Compatibility Review:** Automated check of local building codes, HOA restrictions, and physical material compatibility (e.g., ensuring selected composite decking is rated for the home's local temperature swings and complies with HOA fire-safe material mandates).
* **Architectural Harmony:** An architectural evaluation analyzing how well the design fits the original style of the home (e.g., ensuring a modern horizontal panel design complements a Mid-Century Modern profile, or flags potential style conflicts on a Tudor home).
* **Material Recommendations:** Proactive, data-backed suggestions for alternative or complementary products to maximize longevity, thermal efficiency, or budget.
* **Suggested Improvements:** Value-add suggestions such as upgrading to rot-resistant fasteners, adding soffit ventilation during a roof replacement, or pre-wiring for solar during a siding overhaul.
* **Estimated Complexity:** A multi-dimensional difficulty score (Low, Medium, High, Extreme) based on site accessibility, structural complexity, utility relocations, and permit requirements.
* **Budget Assumptions:** An itemized, localized estimation of material, labor, permits, and contingencies.
* **Confidence Levels:** Every cost line-item and scope estimation must be labeled with one of the four official confidence tiers: **Verified, Estimated, Suggested, or Future**.

---

## 3. Homeowner Preferences

Homeowners establish boundaries and guidelines for how contractors should approach the opportunity. These are not guesses; they represent explicit boundaries that guide the proposal matching and formulation process.

```
+--------------------------------------------------------------------------+
|                        HOMEOWNER PREFERENCES ENGINE                      |
+--------------------------------------------------------------------------+
|  [ Budget ]     Desired: $25,000      Max Cap: $30,000                   |
|  [ Timeline ]   Preferred: Fall 2026  Hard Deadline: Nov 15, 2026        |
|  [ Must-Haves ] Maintenance-free siding, lifetime manufacturer warranty  |
|  [ Nice-Haves ] Accent stone wainscoting, integrated LED soffit lights   |
|  [ Distance ]   Preferred Contractor Max Distance: 25 miles              |
|  [ Comm Pref ]  SMS & Standard Portal Chat, No Unscheduled Phone Calls   |
|  [ Financing ]  Interested in zero-down, low-APR financing partnerships  |
+--------------------------------------------------------------------------+
```

* **Desired Budget:** The preferred investment level and the absolute ceiling (max budget cap).
* **Desired Timeline:** Preferred project start window (e.g., *September 2026*) and any hard deadlines (e.g., *Must complete before winter snows - Nov 15*).
* **Must-Haves:** Non-negotiable scope items (e.g., *Must use Class A fire-rated roofing materials*).
* **Nice-to-Haves:** Optional items that can be discarded to meet budget constraints (e.g., *Accent stone wainscoting on the garage front*).
* **Special Requests:** Specific homeowner notes, such as pet safety requirements (e.g., *Keep yard fence closed during work*), property access limits, or preservation of existing landscaping.
* **Preferred Contractor Distance:** Maximum travel distance from the property (e.g., *Within 25 miles*) to favor local support and faster response times.
* **Communication Preference:** Explicit communication channel configurations (e.g., *Portal Chat & SMS only; do not call unless urgent*).
* **Financing Interest (Optional):** Indication of whether the homeowner is interested in third-party or contractor-offered financing options.

---

## 4. The Contractor Package

To ensure contractors do not feel they are buying "leads" or "cold contact info", they receive an incredibly detailed, high-fidelity project binder. This allows them to spend their time preparing actual bids rather than chasing unvetted inquiries.

The Contractor Package contains:

1. **Project Summary:** A clear, concise overview of the project scope, homeowner intent, and key parameters.
2. **Images:** Before pictures, photorealistic AI renderings from the Design Studio, and annotated diagrams showing work boundaries.
3. **Digital Twin References:** Secure access to the 3D model layers, allowing contractors to take digital measurements, view structural sections, and understand the physical context of the site.
4. **Material Selections:** A complete Material Specification Sheet locking in skew numbers, colors, profile dimensions, and exact product families.
5. **Measurements (Where Verified):** Precise calculations (e.g., square footage of walls, linear footage of trim) labeled with verification sources (e.g., *Verified via 3D Lidar Scan by Certified Reviewer - 98.7% Accuracy*).
6. **Budget Range:** The homeowner's desired budget range combined with the AI pricing engine’s estimated regional costs.
7. **AI Summary:** An executive-level technical summary of the project complexity, structural obstacles, and local permit requirements.
8. **Relevant Passport Evidence:** Cryptographically signed logs from the Digital Home Passport documenting the historical health of structural sub-systems, previous inspections, and surrounding asset ages.
9. **Questions Still Unanswered:** An interactive portal section displaying open, unclarified questions where contractors can submit specific technical inquiries before bidding.
10. **Opportunity Status:** The current state of the opportunity within the lifecycle state-machine.

---

## 5. Engineering Requirements & Principles

To maintain data integrity, scalability, and absolute trust, the Project Opportunity Engine™ must strictly adhere to the following architectural constraints:

### 5.1. No Duplicate Passport Data
The system must never copy or clone historical data from the Digital Home Passport into a local Project Opportunity table. All Passport information (scans, inspection reports, warranty registries) must be referenced via canonical, immutable references (`passport_id`). This ensures that if a Passport is updated, all active opportunities reflect the real-time state.

### 5.2. No Duplicate Property DNA
The physical, spatial, and structural characteristics of the home are canonical. The Opportunity Engine must point to the shared Property DNA record (`property_id`). Modifying material selections in a project concept does not alter the underlying Property DNA until the project is marked as "Completed" and verified.

### 5.3. Referential Canonical Ingestion
All Project Opportunity Packages (POPs) must ingest and reference external data using a strictly normalized, relational JSON structure, eliminating flat data duplication across sub-systems.

### 5.4. Universal Cost Confidence Labeling
The system is prohibited from displaying any cost or estimate without attaching its verified confidence tier. This prevents homeowner sticker shock and protects contractors from being held to loose, conceptual AI pricing.

### 5.5. AI Reason Grounding
The AI Orchestrator cannot produce naked design or material suggestions. Every suggestion must be backed by a deterministic, grounded logic block citing specific values from the Property DNA (e.g., local wind zone ratings, architectural style matching vectors, or material durability constraints).
