"""Governed object-store adapter for H-014B capture uploads.

Wraps the application's Emergent object-store client (`server.put_object` /
`server.get_object`) behind a small async, dependency-injectable interface so
the heavy binary sink stays:
  * non-blocking (network I/O runs in a worker thread), and
  * testable (tests monkeypatch `reality.object_store.put` / `.get`).

Governance: objects are written under the server-derived
`tenant/{tenant}/property/{property}/reality/{artifact_id}` key ONLY. No public
or permanent URLs are minted; retrieval is authorized through the backend.
Objects are treated as immutable (a 409 "already exists" is a benign no-op).
"""
import asyncio


class ObjectStoreError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


_RETRY_STATUSES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3


def _client():
    # Lazy import avoids a circular import at module load (server imports reality.router).
    from server import put_object, get_object
    return put_object, get_object


async def put(path: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
    """Store bytes at a governed key. 409 (already exists) → treated as stored (immutable).
    Transient 429/5xx and network errors are retried with a short backoff."""
    put_object, _ = _client()

    def _do():
        import time
        import requests
        last_status = 0
        for attempt in range(_MAX_ATTEMPTS):
            try:
                return put_object(path, data, content_type)
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
