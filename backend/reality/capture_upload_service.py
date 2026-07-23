"""Resumable, governed chunked upload of heavy capture artifacts (H-014B / H-014B.1).

Flow (client == iOS ResumableUploader):
  1. init_upload   -> create an upload session bound to tenant+property+scan.
  2. put_chunk     -> validate auth already done by router; validate index/size/
                      SHA-256; stream chunk bytes into governed object-storage
                      staging; persist METADATA ONLY in MongoDB
                      (`reality_upload_chunks`) with an opaque object reference.
  3. complete_upload -> require all chunks; ordered disk-backed assemble from
                      object storage; verify whole-file SHA-256; write ONE
                      immutable final object; mark staging for cleanup; never
                      load the complete artifact into MongoDB.
  4. abort_upload  -> mark session aborted; mark staging for cleanup; metadata
                      purge; idempotent on replay.

Governance: tenant is server-derived, property is the authorized scan-session
property (never taken from the client). The final object key is server-derived
`tenant/{tenant}/property/{property}/reality/{artifact_id}`. Checksum mismatch
is rejected (never silently accepted) and audited.

MongoDB stores metadata only — never binary chunk bytes or base64 copies.
API responses never expose bucket names, raw object keys, credentials, public
URLs, or signed URLs.
"""
import hashlib
import math
import uuid
from datetime import datetime, timezone, timedelta

from . import enums
from . import object_store
from .authz import structured, server_tenant_id, not_found_nondisclosure
from .audit_service import write_event
from .artifact_service import (build_manifest_record, public_view, validate_checksum,
                               governed_storage_reference)

# Fields that must NEVER appear on reality_upload_chunks documents.
_FORBIDDEN_BINARY_FIELDS = ("data", "data_b64", "bytes", "payload", "content",
                            "chunk_bytes", "binary", "base64")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _load_session(db, upload_session_id):
    up = await db[enums.C_UPLOAD_SESSIONS].find_one({"id": upload_session_id}, {"_id": 0})
    if not up:
        raise not_found_nondisclosure()
    return up


def _missing_indexes(received, total):
    got = set(received or [])
    return [i for i in range(total) if i not in got]


def _public_upload_view(up: dict) -> dict:
    """Strip any internal storage fields before returning upload session state."""
    out = dict(up)
    out.pop("_id", None)
    out.pop("storage_key", None)
    out.pop("_storage_key_internal", None)
    out.pop("signed_url", None)
    out.pop("public_url", None)
    out.pop("bucket", None)
    return out


def _chunk_metadata_doc(*, up: dict, index: int, size: int, sha256: str,
                        object_reference: str, etag, storage_key_internal: str,
                        now: str) -> dict:
    """Build a metadata-only chunk document. Never includes binary bytes."""
    return {
        "upload_session_id": up["id"],
        "tenant_id": up["tenant_id"],
        "property_id": up["property_id"],
        "scan_session_id": up["scan_session_id"],
        "artifact_id": up.get("artifact_id"),
        "index": index,
        "declared_size": size,
        "verified_size": size,
        "declared_checksum_sha256": sha256,
        "verified_checksum_sha256": sha256,
        "sha256": sha256,
        "size": size,
        "object_reference": object_reference,  # opaque; not a raw key
        "etag": etag,
        "receipt": etag,
        "upload_state": enums.UP_IN_PROGRESS,
        "retry_state": {"attempts": 0, "last_error": None},
        "ownership": {"tenant_id": up["tenant_id"], "property_id": up["property_id"]},
        "lineage": {
            "upload_session_id": up["id"],
            "scan_session_id": up["scan_session_id"],
            "correlation_id": up.get("correlation_id"),
        },
        "expires_at": up.get("expires_at"),
        "audit_refs": {"correlation_id": up.get("correlation_id")},
        # Internal only — never surfaced through API responses.
        "_storage_key_internal": storage_key_internal,
        "created_at": now,
        "updated_at": now,
    }


def assert_no_binary_fields(doc: dict):
    for field in _FORBIDDEN_BINARY_FIELDS:
        if field in doc and doc[field] is not None:
            raise RuntimeError(
                f"storage-boundary violation: chunk document must not contain '{field}'"
            )


async def init_upload(db, user, *, scan_session_id, body: dict, correlation_id):
    session = await db[enums.C_SCANS].find_one({"id": scan_session_id}, {"_id": 0})
    if not session:
        raise not_found_nondisclosure()
    tenant_id = server_tenant_id()
    if session.get("tenant_id") != tenant_id:
        raise structured(403, "SCAN_ACCESS_DENIED", "Cross-tenant scan session.")
    property_id = session["property_id"]

    artifact_type = body.get("artifact_type")
    if artifact_type not in enums.ARTIFACT_TYPES:
        raise structured(422, "INVALID_ARTIFACT_TYPE", f"Unknown artifact_type '{artifact_type}'.")
    checksum = body.get("checksum_sha256")
    validate_checksum(checksum)

    total_size = body.get("total_size")
    if not isinstance(total_size, int) or isinstance(total_size, bool) or total_size <= 0:
        raise structured(422, "INVALID_TOTAL_SIZE", "total_size must be a positive integer (bytes).")
    if total_size > enums.MAX_UPLOAD_BYTES:
        raise structured(413, "UPLOAD_TOO_LARGE",
                         f"total_size exceeds the governed cap ({enums.MAX_UPLOAD_BYTES} bytes).")
    chunk_size = body.get("chunk_size")
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size < enums.MIN_CHUNK_BYTES:
        raise structured(422, "INVALID_CHUNK_SIZE", "chunk_size must be a positive integer (bytes).")
    if chunk_size > enums.MAX_CHUNK_BYTES:
        raise structured(422, "CHUNK_SIZE_TOO_LARGE",
                         f"chunk_size exceeds the maximum staged chunk ({enums.MAX_CHUNK_BYTES} bytes).")
    total_chunks = math.ceil(total_size / chunk_size)
    if total_chunks > enums.MAX_TOTAL_CHUNKS:
        raise structured(422, "TOO_MANY_CHUNKS",
                         f"total_chunks {total_chunks} exceeds the cap {enums.MAX_TOTAL_CHUNKS}; use a larger chunk_size.")

    # Idempotent init: reuse an existing open session for the same idempotency key.
    key = body.get("idempotency_key")
    if key:
        existing = await db[enums.C_UPLOAD_SESSIONS].find_one(
            {"scan_session_id": scan_session_id, "create_idempotency_key": key}, {"_id": 0})
        if existing:
            existing["missing_indexes"] = _missing_indexes(existing.get("received_indexes"),
                                                           existing["total_chunks"])
            return _public_upload_view(existing)

    now = _now_iso()
    ttl_hours = 72
    up_id = f"rf-upload-{uuid.uuid4()}"
    rec = {
        "id": up_id, "upload_session_id": up_id,
        "tenant_id": tenant_id, "property_id": property_id,
        "scan_session_id": scan_session_id,
        "artifact_type": artifact_type,
        "content_type": body.get("content_type") or "application/octet-stream",
        "declared_checksum_sha256": checksum.lower(),
        "declared_size": total_size,
        "chunk_size": chunk_size,
        "total_chunks": total_chunks,
        "received_indexes": [],
        "bytes_received": 0,
        "state": enums.UP_INITIATED,
        "artifact_id": None,
        "truth_classification": body.get("truth_classification", enums.UNKNOWN),
        "error": None,
        "create_idempotency_key": key,
        "version": 1,
        "correlation_id": correlation_id,
        "created_at": now, "updated_at": now,
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat(),
        "authoritative": False,
        "staging_cleanup_marks": [],
    }
    await db[enums.C_UPLOAD_SESSIONS].insert_one(dict(rec))
    await write_event(db, enums.A_UPLOAD_INITIATED, user, property_id=property_id,
                      correlation_id=correlation_id,
                      entity_refs={"upload_session_id": up_id, "scan_session_id": scan_session_id},
                      extra={"artifact_type": artifact_type, "total_chunks": total_chunks,
                             "declared_size": total_size})
    rec["missing_indexes"] = list(range(total_chunks))
    return _public_upload_view(rec)


async def put_chunk(db, user, *, upload_session_id, index, data: bytes, chunk_sha256=None):
    up = await _load_session(db, upload_session_id)
    if up["state"] in enums.UPLOAD_TERMINAL:
        raise structured(409, "UPLOAD_TERMINAL", f"Upload session is {up['state']}.")
    total = up["total_chunks"]
    if not isinstance(index, int) or index < 0 or index >= total:
        raise structured(422, "INVALID_CHUNK_INDEX", f"index must be in [0, {total}).")
    if not data:
        raise structured(422, "EMPTY_CHUNK", "Chunk body is empty.")
    size = len(data)
    is_last = index == total - 1
    if not is_last and size != up["chunk_size"]:
        raise structured(422, "CHUNK_SIZE_MISMATCH",
                         f"Non-final chunk {index} must be exactly {up['chunk_size']} bytes (got {size}).")
    expected_last = up["declared_size"] - up["chunk_size"] * (total - 1)
    if is_last and size != expected_last:
        raise structured(422, "CHUNK_SIZE_MISMATCH",
                         f"Final chunk must be {expected_last} bytes (got {size}).")
    actual_sha = hashlib.sha256(data).hexdigest()
    if chunk_sha256 and chunk_sha256.lower() != actual_sha:
        raise structured(422, "CHUNK_CHECKSUM_MISMATCH", f"Chunk {index} checksum does not match its bytes.")

    existing = await db[enums.C_UPLOAD_CHUNKS].find_one(
        {"upload_session_id": upload_session_id, "index": index}, {"_id": 0})
    if existing:
        prev = (existing.get("verified_checksum_sha256") or existing.get("sha256") or "").lower()
        if prev == actual_sha and existing.get("size") == size:
            # Identical duplicate → idempotent success; do not re-write binaries to Mongo.
            fresh = await db[enums.C_UPLOAD_SESSIONS].find_one({"id": upload_session_id}, {"_id": 0})
            received = sorted(fresh.get("received_indexes") or [])
            return {
                "upload_session_id": upload_session_id,
                "index": index,
                "chunk_sha256": actual_sha,
                "duplicate": True,
                "idempotent": True,
                "received_count": len(received),
                "total_chunks": total,
                "bytes_received": fresh.get("bytes_received", 0),
                "missing_indexes": _missing_indexes(received, total),
                "state": fresh["state"],
            }
        raise structured(409, "CONFLICTING_CHUNK",
                         f"Chunk {index} already stored with different content; "
                         "identical duplicates are idempotent, conflicting content is rejected.")

    # Stream chunk into governed object-storage staging (not MongoDB).
    try:
        staged = await object_store.put_staging_chunk(
            tenant_id=up["tenant_id"], property_id=up["property_id"],
            upload_session_id=upload_session_id, index=index, data=data,
            content_type=up.get("content_type") or "application/octet-stream")
    except object_store.ObjectStoreProviderForbidden as e:
        raise structured(503, "OBJECT_STORE_PROVIDER_FORBIDDEN", str(e))
    except object_store.ObjectStoreError as e:
        raise structured(502, "OBJECT_STORE_UNAVAILABLE",
                         f"Chunk staging failed ({e.status}).")

    now = _now_iso()
    meta = _chunk_metadata_doc(
        up=up, index=index, size=size, sha256=actual_sha,
        object_reference=staged["object_reference"], etag=staged.get("etag"),
        storage_key_internal=staged["_storage_key_internal"], now=now)
    assert_no_binary_fields(meta)

    await db[enums.C_UPLOAD_CHUNKS].update_one(
        {"upload_session_id": upload_session_id, "index": index},
        {"$set": meta},
        upsert=True)

    already = index in (up.get("received_indexes") or [])
    update = {"$set": {"state": enums.UP_IN_PROGRESS, "updated_at": now},
              "$addToSet": {"received_indexes": index}}
    if not already:
        update["$inc"] = {"bytes_received": size}
    await db[enums.C_UPLOAD_SESSIONS].update_one({"id": upload_session_id}, update)

    fresh = await db[enums.C_UPLOAD_SESSIONS].find_one({"id": upload_session_id}, {"_id": 0})
    received = sorted(fresh.get("received_indexes") or [])
    return {
        "upload_session_id": upload_session_id,
        "index": index,
        "chunk_sha256": actual_sha,
        "duplicate": False,
        "idempotent": False,
        "received_count": len(received),
        "total_chunks": total,
        "bytes_received": fresh.get("bytes_received", 0),
        "missing_indexes": _missing_indexes(received, total),
        "state": fresh["state"],
        # Prove API does not leak storage coordinates:
        # (absence is the contract; tests assert these keys are missing)
    }


async def get_status(db, user, *, upload_session_id):
    up = await _load_session(db, upload_session_id)
    received = sorted(up.get("received_indexes") or [])
    total = up["total_chunks"]
    return {
        "upload_session_id": upload_session_id,
        "scan_session_id": up["scan_session_id"],
        "state": up["state"],
        "total_chunks": total,
        "chunk_size": up["chunk_size"],
        "declared_size": up["declared_size"],
        "bytes_received": up.get("bytes_received", 0),
        "received_count": len(received),
        "received_indexes": received,
        "missing_indexes": _missing_indexes(received, total),
        "complete": len(received) == total,
        "artifact_id": up.get("artifact_id"),
    }


async def complete_upload(db, user, *, upload_session_id, correlation_id=None, artifact_id=None):
    up = await _load_session(db, upload_session_id)
    if up["state"] == enums.UP_COMPLETED and up.get("artifact_id"):
        m = await db[enums.C_ARTIFACTS].find_one({"id": up["artifact_id"]}, {"_id": 0})
        return {"upload_session_id": upload_session_id, "state": enums.UP_COMPLETED,
                "idempotent_replay": True, "artifact": public_view(m) if m else None}
    if up["state"] in enums.UPLOAD_TERMINAL:
        raise structured(409, "UPLOAD_TERMINAL", f"Upload session is {up['state']}.")

    total = up["total_chunks"]
    received = sorted(up.get("received_indexes") or [])
    missing = _missing_indexes(received, total)
    if missing:
        raise structured(409, "INCOMPLETE_UPLOAD",
                         f"{len(missing)} chunk(s) missing; resume before completion.",
                         missing_indexes=missing[:64], missing_count=len(missing))

    await db[enums.C_UPLOAD_SESSIONS].update_one(
        {"id": upload_session_id}, {"$set": {"state": enums.UP_ASSEMBLING, "updated_at": _now_iso()}})

    tenant_id = up["tenant_id"]
    property_id = up["property_id"]
    art_id = artifact_id or f"rf-art-{uuid.uuid4()}"

    # Idempotent guard for a deterministic artifact id (e.g. the dev capture proof).
    if artifact_id:
        existing = await db[enums.C_ARTIFACTS].find_one({"id": art_id}, {"_id": 0})
        if existing:
            await db[enums.C_UPLOAD_SESSIONS].update_one(
                {"id": upload_session_id},
                {"$set": {"state": enums.UP_COMPLETED, "artifact_id": art_id, "updated_at": _now_iso()}})
            await _purge_chunk_metadata_and_mark_staging(db, up)
            return {"upload_session_id": upload_session_id, "state": enums.UP_COMPLETED,
                    "idempotent_replay": True, "artifact": public_view(existing)}

    storage_ref = governed_storage_reference(tenant_id, property_id, art_id)
    try:
        assembled = await object_store.compose_or_stream_assemble(
            tenant_id=tenant_id, property_id=property_id,
            upload_session_id=upload_session_id, total_chunks=total,
            final_storage_ref=storage_ref,
            content_type=up.get("content_type") or "application/octet-stream",
            declared_size=up["declared_size"],
            declared_checksum_sha256=up["declared_checksum_sha256"])
    except object_store.ObjectStoreProviderForbidden as e:
        await db[enums.C_UPLOAD_SESSIONS].update_one(
            {"id": upload_session_id}, {"$set": {"state": enums.UP_IN_PROGRESS,
                                                 "error": "OBJECT_STORE_PROVIDER_FORBIDDEN",
                                                 "updated_at": _now_iso()}})
        raise structured(503, "OBJECT_STORE_PROVIDER_FORBIDDEN", str(e))
    except object_store.ObjectStoreError as e:
        await db[enums.C_UPLOAD_SESSIONS].update_one(
            {"id": upload_session_id}, {"$set": {"state": enums.UP_IN_PROGRESS,
                                                 "error": "OBJECT_STORE_UNAVAILABLE",
                                                 "updated_at": _now_iso()}})
        raise structured(502, "OBJECT_STORE_UNAVAILABLE",
                         f"Checksum assemble/store failed ({e.status}); retry completion.")

    if not assembled.get("ok"):
        err = assembled.get("error")
        await db[enums.C_UPLOAD_SESSIONS].update_one(
            {"id": upload_session_id},
            {"$set": {"state": enums.UP_IN_PROGRESS, "error": err, "updated_at": _now_iso()}})
        if err == "SIZE_MISMATCH":
            raise structured(422, "SIZE_MISMATCH",
                             f"Assembled size {assembled.get('computed_size')} != "
                             f"declared {up['declared_size']}.")
        await write_event(db, enums.A_UPLOAD_CHECKSUM_MISMATCH, user, property_id=property_id,
                          correlation_id=correlation_id or up.get("correlation_id"),
                          entity_refs={"upload_session_id": upload_session_id,
                                       "scan_session_id": up["scan_session_id"]},
                          extra={"declared": up["declared_checksum_sha256"],
                                 "computed": assembled.get("computed_checksum_sha256")})
        raise structured(422, "CHECKSUM_MISMATCH",
                         "Assembled checksum does not match the declared manifest checksum; "
                         "re-upload the affected chunks.")

    digest = assembled["checksum_sha256"]
    put_result = assembled.get("put_result") or {}
    # Never persist signed URLs even if a provider leaked one.
    storage_etag = put_result.get("etag") if isinstance(put_result, dict) else None

    rec = build_manifest_record(
        tenant_id=tenant_id, property_id=property_id, artifact_type=up["artifact_type"],
        storage_object_reference=storage_ref, content_type=up.get("content_type") or "application/octet-stream",
        file_size=assembled["bytes_stored"], checksum_sha256=digest,
        correlation_id=correlation_id or up.get("correlation_id"),
        scan_session_id=up["scan_session_id"],
        truth_classification=up.get("truth_classification", enums.UNKNOWN),
        artifact_id=art_id)
    rec["artifact_id"] = art_id
    rec["object_stored"] = True
    rec["bytes_stored"] = assembled["bytes_stored"]
    rec["storage_etag"] = storage_etag
    rec["upload_session_id"] = upload_session_id
    # Explicit: never store signed/public URLs on the manifest.
    rec.pop("signed_url", None)
    rec.pop("public_url", None)
    await db[enums.C_ARTIFACTS].insert_one(dict(rec))

    await db[enums.C_UPLOAD_SESSIONS].update_one(
        {"id": upload_session_id},
        {"$set": {"state": enums.UP_COMPLETED, "artifact_id": art_id,
                  "error": None, "updated_at": _now_iso()}})
    await _purge_chunk_metadata_and_mark_staging(db, up)

    await write_event(db, enums.A_UPLOAD_COMPLETED, user, property_id=property_id,
                      correlation_id=correlation_id or up.get("correlation_id"),
                      entity_refs={"upload_session_id": upload_session_id, "artifact_id": art_id,
                                   "scan_session_id": up["scan_session_id"]},
                      extra={"bytes_stored": assembled["bytes_stored"], "checksum_verified": True,
                             "artifact_type": up["artifact_type"]})
    return {"upload_session_id": upload_session_id, "state": enums.UP_COMPLETED,
            "checksum_verified": True, "bytes_stored": assembled["bytes_stored"],
            "artifact": public_view(rec)}


async def abort_upload(db, user, *, upload_session_id, correlation_id=None):
    up = await _load_session(db, upload_session_id)
    if up["state"] == enums.UP_COMPLETED:
        raise structured(409, "UPLOAD_TERMINAL", "Completed upload cannot be aborted.")
    if up["state"] == enums.UP_ABORTED:
        # Idempotent abort replay.
        return {"upload_session_id": upload_session_id, "state": enums.UP_ABORTED,
                "idempotent_replay": True}
    await db[enums.C_UPLOAD_SESSIONS].update_one(
        {"id": upload_session_id}, {"$set": {"state": enums.UP_ABORTED, "updated_at": _now_iso()}})
    await _purge_chunk_metadata_and_mark_staging(db, up)
    await write_event(db, enums.A_UPLOAD_ABORTED, user, property_id=up["property_id"],
                      correlation_id=correlation_id or up.get("correlation_id"),
                      entity_refs={"upload_session_id": upload_session_id})
    return {"upload_session_id": upload_session_id, "state": enums.UP_ABORTED,
            "idempotent_replay": False}


async def _purge_chunk_metadata_and_mark_staging(db, up: dict):
    """Remove Mongo metadata and mark staging objects for governed cleanup.

    Does not fabricate object-store deletion when the provider has no delete API.
    """
    indexes = list(up.get("received_indexes") or [])
    marks = await object_store.mark_upload_staging_for_cleanup(
        tenant_id=up["tenant_id"], property_id=up["property_id"],
        upload_session_id=up["id"], indexes=indexes)
    # Persist only non-sensitive cleanup intent summaries on the session.
    safe_marks = [{"id": m["id"], "reason": m["reason"],
                   "deletion_executed": False, "deletion_fabricated": False}
                  for m in marks]
    await db[enums.C_UPLOAD_SESSIONS].update_one(
        {"id": up["id"]},
        {"$set": {"staging_cleanup_marks": safe_marks, "updated_at": _now_iso()}})
    await db[enums.C_UPLOAD_CHUNKS].delete_many({"upload_session_id": up["id"]})
