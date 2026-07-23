import React from "react";
import { render, screen } from "@testing-library/react";
import Inspector, { findingClaimsApproved, isSampleFinding } from "@/components/Inspector";

describe("Inspector demo finding safety", () => {
  test("demo findings are marked sample and never approved", () => {
    const finding = {
      id: "f1",
      title: "Example roof maintenance category",
      description: "Demo/sample only.",
      data_origin: "demo",
      truth_status: "sample_only",
      confidence_state: "demo",
      is_approved_finding: false,
      is_lidar_detected: false,
      passport_approved: false,
      priority: "medium",
    };
    expect(isSampleFinding(finding)).toBe(true);
    expect(findingClaimsApproved(finding)).toBe(false);
  });

  test("demoMode prefers empty verified-finding state", () => {
    render(<Inspector demoMode finding={null} asset={null} />);
    expect(screen.getByTestId("inspector-demo-banner")).toBeInTheDocument();
    expect(screen.getByTestId("inspector-empty-demo")).toBeInTheDocument();
    expect(screen.queryByTestId("inspector-finding-block")).not.toBeInTheDocument();
    expect(screen.getByTestId("inspector-panel").getAttribute("data-finding-approved")).toBe("false");
  });

  test("sample finding chip language when rendered outside demo empty mode", () => {
    const finding = {
      id: "f2",
      title: "Example finding",
      description: "Not an approved property finding.",
      data_origin: "demo",
      truth_status: "sample_only",
      priority: "low",
      is_approved_finding: false,
    };
    render(<Inspector demoMode={false} finding={finding} asset={{ name: "Roof", zone: "Z", area: "sample", system: "Roofing", data_origin: "demo" }} />);
    expect(screen.getByTestId("finding-sample-chip").textContent).toMatch(/Not an approved property finding/i);
    expect(screen.getByTestId("inspector-panel").getAttribute("data-finding-approved")).toBe("false");
  });
});
