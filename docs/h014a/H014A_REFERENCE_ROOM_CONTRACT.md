# H-014A — Deterministic Reference-Room Contract

Source: `backend/reality/fixtures.py`. Synthetic property `ref-property-h014a`
(`authz.REF_PROPERTY_ID`). Fixture version `1.0.0`.

## Purpose
A fully deterministic, **explicitly non-authoritative** sample room so the backend contract and
the read-only frontend screen can be validated without any real capture. It is a development/test
fixture — **NOT** canonical Property Passport truth.

## Determinism guarantees (unit-tested)
`build_reference_records()` is pure (no DB, no env, fixed timestamp `2026-01-01T00:00:00Z`):
- `build_reference_records() == build_reference_records()` (byte-stable).
- Every record `authoritative: false`; every entity
  `source_classification == "DETERMINISTIC_REFERENCE_FIXTURE"`.
- Exactly **12** spatial entities; **2** coordinate frames (PROPERTY + ROOM); **1** artifact
  (FLOOR_PLAN); **1** existing-model version (`DRAFT_CANDIDATE`).

## Fixed geometry (meters)
- width 4.88 (X-east), length 6.10 (Y-north), height 2.74 (Z-up) → floor area **29.768 m²**.
- Entities: 1 ROOM, 4 WALL (N/E/S/W), FLOOR, CEILING (`ESTIMATED_EXISTING`), 3 OPENING
  (window/door/adjoining), 1 WINDOW, 1 DOOR.
- `unknowns`: "Concealed wall structure", "Ceiling cavity systems", "Sub-floor condition"
  (recorded as UNKNOWN — never fabricated).

## Governance / fail-closed
- `assert_fixtures_enabled()` delegates to `fixture_provider.require_fixtures(...)`; in production
  this raises `FixtureDisabledError`, and the router returns **403 `FIXTURES_DISABLED`** for both
  bootstrap and view.
- `bootstrap(db, user)` is **idempotent**: deterministic IDs + `$setOnInsert` upsert; re-running
  never duplicates (test asserts count stays 12). Accepted records are never mutated.
- Fixture artifact storage reference uses the governed shape
  `fixture://tenant/{tenant}/property/{ref}/reality/{artifact}` and is still masked to the safe
  token in the public view.

## Assembled read-only view (`assemble_view`)
Returns `authoritative:false`, environment mode + fixtures_enabled + non-authoritative notice,
dimensions, coordinate frames, entity counts by type, truth-classification counts, unknowns,
`artifact_manifest` (public masked view), and `existing_model_version`.

## Endpoints
- `POST /development/reference-room/bootstrap`
- `GET /development/reference-room`
Both require property authorization for `ref-property-h014a` (demo homeowner or privileged roles).
