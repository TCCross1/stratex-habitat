"""
Interior product / finish catalog — homeowner-friendly tiers with planning prices.
Prices are REGIONAL_PLANNING_PRICE style (not bids). Region multiplier applied in estimator.
"""

from __future__ import annotations

from typing import Any, Dict, List


def catalog_tree() -> Dict[str, Any]:
    return {
        "version": "1.0.0",
        "currency": "USD",
        "price_basis": "REGIONAL_PLANNING_PRICE",
        "categories": [
            {
                "id": "flooring",
                "label": "Flooring",
                "items": [
                    {"id": "lvp_std", "label": "LVP — standard", "unit": "sqft", "material": 3.5, "labor_hrs_per_unit": 0.12, "tier": "$"},
                    {"id": "lvp_prem", "label": "LVP — premium rigid core", "unit": "sqft", "material": 5.5, "labor_hrs_per_unit": 0.12, "tier": "$$"},
                    {"id": "eng_hw", "label": "Engineered hardwood", "unit": "sqft", "material": 7.5, "labor_hrs_per_unit": 0.18, "tier": "$$$"},
                    {"id": "solid_hw", "label": "Solid hardwood", "unit": "sqft", "material": 9.5, "labor_hrs_per_unit": 0.22, "tier": "$$$"},
                    {"id": "tile_cer", "label": "Ceramic tile", "unit": "sqft", "material": 4.0, "labor_hrs_per_unit": 0.35, "tier": "$$"},
                    {"id": "tile_porc", "label": "Porcelain tile", "unit": "sqft", "material": 6.0, "labor_hrs_per_unit": 0.4, "tier": "$$$"},
                    {"id": "carpet", "label": "Carpet + pad", "unit": "sqft", "material": 3.2, "labor_hrs_per_unit": 0.1, "tier": "$"},
                ],
            },
            {
                "id": "paint_trim",
                "label": "Paint & trim",
                "items": [
                    {"id": "paint_walls", "label": "Interior paint — walls", "unit": "sqft", "material": 0.45, "labor_hrs_per_unit": 0.02, "tier": "$"},
                    {"id": "paint_ceil", "label": "Ceiling paint", "unit": "sqft", "material": 0.35, "labor_hrs_per_unit": 0.02, "tier": "$"},
                    {"id": "base_mdf", "label": "Baseboard MDF 5.25\"", "unit": "lf", "material": 2.2, "labor_hrs_per_unit": 0.15, "tier": "$"},
                    {"id": "base_hw", "label": "Baseboard hardwood", "unit": "lf", "material": 5.5, "labor_hrs_per_unit": 0.18, "tier": "$$"},
                    {"id": "crown_std", "label": "Crown molding standard", "unit": "lf", "material": 4.0, "labor_hrs_per_unit": 0.25, "tier": "$$"},
                    {"id": "casing_std", "label": "Door/window casing", "unit": "lf", "material": 2.8, "labor_hrs_per_unit": 0.12, "tier": "$"},
                ],
            },
            {
                "id": "kitchen_cab",
                "label": "Kitchen cabinets",
                "items": [
                    {"id": "cab_stock", "label": "Stock cabinets (per LF)", "unit": "lf", "material": 180, "labor_hrs_per_unit": 1.2, "tier": "$"},
                    {"id": "cab_sc", "label": "Semi-custom shaker", "unit": "lf", "material": 320, "labor_hrs_per_unit": 1.4, "tier": "$$"},
                    {"id": "cab_custom", "label": "Custom inset", "unit": "lf", "material": 550, "labor_hrs_per_unit": 1.8, "tier": "$$$$"},
                    {"id": "island_base", "label": "Island base (per LF)", "unit": "lf", "material": 280, "labor_hrs_per_unit": 1.5, "tier": "$$"},
                    {"id": "hw_pull", "label": "Cabinet hardware set", "unit": "each", "material": 8, "labor_hrs_per_unit": 0.1, "tier": "$"},
                ],
            },
            {
                "id": "countertops",
                "label": "Countertops",
                "items": [
                    {"id": "lam", "label": "Laminate", "unit": "sqft", "material": 28, "labor_hrs_per_unit": 0.4, "tier": "$"},
                    {"id": "quartz", "label": "Quartz", "unit": "sqft", "material": 65, "labor_hrs_per_unit": 0.5, "tier": "$$$"},
                    {"id": "granite", "label": "Granite", "unit": "sqft", "material": 55, "labor_hrs_per_unit": 0.5, "tier": "$$"},
                    {"id": "butcher", "label": "Butcher block", "unit": "sqft", "material": 40, "labor_hrs_per_unit": 0.35, "tier": "$$"},
                ],
            },
            {
                "id": "bath",
                "label": "Bath fixtures & surrounds",
                "items": [
                    {"id": "van_single", "label": "Single vanity 36\"", "unit": "each", "material": 450, "labor_hrs_per_unit": 3.0, "tier": "$"},
                    {"id": "van_double", "label": "Double vanity 60\"", "unit": "each", "material": 900, "labor_hrs_per_unit": 4.5, "tier": "$$"},
                    {"id": "toilet_std", "label": "Toilet elongated", "unit": "each", "material": 280, "labor_hrs_per_unit": 2.0, "tier": "$"},
                    {"id": "shower_tile", "label": "Tile shower walls", "unit": "sqft", "material": 8, "labor_hrs_per_unit": 0.55, "tier": "$$"},
                    {"id": "shower_niche", "label": "Shower niche", "unit": "each", "material": 120, "labor_hrs_per_unit": 2.5, "tier": "$$"},
                    {"id": "shower_bench", "label": "Shower bench", "unit": "each", "material": 200, "labor_hrs_per_unit": 3.0, "tier": "$$"},
                    {"id": "door_frame", "label": "Shower door framed", "unit": "each", "material": 450, "labor_hrs_per_unit": 3.0, "tier": "$"},
                    {"id": "door_frameLESS", "label": "Shower door frameless", "unit": "each", "material": 1100, "labor_hrs_per_unit": 4.0, "tier": "$$$"},
                    {"id": "door_neo", "label": "Neo-angle shower enclosure", "unit": "each", "material": 1400, "labor_hrs_per_unit": 5.0, "tier": "$$$"},
                    {"id": "head_std", "label": "Showerhead + trim kit", "unit": "each", "material": 220, "labor_hrs_per_unit": 2.5, "tier": "$"},
                    {"id": "head_rain", "label": "Rain + handheld dual trim", "unit": "each", "material": 480, "labor_hrs_per_unit": 3.5, "tier": "$$"},
                    {"id": "mirror_std", "label": "Vanity mirror", "unit": "each", "material": 120, "labor_hrs_per_unit": 0.8, "tier": "$"},
                    {"id": "towel_bar", "label": "Towel bar set", "unit": "each", "material": 65, "labor_hrs_per_unit": 0.5, "tier": "$"},
                ],
            },
            {
                "id": "doors",
                "label": "Interior doors",
                "items": [
                    {"id": "door_hollow", "label": "Hollow core slab + hardware", "unit": "each", "material": 140, "labor_hrs_per_unit": 2.5, "tier": "$"},
                    {"id": "door_solid", "label": "Solid core slab + hardware", "unit": "each", "material": 280, "labor_hrs_per_unit": 2.8, "tier": "$$"},
                    {"id": "door_french", "label": "French door pair", "unit": "each", "material": 650, "labor_hrs_per_unit": 4.0, "tier": "$$$"},
                ],
            },
            {
                "id": "structural",
                "label": "Structural (open concept)",
                "items": [
                    {"id": "demo_wall", "label": "Non-bearing wall demo", "unit": "lf", "material": 5, "labor_hrs_per_unit": 0.8, "tier": "$"},
                    {"id": "demo_bearing", "label": "Bearing wall demo allowance", "unit": "lf", "material": 15, "labor_hrs_per_unit": 1.5, "tier": "$$"},
                    {"id": "lvl_beam", "label": "LVL beam package (materials)", "unit": "lf", "material": 45, "labor_hrs_per_unit": 1.2, "tier": "$$"},
                    {"id": "post_jack", "label": "Temp shoring / posts", "unit": "each", "material": 120, "labor_hrs_per_unit": 2.0, "tier": "$$"},
                    {"id": "eng_letter", "label": "Structural engineer letter allowance", "unit": "each", "material": 850, "labor_hrs_per_unit": 0, "tier": "$$"},
                ],
            },
            {
                "id": "electrical_hvac",
                "label": "Electrical / lighting / HVAC allowances",
                "items": [
                    {"id": "recessed", "label": "Recessed light", "unit": "each", "material": 45, "labor_hrs_per_unit": 1.2, "tier": "$"},
                    {"id": "pendant", "label": "Pendant light", "unit": "each", "material": 120, "labor_hrs_per_unit": 1.0, "tier": "$$"},
                    {"id": "under_cab", "label": "Under-cabinet LED run", "unit": "lf", "material": 18, "labor_hrs_per_unit": 0.3, "tier": "$$"},
                    {"id": "outlet", "label": "Add outlet", "unit": "each", "material": 35, "labor_hrs_per_unit": 1.5, "tier": "$"},
                    {"id": "hvac_reg", "label": "HVAC register relocate allowance", "unit": "each", "material": 150, "labor_hrs_per_unit": 2.0, "tier": "$$"},
                ],
            },
        ],
    }


def find_item(item_id: str) -> Dict[str, Any] | None:
    for cat in catalog_tree()["categories"]:
        for it in cat["items"]:
            if it["id"] == item_id:
                return {**it, "category_id": cat["id"], "category_label": cat["label"]}
    return None


def region_labor_rate(region: str = "US-KY") -> float:
    """Fully burdened planning rate $/hr by rough region."""
    rates = {
        "US-KY": 55,
        "US-TN": 52,
        "US-OH": 58,
        "US-IN": 54,
        "US-SE": 50,
        "US-NE": 75,
        "US-W": 85,
        "US-DEFAULT": 60,
    }
    return float(rates.get(region, rates["US-DEFAULT"]))
