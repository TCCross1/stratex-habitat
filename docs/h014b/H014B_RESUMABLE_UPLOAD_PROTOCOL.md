# H014B / H-014B.1 — Resumable Governed Chunked Upload Protocol

Backend: `backend/reality/capture_upload_service.py` + `object_store.py`.
Collections: `reality_upload_sessions`, `reality_upload_chunks` (**metadata only**).

## Why chunked + resumable
LiDAR artifacts (point clouds/meshes) are large and networks are unreliable. The
protocol splits the artifact into fixed-size chunks staged in **governed object
storage**, supports resume-after-interruption, and verifies whole-file integrity
before a single immutable object is written. MongoDB never stores binary chunk
bytes or base64 copies.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/scan-sessions/{id}/uploads` | **init** — declare `artifact_type`, `checksum_sha256`, `total_size`, `chunk_size`; returns `total_chunks` + `missing_indexes`. |
| PUT | `/uploads/{uid}/chunks/{index}` | stream one chunk (raw body); optional `X-Chunk-SHA256`; identical duplicate idempotent; conflicting content → `409 CONFLICTING_CHUNK`. |
| GET | `/uploads/{uid}` | **status** — `received_indexes`, `missing_indexes`, `complete` (drives resume). |
| POST | `/uploads/{uid}/complete` | ordered disk-backed assemble from object storage → verify SHA-256 → PUT final object → create manifest; mark staging for cleanup. |
| POST | `/uploads/{uid}/abort` | mark aborted; mark staging for cleanup; metadata purge; abort replay idempotent. |
| GET | `/artifacts/{aid}/content` | authorized, backend-mediated download (no public URL). |

## H-014B.1 storage-boundary correction
MongoDB `reality_upload_chunks` stores **metadata only**:
upload session / tenant / property / scan / artifact IDs, chunk index, declared
and verified checksums, declared/verified size, opaque object reference (`orf-…`),
etag/receipt, upload/retry state, timestamps, ownership, lineage, expiration and
audit refs. Internal `_storage_key_internal` is never returned by API responses.

Governed object storage stores:
actual binary chunks (tenant/property-scoped staging keys), RoomPlan files,
LiDAR data, meshes, point clouds, images, USDZ/other capture artifacts, and the
completed final artifact object.

Required behaviors:
1. Auth + tenant/property authorization before upload (router).
2. Validate chunk index, size, and SHA-256.
3. Stream each chunk directly into a scoped staging object.
4. Store only metadata + opaque reference in MongoDB.
5. Identical duplicate chunks are idempotent.
6. Same index with different content is rejected (`409 CONFLICTING_CHUNK`).
7. Resume reports precise `missing_indexes`.
8. Completion verifies all chunks and whole-file checksum.
9. Never load a complete large artifact into MongoDB.
10. Avoid unbounded whole-file memory buffering (tempfile-backed assemble).
11. Provider multipart/compose used when available; otherwise ordered disk-backed streaming.
12. Never expose bucket names, raw object keys, credentials, public URLs, or signed URLs through API responses.
13. Fake/development providers are impossible in production (`HABITAT_ENV=production`).
14. Abandoned staging objects are marked for governed lifecycle cleanup; deletion is never fabricated.
15. Non-production cleanup utility: `python -m reality.cleanup_binary_chunk_docs --confirm-database <DB_NAME>` (refuses production; never auto-runs).

## Governance & integrity
- **Server-derived ownership:** tenant is server-derived; property is the
  authorized scan-session property. The final object key is
  `tenant/{tenant}/property/{property}/reality/{artifact_id}` (client cannot set it).
- **Chunk validation:** non-final chunk must equal `chunk_size`; final chunk must
  equal `total_size − chunk_size·(n−1)`; empty/oversized chunks rejected.
  `chunk_size` cap 8 MiB (governed staging cap); upload cap 2 GiB; ≤ 4096 chunks.
- **Whole-file checksum:** on complete, chunks are streamed in index order from
  object storage, size and SHA-256 verified against the declared manifest checksum.
  A mismatch → `422 CHECKSUM_MISMATCH` (audited `REALITY_UPLOAD_CHECKSUM_MISMATCH`),
  the session stays resumable.
- **Object store:** final immutable PUT via `object_store.put` (async, 429/5xx +
  network retry with backoff; 409 "already exists" treated as stored). A persistent
  store failure → `502 OBJECT_STORE_UNAVAILABLE` (retryable). Manifest
  `storage_object_reference` masked in the public view.
- **Idempotency:** `complete` on a COMPLETED session replays the manifest; `abort`
  on an ABORTED session replays; a deterministic `artifact_id` (dev proof)
  short-circuits if the manifest exists. Upload-session create idempotency and
  chunk `(session,index)` uniqueness are database-enforced.

## Client (iOS `ResumableUploader`)
4 MiB chunks, per-chunk SHA-256, exponential backoff per chunk, queries
`uploadStatus` to resend only missing indexes, retries `complete` on transient 502.

## Tests
`TestResumableUploadHTTP` + `TestStorageBoundaryHTTP` +
`tests/test_h014b1_storage_boundary.py`: MongoDB metadata-only, scoped object
refs, duplicate/conflict, missing indexes, checksum mismatches, completion/abort
replay, provider production gate, cleanup production gate, no key/URL leakage,
Guardian/DRAFT_CANDIDATE truth boundary.
