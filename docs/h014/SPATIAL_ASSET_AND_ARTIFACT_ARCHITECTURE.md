# SPATIAL ASSET & ARTIFACT ARCHITECTURE (Phase 13)

Version 1.0.0 · Specification only. Defines how large spatial artifacts are stored, referenced,
versioned, and secured. Spatial nodes (Phase 3) hold **references** to artifacts — never inline
binary blobs. Storage uses the existing Emergent-managed object store abstraction + signed
retrieval; **no final storage vendor is hard-coded** beyond that existing abstraction.

---

## 1. Artifact catalogue
Raw LiDAR · raw RGB imagery · raw thermal imagery · point clouds · meshes · textures · orthomosaics ·
panoramas · floor plans · CAD exports · BIM-compatible exports · thumbnails · preview models ·
full-resolution models · derived measurements · design versions · report renders.

## 2. Artifact record (illustrative)
```jsonc
{
  "artifact_id": "art-<uuid>",
  "tenant_id":"…","property_id":"…","session_id":"scan-…|null",
  "kind": "RAW_LIDAR|RAW_RGB|RAW_THERMAL|POINTCLOUD|MESH|TEXTURE|ORTHOMOSAIC|PANORAMA|FLOORPLAN|
           CAD_EXPORT|BIM_EXPORT|THUMBNAIL|PREVIEW_MODEL|FULLRES_MODEL|MEASUREMENT|DESIGN_VERSION|REPORT_RENDER",
  "immutability": "IMMUTABLE_RAW | DERIVED",
  "derived_from": ["art-…"],            // lineage (empty for raw)
  "derivation": { "producer":"processing-x.y","params_ref":"…" },
  "checksum": { "algo":"sha256","value":"…" },
  "size_bytes": 123456789,
  "version": 1,
  "processing_status": "QUEUED|PROCESSING|READY|FAILED",
  "validation_status": "UNVALIDATED|VALID|INVALID",
  "truth_classification": "MEASURED_EXISTING|…",   // for geometry-bearing artifacts
  "storage": { "backend":"object-store","key":"…","encrypted":true },
  "access_classification": "HOMEOWNER|CONTRACTOR|PROFESSIONAL|INTERNAL|RESTRICTED_IMAGERY",
  "retention": { "policy":"RAW_LONG_TERM|DERIVED_REGENERABLE","expires_at":null },
  "signed_access": { "required": true, "ttl_seconds": 900 },
  "cache": { "cacheable": true, "scope":"private","max_age": 3600 },
  "created_at":"…","updated_at":"…","audit_refs":["evt-…"]
}
```

## 3. Immutability & lineage
- **Raw artifacts are immutable** (write-once, checksum-sealed). Reprocessing never overwrites raw.
- **Derived artifacts** record `derived_from` + `derivation` params → full lineage from raw → preview.
- Regenerable derived artifacts may be garbage-collected under retention; raw is retained per policy.

## 4. Integrity & versioning
- Every artifact carries a checksum; integrity verified on read. New processing outputs bump
  `version` and add lineage rather than mutating.

## 5. Access, encryption, signed access
- Encryption at rest + in transit; access gated by tenant + property authorization + role +
  `access_classification`. `RESTRICTED_IMAGERY` (interior RGB) requires elevated scope (Phase 19).
- Retrieval only via short-TTL **signed URLs**; no public/unsigned access to spatial artifacts.

## 6. Transfer, offline recovery, mobile
- **Large-file transfer:** chunked, resumable uploads/downloads; parallel parts; checksum per part.
- **Offline upload recovery:** captured artifacts queue locally and resume via `resume_token`
  (Phase 5) after interruption/connectivity loss.
- **Mobile preview optimization:** `PREVIEW_MODEL`/`THUMBNAIL` (decimated meshes, compressed
  textures) served first; `FULLRES_MODEL` streamed on demand.

## 7. Processing & validation status
- Artifacts expose explicit processing + validation status; failures are surfaced (no fabricated
  "ready" artifacts). Invalid artifacts are quarantined, not shown as truth.

## 8. Relationship to existing code
- Extends `server.py` object-storage `/upload` + signed retrieval and `db.files`. Introduces a
  `spatial_artifacts` collection (documented, not implemented). Vendor-neutral by design.
