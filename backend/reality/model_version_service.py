"""Separated existing / design model version records (Phase 9).

Existing-model versions become immutable once ACCEPTED; corrections create a new
version referencing previous_version_id. Design-model versions must reference an
ACCEPTED existing-model version and never overwrite existing-model records.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone

from . import enums
from .authz import structured, assert_truth_promotion_allowed
from .audit_service import write_event


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(entity_refs, frame_version, artifact_refs) -> str:
    payload = json.dumps({"entities": sorted(entity_refs or []),
                          "frame_version": frame_version,
                          "artifacts": sorted(artifact_refs or [])}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --- Existing model versions ---------------------------------------------
async def create_existing_model(db, user, *, property_id, body: dict, correlation_id):
    tenant_id = enums.TENANT_ID
    entity_refs = body.get("spatial_entity_ids", [])
    # No proposed-only entity may enter an existing-model snapshot.
    if entity_refs:
        cur = db[enums.C_SPATIAL].find(
            {"tenant_id": tenant_id, "property_id": property_id, "id": {"$in": entity_refs}},
            {"_id": 0, "id": 1, "entity_type": 1, "existing_state": 1, "truth_classification": 1})
        found = {e["id"]: e async for e in cur}
        for eid in entity_refs:
            e = found.get(eid)
            if not e:
                raise structured(422, "ENTITY_NOT_FOUND", f"spatial entity {eid} not found for this property.")
            if e["entity_type"] in enums.PROPOSED_ONLY_TYPES or e.get("existing_state") == enums.PROPOSED:
                raise structured(422, "PROPOSED_IN_EXISTING",
                                 f"Proposed entity {eid} cannot enter an existing-model snapshot.")
            assert_truth_promotion_allowed(e.get("truth_classification", enums.UNKNOWN), "N/A")

    now = _now_iso()
    mid = f"rf-existing-{uuid.uuid4()}"
    rec = {
        "id": mid, "existing_model_version_id": mid,
        "tenant_id": tenant_id, "property_id": property_id,
        "source_scan_session_ids": body.get("source_scan_session_ids", []),
        "spatial_entity_ids": entity_refs,
        "coordinate_frame_version": body.get("coordinate_frame_version", 1),
        "artifact_ids": body.get("artifact_ids", []),
        "truth_summary": body.get("truth_summary", {}),
        "quality_summary": body.get("quality_summary", {}),
        "unknown_areas": body.get("unknown_areas", []),
        "model_state": enums.EM_DRAFT_CANDIDATE,
        "accepted_at": None, "accepted_by": None,
        "previous_version_id": body.get("previous_version_id"),
        "content_hash": content_hash(entity_refs, body.get("coordinate_frame_version", 1), body.get("artifact_ids", [])),
        "immutable": False,
        "version": 1,
        "correlation_id": correlation_id,
        "created_at": now, "updated_at": now,
        "authoritative": False,
    }
    await db[enums.C_EXISTING].insert_one(dict(rec))
    await write_event(db, enums.A_EXISTING_CREATED, user, property_id=property_id,
                      correlation_id=correlation_id, entity_refs={"existing_model_version_id": mid},
                      after_state=enums.EM_DRAFT_CANDIDATE)
    rec.pop("_id", None)
    return rec


async def transition_existing_model(db, user, *, model_id, to_state, expected_version=None):
    tenant_id = enums.TENANT_ID
    m = await db[enums.C_EXISTING].find_one({"id": model_id}, {"_id": 0})
    if not m:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Existing model version not found")
    if m.get("tenant_id") != tenant_id:
        raise structured(403, "MODEL_ACCESS_DENIED", "Cross-tenant model access.")
    if m.get("immutable") and m["model_state"] == enums.EM_ACCEPTED and to_state != enums.EM_SUPERSEDED:
        raise structured(409, "MODEL_IMMUTABLE",
                         "Accepted existing-model version is immutable; create a new version for corrections.")
    if to_state not in enums.EM_LEGAL_TRANSITIONS.get(m["model_state"], set()):
        raise structured(409, "ILLEGAL_TRANSITION",
                         f"Illegal existing-model transition {m['model_state']} -> {to_state}.")
    if expected_version is not None and expected_version != m["version"]:
        raise structured(409, "STALE_VERSION", f"expected_version {expected_version} != {m['version']}.")

    now = _now_iso()
    set_fields = {"model_state": to_state, "updated_at": now}
    evt = enums.A_EXISTING_SUPERSEDED
    if to_state == enums.EM_ACCEPTED:
        set_fields.update({"immutable": True, "accepted_at": now, "accepted_by": user.get("id")})
        evt = enums.A_EXISTING_ACCEPTED
    elif to_state == enums.EM_REJECTED:
        evt = enums.A_EXISTING_REJECTED
    res = await db[enums.C_EXISTING].update_one(
        {"id": model_id, "version": m["version"]},
        {"$set": set_fields, "$inc": {"version": 1}})
    if res.modified_count != 1:
        raise structured(409, "STALE_VERSION", "Existing model changed concurrently; reload and retry.")
    updated = await db[enums.C_EXISTING].find_one({"id": model_id}, {"_id": 0})
    await write_event(db, evt, user, property_id=m.get("property_id"),
                      correlation_id=m.get("correlation_id"), before_state=m["model_state"], after_state=to_state,
                      entity_refs={"existing_model_version_id": model_id})
    return updated


# --- Design model versions ------------------------------------------------
async def create_design_model(db, user, *, property_id, body: dict, correlation_id):
    tenant_id = enums.TENANT_ID
    base_id = body.get("base_existing_model_version_id")
    if not base_id:
        raise structured(422, "MISSING_BASE_MODEL", "design model requires base_existing_model_version_id.")
    base = await db[enums.C_EXISTING].find_one(
        {"id": base_id, "tenant_id": tenant_id, "property_id": property_id}, {"_id": 0})
    if not base:
        raise structured(422, "BASE_MODEL_NOT_FOUND", "base_existing_model_version_id not found for this property.")
    if base["model_state"] != enums.EM_ACCEPTED:
        raise structured(409, "BASE_MODEL_NOT_ACCEPTED",
                         "Design model must be created on an ACCEPTED existing-model version.",
                         base_state=base["model_state"])

    # Proposed deltas: any inline proposed entities must be design classes (never restricted).
    for pe in body.get("proposed_entities", []):
        tc = pe.get("truth_classification", enums.PROPOSED_DESIGN)
        assert_truth_promotion_allowed(tc, "N/A")
        if tc not in enums.DESIGN_CLASSES:
            raise structured(422, "INVALID_DESIGN_TRUTH",
                             f"Proposed entity truth must be one of {sorted(enums.DESIGN_CLASSES)}.")

    now = _now_iso()
    did = f"rf-design-{uuid.uuid4()}"
    rec = {
        "id": did, "design_model_version_id": did,
        "tenant_id": tenant_id, "property_id": property_id,
        "base_existing_model_version_id": base_id,
        "proposed_entities": body.get("proposed_entities", []),
        "deltas": body.get("deltas", {"added": [], "modified": [], "removed": []}),
        "design_state": enums.DM_DRAFT,
        "created_by": user.get("id"),
        "previous_design_version_id": body.get("previous_design_version_id"),
        "version": 1,
        "correlation_id": correlation_id,
        "created_at": now, "updated_at": now,
        "authoritative": False,
    }
    await db[enums.C_DESIGN].insert_one(dict(rec))
    await write_event(db, enums.A_DESIGN_CREATED, user, property_id=property_id,
                      correlation_id=correlation_id,
                      entity_refs={"design_model_version_id": did, "base_existing_model_version_id": base_id},
                      after_state=enums.DM_DRAFT)
    rec.pop("_id", None)
    return rec
