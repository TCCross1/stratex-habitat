/**
 * Central Kentucky Demonstration Home — controlled demo/sample configuration.
 *
 * dataOrigin: "demo"
 * truthStatus: "sample_only"
 *
 * Values are illustrative for Habitat UI demos. They are NOT Passport-approved
 * property truth and must never be written as verified measurements or findings.
 */

import {
  MODEL_SOURCES,
  SCAN_READINESS_STATES,
} from "./types";

export const CENTRAL_KENTUCKY_DEMO_PROPERTY_ID = "demo-central-kentucky-home";

/** @type {import('./types').PropertyHotspot[]} */
export const CENTRAL_KENTUCKY_DEMO_HOTSPOTS = [
  {
    id: "hs-roof",
    label: "Roof",
    category: "Roofing",
    xPct: 52,
    yPct: 28,
    summary: "Example intelligence area for architectural-shingle roof review after a verified exterior scan.",
    insightKind: "example_intelligence",
    confidence: "demo",
  },
  {
    id: "hs-gutters",
    label: "Gutters",
    category: "Drainage",
    xPct: 38,
    yPct: 42,
    summary: "Sample maintenance category — gutter and downspout inspection after leaf season.",
    insightKind: "sample_maintenance",
    confidence: "demo",
  },
  {
    id: "hs-attic-vent",
    label: "Attic ventilation",
    category: "Ventilation",
    xPct: 58,
    yPct: 22,
    summary: "Awaiting verified property scan to evaluate ridge and soffit ventilation.",
    insightKind: "awaiting_verified_scan",
    confidence: "demo",
  },
  {
    id: "hs-windows",
    label: "Windows",
    category: "Envelope",
    xPct: 44,
    yPct: 48,
    summary: "Example intelligence area for window seals and energy performance once measured.",
    insightKind: "example_intelligence",
    confidence: "demo",
  },
  {
    id: "hs-envelope",
    label: "Exterior envelope",
    category: "Envelope",
    xPct: 68,
    yPct: 55,
    summary: "Sample maintenance category — brick, siding, and stone entry accents.",
    insightKind: "sample_maintenance",
    confidence: "demo",
  },
  {
    id: "hs-hvac",
    label: "HVAC",
    category: "Systems",
    xPct: 82,
    yPct: 68,
    summary: "Awaiting verified property scan for outdoor mechanical placement.",
    insightKind: "awaiting_verified_scan",
    confidence: "demo",
  },
  {
    id: "hs-foundation",
    label: "Foundation",
    category: "Structure",
    xPct: 30,
    yPct: 78,
    summary: "Example intelligence area for foundation grade and visible stem walls.",
    insightKind: "example_intelligence",
    confidence: "demo",
  },
  {
    id: "hs-drainage",
    label: "Drainage",
    category: "Site",
    xPct: 22,
    yPct: 72,
    summary: "Sample maintenance category — lawn grade and driveway drainage paths.",
    insightKind: "sample_maintenance",
    confidence: "demo",
  },
  {
    id: "hs-electrical",
    label: "Electrical service",
    category: "Electrical",
    xPct: 74,
    yPct: 62,
    summary: "Awaiting verified property scan for service equipment location.",
    insightKind: "awaiting_verified_scan",
    confidence: "demo",
  },
  {
    id: "hs-water-entry",
    label: "Water entry risk",
    category: "Envelope",
    xPct: 48,
    yPct: 70,
    summary: "Example intelligence area for porch and entry water-management review.",
    insightKind: "example_intelligence",
    confidence: "demo",
  },
];

export const CENTRAL_KENTUCKY_DEMO_HOME = Object.freeze({
  propertyId: CENTRAL_KENTUCKY_DEMO_PROPERTY_ID,
  dataOrigin: "demo",
  truthStatus: "sample_only",
  displayName: "Central Kentucky Demonstration Home",
  regionLabel: "Lexington, Kentucky",
  // Illustrative only — not captured facts
  sampleCharacteristics: Object.freeze({
    approximateSqFtRange: "2,600–3,400",
    stories: 2,
    bedrooms: 4,
    bathrooms: "2.5–3",
    garage: "attached two-car",
    exterior: "brick and premium siding with stone entry accent",
    roof: "architectural-shingle pitched roof with multiple gables",
    entry: "covered front porch",
    lot: "traditional Central Kentucky suburban lot",
  }),
  propertyProfile: Object.freeze({
    architecture: "transitional Craftsman / Central Kentucky residential",
    roofStyle: "steep pitched multi-gable with architectural shingles",
    notes: "Demo exterior for Habitat visualization while real LiDAR capture is unavailable.",
  }),
  visualizationSource: "local_demo_asset",
  visualizationType: "image",
  visualizationState: "demo",
  confidenceState: "demo",
  scanReadiness: "no_scan",
  modelSource: "demo",
  exteriorAsset: "/property-visualizations/habitat-central-kentucky-demo-home.webp",
  exteriorAssetMobile: "/property-visualizations/habitat-central-kentucky-demo-home-mobile.webp",
  posterAsset: "/property-visualizations/habitat-central-kentucky-demo-home.webp",
  thumbAsset: "/property-visualizations/habitat-central-kentucky-demo-home-thumb.webp",
  /** Reserved slot — GLB not authored; do not invent mesh geometry. */
  modelAsset: null,
  modelAssetSlot: "/property-visualizations/habitat-central-kentucky-demo-home.glb",
  hotspots: CENTRAL_KENTUCKY_DEMO_HOTSPOTS,
  altText:
    "Demonstration view of a two-story Central Kentucky transitional Craftsman home with a steep pitched roof, brick and siding exterior, covered porch, and attached garage. Sample imagery only.",
});

export function getCentralKentuckyDemoVisualization(overrides = {}) {
  return {
    ...CENTRAL_KENTUCKY_DEMO_HOME,
    ...overrides,
    sampleCharacteristics: {
      ...CENTRAL_KENTUCKY_DEMO_HOME.sampleCharacteristics,
      ...(overrides.sampleCharacteristics || {}),
    },
    propertyProfile: {
      ...CENTRAL_KENTUCKY_DEMO_HOME.propertyProfile,
      ...(overrides.propertyProfile || {}),
    },
    hotspots: overrides.hotspots || CENTRAL_KENTUCKY_DEMO_HOME.hotspots,
  };
}

/** Future LiDAR adapter boundary — interfaces only; no fake processing. */
export const lidarAdapterBoundary = Object.freeze({
  supportedModelSources: MODEL_SOURCES,
  supportedScanReadiness: SCAN_READINESS_STATES,
  /**
   * When a real approved model arrives from Passport projection, Habitat may
   * swap visualizationSource/type/assets. Habitat still must not write truth.
   */
  acceptApprovedProjection(projection) {
    if (!projection || projection.approved !== true) {
      return { visualizationState: "awaiting_scan", modelSource: "demo" };
    }
    return {
      visualizationState: "model_available",
      modelSource: projection.modelSource || "lidar",
      confidenceState: projection.confidence || "verified",
      scanReadiness: "approved_model_available",
      exteriorAsset: projection.exteriorAsset || null,
      modelAsset: projection.modelAsset || null,
    };
  },
});
