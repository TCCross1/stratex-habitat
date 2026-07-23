"""Idempotent index creation for Reality Studio collections (Phase 13)."""
import logging

from pymongo import ASCENDING

from . import enums

logger = logging.getLogger("habitat.reality.indexes")


async def init_reality_indexes(db):
    """Create indexes for all H-014A collections. Idempotent (safe to re-run)."""
    if db is None:
        return
    try:
        # Spatial entities
        await db[enums.C_SPATIAL].create_index([("id", ASCENDING)], unique=True, name="ux_spatial_id")
        await db[enums.C_SPATIAL].create_index([("tenant_id", ASCENDING), ("property_id", ASCENDING)],
                                               name="ix_spatial_tenant_prop")
        await db[enums.C_SPATIAL].create_index(
            [("tenant_id", ASCENDING), ("property_id", ASCENDING), ("entity_type", ASCENDING)],
            name="ix_spatial_tenant_prop_type")
        await db[enums.C_SPATIAL].create_index([("parent_entity_id", ASCENDING)], name="ix_spatial_parent")
        await db[enums.C_SPATIAL].create_index([("coordinate_frame_id", ASCENDING)], name="ix_spatial_frame")
        await db[enums.C_SPATIAL].create_index([("canonical_passport_reference", ASCENDING)],
                                               name="ix_spatial_passport")
        # Coordinate frames
        await db[enums.C_FRAMES].create_index([("id", ASCENDING)], unique=True, name="ux_frame_id")
        await db[enums.C_FRAMES].create_index([("tenant_id", ASCENDING), ("property_id", ASCENDING)],
                                              name="ix_frame_tenant_prop")
        await db[enums.C_FRAMES].create_index([("parent_frame_id", ASCENDING)], name="ix_frame_parent")
        await db[enums.C_FRAMES].create_index([("superseded_by", ASCENDING)], name="ix_frame_superseded")
        # Scan sessions
        await db[enums.C_SCANS].create_index([("id", ASCENDING)], unique=True, name="ux_scan_id")
        await db[enums.C_SCANS].create_index([("tenant_id", ASCENDING), ("property_id", ASCENDING)],
                                             name="ix_scan_tenant_prop")
        await db[enums.C_SCANS].create_index([("current_state", ASCENDING)], name="ix_scan_state")
        await db[enums.C_SCANS].create_index([("updated_at", ASCENDING)], name="ix_scan_updated")
        await db[enums.C_SCANS].create_index([("expires_at", ASCENDING)], name="ix_scan_expires")
        await db[enums.C_SCANS].create_index(
            [("tenant_id", ASCENDING), ("property_id", ASCENDING), ("create_idempotency_key", ASCENDING)],
            name="ix_scan_idempotency")
        # Artifact manifests
        await db[enums.C_ARTIFACTS].create_index([("id", ASCENDING)], unique=True, name="ux_artifact_id")
        await db[enums.C_ARTIFACTS].create_index([("tenant_id", ASCENDING), ("property_id", ASCENDING)],
                                                 name="ix_artifact_tenant_prop")
        await db[enums.C_ARTIFACTS].create_index([("scan_session_id", ASCENDING)], name="ix_artifact_scan")
        await db[enums.C_ARTIFACTS].create_index([("model_version_id", ASCENDING)], name="ix_artifact_model")
        await db[enums.C_ARTIFACTS].create_index([("checksum_sha256", ASCENDING)], name="ix_artifact_checksum")
        await db[enums.C_ARTIFACTS].create_index([("artifact_type", ASCENDING)], name="ix_artifact_type")
        # Existing model versions
        await db[enums.C_EXISTING].create_index([("id", ASCENDING)], unique=True, name="ux_existing_id")
        await db[enums.C_EXISTING].create_index([("tenant_id", ASCENDING), ("property_id", ASCENDING)],
                                                name="ix_existing_tenant_prop")
        await db[enums.C_EXISTING].create_index([("model_state", ASCENDING)], name="ix_existing_state")
        await db[enums.C_EXISTING].create_index([("previous_version_id", ASCENDING)], name="ix_existing_prev")
        # Design model versions
        await db[enums.C_DESIGN].create_index([("id", ASCENDING)], unique=True, name="ux_design_id")
        await db[enums.C_DESIGN].create_index([("tenant_id", ASCENDING), ("property_id", ASCENDING)],
                                              name="ix_design_tenant_prop")
        await db[enums.C_DESIGN].create_index([("base_existing_model_version_id", ASCENDING)],
                                              name="ix_design_base")
        await db[enums.C_DESIGN].create_index([("design_state", ASCENDING)], name="ix_design_state")
        # H-014B: resumable upload sessions + staged chunks
        await db[enums.C_UPLOAD_SESSIONS].create_index([("id", ASCENDING)], unique=True, name="ux_upload_id")
        await db[enums.C_UPLOAD_SESSIONS].create_index([("scan_session_id", ASCENDING)],
                                                       name="ix_upload_scan")
        await db[enums.C_UPLOAD_SESSIONS].create_index([("state", ASCENDING)], name="ix_upload_state")
        await db[enums.C_UPLOAD_SESSIONS].create_index([("expires_at", ASCENDING)], name="ix_upload_expires")
        await db[enums.C_UPLOAD_CHUNKS].create_index(
            [("upload_session_id", ASCENDING), ("index", ASCENDING)], unique=True, name="ux_chunk_session_index")
        logger.info("Reality Studio indexes ensured.")
    except Exception as e:  # pragma: no cover
        logger.error("Reality index init failed: %s", e)
