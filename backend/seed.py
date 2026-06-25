"""STRATEX HABITAT demo seed — Villa Horizon homeowner record + contractors + marketplace."""
from datetime import datetime, timezone
import uuid

DT_HOUSE = "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/4693f2f3df9f41fe888c10d8126e3b5dbdbccf85e75111eb0fa3e6b3a774eed7.png"
PROP_THUMB = "https://images.unsplash.com/photo-1767950470198-c9cd97f8ed87?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MTN8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBsdXh1cnklMjB2aWxsYSUyMG5pZ2h0fGVufDB8fHx8MTc4MjQxNDg1NHww&ixlib=rb-4.1.0&q=85"
AV_HOME = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdCUyMHBvcnRyYWl0fGVufDB8fHx8MTc4MjMzOTcwNHww&ixlib=rb-4.1.0&q=85"
AV_C1 = "https://images.unsplash.com/photo-1607503873903-c5e95f80d7b9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdCUyMHBvcnRyYWl0fGVufDB8fHx8MTc4MjMzOTcwNHww&ixlib=rb-4.1.0&q=85"
AV_C2 = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdCUyMHBvcnRyYWl0fGVufDB8fHx8MTc4MjMzOTcwNHww&ixlib=rb-4.1.0&q=85"


def now():
    return datetime.now(timezone.utc).isoformat()


def spark(vals):
    return [{"i": i, "v": v} for i, v in enumerate(vals)]


async def run_seed(db, hash_password):
    if await db.users.find_one({"email": "alex@stratexhabitat.com"}):
        return  # already seeded

    admin_id = str(uuid.uuid4())
    home_id = str(uuid.uuid4())
    c1_user = str(uuid.uuid4())
    c2_user = str(uuid.uuid4())
    c3_user = str(uuid.uuid4())

    await db.users.insert_many([
        {"id": admin_id, "email": "admin@stratexhabitat.com", "password_hash": hash_password("Admin123!"),
         "name": "STRATEX Admin", "role": "executive", "avatar": None, "created_at": now()},
        {"id": home_id, "email": "alex@stratexhabitat.com", "password_hash": hash_password("Demo123!"),
         "name": "Alex Morgan", "role": "homeowner", "avatar": AV_HOME, "created_at": now()},
        {"id": c1_user, "email": "horizon@stratexhabitat.com", "password_hash": hash_password("Demo123!"),
         "name": "Horizon Roofing", "role": "contractor", "avatar": AV_C1, "created_at": now()},
        {"id": c2_user, "email": "peakbuild@stratexhabitat.com", "password_hash": hash_password("Demo123!"),
         "name": "PeakBuild Solutions", "role": "contractor", "avatar": AV_C2, "created_at": now()},
        {"id": c3_user, "email": "lonestar@stratexhabitat.com", "password_hash": hash_password("Demo123!"),
         "name": "Lonestar Roofing Co.", "role": "contractor", "avatar": None, "created_at": now()},
    ])

    prop_id = str(uuid.uuid4())
    await db.properties.insert_one({
        "id": prop_id, "owner_id": home_id, "name": "Villa Horizon", "location": "Austin, TX",
        "status": "Connected", "thumbnail": PROP_THUMB, "twin_image": DT_HOUSE,
        "property_score": 87, "energy_efficiency": {"value": 72, "label": "Good"},
        "water_efficiency": {"value": 64, "label": "Fair"},
        "system_health": {"value": 91, "label": "Excellent"},
        "maintenance_alerts": 3, "last_updated": "Today, 9:41 AM",
        "year_built": 2019, "sqft": 4280, "stories": 2,
        "created_at": now()})

    await db.analytics.insert_one({
        "property_id": prop_id,
        "cards": [
            {"key": "energy_cost", "label": "Monthly Energy Cost", "value": "$186", "change": -8,
             "spark": spark([210, 198, 205, 190, 192, 188, 186])},
            {"key": "water_usage", "label": "Water Usage", "value": "3,274 gal", "change": -6,
             "spark": spark([3600, 3500, 3550, 3400, 3380, 3300, 3274])},
            {"key": "uptime", "label": "System Uptime", "value": "99.2%", "change": 1.2,
             "spark": spark([97.5, 98.1, 98.4, 98.9, 99.0, 99.1, 99.2])},
            {"key": "carbon", "label": "Carbon Footprint", "value": "1.2 ton CO₂", "change": -9,
             "spark": spark([1.5, 1.45, 1.4, 1.35, 1.3, 1.25, 1.2])},
        ]})

    assets = [
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Roof — North Slope", "zone": "Zone 2",
         "area": "456.3 sq ft", "system": "Roofing", "condition": "Fair", "degradation": 24,
         "remaining_life": "8–12 years", "published": True,
         "thumbnail": "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?w=120&q=80"},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "HVAC — Main Unit", "zone": "Mechanical",
         "area": "5 ton", "system": "HVAC", "condition": "Good", "degradation": 12,
         "remaining_life": "10–14 years", "published": True, "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Water Heater", "zone": "Utility",
         "area": "80 gal", "system": "Plumbing", "condition": "Fair", "degradation": 31,
         "remaining_life": "4–6 years", "published": True, "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Solar Array", "zone": "Roof South",
         "area": "9.6 kW", "system": "Electrical", "condition": "Excellent", "degradation": 5,
         "remaining_life": "18–22 years", "published": True, "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Windows — West Facade", "zone": "Envelope",
         "area": "18 units", "system": "Structural", "condition": "Good", "degradation": 15,
         "remaining_life": "12–16 years", "published": True, "thumbnail": None},
    ]
    await db.assets.insert_many(assets)
    roof_id = assets[0]["id"]

    findings = [
        {"id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": roof_id, "asset_name": "Roof — North Slope",
         "title": "Thermal inefficiency detected", "priority": "medium", "seriousness": "medium",
         "category": "Roofing",
         "description": "Heat loss detected in this area. Recommend insulation upgrade to improve efficiency.",
         "impact_energy": "12% Energy Loss", "impact_cost": "$320/yr Est. Cost",
         "recommended_action": "Insulation Upgrade", "action_detail": "Improve R-value and reduce heat transfer.",
         "price_low": 2450, "price_high": 3200, "created_at": now()},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[2]["id"], "asset_name": "Water Heater",
         "title": "Sediment buildup reducing efficiency", "priority": "high", "seriousness": "high",
         "category": "Plumbing",
         "description": "Tank efficiency declining. Flush recommended; unit nearing end of service life.",
         "impact_energy": "8% Energy Loss", "impact_cost": "$140/yr Est. Cost",
         "recommended_action": "Tank Flush + Inspection", "action_detail": "Service and evaluate replacement.",
         "price_low": 180, "price_high": 420, "created_at": now()},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[4]["id"], "asset_name": "Windows — West Facade",
         "title": "Air infiltration at seals", "priority": "low", "seriousness": "low", "category": "Windows",
         "description": "Minor draft detected at west-facing window seals during thermal scan.",
         "impact_energy": "4% Energy Loss", "impact_cost": "$95/yr Est. Cost",
         "recommended_action": "Re-seal Window Frames", "action_detail": "Weatherstripping and caulk refresh.",
         "price_low": 220, "price_high": 480, "created_at": now()},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[1]["id"], "asset_name": "HVAC — Main Unit",
         "title": "Filter restriction trend", "priority": "low", "seriousness": "low", "category": "HVAC",
         "description": "Airflow data indicates filter approaching replacement threshold.",
         "impact_energy": "3% Energy Loss", "impact_cost": "$60/yr Est. Cost",
         "recommended_action": "Replace Filter", "action_detail": "Standard maintenance.",
         "price_low": 40, "price_high": 90, "created_at": now()},
    ]
    # pad to 8 findings shown as badge
    for i in range(4):
        findings.append({"id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[i % 5]["id"],
                         "asset_name": assets[i % 5]["name"],
                         "title": ["Gutter slope variance", "Minor stucco crack", "Deck fastener wear", "Vent flashing aging"][i],
                         "priority": "low", "seriousness": "low", "category": "Structural",
                         "description": "Detected during latest STRATEX Core scan; monitoring recommended.",
                         "impact_energy": "—", "impact_cost": "Monitoring",
                         "recommended_action": "Monitor", "action_detail": "No immediate action required.",
                         "price_low": 0, "price_high": 0, "created_at": now()})
    await db.findings.insert_many(findings)

    await db.maintenance.insert_many([
        {"id": str(uuid.uuid4()), "title": "HVAC seasonal service", "status": "due", "due": "Jul 15, 2026",
         "system": "HVAC", "priority": "medium"},
        {"id": str(uuid.uuid4()), "title": "Water heater flush", "status": "overdue", "due": "Jun 01, 2026",
         "system": "Plumbing", "priority": "high"},
        {"id": str(uuid.uuid4()), "title": "Roof inspection (annual)", "status": "scheduled", "due": "Sep 20, 2026",
         "system": "Roofing", "priority": "low"},
    ])

    await db.insights.insert_many([
        {"id": str(uuid.uuid4()), "title": "Energy use down 8% MoM", "detail": "Solar offset improving net consumption.",
         "trend": "positive"},
        {"id": str(uuid.uuid4()), "title": "Roof zone driving 12% loss", "detail": "Insulation upgrade has highest ROI.",
         "trend": "action"},
        {"id": str(uuid.uuid4()), "title": "Water efficiency below peer avg", "detail": "Irrigation schedule optimization suggested.",
         "trend": "watch"},
    ])

    # Contractors
    contractors = [
        {"id": str(uuid.uuid4()), "owner_user_id": c1_user, "company_name": "Horizon Roofing & Exteriors",
         "description": "Premium roofing, insulation and exterior envelope specialists serving Central Texas.",
         "service_area": "Austin Metro, TX", "license": "TX-RC-44821", "insurance": "Liability $2M / Workers Comp",
         "website": "horizonroofing.example", "phone": "(512) 555-0142", "email": "horizon@stratexhabitat.com",
         "trades": ["Roofing", "Structural", "Siding", "Windows", "Renovation"], "logo": None, "job_photos": [], "external_testimonials": [],
         "public_rating": 4.9, "verified_reviews": 128, "avatar": AV_C1,
         "scorecard": {"performance_grade": "A+", "external_confidence": 92, "responsiveness": 96,
                       "close_rate": 71, "satisfaction": 98, "compliance": 100}, "created_at": now()},
        {"id": str(uuid.uuid4()), "owner_user_id": c2_user, "company_name": "PeakBuild Solutions",
         "description": "Full-service home performance and renovation contractor.",
         "service_area": "Austin & Round Rock, TX", "license": "TX-GC-90233", "insurance": "Liability $1M",
         "website": "peakbuild.example", "phone": "(512) 555-0199", "email": "peakbuild@stratexhabitat.com",
         "trades": ["Roofing", "HVAC", "Plumbing", "Renovation", "Upgrade", "Front Door"], "logo": None, "job_photos": [], "external_testimonials": [],
         "public_rating": 4.7, "verified_reviews": 86, "avatar": AV_C2,
         "scorecard": {"performance_grade": "A", "external_confidence": 84, "responsiveness": 88,
                       "close_rate": 63, "satisfaction": 93, "compliance": 96}, "created_at": now()},
        {"id": str(uuid.uuid4()), "owner_user_id": c3_user, "company_name": "Lonestar Roofing Co.",
         "description": "Reliable residential roofing and repair across Texas.",
         "service_area": "Greater Austin, TX", "license": "TX-RC-30118", "insurance": "Liability $1M",
         "website": "lonestar.example", "phone": "(512) 555-0177", "email": "lonestar@stratexhabitat.com",
         "trades": ["Roofing"], "logo": None, "job_photos": [], "external_testimonials": [
             {"id": str(uuid.uuid4()), "source": "Google", "url": "google.com/...", "text": "Great fast service",
              "rating": 5, "project_date": "2025-11-02", "status": "pending"}],
         "public_rating": 4.6, "verified_reviews": 54, "avatar": None,
         "scorecard": {"performance_grade": "B+", "external_confidence": 70, "responsiveness": 79,
                       "close_rate": 58, "satisfaction": 89, "compliance": 92}, "created_at": now()},
    ]
    await db.contractors.insert_many(contractors)

    # A quote tied to the roof finding with the 3 contractor responses (Top Contractor Quotes in image)
    qid = str(uuid.uuid4())
    await db.quotes.insert_one({
        "id": qid, "owner_id": home_id, "owner_name": "Alex Morgan", "property_id": prop_id,
        "property_name": "Villa Horizon", "finding_id": findings[0]["id"],
        "title": "Insulation Upgrade — Roof North Slope", "category": "Roofing",
        "description": "Improve R-value and reduce heat transfer.", "seriousness": "medium",
        "target_timeframe": "30 days", "desired_start": "Jul 2026", "status": "responded",
        "routed_to": [contractors[0]["id"], contractors[1]["id"], contractors[2]["id"]],
        "created_at": now(),
        "contractor_responses": [
            {"contractor_id": contractors[0]["id"], "contractor_name": "Horizon Roofing & Exteriors",
             "rating": 4.9, "price_low": 2680, "price_high": 2780, "best_match": True,
             "scope_notes": "Full re-insulation + thermal verification.", "timeline": "2 days",
             "estimated_start": "Jul 8, 2026", "created_at": now(), "avatar": AV_C1, "price_display": "$2,780"},
            {"contractor_id": contractors[1]["id"], "contractor_name": "PeakBuild Solutions",
             "rating": 4.7, "price_low": 2850, "price_high": 2950, "best_match": False,
             "scope_notes": "Insulation + minor flashing.", "timeline": "3 days",
             "estimated_start": "Jul 14, 2026", "created_at": now(), "avatar": AV_C2, "price_display": "$2,950"},
            {"contractor_id": contractors[2]["id"], "contractor_name": "Lonestar Roofing Co.",
             "rating": 4.6, "price_low": 3100, "price_high": 3210, "best_match": False,
             "scope_notes": "Standard insulation package.", "timeline": "2 days",
             "estimated_start": "Jul 20, 2026", "created_at": now(), "avatar": None, "price_display": "$3,210"},
        ]})

    # second open quote
    await db.quotes.insert_one({
        "id": str(uuid.uuid4()), "owner_id": home_id, "owner_name": "Alex Morgan", "property_id": prop_id,
        "property_name": "Villa Horizon", "finding_id": findings[1]["id"],
        "title": "Water Heater Service", "category": "Plumbing", "description": "Flush and inspection.",
        "seriousness": "high", "target_timeframe": "14 days", "desired_start": "Jun 2026", "status": "open",
        "routed_to": [contractors[1]["id"]], "created_at": now(), "contractor_responses": []})

    await db.reviews.insert_many([
        {"id": str(uuid.uuid4()), "contractor_id": contractors[0]["id"], "author_id": home_id,
         "author_name": "Alex Morgan", "rating": 5, "title": "Flawless roof insulation",
         "body": "Horizon was precise and fast. Thermal scan confirmed the fix.", "photos": [],
         "source": "stratex_verified", "verified": True, "created_at": now()},
        {"id": str(uuid.uuid4()), "contractor_id": contractors[1]["id"], "author_id": home_id,
         "author_name": "Jordan Lee", "rating": 4, "title": "Solid HVAC work",
         "body": "Good communication, on schedule.", "photos": [],
         "source": "stratex_verified", "verified": True, "created_at": now()},
    ])

    await db.documents.insert_many([
        {"id": str(uuid.uuid4()), "name": "Property Disclosure 2026.pdf", "type": "document", "size": "1.2 MB",
         "created_at": now()},
        {"id": str(uuid.uuid4()), "name": "Insurance Policy.pdf", "type": "document", "size": "880 KB",
         "created_at": now()},
        {"id": str(uuid.uuid4()), "name": "Solar Warranty.pdf", "type": "document", "size": "640 KB",
         "created_at": now()},
    ])

    await db.reports.insert_many([
        {"id": str(uuid.uuid4()), "name": "Full Property Scan — v3", "type": "scan", "scan_date": "2026-06-10",
         "version": "v3", "status": "approved", "source": "STRATEX Core"},
        {"id": str(uuid.uuid4()), "name": "Thermal Imaging Report", "type": "thermal", "scan_date": "2026-06-10",
         "version": "v3", "status": "approved", "source": "STRATEX Core"},
        {"id": str(uuid.uuid4()), "name": "Energy Performance Report", "type": "energy", "scan_date": "2026-05-02",
         "version": "v2", "status": "approved", "source": "STRATEX Core"},
    ])

    await db.sync_log.insert_one({"id": str(uuid.uuid4()), "ts": now(), "by": admin_id,
                                  "action": "publish", "source": "stratex_core"})
