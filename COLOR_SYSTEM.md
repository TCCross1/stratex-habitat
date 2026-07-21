====================================================================
CENTCOM DIRECTIVE 014: COLOR SYSTEM
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# COLOR SYSTEM

This document establishes the official color palette for the Stratex Design System. It dictates exact hex codes, opacity variables, print-safe rules, and accessibility standards for color-blind operators.

---

## 1. PRIMARY THEME: THE COMMAND CENTER DARK MODE

Our primary palette is **strictly Dark Mode**. It is optimized for long-duration viewing in control rooms, command centers, and field operations, reducing eye strain and maximizing emissive color readability.

*   **Purple and Blue gradients are strictly BANNED.** No playful SaaS "magic" gradients are allowed.
*   **Permitted Gradients:** Subtle black-to-graphite linear gradients (`bg-gradient-to-b from-[#111113] to-[#0A0A0B]`) for card panels are permitted to add architectural depth.

### 1.1 Base Surfaces & Backgrounds
| Token Name | Hex Code | Tailwind Syntax | Description / Usage |
| :--- | :--- | :--- | :--- |
| `background-app` | `#050505` | `bg-[#050505]` | Core dark backdrop of the entire application. |
| `surface-primary`| `#111113` | `bg-[#111113]` | Primary card/panel container color. |
| `surface-secondary`| `#1A1A1E` | `bg-[#1A1A1E]` | Secondary containers, inputs, or popovers. |
| `surface-accent` | `#222226` | `bg-[#222226]` | Selected/focused background states. |

### 1.2 Core Accents
| Token Name | Hex Code | Tailwind Syntax | Description / Usage |
| :--- | :--- | :--- | :--- |
| `primary-accent` | `#14F1D9` | `text-[#14F1D9]` / `border-[#14F1D9]` | **Electric Neon Teal**. Used for brand, active states, Excellent health. |
| `highlight-accent`| `#FF6B00` | `text-[#FF6B00]` / `border-[#FF6B00]` | **High-Contrast Orange**. Used for upgrades, active recommendations. |

### 1.3 Text Palette
| Token Name | Hex Code | Tailwind Syntax | Description / Usage |
| :--- | :--- | :--- | :--- |
| `text-primary` | `#FFFFFF` | `text-white` | Header and primary text (100% opacity). |
| `text-secondary`| `#A1A1AA` | `text-[#A1A1AA]` | Body text and active labels (70% opacity). |
| `text-muted` | `#71717A` | `text-[#71717A]` | Metadata, unit annotations, disabled text (40% opacity). |

---

## 2. FUNCTIONAL & TELEMETRY STATES

Functional colors represent statuses, confidence levels, data categories, and metadata truth-states. They must remain highly distinct.

### 2.1 System Health & Alert Levels
| State | Hex Code | Tailwind | Linguistic Context ("Always Explain, Never Alarm") |
| :--- | :--- | :--- | :--- |
| **Excellent** | `#14F1D9` | `text-[#14F1D9]` | *"Systems are operating at their peak design specification."* |
| **Good** | `#00FF66` | `text-[#00FF66]` | *"Your home is performing beautifully and efficiently."* |
| **Fair** | `#FFB800` | `text-[#FFB800]` | *"A minor tune-up is recommended to restore peak operation."* |
| **Alert** | `#FF3333` | `text-[#FF3333]` | *"A component requires your kind attention to remain protected."* |

### 2.2 Truth & Projection Indicators
These indicators signal the exact origin of a data point or financial figure in the timeline, calculations, or reports.

*   **Verified:** `#00D4FF` (Bright Turquoise Blue). Data that has been verified by manual inspection, utility bills, or authenticated sensors.
*   **Estimated:** `#FFB800` (Amber Gold). Data computed by Stratex local engines based on model trends.
*   **Projected:** `#FF6B00` (Accent Orange). Future-looking modeling, simulated scenarios, or proposed upgrades.
*   **Unknown:** `#71717A` (Zinc Gray). Missing telemetry, inactive sensors, or unconfigured metrics.

### 2.3 Evidence & Confidence Mapping
Used on **Evidence Cards**, **DNA Cards**, and **Knowledge Graphs**:

*   **Evidence Node:** `#D946EF` (Neon Magenta). Represents physical photos, contractor invoices, or diagnostic payloads.
*   **Confidence Levels:**
    *   *High Confidence:* `#00FF66` (Green Glow) — Multi-sensor agreement or verified source.
    *   *Medium Confidence:* `#FFB800` (Gold Glow) — Analytical inference.
    *   *Low Confidence:* `#FF3333` (Red Glow) — Outdated telemetry or sparse sensor input.

---

## 3. PRINT-SAFE PALETTE

For official PDFs, regulatory submittals, or insurance reports, Dark Mode is banned to preserve ink and maintain traditional readability.

*   **Canvas Background:** `#FFFFFF` (Pure White).
*   **Text Primary:** `#111113` (Near Black).
*   **Text Secondary:** `#4B5563` (Dark Slate).
*   **Grid Lines / Borders:** `#E5E7EB` (Light Gray).
*   **System Accents:**
    *   *Excellent / Primary Teal:* `#0891B2` (Darker Teal).
    *   *Warning / Amber:* `#D97706` (Darker Amber).
    *   *Alert / Red:* `#DC2626` (Standard Red).
    *   *Info / Blue:* `#2563EB` (Standard Blue).

---

## 4. COLOR-BLIND ACCESSIBILITY

Color must never be the *sole* mechanism used to convey information or status. Every critical status reading must combine color with a clear icon, textual label, and high-contrast styling.

### 4.1 Contrast Standards (WCAG AAA)
*   All active text must achieve a minimum contrast ratio of **7:1** against backgrounds.
*   Non-text interactive boundaries (input lines, buttons) must maintain a **4.5:1** contrast ratio.

### 4.2 Color-Blind Adaptive Rules
1.  **Deuteranopia / Protanopia (Red-Green Shift):**
    *   Do not overlay red text directly on a green background, or vice versa.
    *   *Excellent* (`#14F1D9`) has a strong blue-cyan component, and *Good* (`#00FF66`) is a very bright green, making them distinct from *Alert* (`#FF3333`).
2.  **Tritanopia (Blue-Yellow Shift):**
    *   *Alert* (`#FF3333`) and *Excellent* (`#14F1D9`) remain highly contrasting.
3.  **Pattern Fill Requirement:**
    *   All charts (recharts) representing discrete channels must use distinct dashed/solid patterns (`strokeDasharray`) alongside color to separate lines.
