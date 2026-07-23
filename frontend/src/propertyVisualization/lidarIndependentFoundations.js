/**
 * LiDAR-independent Habitat foundations: scan readiness, studio empty states,
 * and mock fixtures. No fake LiDAR processing, meshes, or measurements.
 */

import { SCAN_READINESS_STATES, STUDIO_WORKSPACES, TRUTH_CONFIDENCE } from "./types";

export const SCAN_READINESS_LABELS = Object.freeze({
  no_scan: "No property scan available",
  scan_scheduled: "Scan scheduled",
  upload_received: "Upload received",
  processing: "Processing",
  quality_review_required: "Quality review required",
  approved_model_available: "Approved model available",
});

export const STUDIO_EMPTY_COPY = Object.freeze({
  interior_reality: {
    title: "Interior Reality Studio",
    body: "Interior spaces appear here after an approved interior scan or Passport projection. Demo mode does not invent rooms or dimensions.",
  },
  exterior_reality: {
    title: "Exterior Reality Studio",
    body: "Exterior envelope intelligence awaits a verified exterior model. The demonstration home is sample imagery only.",
  },
  home_systems: {
    title: "Home Systems Studio",
    body: "HVAC, electrical, plumbing, and related systems remain empty until approved system locations are projected from Passport.",
  },
  whole_property: {
    title: "Whole Property Transformation",
    body: "Whole-property transformation overlays require an approved property model. No conceptual design is treated as property truth.",
  },
});

export const TRUTH_LABEL_COPY = Object.freeze({
  verified: "Verified",
  measured: "Measured",
  observed: "Observed",
  homeowner_provided: "Homeowner-provided",
  estimated: "Estimated",
  assumed: "Assumed",
  demo: "Demo / sample only",
});

/** Mock fixtures for state transitions — not real capture output. */
export const SCAN_READINESS_FIXTURES = Object.freeze(
  SCAN_READINESS_STATES.reduce((acc, state) => {
    acc[state] = {
      scanReadiness: state,
      label: SCAN_READINESS_LABELS[state],
      dataOrigin: state === "approved_model_available" ? "projection_stub" : "demo",
      truthStatus: state === "approved_model_available" ? "awaiting_passport_projection" : "sample_only",
      // Explicit: fixtures never invent meshes or measurements
      fabricatedGeometry: false,
      fabricatedMeasurements: false,
    };
    return acc;
  }, {})
);

export function studioEmptyState(workspace) {
  if (!STUDIO_WORKSPACES.includes(workspace)) {
    return {
      title: "Studio unavailable",
      body: "Unknown workspace. Habitat does not invent property geometry.",
    };
  }
  return STUDIO_EMPTY_COPY[workspace];
}

export function truthBadgeLabel(confidence) {
  return TRUTH_LABEL_COPY[confidence] || TRUTH_LABEL_COPY.demo;
}

export function assertNoHabitatTruthWrite() {
  // Architectural guard used by tests — Habitat visualization must not expose
  // write helpers for Passport / Core approved truth.
  return Object.freeze({
    canWritePassportTruth: false,
    canWriteCoreInspectionTruth: false,
    canFabricateLidarMesh: false,
    canFabricateMeasurements: false,
  });
}
