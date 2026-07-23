# H014B Phase 6 — Resumable Governed Chunked Upload Protocol

Backend: `backend/reality/capture_upload_service.py` + `object_store.py`.
Collections: `reality_upload_sessions`, `reality_upload_chunks`.

## Why chunked + resumable
LiDAR artifacts (point clouds/meshes) are large and networks are unreliable. The
protocol splits the artifact into fixed-size chunks staged server-side, supports
resume-after-interruption, and verifies whole-file integrity before a single
immutable object is written to governed object storage.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/scan-sessions/{id}/uploads` | **init** — declare `artifact_type`, `checksum_sha256`, `total_size`, `chunk_size`; returns `total_chunks` + `missing_indexes`. |
| PUT | `/uploads/{uid}/chunks/{index}` | stream one chunk (raw body); optional `X-Chunk-SHA256`; idempotent per index. |
| GET | `/uploads/{uid}` | **status** — `received_indexes`, `missing_indexes`, `complete` (drives resume). |
| POST | `/uploads/{uid}/complete` | assemble in order → verify SHA-256 → PUT final object → create manifest. |
| POST | `/uploads/{uid}/abort` | discard staged chunks. |
| GET | `/artifacts/{aid}/content` | authorized, backend-mediated download (no public URL). |

## Governance & integrity
- **Server-derived ownership:** tenant is server-derived; property is the
  authorized scan-session property. The final object key is
  `tenant/{tenant}/property/{property}/reality/{artifact_id}` (client cannot set it).
- **Chunk validation:** non-final chunk must equal `chunk_size`; final chunk must
  equal `total_size − chunk_size·(n−1)`; empty/oversized chunks rejected.
  `chunk_size` cap 8 MiB (< 16 MB BSON limit); upload cap 2 GiB; ≤ 4096 chunks.
- **Whole-file checksum:** on complete, chunks are concatenated in index order,
  the size and SHA-256 are verified against the declared manifest checksum.
  A mismatch → `422 CHECKSUM_MISMATCH` (audited `REALITY_UPLOAD_CHECKSUM_MISMATCH`),
  the session stays resumable (chunks retained for re-upload).
- **Object store:** single immutable PUT via `object_store.put` (async, 429/5xx +
  network retry with backoff; 409 "already exists" treated as stored). A persistent
  store failure → `502 OBJECT_STORE_UNAVAILABLE` (retryable), integrity already
  verified. On success, staged chunks are purged; manifest `object_stored=True`,
  `storage_object_reference` masked in the public view.
- **Idempotency:** `complete` on a COMPLETED session replays the manifest; a
  deterministic `artifact_id` (dev proof) short-circuits if the manifest exists.

## Client (iOS `ResumableUploader`)
4 MiB chunks, per-chunk SHA-256, exponential backoff per chunk, queries
`uploadStatus` to resend only missing indexes, retries `complete` on transient 502.

## Tests
`TestResumableUploadHTTP`: happy path, **resume-missing-chunk**, checksum mismatch,
chunk-size mismatch, invalid chunk-size at init. Plus authorized content
round-trip (`sha256` of downloaded bytes == declared checksum).
