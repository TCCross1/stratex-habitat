"""
Homeowner-facing material catalog for Exterior Design Studio.
Detailed options (grain, profile, roof systems) with simple labels.
"""

from __future__ import annotations

from typing import Any, Dict, List


# Texture / profile options homeowners understand
SIDING_TEXTURES = [
    {"id": "cedar_grain", "label": "Cedar grain texture", "description": "Deep wood-look grain"},
    {"id": "smooth", "label": "Smooth", "description": "Clean modern surface"},
    {"id": "wood_lap", "label": "Wood lap", "description": "Classic horizontal lap lines"},
    {"id": "board_batten", "label": "Board & batten", "description": "Vertical board with battens"},
    {"id": "shingle_style", "label": "Shingle style", "description": "Scalloped / straight shingle look"},
    {"id": "stucco_fine", "label": "Fine stucco", "description": "Light texture stucco"},
    {"id": "stucco_heavy", "label": "Heavy stucco", "description": "Bold stucco texture"},
    {"id": "brick_veneer", "label": "Brick veneer", "description": "Thin brick appearance"},
    {"id": "stone_veneer", "label": "Stone veneer", "description": "Cultured or natural stone look"},
]

ROOF_SYSTEMS = [
    {"id": "arch_shingle", "label": "Architectural asphalt shingles", "unit": "sq"},
    {"id": "3tab_shingle", "label": "3-tab asphalt shingles", "unit": "sq"},
    {"id": "metal_standing_seam", "label": "Standing-seam metal", "unit": "sq"},
    {"id": "metal_corrugated", "label": "Corrugated metal", "unit": "sq"},
    {"id": "metal_shake", "label": "Metal shake", "unit": "sq"},
    {"id": "clay_tile", "label": "Clay tile", "unit": "sq"},
    {"id": "concrete_tile", "label": "Concrete tile", "unit": "sq"},
    {"id": "slate_synthetic", "label": "Synthetic slate", "unit": "sq"},
    {"id": "wood_cedar_shake", "label": "Cedar shake", "unit": "sq"},
]

# Representative catalog entries (extend with full SKU DB later)
MATERIAL_CATALOG: List[Dict[str, Any]] = [
    {
        "sku_id": "SID-1001-CG",
        "zone_tags": ["siding_main", "siding_accent"],
        "material_class": "composite_siding",
        "label": "Composite lap siding — cedar grain",
        "textures": ["cedar_grain"],
        "colors": [
            {"name": "Coastal White", "hex": "#F5F2EB"},
            {"name": "Charcoal", "hex": "#3A3A3A"},
            {"name": "Sage", "hex": "#8A9A7B"},
            {"name": "Naval Navy", "hex": "#1B2A41"},
            {"name": "Barn Red", "hex": "#7A2E2E"},
        ],
        "unit": "sqft",
        "cost_per_unit_low": 4.5,
        "cost_per_unit_high": 8.5,
        "labor_hours_per_unit": 0.12,
    },
    {
        "sku_id": "SID-1002-SM",
        "zone_tags": ["siding_main", "siding_accent"],
        "material_class": "composite_siding",
        "label": "Composite lap siding — smooth",
        "textures": ["smooth"],
        "colors": [
            {"name": "Arctic White", "hex": "#FAFAFA"},
            {"name": "Graphite", "hex": "#4A4A4A"},
            {"name": "Soft Taupe", "hex": "#B8A99A"},
        ],
        "unit": "sqft",
        "cost_per_unit_low": 4.0,
        "cost_per_unit_high": 7.5,
        "labor_hours_per_unit": 0.11,
    },
    {
        "sku_id": "SID-2001-BB",
        "zone_tags": ["siding_main", "siding_accent"],
        "material_class": "board_batten",
        "label": "Board & batten composite",
        "textures": ["board_batten"],
        "colors": [
            {"name": "Black", "hex": "#1A1A1A"},
            {"name": "White", "hex": "#FFFFFF"},
            {"name": "Forest", "hex": "#2F4F3E"},
        ],
        "unit": "sqft",
        "cost_per_unit_low": 5.5,
        "cost_per_unit_high": 10.0,
        "labor_hours_per_unit": 0.15,
    },
    {
        "sku_id": "SID-3001-WD",
        "zone_tags": ["siding_main"],
        "material_class": "wood_lap",
        "label": "Wood lap siding",
        "textures": ["wood_lap", "cedar_grain"],
        "colors": [
            {"name": "Natural Cedar", "hex": "#C4A574"},
            {"name": "Stained Walnut", "hex": "#5C4033"},
        ],
        "unit": "sqft",
        "cost_per_unit_low": 6.0,
        "cost_per_unit_high": 14.0,
        "labor_hours_per_unit": 0.18,
    },
    {
        "sku_id": "ROF-4001-AS",
        "zone_tags": ["roof_main"],
        "material_class": "architectural_shingle",
        "label": "Architectural shingles",
        "textures": ["arch_shingle"],
        "colors": [
            {"name": "Pewter Gray", "hex": "#6B6E70"},
            {"name": "Weathered Wood", "hex": "#7A6A55"},
            {"name": "Midnight Black", "hex": "#1C1C1C"},
            {"name": "Desert Tan", "hex": "#C2A878"},
        ],
        "unit": "sq",
        "cost_per_unit_low": 120.0,
        "cost_per_unit_high": 220.0,
        "labor_hours_per_unit": 2.5,
    },
    {
        "sku_id": "ROF-5001-SS",
        "zone_tags": ["roof_main"],
        "material_class": "standing_seam_metal",
        "label": "Standing-seam metal roof",
        "textures": ["metal_standing_seam"],
        "colors": [
            {"name": "Galvalume", "hex": "#C0C5C8"},
            {"name": "Matte Black", "hex": "#2B2B2B"},
            {"name": "Forest Green", "hex": "#2E4A3F"},
            {"name": "Copper Penny", "hex": "#B87333"},
        ],
        "unit": "sq",
        "cost_per_unit_low": 350.0,
        "cost_per_unit_high": 700.0,
        "labor_hours_per_unit": 4.0,
    },
    {
        "sku_id": "TRM-6001-PVC",
        "zone_tags": ["trim"],
        "material_class": "pvc_trim",
        "label": "PVC trim board",
        "textures": ["smooth"],
        "colors": [{"name": "White", "hex": "#FFFFFF"}, {"name": "Match siding", "hex": None}],
        "unit": "lf",
        "cost_per_unit_low": 3.0,
        "cost_per_unit_high": 8.0,
        "labor_hours_per_unit": 0.08,
    },
]

# National baseline labor $/hr bands by region key (extend with regional engine)
LABOR_RATE_BANDS = {
    "US-NATIONAL": {"low": 55.0, "high": 95.0},
    "US-SOUTH": {"low": 45.0, "high": 85.0},
    "US-MIDWEST": {"low": 50.0, "high": 90.0},
    "US-NORTHEAST": {"low": 65.0, "high": 120.0},
    "US-WEST": {"low": 70.0, "high": 130.0},
    "KY": {"low": 48.0, "high": 88.0},
}


def list_catalog(zone: str | None = None) -> List[Dict[str, Any]]:
    if not zone:
        return MATERIAL_CATALOG
    return [m for m in MATERIAL_CATALOG if zone in m.get("zone_tags", [])]


def get_sku(sku_id: str) -> Dict[str, Any] | None:
    for m in MATERIAL_CATALOG:
        if m["sku_id"] == sku_id:
            return m
    return None
