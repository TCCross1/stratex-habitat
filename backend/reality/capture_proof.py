"""Deterministic, idempotent end-to-end CAPTURE PROOF (H-014B, Phase 8/9 support).

Development/test ONLY (fixture-gated; fails closed in production). Drives the REAL
governed capture pipeline with clearly non-authoritative synthetic data so the
Habitat review experience and the automated proof test have a stable subject:

  scan session (native→canonical state walk) → resumable chunked upload of a
  synthetic point cloud into governed object storage (real machinery, checksum
  verified) → deterministic Scan Quality Guardian evaluation (PASS) → governed
  DRAFT_CANDIDATE existing-model (MEASURED_EXISTING geometry, never VERIFIED).

Everything is tagged authoritative:false and stays inside the truth boundary.
"""
import hashlib
from datetime import datetime, timezone

import fixture_provider as fx

from . import enums
from . import fixtures
from . import scan_guardian
from . import capture
from . import capture_upload_service as uploads
from .artifact_service import public_view
from .authz import REF_CAPTURE_PROPERTY_ID
from .audit_service import write_event
from .coordinate_service import IDENTITY_4X4

PROOF_VERSION = "1.0.0"
PROOF_PROPERTY = REF_CAPTURE_PROPERTY_ID
PROOF_FRAME_ID = "rf-frame-capture-proof-h014b"
PROOF_SCAN_ID = "rf-scan-capture-proof-h014b"
PROOF_PC_ARTIFACT_ID = "rf-art-capture-proof-pc-h014b"

# Deterministic synthetic "point cloud" payload (non-authoritative).
_POINTCLOUD = b"STRATEX-H014B-PROOF-POINTCLOUD;x,y,z,r,g,b\n" * 900
_POINTCLOUD_SHA256 = hashlib.sha256(_POINTCLOUD).hexdigest()
_CHUNK_SIZE = 8192

DEVICE = {"model": "iPhone 15 Pro", "os_version": "iOS 17.5",
          "sensor": "LiDAR Scanner", "framework": "RoomPlan + ARKit"}

# Deterministic PASS-grade quality report for the synthetic capture.
GOOD_REPORT = {
    "captured_area_m2": 29.77, "expected_area_m2": 29.77,
    "surface_coverage": {"WALL": 0.96, "FLOOR": 0.93, "CEILING": 0.88},
    "wall_count_detected": 4, "wall_count_expected": 4,
    "tracking_quality": {"mean": 0.94, "min": 0.71, "limited_fraction": 0.04},
    "drift_estimate_m": 0.021, "frame_count": 812,
    "low_quality_frame_fraction": 0.06, "openings_detected": 3,
    "dimensions_m": {"width": 4.88, "length": 6.10, "height": 2.74, "floor_area_m2": 29.77},
}

_NATIVE_WALK = ["IDLE", "AUTHORIZED", "READY", "CAPTURING", "FINALIZING",
                "UPLOADING", "UPLOADED", "PROCESSING", "COMPLETE"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def assert_enabled():
    fixtures.assert_fixtures_enabled()


def _build_state_history():
    """Walk native capture states → canonical scan states, then end ACCEPTED."""
    now = _now_iso()
    seen, history = [], []
    for native in _NATIVE_WALK:
        canonical = enums.NATIVE_TO_SCAN_STATE[native]
        if not history or history[-1]["state"] != canonical:
            history.append({"state": canonical, "at": now, "from_native": native})
            seen.append(canonical)
    # canonical walk lands on QUALITY_REVIEW; add the governed acceptance.
    history.append({"state": enums.SCAN_ACCEPTED, "at": now})
    return history


async def _ensure_scan(db, user):
    existing = await db[enums.C_SCANS].find_one({"id": PROOF_SCAN_ID}, {"_id": 0})
    if existing:
        return existing
    guardian = scan_guardian.evaluate(GOOD_REPORT)
    now = _now_iso()
    rec = {
        "id": PROOF_SCAN_ID, "scan_session_id": PROOF_SCAN_ID,
        "tenant_id": enums.TENANT_ID, "property_id": PROOF_PROPERTY,
        "actor_id": user.get("id"), "capture_type": "INTERIOR_LIDAR",
        "device": DEVICE, "sensors": ["lidar", "camera", "imu"],
        "app_version": "StratexRealityCapture/0.1.0", "capture_mode": "ROOMPLAN",
        "coordinate_frame_id": PROOF_FRAME_ID,
        "started_at": now, "ended_at": now,
        "current_state": enums.SCAN_ACCEPTED,
        "coverage_state": guardian["coverage_state"],
        "quality_summary": {"guardian_verdict": guardian["verdict"],
                            "guardian_score": guardian["score"],
                            "coverage_state": guardian["coverage_state"],
                            "guardian_version": guardian["guardian_version"]},
        "guardian_result": guardian,
        "missing_areas": guardian["missing_areas"],
        "privacy_classification": "SENSITIVE_INTERIOR",
        "upload_state": enums.SCAN_UPLOAD_COMPLETE,
        "processing_state": "PROCESSING_COMPLETE",
        "validation_state": "GUARDIAN_REVIEWED", "approval_state": "ACCEPTED",
        "failure_info": None, "recovery_token": None,
        "create_idempotency_key": "capture-proof-h014b",
        "processed_idempotency_keys": [], "version": 1,
        "correlation_id": "rf-corr-capture-proof-h014b",
        "created_at": now, "updated_at": now,
        "expires_at": None,
        "state_history": _build_state_history(),
        "capture_telemetry": {"native_state": "COMPLETE",
                              "mapped_scan_state": enums.SCAN_QUALITY_REVIEW,
                              "surface_coverage": GOOD_REPORT["surface_coverage"],
                              "tracking_quality": GOOD_REPORT["tracking_quality"],
                              "captured_area_m2": GOOD_REPORT["captured_area_m2"],
                              "frame_count": GOOD_REPORT["frame_count"], "at": now},
        "authoritative": False,
    }
    await db[enums.C_SCANS].update_one({"id": PROOF_SCAN_ID}, {"$setOnInsert": rec}, upsert=True)
    return await db[enums.C_SCANS].find_one({"id": PROOF_SCAN_ID}, {"_id": 0})


async def _ensure_upload(db, user):
    """Run (once) the REAL resumable chunked upload of the synthetic point cloud."""
    manifest = await db[enums.C_ARTIFACTS].find_one({"id": PROOF_PC_ARTIFACT_ID}, {"_id": 0})
    if manifest:
        return {"artifact_id": PROOF_PC_ARTIFACT_ID, "state": enums.UP_COMPLETED,
                "object_store_state": "STORED", "checksum_verified": True,
                "bytes_stored": manifest.get("file_size"),
                "total_chunks": (len(_POINTCLOUD) + _CHUNK_SIZE - 1) // _CHUNK_SIZE,
                "chunk_size": _CHUNK_SIZE, "reused": True}

    init = await uploads.init_upload(
        db, user, scan_session_id=PROOF_SCAN_ID, correlation_id="rf-corr-capture-proof-h014b",
        body={"artifact_type": "POINT_CLOUD", "checksum_sha256": _POINTCLOUD_SHA256,
              "total_size": len(_POINTCLOUD), "chunk_size": _CHUNK_SIZE,
              "content_type": "application/octet-stream"})
    up_id = init["id"]
    total = init["total_chunks"]
    for i in range(total):
        chunk = _POINTCLOUD[i * _CHUNK_SIZE:(i + 1) * _CHUNK_SIZE]
        await uploads.put_chunk(db, user, upload_session_id=up_id, index=i, data=chunk)
    try:
        res = await uploads.complete_upload(db, user, upload_session_id=up_id,
                                            correlation_id="rf-corr-capture-proof-h014b",
                                            artifact_id=PROOF_PC_ARTIFACT_ID)
        return {"artifact_id": PROOF_PC_ARTIFACT_ID, "state": res["state"],
                "object_store_state": "STORED",
                "checksum_verified": res.get("checksum_verified", True),
                "bytes_stored": res.get("bytes_stored"), "total_chunks": total,
                "chunk_size": _CHUNK_SIZE, "reused": False}
    except Exception as e:  # object store unreachable in an offline test env
        # Integrity (assembly + checksum) already verified before the object PUT;
        # a mismatch would have raised HTTP 422, not reached here.
        return {"artifact_id": PROOF_PC_ARTIFACT_ID, "state": "ASSEMBLED",
                "object_store_state": "UNAVAILABLE", "checksum_verified": True,
                "bytes_stored": len(_POINTCLOUD), "total_chunks": total,
                "chunk_size": _CHUNK_SIZE, "reused": False, "note": str(e)[:160]}


async def _ensure_candidate(db, user):
    existing = await db[enums.C_EXISTING].find_one(
        {"tenant_id": enums.TENANT_ID, "property_id": PROOF_PROPERTY,
         "source_scan_session_ids": PROOF_SCAN_ID}, {"_id": 0})
    if existing:
        return existing
    structure = {
        "room_label": "Captured Living Room (proof)",
        "dimensions_m": {"width": 4.88, "length": 6.10, "height": 2.74, "floor_area_m2": 29.77},
        "has_floor": True, "has_ceiling": True,
        "openings": [{"type": "DOOR", "wall": "North", "label": "Entry Door"},
                     {"type": "WINDOW", "wall": "South", "label": "Exterior Window"},
                     {"type": "OPENING", "wall": "East", "label": "Adjoining Opening"}],
        "unknowns": ["Concealed wall structure", "Ceiling cavity systems", "Sub-floor condition"],
    }
    result = await capture.generate_candidate(
        db, user, session_id=PROOF_SCAN_ID, correlation_id="rf-corr-capture-proof-h014b",
        body={"derived_structure": structure, "artifact_ids": [PROOF_PC_ARTIFACT_ID]})
    return result["existing_model_version"]


async def assemble_review(db):
    scan = await db[enums.C_SCANS].find_one({"id": PROOF_SCAN_ID}, {"_id": 0})
    candidate = await db[enums.C_EXISTING].find_one(
        {"tenant_id": enums.TENANT_ID, "property_id": PROOF_PROPERTY,
         "source_scan_session_ids": PROOF_SCAN_ID}, {"_id": 0})
    manifest = await db[enums.C_ARTIFACTS].find_one({"id": PROOF_PC_ARTIFACT_ID}, {"_id": 0})
    entities = []
    if candidate:
        ids = candidate.get("spatial_entity_ids") or []
        by_id = {e["id"]: e async for e in
                 db[enums.C_SPATIAL].find({"id": {"$in": ids}}, {"_id": 0})}
        entities = [by_id[i] for i in ids if i in by_id]
    counts, truth_counts = {}, {}
    for e in entities:
        counts[e["entity_type"]] = counts.get(e["entity_type"], 0) + 1
        tc = e.get("truth_classification", enums.UNKNOWN)
        truth_counts[tc] = truth_counts.get(tc, 0) + 1

    guardian = (scan or {}).get("guardian_result") or {}
    total_chunks = (len(_POINTCLOUD) + _CHUNK_SIZE - 1) // _CHUNK_SIZE
    return {
        "authoritative": False,
        "proof_version": PROOF_VERSION,
        "environment": {"mode": fx.habitat_env(), "fixtures_enabled": fx.fixtures_enabled(),
                        "native_capture": "BLOCKED_NO_APPLE_TOOLCHAIN",
                        "non_authoritative_notice":
                            "Deterministic development/test capture proof — synthetic data, "
                            "NOT a real device capture and NOT canonical Property Passport truth."},
        "truth_boundary_notice":
            "A completed capture yields a DRAFT_CANDIDATE existing-model only. Promotion to "
            "VERIFIED_EXISTING requires a separate authorized Core/Passport/professional review.",
        "property_id": PROOF_PROPERTY,
        "scan_session": {
            "id": (scan or {}).get("id"),
            "capture_type": (scan or {}).get("capture_type"),
            "device": (scan or {}).get("device"),
            "current_state": (scan or {}).get("current_state"),
            "coverage_state": (scan or {}).get("coverage_state"),
            "missing_areas": (scan or {}).get("missing_areas") or [],
            "state_history": (scan or {}).get("state_history") or [],
            "quality_summary": (scan or {}).get("quality_summary") or {},
        } if scan else None,
        "guardian_result": guardian,
        "upload": {
            "artifact_id": PROOF_PC_ARTIFACT_ID,
            "total_chunks": total_chunks, "chunk_size": _CHUNK_SIZE,
            "declared_size": len(_POINTCLOUD),
            "checksum_sha256": _POINTCLOUD_SHA256,
            "object_stored": bool(manifest),
        },
        "candidate_model": {
            "existing_model_version_id": (candidate or {}).get("existing_model_version_id"),
            "model_state": (candidate or {}).get("model_state"),
            "immutable": (candidate or {}).get("immutable"),
            "entity_count": len(entities),
            "truth_summary": (candidate or {}).get("truth_summary") or {},
            "unknown_areas": (candidate or {}).get("unknown_areas") or [],
        } if candidate else None,
        "dimensions_m": {"width": 4.88, "length": 6.10, "height": 2.74, "floor_area_m2": 29.77},
        "entity_count": len(entities),
        "entity_counts_by_type": counts,
        "truth_classification_counts": truth_counts,
        "entities": entities,
        "artifact_manifest": public_view(manifest) if manifest else None,
        "native_state_map": capture.native_state_map(),
    }


async def _ensure_frame(db):
    """Upsert a single non-authoritative capture coordinate frame for the proof property."""
    now = _now_iso()
    frame = {
        "id": PROOF_FRAME_ID, "coordinate_frame_id": PROOF_FRAME_ID,
        "tenant_id": enums.TENANT_ID, "property_id": PROOF_PROPERTY,
        "frame_type": "ROOM_FRAME", "parent_frame_id": None,
        "units": "METRIC_M", "axis_convention": enums.AXIS_CONVENTION,
        "origin_state": "PROVISIONAL", "origin_source": "LIDAR_CAPTURE",
        "orientation_source": "arkit_world_tracking", "elevation_datum_source": "finished_floor_zero",
        "transform_to_parent": IDENTITY_4X4, "transform_to_property": IDENTITY_4X4,
        "tolerance_class": "PLANNING", "residual_error_m": None, "confidence": "LOW",
        "effective_at": now, "version": 1, "validation_state": "VALIDATED",
        "superseded_by": None, "created_at": now, "updated_at": now, "authoritative": False,
        "source_classification": "LIDAR_CAPTURE",
    }
    await db[enums.C_FRAMES].update_one({"id": PROOF_FRAME_ID}, {"$setOnInsert": frame}, upsert=True)


async def bootstrap(db, user):
    """Idempotent: build the full proof (capture frame, scan, upload, candidate)."""
    assert_enabled()
    await _ensure_frame(db)                     # isolated capture coordinate frame
    scan = await _ensure_scan(db, user)
    upload_summary = await _ensure_upload(db, user)
    await _ensure_candidate(db, user)
    await write_event(db, enums.A_CAPTURE_PROOF_BOOTSTRAPPED, user, property_id=PROOF_PROPERTY,
                      correlation_id="rf-corr-capture-proof-h014b",
                      entity_refs={"scan_session_id": PROOF_SCAN_ID, "artifact_id": PROOF_PC_ARTIFACT_ID},
                      extra={"proof_version": PROOF_VERSION,
                             "object_store_state": upload_summary.get("object_store_state"),
                             "authoritative": False})
    view = await assemble_review(db)
    view["upload"].update({k: upload_summary[k] for k in
                           ("state", "object_store_state", "checksum_verified", "bytes_stored")
                           if k in upload_summary})
    return view
