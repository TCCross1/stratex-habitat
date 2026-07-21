# OPERATION DESIGN STUDIO 2.0: SYSTEM MASTER SPECIFICATION
## SYSTEM FRAMEWORK, COGNITIVE CO-DESIGN, & INTERFACE ARCHITECTURE
**Version:** 2.0  
**Author:** General Atlas / Lead Digital Architect  
**Status:** Approved  
**Classification:** HABITAT-CONFIDENTIAL

---

## 1. MISSION & STRATEGIC VISION

Habitat Design Studio 2.0 represents the flagship interface and flagship experience of the Habitat ecosystem. It bridges the gap between raw, static home visualization and real-world construction execution. 

This platform is **not CAD software**; it is an **AI-assisted, cognitive home-planning co-design platform**. Its mission is to seamlessly transform homeowners from a state of speculative uncertainty ("I wonder what this would look like...") to high-confidence operational readiness ("I know exactly what I want to build, how much it will cost, and who is going to construct it").

```
+-------------------------------------------------------------------------------+
|                       HABITAT DESIGN STUDIO 2.0 PARADIGM                      |
+-------------------------------------------------------------------------------+
|                                                                               |
|  [ COGNITIVE CO-DESIGN ]   <--- (Dialogue, Context, Preferences) ---> [ AI ] |
|            |                                                            |     |
|            v                                                            v     |
|  +-------------------+        +--------------------+          +-------------+ |
|  | 3D DIGITAL TWIN   | <----> | BUDGET ESTIMATE    | <------> | CONTRACTOR  | |
|  | (Interactive PBR) |        | (Confidence Tiers) |          | (RFP Match) | |
|  +-------------------+        +--------------------+          +-------------+ |
|            ^                            ^                            ^        |
|            +----------------------------+----------------------------+        |
|                                         |                                     |
|                        "I know exactly what I want to build"                  |
+-------------------------------------------------------------------------------+
```

---

## 2. THE ENGINEERING LAWS OF HABITAT DESIGN

To ensure absolute safety, trust, and fidelity, every design, layout, and rendering inside Design Studio 2.0 must adhere strictly to the following **Engineering Laws**:

1. **Strict Context Segregation**: Every view, data layer, and report must clearly and unambiguously segregate:
   - **Verified Existing Conditions**: Sourced from the immutable Property Passport (e.g., current lot setbacks, structural walls, existing roof condition).
   - **AI-Generated Concepts**: Non-binding design recommendations, layouts, and style proposals.
   - **Estimated Costs**: Cost breakdowns categorized across the 4 localized Confidence Tiers.
   - **User Preferences**: Aesthetic overrides, material tastes, and budget limits set by the homeowner.
   - **Unknown Information**: Elements requiring on-site structural engineering, geotechnical soil samples, or physical verification.
2. **Immutable Passport Integrity**: No active design sandbox, scenario, or simulation shall overwrite the canonical **Property Passport** in MongoDB. The passport remains the immutable source of truth of verified physical conditions.
3. **隔离 (Isolation of Proposals)**: Proposed designs, ADU footprints, or layout adjustments remain fully isolated sandboxes until the project is physically constructed, inspected, verified by computer vision, and officially synchronized by the contractor.

---

## 3. CORE ARCHITECTURE OVERVIEW

Design Studio 2.0 operates as an event-driven, decoupled service-oriented architecture built to scale infinitely. It integrates the interactive front-end, a dynamic module registry, a localized cost estimation engine, and an AI orchestrator.

```
                    +--------------------------------------------+
                    |           Stratex React Frontend           |
                    |   - Interactive Twin PBR Workspace        |
                    |   - AI Chat & Budget Panels                |
                    +---------------------+----------------------+
                                          |
                                          v (JSON over WebSockets & HTTPS)
                    +--------------------------------------------+
                    |          FastAPI Gateway Router            |
                    +----+----------------+-----------------+----+
                         |                |                 |
                         v                v                 v
                 +---------------+ +--------------+ +---------------+
                 | Module Reg.   | | AI Assistant | | Cost Engine   |
                 | (Mongo/JSON)  | | (Gemini LLM)  | | (Local Index) |
                 +---------------+ +--------------+ +---------------+
                         |                |                 |
                         +----------------+-----------------+
                                          |
                                          v
                    +--------------------------------------------+
                    |             Persistence Layer              |
                    |   - MongoDB (Scenarios, Configs, State)    |
                    |   - AWS S3 (PBR Assets, Drone Scans, RFPs) |
                    +--------------------------------------------+
```

### Decoupled Sub-Engines
- **Dynamic Module Registry**: Standard interface that reads custom JSON documents to dynamically boot studios (e.g., ADU Studio, Pools, Decks) without writing backend code or running database migrations.
- **AI Design Orchestrator**: Manages contextual prompts, translates visual canvas actions into text instructions, and maintains chat session history.
- **Dynamic Cost Estimator**: Interfaces with localized ZIP-code labor indices, material dimensions, and historical contractor bidding patterns to generate dynamic pricing.

---

## 4. STRATEX UX/UI VISUAL SYSTEM

Following the **Stratex Design System**, the user interface uses a high-contrast, high-fidelity aesthetic that emphasizes structure, technical precision, and investor-grade polish.

### Typography & Fonts
- **Headers & Titles**: `Outfit` — Geometric, professional, modern.
- **Body Copy**: `IBM Plex Sans` — Technical, clean, highly readable.
- **Metrics, Costs, & Code**: `JetBrains Mono` — High contrast, precise, data-dense.

### Color Tokens (Command Center Theme)
- **Primary / Background**: Deep Space Charcoal (`#0B0F19`) & Rich Navy (`#111827`)
- **Accent High-Contrast**: Electric Blue (`#00F0FF`) & Cyber Neon Green (`#39FF14`)
- **Warnings & Alerts**: Warning Amber (`#FF9E00`) & Critical Red (`#FF0055`)
- **Muted text & Borders**: Steel Gray (`#4B5563`) & Ice White (`#E5E7EB`)

### Language Tone
The copy must be supportive, educational, and non-alarmist (**"always explain, never alarm"**). If an issue or conflict is found, the platform explains the technical reality and proposes actionable steps.

---

## 5. SYSTEM LAYOUT & MULTI-STUDIO PANELS

The workspace is divided into five modular, high-contrast panels, keeping the 3D Digital Twin centered as the main interface.

```
+---------------------------------------------------------------------------------+
|  HABITAT DESIGN STUDIO 2.0  [Modern Farmhouse Siding]  [ZIP: 80202]  [Menu]     |
+---------------------------------------------------------------------------------+
|  [ LEFT PANEL ]         |  [ CENTER STAGE: 3D DIGITAL TWIN ]  | [ RIGHT PANEL ] |
|                         |                                     |                 |
|  Active Zone List:      |  +-------------------------------+  |  Material Grid: |
|  [-] Exterior Walls     |  |                               |  |  +------------+ |
|    - Siding Main        |  |            [AFTER]            |  |  | SKU-9832A  | |
|    - Trim               |  |                               |  |  | James      | |
|    - Shutters           |  |      PBR Rendering Stage      |  |  | HardiePlank| |
|  [+] Structural         |  |                               |  |  | $14.20/sqft| |
|                         |  |    <=====[Split Slider]=====> |  |  +------------+ |
|  AI Chat Interface:     |  |                               |  |  +------------+ |
|  "Suggest trim color"   |  |           [BEFORE]            |  |  | SKU-1049B  | |
|  [Send]                 |  |                               |  |  | Azek Trim  | |
|                         |  +-------------------------------+  |  | $8.50/ft   | |
|                         |  [Drone]  [First-Person]  [1:1 AR]  |  +------------+ |
+---------------------------------------------------------------------------------+
|  [ BUDGET ANALYSIS PANEL (JETBRAINS MONO) ]                                    |
|  [Verified] James HardiePlank: $14,200  | [Estimated] Labor: $11,800            |
|  [Suggested] Ledgerstone: $4,500        | [Future] Structural Foundation: $2,500  |
+---------------------------------------------------------------------------------+
```

### The Five Core Panels
1. **Interactive Zone List (Left Upper)**: Vertical checklist of zones active within the current module configuration.
2. **AI Design Assistant Chat (Left Lower)**: Proactive conversation thread with inline recommendations, trade-offs, and conflict highlights.
3. **PBR Twin Rendering Stage (Center)**: Full-viewport interactive visualization canvas with the **Before/After Split Slider** and camera angle toggles.
4. **Material Swatch & Configuration Grid (Right)**: Catalog of physical swatches, SKU numbers, prices, and warranties, dynamically filtered by the active zone's valid product categories.
5. **Dynamic Cost Breakdown Bar (Bottom)**: Color-coded bar dividing project costs into **Verified** (Green), **Estimated** (Teal), **Suggested** (Orange), and **Future** (Gray) confidence levels.

---

## 6. SYSTEM NAVIGATION & ACTIVE PROJECTS PORTAL

Homeowner engagement is re-anchored around **Active Projects**, removing settings-centric navigation to guide the homeowner seamlessly from design to physical completion.

### Dynamic Route Architecture
- `/projects`: The Projects Portal. Features a rich grid of active project cards, draft concepts, and system-generated improvement recommendations.
- `/projects/:id/customize`: The main design workspace, dynamically mounting UI controls based on the selected module ID.
- `/projects/:id/compare`: side-by-side scenario comparison grid.
- `/projects/:id/budget`: Localized project costing sheet, tax indices, and active financing scenario modeler.
- `/projects/:id/contractors`: Bidding control room where the homeowner reviews performance cards and accepts direct contractor bids.

### The Unified Navigation Flow
```
[Projects Dashboard] ---> [Choose/Start Project] ---> [Interactive Customize]
                                                            |
                                                            v
[Contractor Match] <--- [Lock Specs] <--- [Budget & Finance] <--- [Compare Drafts]
```

This structural blueprint acts as the master index for all subsystem specifications. Refer to the specific sub-modules (`PROJECT_LIBRARY.md`, `MATERIAL_LIBRARY.md`, `PROJECT_TEMPLATE_SYSTEM.md`, etc.) for detailed database schemas, API contracts, and user interactions.
