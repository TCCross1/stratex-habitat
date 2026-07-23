/**
 * Deterministic visualization selection priority (EXISTING geometry only).
 *
 * 1. current authorized approved Passport projection
 * 2. current draft candidate (explicitly draft)
 * 3. explicit Central Kentucky demonstration configuration
 * 4. awaiting-scan
 * 5. unavailable/error
 */

import { canDisplayAsApproved, isDraftLifecycle } from "./realityModelContract";
import { normalizeRealityModel } from "./normalizeRealityModel";
import { CENTRAL_KENTUCKY_DEMO_HOME } from "../centralKentuckyDemoHome";

/**
 * @param {object} options
 * @param {object|null} [options.approvedProjection]
 * @param {object|null} [options.draftCandidate]
 * @param {object|null} [options.demoConfig]
 * @param {boolean} [options.realPropertyRequestFailed]
 * @param {boolean} [options.isDemoProperty]
 * @param {string} [options.propertyId]
 */
export function selectRealityVisualizationSource({
  approvedProjection = null,
  draftCandidate = null,
  demoConfig = null,
  realPropertyRequestFailed = false,
  isDemoProperty = false,
  propertyId = null,
} = {}) {
  // Network failure on a REAL property must never silently become demo
  if (realPropertyRequestFailed && !isDemoProperty) {
    return {
      selected: "unavailable",
      reason: "real_property_request_failed_no_demo_fallback",
      model: normalizeRealityModel({
        property_id: propertyId || "unknown",
        lifecycle_state: "unavailable",
        truth_status: "unknown",
        data_origin: "unknown",
        display_disclaimer: "Property model temporarily unavailable.",
      }).model,
    };
  }

  if (approvedProjection) {
    const n = normalizeRealityModel(approvedProjection);
    if (n.status !== "REJECTED" && n.model && canDisplayAsApproved(n.model)) {
      // Prefer newer approved over older if versions provided by caller as array — single handled here
      return { selected: "approved_projection", reason: "authorized_approved_beats_all", model: n.model, normalization: n };
    }
  }

  if (draftCandidate) {
    const n = normalizeRealityModel(draftCandidate);
    if (n.status !== "REJECTED" && n.model && isDraftLifecycle(n.model.lifecycle_state)) {
      return { selected: "draft_candidate", reason: "draft_explicit_not_approved", model: n.model, normalization: n };
    }
  }

  if (isDemoProperty || demoConfig) {
    const demo = demoConfig || CENTRAL_KENTUCKY_DEMO_HOME;
    const payload = {
      property_id: demo.propertyId || propertyId || CENTRAL_KENTUCKY_DEMO_HOME.propertyId,
      lifecycle_state: "demo_sample",
      truth_status: "sample_only",
      data_origin: "demo",
      confidence_state: "demo",
      model_version: "demo-exterior-v1",
      schema_version: "h014c1.reality.v1",
      floor_plan_available: false,
      three_d_model_available: false,
      dimensions_available: false,
      openings_available: false,
      thumbnail_ref: demo.thumbAsset || demo.exteriorAsset,
      preview_ref: demo.exteriorAsset,
      display_disclaimer:
        "The Central Kentucky Demonstration Home is demonstration/sample-only data. It is not a physically validated property scan or approved Passport model.",
      unknown_fields: ["walls", "openings", "dimensions", "model_3d_ref"],
      missing_elements: ["approved_floor_plan", "approved_3d_model"],
    };
    const n = normalizeRealityModel(payload);
    return { selected: "demo_sample", reason: "explicit_demo_configuration", model: n.model, normalization: n };
  }

  if (propertyId) {
    const n = normalizeRealityModel({
      property_id: propertyId,
      lifecycle_state: "awaiting_scan",
      truth_status: "unknown",
      data_origin: "unknown",
      display_disclaimer: "Awaiting an approved property scan.",
    });
    return { selected: "awaiting_scan", reason: "no_approved_or_draft_or_demo", model: n.model, normalization: n };
  }

  const n = normalizeRealityModel({
    property_id: "unavailable",
    lifecycle_state: "unavailable",
    truth_status: "unknown",
  });
  // Force property_id for empty case — unavailable without id is REJECTED; use placeholder id
  return {
    selected: "unavailable",
    reason: "no_property_context",
    model: n.status === "REJECTED"
      ? normalizeRealityModel({
          property_id: "none",
          lifecycle_state: "unavailable",
          truth_status: "unknown",
        }).model
      : n.model,
  };
}

/** Prefer newer approved projection by model_version / approved_at when both approved. */
export function preferNewerApproved(a, b) {
  const na = normalizeRealityModel(a);
  const nb = normalizeRealityModel(b);
  if (!canDisplayAsApproved(na.model)) return canDisplayAsApproved(nb.model) ? b : null;
  if (!canDisplayAsApproved(nb.model)) return a;
  const va = String(na.model.model_version || "");
  const vb = String(nb.model.model_version || "");
  if (va && vb && va !== vb) return va > vb ? a : b;
  const ta = na.model.approved_at || "";
  const tb = nb.model.approved_at || "";
  if (ta && tb) return ta >= tb ? a : b;
  return a;
}
