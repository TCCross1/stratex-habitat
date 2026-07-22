# H-014A — Implementation Reconnaissance

**Mission:** Turn the accepted H-014 architecture specification into a working, minimal,
governed **shared spatial foundation** for Reality Studio — backend data model + deterministic
reference-room contract + a read-only frontend screen. **Not** a 3D editor, **not** real LiDAR
capture, **no** unapproved SDKs.

## Scope actually implemented
- Backend module `backend/reality/` mounted at `/api/reality/v1`.
- Six governed collections: spatial entities, coordinate frames, scan sessions, artifact
  manifests, existing-model versions, design-model versions.
- One deterministic, explicitly **non-authoritative** reference room (dev/test only, fails closed
  in production).
- One read-only React screen `frontend/src/pages/RealityStudioFoundation.js` (`/reality-foundation`).

## Reuse of accepted H-013 baseline (not replaced)
- **Auth + DI:** `steward.get_steward_user` / `steward.get_db` (tenant-restricted homeowner + JWT).
- **Fixture governance:** `fixture_provider.require_fixtures` (env-gated, production 409/fail-closed).
- **Audit:** reuses `db.audit_events` collection with a `domain: "reality"` discriminator.
- **Object storage posture:** manifests store metadata + references only; binary lives in governed
  object storage; no public/raw URLs minted.

## Module map (`backend/reality/`)
| File | Responsibility |
|---|---|
| `enums.py` | Controlled vocabularies, collections, legal transition maps, truth taxonomy |
| `authz.py` | Tenant/property authorization, truth-promotion guard, `server_tenant_id()` |
| `audit_service.py` | Sanitized immutable audit events (prohibited-key stripping) |
| `coordinate_service.py` | 4×4 transform validation + coordinate-frame records |
| `spatial_service.py` | Spatial entity records + hierarchy/relationship validation |
| `scan_session_service.py` | Governed scan-session lifecycle (state machine + idempotency + OCC) |
| `artifact_service.py` | Immutable artifact manifests, checksum + storage-reference validation |
| `model_version_service.py` | Separated existing/design model versions + immutability |
| `fixtures.py` | Deterministic reference room (non-authoritative, idempotent bootstrap) |
| `indexes.py` | Idempotent index creation for all six collections |
| `schemas.py` | Pydantic request schemas |
| `router.py` | 17 versioned endpoints under `/api/reality/v1` |

## Current order (Final Closure) — what changed
1. **Phase 1** ownership-safe artifact default storage reference.
2. **Phase 2** nullable-default (`None` vs `dict.get(key, fallback)`) sweep across all reality services.
3. **Phase 3** non-finite transform validation + malformed-JSON safe rejection.
4. **Phase 4** this documentation set.
5. **Phase 5/6** full validation + measured coverage.

## Baseline / lineage
- Accepted targeted-correction commit: `5142c0f` (nullable-field defaults, explicit `None` checks).
- Closure-order starting HEAD: `408e627` (platform auto-commit atop `5142c0f`).
- Branch: `copilot/tcc-1-update-documentation`. No merge to main. No Save-to-GitHub.
