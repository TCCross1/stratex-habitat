"""
Habitat Field-Test Projection Consumer Helper

Ensures Habitat can cleanly consume the projections that Core produces
after a sealed Mission Package is published to Passport.

Habitat remains strictly read-only for canonical property truth.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Re-use the existing adapter
try:
    from passport_projection import (
        PassportProjectionAdapter,
        ProjectionUnavailable,
        TRUTH_CLASSES,
        build_context,
    )
except ImportError:
    PassportProjectionAdapter = None
    ProjectionUnavailable = Exception
    TRUTH_CLASSES = ["VERIFIED", "ESTIMATED", "PROJECTED", "UNKNOWN", "WITHHELD"]
    build_context = None


def extract_digital_twin_summary(projection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull the data Habitat needs to render the rotatable 3D twin
    and anomaly overlays from a Passport projection.
    """
    geometry = projection.get("approved_roof_geometry") or projection.get("geometry") or {}
    awe = projection.get("awe_findings") or projection.get("findings") or []
    scores = projection.get("scores") or {}

    planes = geometry.get("planes", []) if isinstance(geometry, dict) else []
    # Never surface WITHHELD geometry to the homeowner view
    visible_planes = [
        p for p in planes
        if p.get("truth_classification") not in ("WITHHELD",)
    ]

    anomalies = []
    for f in awe:
        if isinstance(f, dict):
            anomalies.append({
                "id": f.get("id"),
                "severity": f.get("severity", "LOW"),
                "description": f.get("description"),
                "location": f.get("location"),
                "truth": f.get("truth_classification", "UNKNOWN"),
                "category": f.get("category"),
            })

    return {
        "twin_available": len(visible_planes) > 0,
        "plane_count": len(visible_planes),
        "anomalies": anomalies,
        "anomaly_counts": {
            "critical": sum(1 for a in anomalies if a["severity"] == "CRITICAL"),
            "high": sum(1 for a in anomalies if a["severity"] == "HIGH"),
            "medium": sum(1 for a in anomalies if a["severity"] == "MEDIUM"),
            "low": sum(1 for a in anomalies if a["severity"] == "LOW"),
        },
        "scores": scores,
        "truth_policy": "WITHHELD geometry is never shown. All findings carry truth classification.",
        "source": "passport_projection",
        "habitat_role": "read-only",
    }


def get_homeowner_view(
    tenant_id: str,
    property_id: str,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    High-level helper for Habitat UI: fetch projection and shape it
    for the 3D twin + AWE anomaly experience.
    """
    if PassportProjectionAdapter is None:
        return {
            "status": "ADAPTER_UNAVAILABLE",
            "message": "PassportProjectionAdapter not importable in this environment",
        }

    adapter = PassportProjectionAdapter()
    try:
        ctx = adapter.get_context(tenant_id, property_id, correlation_id)
        twin = extract_digital_twin_summary(ctx)
        return {
            "status": "OK",
            "property_id": property_id,
            "digital_twin": twin,
            "projection_envelope": ctx.get("_projection"),
        }
    except ProjectionUnavailable as e:
        return {
            "status": "PROJECTION_UNAVAILABLE",
            "message": str(e),
            "property_id": property_id,
        }
