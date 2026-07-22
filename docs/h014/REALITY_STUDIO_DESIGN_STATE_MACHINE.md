# REALITY STUDIO DESIGN STATE MACHINE (Phase 16)

Version 1.0.0 · Specification only. ONE canonical state machine for Reality Studio design projects,
following the accepted H-013 `workflow.py` governance shape (persistent state, optimistic
concurrency, guards, immutable audit events, recovery, single governed publication). It reconciles
the two existing machines (Steward `workflow.py` and `projects.py`) at the documentation level.

---

## 1. States
`IDEA_CAPTURED · SCAN_REQUIRED · SCAN_IN_PROGRESS · SCAN_QUALITY_REVIEW · SCAN_ACCEPTED ·
EXISTING_MODEL_CREATED · EXISTING_MODEL_REVIEWED · DESIGN_DRAFT · AI_SUGGESTION_READY ·
HOMEOWNER_EDITING · ALTERNATIVES_REVIEWED · PRODUCTS_SELECTED · ESTIMATE_READY ·
SYSTEMS_IMPACT_REVIEW · BUILD_READY_REVIEW · PROFESSIONAL_REVIEW_REQUIRED · PROFESSIONALLY_REVIEWED ·
CONTRACTOR_PACKAGE_READY · PROJECT_OPPORTUNITY_READY · IN_BUILD · COMPLETION_REVIEW ·
COMPLETED_AS_BUILT · CANCELLED · EXPIRED · FAILED_RECOVERABLE · FAILED_FINAL`

## 2. Happy-path transitions
```
IDEA_CAPTURED → SCAN_REQUIRED → SCAN_IN_PROGRESS → SCAN_QUALITY_REVIEW → SCAN_ACCEPTED
→ EXISTING_MODEL_CREATED → EXISTING_MODEL_REVIEWED → DESIGN_DRAFT → AI_SUGGESTION_READY
→ HOMEOWNER_EDITING → ALTERNATIVES_REVIEWED → PRODUCTS_SELECTED → ESTIMATE_READY
→ SYSTEMS_IMPACT_REVIEW → BUILD_READY_REVIEW
→ (PROFESSIONAL_REVIEW_REQUIRED → PROFESSIONALLY_REVIEWED)?  // conditional
→ CONTRACTOR_PACKAGE_READY → PROJECT_OPPORTUNITY_READY → IN_BUILD
→ COMPLETION_REVIEW → COMPLETED_AS_BUILT
```
Branches: `HOMEOWNER_EDITING ↔ ALTERNATIVES_REVIEWED` (loop), any active state → `CANCELLED`,
inactivity → `EXPIRED`, recoverable error → `FAILED_RECOVERABLE` → (retry) prior state, hard error →
`FAILED_FINAL`.

## 3. Transition table (actors · guards · audit)
| Transition | Actor | Guard | Audit event |
|---|---|---|---|
| IDEA_CAPTURED→SCAN_REQUIRED | homeowner | intent captured | `DESIGN_IDEA_CAPTURED` |
| SCAN_REQUIRED→SCAN_IN_PROGRESS | homeowner/operator | scan session created | `SCAN_STARTED` |
| SCAN_IN_PROGRESS→SCAN_QUALITY_REVIEW | system | capture complete/partial | `SCAN_CAPTURE_COMPLETE` |
| SCAN_QUALITY_REVIEW→SCAN_ACCEPTED | homeowner | Guardian PASS/PASS_WITH_GAPS ack | `SCAN_ACCEPTED` |
| SCAN_QUALITY_REVIEW→SCAN_IN_PROGRESS | homeowner | Guardian FAIL/FLAG rescan | `SCAN_RESCAN_REQUESTED` |
| SCAN_ACCEPTED→EXISTING_MODEL_CREATED | system | model built | `EXISTING_MODEL_CREATED` |
| EXISTING_MODEL_CREATED→EXISTING_MODEL_REVIEWED | homeowner | corrections confirmed | `EXISTING_MODEL_REVIEWED` |
| EXISTING_MODEL_REVIEWED→DESIGN_DRAFT | homeowner | design started | `DESIGN_DRAFT_STARTED` |
| DESIGN_DRAFT→AI_SUGGESTION_READY | system(AI) | governed suggestion produced | `AI_SUGGESTION_READY` |
| *→HOMEOWNER_EDITING | homeowner | edit op | `DESIGN_EDITED` |
| HOMEOWNER_EDITING→ALTERNATIVES_REVIEWED | homeowner | ≥1 alternative | `ALTERNATIVES_REVIEWED` |
| ALTERNATIVES_REVIEWED→PRODUCTS_SELECTED | homeowner | selections made | `PRODUCTS_SELECTED` |
| PRODUCTS_SELECTED→ESTIMATE_READY | system | estimate computed | `ESTIMATE_READY` |
| ESTIMATE_READY→SYSTEMS_IMPACT_REVIEW | system | systems impact assessed | `SYSTEMS_IMPACT_REVIEWED` |
| SYSTEMS_IMPACT_REVIEW→BUILD_READY_REVIEW | system | readiness policy run | `BUILD_READY_EVALUATED` |
| BUILD_READY_REVIEW→PROFESSIONAL_REVIEW_REQUIRED | policy | HARD/structural/systems trigger | `PROFESSIONAL_REVIEW_REQUIRED` |
| PROFESSIONAL_REVIEW_REQUIRED→PROFESSIONALLY_REVIEWED | professional | review complete | `PROFESSIONALLY_REVIEWED` |
| BUILD_READY_REVIEW/PROFESSIONALLY_REVIEWED→CONTRACTOR_PACKAGE_READY | homeowner+policy | no HARD blockers; conditionals acknowledged | `CONTRACTOR_PACKAGE_READY` |
| CONTRACTOR_PACKAGE_READY→PROJECT_OPPORTUNITY_READY | homeowner | governed publish | `PROJECT_OPPORTUNITY_PUBLISHED` |
| PROJECT_OPPORTUNITY_READY→IN_BUILD | contractor/Core | job accepted | `BUILD_STARTED` |
| IN_BUILD→COMPLETION_REVIEW | contractor/Core | work complete + completion scan | `COMPLETION_SUBMITTED` |
| COMPLETION_REVIEW→COMPLETED_AS_BUILT | Core/professional | approved | `COMPLETION_APPROVED` (→ Passport write-back) |
| *→CANCELLED / EXPIRED | homeowner/system | — | `DESIGN_CANCELLED` / `DESIGN_EXPIRED` |
| *→FAILED_RECOVERABLE→prior | system | transient failure | `DESIGN_FAILED_RECOVERABLE` |
| *→FAILED_FINAL | system | unrecoverable | `DESIGN_FAILED_FINAL` |

## 4. Governance guarantees (inherited from H-013)
- **Single governed publication path** to `PROJECT_OPPORTUNITY_READY` (reuses `governed_publish_service`
  + readiness policy; no bypass, HARD blockers cannot be overridden).
- Optimistic concurrency (version per project), idempotency keys on publish, immutable audit trail,
  correlation IDs, `FAILED_RECOVERABLE` recovery to the last good state.
- **Authority gates:** `PROFESSIONALLY_REVIEWED`, `APPROVED_FOR_BUILD_PACKAGE`, and
  `COMPLETED_AS_BUILT` require Core/professional actors — never Habitat/homeowner alone.

## 5. Explicit reconciliation of the two workflow/state-machine systems (docs only)
There are exactly **two** governing systems, with a clear, non-overlapping division of authority.
No third publication or readiness authority is introduced.

### 5.1 Division of responsibility
- **Reality Studio Design State Machine (H-014, this document)** governs the *design lifecycle*:
  `SCAN` → `EXISTING_MODEL` → `DESIGN` → `PRODUCTS` → `ESTIMATE` → `SYSTEMS_IMPACT` →
  `PROFESSIONAL_REVIEW` → `COMPLETION`. It owns scan, model, design, product selection, estimate,
  professional review, and completion states.
- **H-013 Steward Workflow (`backend/workflow.py`, accepted)** governs *homeowner orchestration*:
  readiness evaluation, contractor **package preview**, publication **approval**, and
  **Project Opportunity publication**.

### 5.2 Single governed publication authority (mandatory)
- The H-014 design lifecycle **does not publish**. When a design reaches
  `CONTRACTOR_PACKAGE_READY`, publication is delegated to the H-013 Steward workflow, which invokes
  the **single governed publication service** `workflow.governed_publish_service` (readiness
  recomputed server-side; HARD blockers non-overridable; idempotent; audited).
- **No third publication authority and no third readiness authority may be created.** Readiness is
  owned solely by `readiness_policy` via the Steward workflow; the design machine consumes readiness
  results, it does not compute a parallel gate.

### 5.3 Authority handoff points
| Design-machine state | Delegates to Steward workflow for |
|---|---|
| `BUILD_READY_REVIEW` | readiness evaluation (`readiness_policy`) |
| `CONTRACTOR_PACKAGE_READY` | contractor package **preview** (redaction) |
| `CONTRACTOR_PACKAGE_READY → PROJECT_OPPORTUNITY_READY` | publication **approval** + **Project Opportunity publication** via `governed_publish_service` (the one governed path) |

### 5.4 Cross-workflow references (stable IDs + auditable transitions)
- The two systems are linked only by **stable IDs**: a design project carries `steward_workflow_id`
  and `correlation_id`; the Steward workflow carries `design_project_ref`. Neither embeds the other's
  mutable state.
- Every cross-workflow handoff is an **explicit, auditable transition** emitting an audit event
  (e.g., `DESIGN_SUBMITTED_FOR_PUBLICATION`, then Steward `PROJECT_OPPORTUNITY_PUBLISHED`) with the
  shared `correlation_id`, so the end-to-end path is reconstructable from `audit_events`.

### 5.5 Legacy mapping (no code rewrite in this mission)
- Steward `workflow.py` states map onto the planning→publication segment (`DESIGN_DRAFT` …
  `PROJECT_OPPORTUNITY_READY`). `projects.py` states (IDEA→…→SAVED_TO_PASSPORT) map onto
  `IDEA_CAPTURED` … `COMPLETED_AS_BUILT`. Reconciliation is implemented in wave **H-014A**; this
  mission documents it only. The single governed H-013 publication service is reused unchanged.

## 6. Completion write-back boundary
- `COMPLETED_AS_BUILT` is the only state that yields canonical truth, and only via a Core/Passport
  -owned write-back (Constitution §8). Habitat submits; it does not write canonical truth.
