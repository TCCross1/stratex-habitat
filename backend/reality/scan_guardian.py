"""AI Scan Quality Guardian (H-014B, Phase 4) — deterministic capture-quality checks.

Despite the "AI" name, the Guardian is INTENTIONALLY deterministic and
rule-based: given the same capture-quality report it always returns the same
verdict, findings, score and coverage state. This makes it reproducible,
auditable, and safe to run identically on-device (Swift mirror) and on the
backend. It never fabricates geometry and never promotes truth — it only
recommends (ACCEPT_CANDIDATE / REVIEW / RECAPTURE); the governed scan-session
state machine remains the sole authority for acceptance.
"""
from datetime import datetime, timezone

from . import enums
from .authz import structured
from .audit_service import write_event

# --- Fixed, versioned thresholds (PLANNING tolerance class) --------------
# Each check yields PASS / WARN / FAIL by comparing a measured value to these.
THRESHOLDS = {
    "wall_coverage":        {"pass": 0.85, "warn": 0.60},   # fraction of wall area observed
    "floor_coverage":       {"pass": 0.80, "warn": 0.50},
    "ceiling_coverage":     {"pass": 0.70, "warn": 0.40},   # ceilings are often partially occluded
    "tracking_mean":        {"pass": 0.80, "warn": 0.60},   # mean ARKit tracking quality (0..1)
    "tracking_limited_frac":{"pass": 0.10, "warn": 0.30, "lower_is_better": True},
    "drift_m":              {"pass": 0.05, "warn": 0.15, "lower_is_better": True},  # loop-closure drift
    "low_quality_frac":     {"pass": 0.15, "warn": 0.35, "lower_is_better": True},
    "area_ratio":           {"pass": 0.90, "warn": 0.70},   # captured / expected floor area
}
MIN_CAPTURED_AREA_M2 = 4.0
MIN_FRAME_COUNT = 120
WARN_FRAME_COUNT = 240
DEFAULT_EXPECTED_WALLS = 4
HEIGHT_RANGE_M = (2.0, 4.5)
PLAN_DIM_RANGE_M = (1.0, 40.0)

_SEVERITY_WEIGHT = {enums.GUARDIAN_WARN: 8, enums.GUARDIAN_FAIL: 25}


def _num(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _grade(measured, key):
    """Return PASS/WARN/FAIL for a measured value against a named threshold."""
    t = THRESHOLDS[key]
    lower_is_better = t.get("lower_is_better", False)
    if lower_is_better:
        if measured <= t["pass"]:
            return enums.GUARDIAN_PASS
        if measured <= t["warn"]:
            return enums.GUARDIAN_WARN
        return enums.GUARDIAN_FAIL
    if measured >= t["pass"]:
        return enums.GUARDIAN_PASS
    if measured >= t["warn"]:
        return enums.GUARDIAN_WARN
    return enums.GUARDIAN_FAIL


def _finding(code, severity, measured, threshold, message, area=None):
    f = {"code": code, "severity": severity, "measured": measured,
         "threshold": threshold, "message": message}
    if area is not None:
        f["area"] = area
    return f


def evaluate(report: dict) -> dict:
    """Pure, deterministic evaluation of a capture-quality report.

    Returns a fully-serialisable Guardian result (verdict, coverage_state,
    score, findings, missing_areas, recommendation). No DB, no I/O.
    """
    report = report or {}
    surf = report.get("surface_coverage") or {}
    tracking = report.get("tracking_quality") or {}
    dims = report.get("dimensions_m") or {}

    wall_cov = _num(surf.get("WALL"))
    floor_cov = _num(surf.get("FLOOR"))
    ceiling_cov = _num(surf.get("CEILING"))
    tmean = _num(tracking.get("mean"))
    tlimited = _num(tracking.get("limited_fraction"))
    drift = _num(report.get("drift_estimate_m"))
    frame_count = int(_num(report.get("frame_count"), 0))
    low_q = _num(report.get("low_quality_frame_fraction"))
    captured_area = _num(report.get("captured_area_m2"))
    expected_area = report.get("expected_area_m2")
    walls_detected = int(_num(report.get("wall_count_detected"), 0))
    walls_expected = int(_num(report.get("wall_count_expected"), DEFAULT_EXPECTED_WALLS)) or DEFAULT_EXPECTED_WALLS

    findings = []
    missing_areas = []

    # 1) Surface coverage
    for area_name, cov, key in (("wall", wall_cov, "wall_coverage"),
                                ("floor", floor_cov, "floor_coverage"),
                                ("ceiling", ceiling_cov, "ceiling_coverage")):
        sev = _grade(cov, key)
        if sev != enums.GUARDIAN_PASS:
            findings.append(_finding(
                f"{area_name.upper()}_COVERAGE_LOW", sev, round(cov, 3), THRESHOLDS[key]["pass"],
                f"{area_name.capitalize()} coverage {cov*100:.0f}% is below the "
                f"{THRESHOLDS[key]['pass']*100:.0f}% target.", area=area_name))
            missing_areas.append(f"{area_name} surfaces (partial coverage)")

    # 2) Missing walls
    if walls_detected < walls_expected:
        missing = walls_expected - walls_detected
        sev = enums.GUARDIAN_FAIL if missing >= 2 else enums.GUARDIAN_WARN
        findings.append(_finding(
            "MISSING_WALL", sev, walls_detected, walls_expected,
            f"{missing} of {walls_expected} expected walls were not captured.", area="wall"))
        missing_areas.append(f"{missing} uncaptured wall(s)")

    # 3) Tracking quality
    if _grade(tmean, "tracking_mean") != enums.GUARDIAN_PASS:
        sev = _grade(tmean, "tracking_mean")
        findings.append(_finding("TRACKING_DEGRADED", sev, round(tmean, 3),
                                 THRESHOLDS["tracking_mean"]["pass"],
                                 f"Mean tracking quality {tmean:.2f} indicates degraded tracking."))
    if _grade(tlimited, "tracking_limited_frac") != enums.GUARDIAN_PASS:
        sev = _grade(tlimited, "tracking_limited_frac")
        findings.append(_finding("TRACKING_LIMITED_FRACTION", sev, round(tlimited, 3),
                                 THRESHOLDS["tracking_limited_frac"]["pass"],
                                 f"Tracking was limited for {tlimited*100:.0f}% of the capture."))

    # 4) Drift (loop closure)
    if _grade(drift, "drift_m") != enums.GUARDIAN_PASS:
        sev = _grade(drift, "drift_m")
        findings.append(_finding("DRIFT_EXCEEDED", sev, round(drift, 4),
                                 THRESHOLDS["drift_m"]["pass"],
                                 f"Estimated drift {drift*100:.1f} cm exceeds the PLANNING tolerance."))

    # 5) Captured area (absolute + relative to expected)
    if captured_area < MIN_CAPTURED_AREA_M2:
        findings.append(_finding("INSUFFICIENT_AREA", enums.GUARDIAN_FAIL, round(captured_area, 2),
                                 MIN_CAPTURED_AREA_M2,
                                 f"Captured area {captured_area:.1f} m² is below the "
                                 f"{MIN_CAPTURED_AREA_M2:.0f} m² minimum for a valid room."))
    if expected_area not in (None, 0):
        ratio = captured_area / _num(expected_area, 1.0) if _num(expected_area) else 0.0
        if _grade(ratio, "area_ratio") != enums.GUARDIAN_PASS:
            sev = _grade(ratio, "area_ratio")
            findings.append(_finding("AREA_INCOMPLETE", sev, round(ratio, 3),
                                     THRESHOLDS["area_ratio"]["pass"],
                                     f"Captured {ratio*100:.0f}% of the expected floor area."))

    # 6) Frame quality
    if _grade(low_q, "low_quality_frac") != enums.GUARDIAN_PASS:
        sev = _grade(low_q, "low_quality_frac")
        findings.append(_finding("LOW_FRAME_QUALITY", sev, round(low_q, 3),
                                 THRESHOLDS["low_quality_frac"]["pass"],
                                 f"{low_q*100:.0f}% of frames were low quality."))
    if frame_count < MIN_FRAME_COUNT:
        findings.append(_finding("FRAME_COUNT_LOW", enums.GUARDIAN_FAIL, frame_count, MIN_FRAME_COUNT,
                                 f"Only {frame_count} frames captured (< {MIN_FRAME_COUNT})."))
    elif frame_count < WARN_FRAME_COUNT:
        findings.append(_finding("FRAME_COUNT_LOW", enums.GUARDIAN_WARN, frame_count, WARN_FRAME_COUNT,
                                 f"Frame count {frame_count} is below the recommended {WARN_FRAME_COUNT}."))

    # 7) Dimensional sanity
    h = _num(dims.get("height"))
    w = _num(dims.get("width"))
    length = _num(dims.get("length"))
    if h and not (HEIGHT_RANGE_M[0] <= h <= HEIGHT_RANGE_M[1]):
        findings.append(_finding("HEIGHT_OUT_OF_RANGE", enums.GUARDIAN_WARN, round(h, 2),
                                 list(HEIGHT_RANGE_M),
                                 f"Ceiling height {h:.2f} m is outside the plausible range."))
    for name, v in (("width", w), ("length", length)):
        if v and not (PLAN_DIM_RANGE_M[0] <= v <= PLAN_DIM_RANGE_M[1]):
            findings.append(_finding("DIMENSION_OUT_OF_RANGE", enums.GUARDIAN_WARN, round(v, 2),
                                     list(PLAN_DIM_RANGE_M),
                                     f"Room {name} {v:.2f} m is outside the plausible range."))

    # --- Aggregate ---
    has_fail = any(f["severity"] == enums.GUARDIAN_FAIL for f in findings)
    has_warn = any(f["severity"] == enums.GUARDIAN_WARN for f in findings)
    if has_fail:
        verdict = enums.GUARDIAN_FAIL
        coverage_state = enums.COVERAGE_INCOMPLETE
        recommendation = "RECAPTURE"
    elif has_warn:
        verdict = enums.GUARDIAN_WARN
        coverage_state = enums.COVERAGE_PARTIAL
        recommendation = "REVIEW"
    else:
        verdict = enums.GUARDIAN_PASS
        coverage_state = enums.COVERAGE_COMPLETE
        recommendation = "ACCEPT_CANDIDATE"

    score = 100
    for f in findings:
        score -= _SEVERITY_WEIGHT.get(f["severity"], 0)
    score = max(0, min(100, score))

    return {
        "guardian_version": enums.GUARDIAN_VERSION,
        "deterministic": True,
        "verdict": verdict,
        "coverage_state": coverage_state,
        "score": score,
        "findings": findings,
        "missing_areas": missing_areas,
        "recommendation": recommendation,
        "checks_run": 7,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


async def run_guardian(db, user, *, session_id, report: dict, correlation_id=None):
    """Evaluate a capture-quality report and persist the Guardian result onto the
    scan session (deterministic). Does NOT transition the session — acceptance is
    a separate governed action. Returns {scan_session, guardian_result}."""
    session = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise structured(404, "NOT_FOUND", "Resource not found or not accessible.")
    result = evaluate(report)
    corr = correlation_id or session.get("correlation_id")
    quality_summary = {
        "guardian_verdict": result["verdict"],
        "guardian_score": result["score"],
        "coverage_state": result["coverage_state"],
        "guardian_version": result["guardian_version"],
    }
    await db[enums.C_SCANS].update_one(
        {"id": session_id},
        {"$set": {"quality_summary": quality_summary,
                  "guardian_result": result,
                  "coverage_state": result["coverage_state"],
                  "missing_areas": result["missing_areas"],
                  "updated_at": result["evaluated_at"]}})
    await write_event(db, enums.A_GUARDIAN_EVALUATED, user, property_id=session.get("property_id"),
                      correlation_id=corr, entity_refs={"scan_session_id": session_id},
                      extra={"verdict": result["verdict"], "score": result["score"],
                             "coverage_state": result["coverage_state"],
                             "finding_count": len(result["findings"]),
                             "recommendation": result["recommendation"]})
    updated = await db[enums.C_SCANS].find_one({"id": session_id}, {"_id": 0})
    return {"scan_session": updated, "guardian_result": result}
