"""Resumable, governed chunked upload of heavy capture artifacts (H-014B, Phase 6).

Flow (client == iOS ResumableUploader):
  1. init_upload   -> create an upload session bound to tenant+property+scan.
  2. put_chunk     -> stream ordered/independent chunks; idempotent per index;
                      chunks are staged in MongoDB (`reality_upload_chunks`) so a
                      client can resume after interruption (see get_status).
  3. complete_upload -> require all chunks; assemble in order; verify the
                      assembled SHA-256 against the client-declared manifest
                      checksum; on match, write ONE immutable object to governed
                      object storage and create the artifact manifest; purge staging.
  4. abort_upload  -> discard staged chunks.

Governance: tenant is server-derived, property is the authorized scan-session
property (never taken from the client). The final object key is server-derived
`tenant/{tenant}/property/{property}/reality/{artifact_id}`. Checksum mismatch is
rejected (never silently accepted) and audited.
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
            return existing

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
    }
    await db[enums.C_UPLOAD_SESSIONS].insert_one(dict(rec))
    await write_event(db, enums.A_UPLOAD_INITIATED, user, property_id=property_id,
                      correlation_id=correlation_id,
                      entity_refs={"upload_session_id": up_id, "scan_session_id": scan_session_id},
                      extra={"artifact_type": artifact_type, "total_chunks": total_chunks,
                             "declared_size": total_size})
    rec["missing_indexes"] = list(range(total_chunks))
    rec.pop("_id", None)
    return rec


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

    already = index in (up.get("received_indexes") or [])
    # Idempotent per-index upsert of the staged chunk bytes.
    await db[enums.C_UPLOAD_CHUNKS].update_one(
        {"upload_session_id": upload_session_id, "index": index},
        {"$set": {"upload_session_id": upload_session_id, "index": index,
                  "size": size, "sha256": actual_sha, "data": data,
                  "created_at": _now_iso()}},
        upsert=True)
    update = {"$set": {"state": enums.UP_IN_PROGRESS, "updated_at": _now_iso()},
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
        "duplicate": already,
        "received_count": len(received),
        "total_chunks": total,
        "bytes_received": fresh.get("bytes_received", 0),
        "missing_indexes": _missing_indexes(received, total),
        "state": fresh["state"],
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

    # Assemble strictly in index order.
    buf = bytearray()
    async for c in db[enums.C_UPLOAD_CHUNKS].find({"upload_session_id": upload_session_id}).sort("index", 1):
        buf.extend(bytes(c["data"]))
    assembled = bytes(buf)

    if len(assembled) != up["declared_size"]:
        await db[enums.C_UPLOAD_SESSIONS].update_one(
            {"id": upload_session_id}, {"$set": {"state": enums.UP_IN_PROGRESS,
                                                 "error": "SIZE_MISMATCH", "updated_at": _now_iso()}})
        raise structured(422, "SIZE_MISMATCH",
                         f"Assembled size {len(assembled)} != declared {up['declared_size']}.")

    digest = hashlib.sha256(assembled).hexdigest()
    if digest != up["declared_checksum_sha256"]:
        await db[enums.C_UPLOAD_SESSIONS].update_one(
            {"id": upload_session_id}, {"$set": {"state": enums.UP_IN_PROGRESS,
                                                 "error": "CHECKSUM_MISMATCH", "updated_at": _now_iso()}})
        await write_event(db, enums.A_UPLOAD_CHECKSUM_MISMATCH, user, property_id=up["property_id"],
                          correlation_id=correlation_id or up.get("correlation_id"),
                          entity_refs={"upload_session_id": upload_session_id,
                                       "scan_session_id": up["scan_session_id"]},
                          extra={"declared": up["declared_checksum_sha256"], "computed": digest})
        raise structured(422, "CHECKSUM_MISMATCH",
                         "Assembled checksum does not match the declared manifest checksum; "
                         "re-upload the affected chunks.")

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
            await db[enums.C_UPLOAD_CHUNKS].delete_many({"upload_session_id": upload_session_id})
            return {"upload_session_id": upload_session_id, "state": enums.UP_COMPLETED,
                    "idempotent_replay": True, "artifact": public_view(existing)}

    storage_ref = governed_storage_reference(tenant_id, property_id, art_id)
    try:
        put_result = await object_store.put(storage_ref, assembled,
                                            up.get("content_type") or "application/octet-stream")
    except object_store.ObjectStoreError as e:
        # Integrity already verified; leave the upload resumable and signal a retryable error.
        await db[enums.C_UPLOAD_SESSIONS].update_one(
            {"id": upload_session_id}, {"$set": {"state": enums.UP_IN_PROGRESS,
                                                 "error": "OBJECT_STORE_UNAVAILABLE",
                                                 "updated_at": _now_iso()}})
        raise structured(502, "OBJECT_STORE_UNAVAILABLE",
                         f"Checksum verified but object storage is unavailable ({e.status}); "
                         "retry completion.")

    rec = build_manifest_record(
        tenant_id=tenant_id, property_id=property_id, artifact_type=up["artifact_type"],
        storage_object_reference=storage_ref, content_type=up.get("content_type") or "application/octet-stream",
        file_size=len(assembled), checksum_sha256=digest,
        correlation_id=correlation_id or up.get("correlation_id"),
        scan_session_id=up["scan_session_id"],
        truth_classification=up.get("truth_classification", enums.UNKNOWN),
        artifact_id=art_id)
    rec["artifact_id"] = art_id
    rec["object_stored"] = True
    rec["bytes_stored"] = len(assembled)
    rec["storage_etag"] = put_result.get("etag") if isinstance(put_result, dict) else None
    rec["upload_session_id"] = upload_session_id
    await db[enums.C_ARTIFACTS].insert_one(dict(rec))

    await db[enums.C_UPLOAD_SESSIONS].update_one(
        {"id": upload_session_id},
        {"$set": {"state": enums.UP_COMPLETED, "artifact_id": art_id,
                  "error": None, "updated_at": _now_iso()}})
    await db[enums.C_UPLOAD_CHUNKS].delete_many({"upload_session_id": upload_session_id})

    await write_event(db, enums.A_UPLOAD_COMPLETED, user, property_id=property_id,
                      correlation_id=correlation_id or up.get("correlation_id"),
                      entity_refs={"upload_session_id": upload_session_id, "artifact_id": art_id,
                                   "scan_session_id": up["scan_session_id"]},
                      extra={"bytes_stored": len(assembled), "checksum_verified": True,
                             "artifact_type": up["artifact_type"]})
    return {"upload_session_id": upload_session_id, "state": enums.UP_COMPLETED,
            "checksum_verified": True, "bytes_stored": len(assembled),
            "artifact": public_view(rec)}


async def abort_upload(db, user, *, upload_session_id, correlation_id=None):
    up = await _load_session(db, upload_session_id)
    if up["state"] == enums.UP_COMPLETED:
        raise structured(409, "UPLOAD_TERMINAL", "Completed upload cannot be aborted.")
    await db[enums.C_UPLOAD_SESSIONS].update_one(
        {"id": upload_session_id}, {"$set": {"state": enums.UP_ABORTED, "updated_at": _now_iso()}})
    await db[enums.C_UPLOAD_CHUNKS].delete_many({"upload_session_id": upload_session_id})
    await write_event(db, enums.A_UPLOAD_ABORTED, user, property_id=up["property_id"],
                      correlation_id=correlation_id or up.get("correlation_id"),
                      entity_refs={"upload_session_id": upload_session_id})
    return {"upload_session_id": upload_session_id, "state": enums.UP_ABORTED}
