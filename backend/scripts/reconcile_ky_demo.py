#!/usr/bin/env python3
"""
Dry-run / apply reconciliation for Habitat Central Kentucky demo fixtures.

Usage:
  python -m scripts.reconcile_ky_demo --dry-run
  python -m scripts.reconcile_ky_demo --apply --allow-legacy-seed

Refuses unmarked / non-demo property records. Never targets production blindly —
requires MONGO_URL + DB_NAME from environment/.env like the rest of Habitat.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import dotenv_values
from pymongo import MongoClient

from demo_property import (
    LEGACY_SEED_HOMEOWNER_EMAIL,
    is_explicit_demo_record,
    reconcile_demo_findings,
    reconcile_demo_properties,
)


def _cfg(key: str) -> str:
    fe = dotenv_values(ROOT.parent / "frontend" / ".env") if False else {}
    # backend/.env relative to backend/
    be = dotenv_values(ROOT / ".env")
    fe = dotenv_values(ROOT.parent / "frontend" / ".env")
    val = os.environ.get(key) or be.get(key) or fe.get(key)
    if not val:
        raise SystemExit(f"Missing config {key}")
    return val


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile KY demo Habitat fixtures")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", help="Persist updates to Mongo")
    parser.add_argument(
        "--allow-legacy-seed",
        action="store_true",
        help="Allow updating Villa Horizon owned by alex@stratexhabitat.com seed only",
    )
    args = parser.parse_args()
    dry_run = not args.apply

    client = MongoClient(_cfg("MONGO_URL"))
    db = client[_cfg("DB_NAME")]

    users = list(db.users.find({}, {"_id": 0, "id": 1, "email": 1}))
    email_by_id = {u["id"]: u.get("email", "") for u in users}
    props = list(db.properties.find({}, {"_id": 0}))
    findings = list(db.findings.find({}, {"_id": 0}))

    prop_report = reconcile_demo_properties(
        props,
        dry_run=dry_run,
        allow_legacy_seed_email=LEGACY_SEED_HOMEOWNER_EMAIL if args.allow_legacy_seed else None,
        owner_email_by_id=email_by_id,
    )

    demo_ids = {
        p["id"] for p in props
        if is_explicit_demo_record(p) or any(
            u.get("id") == p["id"] for u in prop_report["updated"]
        )
    }
    # After in-memory update, recompute demo ids from props list
    if not dry_run:
        demo_ids = {p["id"] for p in props if is_explicit_demo_record(p)}
    else:
        # Include planned updates as demo targets for finding plan
        demo_ids = {p["id"] for p in props if is_explicit_demo_record(p)} | {
            u["id"] for u in prop_report["updated"]
        }

    find_report = reconcile_demo_findings(findings, demo_ids, dry_run=dry_run)

    if not dry_run:
        for entry in prop_report["updated"]:
            db.properties.update_one({"id": entry["id"]}, {"$set": entry["intended_changes"]})
        for entry in find_report["updated"]:
            db.findings.update_one({"id": entry["id"]}, {"$set": entry["intended_changes"]})
        # Quotes property_name for demo properties
        for pid in demo_ids:
            db.quotes.update_many(
                {"property_id": pid},
                {"$set": {"property_name": "Central Kentucky Demonstration Home"}},
            )

    out = {"properties": prop_report, "findings": find_report}
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
