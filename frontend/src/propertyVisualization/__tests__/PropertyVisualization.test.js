import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import PropertyVisualization, { StudioEmptyState } from "@/components/property/PropertyVisualization";
import {
  CENTRAL_KENTUCKY_DEMO_HOME,
  getCentralKentuckyDemoVisualization,
  lidarAdapterBoundary,
} from "@/propertyVisualization/centralKentuckyDemoHome";
import {
  assertNoHabitatTruthWrite,
  SCAN_READINESS_FIXTURES,
  studioEmptyState,
} from "@/propertyVisualization/lidarIndependentFoundations";
import { hotspotClaimsVerifiedFinding, isDemoTruth } from "@/propertyVisualization/types";

describe("Central Kentucky demo property visualization", () => {
  test("loads Central Kentucky demonstration home configuration", () => {
    const cfg = getCentralKentuckyDemoVisualization();
    expect(cfg.displayName).toMatch(/Central Kentucky/i);
    expect(cfg.dataOrigin).toBe("demo");
    expect(cfg.truthStatus).toBe("sample_only");
    expect(cfg.exteriorAsset).toContain("habitat-central-kentucky-demo-home");
    expect(cfg.modelAsset).toBeNull();
  });

  test("demo data is marked sample-only", () => {
    expect(CENTRAL_KENTUCKY_DEMO_HOME.dataOrigin).toBe("demo");
    expect(CENTRAL_KENTUCKY_DEMO_HOME.truthStatus).toBe("sample_only");
    expect(isDemoTruth(CENTRAL_KENTUCKY_DEMO_HOME.confidenceState)).toBe(true);
  });

  test("renders demo stage without remote flat-roof CDN house", () => {
    render(
      <PropertyVisualization
        visualizationState="demo"
        confidenceState="demo"
        modelSource="demo"
        scanReadiness="no_scan"
      />
    );
    const img = screen.getByTestId("twin-image");
    expect(img.getAttribute("src")).toContain("/property-visualizations/habitat-central-kentucky-demo-home");
    expect(img.getAttribute("src")).not.toContain("emergentagent.com");
    expect(img.getAttribute("data-demo-home")).toBe("central-kentucky");
    expect(screen.getByTestId("twin-stage").getAttribute("data-origin")).toBe("demo");
    expect(screen.getByTestId("twin-stage").getAttribute("data-truth-status")).toBe("sample_only");
    expect(screen.getByTestId("property-demo-badge").textContent).toMatch(/demo/i);
  });

  test("supports awaiting_scan and model_available visualization states", () => {
    const { rerender } = render(
      <PropertyVisualization visualizationState="awaiting_scan" confidenceState="demo" />
    );
    expect(screen.getByTestId("property-viz-fallback")).toBeInTheDocument();
    expect(screen.getByTestId("twin-stage").getAttribute("data-visualization-state")).toBe("awaiting_scan");

    rerender(
      <PropertyVisualization
        visualizationState="model_available"
        confidenceState="verified"
        modelSource="lidar"
        exteriorAsset="/property-visualizations/habitat-central-kentucky-demo-home.webp"
        scanReadiness="approved_model_available"
      />
    );
    expect(screen.getByTestId("twin-stage").getAttribute("data-visualization-state")).toBe("model_available");
    expect(screen.queryByTestId("property-viz-fallback")).not.toBeInTheDocument();
  });

  test("hotspots do not claim verified findings for demo data", () => {
    render(<PropertyVisualization visualizationState="demo" />);
    const hotspot = screen.getByTestId("hotspot-hs-roof");
    expect(hotspot.getAttribute("data-claims-verified")).toBe("false");
    fireEvent.click(hotspot);
    expect(screen.getByTestId("hotspot-panel")).toBeInTheDocument();
    expect(screen.getByTestId("hotspot-truth-label").textContent).toMatch(/not an approved finding/i);
    expect(screen.getByTestId("hotspot-panel").textContent).toMatch(/Example intelligence area/i);
    CENTRAL_KENTUCKY_DEMO_HOME.hotspots.forEach((hs) => {
      expect(hotspotClaimsVerifiedFinding(hs)).toBe(false);
    });
  });

  test("fallback appears when preferred asset fails or unavailable", () => {
    render(<PropertyVisualization visualizationState="unavailable" />);
    expect(screen.getByTestId("property-viz-fallback")).toBeInTheDocument();
  });

  test("desktop and mobile layouts render without component failure", () => {
    const { container, rerender } = render(
      <div style={{ width: 1280 }}>
        <PropertyVisualization visualizationState="demo" />
      </div>
    );
    expect(container.querySelector('[data-testid="twin-stage"]')).toBeTruthy();
    rerender(
      <div style={{ width: 375 }}>
        <PropertyVisualization visualizationState="demo" />
      </div>
    );
    expect(screen.getByTestId("twin-image")).toBeInTheDocument();
    expect(screen.getByTestId("property-viz-picture")).toBeInTheDocument();
  });

  test("studio empty foundations do not fabricate content", () => {
    render(<StudioEmptyState workspace="interior_reality" />);
    expect(screen.getByTestId("studio-empty-interior_reality").textContent).toMatch(/no fabricated/i);
    expect(studioEmptyState("exterior_reality").title).toMatch(/Exterior/i);
  });

  test("Habitat does not duplicate Core or Passport write authority", () => {
    const guards = assertNoHabitatTruthWrite();
    expect(guards.canWritePassportTruth).toBe(false);
    expect(guards.canWriteCoreInspectionTruth).toBe(false);
    expect(guards.canFabricateLidarMesh).toBe(false);
    expect(guards.canFabricateMeasurements).toBe(false);
  });

  test("LiDAR adapter boundary rejects unapproved projections", () => {
    expect(lidarAdapterBoundary.acceptApprovedProjection(null).visualizationState).toBe("awaiting_scan");
    expect(
      lidarAdapterBoundary.acceptApprovedProjection({ approved: true, modelSource: "lidar" }).visualizationState
    ).toBe("model_available");
    expect(SCAN_READINESS_FIXTURES.no_scan.fabricatedGeometry).toBe(false);
  });
});
