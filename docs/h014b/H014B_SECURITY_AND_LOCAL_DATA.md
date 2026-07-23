# H014B Phases 10–11 — Security & Local Data Protection

## On-device (native module)
`ios/StratexRealityCapture/SecureLocalStore.swift`:
- All staged capture files written with **`.completeFileProtection`** (encrypted at
  rest; unavailable while the device is locked).
- Staging directory lives under Application-Support and is **excluded from
  iCloud/iTunes backup** (`isExcludedFromBackup`).
- **`purge(scanSessionId:)`** deletes local copies immediately after the governed
  upload completes (called by `CaptureFlowController`), so sensitive interior
  geometry/imagery does not linger. `purgeStale(olderThan:)` reaps abandoned captures.
- Camera/LiDAR gated by `NSCameraUsageDescription`; no analytics/third-party SDKs.

## In transit
- HTTPS only, via `URLSession`. Auth by JWT (cookie or `Bearer`).
- Per-chunk `X-Chunk-SHA256` + whole-file SHA-256 verified server-side before the
  object is persisted (`H014B_RESUMABLE_UPLOAD_PROTOCOL.md`).

## Backend / at rest
- Object keys are **server-derived** (`tenant/{tenant}/property/{property}/reality/{artifact_id}`);
  clients cannot set or read the raw key. `public_view` masks
  `storage_object_reference` → `<governed-object-store-reference>`.
- Manifests set `encryption_state = ENCRYPTED_AT_REST`, `signed_access_required = true`.
- **No public/permanent/presigned URLs.** Retrieval is authorized on every request
  via `GET /artifacts/{aid}/content` (property authorization enforced; 502 if the
  store is unavailable, never a leaked URL).
- Audit events are sanitized: prohibited keys (`data`, `bytes`, `payload`, `image`,
  `token`, `signed_url`, `password`, `authorization`, `secret`, …) are stripped;
  events carry only safe references + correlation ids.
- Tenant isolation + uniform 404 non-disclosure inherited from H-014A; cross-tenant
  scan/upload access is rejected.
- Upload sessions carry a TTL (`expires_at`, 72h) and staged chunks are deleted on
  completion/abort.

## Truth & governance
Capture never self-promotes beyond `MEASURED_EXISTING` / `DRAFT_CANDIDATE`.
Restricted truth classes fail closed (`TRUTH_PROMOTION_FORBIDDEN`). Dev proof data
is tagged `authoritative:false` and isolated on a synthetic property.
