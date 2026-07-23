# H-014C.1 — Governed Reality Model Contract & Read-Only Viewers

## Summary

Habitat exposes a **read-only** existing-room reality-model contract, a
Passport→Habitat projection adapter, and homeowner-safe 2D/3D viewers with a
provenance panel. This wave does **not** perform physical LiDAR validation,
does **not** fabricate room geometry, and does **not** write Property Passport
truth.

> The Central Kentucky Demonstration Home is demonstration/sample-only data.
> It is not a physically validated property scan or approved Passport model.

## Architecture boundary

- **Core** performs the work (outside this repository).
- **Passport** remembers the home (outside this repository).
- **Habitat** sustains the relationship and may consume only authorized,
  versioned, homeowner-safe, **read-only** Passport projections.

Habitat must never become a second canonical property database, approve
geometry, rewrite accepted geometry, or promote demonstration / draft data
into verified truth.

Existing, proposed, and as-built geometry remain separate version sets.
**H-014C.1 concerns EXISTING geometry display only.**

## Reality-model contract

Authoritative Habitat-side contract modules:

- `frontend/src/propertyVisualization/reality/realityModelContract.js`
- `frontend/src/propertyVisualization/reality/normalizeRealityModel.js`

Identity fields: `property_id`, `room_id`, `model_id`, `projection_id`,
`source_capture_id`, `source_mission_id`, `source_passport_version`,
`schema_version`, `model_version`.

Truth / provenance: `data_origin`, `truth_status`, `confidence_state`,
`lifecycle_state`, timestamps, checksum, manifest reference.

Geometry availability flags and governed refs for floor plan / 3D / thumbnail /
preview / manifest. Quality fields are never invented.

### Lifecycle states

`awaiting_scan` · `capture_in_progress` · `draft_candidate` · `quality_review` ·
`needs_recapture` · `professional_review` · `approved_projection` ·
`superseded` · `unavailable` · `demo_sample`

### Truth-state rules

- Approved display requires: lifecycle `approved_projection`, truth
  `approved`/`verified`, non-demo origin, valid `projection_id`,
  `source_passport_version`, `schema_version`, and `property_id`.
- Model URL alone never implies approval.
- Demo / sample_only / draft cannot become approved.
- Proposed geometry is rejected as existing.
- As-built without approved projection is rejected as a silent substitute.
- Unknown values remain unknown (including dimension fields).

Normalization returns: `VALID` | `VALID_WITH_WARNINGS` | `UNAVAILABLE` | `REJECTED`.
Rejected data yields a controlled UI state (no crash). Source payloads are never
mutated.

## Selection priority

Implemented in `selectVisualizationSource.js`:

1. Current authorized approved Passport projection
2. Current draft candidate (explicitly draft)
3. Explicit Central Kentucky demonstration configuration
4. Awaiting-scan
5. Unavailable / error

Hard rules: demo never overrides approved; stale approved never overrides newer
approved (`preferNewerApproved`); draft never appears approved; proposed never
appears as existing; real-property network failure never silently becomes demo;
generic imagery never becomes verified property truth.

## Passport projection adapter

`passportProjectionAdapter.js` — Habitat API client only (cookie auth):

- Read: `GET /api/properties/{pid}/reality-model`
- No write / patch / approve / publish / promote
- No MongoDB / Passport DB / Core credentials in the frontend
- Strips signed URL query strings and internal fields
- Deterministically testable without live Stratex-2

## Backend read support

`GET /api/properties/{pid}/reality-model` in `backend/server.py`:

- Authenticated; tenant / property authorization
- Demo → `demo_sample` / `sample_only` (no fabricated walls/meshes)
- Non-demo → controlled `awaiting_scan` until an approved projection exists
- No raw storage secrets; no promote / write route
- Does **not** create a Habitat canonical geometry collection
- Does **not** modify Property Passport

A separate Reality capture backend (`/api/reality/v1`) remains for H-014A/B
development fixtures and is not a second homeowner twin authority.

## 2D viewer

`RoomFloorPlan2D.js` — SVG, read-only:

- Walls / openings / room names / dimensions only when supplied
- Unknown dimensions labeled unknown
- Pan / zoom / reset; pointer + keyboard; mobile-safe overflow hidden
- Lifecycle empty states: awaiting, draft, review, needs-recapture, approved,
  demo/sample, unavailable
- No drag handles, wall editing, resizing, openings editing, design tools

Synthetic geometry may appear only in isolated tests/fixtures marked
`sample_only` / `not_property_truth` / `not_passport_approved`.

## 3D viewer

`RoomModel3D.js` — **PARTIAL** truthful surface:

- No Three.js / heavy renderer dependency in this repository
- Governed model reference display when a supported ref exists
- States: loading/no-model, unsupported format, load failure, WebGL unavailable
- Orbit / zoom / reset controls reserved (disabled until a renderer mounts)
- Reduced-motion support; no editing tools
- When absent: **“3D model awaiting an approved property scan.”**

### Supported model formats

Documented: `glb`, `gltf`, `usdz`, `obj` (`SUPPORTED_3D_FORMATS`).

## Provenance panel

`ModelProvenancePanel.js` — homeowner-safe labels:

`DEMO / SAMPLE ONLY` · `DRAFT CANDIDATE` · `AWAITING REVIEW` ·
`NEEDS RECAPTURE` · `APPROVED PROPERTY MODEL` · `SUPERSEDED` · `UNAVAILABLE`

Hides internal reviewer notes, raw object keys, signed URL parameters, private
storage paths, contractor-internal fields, and unapproved employee identities.

## Demonstration behavior

Sole Habitat demonstration identity:

| Field | Value |
|-------|-------|
| name | Central Kentucky Demonstration Home |
| location | Lexington, Kentucky |
| property_type | detached_single_family |
| visualization_profile | central-kentucky-demo-home |
| dataOrigin | demo |
| truthStatus | sample_only |
| confidenceState | demo |
| is_demo_fixture | true |

Not represented as physically scanned, LiDAR-derived, verified, approved,
Passport-canonical, dimensionally measured, or thermally analyzed.

## Authentication initialization (Phase 10)

Investigation conclusion: **no deterministic auth race proven.**

Habitat uses HttpOnly cookie sessions (`withCredentials`). `AuthContext` sets
`user` to `null` while `/auth/me` settles, `false` when anonymous, or the user
object when authenticated. `AppDataContext` enables protected queries only when
`!!user`. Protected routes show a loading splash while `user === null`.

A transient 401 on anonymous `/auth/me` during smoke is expected, not evidence
of protected requests firing with an empty bearer. No artificial sleeps, hard-
coded tokens, broad retries, suppressed 401s, or auth bypasses were added.
`ExistingRoomTwinPanel` additionally waits for `user !== null` before fetching.

## Physical-validation dependency

Physical LiDAR / RoomPlan device capture and approved Passport geometry swap
remain **UNEXECUTED**. Future approved projections may be returned from the
same `/reality-model` read path without Habitat gaining write authority.

## Test commands

```bash
# Frontend
cd frontend && CI=true npm test -- --watchAll=false --ci --forceExit
cd frontend && CI=true npm run build

# Backend (requires Mongo + running uvicorn for HTTP suite)
cd backend && python -m pytest tests/test_h014c1_reality_model.py -q
cd backend && python -m pytest -q
```

## Current limitations

- No authored GLB for Central Kentucky (slot reserved only).
- 3D viewer is a governed placeholder surface (no WebGL mesh renderer).
- Non-demo properties return `awaiting_scan` until Core/Passport supply an
  authorized projection.
- Steward quantity fixtures remain planning/demo samples — not measured room
  truth for H-014C.1.

## Frontend CI

`.github/workflows/frontend-quality.yml` — `npm ci`, Jest non-watch, `CI=true`
production build. No live production backend. No secret-dependent steps.
Registry: public npm via GitHub Actions.
