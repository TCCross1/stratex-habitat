# PROPERTY COORDINATE & ALIGNMENT STANDARD (Phase 4)

Version 1.0.0 · Specification only. Defines how every captured and designed dataset aligns to ONE
property coordinate system so Interior and Exterior are spatially the same home.

---

## 1. Frames of reference
| Frame | Origin | Use |
|---|---|---|
| `PROPERTY_FRAME` (canonical) | Fixed property datum (see §3) | The single global frame all data resolves into |
| `LEVEL_LOCAL` | Per-level reference point | Interior room layout within a floor |
| `SCAN_LOCAL` | Per-scan device origin | Raw LiDAR/photogrammetry as captured |
| `DRONE_FRAME` | Exterior reconstruction frame (geo-referenced) | Drone orthomosaic/mesh, roof, elevations |

All non-canonical frames carry a **transform** into `PROPERTY_FRAME`; nothing is displayed as
"aligned" until its transform exists and its residual error is recorded.

## 2. Units, scale, orientation, datum
- **Canonical units:** metric meters (`METRIC_M`). Display may convert to ft-in; storage stays metric.
- **Scale:** 1.0 (true scale). Scale inconsistency is a scan-quality defect (Phase 6), not silently corrected.
- **North orientation:** true-north bearing stored on `PROPERTY_FRAME`; magnetic vs true noted.
- **Elevation datum:** a property-local vertical datum (finished ground floor = 0.000 m by default);
  geodetic elevation optional and labeled if present.

## 3. Origin definition
- `PROPERTY_FRAME` origin = a durable, re-observable point (e.g., a front-elevation building corner
  at ground level) recorded with provenance. If unavailable, a provisional origin is used and marked
  `confidence: LOW` until a durable control point is captured.

## 4. Transforms
- Each dataset stores a 4×4 rigid transform (rotation + translation; optional uniform scale only if
  proven) from its local frame → `PROPERTY_FRAME`, plus:
  - `residual_error_m` (RMS of control-point fit), `method` (control-point | feature-match | manual),
    `control_points[]`, `transform_version`, `computed_at`, `confidence`.
- Illustrative shape:
```jsonc
{ "from":"SCAN_LOCAL","to":"PROPERTY_FRAME","matrix":[[...4],[...4],[...4],[0,0,0,1]],
  "residual_error_m":0.043,"tolerance_class":"PLANNING","method":"control_point",
  "control_points":[{"id":"cp1","local":[..],"property":[..]}],
  "confidence":"MEDIUM","transform_version":2,"computed_at":"…" }
```

## 5. Alignment operations
- **Level alignment:** stack LEVEL_LOCAL frames vertically using shared stair/opening references.
- **Room-to-room:** align adjoining rooms via shared wall/opening overlap (requires overlap; Phase 6
  flags insufficient adjoining overlap).
- **Interior-to-exterior registration:** match interior perimeter walls + window/door openings to
  exterior elevation openings; produces building-level registration.
- **Roof & elevation alignment:** register `ROOF_PLANE`/`EXTERIOR_ELEVATION` from drone frame to
  `PROPERTY_FRAME` via geo-reference + building-corner control points.
- **Scan-to-scan comparison / historical scans:** align new scans to the canonical frame to compare
  against prior scans (change detection); each scan retains its own transform + timestamp.
- **Proposed design geometry:** authored directly in `PROPERTY_FRAME`/`LEVEL_LOCAL`; labeled PROPOSED.
- **Completed as-built geometry:** a post-completion scan re-registered to `PROPERTY_FRAME`.

## 6. Tolerance classes (honest, non-engineering)
| Class | Intended RMS residual | Meaning | Allowed claims |
|---|---|---|---|
| `VISUALIZATION` | not guaranteed | Look/feel only | No dimensions asserted |
| `PLANNING` | ~2–5 cm target (unverified) | Homeowner planning & rough takeoff | "Approximate", confidence shown |
| `FIELD_REVIEW` | tighter, still unverified | Pre-contractor review | Requires on-site verification |
| `SURVEY_GRADE` | **not claimed** | Reserved | **Never claimed unless independently proven** |
- Habitat defaults to `PLANNING`. **No engineering-grade / survey-grade accuracy is claimed** unless
  externally validated evidence exists. Estimates and takeoffs inherit the tolerance class.

## 7. Confidence, residual error & control points
- Every transform stores residual error + confidence; low fit ⇒ `confidence: LOW` and a Guardian
  prompt (Phase 6) to add control points or rescan.
- **Manual control points:** the operator/homeowner may tag matching points to improve/repair a fit;
  each is provenance-stamped.

## 8. Failure & partial states
| State | Meaning | Behavior |
|---|---|---|
| `UNALIGNED` | No transform yet | Data shown only in its local frame, labeled "not aligned" |
| `PARTIALLY_ALIGNED` | Some regions aligned | Aligned regions usable at their tolerance; gaps labeled |
| `ALIGNMENT_FAILED` | Fit exceeded acceptable residual | Blocked from "existing truth"; rescan/control points requested |
| `RE_REGISTRATION_REQUIRED` | Datum/origin changed or drift detected | Recompute transforms; version bumps |
- **Coordinate drift** (exterior) and **scale inconsistency** (interior) are explicit defects.

## 9. Versioning & audit
- Transforms and the `PROPERTY_FRAME` definition are versioned; re-registration creates a new version
  and an audit event; historical alignments are retained for comparison.

## 10. Relationship to boundaries
- Canonical approved geometry from Passport already resides in `PROPERTY_FRAME`; Habitat aligns its
  planning/scan data **to** that canonical frame and never redefines canonical geometry.
