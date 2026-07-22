# H-014A — Database & Migration

Source: `backend/reality/indexes.py`. Invoked from the FastAPI startup path in
`backend/server.py` (`init_reality_indexes(db)`), idempotent (safe to re-run).

## Collections (all new, additive — no existing collection altered)
| Collection | Constant |
|---|---|
| `reality_spatial_entities` | `C_SPATIAL` |
| `reality_coordinate_frames` | `C_FRAMES` |
| `reality_scan_sessions` | `C_SCANS` |
| `reality_artifact_manifests` | `C_ARTIFACTS` |
| `reality_existing_model_versions` | `C_EXISTING` |
| `reality_design_model_versions` | `C_DESIGN` |

Audit events reuse the existing `db.audit_events` collection with a `domain: "reality"`
discriminator (no schema change to H-013 audit).

## Indexes created (idempotent `create_index` with stable names)
- **Spatial:** `ux_spatial_id` (unique), `ix_spatial_tenant_prop`, `ix_spatial_tenant_prop_type`,
  `ix_spatial_parent`, `ix_spatial_frame`, `ix_spatial_passport`.
- **Frames:** `ux_frame_id` (unique), `ix_frame_tenant_prop`, `ix_frame_parent`, `ix_frame_superseded`.
- **Scans:** `ux_scan_id` (unique), `ix_scan_tenant_prop`, `ix_scan_state`, `ix_scan_updated`,
  `ix_scan_expires`, `ix_scan_idempotency`.
- **Artifacts:** `ux_artifact_id` (unique), `ix_artifact_tenant_prop`, `ix_artifact_scan`,
  `ix_artifact_model`, `ix_artifact_checksum`, `ix_artifact_type`.
- **Existing models:** `ux_existing_id` (unique), `ix_existing_tenant_prop`, `ix_existing_state`,
  `ix_existing_prev`.
- **Design models:** `ux_design_id` (unique), `ix_design_tenant_prop`, `ix_design_base`,
  `ix_design_state`.

## Migration posture (honest)
- Indexes are **ensured at application startup**, not via a separate migration runner. Startup log
  confirms: `habitat.reality.indexes - INFO - Reality Studio indexes ensured.`
- No destructive migration, no backfill, no production migration executed.
- Unique `id` indexes support the deterministic reference-room idempotent upsert
  (`$setOnInsert`), which relies on stable fixture ids.
- Index creation is wrapped in try/except and logs (never blocks startup); disclosed as a
  best-effort ensure rather than a gated migration.
