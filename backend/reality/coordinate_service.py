"""Coordinate frame + transform records and validation (Phase 6)."""
import math
import uuid
from datetime import datetime, timezone

from . import enums
from .authz import structured
from .audit_service import write_event


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- pure validation (unit-testable, no DB) ------------------------------
def validate_transform(matrix) -> None:
    """Validate a 4x4 homogeneous transform: dimensions, finite numbers, last row."""
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 4:
        raise structured(422, "INVALID_MATRIX", "Transform must have 4 rows.")
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != 4:
            raise structured(422, "INVALID_MATRIX", "Each transform row must have 4 columns.")
        for v in row:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise structured(422, "INVALID_MATRIX", "Transform entries must be numeric.")
            if not math.isfinite(v):
                raise structured(422, "NON_FINITE_MATRIX", "Transform entries must be finite.")
    last = [float(x) for x in matrix[3]]
    if last != [0.0, 0.0, 0.0, 1.0]:
        raise structured(422, "INVALID_HOMOGENEOUS_ROW",
                         "Homogeneous last row must equal [0,0,0,1].")


IDENTITY_4X4 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def build_frame_record(*, tenant_id, property_id, frame_type, parent_frame_id,
                       transform_to_parent, transform_to_property, origin_state,
                       origin_source, orientation_source=None, elevation_datum_source=None,
                       tolerance_class="PLANNING", residual_error_m=None, confidence="LOW",
                       correlation_id, frame_id=None, validation_state="VALIDATED"):
    if frame_type not in enums.FRAME_TYPES:
        raise structured(422, "INVALID_FRAME_TYPE", f"Unknown frame_type '{frame_type}'.")
    if origin_state not in enums.ORIGIN_STATES:
        raise structured(422, "INVALID_ORIGIN_STATE", f"Unknown origin_state '{origin_state}'.")
    if tolerance_class not in enums.TOLERANCE_CLASSES:
        raise structured(422, "INVALID_TOLERANCE_CLASS", f"Unknown tolerance_class '{tolerance_class}'.")
    validate_transform(transform_to_parent)
    validate_transform(transform_to_property)
    now = _now_iso()
    return {
        "id": frame_id or f"rf-frame-{uuid.uuid4()}",
        "coordinate_frame_id": frame_id or None,  # mirror set below
        "tenant_id": tenant_id,
        "property_id": property_id,
        "frame_type": frame_type,
        "parent_frame_id": parent_frame_id,
        "units": "METRIC_M",
        "axis_convention": enums.AXIS_CONVENTION,
        "origin_state": origin_state,
        "origin_source": origin_source,
        "orientation_source": orientation_source,
        "elevation_datum_source": elevation_datum_source,
        "transform_to_parent": transform_to_parent,
        "transform_to_property": transform_to_property,
        "tolerance_class": tolerance_class,
        "residual_error_m": residual_error_m,
        "confidence": confidence,
        "effective_at": now,
        "version": 1,
        "validation_state": validation_state,
        "superseded_by": None,
        "correlation_id": correlation_id,
        "created_at": now,
        "updated_at": now,
        "authoritative": False,
    }


# --- DB operations -------------------------------------------------------
async def _would_cycle(db, tenant_id, property_id, frame_id, parent_frame_id) -> bool:
    """Walk the parent chain; detect a cycle back to frame_id."""
    seen = set()
    cur = parent_frame_id
    while cur:
        if cur == frame_id or cur in seen:
            return True
        seen.add(cur)
        parent = await db[enums.C_FRAMES].find_one(
            {"id": cur, "tenant_id": tenant_id, "property_id": property_id}, {"_id": 0, "parent_frame_id": 1})
        if not parent:
            return False
        cur = parent.get("parent_frame_id")
    return False


async def create_frame(db, user, *, property_id, body: dict, correlation_id):
    tenant_id = enums.TENANT_ID
    parent_frame_id = body.get("parent_frame_id")
    frame_id = f"rf-frame-{uuid.uuid4()}"
    if parent_frame_id:
        parent = await db[enums.C_FRAMES].find_one(
            {"id": parent_frame_id, "tenant_id": tenant_id, "property_id": property_id}, {"_id": 0})
        if not parent:
            raise structured(422, "PARENT_FRAME_NOT_FOUND", "parent_frame_id does not exist for this property.")
        if await _would_cycle(db, tenant_id, property_id, frame_id, parent_frame_id):
            raise structured(422, "FRAME_CYCLE", "Coordinate-frame cycle detected.")
    # Explicit None-only fallback: an omitted/null transform defaults to identity,
    # but an explicitly supplied (possibly malformed) matrix is preserved so that
    # validate_transform can reject it rather than silently substituting identity.
    transform_to_parent = body.get("transform_to_parent")
    if transform_to_parent is None:
        transform_to_parent = IDENTITY_4X4
    transform_to_property = body.get("transform_to_property")
    if transform_to_property is None:
        transform_to_property = IDENTITY_4X4
    rec = build_frame_record(
        tenant_id=tenant_id, property_id=property_id,
        frame_type=body["frame_type"], parent_frame_id=parent_frame_id,
        transform_to_parent=transform_to_parent,
        transform_to_property=transform_to_property,
        origin_state=body.get("origin_state", "PROVISIONAL"),
        origin_source=body.get("origin_source", "UNKNOWN_SOURCE"),
        orientation_source=body.get("orientation_source"),
        elevation_datum_source=body.get("elevation_datum_source"),
        tolerance_class=body.get("tolerance_class", "PLANNING"),
        residual_error_m=body.get("residual_error_m"),
        confidence=body.get("confidence", "LOW"),
        correlation_id=correlation_id, frame_id=frame_id)
    rec["coordinate_frame_id"] = frame_id
    await db[enums.C_FRAMES].insert_one(dict(rec))
    await write_event(db, enums.A_FRAME_CREATED, user, property_id=property_id,
                      correlation_id=correlation_id, entity_refs={"coordinate_frame_id": frame_id},
                      extra={"frame_type": rec["frame_type"], "origin_state": rec["origin_state"]})
    rec.pop("_id", None)
    return rec
