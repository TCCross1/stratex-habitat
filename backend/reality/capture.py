"""Capture-state mapping + governed candidate-model generation (H-014B, Phases 5, 8).

Truth boundary (non-negotiable): a completed/accepted capture produces ONLY a
DRAFT_CANDIDATE existing-model with MEASURED_EXISTING geometry. It is NEVER
auto-promoted to VERIFIED_EXISTING — that requires a separate authorized
Core/Passport/professional review (fails closed in Habitat).
"""
import uuid
from datetime import datetime, timezone

from . import enums
from .authz import structured, not_found_nondisclosure
from .audit_service import write_event
from .spatial_service import build_entity_record, validate_entity_relationships
from . import model_version_service as mvs


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def map_native_state(native_state: str) -> str:
    """Map a native (iOS RoomPlan/ARKit) capture state to the canonical scan state."""
    if native_state not in enums.NATIVE_TO_SCAN_STATE:
        raise structured(422, "UNKNOWN_NATIVE_STATE",
                         f"Unknown native capture state '{native_state}'.",
                         known_states=sorted(enums.NATIVE_CAPTURE_STATES))
    return enums.NATIVE_TO_SCAN_STATE[native_state]


def native_state_map() -> dict:
    return {
        "axis_convention": enums.AXIS_CONVENTION,
        "native_states": sorted(enums.NATIVE_CAPTURE_STATES),
        "mapping": dict(enums.NATIVE_TO_SCAN_STATE),
        "canonical_scan_states": sorted({v for v in enums.NATIVE_TO_SCAN_STATE.values()}),
    }


async def record_capture_progress(db, user, *, session_id, body: dict, correlation_id=None):
    """Persist live capture telemetry (coverage, tracking, native state) on the
    scan session. Does not itself transition state (that is a governed action);
    optionally records the mapped canonical state for observability."""
    session = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise not_found_nondisclosure()
    native_state = body.get("native_state")
    mapped = map_native_state(native_state) if native_state else None
    telemetry = {
        "native_state": native_state,
        "mapped_scan_state": mapped,
        "surface_coverage": body.get("surface_coverage") or {},
        "tracking_quality": body.get("tracking_quality") or {},
        "captured_area_m2": body.get("captured_area_m2"),
        "frame_count": body.get("frame_count"),
        "at": _now_iso(),
    }
    await db[enums.C_SCANS].update_one(
        {"id": session_id},
        {"$set": {"capture_telemetry": telemetry, "updated_at": telemetry["at"]}})
    await write_event(db, enums.A_CAPTURE_PROGRESS, user, property_id=session.get("property_id"),
                      correlation_id=correlation_id or session.get("correlation_id"),
                      entity_refs={"scan_session_id": session_id},
                      extra={"native_state": native_state, "mapped_scan_state": mapped})
    updated = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    return {"scan_session": updated, "telemetry": telemetry}


def _build_capture_entities(*, property_id, coordinate_frame_id, structure: dict, actor_id, correlation_id):
    """Deterministically construct MEASURED_EXISTING spatial entities (room, 4 walls,
    floor, ceiling, openings) from a derived capture structure. Returns records +
    the room id + the ordered entity id list."""
    tenant_id = enums.TENANT_ID
    dims = structure.get("dimensions_m") or {}
    room_id = f"rf-ent-{uuid.uuid4()}"

    def _mk(entity_type, label, parent, **kw):
        eid = f"rf-ent-{uuid.uuid4()}"
        rec = build_entity_record(
            tenant_id=tenant_id, property_id=property_id, entity_type=entity_type, label=label,
            coordinate_frame_id=coordinate_frame_id, truth_classification=enums.MEASURED_EXISTING,
            source_classification="LIDAR_CAPTURE", confidence="MEDIUM", correlation_id=correlation_id,
            parent_entity_id=parent, geometry_type=kw.get("geometry_type", "PLANE"),
            geometry_reference=kw.get("geometry_reference"), existing_state=enums.EXISTING,
            access_classification="HOMEOWNER", created_by=actor_id, entity_id=eid,
            opening_ref=kw.get("opening_ref"), dimensions=kw.get("dimensions"),
            unknowns=kw.get("unknowns"))
        rec["spatial_entity_id"] = eid
        return rec

    room = _mk("ROOM", structure.get("room_label") or "Captured Room", None,
               geometry_type="POLYGON",
               dimensions={"width_m": dims.get("width"), "length_m": dims.get("length"),
                           "height_m": dims.get("height"),
                           "floor_area_m2": dims.get("floor_area_m2")},
               unknowns=structure.get("unknowns") or ["Concealed wall structure", "Sub-floor condition"])
    room["id"] = room_id
    room["spatial_entity_id"] = room_id
    records = [room]

    walls = {}
    for name in ("North", "East", "South", "West"):
        w = _mk("WALL", f"{name} Wall", room_id)
        walls[name] = w
        records.append(w)
    if structure.get("has_floor", True):
        records.append(_mk("FLOOR", "Floor", room_id, geometry_type="POLYGON"))
    if structure.get("has_ceiling", True):
        records.append(_mk("CEILING", "Ceiling", room_id))

    # Openings sit on a wall; doors/windows reference their opening.
    for op in structure.get("openings") or []:
        wall_name = (op.get("wall") or "North").capitalize()
        wall = walls.get(wall_name, walls["North"])
        opening = _mk("OPENING", op.get("label") or f"{op.get('type', 'Opening')} Opening",
                      wall["id"], geometry_type="POLYGON")
        records.append(opening)
        sub_type = (op.get("type") or "").upper()
        if sub_type in ("DOOR", "WINDOW"):
            records.append(_mk(sub_type, op.get("label") or sub_type.capitalize(),
                               wall["id"], geometry_type="POLYGON", opening_ref=opening["id"]))
    return records, room_id


async def generate_candidate(db, user, *, session_id, body: dict, correlation_id):
    """Create MEASURED_EXISTING geometry + a DRAFT_CANDIDATE existing-model from a
    reviewed/accepted capture. Enforces the truth boundary (DRAFT_CANDIDATE only)."""
    session = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise not_found_nondisclosure()
    tenant_id = enums.TENANT_ID
    if session.get("tenant_id") != tenant_id:
        raise structured(403, "SCAN_ACCESS_DENIED", "Cross-tenant scan session.")
    if session["current_state"] not in (enums.SCAN_QUALITY_REVIEW, enums.SCAN_ACCEPTED):
        raise structured(409, "CAPTURE_NOT_REVIEWABLE",
                         "A candidate model can only be generated once the scan reaches QUALITY_REVIEW.",
                         current_state=session["current_state"])
    property_id = session["property_id"]
    structure = body.get("derived_structure") or {}
    frame_id = session.get("coordinate_frame_id") or body.get("coordinate_frame_id")

    records, _room_id = _build_capture_entities(
        property_id=property_id, coordinate_frame_id=frame_id, structure=structure,
        actor_id=user.get("id"), correlation_id=correlation_id)

    # Validate relationships against the in-batch records (parents resolved locally).
    by_id = {r["id"]: r for r in records}
    for rec in records:
        parent = by_id.get(rec.get("parent_entity_id"))
        opening = by_id.get(rec.get("opening_ref"))
        validate_entity_relationships(rec, parent, opening)
    if records:
        await db[enums.C_SPATIAL].insert_many([dict(r) for r in records])
    entity_ids = [r["id"] for r in records]

    artifact_ids = body.get("artifact_ids") or []
    truth_counts = {enums.MEASURED_EXISTING: len(records)}
    model_body = {
        "source_scan_session_ids": [session_id],
        "spatial_entity_ids": entity_ids,
        "coordinate_frame_version": 1,
        "artifact_ids": artifact_ids,
        "truth_summary": truth_counts,
        "quality_summary": session.get("quality_summary") or {},
        "unknown_areas": (session.get("guardian_result") or {}).get("missing_areas")
        or structure.get("unknowns") or [],
    }
    model = await mvs.create_existing_model(db, user, property_id=property_id,
                                            body=model_body, correlation_id=correlation_id)
    # Truth boundary assertion — capture NEVER auto-promotes.
    assert model["model_state"] == enums.EM_DRAFT_CANDIDATE

    await write_event(db, enums.A_CANDIDATE_GENERATED, user, property_id=property_id,
                      correlation_id=correlation_id,
                      entity_refs={"scan_session_id": session_id,
                                   "existing_model_version_id": model["id"]},
                      after_state=enums.EM_DRAFT_CANDIDATE,
                      extra={"entity_count": len(records), "truth_classification": enums.MEASURED_EXISTING})
    return {"existing_model_version": model, "entity_count": len(records),
            "spatial_entity_ids": entity_ids, "truth_boundary": "DRAFT_CANDIDATE_ONLY"}
