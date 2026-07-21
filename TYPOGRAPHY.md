====================================================================
CENTCOM DIRECTIVE 014: TYPOGRAPHY STANDARDS
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# TYPOGRAPHY STANDARDS

This document dictates the typography rules, font families, scale sizes, line-height configurations, and data density hierarchy for all Stratex interfaces.

---

## 1. FONT FAMILIES

We use three premium fonts, each assigned to a precise cognitive role. There shall be no deviations or substitute fallbacks.

```
       +-----------------------------------------------------------+
       |                     TYPOGRAPHY ROLES                      |
       +-----------------------------------------------------------+
       |  1. HEADINGS (Outfit)                                     |
       |     Vibe: Futurist, clean, premium, architectural.        |
       |                                                           |
       |  2. BODY TEXT (IBM Plex Sans)                             |
       |     Vibe: Highly legible, technical, Swiss-style.        |
       |                                                           |
       |  3. DATA / METRICS (JetBrains Mono)                       |
       |     Vibe: High-precision, zero-ambiguity alignment.      |
       +-----------------------------------------------------------+
```

### 1.1 Heading Font: Outfit
*   **Role:** Product naming, page headings, main section labels.
*   **CSS:** `font-family: 'Outfit', sans-serif;`
*   **Aesthetic:** Broad letterforms, geometric spacing, geometric curves.

### 1.2 Body Font: IBM Plex Sans
*   **Role:** Technical descriptions, contractor details, general copy, modal text, form inputs.
*   **CSS:** `font-family: 'IBM Plex Sans', sans-serif;`
*   **Aesthetic:** Humanist-mechanical hybrid with high readability at small text sizes.

### 1.3 Data / Metric Font: JetBrains Mono
*   **Role:** Telemetry feeds, counts, timestamps, scores, coordinates, currency, and financial figures.
*   **CSS:** `font-family: 'JetBrains Mono', monospace;`
*   **Aesthetic:** Equal-width numeric glyphs. Crucially prevents "jitter" or layout jumping when numeric data updates rapidly in real-time.

---

## 2. THE TYPOGRAPHIC SCALE

All sizes are computed from a default `16px` base (`1rem`).

| Style Token | Size (px) | Tailwind Utility | Weight / Tracking | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `display-h1` | `30px` | `text-2xl sm:text-3xl` | Semi-bold (`font-semibold`) / `tracking-tight` | Page title, Main Command Header |
| `section-h2` | `20px` | `text-xl` | Medium (`font-medium`) / `tracking-tight` | Section headings, panel titles |
| `card-h3` | `16px` | `text-base` | Medium (`font-medium`) / `tracking-tight` | Component card titles, modal headers |
| `body-large` | `16px` | `text-base` | Regular (`font-normal`) / `tracking-normal` | Intro text, primary descriptions |
| `body-normal`| `14px` | `text-sm` | Regular (`font-normal`) / `leading-relaxed` | General UI copy, action labels |
| `body-small` | `12px` | `text-xs` | Regular (`font-normal`) / `leading-normal` | Meta-data, table cell details |
| `overline` | `10px` | `text-[10px]` | Bold (`font-bold`) / `tracking-[0.2em] uppercase` | Super-labels, telemetry headers |
| `data-display`| `30px` | `text-2xl sm:text-3xl`| Medium (`font-medium`) / `font-mono` | KPI numbers, system health scores |
| `data-inline` | `14px` | `text-sm` | Regular (`font-normal`) / `font-mono` | Table metrics, timestamps, UUIDs |

---

## 3. LINE-HEIGHT & COGNITIVE DENSITY

To maintain high data density without cluttering, vertical line-heights are tightly budgeted:

*   **Headings (`display-h1`, `section-h2`):** `leading-tight` (`1.15` to `1.2`). Since these are short and geometric, tight leading prevents separation from their immediate details.
*   **UI Copy (`body-normal`, `body-large`):** `leading-relaxed` (`1.5` to `1.6`). Crucial for explaining home systems without visual fatigue.
*   **Data Feeds / Tables:** `leading-none` or `leading-normal` (`1.0` to `1.25`). Minimizes row height, maximizing visible entries.

---

## 4. DESIGN GUIDELINES & CONTRAINTS

### 4.1 "Number Jitter" Prevention
Never use standard proportional fonts for numbers that change. If displaying a score (e.g. `87/100`), a balance (e.g. `$14,200`), or a duration (e.g. `12m 4s`), you **MUST** apply the `font-mono` (`JetBrains Mono`) class.

### 4.2 Letter Spacing (Tracking)
*   **Outfit Heading Tracking:** Always use `tracking-tight` on headings larger than `20px`. This keeps the geometric font cohesive.
*   **Overline Tracking:** Always use heavy letter-spacing `tracking-[0.2em]` or `tracking-widest` on upper-case overline text to guarantee structural readability.

### 4.3 Text Alignment Rules
*   **Numerical Columns:** Always right-align numeric data in tables or vertical feeds. This allows operators to scan magnitudes instantly.
*   **Text Descriptions:** Always left-align text copy. Never use fully-justified text blocks.
*   **Centered Labels:** Only center text on isolated single-line badges or in small circular metrics (like health gauge centers).

---

## 5. TYPOGRAPHY ACCESSIBILITY

1.  **Strict Relative Units:** All font sizes must be declared in `rem` or `em` values, never hardcoded `px`, allowing the user's browser-level zooming preferences to take effect smoothly.
2.  **Contrast Minimums:** Text smaller than `14px` must use pure white (`#FFFFFF`) or high-contrast secondary (`#A1A1AA`) over the dark app background. Never use `text-muted` (`#71717A`) for functional body paragraphs.
3.  **Maximum Line Length:** To maximize cognitive comprehension, paragraphs of body text should never exceed **75 characters** in width. Use responsive containers to wrap text gracefully.
