"""
H-013 Batch 2A — Governed Publication (single path) integration tests.

Proves, against the live backend + MongoDB, that there is exactly ONE
authoritative publication path and the legacy compatibility wrapper cannot
bypass it:

  * the governed workflow publish endpoint is reachable and gated
    (regression guard for the stray-decorator shadowing that returned 405);
  * the legacy POST /steward/publish routes through the SAME governed service
    (no ungated bypass);
  * a deterministic HARD_BLOCKER scenario returns 409, creates NO opportunity,
    and writes HARD_BLOCKER_DETECTED + PUBLICATION_BLOCKED audit events with no
    PROJECT_OPPORTUNITY_PUBLISHED;
  * a satisfied publication creates exactly ONE opportunity + a
    PROJECT_OPPORTUNITY_PUBLISHED audit event;
  * publication is idempotent on replay (same opportunity, no new row);
  * the full governed workflow journey (create -> transitions -> ack -> publish)
    publishes through the governed endpoint.

Relocated + refactored from the previous root-level `backend_test_batch2.py`
(hard-coded preview URL removed; config comes from conftest).
"""
import uuid

import pytest

PID = "villa-horizon-uuid"
DECK = "RDY-DECK-CONDITION"      # CONDITIONAL blocker (must be acknowledged)
HARD = "RDY-OWNERSHIP"          # HARD blocker (can never be bypassed)


def _legacy_publish(session, api_url, scenario_id=None, **extra):
    body = {"property_id": PID, "scenario_id": scenario_id or str(uuid.uuid4())}
    body.update(extra)
    return session.post(f"{api_url}/steward/publish", json=body, timeout=30), body


class TestGovernedPublicationSinglePath:
    def test_governed_endpoint_reachable_and_gated(self, homeowner_session, api_url):
        """Regression: the governed publish route must not be shadowed (was 405)."""
        wf = homeowner_session.post(f"{api_url}/steward/workflow", json={}, timeout=30).json()
        r = homeowner_session.post(
            f"{api_url}/steward/workflow/{wf['id']}/publish",
            json={"approval": True}, timeout=30)
        assert r.status_code == 409, r.text
        assert r.json()["detail"]["error_code"] == "PUBLICATION_BLOCKED"

    def test_legacy_publish_no_longer_bypasses_gate(self, homeowner_session, api_url):
        """Legacy route must enforce the deck CONDITIONAL blocker when unacknowledged."""
        r, _ = _legacy_publish(homeowner_session, api_url)  # no acknowledgment
        assert r.status_code == 409, r.text
        detail = r.json()["detail"]
        assert detail["error_code"] == "PUBLICATION_BLOCKED"
        assert DECK in detail["blocking_item_ids"]

    def test_hard_blocker_deterministic(self, homeowner_session, api_url, db):
        """Forced HARD blocker: 409, no opportunity, correct audit events."""
        q_before = db.quotes.count_documents({})
        r, _ = _legacy_publish(
            homeowner_session, api_url,
            acknowledged_blockers=[DECK],               # deck acknowledged...
            readiness_overrides={HARD: "MISSING"})      # ...but ownership forced missing
        assert r.status_code == 409, r.text
        detail = r.json()["detail"]
        assert detail["error_code"] == "PUBLICATION_BLOCKED"
        assert HARD in detail["blocking_item_ids"]
        corr = detail["correlation_id"]

        assert db.quotes.count_documents({}) == q_before, "no opportunity may be created on a HARD block"
        assert db.audit_events.count_documents(
            {"correlation_id": corr, "event_type": "HARD_BLOCKER_DETECTED"}) >= 1
        assert db.audit_events.count_documents(
            {"correlation_id": corr, "event_type": "PUBLICATION_BLOCKED"}) >= 1
        assert db.audit_events.count_documents(
            {"correlation_id": corr, "event_type": "PROJECT_OPPORTUNITY_PUBLISHED"}) == 0

    def test_positive_publish_creates_single_opportunity_and_is_idempotent(
            self, homeowner_session, api_url, db):
        q_before = db.quotes.count_documents({})
        r, body = _legacy_publish(homeowner_session, api_url, acknowledged_blockers=[DECK])
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "published"
        opp_id = data["opportunity_id"]

        assert db.quotes.count_documents({}) == q_before + 1
        assert db.quotes.count_documents({"id": opp_id}) == 1
        assert db.audit_events.count_documents(
            {"correlation_id": data["correlation_id"],
             "event_type": "PROJECT_OPPORTUNITY_PUBLISHED"}) >= 1

        # idempotent replay of the SAME property+scenario -> same opportunity, no new row
        r2 = homeowner_session.post(f"{api_url}/steward/publish", json=body, timeout=30)
        assert r2.status_code == 200, r2.text
        data2 = r2.json()
        assert data2["opportunity_id"] == opp_id
        assert data2.get("idempotent_replay") is True
        assert db.quotes.count_documents({}) == q_before + 1, "replay must not create a second opportunity"

    def test_full_governed_workflow_journey_publishes(self, homeowner_session, api_url, db):
        s, base = homeowner_session, api_url
        wf = s.post(f"{base}/steward/workflow", json={}, timeout=30).json()
        wid = wf["id"]
        chain = [
            "CONTEXT_RESOLVED", "ANSWER_PRESENTED", "ACTION_RECOMMENDED", "ACTION_CONFIRMED",
            "PROJECT_CREATED", "ESTIMATE_CREATED", "SCENARIOS_REVIEWED", "READINESS_REVIEWED",
            "PACKAGE_PREVIEWED",
        ]
        for state in chain:
            r = s.post(f"{base}/steward/workflow/{wid}/transition",
                       json={"to_state": state}, timeout=30)
            assert r.status_code == 200, f"transition -> {state} failed: {r.text}"

        # acknowledge the deck CONDITIONAL blocker through the governed endpoint
        r = s.post(f"{base}/steward/workflow/{wid}/acknowledge",
                   json={"item_id": DECK}, timeout=30)
        assert r.status_code == 200, r.text

        q_before = db.quotes.count_documents({})
        r = s.post(f"{base}/steward/workflow/{wid}/publish",
                   json={"approval": True}, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "published"
        assert data["workflow"]["current_state"] == "OPPORTUNITY_PUBLISHED"
        assert db.quotes.count_documents({}) == q_before + 1
