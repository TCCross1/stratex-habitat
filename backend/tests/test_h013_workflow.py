"""
H-013 Batch 2 — Workflow state-machine + publication-gate unit tests (Phase 11).
Pure logic (no DB): legal/illegal transitions and the backend publication gate.
DB-backed flows (resume/cancel/expire/replay/concurrency) are exercised over HTTP
by the backend testing agent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import workflow as wf  # noqa: E402
import readiness_policy as rp  # noqa: E402


class TestTransitions:
    def test_forward_chain_is_legal(self):
        chain = [
            (wf.S_QUESTION_RECEIVED, wf.S_CONTEXT_RESOLVED),
            (wf.S_CONTEXT_RESOLVED, wf.S_ANSWER_PRESENTED),
            (wf.S_ANSWER_PRESENTED, wf.S_ACTION_RECOMMENDED),
            (wf.S_ACTION_RECOMMENDED, wf.S_ACTION_CONFIRMED),
            (wf.S_ACTION_CONFIRMED, wf.S_PROJECT_CREATED),
            (wf.S_PROJECT_CREATED, wf.S_ESTIMATE_CREATED),
            (wf.S_ESTIMATE_CREATED, wf.S_SCENARIOS_REVIEWED),
            (wf.S_SCENARIOS_REVIEWED, wf.S_READINESS_REVIEWED),
            (wf.S_READINESS_REVIEWED, wf.S_PACKAGE_PREVIEWED),
            (wf.S_PACKAGE_PREVIEWED, wf.S_PUBLICATION_APPROVED),
            (wf.S_PUBLICATION_APPROVED, wf.S_OPPORTUNITY_PUBLISHED),
        ]
        for frm, to in chain:
            assert wf.can_transition(frm, to), f"{frm}->{to} should be legal"

    def test_illegal_skip_forward(self):
        assert not wf.can_transition(wf.S_QUESTION_RECEIVED, wf.S_OPPORTUNITY_PUBLISHED)
        assert not wf.can_transition(wf.S_ANSWER_PRESENTED, wf.S_PACKAGE_PREVIEWED)

    def test_terminal_states_have_no_transitions(self):
        for term in (wf.S_OPPORTUNITY_PUBLISHED, wf.S_CANCELLED, wf.S_EXPIRED, wf.S_FAILED_FINAL):
            assert wf.LEGAL_TRANSITIONS[term] == set()

    def test_cancel_allowed_from_active(self):
        assert wf.can_transition(wf.S_READINESS_REVIEWED, wf.S_CANCELLED)


def _ready_wf(state=wf.S_PACKAGE_PREVIEWED, acks=None):
    return {
        "current_state": state, "property_id": "prop-1", "version": 5,
        "design_project_ref": "proj-1", "estimate_snapshot": {"material": "GAF Timberline HDZ"},
        "contractor_package_version": "cp-abc", "redaction_settings": {"remove_personal_info": True},
        "acknowledged_blockers": list(acks or []), "correlation_id": "corr-1",
    }


class TestPublicationGate:
    def test_blocked_when_conditional_not_acknowledged(self):
        w = _ready_wf(acks=[])
        readiness = rp.assess(w["acknowledged_blockers"])
        ok, blocking, reasons, remediation = wf.evaluate_publication_gate(
            w, approval=True, property_id="prop-1", readiness=readiness)
        assert ok is False
        assert "RDY-DECK-CONDITION" in blocking

    def test_allowed_when_all_gates_pass(self):
        w = _ready_wf(acks=["RDY-DECK-CONDITION"])
        readiness = rp.assess(w["acknowledged_blockers"])
        ok, blocking, reasons, remediation = wf.evaluate_publication_gate(
            w, approval=True, property_id="prop-1", readiness=readiness)
        assert ok is True, (blocking, reasons)

    def test_blocked_without_approval(self):
        w = _ready_wf(acks=["RDY-DECK-CONDITION"])
        readiness = rp.assess(w["acknowledged_blockers"])
        ok, blocking, *_ = wf.evaluate_publication_gate(
            w, approval=False, property_id="prop-1", readiness=readiness)
        assert ok is False and "APPROVAL" in blocking

    def test_blocked_on_property_mismatch(self):
        w = _ready_wf(acks=["RDY-DECK-CONDITION"])
        readiness = rp.assess(w["acknowledged_blockers"])
        ok, blocking, *_ = wf.evaluate_publication_gate(
            w, approval=True, property_id="other-prop", readiness=readiness)
        assert ok is False and "PROPERTY_MISMATCH" in blocking

    def test_blocked_when_missing_prerequisites(self):
        w = _ready_wf(acks=["RDY-DECK-CONDITION"])
        w["estimate_snapshot"] = None
        w["contractor_package_version"] = None
        readiness = rp.assess(w["acknowledged_blockers"])
        ok, blocking, *_ = wf.evaluate_publication_gate(
            w, approval=True, property_id="prop-1", readiness=readiness)
        assert ok is False and "ESTIMATE" in blocking and "PACKAGE" in blocking

    def test_hard_blocker_cannot_be_bypassed_by_client(self):
        # Even with everything else satisfied, an unresolved HARD blocker blocks.
        w = _ready_wf(acks=["RDY-DECK-CONDITION"])
        readiness = rp.assess(w["acknowledged_blockers"], overrides={"RDY-OWNERSHIP": "MISSING"})
        ok, blocking, *_ = wf.evaluate_publication_gate(
            w, approval=True, property_id="prop-1", readiness=readiness)
        assert ok is False and "RDY-OWNERSHIP" in blocking
