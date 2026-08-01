"""
Habitat Field-Test Projection Consumer

Shapes Passport projections for:
- Rotatable 3D digital twin (exterior)
- AWE anomaly overlays
- Homeowner-safe scores and maintenance priorities

Habitat remains strictly read-only for canonical property truth.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from passport_projection import (
        PassportProjectionAdapter,
        ProjectionUnavailable,
    )
except ImportError:
    PassportProjectionAdapter = None
    ProjectionUnavailable = Exception


def extract_digital_twin_summary(projection: Dict[str, Any]) -> Dict[str, Any]:
    geometry = projection.get("approved_roof_geometry") or projection.get("geometry") or {}
    awe = projection.get("awe_findings") or projection.get("findings") or []
    scores = projection.get("scores") or {}

    planes = geometry.get("planes", []) if isinstance(geometry, dict) else []
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
        "planes": visible_planes,
        "measurements": geometry.get("measurements", {}) if isinstance(geometry, dict) else {},
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


def extract_homeowner_dashboard(projection: Dict[str, Any]) -> Dict[str, Any]:
    """Shape data for the Habitat homeowner dashboard (matches product mockups)."""
    twin = extract_digital_twin_summary(projection)
    scores = twin.get("scores") or {}
    anomalies = twin.get("anomalies") or []

    priority = sorted(
        anomalies,
        key=lambda a: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(a.get("severity"), 9),
    )

    return {
        "property_summary": projection.get("property_identity") or projection.get("property_summary") or {},
        "awe_index": scores.get("awe_index") or scores.get("awe"),
        "roof_condition": scores.get("roof_condition") or scores.get("roof"),
        "energy_score": scores.get("energy_score") or scores.get("energy"),
        "moisture_score": scores.get("moisture_score") or scores.get("moisture"),
        "property_score": scores.get("property_score") or scores.get("property"),
        "digital_twin": {
            "available": twin["twin_available"],
            "plane_count": twin["plane_count"],
            "measurements": twin["measurements"],
        },
        "anomaly_counts": twin["anomaly_counts"],
        "maintenance_priority": priority[:10],
        "next_actions": [
            a for a in priority if a.get("severity") in ("CRITICAL", "HIGH")
        ][:5],
        "authority": {
            "source": "passport_projection",
            "habitat_role": "read-only",
            "truth_policy": twin["truth_policy"],
        },
    }


def get_homeowner_view(
    tenant_id: str,
    property_id: str,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    if PassportProjectionAdapter is None:
        return {
            "status": "ADAPTER_UNAVAILABLE",
            "message": "PassportProjectionAdapter not importable in this environment",
            "property_id": property_id,
        }

    adapter = PassportProjectionAdapter()
    try:
        # Support both get_context and common adapter method names
        if hasattr(adapter, "get_context"):
            ctx = adapter.get_context(tenant_id, property_id, correlation_id)
        elif hasattr(adapter, "fetch"):
            ctx = adapter.fetch(tenant_id, property_id)
        else:
            return {
                "status": "ADAPTER_METHOD_MISSING",
                "message": "No known fetch method on PassportProjectionAdapter",
                "property_id": property_id,
            }

        dashboard = extract_homeowner_dashboard(ctx if isinstance(ctx, dict) else {})
        return {
            "status": "OK",
            "property_id": property_id,
            "dashboard": dashboard,
            "digital_twin": extract_digital_twin_summary(ctx if isinstance(ctx, dict) else {}),
        }
    except ProjectionUnavailable as e:
        return {
            "status": "PROJECTION_UNAVAILABLE",
            "message": str(e),
            "property_id": property_id,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
            "property_id": property_id,
        }
