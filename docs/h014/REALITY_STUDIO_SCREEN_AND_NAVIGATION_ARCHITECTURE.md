# REALITY STUDIO SCREEN & NAVIGATION ARCHITECTURE (Phase 18)

Version 1.0.0 · Specification only. Premium, homeowner-first screen architecture that preserves the
Stratex design system and progressive disclosure, reusing the existing adaptive shell
(`AppShell`/`IconRail`/`SectionNav`/`MobileNav`).

---

## 1. Screen inventory
| Screen | Purpose | Truth emphasis |
|---|---|---|
| Property overview | Whole-property entry, Living Digital Home summary | Verified + unknowns rollup |
| Reality Studio launch | Choose Interior/Exterior/Systems studio | — |
| Scan preparation | Device/space checklist, privacy notice | Consent |
| Guided scan | Live capture with coverage heatmap + Guardian coaching | Coverage/quality |
| Scan-quality review | Guardian verdict, gaps, requested actions | Coverage/quality |
| Existing model review | 2D/3D existing model, correct segmentation | Measured/Estimated/Unknown |
| 2D editor | Plan editing (walls/openings/additions) | Existing vs proposed |
| 3D editor | 3D editing, product placement | Existing vs proposed |
| Walkthrough | First-person proposal navigation | Proposed labeled |
| Materials & products | Point-and-change selection | Proposed + source |
| Estimate | Live cost + confidence + assumptions | Cost basis + confidence |
| Systems impact | Affected systems, unknowns, pro-review flags | Unknown/advisory |
| Build Ready | Readiness checklist, blockers | HARD/CONDITIONAL |
| Professional review | Submit/track review | Reviewed vs proposed |
| Contractor package | Redacted package preview + publish | Approved-for-package |
| Version history | Named design snapshots, diffs | Version provenance |
| Completed project | As-built vs proposed diff | Completed as-built |

## 2. Navigation model
- **Mobile-first** for capture/review (bottom nav + full-screen scan); **desktop/tablet** for
  editing/review (icon rail + section nav + inspector). One shared route tree under
  `/reality/*`, integrated with existing `/twin`, `/steward`, `/systems`, `/design-studio`.
- Progressive disclosure: primary action prominent; provenance/assumptions/trace behind expanders.
- Studio switching (Interior↔Exterior↔Systems) never changes the property/model — same home, new lens.

## 3. Stratex design system (preserve)
- **Deep-black foundation** (`#0a0a0b`); **thin cyan/steel borders**; **white technical typography**
  (mono/technical); **controlled glow** (restrained, focus/interaction only).
- Restrained semantic palette: **cyan** (primary/AI idea), **green** (reviewed/verified/ready),
  **amber** (proposed/caution), **orange** (attention/brand accent), **red** (blocker/danger).
- Dimensional panels + architectural rendering aesthetic; micro-interactions on hover/selection/
  entrance; motion on specific properties (opacity/transform), not `transition: all`.

## 4. Truth-state visual language (binds Phase 7)
| Truth class | Treatment |
|---|---|
| VERIFIED_EXISTING | Solid steel outline + "verified" icon |
| MEASURED/ESTIMATED/INFERRED_EXISTING | Dashed + confidence chip |
| HOMEOWNER_REPORTED | "you told us" tag |
| AI_SUGGESTED_DESIGN | Cyan "AI idea" badge |
| PROPOSED_DESIGN | Amber "proposed" outline |
| PROFESSIONALLY_REVIEWED_DESIGN | Green "reviewed" chip |
| COMPLETED_AS_BUILT | "as-built" verified chip |
| UNKNOWN | Explicit gap/hatch, "not captured" |
Color is always paired with icon + label (accessibility, Constitution §7).

## 5. Accessibility & performance
- Keyboard/switch navigable; captions/alt text on renders; scalable type; reduced-motion honored.
- Preview models first; full-res streamed on demand; skeleton/staged reveals; offline-friendly capture.

## 6. data-testid convention (for future implementation)
`reality-<screen>-<element>-<action>` (e.g., `reality-scan-start-btn`, `reality-editor-add-wall-btn`,
`reality-estimate-total`, `reality-truth-badge-<class>`). Mandatory on all interactive + critical
info elements (matches H-013 practice).

## 7. Relationship to existing code
- Reuses adaptive shell, `Primitives`, `Inspector`, `Brand`, and the `HomeSteward` journey pattern.
  No screens implemented in this mission.
