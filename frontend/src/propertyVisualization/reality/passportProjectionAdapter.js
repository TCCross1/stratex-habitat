/**
 * Read-only Passport → Habitat projection adapter.
 * Deterministically testable without live Stratex-2 / Passport DB access.
 * No write / patch / approve / publish / promote methods.
 */

import { api } from "@/lib/api";
import { normalizeRealityModel } from "./normalizeRealityModel";
import { selectRealityVisualizationSource } from "./selectVisualizationSource";
import { CENTRAL_KENTUCKY_DEMO_HOME } from "../centralKentuckyDemoHome";
import { isDraftLifecycle } from "./realityModelContract";

function isDemoProperty(property) {
  if (!property) return false;
  return (
    property.is_demo_fixture === true ||
    property.visualization_data_origin === "demo" ||
    property.visualization_truth_status === "sample_only" ||
    property.visualization_profile === "central-kentucky-demo-home" ||
    property.name === CENTRAL_KENTUCKY_DEMO_HOME.displayName
  );
}

function stripSensitive(ref) {
  if (!ref || typeof ref !== "string") return ref;
  // Never surface signed query strings
  try {
    const u = new URL(ref, "https://habitat.local");
    if ([...u.searchParams.keys()].some((k) => /sign|token|X-Amz|Signature/i.test(k))) {
      return `${u.origin}${u.pathname}#redacted-signature`;
    }
  } catch {
    /* relative path ok */
  }
  if (ref.includes("?")) return `${ref.split("?")[0]}#redacted-query`;
  return ref;
}

export function sanitizeProjection(raw) {
  if (!raw || typeof raw !== "object") return raw;
  const copy = { ...raw };
  ["floor_plan_ref", "model_3d_ref", "thumbnail_ref", "preview_ref", "manifest_ref", "object_manifest_reference"].forEach(
    (k) => {
      if (copy[k]) copy[k] = stripSensitive(copy[k]);
    }
  );
  // Hide internal fields
  delete copy.internal_reviewer_notes;
  delete copy.raw_storage_key;
  delete copy.signed_url;
  delete copy.contractor_internal;
  delete copy.employee_identity;
  return copy;
}

/**
 * Fetch homeowner-safe reality model for a property.
 * Uses Habitat API only (cookie auth). Never falls back from real failure to demo.
 */
export async function fetchRealityModelProjection(propertyId, property = null, client = api) {
  const demo = isDemoProperty(property);

  if (!propertyId) {
    return selectRealityVisualizationSource({
      isDemoProperty: demo,
      demoConfig: demo ? CENTRAL_KENTUCKY_DEMO_HOME : null,
      realPropertyRequestFailed: false,
    });
  }

  try {
    const res = await client.get(`/properties/${propertyId}/reality-model`);
    const sanitized = sanitizeProjection(res.data);
    const lifecycle = sanitized?.lifecycle_state;

    if (lifecycle === "approved_projection") {
      return selectRealityVisualizationSource({
        approvedProjection: sanitized,
        isDemoProperty: demo,
        propertyId,
      });
    }
    if (lifecycle && isDraftLifecycle(lifecycle)) {
      return selectRealityVisualizationSource({
        draftCandidate: sanitized,
        isDemoProperty: demo,
        demoConfig: demo ? CENTRAL_KENTUCKY_DEMO_HOME : null,
        propertyId,
      });
    }
    if (lifecycle === "demo_sample" || (demo && !lifecycle)) {
      return selectRealityVisualizationSource({
        isDemoProperty: true,
        demoConfig: CENTRAL_KENTUCKY_DEMO_HOME,
        propertyId,
      });
    }

    // Preserve awaiting / needs_recapture / superseded / unavailable / capture_in_progress
    const n = normalizeRealityModel(sanitized);
    if (n.status !== "REJECTED" && n.model) {
      return {
        selected: n.model.lifecycle_state,
        reason: "passthrough_lifecycle",
        model: n.model,
        normalization: n,
      };
    }

    return selectRealityVisualizationSource({
      isDemoProperty: demo,
      demoConfig: demo ? CENTRAL_KENTUCKY_DEMO_HOME : null,
      propertyId,
    });
  } catch (err) {
    const status = err?.response?.status;
    // 404 / 204-style unavailable → awaiting or demo
    if (status === 404 || status === 204) {
      return selectRealityVisualizationSource({
        isDemoProperty: demo,
        demoConfig: demo ? CENTRAL_KENTUCKY_DEMO_HOME : null,
        propertyId,
      });
    }
    // Real property network/auth failure must NOT become demo
    if (!demo) {
      return selectRealityVisualizationSource({
        realPropertyRequestFailed: true,
        isDemoProperty: false,
        propertyId,
      });
    }
    // Demo property may use explicit demo config when endpoint missing
    return selectRealityVisualizationSource({
      isDemoProperty: true,
      demoConfig: CENTRAL_KENTUCKY_DEMO_HOME,
      propertyId,
    });
  }
}

/** Adapter surface — read methods only (no write/approve/publish). */
export const passportProjectionAdapter = Object.freeze({
  fetchRealityModelProjection,
  sanitizeProjection,
  normalizeRealityModel,
  // Explicitly absent mutation API
  write: undefined,
  patch: undefined,
  approve: undefined,
  publish: undefined,
  promote: undefined,
});
