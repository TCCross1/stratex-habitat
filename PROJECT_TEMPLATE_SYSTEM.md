# PROJECT TEMPLATE SYSTEM & SPATIAL INTERACTIONS
## STARTER TEMPLATES, DRAG-AND-PLACE INTERACTIONS, & COLLISION DETECTION
**Version:** 2.0  
**Classification:** HABITAT-CONFIDENTIAL

This specification defines the interactive template engine and 3D spatial placement systems that govern how homeowners select, position, and snap elements within the Habitat Design Studio 2.0.

---

## 1. SMARTS-START PROJECT TEMPLATES

To eliminate the blank canvas effect, Design Studio 2.0 features **Smart-Start Templates** that pre-configure combinations of materials, colors, and layouts across the 32 catalog projects.

```
       +---------------------------------------------------------+
       |                  SMART-START ENGINE FLOW                |
       +---------------------------------------------------------+
       |  1. Homeowner selects a project category (e.g. Deck)   |
       |  2. System suggests 3-4 architectural templates        |
       |  3. Selection loads full material & boundary preset     |
       |  4. Workspace rendering updates instantly               |
       +---------------------------------------------------------+
```

### Core Architecture-Matching Templates

| Template Name | Aesthetic Target | Siding Theme | Roofing Style | Accent Colors | Best Fit Catalog Projects |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Modern Contrast** | High-contrast, clean lines | Arctic White Lap | Matte Black Metal | Cyber Obsidian | ADUs, Garages, Decks, Pergolas, Siding, Solar |
| **Nordic Minimalist**| Monochromatic, earthy | Iron Gray Vertical | Slate Gray Shingle | Cool Ash Timber | Room Additions, Porches, Walkways, Patios, Pools |
| **Classic Heritage** | Timeless, traditional | Warm Cream Lap | Weathered Wood | Forest Green/Navy | Screened Porches, Gazebos, Sidewalks, Windows/Doors |
| **Solar Off-Grid** | Eco-friendly, functional| Natural Cedar Lap | Obsidian Blue PV | Matte Bronze | Solar Systems, EV Chargers, Attached/Detached Garages |

---

## 2. DRAG-AND-PLACE SPATIAL CO-ORDINATE SYSTEM

For projects requiring layout positioning (e.g., ADUs, detached garages, pools, gazebos, pergolas, fences), Habitat employs an interactive 3D orthographic and perspective grid mapped directly over the homeowner's property parcel coordinates.

```
                      +------------------------------------------+
                      |       3D GRID RESOLUTION SCHEMATIC       |
                      +------------------------------------------+
                      |                                          |
                      |   (Y-Axis: Altitude/Elevation)           |
                      |        ^                                 |
                      |        |                                 |
                      |        |  [Target Anchor Point]          |
                      |        |  /                              |
                      |        +----+-------------> (X-Axis: East/West)
                      |       /                                  |
                      |      /                                   |
                      |     v                                    |
                      |   (Z-Axis: North/South)                  |
                      +------------------------------------------+
```

### Grid Matrix & Anchoring
- **Local Origin (0,0,0)**: Mapped to the geometric center of the primary residential structure's foundation.
- **Orientation Alignment**: North-aligned with the property's municipal GIS survey boundaries.
- **Grid Subdivisions**: 6-inch increments (0.5 feet) for high placement precision without CAD-level complexity.

---

## 3. SPATIAL INTERACTION GESTURES & CONTROLS

The 3D Canvas implements intuitive, fluid mouse and gesture controls, maintaining the center-stage role of the property's Digital Twin.

### Desktop Controls
- **Left-Click + Drag**: Translate/Move selected item across the horizontal (X, Z) placement grid.
- **Right-Click + Drag**: Orbit camera around the workspace focus.
- **Scroll Wheel**: Zoom in/out toward the mouse cursor location.
- **R Key**: Rotate selected item clockwise in 15-degree increments.
- **Shift + Drag**: Disable grid-snap for freeform fine-tuning.

### Touch Controls (Tablet & Mobile)
- **Single Finger Drag**: Translate selected item across the yard grid.
- **Two Finger Pinch/Spread**: Zoom in/out of the workspace view.
- **Two Finger Rotate**: Rotate the active camera viewpoint or rotate selected object when in "Object Modify" mode.

---

## 4. HOVER HIGHLIGHTS, BORDERS, & PLACEMENT MARKERS

The visual state of the selected object changes dynamically in real-time to represent placement safety, alignment, and collisions using high-contrast Stratex tokens.

```
+-----------------------------------------------------------------------------+
|                          PLACEMENT RENDERING ENVELOPE                       |
+-----------------------------------------------------------------------------+
|                                                                             |
|   [ VALID PLACEMENT ]                      [ COLLISION / SETBACK VIOLATION ]|
|   +-----------------------+                +-----------------------+        |
|   |                       |                |     ! COLLISION !     |        |
|   |      (Object Outline) |                |     (Object Outline)  |        |
|   |                       |                |                       |        |
|   +-----------------------+                +-----------------------+        |
|   Border: Solid Electric Blue              Border: Pulsing Critical Red     |
|   Shadow: Glowing Green Glow               Shadow: Dense Red Shadow         |
|   Cursor: Snap Anchor Pin                  Cursor: Warning Anchor Pin       |
+-----------------------------------------------------------------------------+
```

### Visual State Rules
- **Hover State**: Selecting an object triggers an Electric Blue (`#00F0FF`) solid border and bounding box around the asset's structural footprint.
- **Valid Placement State**: If the location violates no rules, a thin Neon Green (`#39FF14`) outer shadow is applied beneath the boundary wireframe.
- **Invalid Placement State**: If the location triggers a collision, setback violation, or height hazard, the border and bounding box pulse in Warning Amber (`#FF9E00`) or Critical Red (`#FF0055`). A helper bubble appears next to the cursor with the rule description.

---

## 5. REAL-TIME COLLISION DETECTOR & BOUNDS CHECKER

To ensure engineering feasibility, the 3D workspace runs a continuous spatial intersection algorithm using bounding volume hierarchies (AABB/OBB).

```
                      +------------------------------------+
                      |    COLLISION DETECTION ALGORITHM   |
                      +------------------------------------+
                      |                                    |
                      |  [ ADU Footprint ]                 |
                      |   +-----------------+              |
                      |   |                 |              |
                      |   |    COLLISION!   |              |
                      |   |   +-------------+----+         |
                      |   +---|-------------+    |         |
                      |       |   [ Pool Shell ] |         |
                      |       |                  |         |
                      |       +------------------+         |
                      +------------------------------------+
```

### Dynamic Safety Checklists

#### Setback Intersections
The boundary checking engine pulls lot dimensions from the Property Passport and evaluates placements against municipal codes:
- **Rear Yard Setbacks**: Must not place accessory structures within 5 feet of the rear property boundary line.
- **Side Yard Setbacks**: Detached buildings must remain at least 5 feet from side property lines.

#### Structure-on-Structure Collisions
The workspace blocks placing overlapping features:
- **Pool Over Deck**: Flagged as structural conflict unless the deck is designated as a perimeter wrap.
- **Structure Over Utility Lines**: Flagged as a critical utility easement collision (blocking placement of ADUs or deep pool excavations directly over water or power main line pathways).

#### Lot Coverage Analysis
The system monitors total impervious surface area (buildings, concrete pads, driveways, pools):
- If the current design exceeds the maximum allowed local lot coverage (e.g., 40% in Denver 80202), the AI assistant flags the issue and suggests reducing driveway expansions or choosing permeable paver walks.
