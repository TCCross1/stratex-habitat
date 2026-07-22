"""Reality Studio versioned API router — mounted at /api/reality/v1 (Phase 11)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException

from steward import get_db, get_steward_user  # reuse tested auth + DB DI (no cycle)
from fixture_provider import FixtureDisabledError

from . import enums
from .authz import authorize_property, structured, REF_PROPERTY_ID
from . import coordinate_service, spatial_service, scan_session_service
from . import artifact_service, model_version_service, fixtures
from .schemas import (CoordinateFrameCreate, SpatialEntityCreate, ScanSessionCreate,
                      ScanTransition, ArtifactManifestCreate, ExistingModelCreate,
                      ExistingModelTransition, DesignModelCreate)

reality_router = APIRouter(prefix=enums.API_PREFIX, tags=["reality"])


def _corr():
    return str(uuid.uuid4())


# --- Spatial graph -------------------------------------------------------
@reality_router.get("/properties/{property_id}/spatial-graph")
async def spatial_graph(property_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    return await spatial_service.get_spatial_graph(db, property_id)


@reality_router.post("/properties/{property_id}/spatial-entities", status_code=201)
async def create_entity(property_id: str, body: SpatialEntityCreate,
                        user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    return await spatial_service.create_entity(db, user, property_id=property_id,
                                               body=body.model_dump(), correlation_id=_corr())


# --- Coordinate frames ---------------------------------------------------
@reality_router.post("/properties/{property_id}/coordinate-frames", status_code=201)
async def create_frame(property_id: str, body: CoordinateFrameCreate,
                       user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    return await coordinate_service.create_frame(db, user, property_id=property_id,
                                                 body=body.model_dump(), correlation_id=_corr())


@reality_router.get("/properties/{property_id}/coordinate-frames")
async def list_frames(property_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    cur = db[enums.C_FRAMES].find({"tenant_id": enums.TENANT_ID, "property_id": property_id}, {"_id": 0})
    return {"property_id": property_id, "coordinate_frames": [f async for f in cur]}


@reality_router.get("/coordinate-frames/{coordinate_frame_id}")
async def get_frame(coordinate_frame_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    frame = await db[enums.C_FRAMES].find_one({"id": coordinate_frame_id}, {"_id": 0})
    if not frame:
        raise HTTPException(status_code=404, detail="Coordinate frame not found")
    await authorize_property(db, user, frame["property_id"])
    return frame


# --- Scan sessions -------------------------------------------------------
@reality_router.post("/properties/{property_id}/scan-sessions", status_code=201)
async def create_scan(property_id: str, body: ScanSessionCreate,
                      user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    return await scan_session_service.create_session(db, user, property_id=property_id,
                                                      body=body.model_dump(), correlation_id=_corr())


@reality_router.get("/scan-sessions/{scan_session_id}")
async def get_scan(scan_session_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    s = await db[enums.C_SCANS].find_one({"id": scan_session_id}, {"_id": 0})
    if not s:
        raise HTTPException(status_code=404, detail="Scan session not found")
    await authorize_property(db, user, s["property_id"])
    return s


@reality_router.post("/scan-sessions/{scan_session_id}/transition")
async def transition_scan(scan_session_id: str, body: ScanTransition,
                          user=Depends(get_steward_user), db=Depends(get_db)):
    s = await db[enums.C_SCANS].find_one({"id": scan_session_id}, {"_id": 0})
    if not s:
        raise HTTPException(status_code=404, detail="Scan session not found")
    await authorize_property(db, user, s["property_id"])
    return await scan_session_service.transition_session(
        db, user, session_id=scan_session_id, to_state=body.to_state,
        expected_version=body.expected_version, idempotency_key=body.idempotency_key)


# --- Artifact manifests --------------------------------------------------
@reality_router.post("/scan-sessions/{scan_session_id}/artifacts", status_code=201)
async def create_artifact(scan_session_id: str, body: ArtifactManifestCreate,
                          user=Depends(get_steward_user), db=Depends(get_db)):
    s = await db[enums.C_SCANS].find_one({"id": scan_session_id}, {"_id": 0})
    if not s:
        raise HTTPException(status_code=404, detail="Scan session not found")
    await authorize_property(db, user, s["property_id"])
    return await artifact_service.create_manifest(db, user, scan_session_id=scan_session_id,
                                                  body=body.model_dump(), correlation_id=_corr())


@reality_router.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    m = await db[enums.C_ARTIFACTS].find_one({"id": artifact_id}, {"_id": 0})
    if not m:
        raise HTTPException(status_code=404, detail="Artifact manifest not found")
    await authorize_property(db, user, m["property_id"])
    return artifact_service.public_view(m)


# --- Existing model versions ---------------------------------------------
@reality_router.post("/properties/{property_id}/existing-models", status_code=201)
async def create_existing(property_id: str, body: ExistingModelCreate,
                          user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    return await model_version_service.create_existing_model(
        db, user, property_id=property_id, body=body.model_dump(), correlation_id=_corr())


@reality_router.get("/existing-models/{existing_model_version_id}")
async def get_existing(existing_model_version_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    m = await db[enums.C_EXISTING].find_one({"id": existing_model_version_id}, {"_id": 0})
    if not m:
        raise HTTPException(status_code=404, detail="Existing model version not found")
    await authorize_property(db, user, m["property_id"])
    return m


@reality_router.post("/existing-models/{existing_model_version_id}/transition")
async def transition_existing(existing_model_version_id: str, body: ExistingModelTransition,
                              user=Depends(get_steward_user), db=Depends(get_db)):
    m = await db[enums.C_EXISTING].find_one({"id": existing_model_version_id}, {"_id": 0})
    if not m:
        raise HTTPException(status_code=404, detail="Existing model version not found")
    await authorize_property(db, user, m["property_id"])
    return await model_version_service.transition_existing_model(
        db, user, model_id=existing_model_version_id, to_state=body.to_state,
        expected_version=body.expected_version)


# --- Design model versions -----------------------------------------------
@reality_router.post("/properties/{property_id}/design-models", status_code=201)
async def create_design(property_id: str, body: DesignModelCreate,
                        user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, property_id)
    return await model_version_service.create_design_model(
        db, user, property_id=property_id, body=body.model_dump(), correlation_id=_corr())


@reality_router.get("/design-models/{design_model_version_id}")
async def get_design(design_model_version_id: str, user=Depends(get_steward_user), db=Depends(get_db)):
    m = await db[enums.C_DESIGN].find_one({"id": design_model_version_id}, {"_id": 0})
    if not m:
        raise HTTPException(status_code=404, detail="Design model version not found")
    await authorize_property(db, user, m["property_id"])
    return m


# --- Reference room (development/test only; fail closed in production) ----
@reality_router.post("/development/reference-room/bootstrap")
async def bootstrap_reference_room(user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, REF_PROPERTY_ID)
    try:
        return await fixtures.bootstrap(db, user)
    except FixtureDisabledError:
        raise structured(403, "FIXTURES_DISABLED",
                         "Reference-room fixtures are disabled (production fail-closed).")


@reality_router.get("/development/reference-room")
async def get_reference_room(user=Depends(get_steward_user), db=Depends(get_db)):
    await authorize_property(db, user, REF_PROPERTY_ID)
    try:
        fixtures.assert_fixtures_enabled()
    except FixtureDisabledError:
        raise structured(403, "FIXTURES_DISABLED",
                         "Reference-room fixtures are disabled (production fail-closed).")
    return await fixtures.assemble_view(db)
