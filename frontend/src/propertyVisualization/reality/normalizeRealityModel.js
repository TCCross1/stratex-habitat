/**
 * Deterministic normalization of backend/property payloads into the governed
 * reality-model contract. Never mutates the source payload.
 */

import {
  NORMALIZE_RESULTS,
  REALITY_DATA_ORIGINS,
  REALITY_LIFECYCLE_STATES,
  REALITY_TRUTH_STATES,
  canDisplayAsApproved,
  emptyRealityModel,
  isApprovedLifecycle,
} from "./realityModelContract";

function isNonEmptyString(v) {
  return typeof v === "string" && v.trim().length > 0;
}

function clone(v) {
  if (v == null) return v;
  return JSON.parse(JSON.stringify(v));
}

/**
 * @param {object|null|undefined} raw
 * @returns {{ status: string, model: object|null, warnings: string[], errors: string[] }}
 */
export function normalizeRealityModel(raw) {
  const warnings = [];
  const errors = [];

  if (raw == null || typeof raw !== "object") {
    return {
      status: NORMALIZE_RESULTS.UNAVAILABLE,
      model: emptyRealityModel({
        lifecycle_state: "unavailable",
        display_disclaimer: "No reality model payload available.",
      }),
      warnings,
      errors: ["payload_missing"],
    };
  }

  // Never mutate source
  const src = clone(raw);

  if (src.geometry_kind === "proposed") {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: ["proposed_geometry_not_allowed_as_existing"],
    };
  }

  // Completed as-built cannot silently replace existing without approved projection
  if (src.geometry_kind === "as_built" && src.lifecycle_state !== "approved_projection") {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: ["as_built_requires_approved_projection"],
    };
  }

  if (!isNonEmptyString(src.property_id)) {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: ["missing_property_association"],
    };
  }

  const lifecycle = src.lifecycle_state || src.lifecycle || "unavailable";
  if (!REALITY_LIFECYCLE_STATES.includes(lifecycle)) {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: [`unsupported_lifecycle:${lifecycle}`],
    };
  }

  const truth = src.truth_status || src.truthStatus || "unknown";
  if (!REALITY_TRUTH_STATES.includes(truth)) {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: [`unsupported_truth_status:${truth}`],
    };
  }

  const origin = src.data_origin || src.dataOrigin || "unknown";
  if (!REALITY_DATA_ORIGINS.includes(origin)) {
    warnings.push(`unknown_data_origin:${origin}`);
  }

  // Demo can never become approved
  if ((origin === "demo" || truth === "demo" || truth === "sample_only" || lifecycle === "demo_sample")
    && isApprovedLifecycle(lifecycle)) {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: ["demo_cannot_become_approved"],
    };
  }

  // Draft cannot become approved via presence of URL alone
  if (
    (lifecycle === "draft_candidate" || truth === "draft")
    && (src.truth_status === "approved" || src.lifecycle_state === "approved_projection")
  ) {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: ["draft_cannot_become_approved"],
    };
  }

  const model = emptyRealityModel({
    property_id: src.property_id,
    room_id: src.room_id ?? null,
    model_id: src.model_id ?? null,
    projection_id: src.projection_id ?? null,
    source_capture_id: src.source_capture_id ?? null,
    source_mission_id: src.source_mission_id ?? null,
    source_passport_version: src.source_passport_version ?? null,
    schema_version: src.schema_version || "h014c1.reality.v1",
    model_version: src.model_version ?? null,

    data_origin: REALITY_DATA_ORIGINS.includes(origin) ? origin : "unknown",
    truth_status: truth,
    confidence_state: src.confidence_state || src.confidenceState || "unknown",
    lifecycle_state: lifecycle,
    source_system: src.source_system || "habitat",
    source_type: "existing_geometry",
    captured_at: src.captured_at ?? null,
    processed_at: src.processed_at ?? null,
    reviewed_at: src.reviewed_at ?? null,
    approved_at: src.approved_at ?? null,
    approved_by_role: src.approved_by_role ?? null,
    checksum: src.checksum ?? null,
    object_manifest_reference: src.object_manifest_reference ?? null,
    generated_at: src.generated_at ?? null,

    floor_plan_available: Boolean(src.floor_plan_available),
    three_d_model_available: Boolean(src.three_d_model_available),
    dimensions_available: Boolean(src.dimensions_available),
    openings_available: Boolean(src.openings_available),
    surfaces_available: Boolean(src.surfaces_available),
    objects_available: Boolean(src.objects_available),
    adjoining_room_alignment_available: Boolean(src.adjoining_room_alignment_available),

    floor_plan_ref: src.floor_plan_ref ?? null,
    model_3d_ref: src.model_3d_ref ?? null,
    thumbnail_ref: src.thumbnail_ref ?? null,
    preview_ref: src.preview_ref ?? null,
    manifest_ref: src.manifest_ref ?? null,

    // quality_score only when legitimately supplied (not invented)
    quality_score: typeof src.quality_score === "number" ? src.quality_score : null,
    completeness_state: src.completeness_state || "unknown",
    unknown_fields: Array.isArray(src.unknown_fields) ? src.unknown_fields : [],
    missing_elements: Array.isArray(src.missing_elements) ? src.missing_elements : [],
    quality_warnings: Array.isArray(src.quality_warnings) ? src.quality_warnings : [],
    review_required: Boolean(src.review_required),
    recapture_required: Boolean(src.recapture_required) || lifecycle === "needs_recapture",
    display_disclaimer: src.display_disclaimer ?? null,

    walls: Array.isArray(src.walls) ? src.walls : null,
    openings: Array.isArray(src.openings) ? src.openings : null,
    dimensions: src.dimensions && typeof src.dimensions === "object" ? src.dimensions : null,
    room_name: isNonEmptyString(src.room_name) ? src.room_name : null,
    geometry_kind: "existing",
  });

  // Distinguish absent/null (unknown) vs zero (explicit measurement)
  if (model.dimensions) {
    const dims = model.dimensions;
    ["width_m", "length_m", "height_m", "area_m2"].forEach((k) => {
      if (dims[k] === undefined || dims[k] === null) {
        model.unknown_fields.push(`dimensions.${k}`);
      }
    });
  } else if (model.dimensions_available) {
    warnings.push("dimensions_available_true_but_payload_absent");
    model.dimensions_available = false;
    model.unknown_fields.push("dimensions");
  }

  if (model.floor_plan_available && !model.walls && !model.floor_plan_ref) {
    warnings.push("floor_plan_flag_without_geometry");
    model.floor_plan_available = false;
  }

  if (model.three_d_model_available && !model.model_3d_ref) {
    warnings.push("three_d_flag_without_model_ref");
    model.three_d_model_available = false;
  }

  // Approved requires full provenance — never infer from URL alone
  if (isApprovedLifecycle(model.lifecycle_state) && !canDisplayAsApproved(model)) {
    return {
      status: NORMALIZE_RESULTS.REJECTED,
      model: null,
      warnings,
      errors: ["approved_requires_projection_provenance"],
    };
  }

  if (model.lifecycle_state === "demo_sample") {
    model.display_disclaimer =
      model.display_disclaimer ||
      "The Central Kentucky Demonstration Home is demonstration/sample-only data. It is not a physically validated property scan or approved Passport model.";
    model.data_origin = "demo";
    model.truth_status = "sample_only";
    model.confidence_state = "demo";
  }

  const status = warnings.length ? NORMALIZE_RESULTS.VALID_WITH_WARNINGS : NORMALIZE_RESULTS.VALID;
  return { status, model, warnings, errors };
}
