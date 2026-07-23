"""H-014B.1 — non-production cleanup/migration for legacy binary chunk documents.

Purpose
-------
The original H-014B preview temporarily stored binary chunk bytes (or base64
copies) inside MongoDB collection `reality_upload_chunks`. That is prohibited.
This utility finds those legacy documents and strips/removes the binary fields
(or entire docs) under explicit operator confirmation.

Safety gates (all required)
---------------------------
1. Refuses to operate when HABITAT_ENV=production.
2. Refuses unknown / non-allow-listed environments (fail closed).
3. Requires an explicit ``--confirm-database <exact DB_NAME>`` that must match
   the configured database name — never runs automatically against an unknown
   database.
4. Dry-run by default; ``--apply`` required to mutate.
5. Never auto-invoked by application startup, indexes, or request handlers.

Usage
-----
  python -m reality.cleanup_binary_chunk_docs --confirm-database habitat_dev --dry-run
  python -m reality.cleanup_binary_chunk_docs --confirm-database habitat_dev --apply
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

_ALLOWED_ENVS = frozenset({"development", "demo", "test"})
_BINARY_FIELDS = ("data", "data_b64", "bytes", "payload", "content",
                  "chunk_bytes", "binary", "base64")


class CleanupRefused(RuntimeError):
    """Raised when the utility refuses to operate for safety reasons."""


def habitat_env() -> str:
    return os.environ.get("HABITAT_ENV", "development").strip().lower()


def assert_non_production(env: str | None = None) -> str:
    current = (env if env is not None else habitat_env()).strip().lower()
    if current == "production":
        raise CleanupRefused(
            "Refusing to operate: HABITAT_ENV=production. "
            "Binary-chunk cleanup is non-production only."
        )
    if current not in _ALLOWED_ENVS:
        raise CleanupRefused(
            f"Refusing to operate: HABITAT_ENV='{current}' is not an allow-listed "
            f"non-production environment {_ALLOWED_ENVS}."
        )
    return current


def assert_database_confirmed(configured_db_name: str, confirm_database: str) -> str:
    if not confirm_database or not str(confirm_database).strip():
        raise CleanupRefused(
            "Refusing to operate: --confirm-database is required and must exactly "
            "match the configured DB_NAME."
        )
    if confirm_database.strip() != configured_db_name:
        raise CleanupRefused(
            f"Refusing to operate: --confirm-database '{confirm_database}' does not "
            f"match configured DB_NAME '{configured_db_name}'. "
            "This utility never runs automatically against an unknown database."
        )
    return configured_db_name


def binary_field_filter() -> dict:
    """Mongo filter matching documents that still carry prohibited binary fields."""
    return {"$or": [{field: {"$exists": True}} for field in _BINARY_FIELDS]}


def summarize_docs(docs: Iterable[dict]) -> dict:
    counts = {field: 0 for field in _BINARY_FIELDS}
    total = 0
    for doc in docs:
        total += 1
        for field in _BINARY_FIELDS:
            if field in doc and doc[field] is not None:
                counts[field] += 1
    return {"matched_documents": total, "binary_field_counts": counts}


def plan_cleanup(docs: Iterable[dict], *, strip_fields: bool = True) -> list[dict]:
    """Return a list of planned mutations (no I/O)."""
    plans = []
    for doc in docs:
        present = [f for f in _BINARY_FIELDS if f in doc and doc[f] is not None]
        if not present:
            continue
        plans.append({
            "upload_session_id": doc.get("upload_session_id"),
            "index": doc.get("index"),
            "fields_to_unset": present,
            "action": "unset_binary_fields" if strip_fields else "delete_document",
        })
    return plans


async def run_cleanup(db, *, confirm_database: str, apply: bool = False,
                      strip_fields: bool = True, env: str | None = None) -> dict:
    """Execute (or dry-run) cleanup against an already-opened DB handle.

    ``db`` must expose motor/pymongo-like ``[collection]`` access. This function
    is intentionally NOT called from application startup.
    """
    assert_non_production(env)
    configured = os.environ.get("DB_NAME", "")
    # Prefer the handle's name when available.
    db_name = getattr(db, "name", None) or configured
    assert_database_confirmed(db_name, confirm_database)

    coll = db["reality_upload_chunks"]
    cursor = coll.find(binary_field_filter())
    docs = []
    if hasattr(cursor, "to_list"):
        docs = await cursor.to_list(length=10_000)
    else:
        # Sync pymongo cursor
        docs = list(cursor)

    summary = summarize_docs(docs)
    plans = plan_cleanup(docs, strip_fields=strip_fields)
    result = {
        "environment": habitat_env() if env is None else env,
        "database": db_name,
        "dry_run": not apply,
        "summary": summary,
        "planned_mutations": len(plans),
        "applied": 0,
        "refused_production": False,
    }
    if not apply:
        return result

    applied = 0
    for plan in plans:
        filt = {"upload_session_id": plan["upload_session_id"], "index": plan["index"]}
        if plan["action"] == "delete_document":
            res = coll.delete_one(filt)
        else:
            unset = {f: "" for f in plan["fields_to_unset"]}
            res = coll.update_one(filt, {"$unset": unset})
        if hasattr(res, "__await__"):
            await res
        applied += 1
    result["applied"] = applied
    result["dry_run"] = False
    return result


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--confirm-database", required=True,
                   help="Exact DB_NAME that must match the configured database.")
    p.add_argument("--apply", action="store_true",
                   help="Actually mutate documents. Default is dry-run.")
    p.add_argument("--delete-documents", action="store_true",
                   help="Delete matching docs instead of unsetting binary fields.")
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    args = _build_parser().parse_args(argv)
    try:
        assert_non_production()
    except CleanupRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2

    try:
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        if not mongo_url or not db_name:
            raise CleanupRefused("MONGO_URL and DB_NAME must be set in the environment.")
        assert_database_confirmed(db_name, args.confirm_database)
    except CleanupRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2

    client = MongoClient(mongo_url)
    try:
        db = client[db_name]
        coll = db["reality_upload_chunks"]
        docs = list(coll.find(binary_field_filter()))
        summary = summarize_docs(docs)
        plans = plan_cleanup(docs, strip_fields=not args.delete_documents)
        print(f"environment={habitat_env()} database={db_name} dry_run={not args.apply}")
        print(f"matched={summary['matched_documents']} planned={len(plans)}")
        print(f"binary_field_counts={summary['binary_field_counts']}")
        if not args.apply:
            print("Dry-run only. Re-run with --apply to mutate.")
            return 0
        applied = 0
        for plan in plans:
            filt = {"upload_session_id": plan["upload_session_id"], "index": plan["index"]}
            if plan["action"] == "delete_document":
                coll.delete_one(filt)
            else:
                coll.update_one(filt, {"$unset": {f: "" for f in plan["fields_to_unset"]}})
            applied += 1
        print(f"applied={applied}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
