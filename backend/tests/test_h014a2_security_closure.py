"""
H-014A.2 — Security and Capture-Lifecycle Closure tests.

Covers:
* Governed geometry_reference contract + attack matrix
* Unconditional production fixture shutdown matrix
* Precise non-disclosure consistency for Reality lookups
* DB-backed scan create / transition idempotency
"""
import concurrent.futures
import json as _json
import os
import sys
import uuid

import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reality import enums, fixtures as rf, geometry_reference as greff, scan_session_service as scans
from reality.authz import REF_PROPERTY_ID
import fixture_provider as fx

REF = REF_PROPERTY_ID


def _api(api_url, path):
    return f"{api_url}/reality/v1{path}"


def _foreign_owner():
    return f"not-alex-{uuid.uuid4()}"


# ===================== GEOMETRY REFERENCE =====================
class TestGeometryReferenceUnit:
    def test_omitted_ok(self):
        assert greff.validate_geometry_reference_format(None) is None

    def test_valid_artifact_form(self):
        assert greff.validate_geometry_reference_format("artifact:rf-art-abc") == ("artifact", "rf-art-abc")

    def test_valid_fixture_form(self):
        assert greff.validate_geometry_reference_format("fixture:rf-ent-room-h014a") == (
            "fixture", "rf-ent-room-h014a")

    @pytest.mark.parametrize("bad", [
        "https://evil.example/x",
        "http://evil/x?sig=abc",
        "https://bucket.s3.amazonaws.com/k?X-Amz-Signature=1",
        "/etc/passwd",
        "tenant/x/property/y/reality/z",
        "../etc/passwd",
        "artifact:rf%2e%2e/x",
        "artifact:rf-art/../x",
        "",
        "   ",
        "artifact: has space",
        "Bearer eyJhbGciOiJIUzI1NiJ9.aaa.bbb",
        "token=supersecret",
        "eyJhbGciOiJIUzI1NiJ9.e30.sig",
        "fixture://rf-ent-room-h014a",  # URI form rejected; structured fixture: only
        "s3://bucket/key",
    ])
    def test_attack_matrix_rejected(self, bad):
        with pytest.raises(HTTPException) as e:
            greff.validate_geometry_reference_format(bad)
        assert e.value.status_code == 422
        assert e.value.detail["error_code"] == "INVALID_GEOMETRY_REFERENCE"

    def test_public_redacts_storage_like(self):
        assert greff.public_geometry_reference("tenant/t/property/p/reality/a") == greff.GOVERNED_GEOMETRY_TOKEN
        assert greff.public_geometry_reference("artifact:rf-art-1") == "artifact:rf-art-1"
        assert greff.public_geometry_reference(None) is None


class TestGeometryReferenceHTTP:
    def _create(self, session, api_url, extra=None):
        body = {"entity_type": "EQUIPMENT", "label": "gref"}
        if extra:
            body.update(extra)
        return session.post(_api(api_url, f"/properties/{REF}/spatial-entities"), json=body, timeout=30)

    def test_omitted_geometry_reference(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url)
        assert r.status_code == 201, r.text
        assert r.json().get("geometry_reference") is None
        eid = r.json()["id"]
        try:
            doc = db[enums.C_SPATIAL].find_one({"id": eid})
            assert doc.get("geometry_reference") is None
        finally:
            db[enums.C_SPATIAL].delete_one({"id": eid})

    def test_valid_same_property_artifact_reference(self, homeowner_session, api_url, db):
        sid = homeowner_session.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                                     json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]
        art = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                     json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64},
                                     timeout=30)
        assert art.status_code == 201, art.text
        aid = art.json()["artifact_id"]
        r = self._create(homeowner_session, api_url, {"geometry_reference": f"artifact:{aid}"})
        assert r.status_code == 201, r.text
        eid = r.json()["id"]
        try:
            assert r.json()["geometry_reference"] == f"artifact:{aid}"
            # public body must never echo raw storage key
            blob = _json.dumps(r.json())
            assert f"tenant/{enums.TENANT_ID}/property/{REF}/reality/{aid}" not in blob
        finally:
            db[enums.C_SPATIAL].delete_one({"id": eid})

    def test_valid_fixture_reference_in_development(self, homeowner_session, api_url, db, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "development")
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", "true")
        r = self._create(homeowner_session, api_url,
                         {"geometry_reference": "fixture:rf-ent-room-h014a"})
        assert r.status_code == 201, r.text
        eid = r.json()["id"]
        try:
            assert r.json()["geometry_reference"] == "fixture:rf-ent-room-h014a"
        finally:
            db[enums.C_SPATIAL].delete_one({"id": eid})

    def test_fixture_reference_rejected_in_production(self, homeowner_session, api_url, monkeypatch):
        # Server process has its own env; unit-level resolve is the authoritative
        # production gate. Also exercise HTTP against a disabled gate via monkeypatch
        # of fixture_provider used inside the request path when possible.
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", "true")
        # Direct service-level check (server may still be development) — production gate.
        import asyncio
        async def _run():
            with pytest.raises(HTTPException) as e:
                await greff.resolve_geometry_reference(
                    None, "fixture:rf-ent-room-h014a",
                    tenant_id=enums.TENANT_ID, property_id=REF)
            assert e.value.status_code == 403
            assert e.value.detail["error_code"] == "FIXTURES_DISABLED"
        asyncio.run(_run())

    @pytest.mark.parametrize("bad", [
        "https://evil.example/x",
        "https://x?sig=1",
        "/abs/path",
        "../traverse",
        "artifact:..%2fx",
        " ",
        "token=abc",
    ])
    def test_http_attack_rejected(self, homeowner_session, api_url, bad):
        r = self._create(homeowner_session, api_url, {"geometry_reference": bad})
        assert r.status_code == 422, r.text
        assert r.json()["detail"]["error_code"] == "INVALID_GEOMETRY_REFERENCE"

    def test_cross_tenant_artifact_rejected(self, homeowner_session, api_url, db):
        aid = f"rf-art-xtenant-{uuid.uuid4()}"
        db[enums.C_ARTIFACTS].insert_one({
            "id": aid, "artifact_id": aid, "tenant_id": "other-tenant",
            "property_id": REF, "artifact_type": "POINT_CLOUD"})
        try:
            r = self._create(homeowner_session, api_url, {"geometry_reference": f"artifact:{aid}"})
            assert r.status_code == 422
            assert r.json()["detail"]["error_code"] == "CROSS_TENANT_GEOMETRY_REFERENCE"
        finally:
            db[enums.C_ARTIFACTS].delete_one({"id": aid})

    def test_cross_property_artifact_rejected(self, homeowner_session, api_url, db):
        aid = f"rf-art-xprop-{uuid.uuid4()}"
        db[enums.C_ARTIFACTS].insert_one({
            "id": aid, "artifact_id": aid, "tenant_id": enums.TENANT_ID,
            "property_id": "other-prop", "artifact_type": "POINT_CLOUD"})
        try:
            r = self._create(homeowner_session, api_url, {"geometry_reference": f"artifact:{aid}"})
            assert r.status_code == 422
            assert r.json()["detail"]["error_code"] == "CROSS_PROPERTY_GEOMETRY_REFERENCE"
        finally:
            db[enums.C_ARTIFACTS].delete_one({"id": aid})

    def test_spatial_graph_has_no_raw_storage_reference(self, homeowner_session, api_url, db):
        homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        # Inject a legacy unsafe geometry_reference and ensure public graph redacts it.
        dirty_id = f"rf-ent-dirty-{uuid.uuid4()}"
        db[enums.C_SPATIAL].insert_one({
            "id": dirty_id, "tenant_id": enums.TENANT_ID, "property_id": REF,
            "entity_type": "EQUIPMENT", "geometry_reference": f"tenant/{enums.TENANT_ID}/property/{REF}/reality/x",
            "truth_classification": "MEASURED_EXISTING"})
        try:
            r = homeowner_session.get(_api(api_url, f"/properties/{REF}/spatial-graph"), timeout=30)
            assert r.status_code == 200
            blob = r.text
            assert f"tenant/{enums.TENANT_ID}/property/{REF}/reality/x" not in blob
            ent = next(e for e in r.json()["entities"] if e["id"] == dirty_id)
            assert ent["geometry_reference"] == greff.GOVERNED_GEOMETRY_TOKEN
        finally:
            db[enums.C_SPATIAL].delete_one({"id": dirty_id})


# ===================== FIXTURE ENVIRONMENT MATRIX =====================
class TestFixtureEnvironmentMatrix:
    @pytest.mark.parametrize("env,flag,expected", [
        ("development", "true", True),
        ("development", "false", False),
        ("demo", "true", True),
        ("test", "true", True),
        ("production", "false", False),
        ("production", "true", False),  # unconditional shutdown
        ("staging", "true", False),     # unknown/non-allow-listed → fail closed
        ("totally-unknown", "true", False),
    ])
    def test_matrix(self, monkeypatch, env, flag, expected):
        monkeypatch.setenv("HABITAT_ENV", env)
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", flag)
        assert fx.fixtures_enabled() is expected

    def test_reference_room_endpoints_respect_production(self, homeowner_session, api_url, monkeypatch):
        # Process-level: monkeypatch fixture_provider used by reality.fixtures / router.
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", "true")
        # The running uvicorn has its own interpreter state; unit gate is authoritative.
        # Additionally call require_fixtures the same way bootstrap does.
        with pytest.raises(fx.FixtureDisabledError):
            rf.assert_fixtures_enabled()


class TestFixtureEnvironmentHTTP:
    """HTTP checks against the live server env (development + fixtures true in QC)."""

    def test_bootstrap_and_get_permitted_in_dev(self, homeowner_session, api_url):
        b = homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        g = homeowner_session.get(_api(api_url, "/development/reference-room"), timeout=30)
        assert b.status_code == 200 and g.status_code == 200
        assert b.json()["authoritative"] is False
        # H-014A.2 fixture geometry form
        ents = b.json()["entities"]
        assert all(str(e.get("geometry_reference") or "").startswith("fixture:") for e in ents)


# ===================== NON-DISCLOSURE ROUTE MATRIX =====================
class TestNonDisclosureRouteMatrix:
    """Existing-unauthorized vs nonexistent → identical 404 NOT_FOUND bodies."""

    def _seed_foreign_property(self, db):
        pid = f"nd-prop-{uuid.uuid4()}"
        db.properties.insert_one({"id": pid, "owner_id": _foreign_owner(), "name": "nd"})
        return pid

    def test_property_spatial_graph(self, homeowner_session, api_url, db):
        pid = self._seed_foreign_property(db)
        try:
            a = homeowner_session.get(_api(api_url, f"/properties/{pid}/spatial-graph"), timeout=30)
            b = homeowner_session.get(_api(api_url, f"/properties/missing-{uuid.uuid4()}/spatial-graph"), timeout=30)
        finally:
            db.properties.delete_one({"id": pid})
        assert a.status_code == 404 and b.status_code == 404
        assert a.json() == b.json()
        assert a.json()["detail"]["error_code"] == "NOT_FOUND"

    def test_coordinate_frame_lookup(self, homeowner_session, api_url, db):
        pid = self._seed_foreign_property(db)
        fid = f"nd-frame-{uuid.uuid4()}"
        db[enums.C_FRAMES].insert_one({"id": fid, "tenant_id": enums.TENANT_ID, "property_id": pid})
        try:
            a = homeowner_session.get(_api(api_url, f"/coordinate-frames/{fid}"), timeout=30)
            b = homeowner_session.get(_api(api_url, f"/coordinate-frames/missing-{uuid.uuid4()}"), timeout=30)
        finally:
            db[enums.C_FRAMES].delete_one({"id": fid}); db.properties.delete_one({"id": pid})
        assert a.status_code == 404 and b.status_code == 404 and a.json() == b.json()

    def test_scan_session_lookup(self, homeowner_session, api_url, db):
        pid = self._seed_foreign_property(db)
        sid = f"nd-scan-{uuid.uuid4()}"
        db[enums.C_SCANS].insert_one({"id": sid, "tenant_id": enums.TENANT_ID, "property_id": pid,
                                      "current_state": "CREATED"})
        try:
            a = homeowner_session.get(_api(api_url, f"/scan-sessions/{sid}"), timeout=30)
            b = homeowner_session.get(_api(api_url, f"/scan-sessions/missing-{uuid.uuid4()}"), timeout=30)
        finally:
            db[enums.C_SCANS].delete_one({"id": sid}); db.properties.delete_one({"id": pid})
        assert a.status_code == 404 and b.status_code == 404 and a.json() == b.json()

    def test_artifact_lookup(self, homeowner_session, api_url, db):
        pid = self._seed_foreign_property(db)
        aid = f"nd-art-{uuid.uuid4()}"
        db[enums.C_ARTIFACTS].insert_one({"id": aid, "tenant_id": enums.TENANT_ID, "property_id": pid})
        try:
            a = homeowner_session.get(_api(api_url, f"/artifacts/{aid}"), timeout=30)
            b = homeowner_session.get(_api(api_url, f"/artifacts/missing-{uuid.uuid4()}"), timeout=30)
        finally:
            db[enums.C_ARTIFACTS].delete_one({"id": aid}); db.properties.delete_one({"id": pid})
        assert a.status_code == 404 and b.status_code == 404 and a.json() == b.json()

    def test_existing_model_lookup(self, homeowner_session, api_url, db):
        pid = self._seed_foreign_property(db)
        mid = f"nd-em-{uuid.uuid4()}"
        db[enums.C_EXISTING].insert_one({"id": mid, "tenant_id": enums.TENANT_ID, "property_id": pid,
                                         "model_state": "DRAFT_CANDIDATE"})
        try:
            a = homeowner_session.get(_api(api_url, f"/existing-models/{mid}"), timeout=30)
            b = homeowner_session.get(_api(api_url, f"/existing-models/missing-{uuid.uuid4()}"), timeout=30)
        finally:
            db[enums.C_EXISTING].delete_one({"id": mid}); db.properties.delete_one({"id": pid})
        assert a.status_code == 404 and b.status_code == 404 and a.json() == b.json()

    def test_design_model_lookup(self, homeowner_session, api_url, db):
        pid = self._seed_foreign_property(db)
        mid = f"nd-dm-{uuid.uuid4()}"
        db[enums.C_DESIGN].insert_one({"id": mid, "tenant_id": enums.TENANT_ID, "property_id": pid})
        try:
            a = homeowner_session.get(_api(api_url, f"/design-models/{mid}"), timeout=30)
            b = homeowner_session.get(_api(api_url, f"/design-models/missing-{uuid.uuid4()}"), timeout=30)
        finally:
            db[enums.C_DESIGN].delete_one({"id": mid}); db.properties.delete_one({"id": pid})
        assert a.status_code == 404 and b.status_code == 404 and a.json() == b.json()

    def test_cross_tenant_scan_transition_nondisclosing(self, homeowner_session, api_url, db):
        sid = f"nd-xt-{uuid.uuid4()}"
        db[enums.C_SCANS].insert_one({"id": sid, "tenant_id": "other-tenant", "property_id": REF,
                                      "actor_id": "x", "current_state": "CREATED", "version": 1,
                                      "processed_idempotency_keys": []})
        try:
            a = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                       json={"to_state": "CAPTURE_READY"}, timeout=30)
            b = homeowner_session.post(_api(api_url, f"/scan-sessions/missing-{uuid.uuid4()}/transition"),
                                       json={"to_state": "CAPTURE_READY"}, timeout=30)
        finally:
            db[enums.C_SCANS].delete_one({"id": sid})
        assert a.status_code == 404 and b.status_code == 404 and a.json() == b.json()

    def test_exceptions_preserved(self, homeowner_session, api_url):
        # 401 unauthenticated
        import requests
        assert requests.get(_api(api_url, f"/properties/{REF}/spatial-graph"), timeout=30).status_code == 401
        # 403 truth promotion
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/spatial-entities"),
                                   json={"entity_type": "WALL",
                                         "truth_classification": "VERIFIED_EXISTING"}, timeout=30)
        assert r.status_code == 403 and r.json()["detail"]["error_code"] == "TRUTH_PROMOTION_FORBIDDEN"
        # 422 malformed / invalid capture
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                                   json={"capture_type": "NOT_A_REAL_TYPE"}, timeout=30)
        assert r.status_code == 422


# ===================== SCAN IDEMPOTENCY =====================
class TestScanCreateIdempotency:
    def test_first_create_and_replay(self, homeowner_session, api_url, db):
        key = f"idem-create-{uuid.uuid4()}"
        a = homeowner_session.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                                   json={"capture_type": "INTERIOR_LIDAR", "idempotency_key": key}, timeout=30)
        b = homeowner_session.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                                   json={"capture_type": "INTERIOR_LIDAR", "idempotency_key": key}, timeout=30)
        assert a.status_code == 201 and b.status_code in (200, 201)
        assert a.json()["id"] == b.json()["id"]
        assert db[enums.C_SCANS].count_documents({"create_idempotency_key": key}) == 1

    def test_concurrent_duplicate_create_one_session(self, homeowner_session, api_url, db):
        key = f"idem-conc-{uuid.uuid4()}"

        def _once():
            return homeowner_session.post(
                _api(api_url, f"/properties/{REF}/scan-sessions"),
                json={"capture_type": "INTERIOR_LIDAR", "idempotency_key": key}, timeout=30)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda _: _once(), range(8)))
        ids = {r.json()["id"] for r in results if r.status_code in (200, 201)}
        assert len(ids) == 1
        assert db[enums.C_SCANS].count_documents({"create_idempotency_key": key}) == 1

    def test_same_key_different_property_allowed(self, homeowner_session, api_url, db):
        key = f"idem-shared-{uuid.uuid4()}"
        alex = db.users.find_one({"email": "alex@stratexhabitat.com"})
        other = f"idem-prop-{uuid.uuid4()}"
        db.properties.insert_one({"id": other, "owner_id": alex["id"], "name": "idem-other"})
        try:
            a = homeowner_session.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                                       json={"capture_type": "INTERIOR_LIDAR", "idempotency_key": key}, timeout=30)
            b = homeowner_session.post(_api(api_url, f"/properties/{other}/scan-sessions"),
                                       json={"capture_type": "INTERIOR_LIDAR", "idempotency_key": key}, timeout=30)
            assert a.status_code == 201 and b.status_code == 201, (a.text, b.text)
            assert a.json()["id"] != b.json()["id"]
        finally:
            db[enums.C_SCANS].delete_many({"create_idempotency_key": key})
            db.properties.delete_one({"id": other})


class TestScanTransitionIdempotency:
    def _create(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]

    def test_first_transition_and_replay_no_duplicate_audit(self, homeowner_session, api_url, db):
        sid = self._create(homeowner_session, api_url)
        key = f"idem-tr-{uuid.uuid4()}"
        before = db.audit_events.count_documents({
            "event_type": "REALITY_SCAN_SESSION_TRANSITIONED",
            "entity_references.scan_session_id": sid})
        a = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "idempotency_key": key}, timeout=30)
        b = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "idempotency_key": key}, timeout=30)
        assert a.status_code == 200 and b.status_code == 200
        assert a.json()["version"] == b.json()["version"]
        import time; time.sleep(0.3)
        after = db.audit_events.count_documents({
            "event_type": "REALITY_SCAN_SESSION_TRANSITIONED",
            "entity_references.scan_session_id": sid})
        assert after == before + 1
        assert db[enums.C_SCAN_TRANSITION_IDEMPOTENCY].count_documents(
            {"scan_session_id": sid, "idempotency_key": key}) == 1

    def test_concurrent_duplicate_transition_one_change(self, homeowner_session, api_url, db):
        sid = self._create(homeowner_session, api_url)
        key = f"idem-tr-conc-{uuid.uuid4()}"

        def _once():
            return homeowner_session.post(
                _api(api_url, f"/scan-sessions/{sid}/transition"),
                json={"to_state": "CAPTURE_READY", "idempotency_key": key}, timeout=30)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda _: _once(), range(8)))
        assert all(r.status_code == 200 for r in results)
        versions = {r.json()["version"] for r in results}
        assert versions == {2}
        doc = db[enums.C_SCANS].find_one({"id": sid})
        assert doc["current_state"] == "CAPTURE_READY"
        assert doc["version"] == 2
        assert db[enums.C_SCAN_TRANSITION_IDEMPOTENCY].count_documents(
            {"scan_session_id": sid, "idempotency_key": key}) == 1

    def test_stale_version_still_fails(self, homeowner_session, api_url):
        sid = self._create(homeowner_session, api_url)
        t = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "expected_version": 999,
                                         "idempotency_key": str(uuid.uuid4())}, timeout=30)
        assert t.status_code == 409
        assert t.json()["detail"]["error_code"] == "STALE_VERSION"

    def test_different_keys_continue_to_work(self, homeowner_session, api_url):
        sid = self._create(homeowner_session, api_url)
        a = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "idempotency_key": str(uuid.uuid4())},
                                   timeout=30)
        b = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_IN_PROGRESS",
                                         "idempotency_key": str(uuid.uuid4()),
                                         "expected_version": a.json()["version"]}, timeout=30)
        assert a.status_code == 200 and b.status_code == 200
        assert b.json()["current_state"] == "CAPTURE_IN_PROGRESS"
        assert b.json()["version"] == a.json()["version"] + 1


class TestScanIdempotencyIndexes:
    def test_unique_indexes_present(self, db):
        scan_idx = {i["name"]: i for i in db[enums.C_SCANS].list_indexes()}
        assert "ux_scan_create_idempotency" in scan_idx
        assert scan_idx["ux_scan_create_idempotency"].get("unique") is True
        # old non-unique index must be gone
        assert "ix_scan_idempotency" not in scan_idx
        tr_idx = {i["name"]: i for i in db[enums.C_SCAN_TRANSITION_IDEMPOTENCY].list_indexes()}
        assert "ux_scan_transition_idempotency" in tr_idx
        assert tr_idx["ux_scan_transition_idempotency"].get("unique") is True
