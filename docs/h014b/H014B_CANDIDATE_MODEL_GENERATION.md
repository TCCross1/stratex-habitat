# H014B Phase 8 — Candidate Existing-Model Generation

Backend: `backend/reality/capture.py::generate_candidate` →
`model_version_service.create_existing_model`.
Endpoint: `POST /api/reality/v1/scan-sessions/{id}/candidate`.

## Preconditions
- Scan session must be in `QUALITY_REVIEW` or `ACCEPTED` (else
  `409 CAPTURE_NOT_REVIEWABLE`).
- Tenant is server-derived; property is the authorized scan-session property.

## What it produces
From a derived structure (`dimensions_m`, walls, floor, ceiling, openings) the
service deterministically builds `MEASURED_EXISTING` spatial entities:
- 1 `ROOM` (POLYGON, dimensions, `unknowns` preserved),
- 4 `WALL`s (North/East/South/West),
- optional `FLOOR`, `CEILING`,
- per opening: an `OPENING` on its wall, plus `DOOR`/`WINDOW` referencing that
  opening (relationship-validated: openings need surface-like parents;
  doors/windows need a valid `opening_ref`).

It then creates an existing-model version referencing the new entity ids, the
uploaded artifact ids, and the source scan session, with:
`model_state = DRAFT_CANDIDATE`, `immutable = false`, `authoritative = false`,
`truth_summary = {MEASURED_EXISTING: n}`, `unknown_areas` from the Guardian.

## Truth boundary (enforced)
- `source_classification = LIDAR_CAPTURE`; `truth_classification = MEASURED_EXISTING`
  (an allowed Habitat class). Restricted classes (`VERIFIED_EXISTING`,
  `PROFESSIONALLY_REVIEWED_DESIGN`, `APPROVED_FOR_BUILD_PACKAGE`,
  `COMPLETED_AS_BUILT`) fail closed via `assert_truth_promotion_allowed`.
- The service asserts `model_state == DRAFT_CANDIDATE` before returning.
- Advancing `DRAFT_CANDIDATE → QUALITY_REVIEW → ACCEPTED` is the normal governed
  H-014A model lifecycle; there is **no path to `VERIFIED_EXISTING`** here.
- Audit `REALITY_CANDIDATE_MODEL_GENERATED` (entity count + truth class).

## Verified
- End-to-end proof: 12 entities (`ROOM×1, WALL×4, FLOOR×1, CEILING×1, OPENING×3,
  DOOR×1, WINDOW×1`), truth counts `{MEASURED_EXISTING: 12}`, `DRAFT_CANDIDATE`.
- `TestCaptureProofHTTP::test_bootstrap_full_pipeline` asserts the model state is
  `DRAFT_CANDIDATE` and **not** `VERIFIED_EXISTING`.
- `TestGuardianAndCandidateHTTP::test_candidate_requires_quality_review` (409 guard).
