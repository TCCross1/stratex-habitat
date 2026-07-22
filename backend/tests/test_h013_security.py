"""
H-013 Wave 1 — Critical Security-Gate Unit Tests

Fast, deterministic unit tests (no network / no DB) that import the governed
provider modules directly and validate the security controls:

* Governed price-book provenance (#7)
* Deterministic fixture environment gate + provenance (#4)
* Server-side contractor-package redaction (#9)

Run as part of the normal backend pytest suite.
"""
import os
import sys

# Ensure the backend package dir (parent of tests/) is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
import pricebook  # noqa: E402
import fixture_provider as fx  # noqa: E402
import redaction  # noqa: E402


# ---------------------------------------------------------------------------
# #7 — Governed price-book provider
# ---------------------------------------------------------------------------
class TestGovernedPriceBook:
    def test_estimate_carries_governance_provenance(self):
        est = pricebook.planning_estimate("GAF Timberline HDZ", basis="local")
        prov = est["provenance"]
        assert prov["price_source"] == "HABITAT_GOVERNED_PRICE_BOOK"
        assert prov["price_book_version"] == pricebook.PRICE_BOOK_VERSION
        assert prov["currency"] == "USD"
        assert prov["governed"] is True
        # Planning references must never masquerade as canonical truth.
        assert prov["authoritative"] is False

    def test_estimate_ranges_are_numeric(self):
        est = pricebook.planning_estimate("GAF Timberline HDZ", basis="local")
        rng = est["range"]
        assert isinstance(rng["low"], (int, float))
        assert isinstance(rng["high"], (int, float))
        assert rng["low"] <= rng["high"]
        assert rng["expected"] == sum(est["breakdown"].values())
        assert est["range_display"] == pricebook.format_range(rng["low"], rng["high"])

    def test_unknown_material_falls_back_to_default(self):
        est = pricebook.planning_estimate("Nonexistent Material")
        assert est["material"] == pricebook.default_roof_material()

    def test_all_materials_listed(self):
        mats = {m["material"] for m in pricebook.list_materials()}
        assert {"GAF Timberline HDZ", "DECRA Standing Seam", "CertainTeed Grand Manor"} <= mats


# ---------------------------------------------------------------------------
# #4 — Deterministic fixture environment gate
# ---------------------------------------------------------------------------
class TestFixtureGate:
    def test_fixtures_disabled_in_production(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.delenv("HABITAT_ENABLE_FIXTURES", raising=False)
        assert fx.fixtures_enabled() is False
        with pytest.raises(fx.FixtureDisabledError):
            fx.require_fixtures("roof_condition")
        with pytest.raises(fx.FixtureDisabledError):
            fx.serve_fixture({"a": 1}, "roof_condition")

    def test_fixtures_enabled_in_development(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "development")
        monkeypatch.delenv("HABITAT_ENABLE_FIXTURES", raising=False)
        assert fx.fixtures_enabled() is True
        served = fx.serve_fixture({"roof": "data"}, "roof_condition")
        assert served["is_fixture"] is True
        assert served["_provenance"]["authoritative"] is False
        assert served["_provenance"]["data_source"] == "DETERMINISTIC_FIXTURE"

    def test_explicit_override_wins(self, monkeypatch):
        # Production but explicitly enabled -> enabled.
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", "true")
        assert fx.fixtures_enabled() is True
        # Development but explicitly disabled -> disabled.
        monkeypatch.setenv("HABITAT_ENV", "development")
        monkeypatch.setenv("HABITAT_ENABLE_FIXTURES", "false")
        assert fx.fixtures_enabled() is False


# ---------------------------------------------------------------------------
# #9 — Contractor-package redaction (server-side enforcement)
# ---------------------------------------------------------------------------
def _internal_package():
    return {
        "summary": "Villa Horizon Roof Replacement",
        "property_context": {"name": "Villa Horizon", "location": "Austin, TX", "year_built": 2019},
        "quantity_takeoff": {"area_sqft": 3200},
        "planning_estimate": "$9,800 - $13,400",
        "assumptions": ["Deck limited to North Slope anomaly."],
        "shared_documents": [
            {"id": "doc_01", "name": "Drone_Report.pdf", "shared": True},
            {"id": "doc_02", "name": "Appraisal.pdf", "shared": False},
        ],
        # Sensitive / internal — must never leak:
        "homeowner_contact": {"last_name": "Morgan", "email": "alex@stratexhabitat.com", "phone": "(512) 555-0101"},
        "owner_id": "owner-uuid-123",
        "internal_trust_grade": "A+",
        "correlation_id": "corr-uuid-999",
    }


class TestContractorRedaction:
    FORBIDDEN = ["Morgan", "alex@stratexhabitat.com", "(512) 555-0101",
                 "owner-uuid-123", "A+", "corr-uuid-999", "Appraisal.pdf"]

    def test_preview_strips_all_pii_and_internal(self):
        out = redaction.redact_contractor_package(_internal_package(), homeowner_approved=False)
        leaked = redaction.assert_no_sensitive_values(out, self.FORBIDDEN)
        assert leaked == [], f"Leaked forbidden values: {leaked}"
        assert "homeowner_contact" not in out
        assert out["redaction"]["redaction_enforced"] is True
        assert out["redaction"]["tier"] == "preview"
        # Backward-compatible keys still present.
        assert "redacted_personal_info" in out
        assert "quantity_takeoff" in out
        assert "shared_documents" in out
        # Only the shared document is exposed.
        assert [d["id"] for d in out["shared_documents"]] == ["doc_01"]

    def test_approved_releases_contact_only(self):
        out = redaction.redact_contractor_package(_internal_package(), homeowner_approved=True)
        assert out["redaction"]["tier"] == "contractor"
        assert out["redaction"]["personal_contact_shared"] is True
        assert out["homeowner_contact"]["email"] == "alex@stratexhabitat.com"
        # Internal-only fields are STILL stripped even after approval.
        internal_leak = redaction.assert_no_sensitive_values(
            out, ["owner-uuid-123", "A+", "corr-uuid-999"]
        )
        assert internal_leak == [], f"Internal fields leaked: {internal_leak}"
