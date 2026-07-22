# H-014A — Test & Coverage Report

Test file: `backend/tests/test_h014a_reality.py` (fixtures: `backend/tests/conftest.py`).
Runner: pytest 8 + pytest-xdist (2 workers, `loadscope`) + pytest-cov / coverage 7.15.2.
Config resolved from env/.env (no hard-coded preview URLs). Tests run against the live backend +
MongoDB (integration) plus in-process pure-logic unit tests.

## Test result counts (exact)
| Suite | Result |
|---|---|
| Originally failing (targeted correction) | 2 passed (were 2 failed) |
| H-014A focused (`test_h014a_reality.py`) | **81 passed** |
| H-013 security + publication + http-gates | 20 passed |
| Full backend (`tests/`) | **191 passed, 1 skipped** |
| Failed | **0** |

Skipped (disclosed): `tests/test_design_studio.py:204` — live Gemini render, gated by
`RUN_RENDER_TEST=1`. Pre-existing and unrelated to H-014A.

## What the H-014A suite covers
- **Pure unit:** transform validation (dimensions / non-finite `inf`,`-inf`,`nan` / homogeneous row),
  spatial relationship rules, truth-promotion guard (all restricted classes), checksum,
  storage-reference validation, label default, reference-room determinism + content hash.
- **HTTP integration:** reference-room bootstrap idempotency + view, spatial graph, authz
  (401/403), truth-promotion over API, scan lifecycle (legal/illegal/terminal/idempotent/stale),
  artifact create + no-binary-in-Mongo + governed token, model accept→immutable→design separation.
- **Phase 1 ownership:** default ref = `tenant/{tenant}/property/{prop}/reality/{artifact}`;
  client tenant/property override ignored; cross-tenant scan 403; cross-property source 422;
  public response exposes only the governed token.
- **Phase 2 null sweep:** content_type / file_size / label / existing-model collections /
  design proposed_entities & deltas — omitted, explicit null, valid, empty.
- **Phase 3:** non-finite rejection (unit) + malformed-JSON safe rejection (HTTP 4xx, never 500).

## Measured coverage (routes + services)
Method: **subprocess coverage with data-file combination** (the acceptable option in the order).
1. Instrumented backend started under
   `coverage run --branch --parallel-mode --source=reality -m uvicorn server:app --port 8001 --workers 1`
   (no `--reload`, so the traced process is the one serving requests).
2. Exercised by the full HTTP suite: `pytest tests/test_h014a_reality.py` → 81 passed.
3. Server stopped (SIGINT) to flush; a second in-process pass of the pure-logic unit classes run
   with `coverage run --branch --parallel-mode -n0 -m pytest -k "<unit classes>"`.
4. `coverage combine --append` + `coverage report -m`.

Tool: **coverage.py 7.15.2** (branch coverage enabled).

```
Name                               Stmts  Miss  Branch  BrPart  Cover
reality/__init__.py                    0     0       0       0   100%
reality/artifact_service.py           71     5      28       6    89%
reality/audit_service.py              19     1       6       1    92%
reality/authz.py                      40    20      24       1    39%
reality/coordinate_service.py         68    21      36       7    63%
reality/enums.py                      91     0       0       0   100%
reality/fixtures.py                   71     0       6       0   100%
reality/indexes.py                    39     1       2       1    95%
reality/model_version_service.py     106    18      50      15    75%
reality/router.py                    112    35      16       3    62%
reality/scan_session_service.py       73    17      28       8    73%
reality/schemas.py                    73     0       0       0   100%
reality/spatial_service.py           101    46      52       6    54%
TOTAL                                864   164     248      48    75%
```

## Uncovered critical paths & honest limitations
- **`spatial_service` create_entity happy path (HTTP) is not exercised** — creating spatial
  entities on the reference property would break the deterministic `entity_count == 12` and
  `WALL == 4` assertions, so create_entity is covered only via pure relationship/label unit tests
  (the DB-writing branch shows as uncovered). This is an intentional determinism-protection
  tradeoff, not a defect.
- **`authz` real-property branches (lines 36-50) and `validate_classifications` (70-77)** are not
  hit because all HTTP tests use the reference property; the truth-promotion guard itself is fully
  covered.
- Several `router.py` GET-by-id + list handlers and error-branch lines are not individually
  exercised (62%). Numbers reflect *only* the reality package (`--source=reality`), not the whole
  repository.
- Coverage numbers are code coverage from server + unit execution — **no browser check is counted
  as coverage**.
