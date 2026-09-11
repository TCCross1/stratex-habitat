# STRATEX TEST AND BUILD EVIDENCE

All commands in this document were executed directly, in this session, inside
`/home/runner/work/stratex-habitat/stratex-habitat` on commit
`6eeb7605a379f5954c7343909eaede57cfc0ea8b`. Where an independent re-run was not
possible (no network, no macOS host, etc.), that limitation is stated
explicitly — no result is inferred or assumed.

## 1. Backend dependency install

```
$ cd backend && pip install -r requirements.txt
...
ERROR: Could not find a version that satisfies the requirement emergentintegrations==0.2.0
ERROR: No matching distribution found for emergentintegrations==0.2.0
```

**Result: FAILS as-authored.** `emergentintegrations==0.2.0` is a private/non-PyPI
package (confirmed by the repo's own CI workflow comment,
`.github/workflows/backend-reality.yml:44-47`: *"private/non-PyPI package used
only by the optional live Gemini render path... Public GitHub Actions cannot
install it"*). All 27 other pinned dependencies installed cleanly on Python
3.12. Excluding that one line (exactly as the project's own CI does) produces
a clean, fully successful install.

## 2. Backend unit/integration test suite — independently reproduced

The suite in `backend/tests/` (16 files) is an **HTTP integration suite**
(`backend/tests/conftest.py`) that requires a live MongoDB and a running
`uvicorn` process — it is not a mocked/in-process unit suite. To get a real
result, this session stood up the exact CI topology
(`.github/workflows/backend-reality.yml`):

```
$ docker run -d --name habitat-ci-mongo -p 27017:27017 mongo:7.0
$ REACT_APP_BACKEND_URL=http://127.0.0.1:8001 MONGO_URL=mongodb://127.0.0.1:27017 \
  DB_NAME=habitat_ci JWT_SECRET=ci-h014b2-jwt-secret-not-for-production \
  HABITAT_ENV=test HABITAT_ENABLE_FIXTURES=true HABITAT_OBJECT_STORE_PROVIDER=fake \
  CORS_ORIGINS=* uvicorn server:app --host 127.0.0.1 --port 8001 --workers 1 &
backend ready after 4s

$ python -m pytest tests/ -rs -q
........................................................................ [ 21%]
........................................................................ [ 42%]
........................................................................ [ 63%]
........................................................................ [ 84%]
.....................................s.............                      [100%]
SKIPPED [1] tests/test_design_studio.py:204: Skip live Gemini render unless RUN_RENDER_TEST=1
338 passed, 1 skipped, 3 warnings in 8.19s
```

**Result: PASS — 338 passed, 1 skipped, 0 failed** (independently reproduced,
not copied from `test_result.md`). The 1 skip is an intentionally gated live
Gemini AI render test (`RUN_RENDER_TEST=1` not set) — a real external LLM call,
correctly excluded from default CI. This is a materially larger count than the
last self-reported figure in `test_result.md` (`281 passed / 1 skipped` at
H-014A.2), consistent with additional H-014B/B.3/C tests added since. The
self-reported historical counts in `test_result.md` are therefore plausible
and directionally consistent with what this session verified live, but they
were **not independently reproducible from those earlier commits** in this
audit (only HEAD was tested) — treat historical pass counts in `test_result.md`
as unverified secondary evidence, and the `338 passed` figure above as the
only primary evidence in this report.

A first-startup log line is notable and was captured directly:
```
ERROR - Storage init failed: ... Failed to resolve 'integrations.emergentagent.com'
```
This confirms `backend/server.py`'s object-storage client unconditionally
attempts to reach a real external managed-storage endpoint
(`https://integrations.emergentagent.com/objstore/api/v1/storage`) at startup
regardless of the `HABITAT_OBJECT_STORE_PROVIDER=fake` env var used by CI/this
test run — it fails soft (logs and continues) rather than crashing, but it is
evidence of an unmanaged external dependency at boot (see technical report §9).

## 3. Backend coverage (reality package)

```
$ python -m pytest tests/ -q --cov=reality --cov-report=term-missing --cov-fail-under=0 -n 0
TOTAL   1862   945   49%
338 passed, 1 skipped, 2 warnings in 8.19s
```

Process-local coverage of the `reality/` package is **49%**, matching the
CI workflow's own documented expectation that "plain pytest --cov against a
separate uvicorn measures ~49% process-local" (`backend-reality.yml:12-14`).
CI's authoritative ≥83% figure requires combining this run with a
coverage-instrumented `uvicorn` subprocess plus a second in-process unit run —
that combination was **not reproduced in this session** (time-boxed); the 49%
process-local number above is the only coverage figure this audit can attest
to first-hand. Modules at 0% in the process-local run: `reality/router.py`,
`reality/schemas.py`, `reality/indexes.py`, `reality/capture_proof.py` (these
are exercised only via the HTTP layer inside the separate uvicorn process,
which process-local `--cov` cannot attribute to).

## 4. Frontend dependency install / build

```
$ cd frontend && yarn install
...
error Error: getaddrinfo ENOTFOUND assets.emergent.sh
```

**Result: BLOCKED — no network access to the required package/asset host in
this sandbox.** `yarn build` / `craco build` were **not attempted** because
install did not complete; no frontend build result can be reported. This is
an environment limitation, not a code defect, but it means the frontend build
could not be independently validated in this audit.

Frontend automated tests: only 2 Jest test files exist
(`frontend/src/propertyVisualization/__tests__/PropertyVisualization.test.js`,
`frontend/src/components/__tests__/Inspector.test.js`); neither could be run
(same install blocker). Prior UI verification evidence in this repo is
screenshot/JSON-based manual-agent testing under `test_reports/` (e.g.
`test_reports/h014b1_browser/report.json`), not an automated CI-gated test
run.

## 5. Lint / static analysis

```
$ find backend frontend -maxdepth 3 \( -name ".eslintrc*" -o -name "eslint.config.*" \
  -o -name "ruff.toml" -o -name "pyproject.toml" -o -name ".flake8" \
  -o -name "mypy.ini" -o -name "tsconfig.json" \)
(no results)
$ rg "\"eslintConfig\"|\"lint\"|\"ruff\"|\"flake8\"|\"mypy\"" backend frontend
(no results)
```

**Result: no lint/type-check configuration or script exists** in either
`backend/` or `frontend/`, despite `black`, `isort`, `flake8`, and `mypy` all
being listed in `backend/requirements.txt` (lines 22-25) — they are installed
dependencies with **no invoked configuration, no CI step, and no committed
config file**. This is a gap: linting/type-checking tooling is present as a
dependency but not wired into any enforceable gate.

## 6. Security / static-analysis checks

No SAST/dependency-scanning tool (e.g. `bandit`, `safety`, `pip-audit`,
`npm audit` in CI, CodeQL workflow) is configured in `.github/workflows/`
(only `backend-reality.yml` and `ios-capture.yml` exist, both functional/unit
test workflows, not security scans). No security-scan evidence exists to
report beyond what this audit's own tooling produces separately.

## 7. Existing CI-equivalent commands — reproduced results

| Workflow | Trigger scope | This session's result |
|---|---|---|
| `backend-reality.yml` | push/PR touching `backend/**` | **Reproduced.** 338 passed / 1 skipped / 0 failed (§2 above); coverage combine step not reproduced (§3). |
| `ios-capture.yml` | push/PR touching `ios/**` | **Not reproducible in this environment** — requires `macos-latest` GitHub runner with Xcode/Swift/iOS Simulator SDK; no macOS host is available here. Per the workflow's own scope (`ios-capture.yml:1-11`), even a successful run only proves the Swift package **compiles** for the iOS Simulator SDK and passes portable (non-hardware) Guardian unit tests — it explicitly does **not** exercise physical LiDAR capture (`ios-capture.yml:9-11`: *"This is NOT physical LiDAR execution (still UNEXECUTED)"*). |

## 8. Summary pass/fail table

| Check | Status | Evidence |
|---|---|---|
| Backend dependency install (as pinned) | **FAIL** (1 unreachable private package) | §1 |
| Backend dependency install (CI's exclusion method) | **PASS** | §1 |
| Backend integration test suite | **PASS** — 338 passed, 1 skipped, 0 failed | §2 |
| Backend `reality` package coverage (process-local) | 49% (informational; CI's authoritative combined gate is ≥83%, not reproduced) | §3 |
| Frontend dependency install | **BLOCKED** (no network to `assets.emergent.sh`) | §4 |
| Frontend build | **NOT RUN** (blocked by above) | §4 |
| Frontend automated tests | **NOT RUN** (blocked by above) | §4 |
| Backend lint/type-check | **NOT CONFIGURED** (tools installed, unused) | §5 |
| Security/SAST scanning | **NOT CONFIGURED** | §6 |
| `ios-capture.yml` (Swift build/test) | **NOT REPRODUCIBLE HERE** (needs macOS); by design never proves physical capture | §7 |
