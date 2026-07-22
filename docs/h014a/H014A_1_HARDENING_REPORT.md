# H-014A.1 — Post-Acceptance Hardening Report

Narrow, authorized hardening pass against the four Atlas QC findings on the **accepted**
H-014A foundation. This is H-014A.1 only. **No** H-014B, LiDAR, 3D editor, object-storage
retrieval, signed uploads, Passport writes, publication authority, new routes, or frontend
navigation changes. Local-only. Not production-ready.

## Lineage
- Accepted H-014A commit (must remain ancestor): `0bf8e85` — confirmed ancestor of HEAD.
- `5142c0f` — confirmed ancestor.
- Branch: `copilot/tcc-1-update-documentation`.

## Preserved reconciliation facts (do not rewrite history)
- Accepted H-014A diff (vs `5142c0f`) was **20 files / +1061 / −24**.
- Before this patch: **15 audit event types emitted / 17 defined** (`A_FRAME_SUPERSEDED`,
  `A_TRUTH_PROMOTION_REJECTED` were defined-but-unused).
- H-014A was ACCEPTED WITH NON-BLOCKING DEBT; this pass closes that debt.

## Debt / limitations table
| Finding | Status after H-014A.1 | Evidence |
|---|---|---|
| **QC-1** property-existence disclosure (403 vs 404) | **RESOLVED** | Real-property nonexistent AND existing-but-unauthorized now return an identical `404 {error_code:"NOT_FOUND","Resource not found or not accessible."}`; applied to subordinate objects (scan/frame/artifact/existing/design) via `not_found_nondisclosure()`. Reference-room synthetic (public) id intentionally keeps `403`. Tests: `TestPropertyNonDisclosure`. |
| **QC-2** client storage-reference not prefix-bound | **RESOLVED** | `validate_storage_reference(value, *, tenant_id, property_id)` now requires the exact server-derived `tenant/{tenant}/property/{property}/reality/` prefix and rejects foreign tenant/property, URL/signed-URL, absolute path, traversal, repeated slash, dot segment, percent/backslash encoding, fragment, whitespace, case tricks, and embedded-later prefixes. Default stays server-generated. Tests: `TestStorageReferenceAttackMatrix`, `TestStorageReferenceValidation`. |
| **QC-3** reference-room view non-determinism | **RESOLVED** | `assemble_view` assembles ONLY from the governed fixture id set (`build_reference_records()` ids), preserving fixture ordering; unrelated same-property dev/test records no longer leak in. Live view now returns exactly 2 coordinate frames / 12 entities. Tests: `TestReferenceRoomViewIsolation`. |
| **QC-4** truth-promotion rejection not audited | **RESOLVED** | `create_entity` emits `REALITY_TRUTH_PROMOTION_REJECTED` (domain=reality, tenant/property/actor bound, sanitized) exactly once on denial; audit is best-effort so a persistence failure still returns the 403 (never converts to success). Tests: `TestTruthPromotionRejectionAudit`, `TestTruthPromotionAuditFailureUnit`. |

## Files changed (this pass, vs `0bf8e85`)
- `backend/reality/artifact_service.py` — QC-2 prefix validation + `authorized_storage_prefix`; uniform not-found.
- `backend/reality/authz.py` — QC-1 `not_found_nondisclosure()`; real-property denial → uniform 404.
- `backend/reality/router.py` — QC-1 uniform not-found across 8 object handlers.
- `backend/reality/fixtures.py` — QC-3 id-based `assemble_view`.
- `backend/reality/spatial_service.py` — QC-4 audited, fail-closed truth-promotion rejection.
- `backend/tests/test_h014a_reality.py` — new/updated QC-1..QC-4 tests.
- docs + PRD + test_result updates.

## Validation (reproduced)
- `pytest tests/test_h014a_reality.py` → **111 passed**.
- H-013 security + publication + http-gates → **20 passed**.
- `pytest tests/ -rs` → **221 passed, 1 skipped** (`test_design_studio.py:204` live-Gemini render, `RUN_RENDER_TEST=1`, unrelated), 0 failed.
- Route enumeration → **17** reality routes (no new route).
- Frontend regression (testing-agent, `test_reports/iteration_5.json`) → **100%**; read-only; QC-3 shows exactly 2 fixture frames; artifact storage masked; Home Steward loads.
- Measured coverage (coverage.py 7.15.2, `--branch`, server subprocess + in-process unit, combined): reality package **78%** total (line+branch); `artifact_service` 91%, `authz` 68% (up from 39%), `fixtures` 100%.
- Write isolation re-confirmed: reality writes ONLY to the six `reality_*` collections + `db.audit_events`; **zero** writes to `properties` / `passport` / `users` / publication authority.

## Investigated / benign disclosures
- `entities[*].geometry_reference` = `fixture://rf-ent-…` in the reference-room response is a
  **fixture-namespaced geometry pointer** (carries only the entity's own public id) — NOT a
  governed object-storage key. Non-negotiable #8 (no raw storage keys) remains intact; the
  artifact `storage_object_reference` is masked to `<governed-object-store-reference>`.
- Cosmetic (unchanged, out of scope): Foundation screen renders `6.1 m` vs spec `6.10 m`
  (numeric equality holds); UI shows only the PROPERTY_FRAME of the 2 fixture frames.

## Honest classification
- H-014A.1 implementation complete **locally**.
- Awaiting independent Atlas QC.
- **Not production-ready** (foundation milestone; no object retrieval, no LiDAR, no 3D editor,
  no Passport write path).
- H-014B not authorized. No merge, no push, no remote, no deployment.
