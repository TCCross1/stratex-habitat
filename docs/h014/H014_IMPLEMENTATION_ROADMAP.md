# H-014 IMPLEMENTATION ROADMAP (Phase 20)

Version 1.0.0 · Specification only. Sequenced to **extend** accepted H-013 architecture, never
replace it. Each wave has dependencies, risks, acceptance gates, and explicit stop conditions.
Nothing in this roadmap is executed in this mission.

---

## Wave sequence
| Wave | Scope | Key deps | Acceptance gate | Stop condition |
|---|---|---|---|---|
| **H-014A** | Constitution, shared spatial model, coordinate standard, scan-session + artifact architecture (schemas + governed skeleton routes, fixture-gated) | H-013 baseline `c2fc57e` | Schemas + boundaries reviewed; projection/audit patterns reused; no canonical writes | Stop before real capture; Atlas review |
| **H-014B** | Interior LiDAR capture + Scan Quality Guardian | H-014A; iOS/iPadOS LiDAR client | Resumable capture + Guardian verdicts on real/sim data; imagery restricted | Stop before model build; no fabricated PASS |
| **H-014C** | Existing-room 2D/3D digital twin (segmentation, review/correct) | H-014B | Existing model labeled MEASURED/ESTIMATED/UNKNOWN; corrections audited | Stop before design edits |
| **H-014D** | Editable family-room addition + design alternatives (governed AI) | H-014C; Phase 16 states | Proposed/AI labeled; alternatives compare; undo/redo/version | Stop before products/estimate |
| **H-014E** | Products, materials, walkthrough, estimate sync | H-014D; Phase 14/15 | Point-and-change propagation; live cost + confidence; allowances flagged | Stop before contractor publish |
| **H-014F** | Build Ready, professional review, contractor package, Passport projection handoff | H-014E; readiness policy; `redaction`; projection boundary | Governed publish (single path); HARD blockers cannot be overridden; redacted package | Stop before as-built write-back automation |
| **H-014G** | Interior expansion to more room types + multiple levels | H-014C–F | Multi-room/level alignment; level stacking | Stop before exterior |
| **H-014H** | Exterior Reality Studio foundation | H-014A shared model | Exterior nodes over shared model; interior↔exterior registration | Stop before drone pipeline |
| **H-014I** | Drone, photogrammetry, LiDAR, thermal/AWE, damage-layer registration | H-014H; capture pipelines | Multi-source alignment to PROPERTY_FRAME with residual error; overlays labeled | Stop before whole-property automation |
| **H-014J** | Whole Property Transformation + Living Digital Home | H-014G–I | Unified layered home; cross-studio consistency | Program review |

## Risks
- **Accuracy over-claiming** — mitigated by tolerance classes (Phase 4) + truth taxonomy (Phase 7);
  never claim survey-grade.
- **AI authority creep** — governed, bounded, non-authoritative AI (Phase 6/16).
- **Imagery/privacy exposure** — restricted imagery + signed access + redaction (Phase 19).
- **Model fragmentation** — single shared spatial model + one coordinate frame (Phases 3/4).
- **Canonical corruption** — projection boundary read-only; write-back Core/Passport-owned.
- **Device/SDK dependency** — LiDAR capabilities vary; fixture-gate + graceful degradation.
- **Large-file/offline** — chunked resumable transfer (Phase 13); no silent data loss.

## Cross-cutting acceptance gates (every wave)
1. No canonical Passport write from Habitat. 2. Every spatial datum carries a truth class + source.
3. Single governed publication path preserved. 4. HARD blockers non-overridable. 5. No fabricated
data; unknowns stay UNKNOWN. 6. Tenant/property authorization + audit on all paths. 7. Atlas QC
evidence review before acceptance.

## Global stop conditions (this mission)
Do not implement LiDAR capture, the 3D editor, Exterior Studio, production cloud processing, or new
third-party SDKs. Documentation only; await Atlas QC.
