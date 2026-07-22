"""Immutable Reality Studio audit events (Phase 12). Reuses db.audit_events.

Safe references + correlation IDs only. Never logs binary data, raw imagery,
secrets, tokens, signed URLs, full artifact payloads, or unnecessary PII.
"""
import uuid
from datetime import datetime, timezone

from . import enums

_PROHIBITED = {"data", "bytes", "payload", "image", "token", "access_token", "signed_url",
               "password", "password_hash", "authorization", "secret"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize(extra: dict) -> dict:
    if not extra:
        return {}
    return {k: v for k, v in extra.items() if k.lower() not in _PROHIBITED}


async def write_event(db, event_type: str, user: dict, *, property_id: str = None,
                      correlation_id: str = None, entity_refs: dict = None,
                      before_state: str = None, after_state: str = None, extra: dict = None):
    if db is None:
        return None
    doc = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "domain": "reality",
        "tenant_id": enums.TENANT_ID,
        "property_id": property_id,
        "actor": {"user_id": user.get("id"), "email": user.get("email"), "role": user.get("role")},
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "timestamp": _now_iso(),
        "entity_references": _sanitize(entity_refs or {}),
        "before_state": before_state,
        "after_state": after_state,
    }
    san = _sanitize(extra or {})
    if san:
        doc["details"] = san
    await db.audit_events.insert_one(doc)
    return doc["id"]
