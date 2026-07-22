"""
H-013 Batch 2 — Build Ready blocker policy unit tests (Phase 11).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import readiness_policy as rp  # noqa: E402

HARD = "RDY-OWNERSHIP"
COND = "RDY-DECK-CONDITION"


class TestReadinessPolicy:
    def test_default_conditional_blocker_blocks_until_ack(self):
        a = rp.assess()
        assert a["can_publish"] is False
        assert COND in a["required_acknowledgment_ids"]
        deck = next(i for i in a["priority_checklist"] if i["item_id"] == COND)
        assert deck["classification"] == rp.CONDITIONAL_BLOCKER
        assert deck["blocks_publication"] is True
        assert deck["status"] == "MISSING"          # backward-compatible legacy field
        assert deck["acknowledgment_required"] is True

    def test_conditional_acknowledged_permits_publication(self):
        a = rp.assess(acknowledged={COND})
        assert a["can_publish"] is True
        assert a["required_acknowledgment_ids"] == []

    def test_hard_blocker_prohibits_publication(self):
        a = rp.assess(acknowledged={COND}, overrides={HARD: "MISSING"})
        assert a["can_publish"] is False
        assert HARD in a["unresolved_hard_blocker_ids"]

    def test_resolved_conditional_permits_without_ack(self):
        a = rp.assess(overrides={COND: "VERIFIED"})
        assert a["can_publish"] is True
        deck = next(i for i in a["priority_checklist"] if i["item_id"] == COND)
        assert deck["blocks_publication"] is False
        assert deck["resolved_at"] is not None

    def test_warning_and_informational_never_block(self):
        a = rp.assess(acknowledged={COND})
        for i in a["priority_checklist"]:
            if i["classification"] in (rp.WARNING, rp.INFORMATIONAL_GAP):
                assert i["blocks_publication"] is False

    def test_default_score_backward_compatible(self):
        assert rp.assess()["project_readiness_score"] == 65
