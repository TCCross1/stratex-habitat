import { useEffect, useId, useMemo, useState } from "react";
import { CENTRAL_KENTUCKY_DEMO_HOME } from "@/propertyVisualization/centralKentuckyDemoHome";
import { hotspotClaimsVerifiedFinding, isDemoTruth } from "@/propertyVisualization/types";
import {
  SCAN_READINESS_LABELS,
  truthBadgeLabel,
} from "@/propertyVisualization/lidarIndependentFoundations";

const INSIGHT_LABEL = {
  example_intelligence: "Example intelligence area",
  awaiting_verified_scan: "Awaiting verified property scan",
  sample_maintenance: "Sample maintenance category",
};

/**
 * Reusable Habitat property visualization stage.
 * Demo mode uses the Central Kentucky sample home; future approved models can
 * swap assets through the visualization contract without rebuilding Habitat UI.
 */
export default function PropertyVisualization({
  propertyId,
  propertyProfile,
  visualizationSource,
  visualizationType = "image",
  exteriorAsset,
  exteriorAssetMobile,
  modelAsset,
  posterAsset,
  hotspots,
  selectedMode = "3D",
  visualizationState = "demo",
  confidenceState = "demo",
  fallbackState = false,
  scanReadiness = "no_scan",
  modelSource = "demo",
  onHotspotSelect,
  altText,
  children,
  className = "",
  showHotspots = true,
}) {
  const panelId = useId();
  const [activeHotspotId, setActiveHotspotId] = useState(null);
  const [assetFailed, setAssetFailed] = useState(false);
  const [preferFallback, setPreferFallback] = useState(Boolean(fallbackState));

  const resolved = useMemo(() => {
    const demo = CENTRAL_KENTUCKY_DEMO_HOME;
    const state = visualizationState || "demo";
    const useDemoAssets =
      state === "demo" ||
      visualizationSource === "local_demo_asset" ||
      modelSource === "demo" ||
      !exteriorAsset;

    return {
      propertyId: propertyId || demo.propertyId,
      propertyProfile: propertyProfile || demo.propertyProfile,
      visualizationSource: visualizationSource || (useDemoAssets ? demo.visualizationSource : "remote"),
      visualizationType,
      exteriorAsset: useDemoAssets ? demo.exteriorAsset : exteriorAsset,
      exteriorAssetMobile: useDemoAssets
        ? demo.exteriorAssetMobile
        : exteriorAssetMobile || exteriorAsset,
      modelAsset: modelAsset ?? demo.modelAsset,
      posterAsset: posterAsset || demo.posterAsset,
      hotspots: hotspots || demo.hotspots,
      visualizationState: state,
      confidenceState: confidenceState || "demo",
      scanReadiness: scanReadiness || "no_scan",
      modelSource: modelSource || "demo",
      altText: altText || demo.altText,
      dataOrigin: useDemoAssets ? "demo" : "projection",
      truthStatus: useDemoAssets ? "sample_only" : "awaiting_verification",
    };
  }, [
    propertyId,
    propertyProfile,
    visualizationSource,
    visualizationType,
    exteriorAsset,
    exteriorAssetMobile,
    modelAsset,
    posterAsset,
    hotspots,
    visualizationState,
    confidenceState,
    scanReadiness,
    modelSource,
    altText,
  ]);

  useEffect(() => {
    setAssetFailed(false);
    setPreferFallback(Boolean(fallbackState));
  }, [resolved.exteriorAsset, fallbackState]);

  const activeHotspot = resolved.hotspots?.find((h) => h.id === activeHotspotId) || null;

  const selectHotspot = (hs) => {
    setActiveHotspotId(hs.id);
    if (onHotspotSelect) onHotspotSelect(hs);
  };

  const showEmptyFallback =
    preferFallback ||
    assetFailed ||
    resolved.visualizationState === "unavailable" ||
    resolved.visualizationState === "error" ||
    resolved.visualizationState === "awaiting_scan" ||
    resolved.visualizationState === "processing";

  // Demo mode always prefers the local house unless the asset itself failed.
  const renderDemoOrModelImage =
    resolved.visualizationState === "demo"
      ? !(assetFailed || preferFallback)
      : !showEmptyFallback;
  const desktopSrc = resolved.exteriorAsset;
  const mobileSrc = resolved.exteriorAssetMobile || resolved.exteriorAsset;

  let fallbackMessage = "Visualization unavailable. Showing a safe empty state with no fabricated property geometry.";
  if (resolved.visualizationState === "awaiting_scan") {
    fallbackMessage =
      "Awaiting a verified property scan. Habitat will not invent rooms, meshes, or measurements.";
  } else if (resolved.visualizationState === "processing") {
    fallbackMessage = "Processing received capture data. Results appear only after quality review.";
  }

  return (
    <div
      className={`relative rounded-md border border-[#27272a] twin-stage overflow-hidden mb-4 min-h-[320px] sm:min-h-[420px] ${className}`}
      data-testid="twin-stage"
      data-property-id={resolved.propertyId}
      data-visualization-state={resolved.visualizationState}
      data-origin={resolved.dataOrigin}
      data-truth-status={resolved.truthStatus}
      data-model-source={resolved.modelSource}
      data-scan-readiness={resolved.scanReadiness}
      data-selected-mode={selectedMode}
    >
      <div className="absolute right-3 top-3 z-30 flex flex-col items-end gap-1.5 pointer-events-none">
        <span
          data-testid="property-demo-badge"
          className="pointer-events-auto text-[10px] tracking-wide uppercase px-2 py-1 rounded border border-[rgba(20,241,217,0.35)] bg-[#0a0a0bcc] text-[#14f1d9]"
        >
          {isDemoTruth(resolved.confidenceState) ? "Demo sample" : truthBadgeLabel(resolved.confidenceState)}
        </span>
        <span
          data-testid="scan-readiness-badge"
          className="pointer-events-auto text-[10px] px-2 py-1 rounded border border-[#27272a] bg-[#0a0a0bcc] text-[#a1a1aa] max-w-[11rem] text-right"
        >
          {SCAN_READINESS_LABELS[resolved.scanReadiness] || SCAN_READINESS_LABELS.no_scan}
        </span>
      </div>

      <div className="absolute inset-0 flex items-center justify-center p-4 sm:p-8">
        {renderDemoOrModelImage ? (
          <picture data-testid="property-viz-picture">
            <source media="(max-width: 767px)" srcSet={mobileSrc} type="image/webp" />
            <source srcSet={desktopSrc} type="image/webp" />
            <img
              src={desktopSrc}
              alt={resolved.altText}
              data-testid="twin-image"
              data-demo-home="central-kentucky"
              width={1600}
              height={1067}
              loading="eager"
              decoding="async"
              className="max-h-[min(52vh,520px)] sm:max-h-[min(58vh,560px)] w-auto max-w-full object-contain drop-shadow-[0_0_24px_rgba(20,241,217,0.12)]"
              onError={() => setAssetFailed(true)}
            />
          </picture>
        ) : (
          <div
            data-testid="property-viz-fallback"
            className="w-full max-w-xl text-center px-4 py-10 rounded-md border border-dashed border-[#3f3f46] bg-[#0a0a0b]"
          >
            <div className="text-sm text-white mb-1">Property model not available yet</div>
            <div className="text-[12px] text-[#71717a] leading-relaxed">{fallbackMessage}</div>
          </div>
        )}
      </div>

      {showHotspots && renderDemoOrModelImage
        ? resolved.hotspots.map((hs) => {
            const active = hs.id === activeHotspotId;
            const claimsVerified = hotspotClaimsVerifiedFinding(hs);
            return (
              <button
                key={hs.id}
                type="button"
                data-testid={`hotspot-${hs.id}`}
                data-insight-kind={hs.insightKind}
                data-confidence={hs.confidence}
                data-claims-verified={claimsVerified ? "true" : "false"}
                aria-label={`${hs.label}: ${INSIGHT_LABEL[hs.insightKind] || "Example intelligence area"}`}
                aria-expanded={active}
                aria-controls={panelId}
                onClick={() => selectHotspot(hs)}
                className={`absolute z-20 -translate-x-1/2 -translate-y-1/2 w-4 h-4 sm:w-[18px] sm:h-[18px] rounded-full border-2 border-[#14f1d9] bg-[rgba(20,241,217,0.25)] shadow-[0_0_10px_rgba(20,241,217,0.45)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#14f1d9] focus-visible:ring-offset-2 focus-visible:ring-offset-[#050505] ${
                  active ? "scale-125 bg-[rgba(20,241,217,0.55)]" : "hover:scale-110"
                }`}
                style={{ left: `${hs.xPct}%`, top: `${hs.yPct}%` }}
              />
            );
          })
        : null}

      {activeHotspot ? (
        <div
          id={panelId}
          role="region"
          aria-label="Property intelligence detail"
          data-testid="hotspot-panel"
          className="absolute z-30 left-3 right-3 sm:left-auto sm:right-3 sm:w-72 bottom-[3.5rem] sm:bottom-14 rounded-md border border-[#27272a] bg-[#0a0a0bee] backdrop-blur p-3"
        >
          <div className="flex items-start justify-between gap-2 mb-1">
            <div>
              <div className="text-sm text-white font-medium">{activeHotspot.label}</div>
              <div className="text-[11px] text-[#14f1d9]">
                {INSIGHT_LABEL[activeHotspot.insightKind] || "Example intelligence area"}
              </div>
            </div>
            <button
              type="button"
              className="text-[#71717a] text-xs hover:text-white"
              data-testid="hotspot-panel-close"
              onClick={() => setActiveHotspotId(null)}
            >
              Close
            </button>
          </div>
          <p className="text-[12px] text-[#a1a1aa] leading-relaxed">{activeHotspot.summary}</p>
          <div className="mt-2 text-[10px] uppercase tracking-wide text-[#52525b]" data-testid="hotspot-truth-label">
            {truthBadgeLabel(activeHotspot.confidence)} · not an approved finding
          </div>
        </div>
      ) : null}

      {children}

      {!resolved.modelAsset ? (
        <span className="sr-only" data-testid="model-asset-slot-empty">
          3D model asset slot reserved; no fabricated mesh loaded.
        </span>
      ) : null}
    </div>
  );
}

export function StudioEmptyState({ workspace }) {
  const copyMap = {
    interior_reality: {
      title: "Interior Reality Studio",
      body: "Interior spaces appear after an approved interior scan or Passport projection.",
    },
    exterior_reality: {
      title: "Exterior Reality Studio",
      body: "Exterior intelligence awaits a verified exterior model.",
    },
    home_systems: {
      title: "Home Systems Studio",
      body: "Systems remain empty until approved locations are projected from Passport.",
    },
    whole_property: {
      title: "Whole Property Transformation",
      body: "Whole-property overlays require an approved property model.",
    },
  };
  const copy = copyMap[workspace] || { title: "Studio", body: "Unavailable." };

  return (
    <div
      data-testid={`studio-empty-${workspace}`}
      className="rounded-md border border-dashed border-[#3f3f46] bg-[#0a0a0b] p-5 text-center"
    >
      <div className="text-sm text-white mb-1">{copy.title}</div>
      <div className="text-[12px] text-[#71717a] leading-relaxed">{copy.body}</div>
      <div className="mt-2 text-[10px] uppercase tracking-wide text-[#52525b]">Sample / empty - no fabricated data</div>
    </div>
  );
}
