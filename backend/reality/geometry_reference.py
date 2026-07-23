"""Governed geometry_reference contract (H-014A.2).

Spatial entities may only store application-governed references:

* ``artifact:<artifact_id>`` — same-tenant, same-property artifact manifest id
* ``fixture:<safe_id>`` — deterministic fixture-only form; allowed solely when
  fixture governance permits (development / demo / test). Rejected in production.

Raw object-storage keys, URLs, signed URLs, paths, credentials, tokens, query
strings, fragments, traversal, encodings, and whitespace are never accepted and
never returned through spatial APIs.
"""
from __future__ import annotations

import re

import fixture_provider as fx

from . import enums
from .authz import structured

# Structured application references — not general-purpose URIs.
_ARTIFACT_RE = re.compile(r"^artifact:([A-Za-z0-9._-]+)$")
_FIXTURE_RE = re.compile(r"^fixture:([A-Za-z0-9._-]+)$")
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")

GOVERNED_GEOMETRY_TOKEN = "<governed-geometry-reference>"


def fixture_geometry_reference(entity_id: str) -> str:
    """Build a fixture-only geometry reference for deterministic reference-room entities."""
    if not isinstance(entity_id, str) or not _SAFE_ID_RE.match(entity_id):
        raise structured(422, "INVALID_GEOMETRY_REFERENCE",
                         "fixture geometry id must be a safe identifier.")
    return f"fixture:{entity_id}"


def public_geometry_reference(value):
    """Response-side redaction: only structured governed forms may leave the API."""
    if value is None:
        return None
    if not isinstance(value, str):
        return GOVERNED_GEOMETRY_TOKEN
    if _ARTIFACT_RE.match(value) or _FIXTURE_RE.match(value):
        return value
    return GOVERNED_GEOMETRY_TOKEN


def _reject(message: str = "geometry_reference must be a governed artifact: or fixture: reference."):
    raise structured(422, "INVALID_GEOMETRY_REFERENCE", message)


def validate_geometry_reference_format(value) -> tuple[str, str] | None:
    """Validate syntactic form. Returns (kind, id) or None when omitted.

    Omitted / explicit null is allowed. Any other non-matching value is rejected.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        _reject()
    if value == "" or value != value.strip() or any(ch.isspace() for ch in value):
        _reject("geometry_reference must be non-empty and contain no whitespace.")
    # Reject URL / path / encoding / credential-shaped constructs before parsing.
    lowered = value.lower()
    if ("://" in value or value.startswith("/") or value.startswith("\\")
            or "?" in value or "#" in value or "\\" in value or "%" in value
            or ".." in value or any(ord(ch) < 0x20 for ch in value)
            or "bearer " in lowered or "token=" in lowered or lowered.startswith("eyj")):
        _reject("geometry_reference must not contain URLs, paths, encodings, or secrets.")

    m = _ARTIFACT_RE.match(value)
    if m:
        return ("artifact", m.group(1))
    m = _FIXTURE_RE.match(value)
    if m:
        return ("fixture", m.group(1))
    _reject()


async def resolve_geometry_reference(db, value, *, tenant_id: str, property_id: str):
    """Validate and authorize a geometry_reference for persistence.

    Returns the canonical stored string, or None when omitted.
    """
    parsed = validate_geometry_reference_format(value)
    if parsed is None:
        return None
    kind, ref_id = parsed
    if kind == "fixture":
        if not fx.fixtures_enabled():
            raise structured(
                403, "FIXTURES_DISABLED",
                "Fixture geometry references are disabled in this environment.")
        return f"fixture:{ref_id}"

    # artifact: — must resolve to a same-tenant, same-property governed manifest.
    if db is None:
        _reject("geometry_reference artifact could not be authorized.")
    art = await db[enums.C_ARTIFACTS].find_one({"id": ref_id}, {"_id": 0})
    if not art:
        raise structured(422, "GEOMETRY_ARTIFACT_NOT_FOUND",
                         "geometry_reference artifact does not exist for this property.")
    if art.get("tenant_id") != tenant_id:
        raise structured(422, "CROSS_TENANT_GEOMETRY_REFERENCE",
                         "geometry_reference artifact belongs to a different tenant.")
    if art.get("property_id") != property_id:
        raise structured(422, "CROSS_PROPERTY_GEOMETRY_REFERENCE",
                         "geometry_reference artifact belongs to a different property.")
    return f"artifact:{ref_id}"


def public_spatial_entity(entity: dict) -> dict:
    """Return a copy safe for API responses (no raw storage keys via geometry_reference)."""
    if not entity:
        return entity
    out = dict(entity)
    out.pop("_id", None)
    out["geometry_reference"] = public_geometry_reference(out.get("geometry_reference"))
    return out
