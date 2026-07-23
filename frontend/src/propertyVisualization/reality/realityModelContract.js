/**
 * H-014C.1 — Governed Habitat-side EXISTING-room reality model contract.
 *
 * Habitat consumes authorized Passport projections only.
 * Habitat never approves geometry, writes Passport truth, or fabricates dimensions.
 */

export const REALITY_LIFECYCLE_STATES = Object.freeze([
  "awaiting_scan",
  "capture_in_progress",
  "draft_candidate",
  "quality_review",
  "needs_recapture",
  "professional_review",
  "approved_projection",
  "superseded",
  "unavailable",
  "demo_sample",
]);

export const REALITY_TRUTH_STATES = Object.freeze([
  "demo",
  "sample_only",
  "draft",
  "observed",
  "estimated",
  "homeowner_provided",
  "measured",
  "verified",
  "approved",
  "unknown",
]);

export const REALITY_DATA_ORIGINS = Object.freeze([
  "demo",
  "lidar",
  "photogrammetry",
  "drone",
  "manual_dimensions",
  "imported_bim_cad",
  "composite",
  "passport_projection",
  "unknown",
]);

export const NORMALIZE_RESULTS = Object.freeze({
  VALID: "VALID",
  VALID_WITH_WARNINGS: "VALID_WITH_WARNINGS",
  UNAVAILABLE: "UNAVAILABLE",
  REJECTED: "REJECTED",
});

export const LIFECYCLE_LABELS = Object.freeze({
  awaiting_scan: "AWAITING SCAN",
  capture_in_progress: "CAPTURE IN PROGRESS",
  draft_candidate: "DRAFT CANDIDATE",
  quality_review: "AWAITING REVIEW",
  needs_recapture: "NEEDS RECAPTURE",
  professional_review: "AWAITING REVIEW",
  approved_projection: "APPROVED PROPERTY MODEL",
  superseded: "SUPERSEDED",
  unavailable: "UNAVAILABLE",
  demo_sample: "DEMO / SAMPLE ONLY",
});

export const SUPPORTED_3D_FORMATS = Object.freeze(["glb", "gltf", "usdz", "obj"]);

/** Empty governed model shell — all geometry flags false; unknowns explicit. */
export function emptyRealityModel(overrides = {}) {
  return {
    property_id: null,
    room_id: null,
    model_id: null,
    projection_id: null,
    source_capture_id: null,
    source_mission_id: null,
    source_passport_version: null,
    schema_version: "h014c1.reality.v1",
    model_version: null,

    data_origin: "unknown",
    truth_status: "unknown",
    confidence_state: "unknown",
    lifecycle_state: "unavailable",
    source_system: "habitat",
    source_type: "existing_geometry",
    captured_at: null,
    processed_at: null,
    reviewed_at: null,
    approved_at: null,
    approved_by_role: null,
    checksum: null,
    object_manifest_reference: null,
    generated_at: null,

    floor_plan_available: false,
    three_d_model_available: false,
    dimensions_available: false,
    openings_available: false,
    surfaces_available: false,
    objects_available: false,
    adjoining_room_alignment_available: false,

    floor_plan_ref: null,
    model_3d_ref: null,
    thumbnail_ref: null,
    preview_ref: null,
    manifest_ref: null,

    quality_score: null,
    completeness_state: "unknown",
    unknown_fields: [],
    missing_elements: [],
    quality_warnings: [],
    review_required: false,
    recapture_required: false,
    display_disclaimer: null,

    // Geometry payloads — only when legitimately supplied
    walls: null,
    openings: null,
    dimensions: null,
    room_name: null,

    geometry_kind: "existing", // existing | proposed | as_built — only existing displayed here
    ...overrides,
  };
}

export function isApprovedLifecycle(state) {
  return state === "approved_projection";
}

export function isDemoLifecycle(state) {
  return state === "demo_sample";
}

export function isDraftLifecycle(state) {
  return state === "draft_candidate" || state === "quality_review" || state === "professional_review";
}

export function canDisplayAsApproved(model) {
  if (!model) return false;
  if (model.lifecycle_state !== "approved_projection") return false;
  if (model.truth_status !== "approved" && model.truth_status !== "verified") return false;
  if (model.data_origin === "demo") return false;
  if (!model.projection_id || !model.source_passport_version) return false;
  if (!model.schema_version || !model.property_id) return false;
  return true;
}
