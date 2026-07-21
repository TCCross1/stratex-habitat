====================================================================
CENTCOM DIRECTIVE 014: DESIGN TOKENS
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# DESIGN TOKENS

This document defines the atomic design variables for the Stratex Design System. These values are the building blocks of every interface and must be implemented as CSS custom variables or Tailwind CSS classes.

---

## 1. SPACING TOKENS

Stratex uses a strict **4px/8px grid** to enforce structural density and precision. Do not use arbitrary padding or margins.

| Token | CSS Value | Tailwind Class | Application |
| :--- | :--- | :--- | :--- |
| `spacing-xxs` | `2px` | `p-0.5` / `m-0.5` | Border spacing, ultra-dense lists |
| `spacing-xs` | `4px` | `p-1` / `m-1` | Inner cell padding, gap between related badges |
| `spacing-sm` | `8px` | `p-2` / `m-2` | List item spacing, form field spacing |
| `spacing-md` | `12px` | `p-3` / `m-3` | Grid gaps, small panel paddings |
| `spacing-lg` | `16px` | `p-4` / `m-4` | Default container gap, main component padding |
| `spacing-xl` | `24px` | `p-6` / `m-6` | Large panel padding, content section gaps |
| `spacing-xxl` | `32px` | `p-8` / `m-8` | App shell outer padding, hero sections |
| `spacing-3xl` | `48px` | `p-12` / `m-12` | Empty states, landing screens |
| `spacing-4xl` | `64px` | `p-16` / `m-16` | Large spatial breaks |

---

## 2. GRID & LAYOUT TOKENS

Stratex layouts use the **Control Room Grid** paradigm — high data density with zero wasted whitespace.

* **Main App Grid:** 12-column grid system (`grid-cols-12`).
* **Default Gap:** `gap-4` (`16px`) for standard dashboards.
* **Dense Gap:** `gap-2` (`8px`) for technical data tables and telemetry readouts.
* **Layout Padding:** `p-4` on mobile, `p-5` on tablet, `p-6` on desktop.
* **App Shell:** Fixed heights (`100vh`) with independent scrolling panels (`overflow-y-auto`) to mimic a professional software workstation. No long scrolling landing pages on monitoring dashboards.

---

## 3. RADIUS TOKENS

To preserve the technical, geometric, and precise aesthetic of a control room, rounded edges are strictly limited.

* **`radius-none` (`0px` / `rounded-none`):** Absolute sharp corners. Used for standard buttons, table rows, and primary panels.
* **`radius-xs` (`2px` / `rounded-sm`):** The primary radius. Used for small cards, badges, and form inputs.
* **`radius-sm` (`4px` / `rounded`):** Maximum rounding allowed. Used only for larger modals/dialogs and outer containers.
* **`radius-pill` (`9999px` / `rounded-full`):** Strictly restricted. Used only for circular avatars, status dots, and indicator rings.

---

## 4. ELEVATION & SHADOWS

Traditional fuzzy drop shadows are banned. We create depth using layers of **1px solid borders**, subtle dark backgrounds, and active neon outer glows.

```
Layer 0 (Base App)     -> #050505
Layer 1 (Card/Panel)   -> #111113 + 1px border (#27272A)
Layer 2 (Dialog/Modal) -> #1A1A1E + 1px border (#3F3F46)
Layer 3 (Hover/Focus)  -> #1A1A1E + 1px border (#14F1D9) + Active Glow
```

---

## 5. BORDERS

Borders define boundaries with scientific precision.

* **Subtle Border:** `1px solid #27272A` (`border-border_subtle`). Used for normal card separations and grid lines.
* **Active Border:** `1px solid #3F3F46` (`border-border_active`). Used for highlighted table headers, input focus, and hover states.
* **Primary Accent Border:** `1px solid #14F1D9` (`border-primary_accent`). Used to draw attention to active components or live alerts.
* **Warning Border:** `1px solid #FF6B00` (`border-highlight_accent`). Used for outstanding recommendations or estimated projections.

---

## 6. OPACITY

Opacity tokens preserve hierarchy while maintaining high contrast in dark mode.

* **`opacity-active` (`1.0` / `opacity-100`):** Primary text (`#FFFFFF`), active state icons, status colors.
* **`opacity-secondary` (`0.7` / `opacity-70`):** Secondary body text (`#A1A1AA`), labels, inert icons.
* **`opacity-muted` (`0.4` / `opacity-40`):** Muted meta-data text (`#71717A`), disabled items, unit markers (e.g. "kWh" in a smaller font next to a value).
* **`opacity-subtle` (`0.2` / `opacity-20`):** Horizontal grid lines, background patterns, unselected chart lines.
* **`opacity-ghost` (`0.08` / `opacity-10`):** Hover panel backgrounds, disabled input fields.

---

## 7. GLOW (NEON EMISSION)

Glows give our high-contrast interfaces an emissive, physical quality.

* **Accent Glow:** `box-shadow: 0 0 8px rgba(20, 241, 217, 0.2)`
* **Accent Active Glow:** `box-shadow: 0 0 16px rgba(20, 241, 217, 0.4)`
* **Highlight Glow:** `box-shadow: 0 0 8px rgba(255, 107, 0, 0.2)`
* **Alert Glow:** `box-shadow: 0 0 8px rgba(255, 51, 53, 0.2)`

---

## 8. ANIMATION TIMING & MOTION CURVES

All micro-interactions must respond instantly to maintain the "high-performance control center" feeling.

### 8.1 Timing
* **`duration-instant` (`80ms`):** Hover states, tooltips.
* **`duration-fast` (`150ms`):** Button click, active tab transitions, slide toggles.
* **`duration-smooth` (`250ms`):** Sidebar collapse/expand, modal overlay transitions.
* **`duration-slow` (`400ms`):** Complex 3D Digital Twin camera resets, long list additions.

### 8.2 Motion Curves (Easing)
* **Linear (`cubic-bezier(0, 0, 1, 1)`):** Telemetry charts, sparklines, loading spinners.
* **Ease-Out / Responsive (`cubic-bezier(0.16, 1, 0.3, 1)`):** Primary user actions (opening sidebar, button states). It is snappy at the beginning and eases out smoothly.
* **Ease-In-Out / System (`cubic-bezier(0.65, 0, 0.35, 1)`):** Automatic system actions (night-mode shifting, recurring data refreshes).

---

## 9. BREAKPOINTS

Stratex is optimized for standard field equipment and office displays.

| Breakpoint | Width | Application |
| :--- | :--- | :--- |
| `xs` | `375px` | Standard Smart Phones (field operations) |
| `sm` | `640px` | Small Tablets |
| `md` | `768px` | Standard Tablets (Contractor/Inspector on-site) |
| `lg` | `1024px` | Small Laptops / Portables |
| `xl` | `1280px` | Standard Desktop Workstations |
| `2xl` | `1536px` | Premium Displays / Developer Workstations |
| `ultra-wide` | `1920px+` | HQ War-Room Displays / Operations Centers |

---

## 10. Z-INDEX HIERARCHY

To ensure overlays do not clash during high-density operations, z-indices are explicitly zoned.

| Level | Value | UI Elements |
| :--- | :--- | :--- |
| `z-deep` | `-10` | Grid backdrops, watermarks |
| `z-base` | `0` | Default panel containers |
| `z-interactive`| `5` | Clickable list items, canvas controls |
| `z-sticky` | `10` | Persistent sub-headers, sticky list columns |
| `z-dropdown` | `20` | Combo-boxes, tooltip overlays, context menus |
| `z-sidebar` | `30` | Left navigations, collapsible drawers |
| `z-header` | `40` | Sticky top navigation bar |
| `z-overlay` | `50` | Background dims, modal screens, dialog box panels |
| `z-notification`| `100` | Broadcast notices, toast messages, critical active alarms |
