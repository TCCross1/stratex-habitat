# H-014A — Coordinate Frame Implementation

Collection: `reality_coordinate_frames` (`enums.C_FRAMES`).
Source: `backend/reality/coordinate_service.py`.

## One property coordinate frame with PLANNING tolerance
Metric (`METRIC_M`), right-handed axis convention `X_EAST_Y_NORTH_Z_UP`. Default tolerance is
`PLANNING` — never survey-grade unless explicitly proven. Frames form a tree
(`parent_frame_id`) with cycle detection (`_would_cycle`).

## Frame types & origin states (`enums.py`)
- **`FRAME_TYPES`** = PROPERTY_FRAME, BUILDING_FRAME, LEVEL_FRAME, ROOM_FRAME, SCAN_LOCAL_FRAME,
  DRONE_LOCAL_FRAME, MODEL_LOCAL_FRAME, DESIGN_LOCAL_FRAME.
- **`ORIGIN_STATES`** = PROVISIONAL, CONTROL_POINT_ALIGNED, EXTERIOR_MODEL_ALIGNED,
  PROFESSIONALLY_ALIGNED, SUPERSEDED.
- **`TOLERANCE_CLASSES`** = VISUALIZATION, PLANNING, FIELD_REVIEW, SURVEY_GRADE.

## Transform validation (`validate_transform`) — pure, unit-tested
A transform must be a homogeneous 4×4:
- exactly 4 rows × 4 columns → else `INVALID_MATRIX`;
- every entry numeric (bools rejected) and **finite** → else `NON_FINITE_MATRIX`
  (rejects `inf`, `-inf`, `nan` — see `H014A_TEST_AND_COVERAGE_REPORT.md` Phase 3);
- last row exactly `[0,0,0,1]` → else `INVALID_HOMOGENEOUS_ROW`.

`IDENTITY_4X4` is the canonical identity.

## Transform default (Phase-2/targeted-correction fix)
`create_frame` uses **explicit `None`-only** fallback:
```
transform_to_parent = body.get("transform_to_parent")
if transform_to_parent is None:
    transform_to_parent = IDENTITY_4X4   # omitted/null → identity
# an explicitly supplied [] / malformed / non-finite matrix is preserved and
# rejected by validate_transform (no silent substitution to identity)
```
Same for `transform_to_property`. This is intentionally NOT `value or default` (which would also
swallow invalid falsy input such as `[]`).

## Endpoints
- `POST /properties/{property_id}/coordinate-frames` (201) — validates parent existence + cycles.
- `GET /properties/{property_id}/coordinate-frames` — list.
- `GET /coordinate-frames/{coordinate_frame_id}` — fetch (property-authorized).

## Governance
Every frame is written with `authoritative: false`, `validation_state: "VALIDATED"`,
`confidence: "LOW"` by default, and an audit event `REALITY_COORDINATE_FRAME_CREATED`.
