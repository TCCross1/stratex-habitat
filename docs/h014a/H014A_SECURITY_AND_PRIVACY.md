# H-014A — Security & Privacy

Sources: `backend/reality/authz.py`, `audit_service.py`, `artifact_service.py`,
and reused H-013 auth (`backend/steward.py`).

## Authentication
Reuses the accepted H-013 auth: `get_steward_user` (JWT via httpOnly cookie or Bearer, tenant
restricted to the demo homeowner `alex@stratexhabitat.com`) + privileged roles
(`executive`, `broker_admin`, `reviewer`). Unauthenticated requests → **401**.

## Tenant isolation
- `TENANT_ID` is a single server-derived value; `server_tenant_id()` **ignores any client-supplied
  tenant**. It is used to derive the artifact storage reference (Phase 1).
- Records are always written with the server tenant and the authorized property; cross-tenant
  scan access → `SCAN_ACCESS_DENIED` (403); cross-tenant relationships → `CROSS_TENANT_RELATIONSHIP`;
  cross-tenant model access → `MODEL_ACCESS_DENIED`.

## Property authorization (`authorize_property`)
- Reference property `ref-property-h014a`: demo homeowner or privileged roles only, else **403**.
- Real property: privileged roles allowed; owner match required (`owner_id == user.id`);
  contractors are denied (no per-job grant model in H-014A); missing property → **404**
  (non-disclosure, not 403).

## Truth-promotion guard (`assert_truth_promotion_allowed`) — fail closed
Habitat-only actors can never self-promote to `RESTRICTED_TRUTH_CLASSES`
(`VERIFIED_EXISTING`, `PROFESSIONALLY_REVIEWED_DESIGN`, `APPROVED_FOR_BUILD_PACKAGE`,
`COMPLETED_AS_BUILT`) → **403 `TRUTH_PROMOTION_FORBIDDEN`**. There is no Core/Passport/professional
authorization channel in H-014A, so these promotions fail closed by design (unit + HTTP tested).

## Artifact / imagery privacy (Phase 1 focus)
- Manifests store metadata only; binary lives in governed object storage.
- Default storage reference is derived from **authenticated tenant + authorized property +
  server-generated artifact id** — never a fixture/demo tenant literal, client override, URL,
  credential, signed URL, or unrestricted bucket path.
- Client-supplied references are validated (`validate_storage_reference`): blank / URL / absolute
  path / query / traversal → `INVALID_STORAGE_REFERENCE`.
- `public_view` masks the raw key to `"<governed-object-store-reference>"`; tests assert the raw
  key never appears in any response body.
- Restricted imagery (`RAW_RGB`, `RAW_THERMAL`, `PANORAMA`) → `access_classification:
  RESTRICTED_IMAGERY`; all artifacts `signed_access_required: true`, `encryption_state:
  ENCRYPTED_AT_REST`.

## Audit hygiene (`audit_service._sanitize`)
Immutable events in `db.audit_events` (`domain: "reality"`) carry actor, correlation id, safe
entity references and states only. A prohibited-key allow-list strips `data`, `bytes`, `payload`,
`image`, `token`, `access_token`, `signed_url`, `password`, `password_hash`, `authorization`,
`secret` — no binary, imagery, secrets, or signed URLs are ever logged.

## Governance boundaries honored
- **No direct Passport write path** — `canonical_passport_reference` is a read-only reference field
  only; nothing in `reality/` writes to Passport.
- **No duplicate readiness/publication authority** — H-014A adds no publication gate; the accepted
  single governed publication path (H-013 workflow) is untouched.
