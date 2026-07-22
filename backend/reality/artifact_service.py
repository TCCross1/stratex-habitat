"""Immutable spatial artifact manifests + lineage (Phase 8).

MongoDB stores manifests/metadata/checksums/lineage/references ONLY. Binary
payloads live in governed object storage. No public permanent URLs are minted.
"""
import re
import uuid
from datetime import datetime, timezone

from . import enums
from .authz import structured, server_tenant_id
from .audit_service import write_event

_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
DEFAULT_CONTENT_TYPE = "application/octet-stream"


def governed_storage_reference(tenant_id: str, property_id: str, artifact_id: str) -> str:
    """Ownership-safe default object-store key derived ONLY from the authenticated
    tenant, the authorized property, and the server-generated artifact id. Never a
    URL, credential, signed URL, public path, or client-supplied override."""
    return f"tenant/{tenant_id}/property/{property_id}/reality/{artifact_id}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_checksum(value: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.match(value.lower()):
        raise structured(422, "INVALID_CHECKSUM", "checksum_sha256 must be 64 lowercase hex chars.")


def validate_storage_reference(value: str) -> None:
    """A client-supplied governed storage reference must be a safe, non-empty,
    tenant-scoped storage key — never blank, a URL, an absolute path, a signed
    reference, or a path-traversal string. Prevents silent fallback on bad input
    and blocks leaking unrestricted object-storage locations."""
    if not isinstance(value, str) or not value.strip():
        raise structured(422, "INVALID_STORAGE_REFERENCE",
                         "storage_object_reference must be a non-empty governed reference.")
    v = value.strip()
    if "://" in v or v.startswith("/") or "?" in v or ".." in v or any(ch.isspace() for ch in v):
        raise structured(422, "INVALID_STORAGE_REFERENCE",
                         "storage_object_reference must be a governed storage key, "
                         "not a URL, absolute path, or signed reference.")


def build_manifest_record(*, tenant_id, property_id, artifact_type, storage_object_reference,
                          content_type, file_size, checksum_sha256, correlation_id,
                          scan_session_id=None, model_version_id=None, source_artifact_ids=None,
                          derivation=None, processor=None, truth_classification=enums.UNKNOWN,
                          access_classification=None, retention_classification="RAW_LONG_TERM",
                          artifact_id=None):
    if artifact_type not in enums.ARTIFACT_TYPES:
        raise structured(422, "INVALID_ARTIFACT_TYPE", f"Unknown artifact_type '{artifact_type}'.")
    validate_checksum(checksum_sha256)
    if truth_classification not in enums.TRUTH_CLASSES:
        raise structured(422, "INVALID_TRUTH_CLASS", f"Unknown truth_classification '{truth_classification}'.")
    is_raw = artifact_type in enums.RAW_ARTIFACT_TYPES
    if access_classification is None:
        access_classification = "RESTRICTED_IMAGERY" if artifact_type in enums.RESTRICTED_IMAGERY_TYPES else "HOMEOWNER"
    now = _now_iso()
    return {
        "id": artifact_id or f"rf-art-{uuid.uuid4()}",
        "artifact_id": artifact_id or None,  # mirror set by caller
        "tenant_id": tenant_id,
        "property_id": property_id,
        "scan_session_id": scan_session_id,
        "model_version_id": model_version_id,
        "artifact_type": artifact_type,
        "storage_provider": "emergent_object_store",
        "storage_object_reference": storage_object_reference,  # path/key, NOT a public URL
        "content_type": content_type,
        "file_size": file_size,
        "checksum_sha256": checksum_sha256.lower(),
        "immutability": "IMMUTABLE_RAW" if is_raw else "DERIVED",
        "source_artifact_ids": source_artifact_ids or [],
        "derivation": derivation,
        "processor": processor,
        "processing_status": "READY",
        "validation_status": "VALID",
        "truth_classification": truth_classification,
        "access_classification": access_classification,
        "encryption_state": "ENCRYPTED_AT_REST",
        "retention_classification": retention_classification,
        "signed_access_required": True,
        "created_at": now,
        "version": 1,
        "correlation_id": correlation_id,
        "superseded_by": None,
        "authoritative": False,
    }


def public_view(manifest: dict) -> dict:
    """Metadata-only view. Never exposes a resolvable/raw storage object."""
    m = dict(manifest)
    m.pop("_id", None)
    ref = m.get("storage_object_reference")
    m["storage_object_reference_present"] = bool(ref)
    # Do not leak the raw storage key/path to clients; signed access is a separate, authorized flow.
    m["storage_object_reference"] = "<governed-object-store-reference>" if ref else None
    return m


async def create_manifest(db, user, *, scan_session_id, body: dict, correlation_id):
    session = await db[enums.C_SCANS].find_one({"id": scan_session_id}, {"_id": 0})
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Scan session not found")
    # Tenant is ALWAYS server-derived; property is the AUTHORIZED scan-session property.
    # Neither is taken from the client body (client overrides are ignored/rejected).
    tenant_id = server_tenant_id()
    property_id = session["property_id"]
    if session.get("tenant_id") != tenant_id:
        raise structured(403, "SCAN_ACCESS_DENIED", "Cross-tenant scan session.")

    source_ids = body.get("source_artifact_ids") or []
    for sid in source_ids:
        src = await db[enums.C_ARTIFACTS].find_one({"id": sid}, {"_id": 0})
        if not src:
            raise structured(422, "SOURCE_ARTIFACT_NOT_FOUND", f"source artifact {sid} not found.")
        if src.get("property_id") != property_id:
            raise structured(422, "CROSS_PROPERTY_ARTIFACT", "source artifact belongs to a different property.")

    artifact_id = f"rf-art-{uuid.uuid4()}"
    # Explicit None-only fallbacks (omitted/null → governed default; never silent on bad input).
    storage_object_reference = body.get("storage_object_reference")
    if storage_object_reference is None:
        storage_object_reference = governed_storage_reference(tenant_id, property_id, artifact_id)
    else:
        validate_storage_reference(storage_object_reference)
    content_type = body.get("content_type")
    if content_type is None:
        content_type = DEFAULT_CONTENT_TYPE
    file_size = body.get("file_size")
    if file_size is None:
        file_size = 0
    rec = build_manifest_record(
        tenant_id=tenant_id, property_id=property_id, artifact_type=body["artifact_type"],
        storage_object_reference=storage_object_reference,
        content_type=content_type,
        file_size=file_size, checksum_sha256=body["checksum_sha256"],
        correlation_id=correlation_id, scan_session_id=scan_session_id,
        model_version_id=body.get("model_version_id"), source_artifact_ids=source_ids,
        derivation=body.get("derivation"), processor=body.get("processor"),
        truth_classification=body.get("truth_classification", enums.UNKNOWN),
        artifact_id=artifact_id)
    rec["artifact_id"] = artifact_id
    await db[enums.C_ARTIFACTS].insert_one(dict(rec))
    await write_event(db, enums.A_ARTIFACT_CREATED, user, property_id=property_id,
                      correlation_id=correlation_id,
                      entity_refs={"artifact_id": artifact_id, "scan_session_id": scan_session_id},
                      extra={"artifact_type": rec["artifact_type"], "immutability": rec["immutability"]})
    return public_view(rec)
