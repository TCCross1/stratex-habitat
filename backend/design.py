"""STRATEX HABITAT — Design Studio: materials library, zones, recommendations, seed."""
from datetime import datetime, timezone
import uuid

BASE_FACADE = "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/d8131a35be696a34f7df7d3c45864fbf1f935060c03d1c8f6551fc33afcdcac9.png"
PRESET_IMG = {
    "white_brick": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/5e8f9813e10fd6dc19b907a77cf7347076d715ae0e7a29a71ccc64794c57198b.png",
    "charcoal": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/857a48b8e5372e77bff2dac31e333273159ea491737b341ffd2ab3f053783bc1.png",
    "copper": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/521bc83aab12e51b01209b7776060cb242be1f86a24a282fb2c0ecbdb0f14160.png",
    "stone": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/3d9d443977a856b4ed39b84ed3abeb4a4192d8b48b93cd2aa72176dc3ac0c7fa.png",
    "budget": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/902fe6b07c37f071cc1a6e433c7a5fa3fd82a47f890d9adbea95ec77e1e58783.png",
    "premium": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/560e1c8205db9952fdd77d93cf8a323eb5e703a5ce46a5ce9df23ff7df120f5d.png",
}

# Editable zones and the material categories each accepts (guided realism)
ZONES = [
    {"id": "roof", "label": "Roof Planes", "group": "Roof", "accepts": ["Roofing"]},
    {"id": "roof_accents", "label": "Ridge / Hips / Accessories", "group": "Roof", "accepts": ["Roofing"]},
    {"id": "siding_main", "label": "Siding — Main Field", "group": "Walls", "accepts": ["Siding", "Brick / Stone Veneer"]},
    {"id": "siding_accent", "label": "Accent Siding Zone", "group": "Walls", "accepts": ["Siding", "Brick / Stone Veneer"]},
    {"id": "veneer", "label": "Brick / Stone Veneer", "group": "Walls", "accepts": ["Brick / Stone Veneer"]},
    {"id": "trim", "label": "Trim", "group": "Details", "accepts": ["Trim"]},
    {"id": "fascia_soffit", "label": "Fascia & Soffit", "group": "Details", "accepts": ["Trim"]},
    {"id": "shutters", "label": "Shutters", "group": "Details", "accepts": ["Shutters"]},
    {"id": "windows", "label": "Windows & Window Trim", "group": "Openings", "accepts": ["Windows"]},
    {"id": "front_door", "label": "Front Door & Entry", "group": "Openings", "accepts": ["Front Door"]},
    {"id": "garage", "label": "Garage Doors", "group": "Openings", "accepts": ["Garage Door"]},
    {"id": "columns", "label": "Columns / Railings / Porch", "group": "Details", "accepts": ["Columns & Railings"]},
    {"id": "gutters", "label": "Gutters & Downspouts", "group": "Details", "accepts": ["Gutters"]},
]


def _p(category, manufacturer, family, profile, colors, finish, style, price_tier, durability,
       maintenance, energy="", notes="", popularity=50):
    return {"id": str(uuid.uuid4()), "category": category, "manufacturer": manufacturer,
            "family": family, "profile": profile, "colors": colors, "finish": finish,
            "styles": style, "price_tier": price_tier, "durability": durability,
            "maintenance": maintenance, "energy": energy, "notes": notes, "popularity": popularity}


def products():
    return [
        # Roofing
        _p("Roofing", "GAF", "Timberline HDZ", "Architectural Shingle",
           [{"name": "Charcoal", "hex": "#33373b", "tone": "cool"}, {"name": "Weathered Wood", "hex": "#6b6258", "tone": "warm"},
            {"name": "Slate", "hex": "#4a4f55", "tone": "cool"}, {"name": "Barkwood", "hex": "#5a4d42", "tone": "warm"}],
           "Matte", ["traditional", "transitional", "craftsman", "colonial"], "$$", "30-year", "Low",
           "Cool-roof options available", "Most popular architectural shingle for resale value", 92),
        _p("Roofing", "DECRA", "Standing Seam", "Metal Standing Seam",
           [{"name": "Copper", "hex": "#b46b3a", "tone": "warm"}, {"name": "Matte Black", "hex": "#1c1c1e", "tone": "cool"},
            {"name": "Charcoal Metal", "hex": "#3a3d40", "tone": "cool"}, {"name": "Bronze", "hex": "#5b4631", "tone": "warm"}],
           "Metallic", ["modern", "farmhouse", "transitional"], "$$$$", "50-year", "Very Low",
           "High energy reflectivity; premium curb appeal", "Reflective metal, excellent longevity", 78),
        _p("Roofing", "CertainTeed", "Grand Manor", "Luxury Shingle",
           [{"name": "Stonegate Gray", "hex": "#5d6066", "tone": "cool"}, {"name": "Colonial Slate", "hex": "#4b4e54", "tone": "cool"}],
           "Dimensional", ["luxury", "colonial", "traditional"], "$$$", "Lifetime", "Low", "",
           "Luxury dimensional profile", 64),
        # Siding
        _p("Siding", "James Hardie", "HardiePlank", "Lap Siding",
           [{"name": "Arctic White", "hex": "#f3f1ec", "tone": "cool"}, {"name": "Light Greige", "hex": "#cfc7ba", "tone": "warm"},
            {"name": "Iron Gray", "hex": "#5a5f63", "tone": "cool"}, {"name": "Khaki Brown", "hex": "#8a7a64", "tone": "warm"},
            {"name": "Boothbay Blue", "hex": "#6f8694", "tone": "cool"}, {"name": "Pearl Gray", "hex": "#b9bbbd", "tone": "cool"}],
           "Matte", ["traditional", "transitional", "craftsman", "colonial"], "$$", "30-year", "Low",
           "Fiber cement, fire & weather resistant", "Industry standard fiber cement lap", 95),
        _p("Siding", "James Hardie", "HardiePanel", "Board & Batten",
           [{"name": "Iron Gray", "hex": "#54585c", "tone": "cool"}, {"name": "Charcoal", "hex": "#34373a", "tone": "cool"},
            {"name": "Arctic White", "hex": "#f3f1ec", "tone": "cool"}, {"name": "Aged Pewter", "hex": "#7d7f80", "tone": "cool"}],
           "Matte", ["modern", "farmhouse", "transitional"], "$$$", "30-year", "Low",
           "Vertical board-and-batten modern farmhouse look", "Great for modern/farmhouse accents", 88),
        _p("Siding", "Everlast", "Composite", "Wood-Look Plank",
           [{"name": "Stained Walnut", "hex": "#5b4030", "tone": "warm"}, {"name": "Cedar", "hex": "#9c6a44", "tone": "warm"},
            {"name": "Espresso", "hex": "#3a2c22", "tone": "warm"}],
           "Wood Grain", ["modern", "luxury", "transitional"], "$$$$", "Lifetime", "Very Low",
           "Warm natural wood appearance without upkeep", "Premium warm wood look", 70),
        # Brick / Stone
        _p("Brick / Stone Veneer", "Eldorado Stone", "Stacked Stone", "Dry-Stack Ledgestone",
           [{"name": "Sierra Tan", "hex": "#a89274", "tone": "warm"}, {"name": "Gray Quartzite", "hex": "#8d8f8e", "tone": "cool"},
            {"name": "Autumn Blend", "hex": "#7a6450", "tone": "warm"}],
           "Natural Stone", ["luxury", "craftsman", "transitional", "farmhouse"], "$$$$", "Lifetime", "Very Low",
           "", "Adds high-end texture to base and entry", 81),
        _p("Brick / Stone Veneer", "General Shale", "Painted Brick", "Brick Veneer",
           [{"name": "Pure White", "hex": "#f2efe9", "tone": "cool"}, {"name": "Mushroom", "hex": "#cabfb0", "tone": "warm"},
            {"name": "Charcoal Wash", "hex": "#4d4a47", "tone": "cool"}],
           "Brick", ["traditional", "colonial", "modern", "transitional"], "$$$", "Lifetime", "Low",
           "", "Timeless painted brick", 85),
        # Trim
        _p("Trim", "Azek", "PVC Trim", "Trim Board",
           [{"name": "Bright White", "hex": "#f7f6f2", "tone": "cool"}, {"name": "Black", "hex": "#1b1b1d", "tone": "cool"},
            {"name": "Warm Almond", "hex": "#e3d9c6", "tone": "warm"}],
           "Smooth", ["traditional", "modern", "transitional", "colonial", "craftsman"], "$$", "Lifetime", "Very Low",
           "", "Crisp rot-free trim", 76),
        # Shutters
        _p("Shutters", "Atlantic", "Louvered Shutter", "Louvered",
           [{"name": "Matte Black", "hex": "#1b1b1d", "tone": "cool"}, {"name": "Hartford Green", "hex": "#2f4031", "tone": "cool"},
            {"name": "Bordeaux", "hex": "#5c2230", "tone": "warm"}, {"name": "Charcoal", "hex": "#36393c", "tone": "cool"}],
           "Painted", ["colonial", "traditional", "craftsman"], "$", "20-year", "Low", "",
           "Classic curb-appeal accent", 72),
        # Front Door
        _p("Front Door", "Therma-Tru", "Pulse Smooth", "Entry Door",
           [{"name": "Charcoal", "hex": "#33363a", "tone": "cool"}, {"name": "Navy", "hex": "#27384f", "tone": "cool"},
            {"name": "Tuscan Red", "hex": "#7a2b27", "tone": "warm"}, {"name": "Stained Walnut", "hex": "#4a3526", "tone": "warm"},
            {"name": "Black", "hex": "#19191b", "tone": "cool"}],
           "Smooth / Wood", ["modern", "transitional", "craftsman", "luxury"], "$$$", "25-year", "Low",
           "Energy Star options", "Statement entry door", 83),
        _p("Front Door", "Pella", "Pivot Glass", "Modern Pivot",
           [{"name": "Black + Glass", "hex": "#1c1c1e", "tone": "cool"}, {"name": "Walnut + Glass", "hex": "#4a3526", "tone": "warm"}],
           "Wood & Glass", ["modern", "luxury"], "$$$$", "30-year", "Low", "Insulated glass",
           "Premium oversized entry", 58),
        # Garage
        _p("Garage Door", "Clopay", "Canyon Ridge", "Carriage / Modern",
           [{"name": "White", "hex": "#f1efe9", "tone": "cool"}, {"name": "Black", "hex": "#1c1c1e", "tone": "cool"},
            {"name": "Walnut", "hex": "#4d3526", "tone": "warm"},
            {"name": "Charcoal", "hex": "#3a3d40", "tone": "cool"}],
           "Faux Wood / Steel", ["modern", "craftsman", "transitional", "farmhouse"], "$$$", "20-year", "Low",
           "Insulated R-value options", "Insulated, design-forward", 74),
        # Windows
        _p("Windows", "Andersen", "400 Series", "Double-Hung / Casement",
           [{"name": "Black Frame", "hex": "#1c1c1e", "tone": "cool"}, {"name": "White Frame", "hex": "#f1efe9", "tone": "cool"},
            {"name": "Bronze Frame", "hex": "#4a4034", "tone": "warm"}],
           "Low-E Glass", ["modern", "transitional", "traditional", "colonial"], "$$$", "20-year", "Low",
           "Low-E, energy efficient", "Black frames modernize instantly", 80),
        # Gutters
        _p("Gutters", "LeafGuard", "Seamless K-Style", "Gutter System",
           [{"name": "White", "hex": "#f1efe9", "tone": "cool"}, {"name": "Black", "hex": "#1c1c1e", "tone": "cool"},
            {"name": "Bronze", "hex": "#4a4034", "tone": "warm"}, {"name": "Copper", "hex": "#b46b3a", "tone": "warm"}],
           "Aluminum / Copper", ["traditional", "modern", "transitional"], "$$", "20-year", "Very Low", "",
           "Seamless, clog-resistant", 60),
        # Columns
        _p("Columns & Railings", "Fypon", "Tapered Column", "Porch Column",
           [{"name": "White", "hex": "#f7f6f2", "tone": "cool"}, {"name": "Black", "hex": "#1b1b1d", "tone": "cool"},
            {"name": "Stone Wrap", "hex": "#a89274", "tone": "warm"}],
           "Composite", ["craftsman", "colonial", "traditional", "farmhouse"], "$$", "Lifetime", "Low", "",
           "Defines the entry", 55),
    ]


def recommendations():
    return [
        {"id": "luxury", "title": "Luxury Upgrade Package", "tag": "luxury",
         "desc": "Stone base, warm wood siding, matte black metal roof — designer-grade curb appeal.",
         "preset": "premium", "price_tier": "$$$$"},
        {"id": "modern_contrast", "title": "High-Contrast Curb Appeal", "tag": "modern",
         "desc": "Charcoal board-and-batten, crisp white trim, black windows. Bold and current.",
         "preset": "charcoal", "price_tier": "$$$"},
        {"id": "historic", "title": "Historically Appropriate Palette", "tag": "colonial",
         "desc": "Painted white brick, black shutters, charcoal door — timeless colonial.",
         "preset": "white_brick", "price_tier": "$$$"},
        {"id": "energy", "title": "Energy-Conscious Option Set", "tag": "energy",
         "desc": "Cool-roof copper metal, Low-E black windows, insulated entry. Efficient + striking.",
         "preset": "copper", "price_tier": "$$$$"},
        {"id": "warm_stone", "title": "Warm Natural Stone Entry", "tag": "craftsman",
         "desc": "Natural stacked stone, warm beige siding, stained timber door.",
         "preset": "stone", "price_tier": "$$$$"},
        {"id": "budget", "title": "Budget-Friendly Refresh", "tag": "transitional",
         "desc": "Quality re-side + repaint, new shutters and navy door. Maximum impact, minimal spend.",
         "preset": "budget", "price_tier": "$$"},
    ]


def now():
    return datetime.now(timezone.utc).isoformat()


PRESET_SCENARIOS = [
    {"key": "white_brick", "name": "Classic White Brick", "style": "Colonial",
     "selections": [{"zone": "siding_main", "product": "Painted Brick", "color": "Pure White"},
                    {"zone": "shutters", "product": "Louvered Shutter", "color": "Matte Black"},
                    {"zone": "front_door", "product": "Pulse Smooth", "color": "Charcoal"}],
     "est_low": 38000, "est_high": 52000},
    {"key": "charcoal", "name": "Modern Charcoal Siding", "style": "Modern",
     "selections": [{"zone": "siding_main", "product": "HardiePanel Board & Batten", "color": "Charcoal"},
                    {"zone": "trim", "product": "PVC Trim", "color": "Bright White"},
                    {"zone": "windows", "product": "400 Series", "color": "Black Frame"},
                    {"zone": "front_door", "product": "Pulse Smooth", "color": "Stained Walnut"}],
     "est_low": 44000, "est_high": 61000},
    {"key": "copper", "name": "Copper Roof Accent", "style": "Transitional",
     "selections": [{"zone": "roof", "product": "Standing Seam", "color": "Copper"},
                    {"zone": "siding_main", "product": "HardiePlank", "color": "Light Greige"},
                    {"zone": "gutters", "product": "Seamless K-Style", "color": "Copper"}],
     "est_low": 58000, "est_high": 79000},
    {"key": "stone", "name": "Warm Natural Stone Entry", "style": "Craftsman",
     "selections": [{"zone": "veneer", "product": "Stacked Stone", "color": "Sierra Tan"},
                    {"zone": "siding_main", "product": "HardiePlank", "color": "Khaki Brown"},
                    {"zone": "front_door", "product": "Pulse Smooth", "color": "Stained Walnut"}],
     "est_low": 49000, "est_high": 68000},
    {"key": "budget", "name": "Budget Refresh Option", "style": "Transitional",
     "selections": [{"zone": "siding_main", "product": "HardiePlank", "color": "Light Greige"},
                    {"zone": "shutters", "product": "Louvered Shutter", "color": "Matte Black"},
                    {"zone": "front_door", "product": "Pulse Smooth", "color": "Navy"}],
     "est_low": 21000, "est_high": 32000},
    {"key": "premium", "name": "Premium Renovation Option", "style": "Luxury",
     "selections": [{"zone": "siding_main", "product": "Composite Wood-Look", "color": "Stained Walnut"},
                    {"zone": "veneer", "product": "Stacked Stone", "color": "Gray Quartzite"},
                    {"zone": "roof", "product": "Standing Seam", "color": "Matte Black"},
                    {"zone": "front_door", "product": "Pivot Glass", "color": "Walnut + Glass"},
                    {"zone": "windows", "product": "400 Series", "color": "Black Frame"}],
     "est_low": 92000, "est_high": 138000},
]


async def seed_design(db):
    if await db.design_products.count_documents({}) == 0:
        await db.design_products.insert_many(products())
    prop = await db.properties.find_one(
        {"$or": [
            {"is_demo_fixture": True},
            {"visualization_profile": "central-kentucky-demo-home"},
            {"name": "Central Kentucky Demonstration Home"},
            {"name": "Villa Horizon"},  # legacy seed name during transition
        ]},
        {"_id": 0, "id": 1, "owner_id": 1},
    )
    if not prop:
        return
    pid = prop["id"]
    if await db.design_bases.count_documents({"property_id": pid}) == 0:
        await db.design_bases.insert_one({"property_id": pid, "base_image": BASE_FACADE,
                                          "source": "STRATEX Core aligned façade", "updated_at": now()})
    if await db.design_scenarios.count_documents({"property_id": pid, "is_preset": True}) == 0:
        docs = []
        for s in PRESET_SCENARIOS:
            docs.append({"id": str(uuid.uuid4()), "property_id": pid, "owner_id": prop["owner_id"],
                         "name": s["name"], "style": s["style"], "selections": s["selections"],
                         "preview_url": PRESET_IMG[s["key"]], "base_image": BASE_FACADE,
                         "est_low": s["est_low"], "est_high": s["est_high"], "lighting": "daylight",
                         "notes": "", "is_preset": True, "favorite": s["key"] in ("charcoal", "stone"),
                         "quote_ready": False, "version": 1, "linked_quotes": [], "created_at": now()})
        await db.design_scenarios.insert_many(docs)
