"""Hydrate Habitat dashboard + openings UI models from habitat.projection.v1 payload."""

from __future__ import annotations

from typing import Any, Dict, List

from habitat_ui.awe_twin import habitat_dashboard_projection_stub, awe_index_card
from habitat_ui.openings import OpeningKind, Elevation, TruthClass, opening_record


def openings_ui_from_contract(openings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for o in openings:
        kind_raw = (o.get("kind") or "window").lower()
        try:
            kind = OpeningKind(kind_raw)
        except ValueError:
            kind = OpeningKind.OTHER
        elev_raw = (o.get("elevation") or "unknown").lower()
        try:
            elev = Elevation(elev_raw)
        except ValueError:
            elev = Elevation.UNKNOWN
        truth_raw = (o.get("truth") or "ESTIMATED").upper()
        try:
            truth = TruthClass(truth_raw)
        except ValueError:
            truth = TruthClass.ESTIMATED
        rec = opening_record(
            kind=kind,
            label=o.get("label") or "Opening",
            elevation=elev,
            unit_width_in=float(o.get("unit_w_in") or 0),
            unit_height_in=float(o.get("unit_h_in") or 0),
            material=o.get("material") or "unknown",
            condition=o.get("condition") or "unknown",
            truth=truth,
        )
        # Prefer contract RO when provided
        if o.get("rough_w_in") and o.get("rough_h_in"):
            rec["rough_opening_in"] = {
                "width_in": float(o["rough_w_in"]),
                "height_in": float(o["rough_h_in"]),
            }
            rec["rough_opening_display"] = f'{o["rough_w_in"]}" × {o["rough_h_in"]}"'
        if o.get("id"):
            rec["id"] = o["id"]
        out.append(rec)
    return out


def dashboard_from_contract(projection: Dict[str, Any]) -> Dict[str, Any]:
    base = habitat_dashboard_projection_stub()
    ident = projection.get("property_identity") or {}
    scores = projection.get("scores") or {}
    health = projection.get("home_health") or {}
    awe = projection.get("awe") or {}
    maint = projection.get("maintenance") or {}
    twin = projection.get("twin") or {}

    if ident.get("address_line"):
        base["property"]["address_line"] = ident["address_line"]
    if ident.get("city_state_zip"):
        base["property"]["city_state_zip"] = ident["city_state_zip"]
    if scores.get("certified_score") is not None:
        base["property"]["certified_score"] = int(scores["certified_score"])
    if scores.get("score_scale"):
        base["property"]["score_scale"] = int(scores["score_scale"])

    if health.get("overall") is not None:
        base["home_health"]["overall"] = int(health["overall"])
    if health.get("systems"):
        base["home_health"]["systems"].update(
            {k: int(v) for k, v in health["systems"].items() if v is not None}
        )

    idx = awe.get("index") or scores.get("awe_index")
    if idx is not None:
        base["awe"] = awe_index_card(int(idx), base["awe"].get("label", "Good"))

    if maint.get("next_12_months_usd") is not None:
        base["predictive_maintenance"]["next_12_months_usd"] = int(maint["next_12_months_usd"])
    actions = maint.get("actions") or []
    if actions:
        base["predictive_maintenance"]["recommended_actions"] = len(actions)
        base["maintenance_priority"] = actions

    base["digital_twin"] = {
        "available": (twin.get("plane_count") or 0) > 0,
        "plane_count": twin.get("plane_count") or 0,
        "measurements": twin.get("measurements") or {},
        "withheld_plane_count": twin.get("withheld_plane_count") or 0,
    }
    base["awe_hotspots"] = awe.get("hotspots") or base.get("awe_hotspots") or []
    base["authoritative"] = bool(projection.get("authoritative"))
    base["passport_status"] = "OK" if projection.get("authoritative") else "PROJECTED"
    base["contract_id"] = projection.get("contract_id")
    base["property_id"] = projection.get("property_id")
    base["mission_id"] = projection.get("mission_id")
    return base
