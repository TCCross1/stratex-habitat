# H-013 Backend Runtime Repair & Dependency Audit (Wave 1 — Phase 2)

**Generated:** 2026-07-22
**Mission priority:** #1 Restore backend startup / #2 Dependency audit

---

## 1. Reported crash (CONTEXT)

```
AttributeError: module 'lib' has no attribute 'GEN_EMAIL'
```

Reported environment:
- Python **3.12**
- motor / pymongo loaded from `/home/runner/.local/lib/python3.12/site-packages`
- pyOpenSSL loaded from `/usr/lib/python3/dist-packages/OpenSSL`

`/home/runner/...` is the **GitHub Actions runner** path — i.e. this crash occurs in **CI**, not in the Emergent preview/runtime container.

## 2. Root cause

`AttributeError: module 'lib' has no attribute 'GEN_EMAIL'` is the classic symptom of an **old `pyOpenSSL` being imported against a too-new `cryptography`**. Modern `cryptography` removed the legacy `_lib.GEN_EMAIL` binding that old `pyOpenSSL` (`< 23`) referenced at import time.

In CI, `pymongo` performs a lazy `import OpenSSL` (TLS/OCSP support). Because a **stale distro `pyOpenSSL`** sat in the system `dist-packages` while a **new `cryptography`** was installed to the user site, the import blew up during backend startup.

## 3. Emergent runtime state (THIS container) — verified healthy

| Item | Value |
|---|---|
| Python | 3.11 (`/root/.venv`) |
| MONGO_URL scheme | `mongodb://localhost:27017` (**no TLS**) |
| pyOpenSSL (before fix) | **not installed** |
| Backend startup | `Application startup complete` |
| `GET /api/` | **HTTP 200** `{"service":"STRATEX HABITAT","status":"online"}` |

Because the local Mongo connection is plain (non-TLS), `pymongo` never imports `pyOpenSSL` here, so **the `GEN_EMAIL` crash cannot occur in this container.** No live outage — the priority-#1 work is a CI/dependency-pinning fix.

## 4. Declared vs installed dependency versions (audit)

| Package | Declared (before) | Installed (before) | Declared (after) | Installed (after) |
|---|---|---|---|---|
| Python | — | 3.11 | — | 3.11 |
| motor | `==3.3.1` | 3.3.1 | `==3.3.1` | 3.3.1 |
| pymongo | `==4.6.3` | 4.6.3 | `==4.6.3` | 4.6.3 |
| fastapi | `==0.110.1` | 0.110.1 | `==0.110.1` | 0.110.1 |
| uvicorn | `==0.25.0` | 0.25.0 | `==0.25.0` | 0.25.0 |
| cryptography | `>=42.0.8` (→ 49.0.0) | 49.0.0 | **`==44.0.1`** | 44.0.1 |
| pyOpenSSL | (undeclared) | absent | **`==25.1.0`** | 25.1.0 |

## 5. Fix applied

`backend/requirements.txt`:

```diff
- cryptography>=42.0.8
+ cryptography==44.0.1
+ pyOpenSSL==25.1.0
```

**Why this pair:** `pyOpenSSL 25.1.0` supports `cryptography >=41.0.5,<=45.0.x`. Pinning a **modern** `pyOpenSSL` guarantees that in CI a compatible `OpenSSL` is installed to the user site and **shadows the stale distro copy**, eliminating the `GEN_EMAIL` import error. `cryptography==44.0.1` sits inside pyOpenSSL's supported ceiling, so pip resolves the pair with no conflict.

### Validation
- `pip install --dry-run cryptography==44.0.1 pyOpenSSL==25.1.0` → resolves cleanly (no conflicts).
- Installed into the venv: `import cryptography, OpenSSL` succeeds together (no `GEN_EMAIL`).
- Backend restarted: `Application startup complete`, `GET /api/` → **HTTP 200**. Live runtime remains healthy.

## 6. Recommendation for CI

Ensure CI installs backend deps from the pinned `backend/requirements.txt` into an isolated environment (venv / clean user site) so the pinned modern `pyOpenSSL` takes precedence over any distro `python3-openssl`. On Python 3.12 this pinned pair also resolves cleanly.
