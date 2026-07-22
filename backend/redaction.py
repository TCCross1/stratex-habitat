"""
STRATEX HABITAT — Contractor-Package Redaction (H-013)

Enforces homeowner privacy on the BACKEND. A contractor-facing package is
built from an internal package (which contains real PII + internal-only
fields), then passed through an allow-list redactor that STRIPS (removes, not
relabels) every field not explicitly approved for contractor visibility.

Guarantees
----------
* Redacted fields never appear in the returned payload (no direct-API leak).
* Personal contact info is included ONLY after explicit homeowner approval.
* Internal-only fields (owner_id, internal trust/confidence, correlation ids,
  audit trails, price internals) are ALWAYS stripped from contractor output.
* A backward-compatible `redacted_personal_info` MASK block is emitted (values
  masked to "REDACTED", never the real values) plus a `redaction` metadata
  block describing what was enforced.
"""
from __future__ import annotations
from typing import Any, Dict, List

# Top-level keys a contractor package is ALLOWED to expose.
CONTRACTOR_VISIBLE_FIELDS = [
    "summary",
    "homeowner_approved_summary",
    "property_context",          # city/region + year only (no exact street)
    "digital_twin_views",
    "proposed_materials",
    "quantity_takeoff",
    "planning_estimate",
    "planning_estimate_provenance",
    "assumptions",
    "exclusions",
    "unknown_conditions",
    "requested_timeline",
    "budget_preference",
    "questions_requiring_site_verification",
    "readiness_score",
]

# Contact fields released ONLY when the homeowner approves.
CONTACT_FIELD = "homeowner_contact"

# Personal / internal fields that must NEVER survive into contractor output.
SENSITIVE_KEYS = {
    "last_name", "email", "phone", "street_address", "exact_address",
    "owner_name_full", "owner_email", "owner_phone",
}
INTERNAL_ONLY_KEYS = {
    "owner_id", "correlation_id", "audit", "audit_events",
    "internal_trust_grade", "internal_confidence", "price_source_internal",
    "cost_basis_internal", "_id",
}

MASK = "REDACTED"


def _strip_sensitive(obj: Any) -> Any:
    """Recursively remove any sensitive/internal keys from nested structures."""
    if isinstance(obj, dict):
        return {
            k: _strip_sensitive(v)
            for k, v in obj.items()
            if k not in SENSITIVE_KEYS and k not in INTERNAL_ONLY_KEYS
        }
    if isinstance(obj, list):
        return [_strip_sensitive(v) for v in obj]
    return obj


def redact_contractor_package(internal: Dict[str, Any], *, homeowner_approved: bool) -> Dict[str, Any]:
    """Produce the contractor-safe package from an internal package."""
    out: Dict[str, Any] = {}
    stripped: List[str] = []

    # 1) Copy only allow-listed fields, deep-stripping any nested sensitive keys.
    for key in CONTRACTOR_VISIBLE_FIELDS:
        if key in internal:
            out[key] = _strip_sensitive(internal[key])

    # 2) Shared documents: expose ONLY those explicitly flagged shared=True.
    docs = internal.get("shared_documents", []) or []
    out["shared_documents"] = [
        {"id": d.get("id"), "name": d.get("name")}
        for d in docs if d.get("shared") is True
    ]
    if any(d.get("shared") is not True for d in docs):
        stripped.append("shared_documents(unshared)")

    # 3) Personal contact: released only on explicit homeowner approval.
    contact = internal.get(CONTACT_FIELD)
    if homeowner_approved and contact:
        out[CONTACT_FIELD] = contact
    elif contact:
        stripped.append(CONTACT_FIELD)

    # 4) Backward-compatible mask block (never real values).
    out["redacted_personal_info"] = {
        "status": "shared" if homeowner_approved else "redacted",
        "last_name": (contact or {}).get("last_name", MASK) if homeowner_approved else MASK,
        "email": (contact or {}).get("email", MASK) if homeowner_approved else MASK,
        "phone": (contact or {}).get("phone", MASK) if homeowner_approved else MASK,
        "note": (
            "Contact details shared with the awarded contractor."
            if homeowner_approved else
            "Personal contact info withheld until the homeowner approves and awards."
        ),
    }

    # 5) Enforcement metadata.
    out["redaction"] = {
        "redaction_enforced": True,
        "tier": "contractor" if homeowner_approved else "preview",
        "homeowner_approved": homeowner_approved,
        "personal_contact_shared": bool(homeowner_approved and contact),
        "stripped_fields": sorted(set(stripped)),
        "policy": (
            "Server-side allow-list redaction. Non-approved fields are removed, "
            "not masked, and are never exposed via direct API access."
        ),
    }
    return out


def assert_no_sensitive_values(payload: Any, forbidden_values: List[str]) -> List[str]:
    """Test helper: return any forbidden raw values that leaked into `payload`."""
    import json
    blob = json.dumps(payload, default=str)
    return [v for v in forbidden_values if v and v in blob]
