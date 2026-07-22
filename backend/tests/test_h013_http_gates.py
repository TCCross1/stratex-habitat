"""
H-013 Batch 1 — Security & governance HTTP gate integration tests.

Relocated + refactored from the previous root-level `backend_test.py`
(hard-coded preview URL removed; config comes from conftest). Exercises the
gates over the wire, complementing the pure-logic units in
`test_h013_security.py`:

  * contractor-package redaction (no PII in preview; contact released only on
    explicit homeowner approval);
  * governed price-book provenance on estimates (versioned, non-authoritative);
  * deterministic fixture gate (served with non-authoritative provenance in
    development);
  * tenant isolation (Steward routes reject non-authorized users).
"""
import pytest

STEWARD = "/steward"


class TestContractorRedaction:
    def test_preview_strips_pii_and_internal_fields(self, homeowner_session, api_url):
        r = homeowner_session.get(f"{api_url}{STEWARD}/contractor-package", timeout=30)
        assert r.status_code == 200, r.text
        pkg = r.json()
        # allow-list survivors present
        assert "planning_estimate" in pkg and "quantity_takeoff" in pkg
        # sensitive / internal fields must be absent from the preview payload
        for forbidden in ("homeowner_contact", "exact_address", "owner_id", "correlation_id",
                          "internal_confidence"):
            assert forbidden not in pkg, f"{forbidden} leaked into preview"
        assert pkg["redaction"]["tier"] == "preview"
        assert pkg["redacted_personal_info"]["status"] == "redacted"

    def test_contact_released_only_on_approval(self, homeowner_session, api_url):
        r = homeowner_session.get(
            f"{api_url}{STEWARD}/contractor-package", params={"approved": "true"}, timeout=30)
        assert r.status_code == 200, r.text
        pkg = r.json()
        assert pkg["redaction"]["tier"] == "contractor"
        assert pkg["redaction"]["personal_contact_shared"] is True
        assert "homeowner_contact" in pkg
        assert pkg["homeowner_contact"].get("email") == "alex@stratexhabitat.com"


class TestGovernedPriceBook:
    def test_estimate_carries_governed_provenance(self, homeowner_session, api_url):
        r = homeowner_session.post(
            f"{api_url}{STEWARD}/estimate", json={"material": "GAF Timberline HDZ"}, timeout=30)
        assert r.status_code == 200, r.text
        est = r.json()
        assert est.get("price_book_version"), "estimate must expose a price-book version"
        prov = est.get("price_provenance", {})
        assert prov.get("governed") is True
        assert prov.get("authoritative") is False
        assert prov.get("price_book_version") == est["price_book_version"]


class TestFixtureGate:
    def test_fixture_served_with_nonauthoritative_provenance(self, homeowner_session, api_url):
        # development env -> fixtures enabled but clearly marked non-authoritative
        r = homeowner_session.get(f"{api_url}{STEWARD}/fixture", timeout=30)
        assert r.status_code == 200, r.text
        fx = r.json()
        assert fx.get("is_fixture") is True
        prov = fx.get("_provenance", {})
        assert prov.get("authoritative") is False
        assert prov.get("data_source") == "DETERMINISTIC_FIXTURE"


class TestTenantIsolation:
    def test_contractor_cannot_access_steward_routes(self, contractor_session, api_url):
        for path in ("/context", "/readiness", "/contractor-package"):
            r = contractor_session.get(f"{api_url}{STEWARD}{path}", timeout=30)
            assert r.status_code == 403, f"{path} should be tenant-restricted, got {r.status_code}"

    def test_contractor_cannot_publish(self, contractor_session, api_url):
        r = contractor_session.post(
            f"{api_url}{STEWARD}/publish",
            json={"property_id": "villa-horizon-uuid", "scenario_id": "x"}, timeout=30)
        assert r.status_code == 403, r.text
