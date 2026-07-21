====================================================================
CENTCOM DIRECTIVE 014: RESPONSIVE STANDARDS
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# RESPONSIVE STANDARDS

This document dictates how the Stratex Design System scales across all screen dimensions, including phone, tablet, desktop, and ultra-wide HQ layouts, alongside touch and accessibility controls.

---

## 1. THE RESPONSIVE VIEWPORT MATRIX

Stratex applications are built to adapt gracefully across four primary device categories.

```
       +-----------------------------------------------------------+
       |                  VIEWPORT MATRIX SCALING                  |
       +-----------------------------------------------------------+
       |   Phone (Touch / Field Mobile)                            |
       |     - Main layout: 1-column vertically stacked card panels |
       |     - Navigation: Floating Bottom Tab Bar                 |
       |                                                           |
       |   Tablet (Touch / Mobile Inspector)                       |
       |     - Main layout: Collapsible icon-only rail sidebar      |
       |     - Navigation: Top-bar + Adaptive Section drawer       |
       |                                                           |
       |   Desktop (Workstation / Operator Desk)                  |
       |     - Main layout: Full 3-column command panel shell      |
       |     - Navigation: Persistent double sidebars + search bar  |
       |                                                           |
       |   Ultra-Wide (HQ Wall / Command Center)                   |
       |     - Main layout: Multi-panel grid viewport dashboard    |
       |     - Navigation: Unrestricted spatial grids              |
       +-----------------------------------------------------------+
```

### 1.1 Phone Layout (xs / sm Breakpoints — 375px to 640px)
*   **Grid:** Single column layout (`flex flex-col` or `grid-cols-1`).
*   **Navigation:** Top nav remains sticky but collapses profile and search into a single expandable `<Menu />` overlay. Traditional left sidebars are hidden; in their place, a persistent **Bottom Nav Bar** provides thumbs-reach buttons (Twin, Timeline, Projects, Docs, Settings).
*   **Spacing:** Margins reduce to `p-4` with tight inner gaps `gap-2` to maximize density on tight screens.

### 1.2 Tablet Layout (md Breakpoint — 768px)
*   **Grid:** 2-column split. The Left sidebar collapses into an icon-only narrow vertical rail. The wide section nav panel slides out on click as a temporary drawer.
*   **Interactive Controls:** Ideal for on-site field contractors holding active clipboards. Touch targets are slightly enlarged, and the center 3D stage takes up **60%** of the canvas.

### 1.3 Desktop Layout (lg / xl Breakpoints — 1024px to 1280px)
*   **Grid:** Full 3-column "Control Room" app shell.
    *   *Column 1:* Double Sidebar Navigation (Left vertical icon rail + Section Navigation Panel).
    *   *Column 2:* Center Stage (Main live 3D Twin canvas + telemetry data tables + KPI metrics).
    *   *Column 3:* Right-side Inspector panel displaying selected component status.
*   **Height:** Fixed `100vh` app frame with zero scrolling outside the designated panel boundaries.

### 1.4 Ultra-Wide Layout (2xl / 1920px+ Breakpoint)
*   **Grid:** 4-column system or extended multi-panel grids.
*   **Usage:** Operations centers, HQ monitoring rooms. Left and right sidebars expand into dual-inspector panels (such as displaying real-time live video streams or raw database feeds alongside the 3D model).

---

## 2. TOUCH & GESTURE OPTIMIZATION

For tablet and smartphone users (especially contractors on ladders or inspectors in crawlspaces), physical click precision is low.

*   **Touch Targets:** Every interactive button, link, or menu row must have a minimum interactive touch target area of **44px x 44px**.
*   **3D Orbit Gestures:**
    *   *Single-finger drag:* Orbit camera angle.
    *   *Two-finger pinch:* Zoom camera focal depth.
    *   *Two-finger swipe:* Pan camera position.
*   **Dismissal:** All slide-out side drawers or overlay modals can be dismissed by swiping away towards the screen edge.

---

## 3. KEYBOARD NAVIGATION & FOCUS SYSTEM

For command center operators managing systems with blazing efficiency, mouse-clicks are too slow. Keyboard control is a strict requirement.

*   **Global Command Search (⌘K / Ctrl+K):** Instantly triggers the global search console from any screen.
*   **Standard Focus Outlines:** Interactive items must use a high-contrast focus outline when traversed via keyboard `Tab` controls. Use `outline-none ring-1 ring-[#14F1D9] ring-offset-2 ring-offset-[#050505]`.
*   **Interactive Hotkeys:**
    *   `1`, `2`, `3`, `4`: Quick-toggle the Digital Twin overlays (Thermal, Energy, Structure, Mechanical).
    *   `Esc`: Closes any active modal or context dropdown.
    *   `⌘R` / `Ctrl+R`: Resets the 3D camera to default isometric angles.

---

## 4. SCREEN READER ACCESSIBILITY (WCAG 2.1 AA)

All Stratex interfaces must remain usable by operators using assistive equipment.

*   **Semantic HTML:** Use proper HTML tags instead of nested generic divs (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`, `<button>`).
*   **ARIA Labels:** All icon-only buttons or graphical status controls must ship with descriptive `aria-label` tags (e.g. `<button aria-label="Toggle structural wireframe overlay">`).
*   **Alt Text:** Non-decorational images must carry descriptive `alt` attributes. 
*   **Skip-Links:** A hidden skip-to-content button must sit at the absolute top of the DOM structure, allowing keyboard users to bypass side navigations instantly.
