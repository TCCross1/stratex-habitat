"""Deterministic, explicitly non-authoritative reference room (Phase 10).

Development/test only. Production access fails closed via fixture governance
(fixture_provider.require_fixtures). Bootstrap is idempotent (deterministic IDs
with upsert-on-insert; accepted records are never mutated).
"""
import hashlib
from datetime import datetime, timezone

import fixture_provider as fx  # H-013 Batch 1 fixture governance

from . import enums
from .authz import REF_PROPERTY_ID
from .coordinate_service import IDENTITY_4X4
from .audit_service import write_event

FIXTURE_VERSION = "1.0.0"
SOURCE_LABEL = "reality-reference-room"

# Deterministic dimensions (meters)
WIDTH_M = 4.88   # X east
LENGTH_M = 6.10  # Y north
HEIGHT_M = 2.74  # Z up

# Deterministic IDs
FRAME_PROPERTY = "rf-frame-property-h014a"
FRAME_ROOM = "rf-frame-room-h014a"
ROOM = "rf-ent-room-h014a"
WALL_N, WALL_E, WALL_S, WALL_W = ("rf-ent-wall-north-h014a", "rf-ent-wall-east-h014a",
                                  "rf-ent-wall-south-h014a", "rf-ent-wall-west-h014a")
FLOOR = "rf-ent-floor-h014a"
CEILING = "rf-ent-ceiling-h014a"
OPENING_WINDOW = "rf-ent-opening-window-h014a"
WINDOW = "rf-ent-window-h014a"
OPENING_DOOR = "rf-ent-opening-door-h014a"
DOOR = "rf-ent-door-h014a"
OPENING_ADJOINING = "rf-ent-opening-adjoining-h014a"
ARTIFACT = "rf-art-floorplan-h014a"
EXISTING_MODEL = "rf-existing-model-v1-h014a"

FLOORPLAN_CHECKSUM = hashlib.sha256(
    f"h014a-reference-room-floorplan-{FIXTURE_VERSION}".encode("utf-8")).hexdigest()


def _fixture_tags(generated_at):
    return {
        "authoritative": False,
        "source_classification": "DETERMINISTIC_REFERENCE_FIXTURE",
        "fixture_id": "h014a-reference-room",
        "fixture_version": FIXTURE_VERSION,
        "generated_at": generated_at,
        "environment_scope": "development_test_only",
        "tenant_id": enums.TENANT_ID,
        "property_id": REF_PROPERTY_ID,
        "correlation_id": "rf-corr-h014a",
    }


def _entity(entity_id, entity_type, label, parent, tags, *, truth=enums.MEASURED_EXISTING,
            opening_ref=None, geometry_type="PLANE", dimensions=None, unknowns=None):
    now = tags["generated_at"]
    rec = {
        "id": entity_id, "spatial_entity_id": entity_id,
        "entity_type": entity_type, "label": label,
        "parent_entity_id": parent, "building_id": None,
        "coordinate_frame_id": FRAME_ROOM,
        "geometry_reference": f"fixture://{entity_id}", "geometry_type": geometry_type,
        "geometry_version": 1,
        "truth_classification": truth, "confidence": "MEDIUM",
        "units": "METRIC_M", "lifecycle_state": "ACTIVE", "existing_state": enums.EXISTING,
        "opening_ref": opening_ref, "canonical_passport_reference": None,
        "provenance": {"source": "DETERMINISTIC_REFERENCE_FIXTURE"},
        "unknowns": unknowns or [], "dimensions": dimensions,
        "created_by": "fixture", "created_at": now, "updated_at": now,
        "version": 1, "access_classification": "HOMEOWNER",
    }
    rec.update(tags)
    return rec


def build_reference_records():
    """Return the full deterministic record set (pure; no DB, no env gate)."""
    now = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()  # deterministic timestamp
    tags = _fixture_tags(now)

    frames = [
        {"id": FRAME_PROPERTY, "coordinate_frame_id": FRAME_PROPERTY, "frame_type": "PROPERTY_FRAME",
         "parent_frame_id": None, "units": "METRIC_M", "axis_convention": enums.AXIS_CONVENTION,
         "origin_state": "PROVISIONAL", "origin_source": "DETERMINISTIC_REFERENCE_FIXTURE",
         "orientation_source": "assumed_true_north", "elevation_datum_source": "finished_floor_zero",
         "transform_to_parent": IDENTITY_4X4, "transform_to_property": IDENTITY_4X4,
         "tolerance_class": "PLANNING", "residual_error_m": None, "confidence": "LOW",
         "effective_at": now, "version": 1, "validation_state": "VALIDATED", "superseded_by": None,
         "created_at": now, "updated_at": now, **tags},
        {"id": FRAME_ROOM, "coordinate_frame_id": FRAME_ROOM, "frame_type": "ROOM_FRAME",
         "parent_frame_id": FRAME_PROPERTY, "units": "METRIC_M", "axis_convention": enums.AXIS_CONVENTION,
         "origin_state": "PROVISIONAL", "origin_source": "DETERMINISTIC_REFERENCE_FIXTURE",
         "orientation_source": "assumed_true_north", "elevation_datum_source": "finished_floor_zero",
         "transform_to_parent": IDENTITY_4X4, "transform_to_property": IDENTITY_4X4,
         "tolerance_class": "PLANNING", "residual_error_m": None, "confidence": "LOW",
         "effective_at": now, "version": 1, "validation_state": "VALIDATED", "superseded_by": None,
         "created_at": now, "updated_at": now, **tags},
    ]

    room = _entity(ROOM, "ROOM", "Reference Living Room", None, tags, geometry_type="POLYGON",
                   dimensions={"width_m": WIDTH_M, "length_m": LENGTH_M, "height_m": HEIGHT_M,
                               "floor_area_m2": round(WIDTH_M * LENGTH_M, 3)},
                   unknowns=["Concealed wall structure", "Ceiling cavity systems", "Sub-floor condition"])
    entities = [
        room,
        _entity(WALL_N, "WALL", "North Wall", ROOM, tags),
        _entity(WALL_E, "WALL", "East Wall", ROOM, tags),
        _entity(WALL_S, "WALL", "South Wall", ROOM, tags),
        _entity(WALL_W, "WALL", "West Wall", ROOM, tags),
        _entity(FLOOR, "FLOOR", "Floor", ROOM, tags),
        _entity(CEILING, "CEILING", "Ceiling",
                ROOM, tags, truth=enums.ESTIMATED_EXISTING),  # ceiling height estimated
        _entity(OPENING_WINDOW, "OPENING", "Window Opening (South)", WALL_S, tags, geometry_type="POLYGON"),
        _entity(WINDOW, "WINDOW", "Exterior Window", WALL_S, tags, opening_ref=OPENING_WINDOW,
                geometry_type="POLYGON"),
        _entity(OPENING_DOOR, "OPENING", "Door Opening (North)", WALL_N, tags, geometry_type="POLYGON"),
        _entity(DOOR, "DOOR", "Entry Door", WALL_N, tags, opening_ref=OPENING_DOOR, geometry_type="POLYGON"),
        _entity(OPENING_ADJOINING, "OPENING", "Adjoining-Room Opening (East)", WALL_E, tags,
                geometry_type="POLYGON"),
    ]

    artifact = {
        "id": ARTIFACT, "artifact_id": ARTIFACT, "scan_session_id": None, "model_version_id": EXISTING_MODEL,
        "artifact_type": "FLOOR_PLAN", "storage_provider": "deterministic_fixture",
        "storage_object_reference": f"fixture://tenant/{enums.TENANT_ID}/property/{REF_PROPERTY_ID}/reality/{ARTIFACT}",
        "content_type": "image/svg+xml", "file_size": 2048, "checksum_sha256": FLOORPLAN_CHECKSUM,
        "immutability": "DERIVED", "source_artifact_ids": [], "derivation": {"method": "deterministic_fixture"},
        "processor": "reality-fixtures/1.0.0", "processing_status": "READY", "validation_status": "VALID",
        "truth_classification": enums.MEASURED_EXISTING, "access_classification": "HOMEOWNER",
        "encryption_state": "ENCRYPTED_AT_REST", "retention_classification": "DERIVED_REGENERABLE",
        "signed_access_required": True, "created_at": now, "version": 1, "superseded_by": None, **tags,
    }

    existing_model = {
        "id": EXISTING_MODEL, "existing_model_version_id": EXISTING_MODEL,
        "source_scan_session_ids": [], "spatial_entity_ids": [e["id"] for e in entities],
        "coordinate_frame_version": 1, "artifact_ids": [ARTIFACT],
        "truth_summary": {enums.MEASURED_EXISTING: 11, enums.ESTIMATED_EXISTING: 1},
        "quality_summary": {"coverage_state": "COMPLETE", "mean_confidence": "MEDIUM"},
        "unknown_areas": ["Concealed wall structure", "Ceiling cavity systems"],
        "model_state": enums.EM_DRAFT_CANDIDATE, "accepted_at": None, "accepted_by": None,
        "previous_version_id": None, "immutable": False, "version": 1,
        "created_at": now, "updated_at": now, **tags,
    }

    return {"frames": frames, "entities": entities, "artifact": artifact, "existing_model": existing_model,
            "property_id": REF_PROPERTY_ID, "fixture_version": FIXTURE_VERSION}


def assert_fixtures_enabled():
    """Fail closed in production (raises FixtureDisabledError)."""
    fx.require_fixtures(SOURCE_LABEL)


async def bootstrap(db, user):
    """Idempotent upsert of the deterministic reference room. Fails closed in production."""
    assert_fixtures_enabled()
    data = build_reference_records()

    async def _upsert(coll, rec):
        await db[coll].update_one({"id": rec["id"]}, {"$setOnInsert": rec}, upsert=True)

    for fr in data["frames"]:
        await _upsert(enums.C_FRAMES, fr)
    for e in data["entities"]:
        await _upsert(enums.C_SPATIAL, e)
    await _upsert(enums.C_ARTIFACTS, data["artifact"])
    await _upsert(enums.C_EXISTING, data["existing_model"])

    await write_event(db, enums.A_REFERENCE_ROOM_BOOTSTRAPPED, user, property_id=REF_PROPERTY_ID,
                      correlation_id="rf-corr-h014a",
                      extra={"fixture_version": FIXTURE_VERSION, "entity_count": len(data["entities"]),
                             "authoritative": False})
    return await assemble_view(db)


async def assemble_view(db):
    """Read-only assembled reference-room view for the API/screen."""
    pid = REF_PROPERTY_ID
    entities = [e async for e in db[enums.C_SPATIAL].find({"property_id": pid}, {"_id": 0})]
    frames = [f async for f in db[enums.C_FRAMES].find({"property_id": pid}, {"_id": 0})]
    artifact = await db[enums.C_ARTIFACTS].find_one({"id": ARTIFACT}, {"_id": 0})
    existing = await db[enums.C_EXISTING].find_one({"id": EXISTING_MODEL}, {"_id": 0})
    counts = {}
    truth_counts = {}
    for e in entities:
        counts[e["entity_type"]] = counts.get(e["entity_type"], 0) + 1
        tc = e.get("truth_classification", enums.UNKNOWN)
        truth_counts[tc] = truth_counts.get(tc, 0) + 1
    from .artifact_service import public_view
    return {
        "authoritative": False,
        "environment": {"mode": fx.habitat_env(), "fixtures_enabled": fx.fixtures_enabled(),
                        "non_authoritative_notice":
                            "Deterministic development/test fixture — NOT canonical Property Passport truth."},
        "property_id": pid,
        "fixture_version": FIXTURE_VERSION,
        "dimensions_m": {"width": WIDTH_M, "length": LENGTH_M, "height": HEIGHT_M,
                         "floor_area_m2": round(WIDTH_M * LENGTH_M, 3)},
        "coordinate_frames": frames,
        "entity_count": len(entities),
        "entity_counts_by_type": counts,
        "truth_classification_counts": truth_counts,
        "unknowns": (next((e for e in entities if e["id"] == ROOM), {}) or {}).get("unknowns", []),
        "artifact_manifest": public_view(artifact) if artifact else None,
        "existing_model_version": existing,
        "entities": entities,
    }
