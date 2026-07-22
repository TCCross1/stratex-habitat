# H-013 Wave 1 — Batch 1 Summary (Critical Security & Runtime Gates)

**Generated:** 2026-07-22
**Repository:** TCCross1/Habitat · **Branch:** copilot/tcc-1-update-documentation
**Scope:** Batch 1 of Wave 1 (per operator sequencing = sub-batches). Delivers the
critical runtime + security gates before Passport-projection / persistence work.

> Git writes (commit/push) are performed by the operator via "Save to Github".
> All changes below are staged in the working tree on the authorized branch.

---

## Priorities addressed in this batch

| # | Priority | Status |
|---|---|---|
| 1 | Restore backend startup | ✅ CI dependency conflict pinned; live runtime verified healthy |
| 2 | Audit repository state | ✅ `H013_REPOSITORY_VERIFICATION.md` + `H013_RUNTIME_REPAIR.md` |
| 3 | Preserve/reuse Home Steward | ✅ All H-012 endpoints preserved (backward-compatible) |
| 4 | Remove production reliance on deterministic fixtures | ✅ `fixture_provider.py` env gate + provenance |
| 7 | Hard-coded pricing → governed price-book | ✅ `pricebook.py` versioned provider |
| 9 | Enforce contractor-package redaction on backend | ✅ `redaction.py` allow-list stripping |
| 10 | Executable tests for security gates | ✅ `tests/test_h013_security.py` (9 tests) |

**Deferred to Batch 2 (per operator):** #5 versioned Passport projection boundary,
#6 Build Ready publication-blocker reconciliation, #8 homeowner workflow persistence,
plus workflow-gate tests.

---

## New modules (backend/)

### `pricebook.py` — Governed, versioned price-book (#7)
- `PRICE_BOOK_VERSION = "2026.07.0"`, `EFFECTIVE_DATE`, `CURRENCY=USD`.
- Roof assemblies (GAF / DECRA / CertainTeed) with national/regional/local ranges + cost breakdown (moved out of Steward's inline `EST_DATA`).
- `planning_estimate(material, basis)` returns a range + breakdown + a **governance provenance** block (`price_source=HABITAT_GOVERNED_PRICE_BOOK`, `price_book_version`, `governed=True`, `authoritative=False`).
- All numeric roof price literals removed from `steward.py` and sourced here.

### `fixture_provider.py` — Deterministic fixture gate (#4)
- `HABITAT_ENV` (default `development`) + optional `HABITAT_ENABLE_FIXTURES` override.
- Fixtures **auto-disabled in production**. When disabled, `serve_fixture()` raises `FixtureDisabledError` → API returns **HTTP 409** (never served silently).
- When enabled, payloads are tagged with `_provenance` (`data_source=DETERMINISTIC_FIXTURE`, `authoritative=False`, `environment`).

### `redaction.py` — Server-side contractor-package redaction (#9)
- Allow-list (`CONTRACTOR_VISIBLE_FIELDS`) — only approved fields survive.
- Recursively **strips** all `SENSITIVE_KEYS` (last name, email, phone, exact address) and `INTERNAL_ONLY_KEYS` (owner_id, correlation ids, internal confidence/trust). Removed, not masked.
- Personal contact released **only** on explicit homeowner approval (`?approved=true`).
- Shared documents filtered to `shared=True` only.
- Emits a backward-compatible `redacted_personal_info` MASK block + a `redaction` enforcement-metadata block.

## Steward endpoint changes (backward-compatible)

| Endpoint | Change |
|---|---|
| `GET /api/steward/fixture` | Gated + provenance-tagged via `fixture_provider`; legacy keys preserved |
| `GET /api/steward/context` | Fixture-tagged projection; nested schema preserved (real projection = Batch 2) |
| `POST /api/steward/estimate` | Sources pricing from `pricebook`; adds `price_book_version` + `price_provenance` |
| `POST /api/steward/confirm` | Project `est_low/est_high` sourced from price-book |
| `GET /api/steward/scenarios` | Scenario A roof cost rendered via governed price-book |
| `GET /api/steward/recommendation` | Replacement-planning range rendered via price-book |
| `GET /api/steward/contractor-package` | Built from an internal package then **redacted server-side**; `?approved=` releases contact only after approval |

## Config
- `backend/.env`: added `HABITAT_ENV=development`, `HABITAT_ENABLE_FIXTURES=true` (additive; protected URL vars untouched).
- `backend/requirements.txt`: `cryptography==44.0.1`, `pyOpenSSL==25.1.0` (CI fix — see runtime repair doc).

## Verification
- `tests/test_h013_security.py`: **9/9 passed** (price-book provenance, fixture gate incl. production-disabled, redaction preview/approved).
- Live HTTP smoke test (homeowner session): fixture/context tagged, estimate governed, contractor-package leaks **0** PII/internal values in preview, contact released only when approved. **PASS**.
- Backend: `Application startup complete`, `GET /api/` → HTTP 200 on the pinned deps.
