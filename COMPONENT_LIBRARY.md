====================================================================
CENTCOM DIRECTIVE 014: COMPONENT LIBRARY
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# COMPONENT LIBRARY

This document catalog-specifies all components within the Stratex Design System. Every UI element in our product ecosystem must be constructed following these exact specifications.

---

## 1. ACTION & FORM ELEMENTS

### 1.1 Buttons
Buttons trigger immediate system events. They are geometric and sharp.

*   **Primary Button:**
    *   *Visuals:* Background `#14F1D9` (Neon Teal), text `#050505` (Pure Dark), border `#14F1D9`. Sharp corners.
    *   *Hover:* Background active neon glow, text `#050505`.
    *   *Usage:* Primary call-to-action (e.g., "Request Quote", "Authorize Action").
*   **Secondary Button:**
    *   *Visuals:* Transparent background, text `#FFFFFF`, border `1px solid #3F3F46` (Active Border).
    *   *Hover:* Background `#1A1A1E`, border `#14F1D9`.
    *   *Usage:* Secondary navigations, dismissals.
*   **Destructive Button:**
    *   *Visuals:* Transparent or dark background, text `#FF3333`, border `1px solid #FF3333`.
    *   *Hover:* Background `#FF3333` (opacity 10%), text `#FF3333`.
*   **Icon-Only Button:**
    *   *Visuals:* Standard size `h-9 w-9` or `h-8 w-8`, background transparent, border none, text `#A1A1AA`.
    *   *Hover:* Text `#14F1D9` with active neon background ghosting.

### 1.2 Form Controls
Form inputs must feel like high-performance diagnostic tools.

*   **Text & Combo-boxes:**
    *   *Visuals:* Background `#1A1A1E`, border `1px solid #27272A`, text `#FFFFFF`, font-family `IBM Plex Sans`. Sharp `radius-xs` (2px).
    *   *Focus:* Border `#14F1D9`, box-shadow `0 0 8px rgba(20, 241, 217, 0.2)`.
    *   *Placeholder:* Text `#71717A` (Muted).
*   **Toggle Slides:**
    *   *Visuals:* Track `#27272A` (or `#14F1D9` when active). Slider knob `#FFFFFF` (circular pill).
*   **Required Attribute:** All forms must have a visible required indicator `*` in highlight orange (`#FF6B00`).

---

## 2. CONTAINER & STRUCTURAL PANELS

### 2.1 Standard Panels & Cards
*   **Visuals:** Background `#111113`, border `1px solid #27272A`. Sharp corner.
*   **Layout:** Standard padding `p-4 sm:p-5`. No nested deep drop shadows.
*   **Permitted Variation:** A subtle linear dark gradient `bg-gradient-to-b from-[#111113] to-[#0A0A0B]` can be applied to central focus panels.

### 2.2 Dialogs & Modals
Dialogs are floating command center overlays.

*   **Visuals:** Background `#1A1A1E`, border `1px solid #3F3F46`, radius `radius-sm` (4px). Centered on screen.
*   **Backdrop Overlay:** `#050505` at 50% opacity with a blur effect (`backdrop-blur-sm`).
*   **Header Section:** Includes an upper overline title, a bold H3 heading, and a sharp closing `X` button on the far right.

---

## 3. ECOSYSTEM DOMAIN CARDS

These custom cards are the core units of specialized dashboards:

```
+-----------------------------------------------------------+
|                   STRATEX CUSTOM DOMAIN CARDS             |
+-----------------------------------------------------------+
| 1. PROPERTY CARDS (E.g. Villa Horizon)                    |
|    - Thumbnail image with orange/teal CSS overlays        |
|    - Connection live indicator (blinking Neon Green/Teal) |
|                                                           |
| 2. EVIDENCE CARDS (Regulatory & Diagnostic proof)         |
|    - Attachment file icon + date + source indicator       |
|    - Confidence badge indicating factual authority        |
|                                                           |
| 3. DNA CARDS (Material & Structural composition)          |
|    - Dense vertical spec table of sub-system materials    |
|    - Sparkline of deterioration trends                     |
|                                                           |
| 4. PROJECT OPPORTUNITY CARDS (Upgrades & Maintenance)     |
|    - Action recommendation title + financial scope        |
|    - "Request Quote" CTA button with primary glow         |
+-----------------------------------------------------------+
```

### 3.1 Property Cards (E.g., Habitat Left Sidebar)
*   **Structure:**
    *   Fixed horizontal layout.
    *   Property thumbnail (Villa Horizon) with thermal highlight filters applied.
    *   Title `Villa Horizon` (`font-sans font-medium text-white`).
    *   Sub-label `Austin, TX` (`font-sans text-xs text-[#A1A1AA]`).
    *   Live state dot: Blinking neon-teal indicator (`#14F1D9`) representing connected, real-time sensor streams.

### 3.2 Evidence Cards
Evidence cards prove structural facts, containing images, document receipts, or raw diagnostic data.
*   **Structure:**
    *   Upper Overline: `EVIDENCE RECORD // REF-4821`
    *   Body: Document preview with confidence level indicator.
    *   Footer: Verified state badge (`#00D4FF`) showing metadata audit info.

### 3.3 DNA Cards
DNA cards map the molecular and system composition of physical assets (e.g. roof age, insulation value, structural load).
*   **Structure:**
    *   Super-dense spec lists (`font-mono text-xs`).
    *   Visual representation of layers (concrete slab, vapor barrier, active sub-base).
    *   Key parameters highlighted with a warning amber (`#FFB800`) or primary teal (`#14F1D9`) color based on state.

### 3.4 Project Opportunity Cards
Used in the Project Opportunity Engine to display maintenance upgrades or carbon-reduction recommendations.
*   **Structure:**
    *   Large Title: E.g., `Solar Photovoltaic Integration`
    *   Financial Scope Block: Cost vs. Return on Investment (`font-mono text-xl`).
    *   Efficiency Impact Gauge (Sparkline).
    *   Primary Action Button: "Request Quote" in Neon Teal.

---

## 4. COMMAND PANELS & NAVIGATION WIDGETS

### 4.1 Passport Panels
The Passport Panel shows historical transaction, modification, and inspection logs.
*   **Structure:**
    *   A sticky sidebar widget with active audit-trail records.
    *   Filter buttons for Verified, Estimated, or Projected events.
    *   Verification signature code block (`font-mono text-[10px] tracking-normal`).

### 4.2 Knowledge Graph Widgets
Shows entity relationships (e.g., HVAC connected to Thermostat connected to Master Bedroom).
*   **Structure:**
    *   Floating panel overlays.
    *   Interconnected node clusters with subtle glowing links.
    *   Active entity inspector sidebar.

### 4.3 3D Twin Controls
Control deck overlaying the central 3D scene canvas.
*   **Structure:**
    *   Floating control box in bottom center of canvas.
    *   Toggle layer buttons: Thermal, Energy, Structure, Mechanical.
    *   Camera reset button (`⌘R`) and orbit controls indicator.

---

## 5. RECHARTS & STATUS GAUGES

### 5.1 Tables
*   **Visuals:** Dark headers (`#111113`), subtle 1px divider lines (`#27272A`).
*   **Data Layout:** Standard text left-aligned, all numeric units/values right-aligned (`font-mono`).
*   **Active Row:** On hover, rows use background ghosting (`#1A1A1E` / `opacity-10`) with a neon teal left edge highlight.

### 5.2 Timeline
The Living Timeline registers chronological home events.
*   **Structure:**
    *   Continuous vertical vertical-line (`1px solid #27272A`).
    *   Chronological event nodes containing action titles and status badges.
    *   Active/Future nodes glow orange (`#FF6B00`); past/completed nodes are marked with a verified teal (`#14F1D9`).

### 5.3 Health Gauges & Progress Indicators
*   **Circular Health Gauge:**
    *   A circular ring (`recharts` or custom SVG) showing an aggregated score (e.g. `87`).
    *   The numeric score inside the ring is represented using `JetBrains Mono` at `text-3xl`.
    *   Ring color dynamically transitions from Teal (Excellent), Green (Good), Gold (Fair) to Red (Alert) based on score.
*   **Progress Indicators:**
    *   Linear progress tracks (`bg-[#27272A]` height `h-1.5`).
    *   Fill bar glows in the corresponding functional status color.

---

## 6. INTERACTIVE DATA TESTING IDs

Every component must ship with a strict, unique `data-testid` attribute for automated inspection and high-fidelity testing:

| Component Category | Element Role | data-testid Syntax |
| :--- | :--- | :--- |
| **Navigation** | Twin Tab | `data-testid="nav-twin-link"` |
| **Navigation** | Settings Gear | `data-testid="nav-settings-btn"` |
| **KPI Score** | Property Score Gauge | `data-testid="kpi-property-score"` |
| **KPI Score** | Energy Gauge | `data-testid="kpi-energy-efficiency"` |
| **Action** | Quote Request CTA | `data-testid="action-request-quote"` |
| **Action** | Toggle Layers | `data-testid="action-toggle-layer-[name]"` |
| **Inspect** | Asset Selected Detail | `data-testid="inspect-asset-name"` |
| **Telemetry** | Live Data Table | `data-testid="telemetry-table"` |
| **Form** | Text Input field | `data-testid="form-input-[field-name]"` |
