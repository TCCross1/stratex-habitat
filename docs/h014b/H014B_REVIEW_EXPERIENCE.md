# H014B Phase 9 — Habitat Capture Review Experience (read-only)

Frontend: `frontend/src/pages/RealityStudioFoundation.js` (route `/reality-foundation`).
The page is now **tabbed** and preserves all H-014A testids:
- **Reference Room** — the unchanged H-014A deterministic reference room view.
- **Capture Review** — the H-014B controlled capture-review dashboard.

## Capture Review contents (all read-only)
Fetches `POST /api/reality/v1/development/capture-proof/bootstrap` and renders:
1. **Truth-boundary banner** — "read-only capture review; completed capture yields
   DRAFT_CANDIDATE only; native_capture: BLOCKED_NO_APPLE_TOOLCHAIN".
2. **Scan Quality Guardian** — big verdict badge (PASS/WARN/FAIL) + score/100,
   coverage state, recommendation, and the findings list (or "all checks passed").
3. **Scan session** — capture type, state, coverage, device (iPhone 15 Pro / iOS /
   LiDAR Scanner / RoomPlan + ARKit).
4. **Resumable upload** — chunks, chunk size, declared size, checksum (truncated),
   `checksum verified` + `object stored` badges.
5. **Capture → backend state mapping** — a horizontal timeline of the governed
   `state_history` with the originating native state under each canonical state.
6. **Candidate existing-model** — `DRAFT_CANDIDATE` badge, entity count, truth
   classification chips, unknown-areas list.
7. **Preview (2D / 3D)** — a 2D floor plan (SVG) and a decorative isometric room
   box. **No editing controls** — strictly a preview.

## Data-testids (for QA/automation)
`reality-studio-page`, `reality-tab-reference`, `reality-tab-capture`,
`reality-capture-page`, `reality-capture-loading`, `reality-capture-error`,
`reality-capture-truth-notice`, `reality-capture-guardian`,
`reality-capture-verdict`, `reality-capture-no-findings` / `reality-capture-findings`,
`reality-capture-scan`, `reality-capture-scan-state`, `reality-capture-upload`,
`reality-capture-upload-chunks`, `reality-capture-checksum-badge`,
`reality-capture-state-mapping`, `reality-capture-timeline`,
`reality-capture-candidate`, `reality-capture-candidate-state`,
`reality-capture-entity-count`, `reality-capture-preview`,
`reality-foundation-svg`, `reality-capture-iso`.

## No unrestricted design editing
The review experience displays status, Guardian results, and previews only. There
are no material/geometry editing affordances — consistent with the truth boundary
and the H-014A read-only foundation.
