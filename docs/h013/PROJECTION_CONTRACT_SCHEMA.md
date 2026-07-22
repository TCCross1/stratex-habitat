# Projection Contract Schema (H-013 Batch 2)

**Contract version:** `1.0.0` (`HABITAT_PROJECTION_CONTRACT_VERSION`)
**Defined in:** `backend/passport_projection.py`

## Envelope: `_projection`
| Field | Meaning |
|---|---|
| `contract_version` | Projection contract version (must equal adapter `CONTRACT_VERSION`) |
| `provider_mode` | production / development / demo / test |
| `tenant_id` | Owning tenant |
| `property_id` | Property the projection describes |
| `authoritative` | `true` only in production; `false` for dev/demo/test |
| `fixture_or_seed_identifier` | Seed/fixture id for non-production payloads |
| `generated_at` | ISO-8601 generation timestamp |
| `correlation_id` | Request correlation id |
| `authorization_scope` | Scope string for the read |
| `stale` / `stale_reason` | Computed freshness state |

## Per-item projection metadata (`_meta`)
Each projected category item carries both legacy H-012 fields and contract fields:

| Legacy field | Contract field |
|---|---|
| `source_system` | `projection_id` |
| `source_id` | `projection_version` |
| `version` | `publication_state` (PUBLISHED / UNPUBLISHED / PROJECTED / UNKNOWN) |
| `truth_classification` | `confidence` (HIGH / MEDIUM / LOW / null) |
| `timestamp` | `generated_at`, `effective_at` |
| `authorization_scope` | `canonical_reference_ids[]` |

## Truth classifications (preserved end-to-end)
`VERIFIED`, `ESTIMATED`, `PROJECTED`, `HOMEOWNER_REPORTED`, `SUGGESTED`, `UNKNOWN`.

## Roof-slice projection categories
`property_identity`, `published_explanation` (published roof explanation), `property_dna_projection`, `timeline_entries` (Living Timeline), `warranty_metadata`, `approved_roof_geometry`, `document_metadata`. (`seasonal_context` and `active_roof_projects` are also returned for the Steward UI.)

**Required for a valid context:** `property_identity`, `published_explanation`, `property_dna_projection`.

## Example (development mode, abbreviated)
```json
{
  "_projection": {"contract_version":"1.0.0","provider_mode":"development",
    "tenant_id":"stratex-habitat","property_id":"<pid>","authoritative":false,
    "fixture_or_seed_identifier":"dev-seed-roof-2026.07","generated_at":"...",
    "stale":false},
  "property_identity": {"name":"Villa Horizon","truth_classification":"VERIFIED",
    "publication_state":"PUBLISHED","projection_id":"proj-identity", ...},
  "published_explanation": { ... },
  "property_dna_projection": { "truth_classification":"PROJECTED", ... }
}
```
