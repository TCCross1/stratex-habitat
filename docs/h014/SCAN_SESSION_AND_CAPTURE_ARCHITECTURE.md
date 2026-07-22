# SCAN SESSION & CAPTURE ARCHITECTURE (Phase 5)

Version 1.0.0 · Specification only. Defines a governed scan-session model. A scan session is the
unit of capture, provenance, and recovery; it produces artifacts (Phase 13) and candidate geometry
(labeled per Phase 7), never canonical truth.

---

## 1. Supported capture types
`INTERIOR_LIDAR`, `EXTERIOR_DRONE`, `EXTERIOR_HANDHELD_LIDAR`, `PHOTOGRAMMETRY`, `THERMAL`,
`ROOM_RESCAN`, `PARTIAL_AREA`, `POST_PROJECT_COMPLETION`.

## 2. Session model (illustrative, non-binding)
```jsonc
{
  "session_id": "scan-<uuid>",
  "tenant_id": "stratex-habitat",
  "property_id": "<uuid>",
  "actor": { "user_id": "…", "role": "homeowner|operator|professional" },
  "device": { "model": "iPhone 15 Pro", "os": "iOS 18.x", "has_lidar": true },
  "sensor_types": ["LIDAR","RGB"],            // + THERMAL / IMU as available
  "app_version": "habitat-capture X.Y.Z",
  "capture_mode": "GUIDED_ROOM|FREEFORM|DRONE_MISSION|OBLIQUE_SET|THERMAL_SWEEP",
  "started_at": "…", "ended_at": "…",
  "coordinate_frame": "SCAN_LOCAL",           // transform to PROPERTY_FRAME added later (Phase 4)
  "coverage_state": "COMPLETE|PARTIAL|INSUFFICIENT",
  "coverage_map_ref": "art-…",                // per-surface coverage heatmap
  "quality_metrics": { "point_density":"…","tracking_loss_events":0,"mean_confidence":"MEDIUM",
                       "loop_closure":true,"scale_check":"OK|SUSPECT" },
  "missing_areas": [ { "target":"ceiling","reason":"not captured" } ],
  "environmental": { "lighting":"…","weather":"…","wind":"…" },  // where relevant (drone/exterior)
  "raw_artifacts": ["art-raw-…"],             // immutable (Phase 13)
  "processed_artifacts": ["art-mesh-…","art-plan-…"],
  "privacy_state": "SENSITIVE_INTERIOR|STANDARD",
  "upload_state": "PENDING|UPLOADING|UPLOADED|UPLOAD_FAILED|RESUMABLE",
  "processing_state": "QUEUED|PROCESSING|PROCESSED|PROCESSING_FAILED",
  "validation_state": "UNVALIDATED|GUARDIAN_PASSED|GUARDIAN_FLAGGED",  // Phase 6
  "approval_state": "NONE|SUBMITTED_FOR_REVIEW|CORE_APPROVED",         // Core owns approval
  "failure_state": "NONE|INTERRUPTED|TRACKING_LOST|CORRUPT|ABORTED",
  "recovery": { "resumable": true, "resume_token":"…","recovered_from":"scan-…|null" },
  "version": 1,
  "correlation_id": "<uuid>",
  "audit_history": ["evt-…"]
}
```

## 3. Lifecycle (states)
`CREATED → CAPTURING → (INTERRUPTED ↺ resume) → CAPTURE_COMPLETE → UPLOADING → UPLOADED →
PROCESSING → PROCESSED → GUARDIAN_REVIEW → {GUARDIAN_PASSED | GUARDIAN_FLAGGED→rescan} →
MODEL_CANDIDATE_READY`. Terminal failures: `ABORTED`, `PROCESSING_FAILED`, `CORRUPT`.
- Every transition emits an audit event with `correlation_id`.

## 4. Coverage & quality
- Coverage is computed per target surface (walls/floor/ceiling/openings for interior; elevations/
  roof planes for exterior) and summarized as `COMPLETE|PARTIAL|INSUFFICIENT`.
- Quality metrics feed the AI Scan Quality Guardian (Phase 6); `validation_state` reflects its verdict.

## 5. Privacy state
- Interior scans default `SENSITIVE_INTERIOR`: raw RGB/imagery is restricted (Phase 19), signed
  access only, excluded from contractor packages unless explicitly shared and redacted.

## 6. Upload, processing & large-file strategy
- **Chunked, resumable uploads** to object storage (extends existing `/upload` + signed retrieval);
  `resume_token` allows continuation after interruption.
- Raw artifacts are immutable; processed artifacts reference their raw lineage (Phase 13).
- Processing (mesh/plan/segmentation) is asynchronous with explicit `processing_state`; no fabricated
  results on failure — the session stays `PROCESSING_FAILED` and prompts retry.

## 7. Failure & recovery principles
- **Interrupted scan:** preserved as `PARTIAL` + `INTERRUPTED`; resumable; never auto-promoted to complete.
- **Tracking loss / scale suspect:** flagged; Guardian requests corrective sweep/control points.
- **Offline capture:** allowed; queued for resumable upload when connectivity returns.

## 8. Truth & boundary rules
- A scan session yields **candidate existing** geometry classified `MEASURED_EXISTING` (good fit) or
  `ESTIMATED_EXISTING`/`INFERRED_EXISTING` (gaps/low confidence) — **never** canonical/verified.
- Promotion to `VERIFIED_EXISTING`/canonical requires Core/professional approval and Passport
  write-back (Phase 8, Constitution §8). Habitat never self-certifies scans as verified truth.

## 9. Relationship to existing code
- Reuses object storage + signed retrieval and the `audit_events` pattern. Introduces a
  `scan_sessions` collection (new; documented, not implemented here) governed like `steward_workflows`.
