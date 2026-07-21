====================================================================
CENTCOM DIRECTIVE 014: IMPLEMENTATION GUIDE
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# IMPLEMENTATION GUIDE

This document serves as the developer handbook for compiling, configuring, testing, and shipping components in the Stratex Design System (SDS).

---

## 1. CSS VARIABLES & TAILWIND INTEGRATION

To maintain a single source of truth, all tokens must compile into CSS custom variables first, which are then mapped into the Tailwind CSS configuration file.

### 1.1 CSS Variables (`:root` mapping)
Create or edit `/src/styles/variables.css`:

```css
:root {
  /* Colors */
  --bg-app: #050505;
  --surface-primary: #111113;
  --surface-secondary: #1A1A1E;
  --primary-accent: #14F1D9;
  --primary-accent-glow: rgba(20, 241, 217, 0.2);
  --highlight-accent: #FF6B00;
  --highlight-accent-glow: rgba(255, 107, 0, 0.2);
  --border-subtle: #27272A;
  --border-active: #3F3F46;

  /* Typography Sizing */
  --font-display: 'Outfit', sans-serif;
  --font-body: 'IBM Plex Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Radius */
  --radius-none: 0px;
  --radius-xs: 2px;
  --radius-sm: 4px;
}
```

### 1.2 Tailwind Configuration (`tailwind.config.js`)
Map the CSS variables into your tailwind configuration file to enable inline class compilation:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        background_app: 'var(--bg-app)',
        surface_primary: 'var(--surface-primary)',
        surface_secondary: 'var(--surface-secondary)',
        primary_accent: 'var(--primary-accent)',
        primary_accent_glow: 'var(--primary-accent-glow)',
        highlight_accent: 'var(--highlight-accent)',
        highlight_accent_glow: 'var(--highlight-accent-glow)',
        border_subtle: 'var(--border-subtle)',
        border_active: 'var(--border-active)',
      },
      fontFamily: {
        display: 'var(--font-display)',
        sans: 'var(--font-body)',
        mono: 'var(--font-mono)',
      },
      borderRadius: {
        none: 'var(--radius-none)',
        sm: 'var(--radius-xs)',
        md: 'var(--radius-sm)',
      },
      boxShadow: {
        accent: '0 0 8px var(--primary-accent-glow)',
        active: '0 0 16px var(--primary-accent-glow)',
        highlight: '0 0 8px var(--highlight-accent-glow)',
      }
    },
  },
  plugins: [],
}
```

---

## 2. REACT COMPONENT INVENTORY & NAMING CONVENTIONS

To avoid code entropy across our distributed teams, we enforce strict naming conventions:

### 2.1 File & Directory Structures
All files must use **kebab-case** for file paths, while React components must use **PascalCase**.

```
src/
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── dialog.tsx
│   └── domain/
│       ├── property-card.tsx
│       ├── evidence-card.tsx
│       ├── dna-card.tsx
│       └── health-gauge.tsx
```

### 2.2 Component Class Declaration Style
All React components must be declared using functional arrow declarations with strict TypeScript type bindings:

```tsx
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface HealthGaugeProps {
  score: number;
  label: string;
  icon?: LucideIcon;
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({ score, label, icon: Icon }) => {
  return (
    <div className="bg-surface_primary border border-border_subtle p-4" data-testid="kpi-property-score">
      {/* Component content */}
    </div>
  );
};
```

---

## 3. STORYBOOK STRUCTURE

Every component must ship with a high-fidelity Storybook descriptor file ending in `.stories.tsx` to enable isolated visual testing.

```
src/components/domain/dna-card.tsx
src/components/domain/dna-card.stories.tsx
```

### 3.1 Storybook Hierarchy Grouping
Group components under their logical domains inside Storybook's sidebar hierarchy:

*   `Atoms/UI` — Simple buttons, sliders, basic badges.
*   `Ecosystem/Cards` — Property Cards, DNA Cards, Evidence Cards.
*   `Ecosystem/Timeline` — Chronological nodes, Living Timelines.
*   `3D Twin/Controls` — Floating overlays, orbit resets.
*   `Data/Analytics` — Sparklines, charts, progress gauges.

---

## 4. TOKEN GENERATION

For multi-platform compatibility (such as exporting to Operator Mobile built on React Native or Contractor Portal running on Swift), we use **Style Dictionary** to automatically output tokens.

*   **Source:** Single JSON file `/src/tokens/design-tokens.json` compiling keys and values.
*   **Compile Script:** Running `npm run generate-tokens` invokes Style Dictionary to build:
    *   `/src/styles/variables.css` (Web/React)
    *   `/src/styles/variables.json` (Native mobile apps)

---

## 5. VERSIONING & MIGRATION STRATEGY

The Stratex Design System uses **Semantic Versioning (SemVer)** to regulate release cycles.

```
+-----------------------------------------------------------+
|                    SEMVER RULES (SDS)                     |
+-----------------------------------------------------------+
|  v1.0.0 -> Breaking / Foundations Change (Major Release)  |
|  v1.1.0 -> New component additions (Minor Release)        |
|  v1.0.1 -> Bug fixes / CSS parameter tuning (Patch)       |
+-----------------------------------------------------------+
```

### 5.1 Three-Step Migration Playbook
When migratory updates are issued from CENTCOM:

1.  **Auditing Code Drift:** Check for custom local class declarations that bypass Tailwind variables. Use grep or eslint rules to flag hardcoded colors like `#ffffff` or custom hex values.
2.  **Shadow Installation:** Install the new SDS package version alongside the legacy build. Map experimental components behind an environment flag or feature toggle.
3.  **Local Dev Mock Run:** Run tests locally to ensure no `data-testid` endpoints are broken during the transition, verifying 100% test coverage before shipping to staging environments.
