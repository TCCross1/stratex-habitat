# Readiness Blocker Policy (H-013 Batch 2, Phase 5)

**Module:** `backend/readiness_policy.py` — backend-owned. The frontend renders results; it never decides blocking behavior.
**Tested:** 6 unit tests + `/api/steward/readiness` HTTP verification.

## Classifications
| Level | Publication effect |
|---|---|
| `HARD_BLOCKER` | Forbidden until the item is resolved (VERIFIED/COMPLETE/RESOLVED). |
| `CONDITIONAL_BLOCKER` | Allowed only when the homeowner **acknowledges** it (site verification required, and the contractor package must expose the requirement) or it is resolved. |
| `WARNING` | Allowed; disclosed. |
| `INFORMATIONAL_GAP` | Allowed; item remains listed as incomplete. |

## Per-item fields (`assess()` -> `priority_checklist[]`)
`item_id`, `item` (name, legacy), `classification`, `description`, `why`/`why_it_matters`, `who_can_verify`/`verified_by` (legacy), `verification_state`, `status` (legacy), `site_verification_required`, `acknowledgment_required`, `acknowledged`, `blocks_publication`, `score`, `resolved_at`, `resolver_identity`.

## Canonical roof items
| item_id | Classification | Default state |
|---|---|---|
| `RDY-OWNERSHIP` | HARD_BLOCKER | VERIFIED |
| `RDY-PROPERTY-INFO` | INFORMATIONAL_GAP | COMPLETE |
| `RDY-ROOF-GEOMETRY` | INFORMATIONAL_GAP | COMPLETE |
| `RDY-DECK-CONDITION` (“Existing Deck & Underlayment Condition”) | CONDITIONAL_BLOCKER | MISSING |
| `RDY-WARRANTY` | WARNING | UNVERIFIED |
| `RDY-PERMIT-HOA` | INFORMATIONAL_GAP | COMPLETE |

## Publish decision
`can_publish = (no unresolved HARD_BLOCKER) AND (no unacknowledged CONDITIONAL_BLOCKER)`.
`assess(acknowledged, overrides)` returns `unresolved_hard_blocker_ids`, `required_acknowledgment_ids`, `can_publish`, and the full checklist.

## Backward compatibility
Default (no acknowledgments) yields `project_readiness_score == 65` and the deck item `status=="MISSING"`, `blocks_publication==true` — matching the H-012 contract the frontend already renders.
