# SPATIAL TRUTH & ASSUMPTION STANDARD (Phase 7)

Version 1.0.0 · Specification only. Defines the ONE mandatory truth taxonomy for every geometry
object, dimension, material, system, opening, finding, and design element across all studios. This
is the unifying vocabulary that reconciles the fragmented classifications found in Phase 1.

---

## 1. Mandatory classifications
| Class | Meaning | Authority | Typical source |
|---|---|---|---|
| `VERIFIED_EXISTING` | Confirmed real condition | Passport/Core-certified | Passport projection, Core field verification |
| `MEASURED_EXISTING` | Captured & well-fit, not yet certified | Habitat (measurement) | Good-coverage LiDAR/photogrammetry |
| `ESTIMATED_EXISTING` | Existing but derived/gap-filled | Habitat (estimate) | Partial scan, interpolation |
| `INFERRED_EXISTING` | Existing inferred from indirect signals | Habitat (inference) | Model inference, adjacency |
| `HOMEOWNER_REPORTED` | Stated by homeowner | Homeowner | Conversation/entry |
| `PROPOSED_DESIGN` | Homeowner-authored proposed change | Habitat (planning) | Editor edits |
| `AI_SUGGESTED_DESIGN` | AI-generated suggestion | Habitat (AI, no authority) | Design assistant |
| `PROFESSIONALLY_REVIEWED_DESIGN` | Reviewed by a professional | Core/professional | Review gate |
| `APPROVED_FOR_BUILD_PACKAGE` | Cleared for contractor package | Core/gated | Build-Ready + review |
| `COMPLETED_AS_BUILT` | Installed & approved reality | Core/Passport write-back | Post-completion scan + approval |
| `UNKNOWN` | Not captured / concealed / undetermined | — | Occlusion, concealed systems |

## 2. Confidence (orthogonal)
`HIGH | MEDIUM | LOW | UNKNOWN` accompanies each classification (a `MEASURED_EXISTING` value can be
MEDIUM confidence). Confidence never upgrades a classification (measured stays measured).

## 3. Promotion rules (one-directional, gated)
```
UNKNOWN ─capture→ MEASURED/ESTIMATED/INFERRED_EXISTING ─Core/pro approval→ VERIFIED_EXISTING
IDEA ─edit→ PROPOSED_DESIGN ─assistant→ AI_SUGGESTED_DESIGN
PROPOSED/AI_SUGGESTED ─review→ PROFESSIONALLY_REVIEWED_DESIGN ─gate→ APPROVED_FOR_BUILD_PACKAGE
APPROVED_FOR_BUILD_PACKAGE ─build+approval→ COMPLETED_AS_BUILT
```
- Habitat can move items only up to `PROPOSED_DESIGN`/`MEASURED_EXISTING`. Everything beyond requires
  Core/professional authority. **Habitat can never self-promote to VERIFIED / REVIEWED / APPROVED /
  COMPLETED.**

## 4. Mandatory UI distinction
The UI must visibly (not by color alone — icon + label + optional pattern) distinguish:
- Existing truth (`VERIFIED_EXISTING`) — solid/steel.
- Estimated existing condition (`MEASURED/ESTIMATED/INFERRED_EXISTING`) — dashed + confidence chip.
- Homeowner-entered (`HOMEOWNER_REPORTED`) — tagged "you told us".
- AI suggestion (`AI_SUGGESTED_DESIGN`) — cyan "AI idea" badge, non-authoritative.
- Proposed design (`PROPOSED_DESIGN`) — amber "proposed" outline, never overlaid as existing.
- Professionally reviewed (`PROFESSIONALLY_REVIEWED_DESIGN`) — green "reviewed" chip.
- Completed as-built (`COMPLETED_AS_BUILT`) — verified "as-built" chip.

## 5. Assumption handling
- Assumptions and unknowns are first-class, listed, and carried into estimates and contractor
  packages (extends `project_assumptions` + Steward "known unknowns").
- No assumption may silently become a fact. Unknown concealed systems/conditions stay `UNKNOWN`.

## 6. Mapping legacy vocabularies (no rename in this mission)
| Legacy | H-014 class |
|---|---|
| Projection `VERIFIED` (canonical) | `VERIFIED_EXISTING` |
| Projection `ESTIMATED` | `ESTIMATED_EXISTING` |
| Projection `PROJECTED`/`SUGGESTED` | `INFERRED_EXISTING` / `AI_SUGGESTED_DESIGN` (by context) |
| Projection `HOMEOWNER_REPORTED` | `HOMEOWNER_REPORTED` |
| Projection `UNKNOWN` | `UNKNOWN` |
| Product `CONCEPT_VISUALIZATION_ONLY` | `AI_SUGGESTED_DESIGN` / `PROPOSED_DESIGN` |
| Product `REQUIRES_FIELD_VERIFICATION` | (existing) MEASURED/ESTIMATED + `UNKNOWN` gaps |

## 7. Auditability
- Any classification change (especially promotions) emits an audit event with actor, before/after,
  authority, and correlation id.

## 8. Anti-fabrication guarantee
No dimension, material, system, opening, finding, or price may be presented without a classification
and source. Absence of data ⇒ `UNKNOWN`, never a filled-in guess presented as fact.
