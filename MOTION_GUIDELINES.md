====================================================================
CENTCOM DIRECTIVE 014: MOTION GUIDELINES
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# MOTION GUIDELINES

This document governs the motion behavior, animation curves, load behaviors, transitions, and immersive interactive graphics of all Stratex user interfaces. 

---

## 1. MOTION PHILOSOPHY

Motion in Stratex is never playful, bouncy, or decorative. Every animation must exist to **reduce cognitive load, demonstrate structural relationships, or highlight live telemetry changes**.

*   **No Playful Bounce:** Avoid standard consumer spring dynamics (`bounce`, `elastic`).
*   **Precision Speed:** Micro-interactions must complete in under **150ms** so the UI feels incredibly responsive.
*   **High Performance:** Avoid animating expensive layout properties (`width`, `height`, `top`, `left`). Instead, leverage GPU-accelerated CSS properties (`transform`, `opacity`).

---

## 2. STANDARD ANIMATION BEHAVIORS

### 2.1 UI Component Transitions
*   **Collapsible Sidebars (e.g. Navigation wide state):**
    *   *Duration:* `250ms` (Ease-Out / Responsive).
    *   *Action:* Translate along the X-axis while fading opacity.
*   **Dropdown Menu / Context Popovers:**
    *   *Duration:* `80ms` (Instant).
    *   *Action:* Fade and scale up slightly from `95%` to `100%` centered on the origin.
*   **Modal Overlay Dims:**
    *   *Duration:* `150ms` (Ease-In-Out).
    *   *Action:* Blur background (`backdrop-blur-sm`) and fade background color.

### 2.2 Skeletons & Loading States
When assets are loading from remote servers, do not show blank pages. Use high-contrast layout skeletons.

```
+-----------------------------------------------------------+
|                   SKELETON COMPONENT SPEC                 |
+-----------------------------------------------------------+
|  [||||||||||||| Shimmering Charcoal Gray Layer ||||||||||] |
|                                                           |
|  - Background: #1A1A1E                                    |
|  - Shimmer Wave: Linear gradient                          |
|    from #1A1A1E via #27272A to #1A1A1E                    |
|  - Animation: CSS Infinite loop translate-X (1.5s duration) |
+-----------------------------------------------------------+
```

*   **Loading Spinners:**
    *   Spinners are prohibited on full pages. Instead, use a linear, horizontal Progress Loader (`h-0.5` or `h-1`) at the extreme top of the page frame.
    *   For inline buttons, use a clean 360-degree rotating, dashed ring `<Loader2 className="animate-spin" />` in primary teal (`#14F1D9`).

### 2.3 Hover, Selection & Hover States
Interactive components must provide immediate visual feedback.

*   **Hover State:**
    *   Snappy border fade-in (`border-border_active`) + slight background glow.
*   **Selection State:**
    *   Immediate border transition to Primary Teal (`#14F1D9`) or Highlight Orange (`#FF6B00`).
    *   Active glow shadow applies (`box-shadow: 0 0 12px rgba(20, 241, 217, 0.35)`).

---

## 3. ECOSYSTEM DOMAIN ANIMATIONS

### 3.1 Timeline Animation
The Living Timeline registers property histories in real-time.
*   **Timeline Dot Pulsing:**
    *   Critical or active future events display a repeating concentric pulse effect.
    *   *CSS:* `@keyframes pulse { 0% { transform: scale(0.9); opacity: 0.8; } 100% { transform: scale(2.0); opacity: 0; } }`
*   **Chronological Expansion:**
    *   When expanding past history records, rows cascade downward sequentially using a staggering delay (`50ms` interval per card).

### 3.2 Knowledge Graph Animation
The node-link network must animate beautifully when navigated.
*   **Node Expansion:**
    *   Double-clicking an entity expands connected child nodes outward radially.
    *   *Curve:* Ease-Out (`cubic-bezier(0.16, 1, 0.3, 1)`).
*   **Path Flow (Energy / Signal Flow):**
    *   Links represent active flows. Show tiny glowing dashes traversing the SVG path in the direction of the flow (simulated energy grid).
    *   *CSS:* `stroke-dasharray: 4, 12; animation: dash 10s linear infinite;`

### 3.3 Digital Twin Animation
The 3D model coordinates are alive with spatial overlays.
*   **Pulse Beacons (Anomaly alerts):**
    *   Pinpoints of localized system failures must emit a flashing red concentric radar circle overlaying the 3D model.
*   **Thermal Layer Transition:**
    *   When switching to Thermal overlay, the model color scheme fades from technical wireframe into a colored, emissive thermal representation. This color transition must take exactly `400ms` using a smooth Ease-In-Out transition.

---

## 4. DESIGN CELEBRATIONS

Stratex does not use confetti, floating balloons, or whimsical celebrations. Our products celebrate engineering victories, regulatory sign-offs, and compliance milestones with high-fidelity, industrial-grade visuals.

### 4.1 "System Synchronized" Celebration
When a homeowner completes a major energy transition upgrade or a contractor uploads a verified inspection:
1.  **Chime / Sound:** A high-frequency, clean sine-wave chime plays (optional, muted by default).
2.  **Visual Sweep:** A neon teal horizontal radar beam sweeps down the entire viewport (taking `1.2s`).
3.  **Audit Seal:** A glowing cryptographic badge `<ShieldCheck />` scales down securely into the header panel with a firm visual impact.
4.  **Linguistic Message:** Displays: *"System synchronization complete. Your home asset's structural integrity and value are fully certified."*
