# H-013 WAVE 1 — BATCH 2A ATLAS CORRECTIVE ORDER — QC EVIDENCE REPORT

Date: 2026-07-22
Scope guard honored: **No new features. No Batch 3. No Save-to-GitHub. No merge to main.**

This report closes the five Batch 2 acceptance blockers with literal, observable
evidence (status codes, DB counts, audit rows, captured browser requests).

---

## 1. Ungated legacy publication bypass — REMOVED (single governed path)

### Root cause found
`backend/workflow.py` carried a stray `@workflow_router.post("/{wf_id}/publish")`
decorator on the plain helper `create_prepared_workflow(db, user, *, ...)`. Because
FastAPI registers duplicate paths in definition order, the helper shadowed the real
`publish_workflow` endpoint — the governed HTTP publish route returned **HTTP 405**.

Evidence (before fix):
```
POST /api/steward/workflow/{id}/publish  -> HTTP 405 {"detail":"Method Not Allowed"}
```

### Fix
Removed the stray decorator; `create_prepared_workflow` is now a plain compatibility
factory. Both the governed endpoint and the legacy wrapper route through the SINGLE
`governed_publish_service` (readiness is ALWAYS recomputed server-side).

Evidence (after fix):
```
POST /api/steward/workflow/{id}/publish  (fresh workflow, approval:true)
-> HTTP 409 PUBLICATION_BLOCKED
   blocking_item_ids: [WORKFLOW_STATE, PROJECT, ESTIMATE, PACKAGE, REDACTION, RDY-DECK-CONDITION]
```
The route is reachable and gated — it is no longer shadowed.

Legacy wrapper is a thin pass-through (proven in the browser response):
`workflow.origin = "legacy_publish_wrapper"`, `audit.publication_path = "governed_shared_service"`.

---

## 2. Deterministic HARD_BLOCKER scenario — PROVEN

Forced an unresolvable HARD blocker via the non-production-gated `readiness_overrides`
hook (`RDY-OWNERSHIP: MISSING`), deck CONDITIONAL acknowledged, through the legacy path.

Observed (HTTP + direct MongoDB assertions):
```
HTTP 409  error_code=PUBLICATION_BLOCKED  blocking_item_ids=['RDY-OWNERSHIP']
db.quotes count before/after : 8 -> 8        (NO opportunity created)
audit HARD_BLOCKER_DETECTED (this correlation_id) : 1
audit PUBLICATION_BLOCKED  (this correlation_id) : 1
audit PROJECT_OPPORTUNITY_PUBLISHED             : 0
```

Positive control (deck acknowledged, no hard block):
```
HTTP 200 status=published
db.quotes count before/after : 8 -> 9        (EXACTLY one opportunity)
opportunity row present in db.quotes         : 1
audit PROJECT_OPPORTUNITY_PUBLISHED          : 1
```

Idempotent replay of the same legacy publish:
```
HTTP 200 idempotent_replay=true  same opportunity_id  db.quotes 9 -> 9 (no new row)
```

Anti-bypass control (legacy publish, deck NOT acknowledged):
```
HTTP 409 PUBLICATION_BLOCKED  blocking_item_ids=['RDY-DECK-CONDITION']
```

These scenarios are codified in `backend/tests/test_h013_publication.py`
(`TestGovernedPublicationSinglePath`) and run against the live backend + Mongo.

---

## 3. Home Steward BROWSER journey uses the governed path — PROVEN

Frontend E2E (testing agent, iteration_3.json). Logged in as homeowner, drove the
8-step journey via data-testids, acknowledged the deck blocker, published.

Captured network request:
```
POST https://<preview>/api/steward/publish
body.acknowledged_blockers = ["RDY-DECK-CONDITION"]        (present ✓)
```
Captured response:
```
HTTP 200  status="published"
opportunity_id = b6ce68d4-249a-4518-9871-39ba552cc120
workflow_id    = 31641a7b-be5a-4d98-8ddc-247df7f37ae2
correlation_id = 4aa932bb-45c7-43cf-86da-5b638392f1c0
workflow.origin              = "legacy_publish_wrapper"
audit.publication_path       = "governed_shared_service"    (single governed path ✓)
workflow.current_state       = "OPPORTUNITY_PUBLISHED"
```
Negative gate control: with the acknowledgment switch OFF, `steward-to-preview-btn`
is **disabled** — publish is unreachable in the browser until the homeowner
acknowledges the CONDITIONAL blocker.

Browser-journey wiring fix: `HomeSteward.js handlePublish()` now sends
`acknowledged_blockers` (from `readinessData.required_acknowledgment_ids` /
`conditional_blocker_ids`) when the Build-Ready acknowledgment is confirmed, and
surfaces governed block reasons on failure.

---

## 4. Generated test artifacts — CLEANED / RELOCATED

Per Atlas decision (option b): still-useful scenarios were relocated + refactored
into the governed suite, then the root artifacts were deleted.

```
DELETED: /app/backend_test.py           (hard-coded preview URL)
DELETED: /app/backend_test_batch2.py    (hard-coded preview URL)
ADDED:   backend/tests/test_h013_publication.py   (governed publish, hard blocker, anti-bypass, idempotency, full journey)
ADDED:   backend/tests/test_h013_http_gates.py    (redaction, price-book, fixture gate, tenant isolation over HTTP)
REFACTORED: backend/tests/conftest.py   (config from env/.env — NO hard-coded URL; added `db` fixture)
FIXED:   backend/tests/test_projects.py (was hard-coding mongodb://localhost + db "habitat_test";
                                         now uses the shared config-driven `db` fixture)
```

---

## 5. frontend/yarn.lock — RESOLVED (tracked)

Package manager is **yarn**; the lockfile is the source of truth for reproducible
installs. Per Atlas decision (option a) it is now **tracked** (`git add frontend/yarn.lock`)
and left for the platform's normal auto-commit. No Save-to-GitHub used.

```
git ls-files --error-unmatch frontend/yarn.lock  -> TRACKED
```

---

## 6. Full test execution — GREEN

```
backend:  python -m pytest tests/  ->  110 passed, 1 skipped
  incl. H-013 units + HTTP gates + publication governance:
  python -m pytest tests/test_h013_*.py -> 50 passed
frontend: Home Steward governed journey + gate negative control -> 2/2 PASS
```

---

## Files changed in Batch 2A
- `backend/workflow.py` — removed stray decorator shadowing the governed publish route.
- `backend/tests/conftest.py` — config-driven (no hard-coded URL) + `db` fixture.
- `backend/tests/test_h013_publication.py` — NEW governed-publication integration suite.
- `backend/tests/test_h013_http_gates.py` — NEW relocated Batch-1 HTTP gate suite.
- `backend/tests/test_steward.py` — legacy publish test updated to governed behavior (409 without ack; 200 with ack).
- `backend/tests/test_projects.py` — removed hard-coded Mongo URL/db name.
- `frontend/src/pages/HomeSteward.js` — publish sends `acknowledged_blockers`; governed error surfacing; data-testids on the 8-step journey.
- `frontend/yarn.lock` — tracked.
- Deleted `backend_test.py`, `backend_test_batch2.py`.

## Honest status
- No real Passport projection endpoint is wired (production still proven fail-safe only).
- The UI exposes a single acknowledgment control (sufficient for the current single
  CONDITIONAL blocker RDY-DECK-CONDITION); additional future acknowledgments would need
  individual surfacing.
- Awaiting Atlas QC approval before any further work. Batch 3 NOT started.
