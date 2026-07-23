# H-014A.2 — Security and Capture-Lifecycle Closure

Branch: `cursor/h014a2-security-closure`  
Baseline: `3e4a75ccd0d2628d8844b5ae968a8c721f766b82`  
Independent audit branch (unchanged): `cursor/h014a-independent-qc`

## Purpose

Close the four General Atlas acceptance conditions from the independent
H-014A / H-014A.1 QC audit:

1. Governed `geometry_reference` contract
2. Unconditional production fixture shutdown
3. Precise non-disclosure consistency on Reality lookups
4. Database-backed scan create/transition idempotency

This is a narrow security/lifecycle closure. It does **not** begin H-014B,
LiDAR capture, 3D editing, or Exterior Reality Studio.

## 1. Geometry-reference contract

Module: `backend/reality/geometry_reference.py`

Accepted stored forms only:

| Form | Meaning | When allowed |
|---|---|---|
| omitted / `null` | no geometry link | always |
| `artifact:<artifact_id>` | same-tenant, same-property artifact manifest | always (must resolve) |
| `fixture:<safe_id>` | deterministic fixture-only reference | only when fixtures enabled |

Rejected (422 `INVALID_GEOMETRY_REFERENCE` unless noted):

- HTTP/HTTPS URLs, signed URLs, bucket URLs
- absolute paths, backslashes, query strings, fragments
- traversal / encoded traversal / whitespace
- token/secret-shaped inputs
- legacy `fixture://…` URI form (not a structured application reference)
- uncontrolled storage keys (`tenant/…/reality/…`)

Cross-tenant / cross-property artifact refs → 422
(`CROSS_TENANT_GEOMETRY_REFERENCE` / `CROSS_PROPERTY_GEOMETRY_REFERENCE`).

Fixture geometry refs while fixtures disabled → 403 `FIXTURES_DISABLED`.

**Public responses** never return raw object-storage keys via
`geometry_reference`. Unsafe legacy values are redacted to
`<governed-geometry-reference>`.

Deterministic reference-room entities now store `fixture:<entity_id>`
(normalized on bootstrap).

## 2. Production fixture matrix

`fixture_provider.fixtures_enabled()` (H-014A.2):

| HABITAT_ENV | HABITAT_ENABLE_FIXTURES | Result |
|---|---|---|
| development | true | permitted |
| development | false | denied |
| demo | true | permitted |
| test | true | permitted |
| production | false | denied |
| production | true | **denied** (unconditional) |
| unknown / staging | true | **denied** (fail closed) |

Allowed non-production modes: `development`, `demo`, `test` only.

Both reference-room endpoints remain gated:

- `POST /api/reality/v1/development/reference-room/bootstrap`
- `GET /api/reality/v1/development/reference-room`

## 3. Non-disclosure route decision table

Approved response for resource-sensitive lookups:

```
404
error_code: NOT_FOUND
message: Resource not found or not accessible.
```

| Route | Resource-sensitive lookup | Non-disclosure | Legitimate exceptions |
|---|---|---|---|
| GET `/properties/{id}/spatial-graph` | property authz | 404 NOT_FOUND | 401 unauth; ref-property 403 |
| GET `/properties/{id}/coordinate-frames` | property authz | 404 NOT_FOUND | 401; ref 403 |
| GET `/coordinate-frames/{id}` | frame → property | 404 NOT_FOUND | 401 |
| GET `/scan-sessions/{id}` | scan → property | 404 NOT_FOUND | 401 |
| POST `/scan-sessions/{id}/transition` | scan load / cross-tenant | 404 NOT_FOUND | 401; same-tenant actor deny 403; 409 state/version |
| POST `/scan-sessions/{id}/artifacts` | scan load / cross-tenant | 404 NOT_FOUND | 401; 422 validation |
| GET `/artifacts/{id}` | artifact → property | 404 NOT_FOUND | 401 |
| GET `/existing-models/{id}` | model → property | 404 NOT_FOUND | 401 |
| POST `/existing-models/{id}/transition` | model load / cross-tenant | 404 NOT_FOUND | 401; 409 immutable/illegal/stale |
| GET `/design-models/{id}` | model → property | 404 NOT_FOUND | 401 |
| POST spatial-entities (truth) | n/a | n/a | **403 TRUTH_PROMOTION_FORBIDDEN** preserved |
| Reference-room when fixtures off | capability | n/a | **403 FIXTURES_DISABLED** preserved |

Executable evidence: `tests/test_h014a2_security_closure.py::TestNonDisclosureRouteMatrix`.

## 4. Scan idempotency design

### Create

Unique partial index `ux_scan_create_idempotency` on:

`tenant_id + property_id + actor_id + create_idempotency_key`

(only when `create_idempotency_key` is a string).

Concurrent duplicates collapse to one session (`DuplicateKeyError` → return original).
Another property may reuse the same external key safely.

### Transition

Collection `reality_scan_transition_idempotency` with unique index
`ux_scan_transition_idempotency` on:

`scan_session_id + idempotency_key`

Claim key after business-rule validation, before versioned update.
Replay / concurrent duplicate → one state change, no duplicate audit.

### TTL decision

`expires_at` remains a **workflow/state invalidation** field with an ordinary
index (`ix_scan_expires`). It is **not** converted to a Mongo TTL delete index.
Physical record deletion requires an approved retention policy.

## 5. Production migration status

**Not deployed to production.**

Local QC Mongo verified indexes after startup ensure:

- `ux_scan_create_idempotency` (unique partial)
- `ux_scan_transition_idempotency` (unique)
- prior non-unique `ix_scan_idempotency` dropped

Production must re-run startup index ensure (or an equivalent ops migration)
before relying on uniqueness under concurrency. No destructive backfill is
required; existing null/absent create keys are excluded by the partial filter.

## 6. Test evidence (this closure)

| Suite | Result |
|---|---|
| `test_h014a2_security_closure.py` | 60 passed |
| `test_h014a_reality.py` | 111 passed |
| H-013 security | 9 passed |
| H-013 publication + http-gates + workflow | 21 passed |
| Full backend | 281 passed, 1 skipped |

Skipped: `tests/test_design_studio.py:204` live Gemini render (`RUN_RENDER_TEST=1`).

Coverage (coverage.py 7.15.2, `--branch`, server subprocess + in-process unit):
reality package **83%** total.
