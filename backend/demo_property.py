"""
Central Kentucky Habitat demonstration property constants and safe reconciliation.

Demo records ONLY. Never rewrite unmarked or production property records.
"""
from __future__ import annotations

from typing import Any

DEMO_PROPERTY_NAME = "Central Kentucky Demonstration Home"
DEMO_LOCATION = "Lexington, Kentucky"
DEMO_VISUALIZATION_PROFILE = "central-kentucky-demo-home"
DEMO_DATA_ORIGIN = "demo"
DEMO_TRUTH_STATUS = "sample_only"
DEMO_CONFIDENCE = "demo"
DEMO_PROPERTY_TYPE = "detached_single_family"
DEMO_TWIN_IMAGE = "/property-visualizations/habitat-central-kentucky-demo-home.webp"
DEMO_THUMB = "/property-visualizations/habitat-central-kentucky-demo-home-thumb.webp"

# Known legacy seed homeowner — used only with explicit allow_legacy_seed_email.
LEGACY_SEED_HOMEOWNER_EMAIL = "alex@stratexhabitat.com"
LEGACY_SEED_PROPERTY_NAMES = frozenset({"Villa Horizon", DEMO_PROPERTY_NAME})

REQUIRED_DEMO_MARKERS = (
    "is_demo_fixture",
    "visualization_data_origin",
    "visualization_truth_status",
)


def demo_property_fields() -> dict[str, Any]:
    return {
        "name": DEMO_PROPERTY_NAME,
        "location": DEMO_LOCATION,
        "habitat_display_name": DEMO_PROPERTY_NAME,
        "thumbnail": DEMO_THUMB,
        "twin_image": DEMO_TWIN_IMAGE,
        "visualization_data_origin": DEMO_DATA_ORIGIN,
        "visualization_truth_status": DEMO_TRUTH_STATUS,
        "visualization_profile": DEMO_VISUALIZATION_PROFILE,
        "confidence_state": DEMO_CONFIDENCE,
        "is_demo_fixture": True,
        "property_type": DEMO_PROPERTY_TYPE,
        # Illustrative sample characteristics — not captured facts
        "year_built": 2014,
        "sqft": 3100,
        "stories": 2,
        "sample_characteristics": {
            "approximate_sqft_range": "2,600–3,400",
            "bedrooms": 4,
            "bathrooms": "2.5–3",
            "garage": "attached two-car",
            "dataOrigin": DEMO_DATA_ORIGIN,
            "truthStatus": DEMO_TRUTH_STATUS,
        },
    }


def is_explicit_demo_record(doc: dict[str, Any] | None) -> bool:
    if not doc:
        return False
    if doc.get("is_demo_fixture") is True:
        return True
    if doc.get("visualization_data_origin") == DEMO_DATA_ORIGIN:
        return True
    if doc.get("visualization_truth_status") == DEMO_TRUTH_STATUS:
        return True
    if doc.get("data_origin") == DEMO_DATA_ORIGIN:
        return True
    if doc.get("truth_status") == DEMO_TRUTH_STATUS:
        return True
    return False


def finding_demo_fields() -> dict[str, Any]:
    return {
        "data_origin": DEMO_DATA_ORIGIN,
        "truth_status": DEMO_TRUTH_STATUS,
        "confidence_state": DEMO_CONFIDENCE,
        "presentation_label": "Example finding",
        "is_approved_finding": False,
        "is_lidar_detected": False,
        "passport_approved": False,
    }


def planned_property_patch() -> dict[str, Any]:
    fields = demo_property_fields()
    return {k: fields[k] for k in (
        "name", "location", "habitat_display_name", "thumbnail", "twin_image",
        "visualization_data_origin", "visualization_truth_status",
        "visualization_profile", "confidence_state", "is_demo_fixture",
        "property_type", "sample_characteristics",
    )}


def reconcile_demo_properties(
    properties: list[dict[str, Any]],
    *,
    dry_run: bool = True,
    allow_legacy_seed_email: str | None = None,
    owner_email_by_id: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Plan (and optionally apply in-memory) updates for demo-marked properties only.

    Unmarked records are refused. Legacy Villa Horizon seed records are refused
    unless allow_legacy_seed_email matches the known demo homeowner email AND the
    property name is in LEGACY_SEED_PROPERTY_NAMES.
    """
    owner_email_by_id = owner_email_by_id or {}
    patch = planned_property_patch()
    report = {
        "dry_run": dry_run,
        "updated": [],
        "refused": [],
        "unchanged": [],
        "applied": False,
    }

    for prop in properties:
        pid = prop.get("id")
        if is_explicit_demo_record(prop):
            intended = {k: v for k, v in patch.items() if prop.get(k) != v}
            if not intended:
                report["unchanged"].append({"id": pid, "reason": "already_reconciled"})
            else:
                entry = {"id": pid, "name": prop.get("name"), "intended_changes": intended}
                report["updated"].append(entry)
                if not dry_run:
                    prop.update(intended)
            continue

        # Legacy seed path — explicit opt-in only
        owner_email = owner_email_by_id.get(prop.get("owner_id") or "", "")
        legacy_ok = (
            allow_legacy_seed_email == LEGACY_SEED_HOMEOWNER_EMAIL
            and owner_email == LEGACY_SEED_HOMEOWNER_EMAIL
            and prop.get("name") in LEGACY_SEED_PROPERTY_NAMES
        )
        if legacy_ok:
            intended = {k: v for k, v in patch.items() if prop.get(k) != v}
            # Force demo markers onto legacy seed
            intended.update({
                "is_demo_fixture": True,
                "visualization_data_origin": DEMO_DATA_ORIGIN,
                "visualization_truth_status": DEMO_TRUTH_STATUS,
            })
            report["updated"].append({
                "id": pid,
                "name": prop.get("name"),
                "intended_changes": intended,
                "legacy_seed": True,
            })
            if not dry_run:
                prop.update(intended)
            continue

        report["refused"].append({
            "id": pid,
            "name": prop.get("name"),
            "reason": "missing_explicit_demo_marker",
        })

    report["applied"] = not dry_run and bool(report["updated"])
    return report


def neutralize_demo_finding_copy(finding: dict[str, Any]) -> dict[str, Any]:
    """Rewrite misleading detection language on demo findings only."""
    patch = {}
    title = (finding.get("title") or "").strip()
    desc = finding.get("description") or ""
    if title and not title.lower().startswith("example"):
        patch["title"] = f"Example: {title}"
    if (
        "detected" in desc.lower()
        or "STRATEX Core scan" in desc
        or "Heat loss" in desc
        or "Demo/sample only" not in desc
    ):
        patch["description"] = (
            "Demo/sample only. Not an approved property finding. "
            "Awaiting a verified property scan."
        )
    if finding.get("impact_energy") and (
        "Energy Loss" in str(finding.get("impact_energy")) or finding.get("impact_energy") != "Sample"
    ):
        if finding.get("impact_energy") not in ("Sample", "—"):
            patch["impact_energy"] = "Sample"
    if finding.get("impact_cost") and "$" in str(finding.get("impact_cost")):
        patch["impact_cost"] = "Sample"
    if (finding.get("price_high") or 0) > 0:
        patch["price_low"] = 0
        patch["price_high"] = 0
    patch["recommended_action"] = "Example review category"
    patch["action_detail"] = "Awaiting verified property scan."
    patch["presentation_label"] = "Example finding"
    return patch


def reconcile_demo_findings(
    findings: list[dict[str, Any]],
    demo_property_ids: set[str],
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Attach sample-only labels to findings that belong to demo properties."""
    base = finding_demo_fields()
    report = {"dry_run": dry_run, "updated": [], "refused": [], "applied": False}
    for f in findings:
        pid = f.get("property_id")
        if pid not in demo_property_ids:
            report["refused"].append({
                "id": f.get("id"),
                "property_id": pid,
                "reason": "property_not_in_demo_set",
            })
            continue
        intended = {k: v for k, v in base.items() if f.get(k) != v}
        intended.update({
            k: v for k, v in neutralize_demo_finding_copy(f).items()
            if f.get(k) != v
        })
        if intended:
            report["updated"].append({"id": f.get("id"), "intended_changes": intended})
            if not dry_run:
                f.update(intended)
    report["applied"] = not dry_run and bool(report["updated"])
    return report
