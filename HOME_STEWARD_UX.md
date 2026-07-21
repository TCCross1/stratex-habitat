# CENTCOM DIRECTIVE H-011: HOME STEWARD USER EXPERIENCE
## INTEGRATED INTERFACE SURFACES, TWIN COORDINATION & MOTION GUIDELINES
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Core Philosophy

The Home Steward AI is designed as an integrated Habitat surface, **not a generic, floating chat bubble** that drifts over content. It is a native, layout-aware layer that resides within the existing column grids of the Stratex Design System (SDS).

The primary visual and spatial core of the platform is the **3D Digital Twin**. The Steward acts as the vocal and text guide for this digital twin, highlighting systems, outlining timeline events, rotating the camera focus, and displaying relevant documents directly around the 3D model.

---

## 2. Supported Presentation Modes

The Steward adapts its visual presence based on the active user surface, maintaining consistency across seven operational layouts:

```
+---------------------------------------------------------------------------------+
|                    HABITAT ADAPTIVE WORKSPACE SHELL                             |
+---------------------------------------------------------------------------------+
|  [Left Nav]  |                                                   |  [RIGHT RAIL] |
|  - Dash      |              CENTRAL 3D DIGITAL TWIN              |  - STEWARD    |
|  - Design    |                OF THE PHYSICAL HOME               |    INSIGHT    |
|  - Docs      |                                                   |    DRAWER     |
|  - Tasks     |                                                   |    (Dynamic)  |
+--------------+---------------------------------------------------+---------------+
|                             [SEDIMENTARY TIMELINE]                              |
+---------------------------------------------------------------------------------+
```

### 2.1. Home Command Center Insight Rail
* **Layout:** Resides in the right-hand panel of the main dashboard.
* **Behavior:** Displays proactive seasonal tips, immediate maintenance priorities, and real-time environment metrics. Clicking an insight card rotates the central 3D Twin to highlight the affected system.

### 2.2. Contextual Assistant within Design Studio
* **Layout:** Integrated as a supportive sidebar panel next to the Material Library drawer.
* **Behavior:** Assists the homeowner with material selections, estimates costs in real time, and identifies package dependencies as materials are swapped on the 3D façade.

### 2.3. Maintenance Coaching Panel
* **Layout:** A side-drawer that slides out over the active checklist view.
* **Behavior:** Displays step-by-step DIY instructions, links product manuals, and provides "how-to" videos for the selected maintenance task.

### 2.4. Document Search Experience
* **Layout:** Integrated directly into the search bar of the Document Vault.
* **Behavior:** Acts as a semantic assistant, allowing the user to search using natural language (e.g., *"Show me the deck permit"*) and displaying matching file cards next to the query.

### 2.5. Project Comparison Guide
* **Layout:** A split-screen, tabular overlay displayed during bid reviews.
* **Behavior:** Highlights variations in materials, labor fees, and warranties across multiple proposals, using plain language to explain trade-offs.

### 2.6. Mobile Conversational Interface
* **Layout:** A bottom-sheet panel that slides up to occupy the lower 50% of the viewport.
* **Behavior:** Optimized for portrait touch targets (min 44px) and quick-reply chips.

### 2.7. Voice-Ready Future Interface
* **Layout:** Visualized as a gentle, ambient neon-teal wave pulsing along the base of the left navigation rail.
* **Behavior:** Synchronizes with voice dictation, adapting its pulse rate to match natural human speech patterns.

---

## 3. Dynamic Coordination with the 3D Digital Twin

The Steward coordinates with the WebGL 3D Digital Twin, bringing the home's systems to life visually as conversations unfold:

```
+---------------------------------------------------------------------------------+
|                          3D TWIN HIGHLIGHTING EXAMPLES                          |
+---------------------------------------------------------------------------------+
|  "Your heat pump filter..." --->  ( 3D Twin rotates. HVAC layer glows teal )   |
|                                                                                 |
|  "Where is the leak?"       --->  ( Façade fades to 40%. Piping glows amber )   |
|                                                                                 |
|  "Show me the deck permit"  --->  ( Camera zooms to Deck. Permit card hovers)   |
+---------------------------------------------------------------------------------+
```

### 3.1. Camera Focusing & Viewport Control
* When discussing a specific system (e.g., roof sheathing, sump pump, foundation), the Steward issues camera movement vectors (FOV, Pitch, Yaw) to automatically center the target asset in the user's viewport.

### 3.2. Layer Transparencies & Glows
* **Mechanical Focus:** Fades the exterior cladding to 40% transparency and highlights plumbing, HVAC ducts, or electrical runs in glowing neon teal (#14F1D9).
* **Attention Flags:** Highlights systems requiring immediate care in a soft, steady, warm amber-gold glow (#FF6B00). It avoids blinking lights, maintaining a calm visual tone.

### 3.3. Document and Event Hover Pins
* Floating document tags or warranty shields hover over their corresponding physical components on the 3D Twin, allowing the homeowner to click and open documents directly from the model.
* For timeline events, the system draws connecting lines down from the physical 3D asset into the sedimentary timeline layers below, illustrating the home's history.
