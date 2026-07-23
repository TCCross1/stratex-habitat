"""
H-014B.1 — Storage-boundary, idempotency, security, and cleanup unit tests.

These tests are deterministic and do not require a live HTTP backend. They prove:
  * MongoDB receives metadata only (no binary / base64 chunk bytes)
  * chunks are staged under tenant/property-scoped object references
  * identical duplicates are idempotent; conflicting content is rejected
  * precise missing indexes, checksum mismatches, completion/abort replay
  * fake provider is production-gated; cleanup utility is production-gated
  * API-facing payloads never leak raw keys / buckets / public / signed URLs
  * Guardian cannot approve property truth; DRAFT_CANDIDATE cannot auto-promote
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import uuid
from typing import Any

import pytest

from reality import enums
from reality import object_store
from reality import capture_upload_service as uploads
from reality import scan_guardian as guardian
from reality import cleanup_binary_chunk_docs as cleanup


# -------------------- minimal async Mongo stand-in --------------------
class _Cursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, *_a, **_k):
        return self

    async def to_list(self, length=None):
        return list(self._docs)[: length or len(self._docs)]

    def __aiter__(self):
        self._i = 0
        return self

    async def __anext__(self):
        if self._i >= len(self._docs):
            raise StopAsyncIteration
        d = self._docs[self._i]
        self._i += 1
        return d


class FakeColl:
    def __init__(self):
        self.docs: list[dict] = []

    async def find_one(self, filt, proj=None):
        for d in self.docs:
            if _match(d, filt):
                out = dict(d)
                out.pop("_id", None)
                return out
        return None

    def find(self, filt=None):
        filt = filt or {}
        return _Cursor([dict(d) for d in self.docs if _match(d, filt)])

    async def insert_one(self, doc):
        self.docs.append(dict(doc))

    async def insert_many(self, docs):
        for d in docs:
            self.docs.append(dict(d))

    async def update_one(self, filt, update, upsert=False):
        for i, d in enumerate(self.docs):
            if _match(d, filt):
                self.docs[i] = _apply(d, update)
                return
        if upsert:
            base = dict(filt)
            self.docs.append(_apply(base, update))

    async def delete_many(self, filt):
        self.docs = [d for d in self.docs if not _match(d, filt)]

    async def delete_one(self, filt):
        for i, d in enumerate(self.docs):
            if _match(d, filt):
                self.docs.pop(i)
                return


def _match(doc, filt):
    if not filt:
        return True
    if "$or" in filt:
        return any(_match(doc, clause) for clause in filt["$or"])
    for k, v in filt.items():
        if isinstance(v, dict) and "$exists" in v:
            exists = k in doc
            if bool(v["$exists"]) != exists:
                return False
        elif isinstance(v, dict) and "$type" in v:
            if not isinstance(doc.get(k), str):
                return False
        elif doc.get(k) != v:
            return False
    return True


def _apply(doc, update):
    out = dict(doc)
    if "$set" in update:
        out.update(update["$set"])
    if "$addToSet" in update:
        for k, v in update["$addToSet"].items():
            cur = list(out.get(k) or [])
            if v not in cur:
                cur.append(v)
            out[k] = cur
    if "$inc" in update:
        for k, v in update["$inc"].items():
            out[k] = (out.get(k) or 0) + v
    if "$unset" in update:
        for k in update["$unset"]:
            out.pop(k, None)
    return out


class FakeDB(dict):
    def __init__(self):
        super().__init__()
        self.name = "habitat_test"
        for name in (enums.C_SCANS, enums.C_UPLOAD_SESSIONS, enums.C_UPLOAD_CHUNKS,
                     enums.C_ARTIFACTS, "audit_events"):
            self[name] = FakeColl()

    def __getitem__(self, key):
        if key not in self:
            self[key] = FakeColl()
        return dict.__getitem__(self, key)


USER = {"id": "u-homeowner", "email": "alex@stratexhabitat.com", "role": "homeowner"}


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _fake_store(monkeypatch):
    monkeypatch.setenv("HABITAT_ENV", "test")
    monkeypatch.setenv("HABITAT_OBJECT_STORE_PROVIDER", "fake")
    monkeypatch.setenv("DB_NAME", "habitat_test")
    object_store.reset_fake_store_for_tests()
    # Silence audit writes that expect a real collection shape.
    async def _noop_event(*_a, **_k):
        return None
    monkeypatch.setattr("reality.capture_upload_service.write_event", _noop_event)
    yield
    object_store.reset_fake_store_for_tests()


def _seed_scan(db, property_id="prop-a", tenant_id=enums.TENANT_ID):
    sid = f"rf-scan-{uuid.uuid4()}"
    _run(db[enums.C_SCANS].insert_one({
        "id": sid, "tenant_id": tenant_id, "property_id": property_id,
        "current_state": enums.SCAN_CREATED,
    }))
    return sid


def _init(db, sid, data, chunk_size=8):
    return _run(uploads.init_upload(
        db, USER, scan_session_id=sid,
        body={"artifact_type": "POINT_CLOUD",
              "checksum_sha256": hashlib.sha256(data).hexdigest(),
              "total_size": len(data), "chunk_size": chunk_size},
        correlation_id="corr-test"))


class TestStorageBoundaryUnit:
    def test_mongo_receives_no_binary_or_base64(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(20)
        up = _init(db, sid, data, 8)
        for i in range(3):
            chunk = data[i * 8:(i + 1) * 8]
            _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=i, data=chunk))
        for doc in db[enums.C_UPLOAD_CHUNKS].docs:
            for field in ("data", "data_b64", "bytes", "payload", "content", "base64", "binary"):
                assert field not in doc or doc[field] is None
            assert doc.get("object_reference", "").startswith("orf-")
            assert "_storage_key_internal" in doc  # internal only
            assert f"tenant/{enums.TENANT_ID}/property/prop-a/reality/staging/" in doc["_storage_key_internal"]

    def test_chunks_stored_under_tenant_property_scan_scope(self):
        db = FakeDB()
        sid = _seed_scan(db, property_id="prop-scoped")
        data = b"abcdefghij"  # 10 bytes → 2 chunks of 8 + 2
        up = _init(db, sid, data, 8)
        _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data[0:8]))
        snap = object_store.fake_store_snapshot_for_tests()
        assert snap, "expected staged object in fake store"
        key = next(iter(snap))
        assert key.startswith(f"tenant/{enums.TENANT_ID}/property/prop-scoped/reality/staging/{up['id']}/")

    def test_identical_duplicate_idempotent(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(8)
        up = _init(db, sid, data, 8)
        a = _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data))
        b = _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data))
        assert a["duplicate"] is False
        assert b["duplicate"] is True and b["idempotent"] is True
        assert len(db[enums.C_UPLOAD_CHUNKS].docs) == 1

    def test_conflicting_duplicate_rejected(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(8)
        up = _init(db, sid, data, 8)
        _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data))
        with pytest.raises(Exception) as ei:
            _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=os.urandom(8)))
        assert ei.value.status_code == 409
        assert ei.value.detail["error_code"] == "CONFLICTING_CHUNK"

    def test_precise_missing_indexes(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(20)
        up = _init(db, sid, data, 8)
        _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data[0:8]))
        st = _run(uploads.get_status(db, USER, upload_session_id=up["id"]))
        assert st["missing_indexes"] == [1, 2]

    def test_chunk_checksum_mismatch_422(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(8)
        up = _init(db, sid, data, 8)
        with pytest.raises(Exception) as ei:
            _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0,
                                   data=data, chunk_sha256="0" * 64))
        assert ei.value.status_code == 422
        assert ei.value.detail["error_code"] == "CHUNK_CHECKSUM_MISMATCH"

    def test_whole_file_checksum_mismatch_422(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = b"HELLOWORLD"
        # Force wrong declared checksum via direct init body
        up = _run(uploads.init_upload(
            db, USER, scan_session_id=sid,
            body={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                  "total_size": len(data), "chunk_size": 8192},
            correlation_id="corr"))
        _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data))
        with pytest.raises(Exception) as ei:
            _run(uploads.complete_upload(db, USER, upload_session_id=up["id"]))
        assert ei.value.status_code == 422
        assert ei.value.detail["error_code"] == "CHECKSUM_MISMATCH"

    def test_completion_and_abort_replay_idempotent(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(16)
        up = _init(db, sid, data, 8)
        for i in range(2):
            _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=i,
                                   data=data[i * 8:(i + 1) * 8]))
        a = _run(uploads.complete_upload(db, USER, upload_session_id=up["id"]))
        b = _run(uploads.complete_upload(db, USER, upload_session_id=up["id"]))
        assert a["checksum_verified"] is True
        assert b["idempotent_replay"] is True
        # Separate abort session
        sid2 = _seed_scan(db)
        data2 = os.urandom(8)
        up2 = _init(db, sid2, data2, 8)
        _run(uploads.put_chunk(db, USER, upload_session_id=up2["id"], index=0, data=data2))
        x = _run(uploads.abort_upload(db, USER, upload_session_id=up2["id"]))
        y = _run(uploads.abort_upload(db, USER, upload_session_id=up2["id"]))
        assert x["state"] == enums.UP_ABORTED and x["idempotent_replay"] is False
        assert y["idempotent_replay"] is True

    def test_api_payload_never_leaks_storage_coordinates(self):
        db = FakeDB()
        sid = _seed_scan(db)
        data = os.urandom(8)
        up = _init(db, sid, data, 8)
        resp = _run(uploads.put_chunk(db, USER, upload_session_id=up["id"], index=0, data=data))
        blob = str(resp)
        assert "tenant/" not in blob
        assert "bucket" not in blob.lower()
        assert "signed" not in blob.lower()
        assert "http://" not in blob and "https://" not in blob
        assert "_storage_key_internal" not in resp
        assert "object_reference" not in resp  # opaque ref stays in Mongo only
        st = _run(uploads.get_status(db, USER, upload_session_id=up["id"]))
        assert "bucket" not in st and "signed_url" not in st and "public_url" not in st


class TestObjectStoreProviderGate:
    def test_fake_provider_disabled_in_production(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.setenv("HABITAT_OBJECT_STORE_PROVIDER", "fake")
        with pytest.raises(object_store.ObjectStoreProviderForbidden):
            object_store.assert_provider_allowed()

    def test_fake_provider_allowed_in_test(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "test")
        monkeypatch.setenv("HABITAT_OBJECT_STORE_PROVIDER", "fake")
        assert object_store.assert_provider_allowed() == "fake"

    def test_signed_url_not_persisted_on_put_result_filter(self, monkeypatch):
        # Direct unit: put() strips signed_url keys from provider responses for governed path.
        # Fake path never invents signed URLs.
        monkeypatch.setenv("HABITAT_ENV", "test")
        monkeypatch.setenv("HABITAT_OBJECT_STORE_PROVIDER", "fake")
        object_store.reset_fake_store_for_tests()
        result = _run(object_store.put("tenant/t/property/p/reality/x", b"abc"))
        assert "signed_url" not in result
        assert "public_url" not in result
        assert "url" not in result


class TestCleanupUtilityGate:
    def test_refuses_production(self):
        with pytest.raises(cleanup.CleanupRefused):
            cleanup.assert_non_production("production")

    def test_refuses_unknown_env(self):
        with pytest.raises(cleanup.CleanupRefused):
            cleanup.assert_non_production("staging")

    def test_refuses_mismatched_database(self):
        with pytest.raises(cleanup.CleanupRefused):
            cleanup.assert_database_confirmed("habitat_test", "some-other-db")

    def test_dry_run_plans_unset_of_binary_fields(self):
        docs = [
            {"upload_session_id": "u1", "index": 0, "data": b"abc", "sha256": "x"},
            {"upload_session_id": "u1", "index": 1, "data_b64": "YWJj", "sha256": "y"},
            {"upload_session_id": "u1", "index": 2, "sha256": "z"},  # clean
        ]
        plans = cleanup.plan_cleanup(docs)
        assert len(plans) == 2
        assert plans[0]["fields_to_unset"] == ["data"]
        assert plans[1]["fields_to_unset"] == ["data_b64"]

    def test_async_cleanup_dry_run(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "test")
        monkeypatch.setenv("DB_NAME", "habitat_test")
        db = FakeDB()
        _run(db[enums.C_UPLOAD_CHUNKS].insert_one(
            {"upload_session_id": "u1", "index": 0, "data": b"nope", "sha256": "a"}))
        result = _run(cleanup.run_cleanup(db, confirm_database="habitat_test", apply=False))
        assert result["dry_run"] is True
        assert result["summary"]["matched_documents"] == 1
        assert result["applied"] == 0

    def test_async_cleanup_apply(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "test")
        monkeypatch.setenv("DB_NAME", "habitat_test")
        db = FakeDB()
        _run(db[enums.C_UPLOAD_CHUNKS].insert_one(
            {"upload_session_id": "u1", "index": 0, "data": b"nope", "data_b64": "eA==", "sha256": "a"}))
        result = _run(cleanup.run_cleanup(db, confirm_database="habitat_test", apply=True))
        assert result["applied"] == 1
        doc = db[enums.C_UPLOAD_CHUNKS].docs[0]
        assert "data" not in doc and "data_b64" not in doc


class TestGuardianTruthBoundaryUnit:
    def test_guardian_cannot_approve_property_truth(self):
        r = guardian.evaluate({
            "captured_area_m2": 29.77, "expected_area_m2": 29.77,
            "surface_coverage": {"WALL": 0.96, "FLOOR": 0.93, "CEILING": 0.88},
            "wall_count_detected": 4, "wall_count_expected": 4,
            "tracking_quality": {"mean": 0.94, "min": 0.71, "limited_fraction": 0.04},
            "drift_estimate_m": 0.021, "frame_count": 812,
            "low_quality_frame_fraction": 0.06, "openings_detected": 3,
            "dimensions_m": {"width": 4.88, "length": 6.10, "height": 2.74},
        })
        assert r["verdict"] == enums.GUARDIAN_PASS
        # Guardian may recommend ACCEPT_CANDIDATE only — never property-truth approval.
        assert r["recommendation"] == "ACCEPT_CANDIDATE"
        assert r["recommendation"] != "APPROVE_PROPERTY_TRUTH"
        assert "VERIFIED_EXISTING" not in str(r)

    def test_draft_candidate_state_exists_and_is_not_verified(self):
        assert enums.EM_DRAFT_CANDIDATE != enums.VERIFIED_EXISTING
        assert enums.EM_DRAFT_CANDIDATE in enums.EM_LEGAL_TRANSITIONS
        # DRAFT_CANDIDATE cannot auto-promote to VERIFIED_EXISTING (not even a legal transition).
        assert enums.VERIFIED_EXISTING not in enums.EM_LEGAL_TRANSITIONS[enums.EM_DRAFT_CANDIDATE]
        assert enums.EM_ACCEPTED not in enums.EM_LEGAL_TRANSITIONS[enums.EM_DRAFT_CANDIDATE]


class TestObjectStoreGovernedPaths:
    def test_governed_put_strips_signed_url_and_handles_409(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "test")
        monkeypatch.setenv("HABITAT_OBJECT_STORE_PROVIDER", "governed")

        class Resp:
            status_code = 409
            def raise_for_status(self):
                import requests
                raise requests.HTTPError(response=self)

        calls = {"n": 0}

        def put_object(path, data, content_type):
            calls["n"] += 1
            if calls["n"] == 1:
                return {"path": path, "signed_url": "https://evil.example/x", "etag": "e1",
                        "public_url": "https://evil.example/p", "url": "https://evil.example/u"}
            import requests
            raise requests.HTTPError(response=Resp())

        def get_object(path):
            return b"abc", "application/octet-stream"

        monkeypatch.setattr(object_store, "_client", lambda: (put_object, get_object))
        r1 = _run(object_store.put("tenant/t/property/p/reality/a", b"x"))
        assert "signed_url" not in r1 and "public_url" not in r1 and "url" not in r1
        assert r1.get("etag") == "e1"
        r2 = _run(object_store.put("tenant/t/property/p/reality/b", b"y"))
        assert r2.get("already_exists") is True
        data, ctype = _run(object_store.get("tenant/t/property/p/reality/a"))
        assert data == b"abc"

    def test_mark_cleanup_does_not_fabricate_deletion(self):
        marks = _run(object_store.mark_upload_staging_for_cleanup(
            tenant_id="t", property_id="p", upload_session_id="u", indexes=[0, 1]))
        assert len(marks) == 2
        assert all(m["deletion_executed"] is False for m in marks)
        assert all(m["deletion_fabricated"] is False for m in marks)



class TestCaptureCandidateBoundary:
    def test_generate_candidate_rejects_wrong_state(self):
        from reality import capture
        from fastapi import HTTPException
        db = FakeDB()
        sid = _seed_scan(db)
        with pytest.raises(HTTPException) as ei:
            _run(capture.generate_candidate(
                db, USER, session_id=sid,
                body={"derived_structure": {"dimensions_m": {"width": 1, "length": 1, "height": 1}}},
                correlation_id="c"))
        assert ei.value.status_code == 409

    def test_generate_candidate_draft_only(self, monkeypatch):
        from reality import capture
        db = FakeDB()
        sid = f"rf-scan-{uuid.uuid4()}"
        _run(db[enums.C_SCANS].insert_one({
            "id": sid, "tenant_id": enums.TENANT_ID, "property_id": "prop-a",
            "current_state": enums.SCAN_QUALITY_REVIEW,
            "guardian_result": {"verdict": enums.GUARDIAN_PASS, "score": 100,
                                "missing_areas": [{"code": "X"}]},
            "quality_summary": {"guardian_verdict": "PASS"},
            "coordinate_frame_id": None,
        }))
        async def _noop(*a, **k):
            return None
        monkeypatch.setattr("reality.capture.write_event", _noop)

        async def fake_create_existing(db, user, **kwargs):
            rec = {"id": "rf-em-1", "model_state": enums.EM_DRAFT_CANDIDATE,
                   "truth_classification": enums.MEASURED_EXISTING,
                   "property_id": kwargs.get("property_id"), "tenant_id": enums.TENANT_ID}
            await db[enums.C_EXISTING].insert_one(rec)
            return rec
        monkeypatch.setattr(capture.mvs, "create_existing_model", fake_create_existing)
        result = _run(capture.generate_candidate(
            db, USER, session_id=sid,
            body={"derived_structure": {
                "dimensions_m": {"width": 4, "length": 5, "height": 2.7, "floor_area_m2": 20},
                "has_floor": True, "has_ceiling": True,
                "openings": [{"type": "DOOR", "wall": "North", "label": "Entry"}],
                "unknowns": ["cavity"], "room_label": "Test Room"}},
            correlation_id="c"))
        assert result["truth_boundary"] == "DRAFT_CANDIDATE_ONLY"
        assert result["existing_model_version"]["model_state"] == enums.EM_DRAFT_CANDIDATE
        assert result["entity_count"] >= 1
