"""
STRATEX HABITAT — Build Ready Blocker Policy (H-013 Batch 2, Phase 5)

Authoritative, backend-owned readiness classification. The frontend must NOT
determine blocking behavior; it renders what this policy returns.

Four readiness levels:
  HARD_BLOCKER        — publication forbidden until resolved
  CONDITIONAL_BLOCKER — publication allowed only when acknowledged (and the
                        contractor package exposes the site-verification need)
  WARNING             — publication allowed, disclosed
  INFORMATIONAL_GAP   — publication allowed, item remains listed as incomplete
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Iterable, Optional

HARD_BLOCKER = "HARD_BLOCKER"
CONDITIONAL_BLOCKER = "CONDITIONAL_BLOCKER"
WARNING = "WARNING"
INFORMATIONAL_GAP = "INFORMATIONAL_GAP"

RESOLVED_STATES = {"VERIFIED", "COMPLETE", "RESOLVED"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Canonical roof-slice readiness items. `default_state` is the seeded happy-path.
ROOF_READINESS_ITEMS = [
    {"item_id": "RDY-OWNERSHIP", "name": "Property Ownership Authorization",
     "classification": HARD_BLOCKER, "default_state": "VERIFIED", "score": 10,
     "description": "Authorized homeowner of record for this property.",
     "why_it_matters": "Only the authorized owner may publish a Project Opportunity for the property.",
     "who_can_verify": "Passport ownership projection", "site_verification_required": False},

    {"item_id": "RDY-PROPERTY-INFO", "name": "Property Information",
     "classification": INFORMATIONAL_GAP, "default_state": "COMPLETE", "score": 10,
     "description": "Standard boundaries and location confirmed.",
     "why_it_matters": "Baseline property identity for scoping.",
     "who_can_verify": "Central Kentucky demonstration GIS sample", "site_verification_required": False},

    {"item_id": "RDY-ROOF-GEOMETRY", "name": "Roof Geometry takeoff",
     "classification": INFORMATIONAL_GAP, "default_state": "COMPLETE", "score": 10,
     "description": "3D Mesh takeoff calculated 3,200 sq ft.",
     "why_it_matters": "Quantities drive the planning estimate.",
     "who_can_verify": "STRATEX Digital Twin Core", "site_verification_required": False},

    {"item_id": "RDY-DECK-CONDITION", "name": "Existing Deck & Underlayment Condition",
     "classification": CONDITIONAL_BLOCKER, "default_state": "MISSING", "score": 0,
     "description": "Concealed North Slope deflection/thermal anomaly indicates potential decking rot.",
     "why_it_matters": "Hidden deck condition materially changes scope and cost; must be verified on site.",
     "who_can_verify": "Licensed inspector (core drill) OR contractor during site review",
     "site_verification_required": True},

    {"item_id": "RDY-WARRANTY", "name": "Shingle Warranty Verification",
     "classification": WARNING, "default_state": "UNVERIFIED", "score": 5,
     "description": "Manufacturer GAF warranty certificate is unuploaded.",
     "why_it_matters": "Warranty may offset cost; absence is disclosed but not blocking.",
     "who_can_verify": "Homeowner upload of physical warranty papers", "site_verification_required": False},

    {"item_id": "RDY-PERMIT-HOA", "name": "Permit & HOA considerations",
     "classification": INFORMATIONAL_GAP, "default_state": "COMPLETE", "score": 10,
     "description": "Standard Lexington zoning and Central Kentucky demonstration HOA materials (sample-only).",
     "why_it_matters": "Confirms no unusual approval path.",
     "who_can_verify": "Zoning Database Sync", "site_verification_required": False},
]

DEFAULT_READINESS_SCORE = 65


def assess(acknowledged: Optional[Iterable[str]] = None,
           overrides: Optional[Dict[str, str]] = None,
           resolver_identity: Optional[str] = None) -> dict:
    """Compute the authoritative readiness assessment.

    acknowledged: item_ids the homeowner has explicitly acknowledged.
    overrides:    {item_id: verification_state} to reflect resolved/changed items.
    """
    acknowledged = set(acknowledged or [])
    overrides = overrides or {}
    items = []
    for defn in ROOF_READINESS_ITEMS:
        state = overrides.get(defn["item_id"], defn["default_state"])
        resolved = state in RESOLVED_STATES
        acked = defn["item_id"] in acknowledged
        cls = defn["classification"]
        if cls == HARD_BLOCKER:
            blocks = not resolved
        elif cls == CONDITIONAL_BLOCKER:
            blocks = (not resolved) and (not acked)
        else:
            blocks = False
        ack_required = cls == CONDITIONAL_BLOCKER and not resolved
        items.append({
            "item_id": defn["item_id"],
            "item": defn["name"],                 # legacy H-012 field name
            "classification": cls,
            "description": defn["description"],
            "why": defn["why_it_matters"],
            "why_it_matters": defn["why_it_matters"],
            "who_can_verify": defn["who_can_verify"],
            "verified_by": defn["who_can_verify"],  # legacy field
            "verification_state": state,
            "status": state,                        # legacy field
            "site_verification_required": defn["site_verification_required"],
            "acknowledgment_required": ack_required,
            "acknowledged": acked,
            "blocks_publication": blocks,
            "score": defn["score"],
            "resolved_at": _now_iso() if resolved and defn["item_id"] in overrides else None,
            "resolver_identity": resolver_identity if resolved and defn["item_id"] in overrides else None,
        })

    unresolved_hard = [i["item_id"] for i in items
                       if i["classification"] == HARD_BLOCKER and i["blocks_publication"]]
    required_acks = [i["item_id"] for i in items
                     if i["classification"] == CONDITIONAL_BLOCKER and i["blocks_publication"]]
    can_publish = (len(unresolved_hard) == 0 and len(required_acks) == 0)

    return {
        "project_readiness_score": DEFAULT_READINESS_SCORE,
        "max_score": 100,
        "classification": "PLANNING_STAGE_ONLY (Unpublished)" if not can_publish else "READY_FOR_PUBLICATION",
        "can_publish": can_publish,
        "unresolved_hard_blocker_ids": unresolved_hard,
        "required_acknowledgment_ids": required_acks,
        "conditional_blocker_ids": [i["item_id"] for i in items
                                    if i["classification"] == CONDITIONAL_BLOCKER],
        "priority_checklist": items,
        "assessed_at": _now_iso(),
    }


def conditional_item_ids() -> set:
    return {d["item_id"] for d in ROOF_READINESS_ITEMS if d["classification"] == CONDITIONAL_BLOCKER}


def is_known_item(item_id: str) -> bool:
    return any(d["item_id"] == item_id for d in ROOF_READINESS_ITEMS)
