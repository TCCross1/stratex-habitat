====================================================================
CENTCOM DIRECTIVE 014: 3D VISUAL STANDARDS
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# 3D VISUAL STANDARDS: DIGITAL TWIN

This document defines the 3D visual standards, lighting models, camera behaviors, and real-time telemetry overlays for the Stratex Digital Twin. It serves as the exact playbook for Three.js, React Three Fiber (R3F), Spline, and custom shader implementations.

---

## 1. THE DIGITAL TWIN ARCHETYPE

The Digital Twin is the central stage of the Habitat interface. It is **the house as the interface**. It must never look like a generic architectural sketch or a cartoonish game asset. 

*   **Visual Philosophy:** High-contrast, glowing technical wireframe overlaying dark graphite surfaces. 
*   **The Blueprint Vibe:** Constructed of clean geometric mesh boundaries and glowing lines, utilizing our primary neon teal (`#14F1D9`) and highlight orange (`#FF6B00`) palette.
*   **Placeholder Fallback:** If a real-time webGL rendering context is not supported, the system must render a high-definition, glowing blueprint image (using our designated orange/teal thermal gradient filters applied via CSS overlays: `sepia`, `hue-rotate`, `mix-blend-mode`).

---

## 2. CAMERA BEHAVIOR & INTERACTIVE CONTROLS

The operator orbits around the physical asset to inspect specific telemetry points.

```
       +-----------------------------------------------------------+
       |                  CAMERA INTERACTION SYSTEM                |
       +-----------------------------------------------------------+
       |   Orbit Camera (Default)                                  |
       |     - Mouse Left Click + Drag: Orbit rotation              |
       |     - Mouse Right Click + Drag: Pan translation           |
       |     - Scroll Wheel: Zoom focal depth                       |
       |                                                           |
       |   Camera Constraints                                      |
       |     - Min Orbit Distance: 5m (Prevents clip through walls) |
       |     - Max Orbit Distance: 50m (Prevents losing model)     |
       |     - Polar Angle Bounds: Min 10deg, Max 85deg              |
       +-----------------------------------------------------------+
```

### 2.1 Standard Views & Presets
Quick-toggle buttons in the 3D Twin Controls Panel must snap the camera to official vectors:
*   **Isometic View (Default):** Camera set at `[X: 15, Y: 15, Z: 15]` looking directly at the model center `[0, 0, 0]`.
*   **Roof Plan (Top-down):** Camera set at `[X: 0, Y: 25, Z: 0]` looking straight down.
*   **Slab/Foundation (Bottom-up):** Camera set at `[X: 0, Y: -15, Z: 0]`.
*   **Interactive Reset (⌘R):** Instantly sweeps the camera back to isometric view using an Ease-Out transition lasting `400ms`.

---

## 3. LIGHTING & SURFACE MODELS

To maintain an "investor-grade control center" look, avoid traditional flat ambient sunlight.

*   **Ambient Light:** Minimal intensity (`0.15`). Colored in dark graphite-slate (`#1A1A1E`).
*   **Directional Spotlights:** Two highly focused spotlights positioned diagonally at `[10, 20, 10]` and `[-10, 20, -10]` (Intensity `0.8`, pure white `#FFFFFF`). Creates stark, high-contrast structural highlights and sharp shadow casting.
*   **The Emissive Shader (Glow):** All active wires, conduits, and sensor points must utilize custom emissive shaders with an exposure value that bleeds a soft glowing halo (`rgba(20, 241, 217, 0.25)`) into the surrounding dark canvas.

---

## 4. FUNCTIONAL METADATA OVERLAYS

Overlays render complex sensor data directly onto the 3D mesh of the home. Operators toggle these layers using the floating controls deck.

### 4.1 Thermal Overlay
*   **Vibe:** Visualizes insulation leaks and heat escape.
*   **Styling:** Shaders replace the technical wireframe with a color gradient representing heat signatures. 
    *   *Warm/Leak Areas:* Red (`#FF3333`) and Orange (`#FF6B00`).
    *   *Normal Insulated Areas:* Deep Slate Blue (`#111113`).
    *   *Cold/Optimal Areas:* Deep Teal (`#044B45`).

### 4.2 Property DNA Overlay
*   **Vibe:** Displays the material composition of physical layers.
*   **Styling:** Renders transparent structural cross-sections (e.g. slicing open the exterior siding to expose insulation studs and vapor barriers). Material details are flagged with high-contrast text label points.

### 4.3 Evidence Overlays
*   **Vibe:** Pins real-world proof (photos, contractor reports, receipts) onto exact spatial locations of the home model.
*   **Styling:** A small glowing node icon (e.g., `<Camera />` inside a magenta circle `#D946EF`) is pinned to the exact X, Y, Z coordinate of the property (such as the upper corner of the roof slope where a leak was photographed). Clicking the icon expands an interactive Evidence Card overlay.

### 4.4 Knowledge Graph Overlays
*   **Vibe:** Links physical assets to their logical entity network.
*   **Styling:** Projects glowing network lines from specific physical nodes (such as the HVAC condenser unit) directly outward to float in front of the model, connecting it to the smart thermostat node and utility meter entities.

---

## 5. SELECTION & SECTOR HIGHLIGHTING

When an operator clicks a component (e.g., Roof - North Slope):
1.  **Component Highlighting:** The selected mesh segment's emissive value increases instantly. The border edge lights up in primary neon teal (`#14F1D9`).
2.  **Dimming Unselected Assets:** All other mesh segments of the digital twin dim down by **60% opacity** to draw absolute focus to the selected asset.
3.  **Active Focus Sweep:** The camera smoothly pans to center the clicked component in the exact center of the 3D viewport.
