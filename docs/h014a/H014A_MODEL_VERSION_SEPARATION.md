# H-014A — Existing / Design Model Version Separation

Source: `backend/reality/model_version_service.py`.
Collections: `reality_existing_model_versions` (`C_EXISTING`),
`reality_design_model_versions` (`C_DESIGN`).

## Strict separation (core H-014 constitution)
Immutable **existing** reality is kept strictly separate from **design** proposals. A design
version can never overwrite an existing-model record; it only *references* an ACCEPTED existing
base and layers proposed deltas.

## Existing-model versions
- States (`EM_LEGAL_TRANSITIONS`): `DRAFT_CANDIDATE` → `QUALITY_REVIEW` → `ACCEPTED`;
  `→ REJECTED` from draft/review; `ACCEPTED → SUPERSEDED` only.
- **Immutability:** on `ACCEPTED`, the record is stamped `immutable: true`, `accepted_at`,
  `accepted_by`. Any further transition except `SUPERSEDED` returns `MODEL_IMMUTABLE` (409).
  Corrections require a **new** version (`previous_version_id`).
- Only real existing geometry may enter a snapshot: proposed-only entity types or `PROPOSED`
  existence → `PROPOSED_IN_EXISTING` (422); each referenced entity is truth-guarded via
  `assert_truth_promotion_allowed`.
- `content_hash` = SHA-256 over sorted(entity_ids) + frame_version + sorted(artifact_ids)
  (order-independent, deterministic — unit-tested).

## Design-model versions
- Requires `base_existing_model_version_id`:
  - missing key → `MISSING_BASE_MODEL` / not found → `BASE_MODEL_NOT_FOUND` (422);
  - base not ACCEPTED → `BASE_MODEL_NOT_ACCEPTED` (409).
- Inline `proposed_entities` must be design truth classes (`PROPOSED_DESIGN`, `AI_SUGGESTED_DESIGN`)
  and are truth-guarded; otherwise `INVALID_DESIGN_TRUTH` (422).
- States: `DRAFT`, `ALTERNATIVES_REVIEW`, `SUPERSEDED`.

## Nullable defaults (Phase 2, explicit `None` checks)
- Existing: `spatial_entity_ids`, `source_scan_session_ids`, `artifact_ids`, `unknown_areas` → `[]`;
  `truth_summary`, `quality_summary` → `{}`; omitted/null all resolve to the empty default.
- Design: `proposed_entities` → `[]` (a null value previously risked iterating `None`);
  `deltas` → `{"added":[],"modified":[],"removed":[]}`.
Explicit `is None` checks preserve any genuinely supplied value.

## Endpoints & audit
`POST /properties/{id}/existing-models`, `POST /existing-models/{id}/transition`,
`GET /existing-models/{id}`, `POST /properties/{id}/design-models`, `GET /design-models/{id}`.
Audit: `REALITY_EXISTING_MODEL_CREATED|ACCEPTED|REJECTED|SUPERSEDED`, `REALITY_DESIGN_MODEL_CREATED`.
