# AI SCAN QUALITY GUARDIAN (Phase 6)

Version 1.0.0 · Specification only. The Guardian is a **capture-time assistant** that helps a
homeowner or operator capture usable data before leaving the room/property. It advises; it does
**not** declare property truth, and it has no authority to certify geometry.

---

## 1. Purpose & authority boundary
- **May:** evaluate coverage/quality, detect likely defects, and request corrective actions.
- **May NOT:** assert dimensions, declare a room/property "verified", approve geometry, or make
  structural/code claims. Its output is advisory metadata attached to the scan session (Phase 5).
- Every Guardian judgment is classified `AI_SUGGESTED_DESIGN`-adjacent advisory (never truth) and
  is auditable.

## 2. Interior checks
Missing walls · missing floor/ceiling coverage · incomplete corners · uncaptured openings ·
misidentified mirrors/glass · motion artifacts · low-confidence geometry · occlusion ·
misalignment · insufficient adjoining-room overlap · scale inconsistency · duplicate surfaces ·
unclosed room boundaries.

## 3. Exterior checks
Missing elevations · roof-plane gaps · poor overlap · blur · exposure problems · insufficient
oblique views · occlusions · thermal/RGB mismatch · incomplete openings · coordinate drift ·
missing site context.

## 4. Verdict model (illustrative)
```jsonc
{
  "session_id": "scan-…",
  "verdict": "PASS | PASS_WITH_GAPS | FLAG | FAIL",
  "coverage_summary": { "walls":"COMPLETE","floor":"PARTIAL","ceiling":"MISSING","openings":"PARTIAL" },
  "issues": [
    { "code":"CEILING_MISSING","severity":"HIGH","surface_ref":"spx-…",
      "explanation":"Ceiling not captured; area/volume will be estimated.",
      "requested_action":"ADDITIONAL_SWEEP" },
    { "code":"MIRROR_SUSPECTED","severity":"MEDIUM","explanation":"Reflective surface may create false depth." }
  ],
  "requested_actions": ["RESCAN","ADDITIONAL_SWEEP","ADDITIONAL_PHOTO","ADD_CONTROL_POINT",
                        "MANUAL_CONFIRMATION","PROFESSIONAL_REVIEW"],
  "confidence": "MEDIUM",
  "classification_effect": "Ungathered regions remain UNKNOWN; low-confidence geometry marked ESTIMATED/INFERRED.",
  "generated_at": "…", "model_version": "guardian-1.0.0"
}
```

## 5. Requested actions
`RESCAN` · `ADDITIONAL_SWEEP` · `ADDITIONAL_PHOTO` · `ADD_CONTROL_POINT` · `MANUAL_CONFIRMATION`
(homeowner confirms an ambiguous element) · `PROFESSIONAL_REVIEW` (defer to Core/professional).

## 6. Effect on truth classification (Phase 7)
- Uncaptured/occluded regions ⇒ remain `UNKNOWN` (never fabricated).
- Low-confidence geometry ⇒ `ESTIMATED_EXISTING` or `INFERRED_EXISTING`, with confidence surfaced.
- Only well-covered, good-fit geometry is eligible for `MEASURED_EXISTING`.
- Guardian never promotes anything to `VERIFIED_EXISTING`/canonical.

## 7. Homeowner experience
- Plain-language guidance ("Point at the ceiling and move slowly to fill the gap"); no jargon.
- Live coverage heatmap; a clear "good enough to plan" vs "needs another pass" signal.
- Blocks silent acceptance of `INSUFFICIENT` coverage for anything presented as existing condition.

## 8. Governance & audit
- Runs at capture-time and on reprocessing; each verdict is versioned and stored on the session.
- If AI inference is used, it is governed (bounded prompts, no free-form authority) and its model
  version is recorded. On AI/service failure the Guardian degrades to deterministic coverage checks
  and marks `verdict: FLAG` rather than fabricating a PASS.

## 9. Relationship to existing code
- Conceptually parallels `readiness_policy` (server-owned classification the UI renders) but scoped
  to capture quality. No engine implemented in this mission.
