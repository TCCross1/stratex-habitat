# HABITAT PROPERTY REALITY STUDIO™ — PRODUCT CONSTITUTION (Phase 2)

Version: 1.0.0 (H-014 architecture baseline) · Status: **Specification only — not implemented.**
Supersedes nothing in H-013; H-013 Wave 1 is the accepted foundation this builds on.

---

## 1. Mission
Give every homeowner a truthful, premium, self-serve way to understand, redesign, price, and
prepare real work on their actual property — interior, exterior, and systems — without needing
professional software or professional vocabulary, while never corrupting canonical property truth.

## 2. Product promise
**Interior Reality Studio:** *"Scan it. Walk it. Redesign it. Price it. Build it."*

The homeowner can: scan a real room (iPhone/iPad LiDAR) → see it as an editable 2D + 3D model →
understand scan quality and gaps → add/modify walls, openings, rooms, additions → change finishes,
products, fixtures, windows, doors, lighting, flooring, paint, trim, cabinetry, systems → walk
through proposals → compare alternatives → see cost and confidence update live → prepare a
contractor-ready package → preserve approved completed work through Property Passport.

The homeowner must NOT need to understand: CAD, BIM, construction drawings, building-science
terminology, professional design software, or material-takeoff systems.

## 3. Immutable operating model (non-negotiable)
**Core performs the work. Passport remembers the home. Habitat sustains the relationship.**
- **STRATEX Core** owns verified field work, inspections, evidence, findings, analysis, contractor
  workflow, professional review, approved completion data.
- **Property Passport** owns canonical property truth, approved geometry, approved findings,
  versioned history, provenance, and property projections.
- **Habitat** owns homeowner interaction, planning geometry, design alternatives, preferences,
  estimates, project preparation, and homeowner-safe visualization.

## 4. Habitat must NEVER
- Alter canonical Passport truth.
- Present proposed design geometry as existing verified geometry.
- Present homeowner edits as professionally approved.
- Fabricate dimensions, systems, materials, or findings.
- Merge verified and proposed geometry without clear labeling.
- Treat AI-generated designs as code-compliant or structurally approved.
- Publish contractor-ready packages without required validation.

## 5. Non-negotiable principles
1. **Truth-state protection** — every geometry, dimension, material, system, opening, finding, and
   design element carries a truth classification (Phase 7) and is visibly distinguished in the UI.
2. **Existing vs proposed** — existing (from Passport/Core/scan) and proposed (homeowner/AI design)
   geometry are never visually conflated; proposed is always labeled.
3. **Verified vs estimated dimensions** — measured/verified values and estimated/inferred values are
   labeled and carry confidence.
4. **Scan confidence is surfaced** — coverage and quality are shown; low-confidence geometry is
   marked, never silently trusted.
5. **Assumptions are explicit** — assumptions and unknowns are listed, never hidden; unknown
   concealed conditions stay UNKNOWN.
6. **Safety & structural boundaries** — nothing in Habitat asserts structural adequacy, load paths,
   or code compliance; those require Core/professional review with explicit disclaimers.
7. **No generic AI design workflows** — AI suggestions are governed, bounded to the real model, and
   classified `AI_SUGGESTED_DESIGN`; they carry no authority.
8. **No fabricated data** — no invented SKUs, prices, measurements, or findings.
9. **Progressive disclosure** — simple by default; depth (trace, provenance, assumptions) on demand.
10. **Human review gates** — professional and contractor handoffs are explicit, gated states.

## 6. Homeowner freedom, control & guidance
- The homeowner may freely explore, edit, and compare; nothing they do mutates canonical truth.
- Guidance ("professional guidance without jargon") is phrased in plain language with optional
  expert detail behind progressive disclosure.
- The homeowner controls what is shared (products, documents, contact) and when.

## 7. Accessibility & premium standards
- WCAG-minded: color is never the sole signal (icons + labels accompany truth-state color coding);
  keyboard/switch navigation; captions/alt text on renders; scalable type.
- Premium Stratex visual system (Phase 18): deep-black foundation, thin cyan/steel borders, white
  technical typography, controlled glow, restrained cyan/green/amber/orange/red, dimensional panels.

## 8. Handoff & completion
- **Contractor/professional handoff** occurs only from gated states with required validations
  (readiness policy), producing a redacted, governed contractor package.
- **Completion update into Passport** is approval-gated: only Core/professionally-approved
  completion data becomes `COMPLETED_AS_BUILT` canonical truth; Habitat proposes, it never writes
  canonical truth directly (write-back is a Core/Passport-owned operation).

## 9. Auditability, versioning, privacy, security
- **Auditability:** every state change, publication, projection read, and handoff emits an immutable
  audit event (extends H-013 `audit_events`).
- **Versioning:** geometry, scans, designs, estimates, projections, and contracts are versioned with
  provenance and effective timestamps.
- **Privacy:** interior imagery, geolocation, and occupant data are sensitive by default; signed,
  scoped access only; redaction at the boundary (Phase 19).
- **Security:** tenant isolation and per-property authorization on every request; least privilege.

## 10. Performance & resilience expectations
- Mobile-first capture and preview; large artifacts stream/optimize; full-resolution on demand.
- **Offline & interrupted-scan recovery:** scans are resumable; partial captures are preserved,
  labeled incomplete, and never treated as complete truth; uploads recover after interruption.

## 11. Explicit non-goals (this mission)
No LiDAR app, no 3D editor, no Exterior Studio implementation, no production cloud processing, no
new third-party SDKs, no storage-vendor lock-in. This is the constitution and architecture only.
