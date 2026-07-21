# CENTCOM DIRECTIVE H-001: DESIGN STUDIO ARCHITECTURE SPECIFICATION
## SYSTEM FRAMEWORK, MODULAR ARCHITECTURE, & UX SPECIFICATION
**Version:** 1.0  
**Author:** Lead Software Architect  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Executive Summary

This architecture specification outlines the transformation of the **Habitat Design Studio** from a legacy single-image exterior material visualizer into a highly modular, AI-assisted residential home planning platform. 

### Core Vision
The evolved Habitat Design Studio bridges the gap between raw visualization and execution. Instead of acting as a complex, specialized CAD application, it operates as a digital architect and designer—actively collaborating with homeowners to imagine, visualize, compare, plan, and prepare renovations on their actual homes. 

```
+--------------------------------------------------------------------------+
|                        HABITAT DESIGN STUDIO EVOLUTION                   |
+--------------------------------------------------------------------------+
|   LEGACY: Exterior Finishes Visualizer                                   |
|   - 1 Static Façade (Preset)                                             |
|   - Linear 1-Step Workflow (Select → Render)                             |
|   - Basic Static Tier Costing ($$, $$$)                                  |
|                                                                          |
|                                  | (Transformation via Directive H-001)  |
|                                  v                                       |
|                                                                          |
|   EVOLVED: Multi-Studio Residential Planning Platform                    |
|   - 14+ Plug-and-Play Design Modules (Extensible Registry)               |
|   - Structured Project Opportunity Lifecycle (9 Stages, End-to-End)     |
|   - AI-Driven Collaborative Workflow (Assists, Explains, Calibrates)     |
|   - Real-Time Localized Dynamic Pricing Engine (4 Confidence Tiers)      |
+--------------------------------------------------------------------------+
```

### Key Deliverables
* **Modular Module Registry**: Standard interface definition and backend schema supporting seamless expansion from exterior finishes into kitchens, landscaping, pools, additions, and future studios.
* **Unified Project Navigation**: Transition from settings-centric pages to a natural, project-focused user flow.
* **The Project Opportunity Pipeline**: A robust state-machine tracking homeowner concepts from raw ideas to completed projects and updated digital home passports.
* **Context-Aware AI Workflow**: Conversational AI guidance that explains material tradeoffs, designs with local architectural context, and itemizes costs clearly across four verification tiers (**Verified, Estimated, Suggested, and Future capability**).
* **Reusable UI Component Inventory**: Standardized interface definitions for consistent visual design and reuse.
* **Extensible Schema Definition**: A robust data framework supporting diverse future project types without system redesign.

---

## 2. Architecture Diagram & Overview

The platform uses a layered, event-driven service-oriented architecture designed to scale. It fully decouples the interactive presentation layer, the modular orchestrator, the AI assistant, the dynamic pricing engine, and the third-party partner integration interfaces.

### System Architecture Layout

```
                  +----------------------------------------------+
                  |               React Frontend                 |
                  |  +------------------------+  +------------+  |
                  |  |  Workspace (3D/PBR)    |  | UI Library |  |
                  |  +------------------------+  +------------+  |
                  +-----------------------+----------------------+
                                          | JSON over HTTPS
                                          v
                  +----------------------------------------------+
                  |             API Gateway / FastAPI            |
                  +-----------------------+----------------------+
                                          |
         +--------------------------------+--------------------------------+
         |                                |                                |
         v                                v                                v
+-------------------+            +-------------------+            +-------------------+
|  Module Registry  |            |  AI Orchestrator  |            |  Dynamic Estimator|
|  - Siding / Roof  |            |  - LLM Assistant  |            |  - Regional Rates |
|  - Kitchen / Bath |            |  - Vision Parser  |            |  - Material Specs |
|  - ADUs / Pools   |            |  - Prompt Builder |            |  - Tax / Permits  |
+--------+----------+            +--------+----------+            +--------+----------+
         |                                |                                |
         +--------------------------------+--------------------------------+
                                          |
                                          v
                  +----------------------------------------------+
                  |               Persistence Layer              |
                  |  +------------------------+  +------------+  |
                  |  | MongoDB (State/Metadata)  |  |  AWS S3  |  |
                  |  +------------------------+  +------------+  |
                  +-----------------------+----------------------+
                                          |
                                          v
                  +----------------------------------------------+
                  |          External Systems & Network          |
                  |  +------------------------+  +------------+  |
                  |  |  Contractor Portals    |  | StratexCore|  |
                  |  +------------------------+  +------------+  |
                  +----------------------------------------------+
```

### Components Description
1. **React Presentation Layer**: Hosts the interactive 3D/PBR Workspace, utilizing the standardized UI Component Library (Project Cards, Material Library, Comparison Views, Mood Boards).
2. **API Gateway / FastAPI Router**: Authenticates users, validates requests, and dispatches tasks to internal sub-engines.
3. **Module Registry**: Maintains the active and future module configurations, acting as the single source of truth for available design zones, product libraries, and structural rules.
4. **AI Orchestrator**: Bridges the user with Gemini/LLM models for semantic styling and image generation. Contains an image-parsing pipeline that automatically segments and masks structural regions.
5. **Dynamic Estimator**: Connects local pricing indices, material dimensions, and historical bidding models to produce dynamic, regional cost estimates.
6. **Persistence Layer**: MongoDB holds project state, scenarios, bids, and passport metadata; S3 holds base scans, PBR rendering assets, and contractor proof images.
7. **External Connectors**: Dispatches RFP requests directly to registered contractors and synchronizes approved, completed projects back into the **Stratex Core Home Passport**.

---

## 3. Task 1: Audit of Current Design Studio

The following audit provides a structural baseline of the existing code, highlighting components that can be harvested, limitations that must be addressed, and architecture patterns that can be extended.

### 3.1. Current Capabilities
* **façade Zone Selection**: Restricts exterior customizations to thirteen pre-defined, logical zones (`roof`, `siding_main`, `siding_accent`, `veneer`, `trim`, `shutters`, `windows`, `front_door`, `garage`, etc.).
* **Guided Material Mapping**: Employs a basic validation rule where each zone only accepts specific product categories (e.g., `roof` accepts `Roofing`; `siding_main` accepts `Siding` or `Brick / Stone Veneer`).
* **Multi-Lighting PBR Rendering**: Supports three presets (`daylight`, `overcast`, `sunset`) sent to an AI renderer (`gemini-3.1-flash-image-preview`) that applies realistic texture and light maps over the facade while retaining structural constraints.
* **Curated Packages / Recommendations**: Ingests predefined design bundles (e.g., `luxury`, `modern_contrast`, `historic`, `budget`) and applies them onto the property as a standard baseline with one click.
* **Scenario comparison**: Permits homeowners to choose up to three saved scenarios and compare their estimated cost ranges and materials side-by-side.
* **Contractor Lead Dispatching**: Translates a completed design scenario into a standard `QuoteRequest` and dispatches it automatically to contractors in the system under the `Renovation` trade.

### 3.2. Reusable Components (From Existing Codebase)
The following React components and services from the current codebase are structurally sound and can be refactored into the new standards:
1. `BeforeAfter` (`frontend/src/pages/DesignStudio.js` line 20): A split-slider component that dynamically reveals before/after images. Perfect for the general `Comparison Views` and `Project Gallery` standards.
2. `Canvas` / `RenderPreview` (`frontend/src/pages/DesignStudio.js` line 323): Containers for loading and displaying rendering previews and triggering asynchronous generation states.
3. `SaveDialog` (`frontend/src/pages/DesignStudio.js` line 396): Basic form layout for naming and persisting configurations, readily adaptable to the `Version History` save mechanic.
4. `CompareDialog` (`frontend/src/pages/DesignStudio.js` line 428): Grid representation of multiple scenario selections. Refactored into the universal `Comparison Views` component.
5. `RequestQuoteScenario` (`frontend/src/pages/DesignStudio.js` line 462): Standardized multi-input popup for converting a design into an RFP. Matches the `Contractor Request` stage of the lifecycle.
6. `_build_render_prompt` (`backend/server.py` line 634): A dynamic prompt-engineering helper that translates zone selections and lighting conditions into structural AI instructions.

### 3.3. Limitations & Constraints
* **Linear Exterior Focus**: Hardcoded to exterior facade images, making it impossible to handle landscaping, floor plan expansions, or interior rooms.
* **Static, Linear Estimates**: Cost estimation is purely additive based on hardcoded arrays (e.g., `TIER_COST = { "$": [2000, 4000], ... }`). It ignores home size, localized labor variances, site preparation, and municipal permitting costs.
* **Unstructured Workspace State**: Selections are maintained in a flat React state (`selections = { zoneId: { ... } }`). This prevents complex undo/redo stacks, active draft versioning, or multi-user co-design.
* **Hardcoded Routing and Category Rules**: The backend is tightly coupled with hardcoded Mongo queries and endpoints. Ingesting new modules requires custom database migrations and code changes.

### 3.4. Future Extension Points
* **Modular Module Registry**: Creating a core module schema so any future studio (e.g., Landscaping, ADU, Kitchen) can register its distinct zones, materials, rules, and rendering instructions dynamically.
* **Interactive Spatial Annotation Canvas**: Enhancing the PBR visualizer to support multi-point spatial measurement tags, letting users tap on the image to measure linear distance, input door width, or draw pool borders.
* **Zoning & Permitting AI Agent**: Connecting the AI assistant to local GIS databases to automatically alert homeowners if an ADU, pool, or addition violates local lot setbacks or HOA height restrictions.

---

## 4. Task 2: Modular Architecture & Registry

To support independent, multi-studio design categories without application redesign, the platform uses a **Modular Registry** pattern. 

### 4.1. Core Module Framework
Each design category operates as a plug-and-play package registering with the core design engine. The interface definition below ensures that both simple finish visualizers and complex structural additions adhere to a unified communication contract.

```typescript
export interface StudioModule {
  id: string;                      // Unique identifier (e.g., 'outdoor-living')
  name: string;                    // Human-readable title
  icon: string;                    // Lucide icon name mapping
  category: 'exterior' | 'interior' | 'addition' | 'structural' | 'landscape';
  isFutureStudio: boolean;         // Flags placeholder state for future roadmaps
  zones: ZoneDefinition[];         // Design surfaces managed by this module
  rules: ValidationRule[];         // Code, HOA, and physical engineering limits
  estimationProfile: PriceProfile;  // Pricing coefficients, prep factors, and formulas
}

export interface ZoneDefinition {
  id: string;                      // e.g., 'patio_decking'
  label: string;                   // 'Patio Decking Material'
  group: string;                   // 'Structural Surfaces'
  accepts: string[];               // Accepted product tags (e.g., ['composite_decking', 'natural_wood'])
  requiresEngineering: boolean;    // Requires foundation calculations
}

export interface ValidationRule {
  id: string;
  type: 'conflict' | 'hoa' | 'code_limit';
  description: string;
  validator: (selections: any, propertyData: any) => ValidationResult;
}
```

### 4.2. Evolved Module Hierarchy
The studio is segmented into logical modules, categorizing active features and providing clean placeholder integration for upcoming studios.

| Module ID | Module Name | Category | Primary Zones / Targets | Development Phase |
| :--- | :--- | :--- | :--- | :--- |
| `exterior-finishes` | Exterior Finishes | Exterior | Siding Main, Siding Accent, Shutters, Trim, Columns | Phase 1 (Active) |
| `roofing` | Roofing | Exterior | Main Roof Planes, Valley Accents, Flashings, Gutters | Phase 1 (Active) |
| `windows` | Windows | Exterior | Window Trim, Glass Panes, Mullions, Screen Profiles | Phase 1 (Active) |
| `doors` | Doors | Exterior | Main Entry Frame, Sidelights, Back Doors, Hardware | Phase 1 (Active) |
| `garage-doors` | Garage Doors | Exterior | Garage Doors, Track Frames, Openers, Window Inserts | Phase 1 (Active) |
| `outdoor-living` | Outdoor Living | Landscape | Decks, Pergolas, Outdoor Kitchens, Screened Porches | Phase 2 |
| `hardscape` | Hardscape | Landscape | Concrete Driveways, Patios, Retaining Walls, Walkways | Phase 2 |
| `landscaping` | Landscaping | Landscape | Turf Zones, Planting Beds, Fencing, Trees, Softscape | Phase 2 |
| `home-additions` | Home Additions | Structural| Room Additions, Attached Garages, ADUs, Workshops | Phase 2 |
| `pools-water` | Pools & Water | Landscape | Pool Shell, Coping, Pool House, Spa, Water Features | Phase 2 |
| `interior-studio` | Future Interior Studio| Interior | Great Room, Master Bed, Living Areas, Hallways | Phase 3 (Future) |
| `kitchen-studio` | Future Kitchen Studio | Interior | Countertops, Cabinets, Splashbacks, Appliances, Islands | Phase 3 (Future) |
| `bathroom-studio` | Future Bathroom Studio| Interior | Tub Surround, Vanities, Wet Zones, Floor Tile, Faucets | Phase 3 (Future) |
| `whole-home` | Future Whole Home | Structural| Interior-Exterior Overhaul, Full Layout Re-planning | Phase 3 (Future) |

---

## 5. Task 3: Navigation Hierarchy

The homeowner’s journey is re-anchored around **Active Projects**, replacing settings-centric pages with a natural design and procurement hierarchy.

### 5.1. Project-First Navigation Flow

```
              [ Homeowner Dashboard ]
                         |
                         v
                [ Choose Project ]
         (Select Existing or Start New Project)
                         |
                         v
                  [ Customize ]
         (Interactive PBR Canvas & AI Assistant)
                         |
                         v
                    [ Compare ]
         (Compare Up to 3 Scenarios Side-by-Side)
                         |
                         v
                    [ Budget ]
         (Detailed Cost Breakdown & Tiers Panel)
                         |
                         v
                     [ Save ]
         (Saves Concept with Version History)
                         |
                         v
         [ Request Contractor Quotes ]
         (Submit RFP package to Local Contractors)
```

### 5.2. Core Route Architecture
* `/projects`: The entry portal. Lists active, saved, and completed projects.
* `/projects/:id/customize`: The interactive designer interface, loading the specific Module Registry configurations based on project scope.
* `/projects/:id/compare`: Side-by-side comparison screen for saved project drafts.
* `/projects/:id/budget`: Transparent cost breakdown screen showing regional calculations.
* `/projects/:id/contractors`: Bidding room showcasing live contractor responses and proposal analysis.

---

## 6. Task 4: Project Opportunity Lifecycle

Every project flows through a clear lifecycle tracked in MongoDB. The system drives action, keeping homeowners and contractors informed.

```
+---------+     +---------------+     +-----------------+     +--------------------+
| Concept | --> | Saved Concept | --> | Budget Estimate | --> | Material Selection |
+---------+     +---------------+     +-----------------+     +--------------------+
                                                                        |
+-------------------+     +---------------------+     +-----------------+
| Completed Project | <-- | Selected Contractor | <-- | Contractor Req. |
+---------+---------+     +---------------------+     +-----------------+
          |
          v
+-------------------+
| Passport Updated  |
+-------------------+
```

### Lifecycle Stage Specification

#### 1. Concept
* **Description**: The sandbox state. Homeowners experiment with materials, colors, and lighting presets on their home façade.
* **Data Payload**: Volatile draft selections in local storage.
* **Transition Trigger**: Homeowner clicks the **"Save"** button.

#### 2. Saved Concept
* **Description**: The concept is saved to the cloud under the property ID. A unique `scenario_id` and `v1` version record are created.
* **Data Payload**: `property_id`, `owner_id`, `selections` array, `base_image`, and `lighting`.
* **Transition Trigger**: Homeowner visits the **"Budget"** panel.

#### 3. Budget Estimate
* **Description**: The AI pricing engine calculates a localized estimate based on the selections, categorized by confidence levels.
* **Data Payload**: Itemized labor/material estimates, regional tax calculations, and municipal permit predictions.
* **Transition Trigger**: Homeowner selects specific manufacturer lines and locks in products.

#### 4. Material Selection
* **Description**: Selections are finalized. Brand, SKU, and exact profiles are locked into a formal "Material Specification Sheet."
* **Data Payload**: Confirmed manufacturer details, warranties, and exact color swatches.
* **Transition Trigger**: Homeowner clicks **"Request Contractor Quotes."**

#### 5. Contractor Request
* **Description**: The design package is automatically compiled into an RFP and dispatched to eligible local contractors.
* **Data Payload**: Detailed photo package, material specs, target timeline, estimated budget range, and location metadata.
* **Transition Trigger**: First contractor submits a bid proposal.

#### 6. Proposal Comparison
* **Description**: Homeowner browses incoming proposals side-by-side on a standardized comparison grid.
* **Data Payload**: List of bids, contractor company details, performance grades, exact prices, and proposed timelines.
* **Transition Trigger**: Homeowner accepts a bid.

#### 7. Selected Contractor
* **Description**: Bid accepted. Digital contracts are initialized, and the project moves to "Active Construction."
* **Data Payload**: Accepted bid ID, signed contract document, down-payment schedule, and agreed-upon start date.
* **Transition Trigger**: Contractor uploads photo proof of completion or local inspector signs off.

#### 8. Completed Project
* **Description**: Work is physically completed and verified (using computer vision to match the post-construction photo against the design scenario).
* **Data Payload**: Completed project photos, physical warranties, and final invoice records.
* **Transition Trigger**: System automated job finalization.

#### 9. Passport Updated
* **Description**: The home's "Digital Twin" and "Property Passport" are updated with the installed assets, locking in home appreciation value.
* **Data Payload**: Updated asset records, transferrable warranties, and active future maintenance schedules.

---

## 7. Task 5: AI Workflow & Reasoning Engine

The Habitat AI Assistant serves as a knowledgeable, collaborative architectural advisor. It guides design choices, explains practical tradeoffs, and maintains complete financial transparency.

### 7.1. Core Operating Principles
1. **AI Assists**: The AI is proactive but collaborative. It suggests materials based on structural architecture (e.g., suggesting standing seam metal roofs for a Modern Farmhouse façade).
2. **AI Explains**: Every design recommendation includes clear, technical reasoning (e.g., *"I recommended Eldorado Stacked Stone because it adds grounding vertical texture that complements your light horizontal Hardie siding, and features a lifetime durability rating with zero maintenance."*).
3. **AI Never Fabricates**: If localized building regulations, HOA guidelines, or structural load limits are unknown, the AI states this clearly and schedules a professional site survey rather than guessing.

### 7.2. The Estimate Confidence Framework
To maintain trust, pricing is transparently categorized across four verification tiers:

* **Verified (Green)**: 
  * **Definition**: Binding pricing from active contractor bids or manufacturer lists.
  * **UI Treatment**: Solid green border with check badge. High-level confidence (100%).
* **Estimated (Teal)**:
  * **Definition**: Confirmed local material prices and regional average labor rates calculated based on regional square footage.
  * **UI Treatment**: Teal colored text with calculator icon. Medium-high confidence (85-95%).
* **Suggested (Orange)**:
  * **Definition**: General allowances for areas where specific products aren't locked in yet, based on average regional sizing.
  * **UI Treatment**: Orange colored text with warning icon. Moderate confidence (60-80%).
* **Future capability (Gray)**:
  * **Definition**: Rough placeholders for items requiring structural engineering, onsite evaluation, or modules that are not yet active.
  * **UI Treatment**: Dotted gray border with placeholder badge. Conceptual confidence (<50%).

#### Cost Breakdown Interface Example

```
+-----------------------------------------------------------------------+
|  PROJECT BUDGET ANALYSIS: Modern Charcoal Overhaul                    |
+-----------------------------------------------------------------------+
|  [Verified]   James HardiePlank Lap Siding (Materials)       $14,200  |
|               (Direct manufacturer quote locked in)                   |
|                                                                       |
|  [Estimated]  Siding Installation Labor (Regional)           $11,800  |
|               (Calculated for Denver, CO ZIP 80202)                   |
|                                                                       |
|  [Suggested]  Dry-Stack Ledgestone Veneer Accent              $4,500  |
|               (Standard material & labor allowance)                   |
|                                                                       |
|  [Future]     Structural Column Reinforcement Plan              $2,500  |
|               (Pending engineer site-survey evaluation)               |
+-----------------------------------------------------------------------+
|  TOTAL ESTIMATED PROJECT COST:                      $30,500 - $33,000 |
+-----------------------------------------------------------------------+
```

---

## 8. Task 6: Reusable Component Inventory

To ensure consistency and ease of development, the system framework utilizes eight standardized React component specifications.

```
   +-----------------------------------------------------------------+
   |  Workspace Layout                                               |
   |  +--------------------+ +-------------------------------------+  |
   |  | [Mood Board Panel] | |  BeforeAfter Slider Visualizer      |  |
   |  |                    | |                                     |  |
   |  | - Pins             | |  +---------------+---------------+  |  |
   |  | - Colors           | |  |               |               |  |  |
   |  | - Swatches         | |  |    BEFORE     |     AFTER     |  |  |
   |  |                    | |  |   (Current)   |   (Design)    |  |  |
   |  |                    | |  |               |<====[Slider]=>|  |  |
   |  |                    | |  |               |               |  |  |
   |  |                    | |  +---------------+---------------+  |  |
   |  +--------------------+ +-------------------------------------+  |
   +-----------------------------------------------------------------+
   |  +------------------+ +------------------+ +-------------------+  |
   |  | [Material Card]  | | [Budget Panel]   | | [Version Panel]   |  |
   |  | - GAF Shingle    | | - Verified       | | - v3 (Current)    |  |
   |  | - $$ Price       | | - Estimated      | | - v2 (2 hrs ago)  |  |
   |  | - Durability Info| | - Suggested      | | - v1 (Yesterday)  |  |
   |  +------------------+ +------------------+ +-------------------+  |
   +-----------------------------------------------------------------+
```

### Component Inventory Specifications

```typescript
// 1. Project Cards
interface ProjectCardProps {
  projectId: string;
  title: string;
  status: 'concept' | 'saved' | 'estimate' | 'materials' | 'rfp' | 'active' | 'completed' | 'passport';
  lastUpdated: string;
  thumbnailUrl: string;
  estimatedCostRange: [number, number];
  percentComplete: number; // For active projects
  contractorName?: string;
}

// 2. Material Library
interface MaterialLibraryProps {
  moduleId: string;
  zoneId: string;
  selectedProductFamily?: string;
  selectedColorName?: string;
  filters: {
    priceTiers: ('$' | '$$' | '$$$' | '$$$$')[];
    durabilityRating?: string;
    tones?: ('warm' | 'cool' | 'neutral')[];
    searchQuery?: string;
  };
  onSelect: (product: Product, color: Color) => void;
}

// 3. Comparison Views
interface ComparisonGridProps {
  scenarios: SavedScenario[]; // Max 3
  metrics: ('cost' | 'durability' | 'efficiency' | 'maintenance' | 'warranty')[];
  onMakeActive: (scenarioId: string) => void;
  onSelectForQuote: (scenarioId: string) => void;
}

// 4. Budget Panels
interface BudgetPanelProps {
  items: BudgetItem[];
  zipCode: string;
  taxRate: number;
  permitAllowance: number;
}
interface BudgetItem {
  id: string;
  label: string;
  cost: number;
  confidence: 'verified' | 'estimated' | 'suggested' | 'future';
  category: 'material' | 'labor' | 'permit' | 'contingency';
  detailsUrl?: string;
}

// 5. Timeline Cards
interface TimelineCardProps {
  currentStage: number; // 1 to 9
  stages: {
    step: number;
    label: string;
    description: string;
    status: 'completed' | 'active' | 'upcoming';
    dateCompleted?: string;
  }[];
}

// 6. Project Gallery
interface ProjectGalleryProps {
  images: {
    id: string;
    url: string;
    type: 'before' | 'after' | 'drone' | 'inspect' | 'cad';
    caption: string;
    timestamp: string;
  }[];
  enableSliderView: boolean;
}

// 7. Version History
interface VersionHistoryProps {
  scenarioId: string;
  versions: {
    versionNumber: number;
    timestamp: string;
    authorName: string;
    changeSummary: string; // e.g., 'Swapped GAF shingles for Standing Seam Copper Metal Roof'
    selectionsCount: number;
  }[];
  onRestoreVersion: (versionNumber: number) => void;
}

// 8. Mood Boards
interface MoodBoardProps {
  boardId: string;
  title: string;
  items: {
    id: string;
    type: 'color' | 'image' | 'text' | 'product_swatch';
    content: string; // hex value, image url, or text
    posX: number;    // dynamic layout coordinates
    posY: number;
  }[];
  onItemMove: (itemId: string, x: number, y: number) => void;
  onItemAdd: (item: Omit<MoodBoardItem, 'id'>) => void;
}
```

---

## 9. Task 7: Future Expansion Plan & Data Schemas

To prepare Habitat Design Studio for the wide array of future projects (including ADUs, room additions, detached garages, pools, outdoor kitchens, concrete patios, etc.), the core database is engineered around a generic JSON schema structure.

Adding a new project type requires **zero database schema updates or backend code redeployments**. Instead, administrators simply post a new **Module Configuration** record.

### 9.1. Core Ingestion Schemas (JSON Schema Specification)

#### Design Scenario Schema (`design_scenarios` collection)
Holds the locked-in design configurations for any project, mapping across any modular category.
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DesignScenario",
  "type": "object",
  "required": ["id", "property_id", "owner_id", "name", "module_id", "selections"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "property_id": { "type": "string" },
    "owner_id": { "type": "string" },
    "name": { "type": "string", "minLength": 1 },
    "module_id": { "type": "string" },
    "style": { "type": "string" },
    "selections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["zone_id", "product_id", "color_name"],
        "properties": {
          "zone_id": { "type": "string" },
          "product_id": { "type": "string" },
          "color_name": { "type": "string" },
          "hex": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" },
          "custom_notes": { "type": "string" }
        }
      }
    },
    "spatial_data": {
      "type": "object",
      "properties": {
        "calculated_area_sqft": { "type": "number" },
        "linear_measurements": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "label": { "type": "string" },
              "value_inches": { "type": "number" }
            }
          }
        }
      }
    },
    "preview_url": { "type": "string", "format": "uri" },
    "lighting": { "type": "string", "enum": ["daylight", "overcast", "sunset"] },
    "est_low": { "type": "number", "minimum": 0 },
    "est_high": { "type": "number", "minimum": 0 },
    "favorite": { "type": "boolean" },
    "version": { "type": "integer", "minimum": 1 },
    "created_at": { "type": "string", "format": "date-time" }
  }
}
```

#### Module Configuration Schema (`design_modules` collection)
Defines how any future studio operates—its distinct surface areas, validation rules, and sizing coefficients.
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ModuleConfiguration",
  "type": "object",
  "required": ["id", "name", "category", "zones", "is_future_studio"],
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "category": { "type": "string", "enum": ["exterior", "interior", "landscape", "structural"] },
    "icon": { "type": "string" },
    "is_future_studio": { "type": "boolean" },
    "zones": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "accepts_categories"],
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "group": { "type": "string" },
          "accepts_categories": {
            "type": "array",
            "items": { "type": "string" }
          },
          "requires_permit": { "type": "boolean" },
          "pricing_coefficient": { "type": "number" }
        }
      }
    },
    "regulatory_checklists": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

### 9.2. Real-World Future Ingestion Example: **ADU (Accessory Dwelling Unit) Module**
To activate the complex **ADU Studio** in the UI, an administrator simply inserts the following document into the `design_modules` database:

```json
{
  "id": "adu-studio",
  "name": "Accessory Dwelling Unit (ADU) Studio",
  "category": "structural",
  "icon": "HomePlus",
  "is_future_studio": false,
  "zones": [
    {
      "id": "adu_shell",
      "label": "Foundation & Shell Framing",
      "group": "Structure",
      "accepts_categories": ["Framing & Concrete"],
      "requires_permit": true,
      "pricing_coefficient": 120.0
    },
    {
      "id": "adu_roof",
      "label": "ADU Roofing Profile",
      "group": "Exterior",
      "accepts_categories": ["Roofing"],
      "requires_permit": true,
      "pricing_coefficient": 35.0
    },
    {
      "id": "adu_power",
      "label": "Electrical Grid Hookup",
      "group": "Utilities",
      "accepts_categories": ["Electrical Systems"],
      "requires_permit": true,
      "pricing_coefficient": 2500.0
    }
  ],
  "regulatory_checklists": [
    "Verify local lot setback minimum distance (typically 5-10 feet from property lines)",
    "Review local height restriction limitations (maximum 15-24 feet for detached structures)",
    "Ensure municipal sewage utility tap capacity matches zoning requirements"
  ]
}
```

The React frontend immediately detects this new configuration, rendering the custom ADU workspace with utility tap calculations, engineering alerts, and specific material configurations.

---

## 10. Task 8: Complete UX Specification

This section details every interface screen, interaction, navigation path, and homeowner journey within the new Habitat Design Studio.

### 10.1. Screen-by-Screen Breakdown

#### Screen 1: Homeowner Projects Portal (`/projects`)
* **Primary Objective**: Allow homeowners to organize active design projects.
* **Layout**: Rich grid of active project cards, recommendations for next projects, and a "Start New Project" action panel.
* **Key Interactions**:
  * Hovering over an active Project Card displays progress status (e.g., *"Contractor Quotes Pending — 3 Received"*).
  * Clicking "Start New Project" opens a modal suggesting projects based on the property’s current Digital Twin scan data (e.g., *"Your roof is nearing its 20-year age mark. Start Roofing Refresh"*).

#### Screen 2: Interactive Design Workspace (`/projects/:id/customize`)
* **Primary Objective**: Serve as the core collaborative visualization workspace.
* **Layout**: Three-column dashboard:
  * **Left Panel**: Interactive Zone List (grouped by structure) and the collaborative **AI Assistant Chat Interface**.
  * **Center Panel**: High-definition PBR Rendering Stage with the sliding **Before/After split visualizer**, interactive lighting toggles, and measurement annotations.
  * **Right Panel**: Material Swatch and Product Grid, dynamically filtered by the active zone’s validation rules.
* **Key Interactions**:
  * Selecting a zone (e.g., Siding) updates the right panel to show only valid composite or fiber cement siding manufacturers.
  * Adjusting the slider on the PBR stage dynamically updates the visual contrast between the original house scan and the customized model.
  * Typing in the AI chat bar (e.g., *"Show me options that stand out but match colonial styles"*) prompts the assistant to automatically filter materials and highlights the recommended zones in the workspace.

#### Screen 3: The Compare Studio (`/projects/:id/compare`)
* **Primary Objective**: Compare up to three design configurations side-by-side.
* **Layout**: Standard three-column comparison grid showcasing high-res thumbnail cards of the design scenarios.
* **Key Interactions**:
  * **Interactive Metrics Checklist**: Hovering over details reveals aesthetic contrast ratings, maintenance schedules, manufacturer warranties, and projected ROI percentages.
  * **"Set Active Scenario" Action**: Clicking locks in the selections and updates the primary project draft.

#### Screen 4: Dynamic Budget Dashboard (`/projects/:id/budget`)
* **Primary Objective**: Provide transparent cost estimations and breakdown controls.
* **Layout**: Double-panel dashboard:
  * **Left Side**: Scrollable cost breakdown with clear labels showing verification confidence (**Verified**, **Estimated**, **Suggested**, **Future**).
  * **Right Side**: Zip-code labor index tuning panel, permitting cost estimator, and active contingency sliders.
* **Key Interactions**:
  * Clicking a **Verified** item displays the associated manufacturer price sheet.
  * Adjusting the **Contingency Slider** updates the Suggested budget ranges in real-time, helping homeowners plan for hidden site-prep costs.

#### Screen 5: Proposal Comparison Room (`/projects/:id/contractors`)
* **Primary Objective**: Review, contrast, and accept contractor bids.
* **Layout**: Side-by-side bid analysis deck.
* **Key Interactions**:
  * **Performance Grades**: Hovering over a contractor's grade displays historical metrics (on-time rate, verified reviews, rating).
  * **Accept Bid Trigger**: Opens an escrow scheduling dialog to lock in the project.

#### Screen 6: The Digital Twin & Home Passport (`/properties/:pid/passport`)
* **Primary Objective**: View historical home projects and transferable asset records.
* **Layout**: Interactive visual history timeline of completed renovations, featuring transferable warranty documents and dynamic maintenance indicators.
* **Key Interactions**:
  * Clicking a historical project (e.g., *"Roofing Overhaul 2026"*) displays the verified product line, SKU numbers, warranty documents, and the contractor of record.

---

### 10.2. Major User Journeys

#### Journey A: Siding & Window Overhaul (Phase 1 active module)
* **Goal**: Transform a weathered exterior facade into a "Modern Farmhouse" style.
* **Step-by-Step Experience**:
  1. **Discovery**: Homeowner logs in and clicks the recommended project: *"Exterior Façade Upgrade."*
  2. **Customization**:
     * Homeowner taps the main siding zone and selects *James Hardie Board & Batten* in *Iron Gray*.
     * The PBR stage displays the change pending.
     * The homeowner opens the AI Chat panel: *"Suggest a complementary trim and window package."*
     * The AI analyzes the design and recommends *Azek PVC Trim* in *Bright White* and *Andersen 400 Series Windows* with *Black Frames* to create a high-contrast farmhouse aesthetic.
     * The homeowner clicks **"Render Realistic Preview."** The PBR workspace applies texture maps and lighting.
  3. **comparison**: Homeowner saves this option as *v1: Modern Farmhouse*, then drafts *v2: Classic Colonial* with white brick and black shutters. They compare them side-by-side to review aesthetic and cost differences.
  4. **Budgeting**: The homeowner selects the *Modern Farmhouse* concept and moves to the Budget screen. They review localized labor averages and adjust the permitting allowances for Denver, CO.
  5. **Procurement**: Homeowner locks in selections and clicks **"Request Contractor Quotes."** System automatically dispatches the detailed design RFP.
  6. **bidding**: Within 48 hours, three proposals arrive. The homeowner reviews performance grades and accepts *Apex Exterior Renovations’* verified bid.
  7. **Construction & Passport Update**: Apex completes the installation. The contractor uploads completion photos. The system validates the final facade and automatically updates the homeowner's **Property Passport** with the warranty records.

#### Journey B: Detached Accessory Dwelling Unit (Phase 2 future module)
* **Goal**: Build a detached 600 sqft rental ADU in the backyard, illustrating how the flexible schema parses zoning limits.
* **Step-by-Step Experience**:
  1. **Discovery**: Homeowner selects *"Add Detached Structure"* from their Projects Portal.
  2. **Customization & AI Zoning Guardrails**:
     * Homeowner clicks the *ADU Shell* zone and draws a 20ft x 30ft rectangle on their property map.
     * The AI assistant automatically evaluates the design against local zoning limits: *"Your property in Denver, CO ZIP 80202 allows a maximum ADU footprint of 650 sqft. Your draft footprint is 600 sqft (Pass). However, please note: detached structures must maintain a minimum 5-foot setback from the rear property line."*
     * The homeowner adjusts the placement on the map.
     * The AI updates: *"Setbacks verified (Pass). Detached structures in this zone are capped at 1.5 stories or 18 feet. What roofing profile would you like to match your primary residence?"*
     * Homeowner selects *GAF Timberline HDZ Architectural Shingles* in *Charcoal* to match the primary home roof.
  3. **Dynamic Estimating**:
     * The Budget panel displays:
       * **Estimated**: ADU Shell Foundation & Framing ($72,000 based on standard regional framing averages of $120/sqft).
       * **Suggested**: Municipal Sewers Tap Fee ($5,000 standard utility hookup allowance).
       * **Future capability**: Structural Soil Stability Evaluation ($2,500 pending onsite geotechnical review).
  4. **Procurement**: Homeowner submits the ADU RFP package. Contractors submit bids. Homeowner accepts the proposal from *BuildWright ADU Specialist*, starting the construction process.

---

## 11. Recommendations for Directive H-002

With the modular architecture and data schemas finalized, we recommend the following roadmap for Phase 1 implementation under Directive H-002:

### Phase 1 Priority Implementation Map

```
Sprint 1: Schema Ingestion  -->  Sprint 2: Assistant API   -->  Sprint 3: Workspace UI
- Deploy design_modules JSON     - Implement context-aware      - Refactor DesignStudio.js
- Seed exterior active modules     Gemini prompts in server.py    with dynamic Zone panels
- Define pricing coefficients    - Connect localized labor      - Implement unified cost Tiers
```

1. **Sprint 1: Database Ingestion & Schema Deployment**
   * **Deliverable**: Deploy the `design_modules` and `design_scenarios` JSON schemas in MongoDB.
   * **Task**: Migrate legacy hardcoded zones and recommendation structures in `backend/design.py` to the dynamic `ModuleConfiguration` format. Seed the active Phase 1 modules (Exterior, Roofing, Windows, Doors, Garage Doors) into the database.
2. **Sprint 2: Collaborative AI Assistant & Dynamic Estimator API**
   * **Deliverable**: Deploy the backend reasoning and localization pricing engines.
   * **Task**: Implement prompt builders that inject local zoning codes and product specifications directly into the LLM chat assistant. Connect a regional pricing matrix API to output itemized estimate ranges across the four verification tiers.
3. **Sprint 3: Unified Workspace Workspace UI**
   * **Deliverable**: Refactor the frontend interface.
   * **Task**: Redesign `frontend/src/pages/DesignStudio.js` to dynamically load the active module's zones and material libraries. Replace static cost labels with the interactive, color-coded **Budget Confidence Tiers** component, delivering a cohesive, project-first design experience.
