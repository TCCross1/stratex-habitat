"""Shared spatial entity records + hierarchy validation (Phase 5)."""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from . import enums
from .authz import structured, assert_truth_promotion_allowed, validate_classifications
from .audit_service import write_event
from .geometry_reference import resolve_geometry_reference, public_spatial_entity


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_label(body: dict) -> str:
    """Explicit None-only default: an omitted/null label falls back to entity_type;
    an explicitly supplied value (including empty string) is preserved (no silent fallback)."""
    label = body.get("label")
    if label is None:
        label = body.get("entity_type")
    return label


# --- pure relationship validation (unit-testable) ------------------------
def validate_entity_relationships(entity: dict, parent: dict = None, opening: dict = None) -> None:
    et = entity.get("entity_type")
    if et not in enums.ENTITY_TYPES:
        raise structured(422, "INVALID_ENTITY_TYPE", f"Unknown entity_type '{et}'.")

    eid = entity.get("id")
    parent_id = entity.get("parent_entity_id")

    if parent_id and parent_id == eid:
        raise structured(422, "SELF_PARENT", "Entity cannot be its own parent.")

    if parent_id:
        if parent is None:
            raise structured(422, "PARENT_NOT_FOUND", "parent_entity_id does not exist.")
        if parent.get("tenant_id") != entity.get("tenant_id"):
            raise structured(403, "CROSS_TENANT_RELATIONSHIP", "Parent belongs to a different tenant.")
        if parent.get("property_id") != entity.get("property_id"):
            raise structured(422, "CROSS_PROPERTY_RELATIONSHIP", "Parent belongs to a different property.")

    # Openings must sit on a surface-like parent (no orphan openings).
    if et in enums.OPENING_LIKE and et == "OPENING":
        if not parent or parent.get("entity_type") not in enums.SURFACE_LIKE:
            raise structured(422, "ORPHAN_OPENING", "An OPENING must have a surface-like parent (WALL/SURFACE/etc.).")

    # Doors/windows must reference a valid OPENING.
    if et in ("DOOR", "WINDOW"):
        ref = entity.get("opening_ref")
        if not ref:
            raise structured(422, "MISSING_OPENING_REF", f"{et} must reference an OPENING via opening_ref.")
        if opening is None:
            raise structured(422, "OPENING_REF_NOT_FOUND", "opening_ref does not exist.")
        if opening.get("entity_type") != "OPENING":
            raise structured(422, "INVALID_OPENING_REF", "opening_ref must point to an OPENING entity.")
        if opening.get("property_id") != entity.get("property_id"):
            raise structured(422, "CROSS_PROPERTY_RELATIONSHIP", "opening_ref belongs to a different property.")

    # Proposed-only types must not claim EXISTING state.
    if et in enums.PROPOSED_ONLY_TYPES and entity.get("existing_state") == enums.EXISTING:
        raise structured(422, "PROPOSED_IN_EXISTING",
                         f"{et} is proposed geometry and cannot be marked EXISTING.")


def build_entity_record(*, tenant_id, property_id, entity_type, label, coordinate_frame_id,
                        truth_classification, source_classification, confidence, correlation_id,
                        parent_entity_id=None, building_id=None, opening_ref=None,
                        geometry_type="NONE", geometry_reference=None, units="METRIC_M",
                        existing_state=enums.EXISTING, canonical_passport_reference=None,
                        access_classification="HOMEOWNER", created_by=None, entity_id=None,
                        unknowns=None, dimensions=None):
    validate_classifications(truth_classification, source_classification, confidence, units)
    if geometry_type not in enums.GEOMETRY_TYPES:
        raise structured(422, "INVALID_GEOMETRY_TYPE", f"Unknown geometry_type '{geometry_type}'.")
    if existing_state not in enums.EXISTENCE_STATES:
        raise structured(422, "INVALID_EXISTENCE_STATE", f"Unknown existing_state '{existing_state}'.")
    if access_classification not in enums.ACCESS_CLASSES:
        raise structured(422, "INVALID_ACCESS_CLASS", f"Unknown access_classification '{access_classification}'.")
    now = _now_iso()
    return {
        "id": entity_id or f"rf-ent-{uuid.uuid4()}",
        "spatial_entity_id": entity_id or None,  # mirror set by caller
        "tenant_id": tenant_id,
        "property_id": property_id,
        "building_id": building_id,
        "parent_entity_id": parent_entity_id,
        "entity_type": entity_type,
        "label": label,
        "coordinate_frame_id": coordinate_frame_id,
        "geometry_reference": geometry_reference,
        "geometry_type": geometry_type,
        "geometry_version": 1,
        "truth_classification": truth_classification,
        "source_classification": source_classification,
        "confidence": confidence,
        "units": units,
        "lifecycle_state": "ACTIVE",
        "existing_state": existing_state,
        "opening_ref": opening_ref,
        "canonical_passport_reference": canonical_passport_reference,
        "provenance": {"source": source_classification, "created_by": created_by},
        "unknowns": unknowns or [],
        "dimensions": dimensions,
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
        "version": 1,
        "access_classification": access_classification,
        "correlation_id": correlation_id,
        "authoritative": False,
    }


# --- DB operations -------------------------------------------------------
async def _would_cycle(db, tenant_id, property_id, entity_id, parent_id) -> bool:
    seen = set()
    cur = parent_id
    while cur:
        if cur == entity_id or cur in seen:
            return True
        seen.add(cur)
        p = await db[enums.C_SPATIAL].find_one(
            {"id": cur, "tenant_id": tenant_id, "property_id": property_id}, {"_id": 0, "parent_entity_id": 1})
        if not p:
            return False
        cur = p.get("parent_entity_id")
    return False


async def create_entity(db, user, *, property_id, body: dict, correlation_id):
    tenant_id = enums.TENANT_ID
    truth = body.get("truth_classification", enums.MEASURED_EXISTING)
    source = body.get("source_classification", "HOMEOWNER_INPUT")
    # Fail closed on restricted truth promotion by Habitat actors — and audit the
    # rejection exactly once. Audit is best-effort: a persistence failure must NOT
    # convert the forbidden operation into a success (the denial still propagates).
    try:
        assert_truth_promotion_allowed(truth, source)
    except HTTPException:
        try:
            await write_event(db, enums.A_TRUTH_PROMOTION_REJECTED, user, property_id=property_id,
                              correlation_id=correlation_id,
                              entity_refs={"entity_type": body.get("entity_type")},
                              extra={"attempted_truth_classification": truth,
                                     "attempted_source_classification": source,
                                     "operation": "create_spatial_entity"})
        except Exception:
            pass
        raise

    entity_id = f"rf-ent-{uuid.uuid4()}"
    # H-014A.2: governed geometry_reference (artifact: / fixture:) — never raw storage/URLs.
    geometry_reference = await resolve_geometry_reference(
        db, body.get("geometry_reference"), tenant_id=tenant_id, property_id=property_id)
    rec = build_entity_record(
        tenant_id=tenant_id, property_id=property_id,
        entity_type=body["entity_type"], label=resolve_label(body),
        coordinate_frame_id=body.get("coordinate_frame_id"),
        truth_classification=truth, source_classification=source,
        confidence=body.get("confidence", "MEDIUM"), correlation_id=correlation_id,
        parent_entity_id=body.get("parent_entity_id"), building_id=body.get("building_id"),
        opening_ref=body.get("opening_ref"), geometry_type=body.get("geometry_type", "NONE"),
        geometry_reference=geometry_reference, units=body.get("units", "METRIC_M"),
        existing_state=body.get("existing_state", enums.EXISTING),
        access_classification=body.get("access_classification", "HOMEOWNER"),
        created_by=user.get("id"), entity_id=entity_id, unknowns=body.get("unknowns"),
        dimensions=body.get("dimensions"))
    rec["spatial_entity_id"] = entity_id

    parent = None
    if rec.get("parent_entity_id"):
        parent = await db[enums.C_SPATIAL].find_one({"id": rec["parent_entity_id"]}, {"_id": 0})
    opening = None
    if rec.get("opening_ref"):
        opening = await db[enums.C_SPATIAL].find_one({"id": rec["opening_ref"]}, {"_id": 0})

    try:
        validate_entity_relationships(rec, parent, opening)
    except Exception:
        await write_event(db, enums.A_INVALID_RELATIONSHIP_REJECTED, user, property_id=property_id,
                          correlation_id=correlation_id, extra={"entity_type": rec["entity_type"]})
        raise
    if rec.get("parent_entity_id") and await _would_cycle(db, tenant_id, property_id, entity_id, rec["parent_entity_id"]):
        raise structured(422, "ENTITY_CYCLE", "Parent chain would create a cycle.")

    await db[enums.C_SPATIAL].insert_one(dict(rec))
    await write_event(db, enums.A_SPATIAL_ENTITY_CREATED, user, property_id=property_id,
                      correlation_id=correlation_id,
                      entity_refs={"spatial_entity_id": entity_id, "parent_entity_id": rec.get("parent_entity_id")},
                      extra={"entity_type": rec["entity_type"], "truth_classification": truth})
    rec.pop("_id", None)
    return public_spatial_entity(rec)


async def get_spatial_graph(db, property_id: str) -> dict:
    tenant_id = enums.TENANT_ID
    cur = db[enums.C_SPATIAL].find({"tenant_id": tenant_id, "property_id": property_id}, {"_id": 0})
    entities = [public_spatial_entity(e) async for e in cur]
    counts = {}
    for e in entities:
        counts[e["entity_type"]] = counts.get(e["entity_type"], 0) + 1
    truth_counts = {}
    for e in entities:
        tc = e.get("truth_classification", enums.UNKNOWN)
        truth_counts[tc] = truth_counts.get(tc, 0) + 1
    return {
        "property_id": property_id,
        "tenant_id": tenant_id,
        "entity_count": len(entities),
        "entity_counts_by_type": counts,
        "truth_classification_counts": truth_counts,
        "entities": entities,
    }
