# H-014A — Artifact Manifest Implementation

Collection: `reality_artifact_manifests` (`enums.C_ARTIFACTS`).
Source: `backend/reality/artifact_service.py`.

## Metadata-only, binary lives in governed object storage
MongoDB stores **manifests / metadata / checksums / lineage / references ONLY**. Binary payloads
never enter Mongo (tests assert the stored doc has no `data`/`bytes`/`payload` keys). No public or
raw storage URL is ever minted; signed access is a separate authorized flow.

## Artifact types (`enums.py`)
`ARTIFACT_TYPES` (15): RAW_LIDAR, RAW_RGB, RAW_THERMAL, POINT_CLOUD, MESH, TEXTURE, ORTHOMOSAIC,
PANORAMA, FLOOR_PLAN, MODEL_PREVIEW, FULL_RESOLUTION_MODEL, DERIVED_MEASUREMENTS,
DESIGN_VERSION_EXPORT, REPORT_RENDER, OTHER_GOVERNED_ARTIFACT.
- `RAW_ARTIFACT_TYPES` → `immutability: IMMUTABLE_RAW`; others → `DERIVED`.
- `RESTRICTED_IMAGERY_TYPES` {RAW_RGB, RAW_THERMAL, PANORAMA} → `access_classification: RESTRICTED_IMAGERY`.

## Validation
- **`validate_checksum`** — `checksum_sha256` must be 64 lowercase hex chars → else
  `INVALID_CHECKSUM` (422).
- **`validate_storage_reference`** (Phase 1/2) — a *client-supplied* reference must be a safe,
  non-empty, tenant-scoped storage key. Rejects blank/whitespace, `://` (URL), leading `/`
  (absolute path), `?` (signed-URL query), `..` (traversal), or any whitespace →
  `INVALID_STORAGE_REFERENCE` (422). No silent fallback on bad input.

## Ownership-safe default storage reference (Phase 1)
`governed_storage_reference(tenant_id, property_id, artifact_id)` →
`tenant/{tenant_id}/property/{property_id}/reality/{artifact_id}` where:
- **tenant** = `authz.server_tenant_id()` (server-derived; client override ignored/rejected);
- **property** = the **authorized** scan session's `property_id` (never from the client body);
- **artifact_id** = server-generated (`rf-art-<uuid4>`).

Cross-tenant scan → `SCAN_ACCESS_DENIED` (403). Cross-property source-artifact lineage →
`CROSS_PROPERTY_ARTIFACT` (422).

## Nullable defaults (Phase 2, explicit `None` checks)
`storage_object_reference` → governed default; `content_type` → `application/octet-stream`;
`file_size` → `0`. Explicitly supplied values (incl. falsy like empty `content_type`) are
preserved; only `None` triggers the default.

## Public projection (`public_view`)
Never returns the raw storage key. `storage_object_reference` is masked to the literal token
`"<governed-object-store-reference>"` and `storage_object_reference_present: true` is set.
Tests assert the internal key does not appear anywhere in the public response body.

## Endpoints & audit
`POST /scan-sessions/{id}/artifacts` (201), `GET /artifacts/{artifact_id}`.
Audit: `REALITY_ARTIFACT_MANIFEST_CREATED`.
