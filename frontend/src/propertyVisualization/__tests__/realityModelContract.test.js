/**
 * H-014C.1 — governed reality-model contract, normalization, selection, adapter.
 */
import {
  NORMALIZE_RESULTS,
  REALITY_LIFECYCLE_STATES,
  canDisplayAsApproved,
  emptyRealityModel,
} from "../reality/realityModelContract";
import { normalizeRealityModel } from "../reality/normalizeRealityModel";
import {
  preferNewerApproved,
  selectRealityVisualizationSource,
} from "../reality/selectVisualizationSource";
import {
  fetchRealityModelProjection,
  passportProjectionAdapter,
} from "../reality/passportProjectionAdapter";
import { CENTRAL_KENTUCKY_DEMO_HOME } from "../centralKentuckyDemoHome";

function approvedFixture(overrides = {}) {
  return {
    property_id: "prop-real-1",
    projection_id: "proj-1",
    source_passport_version: "passport-v3",
    schema_version: "h014c1.reality.v1",
    model_version: "m2.0.0",
    lifecycle_state: "approved_projection",
    truth_status: "approved",
    data_origin: "passport_projection",
    geometry_kind: "existing",
    floor_plan_available: true,
    walls: [
      { x1: 0, y1: 0, x2: 40, y2: 0 },
      { x1: 40, y1: 0, x2: 40, y2: 30 },
      { x1: 40, y1: 30, x2: 0, y2: 30 },
      { x1: 0, y1: 30, x2: 0, y2: 0 },
    ],
    openings: [{ x1: 10, y1: 0, x2: 18, y2: 0 }],
    dimensions: { width_m: 4, length_m: 3, height_m: null },
    ...overrides,
  };
}

describe("H-014C.1 reality model contract", () => {
  test("lifecycle catalog includes required states", () => {
    expect(REALITY_LIFECYCLE_STATES).toEqual(
      expect.arrayContaining([
        "awaiting_scan",
        "draft_candidate",
        "quality_review",
        "needs_recapture",
        "approved_projection",
        "superseded",
        "unavailable",
        "demo_sample",
      ])
    );
  });

  test("approved projection normalizes VALID and canDisplayAsApproved", () => {
    const n = normalizeRealityModel(approvedFixture());
    expect(n.status).toBe(NORMALIZE_RESULTS.VALID);
    expect(canDisplayAsApproved(n.model)).toBe(true);
    expect(n.model.unknown_fields).toContain("dimensions.height_m");
  });

  test("draft candidate remains draft — never approved", () => {
    const n = normalizeRealityModel({
      property_id: "p1",
      lifecycle_state: "draft_candidate",
      truth_status: "draft",
      data_origin: "lidar",
      model_3d_ref: "https://cdn.example/model.glb",
      three_d_model_available: true,
    });
    expect(n.status).toBe(NORMALIZE_RESULTS.VALID);
    expect(canDisplayAsApproved(n.model)).toBe(false);
    expect(n.model.lifecycle_state).toBe("draft_candidate");
  });

  test("demo sample cannot become approved", () => {
    const n = normalizeRealityModel({
      property_id: "demo",
      lifecycle_state: "approved_projection",
      truth_status: "sample_only",
      data_origin: "demo",
      projection_id: "x",
      source_passport_version: "y",
    });
    expect(n.status).toBe(NORMALIZE_RESULTS.REJECTED);
    expect(n.errors).toContain("demo_cannot_become_approved");
  });

  test("awaiting scan and unavailable", () => {
    const a = normalizeRealityModel({
      property_id: "p1",
      lifecycle_state: "awaiting_scan",
      truth_status: "unknown",
    });
    expect(a.status).toBe(NORMALIZE_RESULTS.VALID);
    expect(a.model.lifecycle_state).toBe("awaiting_scan");

    const u = normalizeRealityModel({
      property_id: "p1",
      lifecycle_state: "unavailable",
      truth_status: "unknown",
    });
    expect(u.model.lifecycle_state).toBe("unavailable");
  });

  test("superseded remains superseded", () => {
    const n = normalizeRealityModel({
      property_id: "p1",
      lifecycle_state: "superseded",
      truth_status: "approved",
      data_origin: "passport_projection",
    });
    expect(n.model.lifecycle_state).toBe("superseded");
    expect(canDisplayAsApproved(n.model)).toBe(false);
  });

  test("schema / lifecycle mismatch and malformed payloads reject safely", () => {
    expect(normalizeRealityModel(null).status).toBe(NORMALIZE_RESULTS.UNAVAILABLE);
    expect(normalizeRealityModel({ property_id: "p1", lifecycle_state: "bogus" }).status).toBe(
      NORMALIZE_RESULTS.REJECTED
    );
    expect(normalizeRealityModel({ lifecycle_state: "awaiting_scan" }).errors).toContain(
      "missing_property_association"
    );
  });

  test("approved without projection provenance is rejected", () => {
    const n = normalizeRealityModel({
      property_id: "p1",
      lifecycle_state: "approved_projection",
      truth_status: "approved",
      data_origin: "passport_projection",
      model_3d_ref: "/models/x.glb",
    });
    expect(n.status).toBe(NORMALIZE_RESULTS.REJECTED);
    expect(n.errors).toContain("approved_requires_projection_provenance");
  });

  test("proposed geometry rejected; as-built without approval rejected", () => {
    expect(
      normalizeRealityModel({
        property_id: "p1",
        geometry_kind: "proposed",
        lifecycle_state: "draft_candidate",
        truth_status: "draft",
      }).errors
    ).toContain("proposed_geometry_not_allowed_as_existing");

    expect(
      normalizeRealityModel({
        property_id: "p1",
        geometry_kind: "as_built",
        lifecycle_state: "draft_candidate",
        truth_status: "draft",
      }).errors
    ).toContain("as_built_requires_approved_projection");
  });

  test("missing openings stay absent — never fabricated", () => {
    const n = normalizeRealityModel(approvedFixture({ openings: undefined, openings_available: false }));
    expect(n.model.openings).toBeNull();
  });

  test("does not mutate source payload", () => {
    const raw = approvedFixture();
    const before = JSON.stringify(raw);
    normalizeRealityModel(raw);
    expect(JSON.stringify(raw)).toBe(before);
  });

  test("emptyRealityModel defaults are safe", () => {
    const m = emptyRealityModel();
    expect(m.floor_plan_available).toBe(false);
    expect(m.walls).toBeNull();
    expect(m.quality_score).toBeNull();
  });
});

describe("H-014C.1 visualization selection rules", () => {
  test("approved beats demo", () => {
    const r = selectRealityVisualizationSource({
      approvedProjection: approvedFixture(),
      isDemoProperty: true,
      demoConfig: CENTRAL_KENTUCKY_DEMO_HOME,
      propertyId: "prop-real-1",
    });
    expect(r.selected).toBe("approved_projection");
  });

  test("approved beats draft", () => {
    const r = selectRealityVisualizationSource({
      approvedProjection: approvedFixture(),
      draftCandidate: {
        property_id: "prop-real-1",
        lifecycle_state: "draft_candidate",
        truth_status: "draft",
        data_origin: "lidar",
      },
      propertyId: "prop-real-1",
    });
    expect(r.selected).toBe("approved_projection");
  });

  test("newer approved beats older approved", () => {
    const older = approvedFixture({ model_version: "m1.0.0", approved_at: "2025-01-01T00:00:00Z" });
    const newer = approvedFixture({ model_version: "m2.0.0", approved_at: "2026-01-01T00:00:00Z" });
    expect(preferNewerApproved(older, newer).model_version).toBe("m2.0.0");
  });

  test("draft never becomes approved; demo never becomes approved", () => {
    const draft = selectRealityVisualizationSource({
      draftCandidate: {
        property_id: "p1",
        lifecycle_state: "draft_candidate",
        truth_status: "draft",
        data_origin: "lidar",
      },
      propertyId: "p1",
    });
    expect(draft.selected).toBe("draft_candidate");
    expect(canDisplayAsApproved(draft.model)).toBe(false);

    const demo = selectRealityVisualizationSource({
      isDemoProperty: true,
      demoConfig: CENTRAL_KENTUCKY_DEMO_HOME,
      propertyId: CENTRAL_KENTUCKY_DEMO_HOME.propertyId,
    });
    expect(demo.selected).toBe("demo_sample");
    expect(canDisplayAsApproved(demo.model)).toBe(false);
    expect(demo.model.truth_status).toBe("sample_only");
  });

  test("failed real request never silently becomes demo", () => {
    const r = selectRealityVisualizationSource({
      realPropertyRequestFailed: true,
      isDemoProperty: false,
      propertyId: "real-prop",
    });
    expect(r.selected).toBe("unavailable");
    expect(r.reason).toBe("real_property_request_failed_no_demo_fallback");
  });

  test("unavailable remains unavailable", () => {
    const r = selectRealityVisualizationSource({});
    expect(r.selected).toBe("unavailable");
  });
});

describe("H-014C.1 passport projection adapter", () => {
  test("exposes no write/approve/publish/promote methods", () => {
    expect(passportProjectionAdapter.write).toBeUndefined();
    expect(passportProjectionAdapter.patch).toBeUndefined();
    expect(passportProjectionAdapter.approve).toBeUndefined();
    expect(passportProjectionAdapter.publish).toBeUndefined();
    expect(passportProjectionAdapter.promote).toBeUndefined();
  });

  test("strips signed URL query strings", () => {
    const clean = passportProjectionAdapter.sanitizeProjection({
      property_id: "p1",
      lifecycle_state: "awaiting_scan",
      truth_status: "unknown",
      model_3d_ref: "https://store.example/m.glb?X-Amz-Signature=secret&token=abc",
      internal_reviewer_notes: "hide me",
      raw_storage_key: "s3://secret",
    });
    expect(clean.model_3d_ref).not.toMatch(/Signature|token=/);
    expect(clean.internal_reviewer_notes).toBeUndefined();
    expect(clean.raw_storage_key).toBeUndefined();
  });

  test("real property 500 does not fall back to demo", async () => {
    const client = {
      get: async () => {
        const err = new Error("fail");
        err.response = { status: 500 };
        throw err;
      },
    };
    const r = await fetchRealityModelProjection("real-1", { is_demo_fixture: false }, client);
    expect(r.selected).toBe("unavailable");
  });

  test("demo property may use explicit demo config on 404", async () => {
    const client = {
      get: async () => {
        const err = new Error("missing");
        err.response = { status: 404 };
        throw err;
      },
    };
    const r = await fetchRealityModelProjection(
      CENTRAL_KENTUCKY_DEMO_HOME.propertyId,
      { is_demo_fixture: true, visualization_profile: "central-kentucky-demo-home" },
      client
    );
    expect(r.selected).toBe("demo_sample");
  });

  test("approved projection from API selected", async () => {
    const client = {
      get: async () => ({ data: approvedFixture() }),
    };
    const r = await fetchRealityModelProjection("prop-real-1", { is_demo_fixture: false }, client);
    expect(r.selected).toBe("approved_projection");
  });
});

describe("Central Kentucky demonstration markers", () => {
  test("exactly one governed Habitat demo identity", () => {
    expect(CENTRAL_KENTUCKY_DEMO_HOME.displayName).toBe("Central Kentucky Demonstration Home");
    expect(CENTRAL_KENTUCKY_DEMO_HOME.truthStatus).toBe("sample_only");
    expect(CENTRAL_KENTUCKY_DEMO_HOME.dataOrigin).toBe("demo");
    expect(CENTRAL_KENTUCKY_DEMO_HOME.confidenceState).toBe("demo");
  });

  test("demo selection never yields approved truth", () => {
    const r = selectRealityVisualizationSource({
      isDemoProperty: true,
      demoConfig: CENTRAL_KENTUCKY_DEMO_HOME,
    });
    expect(r.model.data_origin).toBe("demo");
    expect(r.model.truth_status).toBe("sample_only");
    expect(canDisplayAsApproved(r.model)).toBe(false);
  });
});
