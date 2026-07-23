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

    @pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
    def test_non_finite(self, bad):
        m = [r[:] for r in cs.IDENTITY_4X4]
        m[0][0] = bad
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
    """Focused regression: supplied governed storage references (QC-2 prefix-bound)."""
    def test_valid_governed_key(self):
        arts.validate_storage_reference(
            f"tenant/{enums.TENANT_ID}/property/{REF}/reality/obj-123",
            tenant_id=enums.TENANT_ID, property_id=REF)  # no raise

    @pytest.mark.parametrize("bad", [
        "", "   ", "https://x/y", "//host/x", "/abs/path", "key with space",
        "a/../b", "k?sig=1",
        "reality/obj-1",                                                   # missing prefix
        "tenant/other-tenant/property/ref-property-h014a/reality/x",       # foreign tenant
        "tenant/stratex-habitat/property/other-prop/reality/x",           # foreign property
    ])
    def test_invalid_refs_rejected(self, bad):
        with pytest.raises(HTTPException) as e:
            arts.validate_storage_reference(bad, tenant_id=enums.TENANT_ID, property_id=REF)
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
        # Idempotency is defined over the fixed fixture entity ids (QC-3), not the
        # entire REF property_id namespace (which may accumulate unrelated dev writes).
        fixture_ids = [e["id"] for e in rf.build_reference_records()["entities"]]
        r1 = homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        assert r1.status_code == 200, r1.text
        n1 = db[enums.C_SPATIAL].count_documents({"id": {"$in": fixture_ids}})
        r2 = homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        assert r2.status_code == 200
        n2 = db[enums.C_SPATIAL].count_documents({"id": {"$in": fixture_ids}})
        assert n1 == n2 == 12, "bootstrap must be idempotent (no duplicate fixture entities)"

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
        assert doc["storage_object_reference"] == f"tenant/{enums.TENANT_ID}/property/{REF}/reality/{aid}"

    def test_storage_ref_explicit_null_uses_governed_default(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "storage_object_reference": None}, timeout=30)
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert doc["storage_object_reference"] == f"tenant/{enums.TENANT_ID}/property/{REF}/reality/{aid}"

    def test_storage_ref_valid_supplied_preserved(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        supplied = f"tenant/{enums.TENANT_ID}/property/{REF}/reality/custom-object-key"
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

    def test_malformed_json_rejected_safely(self, homeowner_session, api_url):
        # Genuinely malformed JSON must be rejected with a 4xx, never a 500. The
        # transform validator — not permissive JSON parsing — is the contract.
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/coordinate-frames"),
                                   data="{ this is not valid json ",
                                   headers={"Content-Type": "application/json"}, timeout=30)
        assert r.status_code in (400, 422), r.text
        assert r.status_code != 500


# ================= PHASE 1: OWNERSHIP-SAFE STORAGE REFERENCE =================
class TestStorageReferenceOwnership:
    def _scan(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]

    def test_default_ref_uses_tenant_property_and_artifact(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}, timeout=30)
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert doc["storage_object_reference"] == f"tenant/{enums.TENANT_ID}/property/{REF}/reality/{aid}"
        assert doc["tenant_id"] == enums.TENANT_ID   # authenticated / server-derived tenant
        assert doc["property_id"] == REF             # authorized property
        assert aid in doc["storage_object_reference"]  # server-generated artifact id

    def test_client_tenant_property_override_ignored(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "tenant_id": "attacker-tenant", "property_id": "attacker-prop"},
                                   timeout=30)
        assert r.status_code == 201, r.text
        doc = db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})
        assert doc["tenant_id"] == enums.TENANT_ID and doc["property_id"] == REF
        assert "attacker" not in doc["storage_object_reference"]

    def test_cross_tenant_scan_creation_fails(self, homeowner_session, api_url, db):
        sid = f"rf-scan-foreign-{uuid.uuid4()}"
        db[enums.C_SCANS].insert_one({"id": sid, "scan_session_id": sid, "tenant_id": "other-tenant",
                                      "property_id": REF, "current_state": "CREATED"})
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}, timeout=30)
        # H-014A.2: uniform non-disclosure (no cross-tenant existence oracle).
        assert r.status_code == 404
        assert r.json()["detail"]["error_code"] == "NOT_FOUND"

    def test_cross_property_source_artifact_fails(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        foreign_art = f"rf-art-foreign-{uuid.uuid4()}"
        db[enums.C_ARTIFACTS].insert_one({"id": foreign_art, "artifact_id": foreign_art,
                                          "tenant_id": enums.TENANT_ID, "property_id": "other-prop",
                                          "artifact_type": "POINT_CLOUD"})
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "MESH", "checksum_sha256": "a" * 64,
                                         "source_artifact_ids": [foreign_art]}, timeout=30)
        assert r.status_code == 422
        assert r.json()["detail"]["error_code"] == "CROSS_PROPERTY_ARTIFACT"

    def test_public_response_exposes_only_governed_token(self, homeowner_session, api_url, db):
        sid = self._scan(homeowner_session, api_url)
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}, timeout=30)
        body = r.json()
        internal = db[enums.C_ARTIFACTS].find_one({"id": body["artifact_id"]})["storage_object_reference"]
        assert body["storage_object_reference"] == "<governed-object-store-reference>"
        assert internal not in _json.dumps(body)


# ============ PHASE 2: NULLABLE-DEFAULT SWEEP (content_type/file_size) ============
class TestArtifactDefaultsHTTP:
    def _create(self, s, api_url, extra):
        sid = s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                     json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]
        payload = {"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}
        payload.update(extra)
        return s.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"), json=payload, timeout=30)

    def test_content_type_omitted_defaults(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url, {})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["content_type"] == "application/octet-stream"

    def test_content_type_explicit_null_defaults(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url, {"content_type": None})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["content_type"] == "application/octet-stream"

    def test_content_type_valid_preserved(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url, {"content_type": "image/png"})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["content_type"] == "image/png"

    def test_content_type_empty_string_preserved_no_fallback(self, homeowner_session, api_url, db):
        # empty string is a supplied value, NOT None → preserved (no silent fallback)
        r = self._create(homeowner_session, api_url, {"content_type": ""})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["content_type"] == ""

    def test_file_size_omitted_defaults_zero(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url, {})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["file_size"] == 0

    def test_file_size_explicit_null_defaults_zero(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url, {"file_size": None})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["file_size"] == 0

    def test_file_size_valid_preserved(self, homeowner_session, api_url, db):
        r = self._create(homeowner_session, api_url, {"file_size": 99999})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["file_size"] == 99999


class TestLabelDefault:
    """Spatial entity label null-fallback (pure)."""
    def test_omitted_uses_entity_type(self):
        assert ss.resolve_label({"entity_type": "WALL"}) == "WALL"

    def test_explicit_null_uses_entity_type(self):
        assert ss.resolve_label({"entity_type": "WALL", "label": None}) == "WALL"

    def test_valid_preserved(self):
        assert ss.resolve_label({"entity_type": "WALL", "label": "North Wall"}) == "North Wall"

    def test_empty_string_preserved_no_fallback(self):
        assert ss.resolve_label({"entity_type": "WALL", "label": ""}) == ""


class TestModelVersionDefaultsHTTP:
    """Existing/design model collection null-fallbacks."""
    def test_existing_model_omitted_collections_default_empty(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/existing-models"), json={}, timeout=30)
        assert r.status_code == 201, r.text
        b = r.json()
        assert b["spatial_entity_ids"] == [] and b["source_scan_session_ids"] == []
        assert b["artifact_ids"] == [] and b["unknown_areas"] == []
        assert b["truth_summary"] == {} and b["quality_summary"] == {}

    def test_existing_model_explicit_null_collections_default_empty(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/existing-models"),
                                   json={"spatial_entity_ids": None, "truth_summary": None,
                                         "artifact_ids": None, "quality_summary": None,
                                         "unknown_areas": None, "source_scan_session_ids": None}, timeout=30)
        assert r.status_code == 201, r.text
        b = r.json()
        assert b["spatial_entity_ids"] == [] and b["truth_summary"] == {}
        assert b["artifact_ids"] == [] and b["quality_summary"] == {}
        assert b["unknown_areas"] == [] and b["source_scan_session_ids"] == []

    def test_design_model_null_proposed_entities_and_deltas_safe(self, homeowner_session, api_url):
        mid = homeowner_session.post(_api(api_url, f"/properties/{REF}/existing-models"),
                                     json={}, timeout=30).json()["id"]
        homeowner_session.post(_api(api_url, f"/existing-models/{mid}/transition"),
                               json={"to_state": "QUALITY_REVIEW"}, timeout=30)
        homeowner_session.post(_api(api_url, f"/existing-models/{mid}/transition"),
                               json={"to_state": "ACCEPTED"}, timeout=30)
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/design-models"),
                                   json={"base_existing_model_version_id": mid,
                                         "proposed_entities": None, "deltas": None}, timeout=30)
        assert r.status_code == 201, r.text
        b = r.json()
        assert b["proposed_entities"] == []
        assert b["deltas"] == {"added": [], "modified": [], "removed": []}


# ================= H-014A.1 QC-2: STORAGE-REFERENCE ATTACK MATRIX =================
class TestStorageReferenceAttackMatrix:
    def _art(self, s, api_url, extra):
        sid = s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                     json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]
        p = {"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64}
        p.update(extra)
        return s.post(_api(api_url, f"/scan-sessions/{sid}/artifacts"), json=p, timeout=30)

    def test_omitted_server_generated(self, homeowner_session, api_url, db):
        r = self._art(homeowner_session, api_url, {})
        assert r.status_code == 201, r.text
        aid = r.json()["artifact_id"]
        doc = db[enums.C_ARTIFACTS].find_one({"id": aid})
        assert doc["storage_object_reference"] == f"tenant/{enums.TENANT_ID}/property/{REF}/reality/{aid}"

    def test_null_server_generated(self, homeowner_session, api_url, db):
        r = self._art(homeowner_session, api_url, {"storage_object_reference": None})
        assert r.status_code == 201, r.text
        doc = db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})
        assert doc["storage_object_reference"].startswith(f"tenant/{enums.TENANT_ID}/property/{REF}/reality/")

    def test_authorized_exact_prefix_accepted(self, homeowner_session, api_url, db):
        ref = f"tenant/{enums.TENANT_ID}/property/{REF}/reality/custom-key_1.bin"
        r = self._art(homeowner_session, api_url, {"storage_object_reference": ref})
        assert r.status_code == 201, r.text
        assert db[enums.C_ARTIFACTS].find_one({"id": r.json()["artifact_id"]})["storage_object_reference"] == ref

    @pytest.mark.parametrize("ref", [
        "tenant/victim-tenant/property/ref-property-h014a/reality/x",       # foreign tenant
        "tenant/stratex-habitat/property/victim-prop/reality/x",            # foreign property
        "tenant/attacker/property/x/tenant/stratex-habitat/property/ref-property-h014a/reality/y",  # embedded later
        "tenant/stratex-habitat/property/ref-property-h014a/reality/../../etc/passwd",  # traversal suffix
        "https://evil.example.com/x",                                       # url
        "https://evil/x?sig=abc",                                          # signed url
        "/abs/tenant/stratex-habitat/property/ref-property-h014a/reality/x",  # absolute
        "tenant/stratex-habitat/property/ref-property-h014a/reality//x",    # repeated slash
        "tenant/stratex-habitat/property/ref-property-h014a/reality/%2e%2e/x",  # percent-encoded
        "tenant/stratex-habitat/property/ref-property-h014a/reality/a\\b",  # backslash
        "",                                                                 # blank
        "   ",                                                              # whitespace
        "TENANT/stratex-habitat/property/ref-property-h014a/reality/x",     # case trick
    ])
    def test_unauthorized_refs_rejected(self, homeowner_session, api_url, ref):
        r = self._art(homeowner_session, api_url, {"storage_object_reference": ref})
        assert r.status_code == 422, (ref, r.text)
        assert r.json()["detail"]["error_code"] == "INVALID_STORAGE_REFERENCE"

    def test_public_masked_and_audit_clean(self, homeowner_session, api_url, db):
        r = self._art(homeowner_session, api_url, {})
        aid = r.json()["artifact_id"]
        assert r.json()["storage_object_reference"] == "<governed-object-store-reference>"
        internal = db[enums.C_ARTIFACTS].find_one({"id": aid})["storage_object_reference"]
        assert internal not in _json.dumps(r.json())
        ev = db.audit_events.find_one({"domain": "reality", "event_type": "REALITY_ARTIFACT_MANIFEST_CREATED",
                                       "entity_references.artifact_id": aid})
        assert ev is not None
        assert ev["tenant_id"] == enums.TENANT_ID and ev["property_id"] == REF
        assert internal not in _json.dumps(ev, default=str)


# ================= H-014A.1 QC-1: UNIFORM PROPERTY NON-DISCLOSURE =================
def _foreign_owner():
    return f"not-alex-{uuid.uuid4()}"


class TestPropertyNonDisclosure:
    def test_owner_accesses_own_property(self, homeowner_session, api_url, db):
        alex = db.users.find_one({"email": "alex@stratexhabitat.com"})
        pid = f"qc1-own-{uuid.uuid4()}"
        db.properties.insert_one({"id": pid, "owner_id": alex["id"], "name": "qc1-own"})
        try:
            r = homeowner_session.get(_api(api_url, f"/properties/{pid}/spatial-graph"), timeout=30)
            assert r.status_code == 200, r.text
        finally:
            db.properties.delete_one({"id": pid})

    def test_unauthorized_existing_and_nonexistent_identical(self, homeowner_session, api_url, db):
        other = f"qc1-other-{uuid.uuid4()}"
        db.properties.insert_one({"id": other, "owner_id": _foreign_owner(), "name": "qc1-other"})
        try:
            r_exists = homeowner_session.get(_api(api_url, f"/properties/{other}/spatial-graph"), timeout=30)
            r_missing = homeowner_session.get(_api(api_url, f"/properties/nope-{uuid.uuid4()}/spatial-graph"), timeout=30)
        finally:
            db.properties.delete_one({"id": other})
        assert r_exists.status_code == 404 and r_missing.status_code == 404
        assert r_exists.json() == r_missing.json()  # identical body: no existence/ownership oracle

    def test_subordinate_object_nondisclosing(self, homeowner_session, api_url, db):
        other = f"qc1-prop-{uuid.uuid4()}"
        db.properties.insert_one({"id": other, "owner_id": _foreign_owner(), "name": "x"})
        art = f"qc1-art-{uuid.uuid4()}"
        db[enums.C_ARTIFACTS].insert_one({"id": art, "artifact_id": art, "tenant_id": enums.TENANT_ID,
                                          "property_id": other, "artifact_type": "POINT_CLOUD"})
        try:
            r_exists = homeowner_session.get(_api(api_url, f"/artifacts/{art}"), timeout=30)
            r_missing = homeowner_session.get(_api(api_url, f"/artifacts/nope-{uuid.uuid4()}"), timeout=30)
        finally:
            db[enums.C_ARTIFACTS].delete_one({"id": art}); db.properties.delete_one({"id": other})
        assert r_exists.status_code == 404 and r_missing.status_code == 404
        assert r_exists.json() == r_missing.json()

    def test_unauthenticated_401(self, api_url):
        import requests
        r = requests.get(_api(api_url, "/properties/anything/spatial-graph"), timeout=30)
        assert r.status_code == 401

    def test_reference_fixture_access_ok(self, homeowner_session, api_url):
        assert homeowner_session.get(_api(api_url, "/development/reference-room"), timeout=30).status_code == 200

    def test_contractor_denied_on_reference(self, contractor_session, api_url):
        # reference property id is public → 403 access-denied contract preserved
        assert contractor_session.get(_api(api_url, "/development/reference-room"), timeout=30).status_code == 403


# ================= H-014A.1 QC-3: DETERMINISTIC REFERENCE-ROOM VIEW =================
class TestReferenceRoomViewIsolation:
    def test_view_ignores_unrelated_same_property_records(self, homeowner_session, api_url, db):
        homeowner_session.post(_api(api_url, "/development/reference-room/bootstrap"), timeout=30)
        injected = []
        for _ in range(3):  # unrelated records sharing REF property_id + imitating classification
            fid = f"qc3-frame-{uuid.uuid4()}"
            db[enums.C_FRAMES].insert_one({"id": fid, "property_id": REF, "tenant_id": enums.TENANT_ID,
                                           "frame_type": "ROOM_FRAME",
                                           "source_classification": "DETERMINISTIC_REFERENCE_FIXTURE"})
            injected.append(fid)
        try:
            v1 = homeowner_session.get(_api(api_url, "/development/reference-room"), timeout=30).json()
            v2 = homeowner_session.get(_api(api_url, "/development/reference-room"), timeout=30).json()
        finally:
            db[enums.C_FRAMES].delete_many({"id": {"$in": injected}})
        assert len(v1["coordinate_frames"]) == 2, [f.get("frame_type") for f in v1["coordinate_frames"]]
        assert v1["entity_count"] == 12
        for fid in injected:
            assert fid not in [f["id"] for f in v1["coordinate_frames"]]
        # deterministic ordering/content across repeated reads
        assert [f["id"] for f in v1["coordinate_frames"]] == [f["id"] for f in v2["coordinate_frames"]]
        assert [e["id"] for e in v1["entities"]] == [e["id"] for e in v2["entities"]]
        assert v1["dimensions_m"] == v2["dimensions_m"]


# ================= H-014A.1 QC-4: TRUTH-PROMOTION REJECTION AUDIT =================
class TestTruthPromotionRejectionAudit:
    def test_rejected_and_audited_exactly_once(self, homeowner_session, api_url, db):
        # unique (entity_type, truth) combo → count is immune to concurrent tests
        flt = {"event_type": "REALITY_TRUTH_PROMOTION_REJECTED",
               "entity_references.entity_type": "EQUIPMENT",
               "details.attempted_truth_classification": "COMPLETED_AS_BUILT"}
        before = db.audit_events.count_documents(flt)
        r = homeowner_session.post(_api(api_url, f"/properties/{REF}/spatial-entities"),
                                   json={"entity_type": "EQUIPMENT",
                                         "truth_classification": "COMPLETED_AS_BUILT"}, timeout=30)
        assert r.status_code == 403
        assert r.json()["detail"]["error_code"] == "TRUTH_PROMOTION_FORBIDDEN"
        import time; time.sleep(0.4)
        assert db.audit_events.count_documents(flt) == before + 1  # exactly one
        ev = db.audit_events.find_one(flt, sort=[("timestamp", -1)])
        assert ev["domain"] == "reality"
        assert ev["tenant_id"] == enums.TENANT_ID
        assert ev["property_id"] == REF
        assert ev["actor"]["email"] == "alex@stratexhabitat.com"
        blob = _json.dumps(ev, default=str).lower()
        for bad in ["password", "token", "authorization", "signed_url", "secret", '"data"', '"bytes"']:
            assert bad not in blob

    def test_no_entity_persisted_on_rejection(self, homeowner_session, api_url, db):
        before = db[enums.C_SPATIAL].count_documents({"property_id": REF})
        homeowner_session.post(_api(api_url, f"/properties/{REF}/spatial-entities"),
                               json={"entity_type": "WALL",
                                     "truth_classification": "APPROVED_FOR_BUILD_PACKAGE"}, timeout=30)
        assert db[enums.C_SPATIAL].count_documents({"property_id": REF}) == before  # no write on denial


class TestTruthPromotionAuditFailureUnit:
    def test_denial_survives_audit_persistence_failure(self, monkeypatch):
        import asyncio
        async def boom(*a, **k):
            raise RuntimeError("audit backend down")
        monkeypatch.setattr(ss, "write_event", boom)
        with pytest.raises(HTTPException) as e:
            asyncio.run(ss.create_entity(
                None, {"id": "u", "email": "x", "role": "homeowner"},
                property_id=REF,
                body={"entity_type": "WALL", "truth_classification": "VERIFIED_EXISTING"},
                correlation_id="c"))
        assert e.value.status_code == 403
        assert e.value.detail["error_code"] == "TRUTH_PROMOTION_FORBIDDEN"