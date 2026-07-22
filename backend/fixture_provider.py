"""
STRATEX HABITAT — Deterministic Fixture Provider (H-013)

Wraps demo / deterministic fixtures behind an explicit environment gate so they
can NEVER be served silently as truth in production.

Environment
-----------
* HABITAT_ENV            : "development" (default) | "staging" | "production"
* HABITAT_ENABLE_FIXTURES: "true" / "false" (optional explicit override).
                           When unset, fixtures are enabled for every
                           environment EXCEPT production.

Contract
--------
* When fixtures are DISABLED, `require_fixtures()` / `serve_fixture()` raise
  `FixtureDisabledError`. The API layer surfaces this as HTTP 409 — a fixture
  payload is NEVER returned silently.
* When fixtures are ENABLED, `serve_fixture()` tags the payload with a
  `_provenance` block marking it clearly non-authoritative demo data.

All environment reads are LAZY (evaluated per call) so tests can toggle the
gate via monkeypatch without re-importing the module.
"""
from __future__ import annotations
import os
import copy
from typing import Any, Dict


class FixtureDisabledError(Exception):
    """Raised when a deterministic fixture is requested while fixtures are off."""

    def __init__(self, source_label: str = ""):
        self.source_label = source_label
        super().__init__(
            f"Deterministic fixtures are disabled in this environment "
            f"(source='{source_label}'). A governed data projection is required."
        )


def habitat_env() -> str:
    return os.environ.get("HABITAT_ENV", "development").strip().lower()


def fixtures_enabled() -> bool:
    """Explicit HABITAT_ENABLE_FIXTURES wins; otherwise on unless production."""
    explicit = os.environ.get("HABITAT_ENABLE_FIXTURES")
    if explicit is not None and explicit.strip() != "":
        return explicit.strip().lower() in ("1", "true", "yes", "on")
    return habitat_env() != "production"


def fixture_provenance(source_label: str) -> dict:
    return {
        "data_source": "DETERMINISTIC_FIXTURE",
        "authoritative": False,
        "fixture": True,
        "environment": habitat_env(),
        "source_label": source_label,
        "note": (
            "Deterministic demo fixture — NOT canonical STRATEX Core / "
            "Property Passport truth. Disabled automatically in production."
        ),
    }


def require_fixtures(source_label: str = "") -> None:
    if not fixtures_enabled():
        raise FixtureDisabledError(source_label)


def tag_fixture(payload: Dict[str, Any], source_label: str) -> Dict[str, Any]:
    """Return a copy of `payload` with fixture provenance attached."""
    tagged = copy.deepcopy(payload)
    tagged["is_fixture"] = True
    tagged["_provenance"] = fixture_provenance(source_label)
    return tagged


def serve_fixture(payload: Dict[str, Any], source_label: str) -> Dict[str, Any]:
    """Gate + tag: raise if fixtures are disabled, else return tagged copy."""
    require_fixtures(source_label)
    return tag_fixture(payload, source_label)
