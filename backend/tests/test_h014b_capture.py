"""
H-014B — Real LiDAR capture proof + AI Scan Quality Guardian tests.

Pure-logic unit tests (deterministic Guardian, native→canonical state mapping)
plus HTTP integration tests (resumable governed chunked upload, checksum
integrity, capture proof, candidate truth boundary, authorization) driven
against the live backend + MongoDB via the shared conftest fixtures.
"""
import hashlib
import os
import uuid

import pytest
import requests

from reality import enums
from reality import scan_guardian as guardian
from reality import capture
from fastapi import HTTPException

REF = "ref-property-h014a"
BASE = enums.API_PREFIX  # /reality/v1


def _api(api_url, path):
    return f"{api_url}{BASE}{path}"


def _complete(session, api_url, up_id, expect_ok=True):
    """Complete an upload, retrying once on a transient object-store 502."""
    import time
    for attempt in range(3):
        r = session.post(_api(api_url, f"/uploads/{up_id}/complete"), timeout=60)
        if r.status_code == 502 and attempt < 2:
            time.sleep(1.0)
            continue
        return r
    return r


GOOD_REPORT = {
    "captured_area_m2": 29.77, "expected_area_m2": 29.77,
    "surface_coverage": {"WALL": 0.96, "FLOOR": 0.93, "CEILING": 0.88},
    "wall_count_detected": 4, "wall_count_expected": 4,
    "tracking_quality": {"mean": 0.94, "min": 0.71, "limited_fraction": 0.04},
    "drift_estimate_m": 0.021, "frame_count": 812,
    "low_quality_frame_fraction": 0.06, "openings_detected": 3,
    "dimensions_m": {"width": 4.88, "length": 6.10, "height": 2.74},
}
BAD_REPORT = {
    "captured_area_m2": 2.0, "expected_area_m2": 30.0,
    "surface_coverage": {"WALL": 0.3, "FLOOR": 0.2, "CEILING": 0.1},
    "wall_count_detected": 1, "wall_count_expected": 4,
    "tracking_quality": {"mean": 0.4, "min": 0.1, "limited_fraction": 0.7},
    "drift_estimate_m": 0.4, "frame_count": 30,
    "low_quality_frame_fraction": 0.6,
    "dimensions_m": {"width": 4.0, "length": 5.0, "height": 2.6},
}
WARN_REPORT = {
    "captured_area_m2": 24.0, "expected_area_m2": 29.77,
    "surface_coverage": {"WALL": 0.7, "FLOOR": 0.85, "CEILING": 0.75},
    "wall_count_detected": 4, "wall_count_expected": 4,
    "tracking_quality": {"mean": 0.85, "min": 0.6, "limited_fraction": 0.08},
    "drift_estimate_m": 0.03, "frame_count": 300,
    "low_quality_frame_fraction": 0.1,
    "dimensions_m": {"width": 4.88, "length": 6.10, "height": 2.74},
}


# ========================= PURE UNIT TESTS =========================
class TestGuardianDeterminism:
    def test_pass_verdict_deterministic(self):
        a = guardian.evaluate(GOOD_REPORT)
        b = guardian.evaluate(GOOD_REPORT)
        assert a["verdict"] == enums.GUARDIAN_PASS
        assert a["score"] == 100 and a["coverage_state"] == enums.COVERAGE_COMPLETE
        assert a["recommendation"] == "ACCEPT_CANDIDATE"
        # Identical inputs → identical outputs (ignoring the timestamp field).
        a2 = {k: v for k, v in a.items() if k != "evaluated_at"}
        b2 = {k: v for k, v in b.items() if k != "evaluated_at"}
        assert a2 == b2

    def test_fail_verdict_and_recapture(self):
        r = guardian.evaluate(BAD_REPORT)
        assert r["verdict"] == enums.GUARDIAN_FAIL
        assert r["coverage_state"] == enums.COVERAGE_INCOMPLETE
        assert r["recommendation"] == "RECAPTURE"
        codes = {f["code"] for f in r["findings"]}
        assert "WALL_COVERAGE_LOW" in codes
        assert "MISSING_WALL" in codes
        assert "DRIFT_EXCEEDED" in codes
        assert "INSUFFICIENT_AREA" in codes
        assert "TRACKING_DEGRADED" in codes

    def test_warn_verdict_review(self):
        r = guardian.evaluate(WARN_REPORT)
        assert r["verdict"] == enums.GUARDIAN_WARN
        assert r["coverage_state"] == enums.COVERAGE_PARTIAL
        assert r["recommendation"] == "REVIEW"
        assert 0 < r["score"] < 100

    def test_missing_areas_reported(self):
        r = guardian.evaluate(BAD_REPORT)
        assert r["missing_areas"], "missing areas must be surfaced on a poor scan"


class TestNativeStateMapping:
    def test_all_native_states_map(self):
        for s in enums.NATIVE_CAPTURE_STATES:
            assert capture.map_native_state(s) in {
                enums.SCAN_CREATED, enums.SCAN_CAPTURE_READY, enums.SCAN_CAPTURE_IN_PROGRESS,
                enums.SCAN_CAPTURE_PAUSED, enums.SCAN_UPLOAD_PENDING, enums.SCAN_UPLOAD_IN_PROGRESS,
                enums.SCAN_UPLOAD_COMPLETE, enums.SCAN_PROCESSING_IN_PROGRESS,
                enums.SCAN_QUALITY_REVIEW, enums.SCAN_FAILED_RECOVERABLE, enums.SCAN_CANCELLED}

    def test_specific_mappings(self):
        assert capture.map_native_state("CAPTURING") == enums.SCAN_CAPTURE_IN_PROGRESS
        assert capture.map_native_state("UPLOADED") == enums.SCAN_UPLOAD_COMPLETE
        assert capture.map_native_state("COMPLETE") == enums.SCAN_QUALITY_REVIEW

    def test_unknown_state_rejected(self):
        with pytest.raises(HTTPException) as e:
            capture.map_native_state("TELEPORTING")
        assert e.value.detail["error_code"] == "UNKNOWN_NATIVE_STATE"


# ========================= HTTP INTEGRATION =========================
class TestCaptureProofHTTP:
    def test_bootstrap_full_pipeline(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=60)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["authoritative"] is False
        assert d["scan_session"]["current_state"] == enums.SCAN_ACCEPTED
        assert d["guardian_result"]["verdict"] == enums.GUARDIAN_PASS
        up = d["upload"]
        assert up["checksum_verified"] is True
        assert up["total_chunks"] >= 2
        cand = d["candidate_model"]
        assert cand["model_state"] == enums.EM_DRAFT_CANDIDATE  # truth boundary
        assert cand["model_state"] != enums.VERIFIED_EXISTING
        assert d["entity_count"] == 12
        assert set(d["truth_classification_counts"].keys()) == {enums.MEASURED_EXISTING}

    def test_bootstrap_idempotent(self, homeowner_session, api_url):
        a = homeowner_session.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=60).json()
        b = homeowner_session.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=60).json()
        assert a["candidate_model"]["existing_model_version_id"] == \
            b["candidate_model"]["existing_model_version_id"]
        assert a["entity_count"] == b["entity_count"] == 12

    def test_storage_reference_masked(self, homeowner_session, api_url):
        d = homeowner_session.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=60).json()
        am = d.get("artifact_manifest")
        if am:  # present when object storage is reachable
            assert am["storage_object_reference"] == "<governed-object-store-reference>"

    def test_authorized_content_roundtrip(self, homeowner_session, api_url):
        d = homeowner_session.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=60).json()
        if not d.get("artifact_manifest"):
            pytest.skip("object storage unavailable in this environment")
        aid = "rf-art-capture-proof-pc-h014b"
        declared = d["upload"]["checksum_sha256"]
        r = homeowner_session.get(_api(api_url, f"/artifacts/{aid}/content"), timeout=60)
        if r.status_code == 502:
            # Manifest may exist from a prior process while in-memory fake store was reset.
            pytest.skip("object storage unavailable in this environment")
        assert r.status_code == 200
        assert hashlib.sha256(r.content).hexdigest() == declared


class TestResumableUploadHTTP:
    def _scan(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]

    def _init(self, s, api_url, sid, data, chunk_size):
        return s.post(_api(api_url, f"/scan-sessions/{sid}/uploads"),
                      json={"artifact_type": "POINT_CLOUD",
                            "checksum_sha256": hashlib.sha256(data).hexdigest(),
                            "total_size": len(data), "chunk_size": chunk_size}, timeout=30)

    def test_happy_path(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(20)
        up = self._init(s, api_url, sid, data, 8).json()
        assert up["total_chunks"] == 3
        for i in range(3):
            chunk = data[i * 8:(i + 1) * 8]
            r = s.put(_api(api_url, f"/uploads/{up['id']}/chunks/{i}"),
                      data=chunk, headers={"Content-Type": "application/octet-stream"}, timeout=30)
            assert r.status_code == 200, r.text
        comp = _complete(s, api_url, up['id'])
        assert comp.status_code == 200, comp.text
        assert comp.json()["checksum_verified"] is True

    def test_resume_missing_chunk(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(20)
        up = self._init(s, api_url, sid, data, 8).json()
        # Upload only chunk 0, then query status → chunk 1,2 missing.
        s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=data[0:8],
              headers={"Content-Type": "application/octet-stream"}, timeout=30)
        st = s.get(_api(api_url, f"/uploads/{up['id']}"), timeout=30).json()
        assert st["missing_indexes"] == [1, 2] and st["complete"] is False
        # Completing early is rejected.
        early = s.post(_api(api_url, f"/uploads/{up['id']}/complete"), timeout=30)
        assert early.status_code == 409 and early.json()["detail"]["error_code"] == "INCOMPLETE_UPLOAD"
        # Resume the rest.
        s.put(_api(api_url, f"/uploads/{up['id']}/chunks/1"), data=data[8:16],
              headers={"Content-Type": "application/octet-stream"}, timeout=30)
        s.put(_api(api_url, f"/uploads/{up['id']}/chunks/2"), data=data[16:20],
              headers={"Content-Type": "application/octet-stream"}, timeout=30)
        comp = _complete(s, api_url, up['id'])
        assert comp.status_code == 200, comp.text

    def test_checksum_mismatch_rejected(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        # Declare a checksum that will not match the uploaded bytes.
        up = s.post(_api(api_url, f"/scan-sessions/{sid}/uploads"),
                    json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                          "total_size": 10, "chunk_size": 8192}, timeout=30).json()
        s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=b"HELLOWORLD",
              headers={"Content-Type": "application/octet-stream"}, timeout=30)
        comp = s.post(_api(api_url, f"/uploads/{up['id']}/complete"), timeout=30)
        assert comp.status_code == 422 and comp.json()["detail"]["error_code"] == "CHECKSUM_MISMATCH"

    def test_chunk_size_mismatch_rejected(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(20)
        up = self._init(s, api_url, sid, data, 8).json()
        # Non-final chunk with the wrong size is rejected.
        r = s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=data[0:5],
                  headers={"Content-Type": "application/octet-stream"}, timeout=30)
        assert r.status_code == 422 and r.json()["detail"]["error_code"] == "CHUNK_SIZE_MISMATCH"

    def test_invalid_chunk_size_rejected_at_init(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        r = s.post(_api(api_url, f"/scan-sessions/{sid}/uploads"),
                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                         "total_size": 100, "chunk_size": 99_000_000}, timeout=30)
        assert r.status_code == 422 and r.json()["detail"]["error_code"] == "CHUNK_SIZE_TOO_LARGE"


class TestGuardianAndCandidateHTTP:
    def _scan(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]

    def test_guardian_evaluate_persists(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        r = s.post(_api(api_url, f"/scan-sessions/{sid}/guardian/evaluate"), json=GOOD_REPORT, timeout=30)
        assert r.status_code == 200, r.text
        assert r.json()["guardian_result"]["verdict"] == enums.GUARDIAN_PASS
        got = s.get(_api(api_url, f"/scan-sessions/{sid}"), timeout=30).json()
        assert got["guardian_result"]["verdict"] == enums.GUARDIAN_PASS
        assert got["coverage_state"] == enums.COVERAGE_COMPLETE

    def test_candidate_requires_quality_review(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)  # state == CREATED
        r = s.post(_api(api_url, f"/scan-sessions/{sid}/candidate"),
                   json={"derived_structure": {"dimensions_m": {"width": 4, "length": 5, "height": 2.7}}},
                   timeout=30)
        assert r.status_code == 409 and r.json()["detail"]["error_code"] == "CAPTURE_NOT_REVIEWABLE"

    def test_capture_progress_records_state(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        r = s.post(_api(api_url, f"/scan-sessions/{sid}/capture-progress"),
                   json={"native_state": "CAPTURING", "captured_area_m2": 12.0,
                         "surface_coverage": {"WALL": 0.5}}, timeout=30)
        assert r.status_code == 200, r.text
        assert r.json()["telemetry"]["mapped_scan_state"] == enums.SCAN_CAPTURE_IN_PROGRESS


class TestCaptureAuthorizationHTTP:
    def test_unauthenticated_401(self, api_url):
        r = requests.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=30)
        assert r.status_code == 401

    def test_contractor_denied(self, contractor_session, api_url):
        r = contractor_session.post(_api(api_url, "/development/capture-proof/bootstrap"), timeout=30)
        assert r.status_code == 403

    def test_upload_on_missing_scan_nondisclosure_404(self, homeowner_session, api_url):
        r = homeowner_session.post(_api(api_url, f"/scan-sessions/rf-scan-{uuid.uuid4()}/uploads"),
                                   json={"artifact_type": "POINT_CLOUD", "checksum_sha256": "a" * 64,
                                         "total_size": 10, "chunk_size": 8192}, timeout=30)
        assert r.status_code == 404 and r.json()["detail"]["error_code"] == "NOT_FOUND"


class TestStorageBoundaryHTTP:
    """H-014B.1 — prove MongoDB metadata-only staging via live HTTP + DB."""

    def _scan(self, s, api_url):
        return s.post(_api(api_url, f"/properties/{REF}/scan-sessions"),
                      json={"capture_type": "INTERIOR_LIDAR"}, timeout=30).json()["id"]

    def _init(self, s, api_url, sid, data, chunk_size):
        return s.post(_api(api_url, f"/scan-sessions/{sid}/uploads"),
                      json={"artifact_type": "POINT_CLOUD",
                            "checksum_sha256": hashlib.sha256(data).hexdigest(),
                            "total_size": len(data), "chunk_size": chunk_size}, timeout=30)

    def test_mongo_chunk_docs_have_no_binary(self, homeowner_session, api_url, db):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(20)
        up = self._init(s, api_url, sid, data, 8).json()
        for i in range(3):
            chunk = data[i * 8:(i + 1) * 8]
            r = s.put(_api(api_url, f"/uploads/{up['id']}/chunks/{i}"),
                      data=chunk, headers={"Content-Type": "application/octet-stream"}, timeout=30)
            assert r.status_code == 200, r.text
            body = r.json()
            assert "bucket" not in body and "signed_url" not in body and "public_url" not in body
            assert "object_reference" not in body
            assert "tenant/" not in str(body)
        docs = list(db[enums.C_UPLOAD_CHUNKS].find({"upload_session_id": up["id"]}))
        assert len(docs) == 3
        for doc in docs:
            for field in ("data", "data_b64", "bytes", "payload", "content", "base64", "binary"):
                assert field not in doc
            assert doc.get("object_reference", "").startswith("orf-")
            assert doc.get("tenant_id") == enums.TENANT_ID
            assert doc.get("property_id") == REF
            key = doc.get("_storage_key_internal") or ""
            assert f"tenant/{enums.TENANT_ID}/property/{REF}/reality/staging/" in key

    def test_duplicate_and_conflict_http(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(8)
        up = self._init(s, api_url, sid, data, 8).json()
        a = s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=data,
                  headers={"Content-Type": "application/octet-stream"}, timeout=30)
        b = s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=data,
                  headers={"Content-Type": "application/octet-stream"}, timeout=30)
        assert a.status_code == 200 and b.status_code == 200
        assert b.json().get("duplicate") is True
        c = s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=os.urandom(8),
                  headers={"Content-Type": "application/octet-stream"}, timeout=30)
        assert c.status_code == 409 and c.json()["detail"]["error_code"] == "CONFLICTING_CHUNK"

    def test_abort_replay_idempotent_http(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(8)
        up = self._init(s, api_url, sid, data, 8).json()
        s.put(_api(api_url, f"/uploads/{up['id']}/chunks/0"), data=data,
              headers={"Content-Type": "application/octet-stream"}, timeout=30)
        a = s.post(_api(api_url, f"/uploads/{up['id']}/abort"), timeout=30)
        b = s.post(_api(api_url, f"/uploads/{up['id']}/abort"), timeout=30)
        assert a.status_code == 200 and b.status_code == 200
        assert b.json().get("idempotent_replay") is True

    def test_completion_replay_idempotent_http(self, homeowner_session, api_url):
        s = homeowner_session
        sid = self._scan(s, api_url)
        data = os.urandom(16)
        up = self._init(s, api_url, sid, data, 8).json()
        for i in range(2):
            s.put(_api(api_url, f"/uploads/{up['id']}/chunks/{i}"),
                  data=data[i * 8:(i + 1) * 8],
                  headers={"Content-Type": "application/octet-stream"}, timeout=30)
        a = _complete(s, api_url, up["id"])
        b = _complete(s, api_url, up["id"])
        assert a.status_code == 200, a.text
        assert b.status_code == 200 and b.json().get("idempotent_replay") is True
        art = a.json().get("artifact") or {}
        assert art.get("storage_object_reference") == "<governed-object-store-reference>"
        assert "signed_url" not in art and "public_url" not in art and "bucket" not in art
