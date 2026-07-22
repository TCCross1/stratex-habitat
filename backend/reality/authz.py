"""Authorization, tenant isolation, and truth-promotion guards (Phase 4/15)."""
from fastapi import HTTPException

from . import enums

# The deterministic reference room owns a dedicated synthetic property, authorized
# to the demo homeowner + privileged roles only.
REF_PROPERTY_ID = "ref-property-h014a"
REF_HOMEOWNER_EMAIL = "alex@stratexhabitat.com"


def structured(status: int, code: str, message: str, **extra):
    detail = {"error_code": code, "message": message}
    detail.update(extra)
    return HTTPException(status_code=status, detail=detail)


def server_tenant_id(_client_value=None) -> str:
    """Tenant is ALWAYS server-derived; any client-supplied tenant is ignored."""
    return enums.TENANT_ID


def not_found_nondisclosure():
    """Uniform 404 for BOTH 'does not exist' and 'exists but not authorized' on real
    (secret-existence) resources, so an actor cannot use the status code or message
    as an existence/ownership oracle. Identical error_code + message in every case.
    (The reference-room synthetic property id is public and intentionally keeps a
    403 access-denied contract.)"""
    return structured(404, "NOT_FOUND", "Resource not found or not accessible.")


async def authorize_property(db, user: dict, property_id: str) -> dict:
    """Enforce tenant + property authorization.

    Reference-room synthetic property (public id): 403 when not permitted.
    Real properties: a uniform 404 non-disclosure for BOTH nonexistent and
    existing-but-unauthorized, preventing existence/ownership enumeration.
    Authorization is never weakened — denial simply does not disclose existence.
    """
    role = user.get("role")
    # Reference-room synthetic property: demo homeowner + privileged roles only.
    if property_id == REF_PROPERTY_ID:
        if role in enums.PRIVILEGED_ROLES or user.get("email") == REF_HOMEOWNER_EMAIL:
            return {"id": REF_PROPERTY_ID, "owner_email": REF_HOMEOWNER_EMAIL, "reference": True}
        raise structured(403, "PROPERTY_ACCESS_DENIED", "Not authorized for this property.")

    prop = None
    if db is not None:
        prop = await db.properties.find_one({"id": property_id}, {"_id": 0})
    if not prop:
        raise not_found_nondisclosure()

    if role in enums.PRIVILEGED_ROLES:
        return prop
    # Contractors have no per-job grant model in H-014A, and non-owners are not
    # authorized; both are denied WITHOUT disclosing that the property exists.
    if role == "contractor":
        raise not_found_nondisclosure()
    if prop.get("owner_id") == user.get("id"):
        return prop
    raise not_found_nondisclosure()


def assert_truth_promotion_allowed(truth_classification: str, source_classification: str):
    """Habitat-only actors cannot promote records to restricted truth classes.

    H-014A has no Core/Passport/professional authorization channel, so any
    restricted promotion through these APIs fails closed with a structured error.
    """
    if truth_classification in enums.RESTRICTED_TRUTH_CLASSES:
        raise structured(
            403, "TRUTH_PROMOTION_FORBIDDEN",
            f"'{truth_classification}' requires an authorized Core/Passport/professional-review event.",
            restricted_class=truth_classification,
            allowed_habitat_classes=sorted(enums.HABITAT_EXISTING_CLASSES | enums.DESIGN_CLASSES),
        )


def validate_classifications(truth_classification: str, source_classification: str,
                             confidence: str, units: str):
    if truth_classification not in enums.TRUTH_CLASSES:
        raise structured(422, "INVALID_TRUTH_CLASS", f"Unknown truth_classification '{truth_classification}'.")
    if source_classification not in enums.SOURCE_CLASSES:
        raise structured(422, "INVALID_SOURCE_CLASS", f"Unknown source_classification '{source_classification}'.")
    if confidence not in enums.CONFIDENCE_LEVELS:
        raise structured(422, "INVALID_CONFIDENCE", f"Unknown confidence '{confidence}'.")
    if units not in enums.UNITS:
        raise structured(422, "INVALID_UNITS", f"Unsupported units '{units}' (expected METRIC_M).")
