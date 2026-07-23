/**
 * Habitat Property Visualization contract.
 *
 * Habitat may render approved Passport *projections* and demo/sample exteriors.
 * Habitat must never write approved inspection truth, Passport records, or Core
 * property truth from this module.
 */

/** @typedef {'demo'|'awaiting_scan'|'processing'|'model_available'|'partial_model'|'unavailable'|'error'} VisualizationState */

/** @typedef {'demo'|'lidar'|'photogrammetry'|'drone'|'manual_dimensions'|'imported_bim_cad'|'composite'} ModelSource */

/** @typedef {'verified'|'measured'|'observed'|'homeowner_provided'|'estimated'|'assumed'|'demo'} TruthConfidence */

/** @typedef {'interior_reality'|'exterior_reality'|'home_systems'|'whole_property'} StudioWorkspace */

/**
 * Scan-readiness lifecycle (LiDAR-independent foundation).
 * Does not imply capture hardware is available.
 * @typedef {'no_scan'|'scan_scheduled'|'upload_received'|'processing'|'quality_review_required'|'approved_model_available'} ScanReadiness
 */

/**
 * @typedef {Object} PropertyHotspot
 * @property {string} id
 * @property {string} label
 * @property {string} category
 * @property {number} xPct  // 0–100 left
 * @property {number} yPct  // 0–100 top
 * @property {string} summary
 * @property {'example_intelligence'|'awaiting_verified_scan'|'sample_maintenance'} insightKind
 * @property {TruthConfidence} confidence
 */

/**
 * @typedef {Object} PropertyVisualizationProps
 * @property {string} propertyId
 * @property {object} [propertyProfile]
 * @property {string} [visualizationSource]
 * @property {'image'|'model'|'poster'|'unavailable'} [visualizationType]
 * @property {string} [exteriorAsset]
 * @property {string} [exteriorAssetMobile]
 * @property {string} [modelAsset]
 * @property {string} [posterAsset]
 * @property {PropertyHotspot[]} [hotspots]
 * @property {string} [selectedMode]
 * @property {VisualizationState} [loadingState]  // preferred: visualizationState
 * @property {VisualizationState} [visualizationState]
 * @property {TruthConfidence} [confidenceState]
 * @property {boolean} [fallbackState]
 * @property {ScanReadiness} [scanReadiness]
 * @property {ModelSource} [modelSource]
 * @property {(hotspot: PropertyHotspot) => void} [onHotspotSelect]
 * @property {React.ReactNode} [children] overlays (layers panel, toolbars)
 */

export const VISUALIZATION_STATES = Object.freeze([
  "demo",
  "awaiting_scan",
  "processing",
  "model_available",
  "partial_model",
  "unavailable",
  "error",
]);

export const SCAN_READINESS_STATES = Object.freeze([
  "no_scan",
  "scan_scheduled",
  "upload_received",
  "processing",
  "quality_review_required",
  "approved_model_available",
]);

export const MODEL_SOURCES = Object.freeze([
  "demo",
  "lidar",
  "photogrammetry",
  "drone",
  "manual_dimensions",
  "imported_bim_cad",
  "composite",
]);

export const TRUTH_CONFIDENCE = Object.freeze([
  "verified",
  "measured",
  "observed",
  "homeowner_provided",
  "estimated",
  "assumed",
  "demo",
]);

export const STUDIO_WORKSPACES = Object.freeze([
  "interior_reality",
  "exterior_reality",
  "home_systems",
  "whole_property",
]);

export function isDemoTruth(confidence) {
  return confidence === "demo" || confidence === "assumed" || confidence === "estimated";
}

export function hotspotClaimsVerifiedFinding(hotspot) {
  if (!hotspot) return false;
  if (hotspot.confidence === "demo") return false;
  if (hotspot.insightKind === "example_intelligence") return false;
  if (hotspot.insightKind === "awaiting_verified_scan") return false;
  if (hotspot.insightKind === "sample_maintenance") return false;
  return hotspot.confidence === "verified" || hotspot.confidence === "measured";
}
