# H-014A — Spatial Data Model

Collection: `reality_spatial_entities` (`enums.C_SPATIAL`).
Source: `backend/reality/spatial_service.py`, `backend/reality/enums.py`.

## One shared spatial graph
Interior / Exterior / Systems are **views** over ONE entity graph, never separate stores.
Each entity is tenant- and property-scoped and carries a mandatory truth classification.

## Record shape (authored by `build_entity_record`)
Key fields: `id` / `spatial_entity_id`, `tenant_id`, `property_id`, `building_id`,
`parent_entity_id`, `entity_type`, `label`, `coordinate_frame_id`, `geometry_type`,
`geometry_reference`, `geometry_version`, `truth_classification`, `source_classification`,
`confidence`, `units` (`METRIC_M`), `lifecycle_state`, `existing_state`
(`EXISTING|PROPOSED|COMPLETED`), `opening_ref`, `canonical_passport_reference`, `provenance`,
`unknowns[]`, `dimensions`, `access_classification`, `version`, timestamps,
`authoritative: false`.

## Controlled vocabularies (`enums.py`)
- **`ENTITY_TYPES`** — 25 types (PROPERTY … SITE_FEATURE).
- **`SURFACE_LIKE`** = {SURFACE, WALL, FLOOR, CEILING, EXTERIOR_ELEVATION, ROOF_PLANE}.
- **`OPENING_LIKE`** = {OPENING, DOOR, WINDOW}.
- **`PROPOSED_ONLY_TYPES`** = {DESIGN_ELEMENT, PROPOSED_ADDITION} (never EXISTING).
- **`GEOMETRY_TYPES`**, **`ACCESS_CLASSES`**, **`EXISTENCE_STATES`**.

## Hierarchy / relationship validation (`validate_entity_relationships`)
Pure, unit-tested. Enforces:
- `SELF_PARENT` — entity cannot parent itself.
- `PARENT_NOT_FOUND`, `CROSS_TENANT_RELATIONSHIP` (403), `CROSS_PROPERTY_RELATIONSHIP` (422).
- `ORPHAN_OPENING` — an `OPENING` must sit on a surface-like parent.
- `MISSING_OPENING_REF` / `OPENING_REF_NOT_FOUND` / `INVALID_OPENING_REF` — DOOR/WINDOW must
  reference a valid `OPENING`.
- `PROPOSED_IN_EXISTING` — proposed-only types cannot claim `EXISTING`.
- `ENTITY_CYCLE` — parent chain cycle detection (`_would_cycle`).

## Label default (Phase 2 fix)
`resolve_label(body)` — explicit `None`-only fallback: an omitted/null `label` defaults to
`entity_type`; an explicitly supplied value (including empty string) is preserved (no silent
fallback). Previously `body.get("label", entity_type)` returned `None` when the key was present
with value `None`.

## Truth authoring rules
`create_entity` calls `assert_truth_promotion_allowed(...)` before persisting, so a Habitat actor
cannot self-promote to a `RESTRICTED_TRUTH_CLASSES` value (see `H014A_SECURITY_AND_PRIVACY.md`).
