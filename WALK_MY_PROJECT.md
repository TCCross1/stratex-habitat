# WALK MY PROJECT IMMERSIVE VIEWS & SLIDERS
## DRONE ORBITS, FIRST-PERSON WALKING, AR PORTALS, & BEFORE/AFTER COMPARISONS
**Version:** 2.0  
**Classification:** HABITAT-CONFIDENTIAL

This specification outlines the technical design, interaction paradigms, and rendering modes for the "Walk My Project" immersive visualization and comparison systems in Habitat Design Studio 2.0.

---

## 1. THE "WALK MY PROJECT" IMMERSIVE ENGAGEMENT ENGINE

To build high-confidence operational readiness, Design Studio 2.0 shifts visualization from static images into active spatial immersion. Homeowners can experience their design concepts at 1:1 scale under various lighting, seasonal, and perspective states before breaking ground.

```
                  +----------------------------------------------+
                  |            IMMERSIVE VIEWPORT CORE           |
                  +----------------------------------------------+
                  |  [ Drone Orbit ]      [ 1st-Person Walk ]    |
                  |  - High-res orbital   - Eye-level WASD       |
                  |    flyovers.          - 5.5ft collision cam. |
                  |                                              |
                  |  [ 1:1 Mobile AR ]    [ Seasonal & Light ]   |
                  |  - On-site camera     - Spring/Winter snow.  |
                  |    spatial anchors.   - Dusk lighting shadow.|
                  +----------------------------------------------+
```

---

## 2. THE FOUR IMMERSIVE RENDERING MODES

### Mode A: Drone / Flyover View
- **Description**: A birds-eye, dynamic orbital perspective of the home property's Digital Twin.
- **Camera Controls**: Autopilot 360-degree orbit with manual tilt/zoom overrides.
- **Key Use Case**: Visualizing large-footprint landscape overhauls, pool placements, roof replacements, detached garages, or solar panel layouts.
- **Asset Rendering**: Loads the complete low-poly terrain mesh and applies high-resolution PBR maps onto structures.

### Mode B: First-Person Walking Simulator
- **Description**: An eye-level, terrain-hugging walk-through of the property.
- **Physics & Collisions**: Camera height locked to a natural human eye-level of 5.5 feet. Implements terrain slopes and solid structure collision boundaries (prevents walking through walls or falling off unrailed decks).
- **Navigation Scheme**: Touchscreen joystick or WASD/Arrow keys for fluid motion.
- **Key Use Case**: Walking onto a newly designed deck, stepping inside an ADU, or standing under a pergola to review real-world volume and sightlines.

### Mode C: 1:1 Scale Augmented Reality (AR) Portal
- **Description**: Projects designed elements directly onto the physical environment using mobile camera passes and WebXR spatial anchors.
- **Tracking Mechanics**: Implements plane-detection algorithms to map physical ground surfaces. Anchors virtual assets (e.g., a new fence line or outdoor kitchen) onto physical coordinates.
- **Key Use Case**: Standing in the physical backyard, looking through a mobile device, and seeing the exact scale, placement, and shadows of a proposed deck or pool.

### Mode D: Seasonal & Lighting Simulator
- **Description**: Realistic environment adjustments based on localized geographic coordinates, date/time inputs, and seasonal presets.
- **Lighting Presets**:
  - **Sunrise/Morning**: Soft, warm light cast from the east with elongated morning shadows.
  - **Midday**: High-intensity, neutral-white overhead lighting with minimal sharp shadows.
  - **Dusk/Golden Hour**: Warm amber lighting cast from the west, creating rich reflections and deep shadows.
  - **Night/Moonlight**: Dark skybox with low-intensity ambient light, activating designed low-voltage **Exterior Lighting** fixtures.
- **Seasonal Presets**:
  - **Spring/Summer**: Lush green turf shaders, full plant foliage, active pool water reflections.
  - **Autumn**: Amber-toned deciduous tree foliage, ground leaf overlays.
  - **Winter**: Snow cap shaders layered over structures, bare branch models, frost glass shaders on windows.

---

## 3. BEFORE/AFTER COMPARISON SPLIT SLIDER

The interactive split slider allows homeowners to dynamically swipe between verified existing conditions and proposed design concepts.

```
                      +-----------------------------------+
                      |      SPLIT-SLIDER CORE UTILITY    |
                      +-----------------------------------+
                      |                 |                 |
                      |                 |                 |
                      |                 |                 |
                      |     BEFORE      |      AFTER      |
                      |    (Existing)   |    (Proposed)   |
                      |                 |                 |
                      |                 |<====[Handle]===>|
                      |                 |                 |
                      +-----------------+-----------------+
```

### UX & UI Interaction
- **Center Handle**: Dragging the vertical bar left-to-right adjusts the clip-path coordinates of the overlaying "After" rendering canvas over the underlying "Before" canvas.
- **Keyboard Override**: Left and Right arrow keys move the slider incrementally for accessible fine-tuning.
- **Responsive Adaptability**: On mobile devices, the handle expands to support touch swipes.

---

## 4. MULTI-SCENARIO SIDE-BY-SIDE COMPARISON MATRIX

Homeowners can compare up to **Three Saved Scenarios** on a synced grid, making it easy to contrast aesthetic styles, warranties, maintenance needs, and financial commitments.

```
+-----------------------------------------------------------------------------+
|  COMPARE SANDBOX: Backyard Transformations                                  |
+-----------------------------------------------------------------------------+
|  METRICS          |  SCENARIO 1: Wood Deck   |  SCENARIO 2: Composite Deck  |
+-------------------+--------------------------+------------------------------+
|  Visual Concept   |  [3D Render Wood]        |  [3D Render Composite]       |
|                   |                          |                              |
|  Material Class   |  Pressure-Treated Pine   |  Trex Transcend              |
|                   |                          |                              |
|  Total Budget     |  $6,800 [Estimated]      |  $9,800 [Verified]           |
|                   |                          |                              |
|  Warranty Term    |  1 Year Labor            |  25 Years Manufacturer       |
|                   |                          |                              |
|  10-Yr Maint. Cost|  $3,200 (Sealing/Stain)  |  $0.00 (Wash Only)           |
|                   |                          |                              |
|  Est. Timeline    |  3-5 Days                |  4-6 Days                    |
+-------------------+--------------------------+------------------------------+
|  ACTIONS          |  [Set Active Scenario]   |  [Set Active Scenario]       |
+-----------------------------------------------------------------------------+
```

### Synced Viewport Interaction
- **Camera Coupling**: Orbiting or zooming the camera inside one comparison card applies identical transformation matrices to the other cards, ensuring the homeowner views the design scenarios from identical perspectives.
- **Active Scenario Lock**: Clicking **"Set Active Scenario"** updates the master design draft and navigates the homeowner back to the customization workspace.
