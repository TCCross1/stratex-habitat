"""
H-013 Batch 2 — Passport Projection unit tests (Phase 11).
No network / no DB. Validates the versioned read-only projection boundary.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
import passport_projection as pj  # noqa: E402


TENANT = "stratex-habitat"
PROP = "villa-horizon-uuid"


class TestModeResolution:
    def test_production_env_resolves_production(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.delenv("HABITAT_PROJECTION_MODE", raising=False)
        assert pj.resolve_mode() == pj.MODE_PRODUCTION

    def test_explicit_mode_wins(self, monkeypatch):
        monkeypatch.setenv("HABITAT_ENV", "production")
        monkeypatch.setenv("HABITAT_PROJECTION_MODE", "test")
        assert pj.resolve_mode() == pj.MODE_TEST


class TestDevelopmentProjection:
    def test_dev_context_is_labeled_non_authoritative(self, monkeypatch):
        monkeypatch.setenv("HABITAT_PROJECTION_MODE", "development")
        ctx = pj.PassportProjectionAdapter().get_context(TENANT, PROP)
        env = ctx["_projection"]
        assert env["authoritative"] is False
        assert env["provider_mode"] == "development"
        assert env["contract_version"] == pj.CONTRACT_VERSION
        assert env["fixture_or_seed_identifier"]
        assert env["generated_at"]
        # required categories present
        for cat in pj.REQUIRED_CONTEXT_CATEGORIES:
            assert cat in ctx


class TestValidation:
    def _good(self):
        return pj._seed_context("development", TENANT, PROP, "cid", "seed")

    def test_contract_version_mismatch_rejected(self):
        bad = self._good()
        bad["_projection"]["contract_version"] = "9.9.9"
        with pytest.raises(pj.ContractVersionError):
            pj.validate_projection(bad, TENANT, PROP)

    def test_tenant_mismatch_rejected(self):
        with pytest.raises(pj.TenantMismatchError):
            pj.validate_projection(self._good(), "other-tenant", PROP)

    def test_property_mismatch_rejected(self):
        with pytest.raises(pj.PropertyMismatchError):
            pj.validate_projection(self._good(), TENANT, "other-property")

    def test_invalid_schema_rejected(self):
        bad = self._good()
        del bad["property_identity"]
        with pytest.raises(pj.ProjectionValidationError):
            pj.validate_projection(bad, TENANT, PROP)

    def test_missing_envelope_rejected(self):
        with pytest.raises(pj.ProjectionValidationError):
            pj.validate_projection({"property_identity": {}}, TENANT, PROP)


class TestStale:
    def test_old_generated_at_is_stale(self):
        assert pj.compute_stale("2000-01-01T00:00:00+00:00") is True

    def test_fresh_generated_at_not_stale(self):
        from datetime import datetime, timezone
        assert pj.compute_stale(datetime.now(timezone.utc).isoformat()) is False


class TestProductionFailSafe:
    def test_production_without_endpoint_raises_unavailable(self, monkeypatch):
        monkeypatch.setenv("HABITAT_PROJECTION_MODE", "production")
        monkeypatch.delenv("HABITAT_PROJECTION_BASE_URL", raising=False)
        pj._reset_failures()
        with pytest.raises(pj.ProjectionUnavailable):
            pj.PassportProjectionAdapter().get_context(TENANT, PROP)

    def test_production_never_falls_back_to_seed(self, monkeypatch):
        # Even when a dev seed is trivially available, production must not use it.
        monkeypatch.setenv("HABITAT_PROJECTION_MODE", "production")
        monkeypatch.delenv("HABITAT_PROJECTION_BASE_URL", raising=False)
        pj._reset_failures()
        adapter = pj.PassportProjectionAdapter()
        assert isinstance(adapter.provider, pj.HttpProjectionProvider)
        with pytest.raises(pj.ProjectionUnavailable):
            adapter.get_context(TENANT, PROP)

    def test_production_unreachable_endpoint_times_out(self, monkeypatch):
        monkeypatch.setenv("HABITAT_PROJECTION_MODE", "production")
        monkeypatch.setenv("HABITAT_PROJECTION_BASE_URL", "http://127.0.0.1:9/projection")
        monkeypatch.setenv("HABITAT_PROJECTION_TIMEOUT_SECONDS", "1")
        pj._reset_failures()
        with pytest.raises(pj.ProjectionUnavailable):
            pj.PassportProjectionAdapter().get_context(TENANT, PROP)


class TestMissingProjection:
    def test_missing_category_is_unknown(self, monkeypatch):
        monkeypatch.setenv("HABITAT_PROJECTION_MODE", "development")
        got = pj.PassportProjectionAdapter().get_projection("nonexistent_category", TENANT, PROP)
        assert got["truth_classification"] == "UNKNOWN"
        assert got["authoritative"] is False
