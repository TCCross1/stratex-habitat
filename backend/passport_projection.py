"""
STRATEX HABITAT — Versioned, read-only Passport Projection Adapter (H-013 Batch 2)

Habitat consumes canonical property truth ONLY through this adapter:

    Habitat  ->  PassportProjectionAdapter  ->  authorized projection provider

Habitat never queries Core/Passport databases directly and never writes canonical
facts. Every projection payload is versioned and carries provenance. In
non-production modes the payload is explicitly marked `authoritative: false` with a
provider mode and a fixture/seed identifier. In PRODUCTION mode the adapter uses the
configured HTTP projection endpoint and **fails safe** (503) when it is unavailable —
it NEVER silently substitutes demo/test data.

Provider modes: production | development | demo | test
"""
from __future__ import annotations
import os
import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger("habitat.projection")

# ---------------------------------------------------------------------------
# Contract + configuration
# ---------------------------------------------------------------------------
CONTRACT_VERSION = os.environ.get("HABITAT_PROJECTION_CONTRACT_VERSION", "1.0.0")

MODE_PRODUCTION = "production"
MODE_DEVELOPMENT = "development"
MODE_DEMO = "demo"
MODE_TEST = "test"
VALID_MODES = {MODE_PRODUCTION, MODE_DEVELOPMENT, MODE_DEMO, MODE_TEST}

# Truth classifications preserved end-to-end (Phase 4)
TRUTH_CLASSES = ["VERIFIED", "ESTIMATED", "PROJECTED", "HOMEOWNER_REPORTED", "SUGGESTED", "UNKNOWN"]

REQUIRED_CONTEXT_CATEGORIES = ["property_identity", "published_explanation", "property_dna_projection"]
PROJECTION_CATEGORIES = [
    "property_identity", "published_explanation", "property_dna_projection",
    "timeline_entries", "warranty_metadata", "approved_roof_geometry", "document_metadata",
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def stale_after_seconds() -> int:
    try:
        return int(os.environ.get("HABITAT_PROJECTION_STALE_SECONDS", "86400"))
    except ValueError:
        return 86400


def resolve_mode() -> str:
    explicit = os.environ.get("HABITAT_PROJECTION_MODE")
    if explicit and explicit.strip():
        m = explicit.strip().lower()
        return m if m in VALID_MODES else MODE_DEVELOPMENT
    env = os.environ.get("HABITAT_ENV", "development").strip().lower()
    return MODE_PRODUCTION if env == "production" else MODE_DEVELOPMENT


# ---------------------------------------------------------------------------
# Structured errors
# ---------------------------------------------------------------------------
class ProjectionError(Exception):
    status_code = 502
    code = "PROJECTION_ERROR"

    def __init__(self, message: str, code: str = None, status_code: int = None, details: dict = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.details = details or {}

    def to_dict(self, correlation_id: str = None) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "details": self.details,
            "correlation_id": correlation_id,
        }


class ProjectionUnavailable(ProjectionError):
    status_code = 503
    code = "PROJECTION_UNAVAILABLE"


class ProjectionValidationError(ProjectionError):
    status_code = 502
    code = "PROJECTION_INVALID"


class ContractVersionError(ProjectionError):
    status_code = 502
    code = "CONTRACT_VERSION_MISMATCH"


class TenantMismatchError(ProjectionError):
    status_code = 403
    code = "TENANT_MISMATCH"


class PropertyMismatchError(ProjectionError):
    status_code = 409
    code = "PROPERTY_MISMATCH"


# ---------------------------------------------------------------------------
# Envelope + per-item projection metadata
# ---------------------------------------------------------------------------
def build_envelope(mode: str, tenant_id: str, property_id: str, correlation_id: str,
                   seed_identifier: Optional[str]) -> dict:
    generated_at = _iso(_now())
    return {
        "contract_version": CONTRACT_VERSION,
        "provider_mode": mode,
        "tenant_id": tenant_id,
        "property_id": property_id,
        "authoritative": mode == MODE_PRODUCTION,
        "fixture_or_seed_identifier": seed_identifier,
        "generated_at": generated_at,
        "correlation_id": correlation_id,
        "authorization_scope": "property_projections_read",
        "stale": False,
        "stale_reason": None,
    }


def _meta(projection_id: str, version: str, publication_state: str, source_system: str,
          source_id: str, truth: str, confidence: Optional[str], effective_at: str,
          canonical_ref_ids, scope: str) -> dict:
    generated_at = _iso(_now())
    return {
        # legacy H-012 fields (kept for backward compatibility)
        "source_system": source_system,
        "source_id": source_id,
        "version": version,
        "truth_classification": truth,
        "timestamp": generated_at,
        "authorization_scope": scope,
        # projection contract fields
        "projection_id": projection_id,
        "projection_version": version,
        "publication_state": publication_state,
        "confidence": confidence,
        "generated_at": generated_at,
        "effective_at": effective_at,
        "canonical_reference_ids": canonical_ref_ids or [],
    }


def compute_stale(generated_at_iso: str, now: datetime = None) -> bool:
    now = now or _now()
    try:
        gen = datetime.fromisoformat(generated_at_iso)
        if gen.tzinfo is None:
            gen = gen.replace(tzinfo=timezone.utc)
    except Exception:
        return True
    return (now - gen).total_seconds() > stale_after_seconds()


def _apply_stale(payload: dict) -> None:
    env = payload.get("_projection", {})
    gen = env.get("generated_at")
    if gen and compute_stale(gen):
        env["stale"] = True
        env["stale_reason"] = f"generated_at older than {stale_after_seconds()}s freshness window"


# ---------------------------------------------------------------------------
# Seed context (development/demo/test providers share this shape)
# ---------------------------------------------------------------------------
def _seed_context(mode: str, tenant_id: str, property_id: str, correlation_id: str,
                  seed_identifier: str) -> dict:
    return {
        "_projection": build_envelope(mode, tenant_id, property_id, correlation_id, seed_identifier),
        "property_identity": {
            "id": property_id, "name": "Central Kentucky Demonstration Home",
            "address": "Lexington, Kentucky",
            "property_type": "detached_single_family",
            "is_demo_fixture": True,
            "data_origin": "demo",
            "truth_status": "sample_only",
            **_meta("proj-identity", "1.2.0", "PUBLISHED", "Central Kentucky demonstration seed",
                    "DEMO-SEED-IDENTITY", "SAMPLE_ONLY", "DEMO", "2019-01-01T00:00:00Z",
                    ["DEMO-SEED-IDENTITY"], "property_ownership"),
        },
        "published_explanation": {
            "system": "Roofing", "material": "Asphalt Shingle (Architectural Shingles)",
            "installed_year": 2010, "current_condition": "Fair",
            **_meta("proj-roof-explanation", "2.0.1", "PUBLISHED", "Passport Core Certified Facts",
                    "PASSPORT-ROOF-7718", "VERIFIED", "HIGH", "2024-10-05T14:30:00Z",
                    ["PASSPORT-ROOF-7718", "SCAN-DRONE-2024-X"], "property_projections_read"),
        },
        "property_dna_projection": {
            "material_class": "Asphalt/Bituminous Shingle", "estimated_age_years": 16,
            "weather_exposure_cycles": 16,
            **_meta("proj-dna-roof", "1.0.4", "PROJECTED", "Property DNA Projection Engine",
                    "DNA-PROJ-8821", "PROJECTED", "MEDIUM", "2026-01-01T00:00:00Z",
                    ["DNA-PROJ-8821"], "property_projections_read"),
        },
        "timeline_entries": [
            {"id": "t_01", "date": "2010-06-15", "event": "Roof Installed",
             **_meta("proj-tl-01", "1.0", "PUBLISHED", "Central Kentucky demonstration appraisal sample", "DEMO-APP-2010-R",
                     "ESTIMATED", "MEDIUM", "2010-06-15T00:00:00Z", ["DEMO-APP-2010-R"], "property_timeline_read")},
            {"id": "t_02", "date": "2024-10-05", "event": "Aerial Drone Thermal Scan",
             **_meta("proj-tl-02", "1.1", "PUBLISHED", "STRATEX Core Aerial Audit", "SCAN-DRONE-2024-X",
                     "VERIFIED", "HIGH", "2024-10-05T14:30:00Z", ["SCAN-DRONE-2024-X"], "property_timeline_read")},
        ],
        "warranty_metadata": {
            "warranty_id": "w_002", "type": "Manufacturer Shingle Warranty", "coverage": "30-year limited",
            **_meta("proj-warranty", "1.0.0", "UNPUBLISHED", "Homeowner Conversation Assertions",
                    "MEM-CONV-9011", "HOMEOWNER_REPORTED", "LOW", "2022-01-01T00:00:00Z",
                    ["MEM-CONV-9011"], "property_warranties_read"),
        },
        "approved_roof_geometry": {
            "approx_area_sqft": 3200, "pitch": "6:12",
            "penetrations": ["1 chimney", "3 plumbing vents", "2 attic ridge vents"],
            **_meta("proj-geometry", "1.0.0", "PUBLISHED", "STRATEX Core 3D Mesh Audit",
                    "MESH-3D-2024", "VERIFIED", "HIGH", "2024-10-05T14:30:00Z",
                    ["MESH-3D-2024"], "property_projections_read"),
        },
        "document_metadata": [
            {"id": "doc_01", "name": "2024_Drone_Inspection_Report.pdf", "category": "inspection",
             "publication_state": "PUBLISHED", "truth_classification": "VERIFIED",
             "canonical_reference_ids": ["SCAN-DRONE-2024-X"]},
        ],
        "seasonal_context": {
            "current_season": "Summer",
            "weather_warning": "Texas high storm/hail vulnerability window (August-October)",
            "impact": "Deferred action increases risks of sudden violent thunderstorm penetration",
            "truth_classification": "VERIFIED", "timestamp": _iso(_now()),
            "source_system": "Stratex Seasonal Intel Service", "source_id": "SEASONAL-AUSTIN-2026",
            "authorization_scope": "environmental_conditions_read",
        },
        "active_roof_projects": [],
    }


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------
class ProjectionProvider:
    mode = None

    def get_context(self, tenant_id: str, property_id: str, correlation_id: str) -> dict:
        raise NotImplementedError


class DevelopmentSeedProvider(ProjectionProvider):
    mode = MODE_DEVELOPMENT

    def get_context(self, tenant_id, property_id, correlation_id):
        return _seed_context(self.mode, tenant_id, property_id, correlation_id, "dev-seed-roof-2026.07")


class DemoProvider(ProjectionProvider):
    mode = MODE_DEMO

    def get_context(self, tenant_id, property_id, correlation_id):
        return _seed_context(self.mode, tenant_id, property_id, correlation_id, "demo-seed-roof-2026.07")


class TestFixtureProvider(ProjectionProvider):
    mode = MODE_TEST

    def get_context(self, tenant_id, property_id, correlation_id):
        return _seed_context(self.mode, tenant_id, property_id, correlation_id, "test-fixture-roof")


# simple module-level circuit breaker for the HTTP provider
_CB = {"failures": 0, "open_until": 0.0}
_CB_THRESHOLD = 3
_CB_COOLDOWN = 30.0


class HttpProjectionProvider(ProjectionProvider):
    mode = MODE_PRODUCTION

    def get_context(self, tenant_id, property_id, correlation_id):
        base = (os.environ.get("HABITAT_PROJECTION_BASE_URL") or "").strip()
        if not base:
            # Fail safe. NEVER fall back to seed/demo/test data in production.
            raise ProjectionUnavailable(
                "No authorized Passport projection endpoint is configured (HABITAT_PROJECTION_BASE_URL).",
                details={"tenant_id": tenant_id, "property_id": property_id, "mode": self.mode},
            )
        now = time.time()
        if _CB["open_until"] > now:
            raise ProjectionUnavailable("Projection circuit breaker is open.",
                                        code="CIRCUIT_OPEN",
                                        details={"open_until": _CB["open_until"]})
        try:
            import requests
            timeout = float(os.environ.get("HABITAT_PROJECTION_TIMEOUT_SECONDS", "5"))
            headers = {"X-Correlation-Id": correlation_id}
            api_key = os.environ.get("HABITAT_PROJECTION_API_KEY")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            url = f"{base.rstrip('/')}/v{CONTRACT_VERSION.split('.')[0]}/projections/context"
            resp = requests.get(url, headers=headers,
                                 params={"tenant_id": tenant_id, "property_id": property_id,
                                         "contract_version": CONTRACT_VERSION},
                                 timeout=timeout)
        except Exception as e:  # network/timeout
            _record_failure()
            raise ProjectionUnavailable(f"Projection request failed: {e}",
                                        details={"tenant_id": tenant_id, "property_id": property_id})
        if resp.status_code != 200:
            _record_failure()
            raise ProjectionUnavailable(f"Projection endpoint returned HTTP {resp.status_code}",
                                        details={"status": resp.status_code})
        try:
            data = resp.json()
        except Exception:
            _record_failure()
            raise ProjectionValidationError("Projection endpoint returned a non-JSON body",
                                            code="SCHEMA_INVALID")
        _reset_failures()
        return data


def _record_failure():
    _CB["failures"] += 1
    if _CB["failures"] >= _CB_THRESHOLD:
        _CB["open_until"] = time.time() + _CB_COOLDOWN


def _reset_failures():
    _CB["failures"] = 0
    _CB["open_until"] = 0.0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_projection(payload: dict, expected_tenant: Optional[str], expected_property: Optional[str]) -> bool:
    env = payload.get("_projection") if isinstance(payload, dict) else None
    if not isinstance(env, dict):
        raise ProjectionValidationError("Missing _projection envelope", code="SCHEMA_INVALID")
    if env.get("contract_version") != CONTRACT_VERSION:
        raise ContractVersionError(
            f"Contract version mismatch: expected {CONTRACT_VERSION}, got {env.get('contract_version')}",
            details={"expected": CONTRACT_VERSION, "received": env.get("contract_version")},
        )
    if expected_tenant is not None and env.get("tenant_id") != expected_tenant:
        raise TenantMismatchError("Projection tenant does not match requesting tenant",
                                  details={"expected": expected_tenant, "received": env.get("tenant_id")})
    if expected_property is not None and env.get("property_id") != expected_property:
        raise PropertyMismatchError("Projection property does not match requested property",
                                    details={"expected": expected_property, "received": env.get("property_id")})
    for cat in REQUIRED_CONTEXT_CATEGORIES:
        if cat not in payload:
            raise ProjectionValidationError(f"Projection missing required category '{cat}'",
                                            code="SCHEMA_INVALID", details={"missing": cat})
    return True


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------
def build_provider(mode: str) -> ProjectionProvider:
    if mode == MODE_PRODUCTION:
        return HttpProjectionProvider()
    if mode == MODE_DEMO:
        return DemoProvider()
    if mode == MODE_TEST:
        return TestFixtureProvider()
    return DevelopmentSeedProvider()


class PassportProjectionAdapter:
    def __init__(self, mode: str = None):
        self.mode = mode or resolve_mode()
        self.provider = build_provider(self.mode)

    def get_context(self, tenant_id: str, property_id: str, correlation_id: str = None) -> dict:
        cid = correlation_id or str(uuid.uuid4())
        payload = self.provider.get_context(tenant_id, property_id, cid)  # may raise ProjectionUnavailable
        validate_projection(payload, tenant_id, property_id)
        _apply_stale(payload)
        return payload

    def get_projection(self, category: str, tenant_id: str, property_id: str,
                       correlation_id: str = None) -> dict:
        ctx = self.get_context(tenant_id, property_id, correlation_id)
        value = ctx.get(category)
        if value is None:
            # Missing projection stays UNKNOWN — never fabricated.
            return {
                "category": category,
                "truth_classification": "UNKNOWN",
                "publication_state": "UNKNOWN",
                "authoritative": False,
                "note": "Projection not available; treated as UNKNOWN.",
                "_projection": ctx.get("_projection"),
            }
        return value


def build_context(tenant_id: str, property_id: str, correlation_id: str = None) -> dict:
    """Convenience entrypoint used by the Steward context flow."""
    return PassportProjectionAdapter().get_context(tenant_id, property_id, correlation_id)
