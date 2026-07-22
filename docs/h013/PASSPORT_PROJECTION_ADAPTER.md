# Passport Projection Adapter (H-013 Batch 2)

**Module:** `backend/passport_projection.py`
**Status:** Implemented and tested (14 unit tests + HTTP verification via `/api/steward/context`).

## Purpose
Habitat consumes canonical property truth ONLY through a versioned, **read-only** adapter:

```
Habitat  ->  PassportProjectionAdapter  ->  authorized projection provider
```

Habitat never queries Core/Passport database collections directly and never writes canonical facts. This module is the single boundary.

## Provider modes (`HABITAT_PROJECTION_MODE`, else derived from `HABITAT_ENV`)
| Mode | Provider | Data | `authoritative` |
|---|---|---|---|
| `production` | `HttpProjectionProvider` | configured authorized endpoint | `true` |
| `development` | `DevelopmentSeedProvider` | labeled dev seed | `false` |
| `demo` | `DemoProvider` | labeled demo seed | `false` |
| `test` | `TestFixtureProvider` | deterministic fixture | `false` |

Resolution: explicit `HABITAT_PROJECTION_MODE` wins; otherwise `production` iff `HABITAT_ENV=production`, else `development`.

## Production failure behavior (implemented)
- `HttpProjectionProvider` reads `HABITAT_PROJECTION_BASE_URL` (+ optional `HABITAT_PROJECTION_API_KEY`).
- If the base URL is **unset** -> raises `ProjectionUnavailable` (HTTP **503**). **No fixture/seed/demo fallback** is ever used in production.
- Network error / timeout / non-200 / non-JSON -> `ProjectionUnavailable` (or `ProjectionValidationError`), with a simple **circuit breaker** (3 failures -> 30s open).
- Correlation ID (`X-Correlation-Id`) sent on every request. Timeout via `HABITAT_PROJECTION_TIMEOUT_SECONDS` (default 5).
- **Secrets** (`HABITAT_PROJECTION_API_KEY`) are read from server env only, never returned to the frontend and never stored in the repo. No real endpoint is configured in this environment.

## Validation (`validate_projection`) — enforced on every context read
1. `_projection` envelope present (else `SCHEMA_INVALID`).
2. `contract_version` == `CONTRACT_VERSION` (`1.0.0`) else `ContractVersionError`.
3. `tenant_id` matches requester else `TenantMismatchError` (403).
4. `property_id` matches request else `PropertyMismatchError` (409).
5. Required categories present (`property_identity`, `published_explanation`, `property_dna_projection`) else `SCHEMA_INVALID`.
6. Staleness computed (`compute_stale`) against `HABITAT_PROJECTION_STALE_SECONDS` (default 86400); sets `_projection.stale`/`stale_reason`.

Missing category via `get_projection()` returns an explicit `UNKNOWN`, `authoritative:false` stub — never fabricated.

## Steward integration
`GET /api/steward/context` calls `passport_projection.build_context("stratex-habitat", pid, correlation_id)` and maps `ProjectionError` -> the error's `status_code` + structured body. Legacy top-level keys are preserved for backward compatibility.

## Known limitations
- No real Passport/Core endpoint is wired here (none available in this environment); production mode is proven to **fail safe**, not proven against a live service.
- Response-schema validation covers required categories + envelope, not a full JSON-Schema contract.
