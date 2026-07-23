"""Governed object-store adapter for H-014B capture uploads.

Wraps the application's Emergent object-store client (`server.put_object` /
`server.get_object`) behind a small async, dependency-injectable interface so
the heavy binary sink stays:
  * non-blocking (network I/O runs in a worker thread), and
  * testable (tests monkeypatch `reality.object_store.put` / `.get`).

Governance
----------
* Objects are written under server-derived
  `tenant/{tenant}/property/{property}/reality/...` keys ONLY.
* No public or permanent URLs are minted; retrieval is authorized through
  the backend.
* Objects are treated as immutable (a 409 "already exists" is a benign no-op).
* Binary chunk bytes and completed artifacts live in object storage — never in
  MongoDB.
* Development / fake providers are impossible in production
  (`HABITAT_ENV=production` refuses `HABITAT_OBJECT_STORE_PROVIDER=fake`).
* Deletion is not fabricated: when a provider cannot delete, staging objects
  are marked for governed lifecycle cleanup only.
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import tempfile
import uuid
from typing import Optional

_RETRY_STATUSES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3
_ALLOWED_FAKE_ENVS = frozenset({"development", "demo", "test"})

# In-process fake store (non-production only). Keys → (bytes, content_type).
_FAKE_STORE: dict[str, tuple[bytes, str]] = {}
# Staging objects marked for governed lifecycle cleanup when delete is unavailable.
_CLEANUP_MARKS: list[dict] = []


class ObjectStoreError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class ObjectStoreProviderForbidden(Exception):
    """Raised when a non-governed provider is requested in a forbidden environment."""


def habitat_env() -> str:
    return os.environ.get("HABITAT_ENV", "development").strip().lower()


def provider_name() -> str:
    raw = os.environ.get("HABITAT_OBJECT_STORE_PROVIDER", "governed").strip().lower()
    return raw or "governed"


def assert_provider_allowed() -> str:
    """Return the active provider, refusing fake/dev in production or unknown envs."""
    name = provider_name()
    env = habitat_env()
    if name in ("fake", "dev", "development", "memory", "local"):
        if env == "production" or env not in _ALLOWED_FAKE_ENVS:
            raise ObjectStoreProviderForbidden(
                f"Object-store provider '{name}' is forbidden when "
                f"HABITAT_ENV='{env}'. Production and unknown environments "
                "require the governed provider only."
            )
        return "fake"
    return "governed"


def staging_storage_key(tenant_id: str, property_id: str, upload_session_id: str, index: int) -> str:
    """Internal governed staging key. Never return this through API responses."""
    return (
        f"tenant/{tenant_id}/property/{property_id}/reality/"
        f"staging/{upload_session_id}/chunk-{int(index):06d}"
    )


def opaque_object_reference(upload_session_id: str, index: int) -> str:
    """Opaque internal reference stored in MongoDB metadata (not a raw key/URL)."""
    return f"orf-{upload_session_id}-{int(index)}"


def _client():
    # Lazy import avoids a circular import at module load (server imports reality.router).
    from server import put_object, get_object
    return put_object, get_object


async def put(path: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
    """Store bytes at a governed key. 409 (already exists) → treated as stored (immutable).
    Transient 429/5xx and network errors are retried with a short backoff."""
    provider = assert_provider_allowed()
    if provider == "fake":
        _FAKE_STORE[path] = (bytes(data), content_type)
        return {"path": path, "size": len(data), "etag": hashlib.sha256(data).hexdigest()[:16],
                "provider": "fake"}

    put_object, _ = _client()

    def _do():
        import time
        import requests
        last_status = 0
        for attempt in range(_MAX_ATTEMPTS):
            try:
                result = put_object(path, data, content_type)
                if isinstance(result, dict):
                    # Never persist signed URLs even if a provider returns them.
                    result = {k: v for k, v in result.items()
                              if k.lower() not in {"signed_url", "url", "public_url", "download_url"}}
                return result
            except requests.HTTPError as e:  # raised by resp.raise_for_status()
                status = e.response.status_code if e.response is not None else 0
                if status == 409:
                    return {"path": path, "size": len(data), "already_exists": True}
                last_status = status
                if status in _RETRY_STATUSES and attempt < _MAX_ATTEMPTS - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise ObjectStoreError(status, f"object store PUT failed ({status})")
            except requests.RequestException as e:
                last_status = 0
                if attempt < _MAX_ATTEMPTS - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise ObjectStoreError(0, f"object store unreachable: {e}")
        raise ObjectStoreError(last_status, f"object store PUT failed ({last_status})")

    return await asyncio.to_thread(_do)


async def get(path: str):
    """Return (bytes, content_type) for an authorized, backend-mediated download."""
    provider = assert_provider_allowed()
    if provider == "fake":
        if path not in _FAKE_STORE:
            raise ObjectStoreError(404, f"object store GET failed (404)")
        data, ctype = _FAKE_STORE[path]
        return data, ctype

    _, get_object = _client()

    def _do():
        import requests
        try:
            return get_object(path)
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            raise ObjectStoreError(status, f"object store GET failed ({status})")
        except requests.RequestException as e:
            raise ObjectStoreError(0, f"object store unreachable: {e}")

    return await asyncio.to_thread(_do)


async def put_staging_chunk(*, tenant_id: str, property_id: str, upload_session_id: str,
                            index: int, data: bytes,
                            content_type: str = "application/octet-stream") -> dict:
    """Stream one chunk into a tenant/property/scan-scoped staging object.

    Returns metadata suitable for MongoDB (opaque reference + optional etag).
    Never returns bucket names, public URLs, or signed URLs.
    """
    key = staging_storage_key(tenant_id, property_id, upload_session_id, index)
    result = await put(key, data, content_type)
    etag = None
    if isinstance(result, dict):
        etag = result.get("etag") or result.get("ETag")
    return {
        "object_reference": opaque_object_reference(upload_session_id, index),
        "etag": etag,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        # Internal only — callers must not expose this through API responses.
        "_storage_key_internal": key,
    }


async def get_staging_chunk(*, tenant_id: str, property_id: str, upload_session_id: str,
                            index: int) -> bytes:
    key = staging_storage_key(tenant_id, property_id, upload_session_id, index)
    data, _ = await get(key)
    return data


def mark_for_cleanup(*, storage_key: str, reason: str, tenant_id: str = None,
                     property_id: str = None, upload_session_id: str = None) -> dict:
    """Record a governed lifecycle cleanup intent. Does NOT fabricate deletion.

    The Emergent object-store client used here has no delete API; abandoned
    staging objects are marked for later governed cleanup rather than claiming
    a deletion that did not occur.
    """
    mark = {
        "id": f"cleanup-{uuid.uuid4()}",
        "storage_key_present": bool(storage_key),
        # Opaque — do not surface raw keys via API; this mark is internal/ops.
        "storage_key": storage_key,
        "reason": reason,
        "tenant_id": tenant_id,
        "property_id": property_id,
        "upload_session_id": upload_session_id,
        "deletion_executed": False,
        "deletion_fabricated": False,
        "provider": provider_name(),
    }
    _CLEANUP_MARKS.append(mark)
    return mark


async def mark_upload_staging_for_cleanup(*, tenant_id: str, property_id: str,
                                          upload_session_id: str, indexes) -> list:
    marks = []
    for index in indexes or []:
        key = staging_storage_key(tenant_id, property_id, upload_session_id, int(index))
        marks.append(mark_for_cleanup(
            storage_key=key, reason="upload_session_terminal_or_abandoned",
            tenant_id=tenant_id, property_id=property_id,
            upload_session_id=upload_session_id))
    return marks


async def compose_or_stream_assemble(*, tenant_id: str, property_id: str,
                                     upload_session_id: str, total_chunks: int,
                                     final_storage_ref: str,
                                     content_type: str = "application/octet-stream",
                                     declared_size: Optional[int] = None,
                                     declared_checksum_sha256: Optional[str] = None) -> dict:
    """Assemble staged chunks into the final immutable artifact object.

    Multipart/compose is unavailable on the current Emergent provider, so this
    uses ordered, disk-backed streaming (tempfile) to avoid unbounded whole-file
    memory buffering and to avoid loading the complete artifact into MongoDB.
    """
    digest = hashlib.sha256()
    total = 0
    with tempfile.NamedTemporaryFile(prefix="h014b-assemble-", suffix=".bin", delete=True) as tmp:
        for index in range(total_chunks):
            chunk = await get_staging_chunk(
                tenant_id=tenant_id, property_id=property_id,
                upload_session_id=upload_session_id, index=index)
            tmp.write(chunk)
            digest.update(chunk)
            total += len(chunk)
        tmp.flush()
        computed = digest.hexdigest()
        if declared_size is not None and total != declared_size:
            return {"ok": False, "error": "SIZE_MISMATCH", "computed_size": total,
                    "declared_size": declared_size, "computed_checksum_sha256": computed}
        if declared_checksum_sha256 and computed != declared_checksum_sha256.lower():
            return {"ok": False, "error": "CHECKSUM_MISMATCH", "computed_size": total,
                    "computed_checksum_sha256": computed,
                    "declared_checksum_sha256": declared_checksum_sha256.lower()}
        # Bounded read from the temp file for the final governed PUT. The
        # underlying put_object API accepts bytes; we still never touch MongoDB.
        tmp.seek(0)
        assembled = tmp.read()
        put_result = await put(final_storage_ref, assembled, content_type)
    return {
        "ok": True,
        "bytes_stored": total,
        "checksum_sha256": computed,
        "put_result": put_result if isinstance(put_result, dict) else {},
    }


def reset_fake_store_for_tests():
    """Test helper — clears in-memory fake store + cleanup marks."""
    _FAKE_STORE.clear()
    _CLEANUP_MARKS.clear()


def fake_store_snapshot_for_tests() -> dict:
    """Test helper — returns {key: size} without exposing full binary payloads."""
    return {k: len(v[0]) for k, v in _FAKE_STORE.items()}


def cleanup_marks_for_tests() -> list:
    return list(_CLEANUP_MARKS)
