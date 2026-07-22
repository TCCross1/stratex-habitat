# H-014 MASTER ARCHITECTURE DECISION RECORD (Phase 21)

Version 1.0.0 · Specification only. The authoritative summary of what was decided for the Habitat
Property Reality Studio architecture and why. Baseline: accepted commit `c2fc57e`.

---

## 1. What was decided
1. Adopt **one shared spatial domain model** (Phase 3) consumed by Interior, Exterior, Systems,
   Passport projections, and Living Digital Home. Interior/Exterior are views, not separate apps.
2. Adopt **one property coordinate frame** + tolerance classes (Phase 4); never claim survey-grade.
3. Govern capture via **scan sessions** (Phase 5) + an advisory **AI Scan Quality Guardian** (Phase 6).
4. Adopt **one truth & assumption taxonomy** (Phase 7) mandatory on every datum; UI must visibly
   distinguish states (color + icon + label).
5. Treat **Room DNA / Property DNA** as projections (Phase 8), not a competing canonical store.
6. Define **one Reality Studio design state machine** (Phase 16) following H-013 governance.
7. Preserve the **single governed publication path** and non-overridable HARD blockers.
8. Extend (not replace) H-013 modules: projection boundary, workflow governance, readiness policy,
   price book, redaction, fixtures, object storage, projects/PIP, audit/passport events.

## 2. Why
- The dominant failure mode for scan+design products is fragmentation (interior and exterior become
  disconnected 3D toys) and truth corruption (proposed shown as existing, estimates shown as facts).
  A shared model + one coordinate frame + one truth taxonomy + governed state machine directly
  prevent both, and reuse the proven H-013 governance so we don't rebuild accepted architecture.

## 3. Existing architecture reused
Projection boundary (`passport_projection`), governed workflow + single publish service
(`workflow`), readiness policy (`readiness_policy`), governed price book (`pricebook`), redaction
(`redaction`), fixtures (`fixture_provider`), object storage + signed retrieval + auth (`server`),
projects spine + PIP + contractor matching (`projects`), Design Studio façade + render (`design`),
`audit_events` + `passport_events`, adaptive frontend shell + Steward journey.

## 4. New architecture proposed (spec only)
Shared spatial nodes (`spatial_nodes`), scan sessions (`scan_sessions`), spatial artifacts
(`spatial_artifacts`), reality designs (`reality_designs`), Room/Property DNA projection categories,
coordinate/alignment standard, Scan Quality Guardian, Product Graph, cost-confidence estimating,
layered Living Digital Home, `/api/reality/*` route family.

## 5. Ownership matrix
| Concern | Owner |
|---|---|
| **Data ownership** — canonical property records | Passport |
| **Data ownership** — planning/design/estimates | Habitat |
| **Truth ownership** — verified/approved/completed | Core/Passport |
| **Truth ownership** — proposed/measured/estimated | Habitat (labeled) |
| **Spatial ownership** — canonical geometry | Passport/Core |
| **Spatial ownership** — planning/scan/proposed geometry | Habitat |
| **Work ownership** — field/inspection/completion | Core |
| **Relationship ownership** — homeowner experience | Habitat |

## 6. Security & integration boundaries
- Read canonical truth **only** via the projection boundary; **no** Habitat write to canonical truth.
- Contractor/professional handoff via redacted, gated packages; completion write-back is Core/Passport
  -owned. Tenant + property authorization + signed artifact access + audit everywhere.

## 7. Alternatives rejected
- **Separate Interior & Exterior data models** — rejected (fragmentation, no whole-property truth).
- **Habitat as canonical geometry owner** — rejected (violates operating model; corruption risk).
- **Per-studio coordinate systems** — rejected (cannot register interior↔exterior).
- **Unlabeled AI-generated designs / auto-promotion to verified** — rejected (fabrication/authority).
- **Vendor-locked storage or survey-grade accuracy claims** — rejected (unsupported).
- **Rewriting the two existing state machines now** — deferred (map in docs; reconcile in H-014A).

## 8. Future implementation sequence
H-014A→J per the Roadmap (Phase 20).

## 9. Known unknowns
- LiDAR device/SDK capability envelope and achievable PLANNING-tolerance residuals on real homes.
- Interior↔exterior registration reliability without control points.
- Guardian detection accuracy (mirrors/glass/occlusion) on consumer devices.
- Real regional pricing coverage/freshness beyond the current roof price book.
- Concealed-systems inference limits (mostly remain UNKNOWN by policy).

## 10. Decisions requiring human confirmation
1. Canonical **PROPERTY_FRAME origin** convention per property (auto vs surveyed control point).
2. Raw imagery **retention & deletion** windows vs warranty/legal holds.
3. Which **capture client/SDK** (and whether early waves are fixture/simulated).
4. Regional **pricing data source(s)** and licensing.
5. Whether **CAD/BIM export** is in-scope for homeowners or professional-only.
6. Storage backend selection when moving beyond the current managed object store.
