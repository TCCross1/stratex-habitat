/**
 * H-014C.1 — read-only 2D/3D viewers + provenance panel.
 * Synthetic geometry fixtures are explicitly sample_only / not_property_truth.
 */
import { render, screen, fireEvent } from "@testing-library/react";
import RoomFloorPlan2D from "../RoomFloorPlan2D";
import RoomModel3D from "../RoomModel3D";
import ModelProvenancePanel from "../ModelProvenancePanel";
import { emptyRealityModel } from "@/propertyVisualization/reality/realityModelContract";

const SAMPLE_WALLS = {
  sample_only: true,
  not_property_truth: true,
  not_passport_approved: true,
  walls: [
    { x1: 0, y1: 0, x2: 50, y2: 0 },
    { x1: 50, y1: 0, x2: 50, y2: 40 },
    { x1: 50, y1: 40, x2: 0, y2: 40 },
    { x1: 0, y1: 40, x2: 0, y2: 0 },
  ],
  openings: [{ x1: 12, y1: 0, x2: 22, y2: 0 }],
};

describe("RoomFloorPlan2D", () => {
  test("supplied walls and openings render; no editing controls", () => {
    const model = emptyRealityModel({
      property_id: "fixture",
      lifecycle_state: "draft_candidate",
      truth_status: "draft",
      data_origin: "lidar",
      walls: SAMPLE_WALLS.walls,
      openings: SAMPLE_WALLS.openings,
      room_name: "Fixture Room",
      dimensions: { width_m: null, length_m: 4, height_m: undefined },
      floor_plan_available: true,
      openings_available: true,
    });
    render(<RoomFloorPlan2D model={model} />);
    expect(screen.getByTestId("room-floorplan-2d-svg")).toBeInTheDocument();
    expect(screen.getByTestId("room-floorplan-2d-wall-0")).toBeInTheDocument();
    expect(screen.getByTestId("room-floorplan-2d-opening-0")).toBeInTheDocument();
    expect(screen.getByTestId("room-floorplan-2d-dims").textContent).toMatch(/unknown/);
    expect(screen.queryByLabelText(/edit|resize|drag handle/i)).not.toBeInTheDocument();
    expect(screen.getByTestId("room-floorplan-2d-lifecycle")).toHaveTextContent(/DRAFT CANDIDATE/i);
  });

  test("absent geometry does not fabricate; state displays", () => {
    const model = emptyRealityModel({
      property_id: "p1",
      lifecycle_state: "awaiting_scan",
      truth_status: "unknown",
    });
    render(<RoomFloorPlan2D model={model} />);
    expect(screen.getByTestId("room-floorplan-2d-empty")).toBeInTheDocument();
    expect(screen.queryByTestId("room-floorplan-2d-svg")).not.toBeInTheDocument();
    expect(screen.getByTestId("room-floorplan-2d")).toHaveAttribute("data-has-geometry", "false");
  });

  test("demo/sample and needs-recapture and unavailable states", () => {
    const { rerender } = render(
      <RoomFloorPlan2D
        model={emptyRealityModel({ property_id: "d", lifecycle_state: "demo_sample", truth_status: "sample_only", data_origin: "demo" })}
      />
    );
    expect(screen.getByTestId("room-floorplan-2d-lifecycle")).toHaveTextContent(/DEMO/i);

    rerender(
      <RoomFloorPlan2D
        model={emptyRealityModel({ property_id: "d", lifecycle_state: "needs_recapture", truth_status: "draft", recapture_required: true })}
      />
    );
    expect(screen.getByTestId("room-floorplan-2d-lifecycle")).toHaveTextContent(/NEEDS RECAPTURE/i);

    rerender(
      <RoomFloorPlan2D
        model={emptyRealityModel({ property_id: "d", lifecycle_state: "unavailable", truth_status: "unknown" })}
      />
    );
    expect(screen.getByTestId("room-floorplan-2d-lifecycle")).toHaveTextContent(/UNAVAILABLE/i);
  });

  test("keyboard zoom controls on viewport", () => {
    const model = emptyRealityModel({
      property_id: "fixture",
      lifecycle_state: "approved_projection",
      truth_status: "approved",
      walls: SAMPLE_WALLS.walls,
    });
    render(<RoomFloorPlan2D model={model} />);
    const viewport = screen.getByTestId("room-floorplan-2d-viewport");
    viewport.focus();
    fireEvent.keyDown(viewport, { key: "+" });
    fireEvent.keyDown(viewport, { key: "ArrowRight" });
    fireEvent.keyDown(viewport, { key: "0" });
    expect(screen.getByTestId("room-floorplan-2d-reset")).toBeInTheDocument();
  });

  test("mobile-safe layout — no horizontal overflow class on root", () => {
    const { container } = render(
      <RoomFloorPlan2D
        model={emptyRealityModel({ property_id: "p", lifecycle_state: "quality_review", truth_status: "draft" })}
      />
    );
    expect(container.firstChild.className).toMatch(/overflow-hidden/);
  });
});

describe("RoomModel3D", () => {
  test("no-model state message", () => {
    render(
      <RoomModel3D
        model={emptyRealityModel({ property_id: "p", lifecycle_state: "awaiting_scan", truth_status: "unknown" })}
      />
    );
    expect(screen.getByTestId("room-model-3d-no-model")).toHaveTextContent(
      /3D model awaiting an approved property scan/i
    );
    expect(screen.queryByLabelText(/edit mesh|sculpt/i)).not.toBeInTheDocument();
  });

  test("supported model reference present state", () => {
    render(
      <RoomModel3D
        model={emptyRealityModel({
          property_id: "p",
          lifecycle_state: "approved_projection",
          truth_status: "approved",
          three_d_model_available: true,
          model_3d_ref: "/fixtures/not-property-truth-sample.glb",
        })}
      />
    );
    expect(screen.getByTestId("room-model-3d-present")).toBeInTheDocument();
  });

  test("unsupported format and WebGL unavailable", () => {
    const { rerender } = render(
      <RoomModel3D
        model={emptyRealityModel({
          property_id: "p",
          lifecycle_state: "draft_candidate",
          truth_status: "draft",
          three_d_model_available: true,
          model_3d_ref: "/fixtures/sample.fbx",
        })}
      />
    );
    expect(screen.getByTestId("room-model-3d-unsupported")).toBeInTheDocument();

    rerender(
      <RoomModel3D
        webglAvailable={false}
        model={emptyRealityModel({
          property_id: "p",
          lifecycle_state: "draft_candidate",
          truth_status: "draft",
          three_d_model_available: true,
          model_3d_ref: "/fixtures/sample.glb",
        })}
      />
    );
    expect(screen.getByTestId("room-model-3d-webgl-unavailable")).toBeInTheDocument();
  });

  test("reduced-motion omits pulse animation class", () => {
    render(
      <RoomModel3D
        reducedMotion
        model={emptyRealityModel({
          property_id: "p",
          lifecycle_state: "approved_projection",
          truth_status: "approved",
          three_d_model_available: true,
          model_3d_ref: "/fixtures/sample.glb",
        })}
      />
    );
    const present = screen.getByTestId("room-model-3d-present");
    expect(present.innerHTML).not.toMatch(/animate-pulse/);
  });

  test("orbit/zoom/reset are present but read-only (disabled until renderer)", () => {
    render(
      <RoomModel3D
        model={emptyRealityModel({ property_id: "p", lifecycle_state: "unavailable", truth_status: "unknown" })}
      />
    );
    expect(screen.getByTestId("room-model-3d-orbit")).toBeDisabled();
    expect(screen.getByTestId("room-model-3d-zoom")).toBeDisabled();
    expect(screen.getByTestId("room-model-3d-reset")).toBeDisabled();
  });
});

describe("ModelProvenancePanel", () => {
  test("shows lifecycle label, demo warning, unknowns; hides internal fields", () => {
    render(
      <ModelProvenancePanel
        model={emptyRealityModel({
          property_id: "demo",
          lifecycle_state: "demo_sample",
          truth_status: "sample_only",
          data_origin: "demo",
          model_version: "demo-exterior-v1",
          source_passport_version: null,
          checksum: "abcdef0123456789deadbeef",
          unknown_fields: ["walls", "dimensions"],
          missing_elements: ["approved_3d_model"],
          display_disclaimer: "The Central Kentucky Demonstration Home is demonstration/sample-only data.",
          internal_reviewer_notes: "should not render",
        })}
      />
    );
    expect(screen.getByTestId("model-provenance-badge")).toHaveTextContent(/DEMO \/ SAMPLE ONLY/i);
    expect(screen.getByTestId("model-provenance-demo-warning")).toBeInTheDocument();
    expect(screen.getByTestId("model-provenance-unknowns")).toHaveTextContent(/walls/);
    expect(screen.getByTestId("model-provenance-checksum").textContent.length).toBeLessThan(20);
    expect(screen.queryByText(/should not render/)).not.toBeInTheDocument();
  });

  test("approved version visible", () => {
    render(
      <ModelProvenancePanel
        model={emptyRealityModel({
          property_id: "p",
          lifecycle_state: "approved_projection",
          truth_status: "approved",
          data_origin: "passport_projection",
          model_version: "m2.0.0",
          source_passport_version: "passport-v3",
          projection_id: "proj-1",
        })}
      />
    );
    expect(screen.getByTestId("model-provenance-badge")).toHaveTextContent(/APPROVED PROPERTY MODEL/i);
    expect(screen.getByTestId("model-provenance-model-version")).toHaveTextContent("m2.0.0");
    expect(screen.getByTestId("model-provenance-passport-version")).toHaveTextContent("passport-v3");
  });
});
