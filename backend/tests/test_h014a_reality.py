"""
H-014A — Reality Studio shared spatial foundation tests.

Mix of pure-logic unit tests (fast, cover validation branches) and HTTP
integration tests (governed lifecycle, authorization, reference-room
determinism) driven against the live backend + MongoDB via conftest fixtures.
"""
import json as _json
import uuid

import pytest

from reality import enums
from reality import coordinate_service as cs
from reality import spatial_service as ss
from reality import artifact_service as arts
from reality import model_version_service as mvs
from reality import fixtures as rf
from reality.authz import assert_truth_promotion_allowed, structured
from fastapi import HTTPException

REF = "ref-property-h014a"
BASE = enums.API_PREFIX  # /reality/v1


def _api(api_url, path):
    return f"{api_url}{BASE}{path}"


# ========================= PURE UNIT TESTS =========================
class TestCoordinateTransformValidation:
    def test_valid_identity(self):
        cs.validate_transform(cs.IDENTITY_4X4)  # no raise

    def test_wrong_dimensions(self):
        with pytest.raises(HTTPException) as e:
            cs.validate_transform([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        assert e.value.detail["error_code"] == "INVALID_MATRIX"

    def test_non_finite(self):
        m = [r[:] for r in cs.IDENTITY_4X4]
        m[0][0] = float("inf")
        with pytest.raises(HTTPException) as e:
            cs.validate_transform(m)
        assert e.value.detail["error_code"] == "NON_FINITE_MATRIX"

    def test_bad_homogeneous_row(self):
        m = [r[:] for r in cs.IDENTITY_4X4]
        m[3] = [0, 0, 0, 2]
        with pytest.raises(HTTPException) as e:
            cs.validate_transform(m)
        assert e.value.detail["error_code"] == "INVALID_HOMOGENEOUS_ROW"


class TestSpatialRelationshipValidation:
    def _ent(self, **kw):
        base = {"id": "e1", "tenant_id": enums.TENANT_ID, "property_id": REF,
                "entity_type": "WALL", "existing_state": enums.EXISTING}
        base.update(kw)
        return base

    def test_valid_wall_with_room_parent(self):
        parent = self._ent(id="room1", entity_type="ROOM")
        ss.validate_entity_relationships(self._ent(id="w1", parent_entity_id="room1"), parent)

    def test_self_parent_fails(self):
        with pytest.raises(HTTPException) as e:
            ss.validate_entity_relationships(self._ent(id="w1", parent_entity_id="w1"),
                                             self._ent(id="w1", entity_type="ROOM"))
        assert e.value.detail["error_code"] == "SELF_PARENT"

    def test_cross_tenant_fails(self):
        parent = self._ent(id="room1", entity_type="ROOM", tenant_id="other-tenant")
        with pytest.raises(HTTPException) as e:
            ss.validate_entity_relationships(self._ent(id="w1", parent_entity_id="room1"), parent)
        assert e.value.detail["error_code"] == "CROSS_TENANT_RELATIONSHIP"

    def test_cross_property_fails(self):
        parent = self._ent(id="room1", entity_type="ROOM", property_id="other-prop")
        with pytest.raises(HTTPException) as e:
            ss.validate_entity_relationships(self._ent(id="w1", parent_entity_id="room1"), parent)
        assert e.value.detail["error_code"] == "CROSS_PROPERTY_RELATIONSHIP"

    def test_orphan_opening_fails(self):
        parent = self._ent(id="room1", entity_type="ROOM")  # not surface-like
        with pytest.raises(HTTPException) as e:
            ss.validate_entity_relationships(
                self._ent(id="o1", entity_type="OPENING", parent_entity_id="room1"), parent)
        assert e.value.detail["error_code"] == "ORPHAN_OPENING"

    def test_door_requires_opening_ref(self):
        parent = self._ent(id="w1", entity_type="WALL")
        with pytest.raises(HTTPException) as e:
            ss.validate_entity_relationships(
                self._ent(id="d1", entity_type="DOOR", parent_entity_id="w1"), parent)
        assert e.value.detail["error_code"] == "MISSING_OPENING_REF"

    def test_door_with_valid_opening_ok(self):
        parent = self._ent(id="w1", entity_type="WALL")
        opening = self._ent(id="op1", entity_type="OPENING")
        ss.validate_entity_relationships(
            self._ent(id="d1", entity_type="DOOR", parent_entity_id="w1", opening_ref="op1"),
            parent, opening)

    def test_proposed_type_cannot_be_existing(self):
        with pytest.raises(HTTPException) as e:
            ss.validate_entity_relationships(
                self._ent(id="p1", entity_type="PROPOSED_ADDITION", existing_state=enums.EXISTING))
        assert e.value.detail["error_code"] == "PROPOSED_IN_EXISTING"


class TestTruthPromotionGuard:
    @pytest.mark.parametrize("cls", sorted(enums.RESTRICTED_TRUTH_CLASSES))
    def test_restricted_promotion_forbidden(self, cls):
        with pytest.raises(HTTPException) as e:
            assert_truth_promotion_allowed(cls, "HOMEOWNER_INPUT")
        assert e.value.status_code == 403
        assert e.value.detail["error_code"] == "TRUTH_PROMOTION_FORBIDDEN"

    def test_measured_existing_allowed(self):
        assert_truth_promotion_allowed(enums.MEASURED_EXISTING, "LIDAR_CAPTURE")  # no raise


class TestArtifactChecksum:
    def test_valid_sha256(self):
        arts.validate_checksum("a" * 64)

    def test_invalid_checksum(self):
        with pytest.raises(HTTPException) as e:
            arts.validate_checksum("nothex")
        assert e.value.detail["error_code"] == "INVALID_CHECKSUM"


class TestStorageReferenceValidation:
    """Focused regression: supplied governed storage references (Defect 2)."""
    def test_valid_governed_key(self):
        arts.validate_storage_reference("stratex-habitat/reality/obj-123")  # no raise

    @pytest.mark.parametrize("bad", ["", "   ", "https://x/y", "//host/x", "/abs/path",
                                     "key with space", "a/../b", "k?sig=1"])
    def test_invalid_refs_rejected(self, bad):
        with pytest.raises(HTTPException) as e:
            arts.validate_storage_reference(bad)
        assert e.value.detail["error_code"] == "INVALID_STORAGE_REFERENCE"


class TestReferenceRoomDeterminism:
    def test_ids_and_values_stable(self):
        a = rf.build_reference_records()
        b = rf.build_reference_records()
        assert a == b  # fully deterministic
        assert a["property_id"] == REF
        assert len(a["entities"]) == 12
        room = next(e for e in a["entities"] if e["id"] == rf.ROOM)
        assert room["dimensions"]["width_m"] == 4.88
        assert room["dimensions"]["length_m"] == 6.10
        assert room["dimensions"]["height_m"] == 2.74

    def test_all_records_non_authoritative(self):
        a = rf.build_reference_records()
        assert all(e["authoritative"] is False for e in a["entities"])
        assert a["artifact"]["authoritative"] is False
        for e in a["entities"]:
            assert e["source_classification"] == "DETERMINISTIC_REFERENCE_FIXTURE"

    def test_production_fixture_fails_closed(self, monkeypatch):
        from fixture_provider import FixtureDisabledError
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", "false")
        with pytest.raises(FixtureDisabledError):
            rf.assert_fixtures_enabled()

    def test_content_hash_deterministic(self):
        h1 = mvs.content_hash(["b", "a"], 1, ["y", "x"])
        h2 = mvs.content_hash(["a", "b"], 1, ["x", "y"])
        assert h1 == h2 and len(h1) == 64


# ========================= HTTP INTEGRATION TESTS =========================
class TestReferenceRoomHTTP:
    def test_bootstrap_idempotent(self, homeowner_session, api_url, db):
        r1 = homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        assert r1.status_code == 200, r1.text
        n1 = db[enums.C_SPATIAL].count_documents({"property_id": REF})
        r2 = homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        assert r2.status_code == 200
        n2 = db[enums.C_SPATIAL].count_documents({"property_id": REF})
        assert n1 == n2 == 12, "bootstrap must be idempotent (no duplicates)"

    def test_reference_room_view(self, homeowner_session, api_url):
        homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        r = homeowner_session.get(_api(api_url, "/development/reference-room"), timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d["authoritative"] is False
        assert d["dimensions_m"]["floor_area_m2"] == 29.768
        assert d["entity_count"] == 12
        assert d["existing_model_version"]["model_state"] == "DRAFT_CANDIDATE"
        assert d["artifact_manifest"]["storage_object_reference"] == "<governed-object-store-reference>"

    def test_spatial_graph(self, homeowner_session, api_url):
        homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        r = homeowner_session.get(_api(api_url, f"/properties/{REF}/spatial-graph"), timeout=30)
        assert r.status_code == 200
        assert r.json()["entity_counts_by_type"]["WALL"] == 4


class TestAuthorizationHTTP:
    def test_unauthenticated_401(self, api_url):
        import requests
        r = requests.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        assert r.status_code == 401

    def test_contractor_denied_403(self, contractor_session, api_url):
        r = contractor_session.get(_api(api_url, "/development/reference-room"), timeout=30)
        assert r.status_code == 403

    def test_truth_promotion_forbidden_over_api(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/spatial-entities"),
                                   json={"entity_type": "WALL", "truth_classification": "VERIFIED_EXISTING"},
                                   timeout=30)
        assert r.status_code == 403
        assert r.json()["detail"]["error_code"] == "TRUTH_PROMOTION_FORBIDDEN"


class TestScanSessionHTTP:
    def _create(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR", "idempotency_key": str(uuid.uuid4())}, timeout=30)

    def test_create_and_legal_transition(self, homeowner_session, api_url):
        r = self._create(homeowner_session, api_url)
        assert r.status_code == 201, r.text
        sid = r.json()["id"]
        assert r.json()["current_state"] == "CREATED"
        t = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY"}, timeout=30)
        assert t.status_code == 200 and t.json()["current_state"] == "CAPTURE_READY"

    def test_illegal_transition_409(self, homeowner_session, api_url):
        sid = self._create(homeowner_session, api_url).json()["id"]
        t = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "ACCEPTED"}, timeout=30)
        assert t.status_code == 409
        assert t.json()["detail"]["error_code"] == "ILLEGAL_TRANSITION"

    def test_duplicate_transition_idempotent(self, homeowner_session, api_url):
        sid = self._create(homeowner_session, api_url).json()["id"]
        key = str(uuid.uuid4())
        a = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "idempotency_key": key}, timeout=30)
        b = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "idempotency_key": key}, timeout=30)
        assert a.status_code == 200 and b.status_code == 200
        assert a.json()["version"] == b.json()["version"], "idempotent replay must not double-increment"

    def test_stale_version_409(self, homeowner_session, api_url):
        sid = self._create(homeowner_session, api_url).json()["id"]
        t = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/transition"),
                                   json={"to_state": "CAPTURE_READY", "expected_version": 999}, timeout=30)
        assert t.status_code == 409
        assert t.json()["detail"]["error_code"] == "STALE_VERSION"


class TestArtifactHTTP:
    def _scan(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]

    def test_valid_checksum_accepted(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "file_size": 12345}, timeout=30)
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        # binary payload not stored in Mongo
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert "data" not in doc and "bytes" not in doc and "payload" not in doc
        assert r.json()["storage_object_reference"] == "<governed-object-store-reference>"

    def test_invalid_checksum_422(self, homeowner_session, api_url):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "xyz"}, timeout=30)
        assert r.status_code == 422
        assert r.json()["detail"]["error_code"] == "INVALID_CHECKSUM"

    # --- Defect 2 regression: storage_object_reference null-fallback + validation ---
    def test_storage_ref_omitted_uses_governed_default(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}, timeout=30)
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        assert r.json()["storage_object_reference"] == "<governed-object-store-reference>"
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert doc["storage_object_reference"] == f"{enums.TENANT_ID}/reality/{aid}"

    def test_storage_ref_explicit_null_uses_governed_default(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "storage_object_reference": None}, timeout=30)
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert doc["storage_object_reference"] == f"{enums.TENANT_ID}/reality/{aid}"

    def test_storage_ref_valid_supplied_preserved(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        supplied = f"{enums.TENANT_ID}/reality/custom-object-key"
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "storage_object_reference": supplied}, timeout=30)
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        # public response never leaks the raw key ...
        assert r.json()["storage_object_reference"] == "<governed-object-store-reference>"
        # ... but the supplied governed key is preserved in storage (no silent fallback)
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert doc["storage_object_reference"] == supplied

    def test_storage_ref_empty_string_rejected(self, homeowner_session, api_url):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "storage_object_reference": ""}, timeout=30)
        assert r.status_code == 422
        assert r.json()["detail"]["error_code"] == "INVALID_STORAGE_REFERENCE"

    def test_storage_ref_url_rejected(self, homeowner_session, api_url):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "storage_object_reference": "https://public.example.com/leak?sig=abc"},
                                   timeout=30)
        assert r.status_code == 422
        assert r.json()["detail"]["error_code"] == "INVALID_STORAGE_REFERENCE"

    def test_public_response_hides_internal_storage(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}, timeout=30)
        assert r.status_code == 201, r.text
        body = r.json()
        aid = body["artifact_id"]
        internal_ref = db[enums.C_ARTIFACTS].find_one({"id": aid})["storage_object_reference"]
        assert body["storage_object_reference"] == "<governed-object-store-reference>"
        assert internal_ref not in _json.dumps(body)


class TestModelVersionHTTP:
    def test_existing_model_accept_immutable_then_design(self, homeowner_session, api_url):
        # create draft existing model
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/existing-models"),
                                   json={"spatial_entity_ids": []}, timeout=30)
        assert r.status_code == 201, r.text
        mid = r.json()["id"]
        # design model on a NON-accepted base must fail
        d0 = homeowner_session.post(_api(api_url, f"/properties/{REF}/design-models"),
                                    json={"base_existing_model_version_id": mid}, timeout=30)
        assert d0.status_code == 409 and d0.json()["detail"]["error_code"] == "BASE_MODEL_NOT_ACCEPTED"
        # accept: DRAFT_CANDIDATE -> QUALITY_REVIEW -> ACCEPTED
        homeowner_session.post(_api(api_url, f"/existing-models/{mid}/transition"),
                               json={"to_state": "QUALITY_REVIEW"}, timeout=30)
        acc = homeowner_session.post(_api(api_url, f"/existing-models/{mid}/transition"),
                                     json={"to_state": "ACCEPTED"}, timeout=30)
        assert acc.status_code == 200 and acc.json()["immutable"] is True
        # accepted model is immutable (cannot revert)
        bad = homeowner_session.post(_api(api_url, f"/existing-models/{mid}/transition"),
                                     json={"to_state": "QUALITY_REVIEW"}, timeout=30)
        assert bad.status_code == 409 and bad.json()["detail"]["error_code"] == "MODEL_IMMUTABLE"
        # design model on accepted base succeeds
        d1 = homeowner_session.post(_api(api_url, f"/properties/{REF}/design-models"),
                                    json={"base_existing_model_version_id": mid,
                                          "proposed_entities": [{"entity_type": "PROPOSED_ADDITION",
                                                                 "truth_classification": "PROPOSED_DESIGN"}]},
                                    timeout=30)
        assert d1.status_code == 201, d1.text
        assert d1.json()["base_existing_model_version_id"] == mid

    def test_design_missing_base_422(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/design-models"),
                                   json={"base_existing_model_version_id": "does-not-exist"}, timeout=30)
        assert r.status_code == 422
        assert r.json()["detail"]["error_code"] == "BASE_MODEL_NOT_FOUND"


class TestCoordinateFrameHTTP:
    def test_create_valid_frame(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   json={"frame_type": "ROOM_FRAME"}, timeout=30)
        assert r.status_code == 201, r.text
        assert r.json()["authoritative"] is False

    def test_invalid_transform_422(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   json={"frame_type": "ROOM_FRAME",
                                         "transform_to_parent": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}, timeout=30)
        assert r.status_code == 422
        assert r.json()["detail"]["error_code"] == "INVALID_MATRIX"

    # --- Defect 1 regression: transform null-fallback + preserved validation ---
    def test_frame_field_omitted_uses_identity(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   json={"frame_type": "ROOM_FRAME"}, timeout=30)
        assert r.status_code == 201, r.text
        assert r.json()["transform_to_parent"] == cs.IDENTITY_4X4
        assert r.json()["transform_to_property"] == cs.IDENTITY_4X4

    def test_frame_field_explicit_null_uses_identity(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   json={"frame_type": "ROOM_FRAME", "transform_to_parent": None,
                                         "transform_to_property": None}, timeout=30)
        assert r.status_code == 201, r.text
        assert r.json()["transform_to_parent"] == cs.IDENTITY_4X4
        assert r.json()["transform_to_property"] == cs.IDENTITY_4X4

    def test_frame_valid_matrix_preserved(self, homeowner_session, api_url):
        m = [[1, 0, 0, 2.5], [0, 1, 0, -1.0], [0, 0, 1, 0.75], [0, 0, 0, 1]]
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   json={"frame_type": "ROOM_FRAME", "transform_to_parent": m}, timeout=30)
        assert r.status_code == 201, r.text
        assert r.json()["transform_to_parent"] == m  # supplied matrix preserved, not defaulted

    def test_frame_empty_list_rejected(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   json={"frame_type": "ROOM_FRAME", "transform_to_parent": []}, timeout=30)
        assert r.status_code == 422  # no silent fallback to identity
        assert r.json()["detail"]["error_code"] == "INVALID_MATRIX"

    def test_frame_non_finite_rejected(self, homeowner_session, api_url):
        # Infinity is not valid JSON; send a raw body so a non-finite value reaches validation.
        raw = ('{"frame_type": "ROOM_FRAME", "transform_to_parent": '
               '[[Infinity,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]}')
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   data=raw, headers={"Content-Type": "application/json"}, timeout=30)
        assert r.status_code == 422, r.text
        assert r.json()["detail"]["error_code"] == "NON_FINITE_MATRIX"
