"""Governed scan-session records + lifecycle (Phase 7 / H-014A.2 idempotency)."""
import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta

from pymongo.errors import DuplicateKeyError

from . import enums
from .authz import structured, not_found_nondisclosure
from .audit_service import write_event


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ttl_hours() -> int:
    try:
        return int(os.environ.get("HABITAT_SCAN_TTL_HOURS", "72"))
    except ValueError:
        return 72


def build_session_record(*, tenant_id, property_id, actor_id, capture_type, correlation_id,
                         coordinate_frame_id=None, device=None, sensors=None, app_version=None,
                         capture_mode=None, privacy_classification="SENSITIVE_INTERIOR",
                         create_idempotency_key=None, expires_in_seconds=None):
    if capture_type not in enums.CAPTURE_TYPES:
        raise structured(422, "INVALID_CAPTURE_TYPE", f"Unknown capture_type '{capture_type}'.")
    now = _now_iso()
    ttl = expires_in_seconds if (expires_in_seconds is not None) else _ttl_hours() * 3600
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=int(ttl))).isoformat()
    return {
        "id": f"rf-scan-{uuid.uuid4()}",
        "scan_session_id": None,  # mirror set by caller
        "tenant_id": tenant_id,
        "property_id": property_id,
        "actor_id": actor_id,
        "capture_type": capture_type,
        "device": device or {},
        "sensors": sensors or [],
        "app_version": app_version,
        "capture_mode": capture_mode,
        "coordinate_frame_id": coordinate_frame_id,
        "started_at": None,
        "ended_at": None,
        "current_state": enums.SCAN_CREATED,
        "coverage_state": "UNKNOWN",
        "quality_summary": {},
        "missing_areas": [],
        "privacy_classification": privacy_classification,
        "upload_state": enums.SCAN_UPLOAD_PENDING,
        "processing_state": enums.SCAN_PROCESSING_PENDING,
        "validation_state": "UNVALIDATED",
        "approval_state": "NONE",
        "failure_info": None,
        "recovery_token": None,
        "create_idempotency_key": create_idempotency_key,
        "processed_idempotency_keys": [],
        "version": 1,
        "correlation_id": correlation_id,
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at,
        "state_history": [{"state": enums.SCAN_CREATED, "at": now}],
        "authoritative": False,
    }


async def create_session(db, user, *, property_id, body: dict, correlation_id):
    """Create a scan session with scoped create-idempotency.

    Unique scope (partial unique index): tenant_id + property_id + actor_id +
    create_idempotency_key. Concurrent duplicates collapse to one session.
    """
    tenant_id = enums.TENANT_ID
    actor_id = user.get("id")
    key = body.get("idempotency_key")
    if key:
        existing = await db[enums.C_SCANS].find_one(
            {"tenant_id": tenant_id, "property_id": property_id, "actor_id": actor_id,
             "create_idempotency_key": key}, {"_id": 0})
        if existing:
            return existing
    rec = build_session_record(
        tenant_id=tenant_id, property_id=property_id, actor_id=actor_id,
        capture_type=body["capture_type"], correlation_id=correlation_id,
        coordinate_frame_id=body.get("coordinate_frame_id"), device=body.get("device"),
        sensors=body.get("sensors"), app_version=body.get("app_version"),
        capture_mode=body.get("capture_mode"),
        privacy_classification=body.get("privacy_classification", "SENSITIVE_INTERIOR"),
        create_idempotency_key=key, expires_in_seconds=body.get("expires_in_seconds"))
    rec["scan_session_id"] = rec["id"]
    try:
        await db[enums.C_SCANS].insert_one(dict(rec))
    except DuplicateKeyError:
        # Concurrent create with the same scoped idempotency key — return original.
        if key:
            existing = await db[enums.C_SCANS].find_one(
                {"tenant_id": tenant_id, "property_id": property_id, "actor_id": actor_id,
                 "create_idempotency_key": key}, {"_id": 0})
            if existing:
                return existing
        raise structured(409, "IDEMPOTENCY_CONFLICT",
                         "Scan session create collided on idempotency key; retry.")
    await write_event(db, enums.A_SCAN_CREATED, user, property_id=property_id,
                      correlation_id=correlation_id, entity_refs={"scan_session_id": rec["id"]},
                      after_state=enums.SCAN_CREATED, extra={"capture_type": rec["capture_type"]})
    rec.pop("_id", None)
    return rec


async def transition_session(db, user, *, session_id, to_state, expected_version=None,
                             idempotency_key=None):
    """Transition a scan session with DB-backed transition idempotency.

    Unique scope: (scan_session_id, transition_idempotency_key) in
    ``reality_scan_transition_idempotency``. Replay returns the current session
    without duplicating state changes or audit events.
    """
    tenant_id = enums.TENANT_ID
    wf = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    if not wf:
        raise not_found_nondisclosure()
    # Cross-tenant: uniform non-disclosure (no existence oracle).
    if wf.get("tenant_id") != tenant_id:
        await write_event(db, enums.A_CROSS_TENANT_REJECTED, user, property_id=wf.get("property_id"),
                          correlation_id=wf.get("correlation_id"), extra={"scan_session_id": session_id})
        raise not_found_nondisclosure()
    # Same-tenant actor isolation for non-privileged actors (action authz, not lookup oracle).
    if wf.get("actor_id") != user.get("id") and user.get("role") not in enums.PRIVILEGED_ROLES:
        await write_event(db, enums.A_CROSS_TENANT_REJECTED, user, property_id=wf.get("property_id"),
                          correlation_id=wf.get("correlation_id"), extra={"scan_session_id": session_id})
        raise structured(403, "SCAN_ACCESS_DENIED", "Not authorized for this scan session.")

    # Fast-path replay from session document.
    if idempotency_key and idempotency_key in (wf.get("processed_idempotency_keys") or []):
        return wf

    # Validate business rules BEFORE claiming the idempotency key so illegal /
    # stale / terminal requests do not consume the key.
    if wf["current_state"] in enums.SCAN_TERMINAL:
        raise structured(409, "TERMINAL_STATE", f"Scan session is terminal ({wf['current_state']}).",
                         correlation_id=wf.get("correlation_id"))
    if to_state not in enums.SCAN_LEGAL_TRANSITIONS.get(wf["current_state"], set()):
        raise structured(409, "ILLEGAL_TRANSITION",
                         f"Illegal scan transition {wf['current_state']} -> {to_state}.",
                         correlation_id=wf.get("correlation_id"))
    if expected_version is not None and expected_version != wf["version"]:
        await write_event(db, enums.A_VERSION_CONFLICT, user, property_id=wf.get("property_id"),
                          correlation_id=wf.get("correlation_id"), extra={"scan_session_id": session_id})
        raise structured(409, "STALE_VERSION",
                         f"expected_version {expected_version} != current {wf['version']}.",
                         correlation_id=wf.get("correlation_id"))

    # DB-backed transition idempotency claim (unique: scan_session_id + key).
    if idempotency_key:
        try:
            await db[enums.C_SCAN_TRANSITION_IDEMPOTENCY].insert_one({
                "id": f"rf-scan-idem-{uuid.uuid4()}",
                "scan_session_id": session_id,
                "idempotency_key": idempotency_key,
                "tenant_id": tenant_id,
                "property_id": wf.get("property_id"),
                "actor_id": user.get("id"),
                "to_state": to_state,
                "created_at": _now_iso(),
            })
        except DuplicateKeyError:
            # Concurrent winner may still be applying the versioned update — wait briefly
            # for the session document to reflect the single state change, then return.
            for _ in range(40):
                updated = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
                if updated and (
                    idempotency_key in (updated.get("processed_idempotency_keys") or [])
                    or updated.get("version", 0) > wf.get("version", 0)
                ):
                    return updated
                await asyncio.sleep(0.025)
            updated = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
            return updated or wf

    now = _now_iso()
    set_fields = {"current_state": to_state, "updated_at": now}
    if to_state == enums.SCAN_CAPTURE_IN_PROGRESS and not wf.get("started_at"):
        set_fields["started_at"] = now
    if to_state in (enums.SCAN_ACCEPTED, enums.SCAN_REJECTED):
        set_fields["ended_at"] = now
        set_fields["validation_state"] = "GUARDIAN_REVIEWED"
        set_fields["approval_state"] = "ACCEPTED" if to_state == enums.SCAN_ACCEPTED else "REJECTED"
    update = {"$set": set_fields, "$inc": {"version": 1},
              "$push": {"state_history": {"state": to_state, "at": now}}}
    if idempotency_key:
        update["$addToSet"] = {"processed_idempotency_keys": idempotency_key}
    res = await db[enums.C_SCANS].update_one({"id": session_id, "version": wf["version"]}, update)
    if res.modified_count != 1:
        # Concurrent version loss — if our idempotency key was claimed by the winner, replay.
        updated = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
        if idempotency_key and updated and idempotency_key in (updated.get("processed_idempotency_keys") or []):
            return updated
        await write_event(db, enums.A_VERSION_CONFLICT, user, property_id=wf.get("property_id"),
                          correlation_id=wf.get("correlation_id"), extra={"scan_session_id": session_id})
        raise structured(409, "STALE_VERSION", "Scan session changed concurrently; reload and retry.",
                         correlation_id=wf.get("correlation_id"))
    updated = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    evt = enums.A_SCAN_REJECTED if to_state == enums.SCAN_REJECTED else enums.A_SCAN_TRANSITIONED
    await write_event(db, evt, user, property_id=wf.get("property_id"),
                      correlation_id=wf.get("correlation_id"), before_state=wf["current_state"],
                      after_state=to_state, entity_refs={"scan_session_id": session_id})
    return updated
