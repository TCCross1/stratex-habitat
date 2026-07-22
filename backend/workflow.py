"""
STRATEX HABITAT — Persistent Steward Workflow (H-013 Batch 2, Phases 6-10)

Owns:
  * the persistent `steward_workflows` collection + explicit state machine
  * optimistic-concurrency (version) writes + idempotency-key replay protection
  * backend-enforced publication gate (Phase 6)
  * immutable audit events (Phase 9)
  * index initialization (Phase 10)

Tenant model: single demo tenant "stratex-habitat"; Steward is restricted to the
authorized homeowner. Habitat never writes canonical Passport facts here — it only
persists homeowner planning workflow state and references.
"""
from __future__ import annotations
import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

import pricebook
import readiness_policy
import passport_projection as projection
from steward import get_steward_user, get_db

logger = logging.getLogger("habitat.workflow")

workflow_router = APIRouter(prefix="/steward/workflow")

TENANT_ID = "stratex-habitat"
HOMEOWNER_EMAIL = "alex@stratexhabitat.com"
COLLECTION = "steward_workflows"

# ---------------------------------------------------------------------------
# States + legal transitions
# ---------------------------------------------------------------------------
S_QUESTION_RECEIVED = "QUESTION_RECEIVED"
S_CONTEXT_RESOLVED = "CONTEXT_RESOLVED"
S_ANSWER_PRESENTED = "ANSWER_PRESENTED"
S_ACTION_RECOMMENDED = "ACTION_RECOMMENDED"
S_ACTION_CONFIRMED = "ACTION_CONFIRMED"
S_PROJECT_CREATED = "PROJECT_CREATED"
S_ESTIMATE_CREATED = "ESTIMATE_CREATED"
S_SCENARIOS_REVIEWED = "SCENARIOS_REVIEWED"
S_READINESS_REVIEWED = "READINESS_REVIEWED"
S_PACKAGE_PREVIEWED = "PACKAGE_PREVIEWED"
S_PUBLICATION_APPROVED = "PUBLICATION_APPROVED"
S_OPPORTUNITY_PUBLISHED = "OPPORTUNITY_PUBLISHED"
S_CANCELLED = "CANCELLED"
S_EXPIRED = "EXPIRED"
S_FAILED_RECOVERABLE = "FAILED_RECOVERABLE"
S_FAILED_FINAL = "FAILED_FINAL"

TERMINAL_STATES = {S_OPPORTUNITY_PUBLISHED, S_CANCELLED, S_EXPIRED, S_FAILED_FINAL}

LEGAL_TRANSITIONS = {
    S_QUESTION_RECEIVED: {S_CONTEXT_RESOLVED, S_CANCELLED, S_FAILED_RECOVERABLE, S_EXPIRED},
    S_CONTEXT_RESOLVED: {S_ANSWER_PRESENTED, S_CANCELLED, S_FAILED_RECOVERABLE, S_EXPIRED},
    S_ANSWER_PRESENTED: {S_ACTION_RECOMMENDED, S_CANCELLED, S_EXPIRED},
    S_ACTION_RECOMMENDED: {S_ACTION_CONFIRMED, S_CANCELLED, S_EXPIRED},
    S_ACTION_CONFIRMED: {S_PROJECT_CREATED, S_CANCELLED, S_FAILED_RECOVERABLE, S_EXPIRED},
    S_PROJECT_CREATED: {S_ESTIMATE_CREATED, S_CANCELLED, S_EXPIRED},
    S_ESTIMATE_CREATED: {S_SCENARIOS_REVIEWED, S_CANCELLED, S_EXPIRED},
    S_SCENARIOS_REVIEWED: {S_READINESS_REVIEWED, S_CANCELLED, S_EXPIRED},
    S_READINESS_REVIEWED: {S_PACKAGE_PREVIEWED, S_CANCELLED, S_EXPIRED},
    S_PACKAGE_PREVIEWED: {S_PUBLICATION_APPROVED, S_CANCELLED, S_EXPIRED},
    S_PUBLICATION_APPROVED: {S_OPPORTUNITY_PUBLISHED, S_PACKAGE_PREVIEWED, S_CANCELLED,
                             S_FAILED_RECOVERABLE, S_EXPIRED},
    S_FAILED_RECOVERABLE: {S_CONTEXT_RESOLVED, S_ACTION_CONFIRMED, S_PROJECT_CREATED,
                           S_PUBLICATION_APPROVED, S_CANCELLED, S_FAILED_FINAL, S_EXPIRED},
    S_OPPORTUNITY_PUBLISHED: set(),
    S_CANCELLED: set(),
    S_EXPIRED: set(),
    S_FAILED_FINAL: set(),
}


def can_transition(frm: str, to: str) -> bool:
    return to in LEGAL_TRANSITIONS.get(frm, set())


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ttl_hours() -> int:
    try:
        return int(os.environ.get("HABITAT_WORKFLOW_TTL_HOURS", "72"))
    except ValueError:
        return 72


def _require_homeowner(user: dict):
    if user.get("email") != HOMEOWNER_EMAIL:
        raise HTTPException(status_code=403, detail="Tenant access restricted")


def _public(wf: dict) -> dict:
    wf = dict(wf)
    wf.pop("_id", None)
    return wf


async def write_audit(db, event_type: str, user: dict, wf: dict, *,
                      correlation_id: str = None, before_state: str = None,
                      after_state: str = None, entity_refs: dict = None, extra: dict = None):
    """Immutable audit event. No secrets / no full documents / no raw evidence."""
    if db is None:
        return
    doc = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "tenant_id": wf.get("tenant_id", TENANT_ID),
        "property_id": wf.get("property_id"),
        "actor": {"homeowner_id": user.get("id"), "email": user.get("email")},
        "workflow_id": wf.get("id"),
        "correlation_id": correlation_id or wf.get("correlation_id"),
        "timestamp": now_iso(),
        "entity_references": entity_refs or {},
        "before_state": before_state,
        "after_state": after_state,
    }
    if extra:
        doc["details"] = extra
    await db.audit_events.insert_one(doc)


async def init_indexes(db):
    """Phase 10 — must be created explicitly, not left to implicit creation."""
    if db is None:
        return
    col = db[COLLECTION]
    await col.create_index("id", unique=True, name="ux_workflow_id")
    await col.create_index([("tenant_id", 1), ("property_id", 1)], name="ix_tenant_property")
    await col.create_index([("tenant_id", 1), ("homeowner_id", 1)], name="ix_tenant_homeowner")
    await col.create_index("current_state", name="ix_state")
    await col.create_index("updated_at", name="ix_updated_at")
    await col.create_index("expires_at", name="ix_expires_at")
    await col.create_index("publication_idempotency_key", sparse=True, name="ix_pub_idem")
    await col.create_index("confirmation_idempotency_key", sparse=True, name="ix_confirm_idem")
    logger.info("steward_workflows indexes ensured")


async def _maybe_expire(db, wf: dict) -> dict:
    if wf["current_state"] in TERMINAL_STATES:
        return wf
    exp = wf.get("expires_at")
    if exp and now_iso() > exp:
        res = await db[COLLECTION].update_one(
            {"id": wf["id"], "version": wf["version"]},
            {"$set": {"current_state": S_EXPIRED, "updated_at": now_iso()}, "$inc": {"version": 1}})
        if res.modified_count:
            fresh = await db[COLLECTION].find_one({"id": wf["id"]})
            await write_audit(db, "WORKFLOW_EXPIRED", {"id": wf.get("homeowner_id"), "email": HOMEOWNER_EMAIL},
                              fresh, before_state=wf["current_state"], after_state=S_EXPIRED)
            return fresh
    return wf


async def _load(db, wf_id: str, user: dict) -> dict:
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    wf = await db[COLLECTION].find_one({"id": wf_id})
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    # tenant/owner isolation
    if wf.get("homeowner_id") != user.get("id") or wf.get("tenant_id") != TENANT_ID:
        raise HTTPException(status_code=403, detail="Cross-tenant/owner access denied")
    return await _maybe_expire(db, wf)


# ---------------------------------------------------------------------------
# publication gate (pure — unit testable)
# ---------------------------------------------------------------------------
def evaluate_publication_gate(wf: dict, *, approval: bool, property_id: Optional[str],
                              readiness: dict):
    blocking: List[str] = []
    reasons: List[str] = []
    remediation: List[str] = []

    if wf.get("current_state") not in (S_PACKAGE_PREVIEWED, S_PUBLICATION_APPROVED):
        blocking.append("WORKFLOW_STATE")
        reasons.append(f"Workflow must be PACKAGE_PREVIEWED/PUBLICATION_APPROVED (is {wf.get('current_state')}).")
        remediation.append("Complete readiness review and package preview first.")
    if property_id and property_id != wf.get("property_id"):
        blocking.append("PROPERTY_MISMATCH")
        reasons.append("Requested property does not match the workflow property.")
        remediation.append("Publish against the workflow's own property.")
    if not approval:
        blocking.append("APPROVAL")
        reasons.append("Explicit homeowner publication approval is required.")
        remediation.append("Submit approval=true.")
    if not wf.get("design_project_ref"):
        blocking.append("PROJECT")
        reasons.append("No Design Studio project reference on the workflow.")
        remediation.append("Advance to PROJECT_CREATED.")
    if not wf.get("estimate_snapshot"):
        blocking.append("ESTIMATE")
        reasons.append("No estimate snapshot on the workflow.")
        remediation.append("Advance to ESTIMATE_CREATED.")
    if not wf.get("contractor_package_version"):
        blocking.append("PACKAGE")
        reasons.append("No contractor package version on the workflow.")
        remediation.append("Advance to PACKAGE_PREVIEWED.")
    if not wf.get("redaction_settings"):
        blocking.append("REDACTION")
        reasons.append("Missing redaction configuration.")
        remediation.append("Provide redaction settings on the package step.")

    # server-authoritative readiness (client cannot override)
    for hid in readiness.get("unresolved_hard_blocker_ids", []):
        blocking.append(hid)
        reasons.append(f"Unresolved HARD blocker: {hid}.")
        remediation.append(f"Resolve {hid} through required verification.")
    for cid in readiness.get("required_acknowledgment_ids", []):
        blocking.append(cid)
        reasons.append(f"CONDITIONAL blocker requires acknowledgment: {cid}.")
        remediation.append(f"Acknowledge {cid} (site verification required).")

    return (len(blocking) == 0), blocking, reasons, remediation


# ---------------------------------------------------------------------------
# request bodies
# ---------------------------------------------------------------------------
class CreateWorkflowReq(BaseModel):
    question: str = "Do I need a new roof?"
    property_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    expires_in_seconds: Optional[int] = None  # honored outside production (testing)


class TransitionReq(BaseModel):
    to_state: str
    expected_version: Optional[int] = None
    idempotency_key: Optional[str] = None
    material: Optional[str] = None
    redaction_settings: Optional[dict] = None
    recommended_action: Optional[str] = None
    investment_scenario_ref: Optional[str] = None


class AckReq(BaseModel):
    item_id: str
    expected_version: Optional[int] = None


class PublishReq(BaseModel):
    approval: bool = False
    property_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    expected_version: Optional[int] = None


class CancelReq(BaseModel):
    reason: Optional[str] = None
    expected_version: Optional[int] = None


# ---------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------
@workflow_router.post("")
async def create_workflow(body: CreateWorkflowReq, user: dict = Depends(get_steward_user),
                          db=Depends(get_db)):
    _require_homeowner(user)
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    pid = body.property_id
    if not pid:
        prop = await db.properties.find_one({"owner_id": {"$exists": True}})
        pid = prop["id"] if prop else "villa-horizon-uuid"

    # creation idempotency
    if body.idempotency_key:
        existing = await db[COLLECTION].find_one(
            {"homeowner_id": user["id"], "create_idempotency_key": body.idempotency_key})
        if existing:
            return _public(await _maybe_expire(db, existing))

    created = now_iso()
    ttl_seconds = _ttl_hours() * 3600
    if body.expires_in_seconds is not None and projection.resolve_mode() != projection.MODE_PRODUCTION:
        ttl_seconds = int(body.expires_in_seconds)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()

    wf = {
        "id": str(uuid.uuid4()),
        "tenant_id": TENANT_ID,
        "property_id": pid,
        "homeowner_id": user["id"],
        "current_state": S_QUESTION_RECEIVED,
        "version": 1,
        "correlation_id": str(uuid.uuid4()),
        "question": body.question,
        "context_projection_ref": None,
        "context_projection_version": None,
        "steward_response_ref": None,
        "recommended_action": None,
        "confirmation_event_id": None,
        "confirmation_idempotency_key": None,
        "design_project_ref": None,
        "estimate_snapshot": None,
        "investment_scenario_ref": None,
        "readiness_ref": None,
        "readiness_assessment": None,
        "acknowledged_blockers": [],
        "contractor_package_version": None,
        "redaction_settings": None,
        "publication_approval": None,
        "publication_idempotency_key": None,
        "opportunity_ref": None,
        "create_idempotency_key": body.idempotency_key,
        "processed_idempotency_keys": [],
        "cancelled": False,
        "cancel_reason": None,
        "created_at": created,
        "updated_at": created,
        "expires_at": expires_at,
        "state_history": [{"state": S_QUESTION_RECEIVED, "at": created}],
    }
    await db[COLLECTION].insert_one(wf)
    await write_audit(db, "STEWARD_WORKFLOW_CREATED", user, wf,
                      after_state=S_QUESTION_RECEIVED, entity_refs={"property_id": pid})
    return _public(wf)


@workflow_router.get("")
async def list_active_workflow(user: dict = Depends(get_steward_user), db=Depends(get_db)):
    _require_homeowner(user)
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    cur = db[COLLECTION].find({"homeowner_id": user["id"]}).sort("updated_at", -1).limit(10)
    items = [_public(await _maybe_expire(db, w)) async for w in cur]
    return {"workflows": items, "count": len(items)}


@workflow_router.get("/{wf_id}")
async def get_workflow(wf_id: str, user: dict = Depends(get_steward_user), db=Depends(get_db)):
    _require_homeowner(user)
    wf = await _load(db, wf_id, user)
    return _public(wf)


async def _apply_transition(db, wf: dict, user: dict, to_state: str, set_fields: dict,
                            idempotency_key: Optional[str]):
    set_fields = dict(set_fields)
    set_fields["current_state"] = to_state
    set_fields["updated_at"] = now_iso()
    push = {"state_history": {"state": to_state, "at": now_iso()}}
    inc = {"version": 1}
    query = {"id": wf["id"], "version": wf["version"]}
    update = {"$set": set_fields, "$inc": inc, "$push": push}
    if idempotency_key:
        update.setdefault("$addToSet", {})["processed_idempotency_keys"] = idempotency_key
    res = await db[COLLECTION].update_one(query, update)
    if res.modified_count != 1:
        raise HTTPException(status_code=409, detail={
            "error_code": "STALE_VERSION",
            "message": "Workflow was modified concurrently; reload and retry.",
            "correlation_id": wf.get("correlation_id"),
        })
    return await db[COLLECTION].find_one({"id": wf["id"]})


@workflow_router.post("/{wf_id}/transition")
async def transition_workflow(wf_id: str, body: TransitionReq,
                              user: dict = Depends(get_steward_user), db=Depends(get_db)):
    _require_homeowner(user)
    wf = await _load(db, wf_id, user)

    # idempotent replay
    if body.idempotency_key and body.idempotency_key in (wf.get("processed_idempotency_keys") or []):
        return _public(wf)

    if wf["current_state"] in TERMINAL_STATES:
        raise HTTPException(status_code=409, detail={
            "error_code": "TERMINAL_STATE",
            "message": f"Workflow is terminal ({wf['current_state']}).",
            "correlation_id": wf.get("correlation_id")})

    to_state = body.to_state
    if to_state == S_OPPORTUNITY_PUBLISHED:
        raise HTTPException(status_code=400, detail={
            "error_code": "USE_PUBLISH_ENDPOINT",
            "message": "Publication must go through POST /steward/workflow/{id}/publish."})
    if not can_transition(wf["current_state"], to_state):
        raise HTTPException(status_code=409, detail={
            "error_code": "ILLEGAL_TRANSITION",
            "message": f"Illegal transition {wf['current_state']} -> {to_state}.",
            "correlation_id": wf.get("correlation_id")})
    if body.expected_version is not None and body.expected_version != wf["version"]:
        raise HTTPException(status_code=409, detail={
            "error_code": "STALE_VERSION",
            "message": f"expected_version {body.expected_version} != current {wf['version']}.",
            "correlation_id": wf.get("correlation_id")})

    set_fields = {}
    audit_event = "STEWARD_WORKFLOW_TRANSITION"
    audit_extra = None
    corr = wf.get("correlation_id")

    if to_state == S_CONTEXT_RESOLVED:
        try:
            ctx = projection.build_context(TENANT_ID, wf["property_id"], corr)
        except projection.ProjectionError as e:
            # fail safe: mark recoverable, do not fabricate context
            await _apply_transition(db, wf, user, S_FAILED_RECOVERABLE,
                                    {"last_error": e.code}, None)
            wf2 = await db[COLLECTION].find_one({"id": wf["id"]})
            await write_audit(db, "STEWARD_CONTEXT_RESOLVED", user, wf2,
                              after_state=S_FAILED_RECOVERABLE, extra={"projection_error": e.code})
            raise HTTPException(status_code=e.status_code, detail=e.to_dict(corr))
        env = ctx.get("_projection", {})
        set_fields["context_projection_ref"] = env.get("fixture_or_seed_identifier") or "projection"
        set_fields["context_projection_version"] = env.get("contract_version")
        set_fields["context_provider_mode"] = env.get("provider_mode")
        set_fields["context_authoritative"] = env.get("authoritative")
        audit_event = "STEWARD_CONTEXT_RESOLVED"
    elif to_state == S_ANSWER_PRESENTED:
        set_fields["steward_response_ref"] = str(uuid.uuid4())
    elif to_state == S_ACTION_RECOMMENDED:
        set_fields["recommended_action"] = body.recommended_action or "Explore Roof Replacement"
    elif to_state == S_ACTION_CONFIRMED:
        set_fields["confirmation_event_id"] = str(uuid.uuid4())
        set_fields["confirmation_idempotency_key"] = body.idempotency_key
        audit_event = "HOMEOWNER_ACTION_CONFIRMED"
    elif to_state == S_PROJECT_CREATED:
        # idempotent project creation
        if wf.get("design_project_ref"):
            set_fields["design_project_ref"] = wf["design_project_ref"]
        else:
            sid = str(uuid.uuid4())
            if db is not None:
                await db.design_scenarios.insert_one({
                    "id": sid, "property_id": wf["property_id"], "owner_id": user["id"],
                    "name": "Project: Roof Replacement (Workflow)", "is_project": True,
                    "is_preset": False, "version": 1, "created_at": now_iso(),
                    "workflow_id": wf["id"], "selections": [], "linked_quotes": [],
                })
            set_fields["design_project_ref"] = sid
        audit_event = "DESIGN_PROJECT_CREATED"
    elif to_state == S_ESTIMATE_CREATED:
        material = body.material or pricebook.default_roof_material()
        est = pricebook.planning_estimate(material, basis="local")
        set_fields["estimate_snapshot"] = {
            "material": est["material"], "range": est["range"],
            "range_display": est["range_display"], "price_book_version": est["provenance"]["price_book_version"],
            "provenance": est["provenance"], "snapshot_at": now_iso(),
        }
        audit_event = "ESTIMATE_SNAPSHOT_CREATED"
    elif to_state == S_SCENARIOS_REVIEWED:
        set_fields["investment_scenario_ref"] = body.investment_scenario_ref or str(uuid.uuid4())
    elif to_state == S_READINESS_REVIEWED:
        assessment = readiness_policy.assess(wf.get("acknowledged_blockers"))
        set_fields["readiness_assessment"] = assessment
        set_fields["readiness_ref"] = str(uuid.uuid4())
        audit_event = "READINESS_ASSESSED"
        if assessment["unresolved_hard_blocker_ids"]:
            audit_extra = {"unresolved_hard_blockers": assessment["unresolved_hard_blocker_ids"]}
    elif to_state == S_PACKAGE_PREVIEWED:
        set_fields["contractor_package_version"] = f"cp-{uuid.uuid4().hex[:12]}"
        set_fields["redaction_settings"] = body.redaction_settings or {"remove_personal_info": True}
        audit_event = "CONTRACTOR_PACKAGE_PREVIEWED"
    elif to_state == S_PUBLICATION_APPROVED:
        set_fields["publication_approval"] = {
            "approved": True, "at": now_iso(), "actor": user.get("email")}
        audit_event = "PUBLICATION_APPROVED"
    elif to_state in (S_CANCELLED, S_FAILED_RECOVERABLE, S_FAILED_FINAL):
        pass  # handled generically

    updated = await _apply_transition(db, wf, user, to_state, set_fields, body.idempotency_key)
    await write_audit(db, audit_event, user, updated, before_state=wf["current_state"],
                      after_state=to_state, extra=audit_extra)
    if to_state == S_READINESS_REVIEWED and updated.get("readiness_assessment", {}).get("unresolved_hard_blocker_ids"):
        await write_audit(db, "HARD_BLOCKER_DETECTED", user, updated, after_state=to_state,
                          extra={"ids": updated["readiness_assessment"]["unresolved_hard_blocker_ids"]})
    return _public(updated)


@workflow_router.post("/{wf_id}/acknowledge")
async def acknowledge_blocker(wf_id: str, body: AckReq,
                              user: dict = Depends(get_steward_user), db=Depends(get_db)):
    _require_homeowner(user)
    wf = await _load(db, wf_id, user)
    if wf["current_state"] in TERMINAL_STATES:
        raise HTTPException(status_code=409, detail={"error_code": "TERMINAL_STATE",
                            "message": f"Workflow is terminal ({wf['current_state']})."})
    if not readiness_policy.is_known_item(body.item_id):
        raise HTTPException(status_code=400, detail={"error_code": "UNKNOWN_READINESS_ITEM",
                            "message": f"Unknown readiness item {body.item_id}."})
    if body.item_id not in readiness_policy.conditional_item_ids():
        raise HTTPException(status_code=400, detail={"error_code": "NOT_ACKNOWLEDGEABLE",
                            "message": f"{body.item_id} is not a conditional blocker."})
    if body.expected_version is not None and body.expected_version != wf["version"]:
        raise HTTPException(status_code=409, detail={"error_code": "STALE_VERSION",
                            "message": f"expected_version {body.expected_version} != current {wf['version']}."})

    acks = set(wf.get("acknowledged_blockers") or [])
    acks.add(body.item_id)
    new_assessment = readiness_policy.assess(acks)
    res = await db[COLLECTION].update_one(
        {"id": wf["id"], "version": wf["version"]},
        {"$set": {"acknowledged_blockers": sorted(acks), "readiness_assessment": new_assessment,
                  "updated_at": now_iso()}, "$inc": {"version": 1}})
    if res.modified_count != 1:
        raise HTTPException(status_code=409, detail={"error_code": "STALE_VERSION",
                            "message": "Workflow changed concurrently."})
    updated = await db[COLLECTION].find_one({"id": wf["id"]})
    await write_audit(db, "CONDITIONAL_BLOCKER_ACKNOWLEDGED", user, updated,
                      after_state=updated["current_state"], extra={"item_id": body.item_id})
    return _public(updated)


def _build_opportunity(wf: dict, user: dict):
    redact = (wf.get("redaction_settings") or {}).get("remove_personal_info", True)
    opp_id = str(uuid.uuid4())
    opp = {
        "id": opp_id,
        "owner_id": user["id"],
        "owner_name": "Alex M." if redact else user.get("name"),
        "property_id": wf["property_id"],
        "property_name": "Villa Horizon",
        "title": "Published: Roof Replacement",
        "category": "Roofing",
        "project_type": "renovation",
        "description": "Homeowner-approved roof replacement opportunity (workflow-governed).",
        "seriousness": "high",
        "status": "open",
        "is_opportunity": True,
        "created_at": now_iso(),
        "contractor_responses": [],
        "routed_to": [],
        "workflow_id": wf["id"],
        "estimate_snapshot": wf.get("estimate_snapshot"),
        "personal_info_redacted": redact,
    }
    return opp_id, opp


@workflow_router.post("/{wf_id}/publish")
async def publish_workflow(wf_id: str, body: PublishReq,
                           user: dict = Depends(get_steward_user), db=Depends(get_db)):
    _require_homeowner(user)
    wf = await _load(db, wf_id, user)
    corr = wf.get("correlation_id")

    # idempotent publication replay
    if body.idempotency_key and wf.get("publication_idempotency_key") == body.idempotency_key \
            and wf.get("opportunity_ref"):
        return {"status": "published", "idempotent_replay": True,
                "opportunity_id": wf["opportunity_ref"], "workflow": _public(wf)}
    if wf["current_state"] == S_OPPORTUNITY_PUBLISHED and wf.get("opportunity_ref"):
        return {"status": "published", "idempotent_replay": True,
                "opportunity_id": wf["opportunity_ref"], "workflow": _public(wf)}
    if wf["current_state"] in TERMINAL_STATES:
        raise HTTPException(status_code=409, detail={"error_code": "TERMINAL_STATE",
                            "message": f"Workflow is terminal ({wf['current_state']})."})

    # server-authoritative readiness recomputation (client cannot bypass)
    readiness = readiness_policy.assess(wf.get("acknowledged_blockers"))
    ok, blocking, reasons, remediation = evaluate_publication_gate(
        wf, approval=body.approval, property_id=body.property_id, readiness=readiness)

    if not ok:
        await write_audit(db, "PUBLICATION_BLOCKED", user, wf, correlation_id=corr,
                          before_state=wf["current_state"],
                          extra={"blocking_item_ids": blocking, "reasons": reasons})
        raise HTTPException(status_code=409, detail={
            "error_code": "PUBLICATION_BLOCKED",
            "blocking_item_ids": blocking,
            "reason": "; ".join(reasons),
            "remediation_actions": remediation,
            "correlation_id": corr,
        })

    if body.expected_version is not None and body.expected_version != wf["version"]:
        raise HTTPException(status_code=409, detail={"error_code": "STALE_VERSION",
                            "message": f"expected_version {body.expected_version} != current {wf['version']}.",
                            "correlation_id": corr})

    opp_id, opp = _build_opportunity(wf, user)

    # atomic single-publish claim (prevents concurrent double publish)
    claim = await db[COLLECTION].update_one(
        {"id": wf["id"], "version": wf["version"], "opportunity_ref": None,
         "current_state": {"$in": [S_PACKAGE_PREVIEWED, S_PUBLICATION_APPROVED]}},
        {"$set": {"current_state": S_OPPORTUNITY_PUBLISHED, "opportunity_ref": opp_id,
                  "publication_idempotency_key": body.idempotency_key,
                  "publication_approval": {"approved": True, "at": now_iso(), "actor": user.get("email")},
                  "updated_at": now_iso()},
         "$inc": {"version": 1},
         "$push": {"state_history": {"state": S_OPPORTUNITY_PUBLISHED, "at": now_iso()}}})
    if claim.modified_count != 1:
        current = await db[COLLECTION].find_one({"id": wf["id"]})
        if current and current.get("opportunity_ref"):
            return {"status": "published", "idempotent_replay": True,
                    "opportunity_id": current["opportunity_ref"], "workflow": _public(current)}
        raise HTTPException(status_code=409, detail={"error_code": "STALE_VERSION",
                            "message": "Publication lost the concurrency race; reload and retry.",
                            "correlation_id": corr})

    # persist audit + opportunity; if this fails, compensate (do not leave a published opp)
    try:
        published = await db[COLLECTION].find_one({"id": wf["id"]})
        await write_audit(db, "PROJECT_OPPORTUNITY_PUBLISHED", user, published, correlation_id=corr,
                          before_state=wf["current_state"], after_state=S_OPPORTUNITY_PUBLISHED,
                          entity_refs={"opportunity_id": opp_id, "design_project_ref": wf.get("design_project_ref")})
        await db.quotes.insert_one(opp)
    except Exception as e:
        # compensating rollback -> recoverable, opportunity not finalized
        await db[COLLECTION].update_one(
            {"id": wf["id"]},
            {"$set": {"current_state": S_FAILED_RECOVERABLE, "opportunity_ref": None,
                      "updated_at": now_iso()}, "$inc": {"version": 1}})
        logger.error("publish persistence failed, compensated: %s", e)
        raise HTTPException(status_code=500, detail={"error_code": "PUBLISH_PERSIST_FAILED",
                            "message": "Publication reverted; audit/opportunity persistence failed.",
                            "correlation_id": corr})

    final = await db[COLLECTION].find_one({"id": wf["id"]})
    return {"status": "published", "opportunity_id": opp_id, "correlation_id": corr,
            "workflow": _public(final)}


@workflow_router.post("/{wf_id}/cancel")
async def cancel_workflow(wf_id: str, body: CancelReq,
                          user: dict = Depends(get_steward_user), db=Depends(get_db)):
    _require_homeowner(user)
    wf = await _load(db, wf_id, user)
    if wf["current_state"] in TERMINAL_STATES:
        raise HTTPException(status_code=409, detail={"error_code": "TERMINAL_STATE",
                            "message": f"Workflow is already terminal ({wf['current_state']})."})
    if body.expected_version is not None and body.expected_version != wf["version"]:
        raise HTTPException(status_code=409, detail={"error_code": "STALE_VERSION",
                            "message": f"expected_version {body.expected_version} != current {wf['version']}."})
    res = await db[COLLECTION].update_one(
        {"id": wf["id"], "version": wf["version"]},
        {"$set": {"current_state": S_CANCELLED, "cancelled": True,
                  "cancel_reason": body.reason, "updated_at": now_iso()},
         "$inc": {"version": 1},
         "$push": {"state_history": {"state": S_CANCELLED, "at": now_iso()}}})
    if res.modified_count != 1:
        raise HTTPException(status_code=409, detail={"error_code": "STALE_VERSION",
                            "message": "Workflow changed concurrently."})
    updated = await db[COLLECTION].find_one({"id": wf["id"]})
    await write_audit(db, "WORKFLOW_CANCELLED", user, updated, before_state=wf["current_state"],
                      after_state=S_CANCELLED, extra={"reason": body.reason})
    return _public(updated)
