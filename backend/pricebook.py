"""
STRATEX HABITAT — Governed Price-Book Provider (H-013)

Single, versioned source of numeric planning-estimate pricing for the roof
vertical slice. This replaces hard-coded price literals that previously lived
inline inside the Steward module.

Governance contract
-------------------
* Every estimate produced carries a `provenance` block recording the
  price-book version, effective date, currency, and region basis.
* These numbers are GOVERNED PLANNING REFERENCES only. They are explicitly
  marked `authoritative: False` — Habitat may plan with them but must never
  present them as canonical STRATEX Core / Property Passport truth, nor as a
  contractor bid.
* To change pricing, bump PRICE_BOOK_VERSION and EFFECTIVE_DATE here. Nothing
  else in the app should contain bare numeric price literals for the roof slice.
"""
from __future__ import annotations
from typing import Dict, List

# ---------------------------------------------------------------------------
# Governance header
# ---------------------------------------------------------------------------
PRICE_BOOK_VERSION = "2026.07.0"
EFFECTIVE_DATE = "2026-07-01"
CURRENCY = "USD"
PRICE_SOURCE = "HABITAT_GOVERNED_PRICE_BOOK"
REGION_BASIS = {
    "national": "US National Average",
    "regional": "South Central US (regional)",
    "local": "Austin, TX (local multiplier applied)",
}
DEFAULT_BASIS = "local"

# ---------------------------------------------------------------------------
# Governed roof assemblies (moved out of Steward's inline EST_DATA)
# ---------------------------------------------------------------------------
ROOF_ASSEMBLIES: Dict[str, dict] = {
    "GAF Timberline HDZ": {
        "material_label": "Architectural Shingle (GAF Timberline HDZ)",
        "national_low": 8500, "national_high": 11500,
        "regional_low": 9200, "regional_high": 12800,
        "local_low": 9800, "local_high": 13400,
        "breakdown": {
            "materials": 3800, "labor": 4200, "equipment": 800,
            "tear_off_disposal": 1200, "permits_fees": 400,
            "contractor_op": 1500, "contingency": 700, "taxes": 300,
        },
    },
    "DECRA Standing Seam": {
        "material_label": "Standing Seam Metal Roofing (DECRA Standing Seam)",
        "national_low": 22000, "national_high": 32000,
        "regional_low": 24000, "regional_high": 35000,
        "local_low": 26000, "local_high": 38000,
        "breakdown": {
            "materials": 13500, "labor": 10500, "equipment": 1800,
            "tear_off_disposal": 1600, "permits_fees": 500,
            "contractor_op": 4500, "contingency": 2500, "taxes": 1100,
        },
    },
    "CertainTeed Grand Manor": {
        "material_label": "Luxury Dimensional Shingle (CertainTeed Grand Manor)",
        "national_low": 16000, "national_high": 22000,
        "regional_low": 17500, "regional_high": 24500,
        "local_low": 19000, "local_high": 26500,
        "breakdown": {
            "materials": 8800, "labor": 7500, "equipment": 1200,
            "tear_off_disposal": 1400, "permits_fees": 450,
            "contractor_op": 3200, "contingency": 1800, "taxes": 750,
        },
    },
}

DEFAULT_ROOF_MATERIAL = "GAF Timberline HDZ"


def default_roof_material() -> str:
    return DEFAULT_ROOF_MATERIAL


def list_materials() -> List[dict]:
    return [{"material": k, "material_label": v["material_label"]}
            for k, v in ROOF_ASSEMBLIES.items()]


def has_material(material: str) -> bool:
    return material in ROOF_ASSEMBLIES


def get_assembly(material: str) -> dict:
    """Return the governed assembly, falling back to the default material."""
    return ROOF_ASSEMBLIES.get(material, ROOF_ASSEMBLIES[DEFAULT_ROOF_MATERIAL])


def provenance(basis: str = DEFAULT_BASIS) -> dict:
    """Governance provenance attached to every estimate produced here."""
    return {
        "price_source": PRICE_SOURCE,
        "price_book_version": PRICE_BOOK_VERSION,
        "effective_date": EFFECTIVE_DATE,
        "currency": CURRENCY,
        "region_basis": REGION_BASIS.get(basis, REGION_BASIS[DEFAULT_BASIS]),
        "governed": True,
        "authoritative": False,
        "disclaimer": (
            "Governed planning reference from the Habitat price-book. "
            "Not a contractor bid and not a Passport/Core-certified value."
        ),
    }


def _range_for_basis(assembly: dict, basis: str) -> tuple:
    basis = basis if basis in ("national", "regional", "local") else DEFAULT_BASIS
    return assembly[f"{basis}_low"], assembly[f"{basis}_high"]


def format_range(low: float, high: float) -> str:
    return f"${low:,.0f} - ${high:,.0f}"


def planning_estimate(material: str, basis: str = DEFAULT_BASIS) -> dict:
    """Return a governed planning estimate for a roof material.

    Shape:
        {
          material, material_label,
          basis, range: {low, expected, high}, range_display,
          breakdown, provenance{...}
        }
    """
    assembly = get_assembly(material)
    low, high = _range_for_basis(assembly, basis)
    breakdown = dict(assembly["breakdown"])
    expected = sum(breakdown.values())
    return {
        "material": material if has_material(material) else DEFAULT_ROOF_MATERIAL,
        "material_label": assembly["material_label"],
        "basis": basis if basis in REGION_BASIS else DEFAULT_BASIS,
        "range": {"low": low, "expected": expected, "high": high},
        "range_display": format_range(low, high),
        "breakdown": breakdown,
        "provenance": provenance(basis),
    }
