"""
STRATEX HABITAT demo seed — Central Kentucky Demonstration Home + contractors.

Property and findings are explicitly marked demo/sample_only. They are not
Passport-approved property truth and must never be treated as LiDAR detections.
"""
from datetime import datetime, timezone
import uuid

from demo_property import (
    DEMO_PROPERTY_NAME,
    DEMO_TWIN_IMAGE,
    DEMO_THUMB,
    demo_property_fields,
    finding_demo_fields,
)

DT_HOUSE = DEMO_TWIN_IMAGE
PROP_THUMB = DEMO_THUMB
AV_HOME = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdCUyMHBvcnRyYWl0fGVufDB8fHx8MTc4MjMzOTcwNHww&ixlib=rb-4.1.0&q=85"
AV_C1 = "https://images.unsplash.com/photo-1607503873903-c5e95f80d7b9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdCUyMHBvcnRyYWl0fGVufDB8fHx8MTc4MjMzOTcwNHww&ixlib=rb-4.1.0&q=85"
AV_C2 = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdCUyMHBvcnRyYWl0fGVufDB8fHx8MTc4MjMzOTcwNHww&ixlib=rb-4.1.0&q=85"


def now():
    return datetime.now(timezone.utc).isoformat()


def spark(vals):
    return [{"i": i, "v": v} for i, v in enumerate(vals)]


def _demo_finding(base: dict) -> dict:
    out = {**base, **finding_demo_fields()}
    return out


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
    prop_doc = {
        "id": prop_id,
        "owner_id": home_id,
        "status": "Connected",
        "property_score": 87,
        "energy_efficiency": {"value": 72, "label": "Good"},
        "water_efficiency": {"value": 64, "label": "Fair"},
        "system_health": {"value": 91, "label": "Excellent"},
        "maintenance_alerts": 3,
        "last_updated": "Today, 9:41 AM",
        "created_at": now(),
        **demo_property_fields(),
    }
    await db.properties.insert_one(prop_doc)

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
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Roof — Front Slope", "zone": "Zone 2",
         "area": "sample", "system": "Roofing", "condition": "Fair", "degradation": 24,
         "remaining_life": "sample only", "published": True,
         "data_origin": "demo", "truth_status": "sample_only",
         "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "HVAC — Main Unit", "zone": "Mechanical",
         "area": "sample", "system": "HVAC", "condition": "Good", "degradation": 12,
         "remaining_life": "sample only", "published": True,
         "data_origin": "demo", "truth_status": "sample_only", "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Water Heater", "zone": "Utility",
         "area": "sample", "system": "Plumbing", "condition": "Fair", "degradation": 31,
         "remaining_life": "sample only", "published": True,
         "data_origin": "demo", "truth_status": "sample_only", "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Electrical Service", "zone": "Utility",
         "area": "sample", "system": "Electrical", "condition": "Good", "degradation": 10,
         "remaining_life": "sample only", "published": True,
         "data_origin": "demo", "truth_status": "sample_only", "thumbnail": None},
        {"id": str(uuid.uuid4()), "property_id": prop_id, "name": "Windows — Front Facade", "zone": "Envelope",
         "area": "sample", "system": "Structural", "condition": "Good", "degradation": 15,
         "remaining_life": "sample only", "published": True,
         "data_origin": "demo", "truth_status": "sample_only", "thumbnail": None},
    ]
    await db.assets.insert_many(assets)
    roof_id = assets[0]["id"]

    # Sample-only illustrative findings — not approved, not LiDAR-detected.
    # Soft language; Inspector on /twin prefers empty state over these.
    findings = [
        _demo_finding({
            "id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": roof_id,
            "asset_name": "Roof — Front Slope",
            "title": "Example roof maintenance category", "priority": "medium", "seriousness": "medium",
            "category": "Roofing",
            "description": "Sample maintenance category for illustration only. Not an approved property finding.",
            "impact_energy": "Sample", "impact_cost": "Sample",
            "recommended_action": "Example review category", "action_detail": "Awaiting verified property scan.",
            "price_low": 0, "price_high": 0, "created_at": now(),
        }),
        _demo_finding({
            "id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[2]["id"],
            "asset_name": "Water Heater",
            "title": "Example water-heater maintenance category", "priority": "low", "seriousness": "low",
            "category": "Plumbing",
            "description": "Demo/sample only. Not an approved property finding.",
            "impact_energy": "Sample", "impact_cost": "Sample",
            "recommended_action": "Example review category", "action_detail": "Awaiting verified property scan.",
            "price_low": 0, "price_high": 0, "created_at": now(),
        }),
        _demo_finding({
            "id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[4]["id"],
            "asset_name": "Windows — Front Facade",
            "title": "Example window envelope category", "priority": "low", "seriousness": "low",
            "category": "Windows",
            "description": "Demo/sample only. Not an approved property finding.",
            "impact_energy": "Sample", "impact_cost": "Sample",
            "recommended_action": "Example review category", "action_detail": "Awaiting verified property scan.",
            "price_low": 0, "price_high": 0, "created_at": now(),
        }),
        _demo_finding({
            "id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[1]["id"],
            "asset_name": "HVAC — Main Unit",
            "title": "Example HVAC maintenance category", "priority": "low", "seriousness": "low",
            "category": "HVAC",
            "description": "Demo/sample only. Not an approved property finding.",
            "impact_energy": "Sample", "impact_cost": "Sample",
            "recommended_action": "Example review category", "action_detail": "Awaiting verified property scan.",
            "price_low": 0, "price_high": 0, "created_at": now(),
        }),
    ]
    for i in range(4):
        findings.append(_demo_finding({
            "id": str(uuid.uuid4()), "property_id": prop_id, "asset_id": assets[i % 5]["id"],
            "asset_name": assets[i % 5]["name"],
            "title": [
                "Example gutter category", "Example envelope category",
                "Example drainage category", "Example ventilation category",
            ][i],
            "priority": "low", "seriousness": "low", "category": "Structural",
            "description": "Demo/sample only. Not an approved property finding.",
            "impact_energy": "—", "impact_cost": "Sample",
            "recommended_action": "Monitor (sample)", "action_detail": "No verified action required.",
            "price_low": 0, "price_high": 0, "created_at": now(),
        }))
    await db.findings.insert_many(findings)

    await db.maintenance.insert_many([
        {"id": str(uuid.uuid4()), "title": "HVAC seasonal service (sample)", "status": "due", "due": "Jul 15, 2026",
         "system": "HVAC", "priority": "medium", "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "title": "Gutter cleaning (sample)", "status": "scheduled", "due": "Oct 01, 2026",
         "system": "Drainage", "priority": "low", "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "title": "Roof inspection (sample)", "status": "scheduled", "due": "Sep 20, 2026",
         "system": "Roofing", "priority": "low", "data_origin": "demo"},
    ])

    await db.insights.insert_many([
        {"id": str(uuid.uuid4()), "title": "Sample energy insight", "detail": "Demo/sample only — not verified.",
         "trend": "positive", "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "title": "Sample maintenance insight", "detail": "Awaiting verified property scan.",
         "trend": "action", "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "title": "Sample water insight", "detail": "Demo/sample only — not verified.",
         "trend": "watch", "data_origin": "demo"},
    ])

    contractors = [
        {"id": str(uuid.uuid4()), "owner_user_id": c1_user, "company_name": "Horizon Roofing & Exteriors",
         "description": "Premium roofing and exterior envelope specialists (demo contractor profile).",
         "service_area": "Central Kentucky (sample)", "license": "KY-DEMO-44821", "insurance": "Liability $2M / Workers Comp",
         "website": "horizonroofing.example", "phone": "(859) 555-0142", "email": "horizon@stratexhabitat.com",
         "trades": ["Roofing", "Structural", "Siding", "Windows", "Renovation"], "logo": None, "job_photos": [], "external_testimonials": [],
         "public_rating": 4.9, "verified_reviews": 128, "avatar": AV_C1,
         "scorecard": {"performance_grade": "A+", "external_confidence": 92, "responsiveness": 96,
                       "close_rate": 71, "satisfaction": 98, "compliance": 100}, "created_at": now()},
        {"id": str(uuid.uuid4()), "owner_user_id": c2_user, "company_name": "PeakBuild Solutions",
         "description": "Full-service home performance contractor (demo profile).",
         "service_area": "Lexington & Central Kentucky (sample)", "license": "KY-DEMO-90233", "insurance": "Liability $1M",
         "website": "peakbuild.example", "phone": "(859) 555-0199", "email": "peakbuild@stratexhabitat.com",
         "trades": ["Roofing", "HVAC", "Plumbing", "Renovation", "Upgrade", "Front Door"], "logo": None, "job_photos": [], "external_testimonials": [],
         "public_rating": 4.7, "verified_reviews": 86, "avatar": AV_C2,
         "scorecard": {"performance_grade": "A", "external_confidence": 84, "responsiveness": 88,
                       "close_rate": 63, "satisfaction": 93, "compliance": 96}, "created_at": now()},
        {"id": str(uuid.uuid4()), "owner_user_id": c3_user, "company_name": "Bluegrass Roofing Co.",
         "description": "Residential roofing demo contractor profile.",
         "service_area": "Central Kentucky (sample)", "license": "KY-DEMO-30118", "insurance": "Liability $1M",
         "website": "bluegrass.example", "phone": "(859) 555-0177", "email": "lonestar@stratexhabitat.com",
         "trades": ["Roofing"], "logo": None, "job_photos": [], "external_testimonials": [
             {"id": str(uuid.uuid4()), "source": "Google", "url": "google.com/...", "text": "Great fast service",
              "rating": 5, "project_date": "2025-11-02", "status": "pending"}],
         "public_rating": 4.6, "verified_reviews": 54, "avatar": None,
         "scorecard": {"performance_grade": "B+", "external_confidence": 70, "responsiveness": 79,
                       "close_rate": 58, "satisfaction": 89, "compliance": 92}, "created_at": now()},
    ]
    await db.contractors.insert_many(contractors)

    # Quotes remain for marketplace UX; prices are sample placeholders (0 finding price).
    qid = str(uuid.uuid4())
    await db.quotes.insert_one({
        "id": qid, "owner_id": home_id, "owner_name": "Alex Morgan", "property_id": prop_id,
        "property_name": DEMO_PROPERTY_NAME, "finding_id": findings[0]["id"],
        "title": "Example roof review category", "category": "Roofing",
        "description": "Demo/sample only — not an approved scope.", "seriousness": "medium",
        "target_timeframe": "30 days", "desired_start": "Jul 2026", "status": "responded",
        "data_origin": "demo", "truth_status": "sample_only",
        "routed_to": [contractors[0]["id"], contractors[1]["id"], contractors[2]["id"]],
        "created_at": now(),
        "contractor_responses": [
            {"contractor_id": contractors[0]["id"], "contractor_name": "Horizon Roofing & Exteriors",
             "rating": 4.9, "price_low": 2680, "price_high": 2780, "best_match": True,
             "scope_notes": "Sample quote only.", "timeline": "2 days",
             "estimated_start": "Jul 8, 2026", "created_at": now(), "avatar": AV_C1, "price_display": "$2,780"},
            {"contractor_id": contractors[1]["id"], "contractor_name": "PeakBuild Solutions",
             "rating": 4.7, "price_low": 2850, "price_high": 2950, "best_match": False,
             "scope_notes": "Sample quote only.", "timeline": "3 days",
             "estimated_start": "Jul 14, 2026", "created_at": now(), "avatar": AV_C2, "price_display": "$2,950"},
            {"contractor_id": contractors[2]["id"], "contractor_name": "Bluegrass Roofing Co.",
             "rating": 4.6, "price_low": 3100, "price_high": 3210, "best_match": False,
             "scope_notes": "Sample quote only.", "timeline": "2 days",
             "estimated_start": "Jul 20, 2026", "created_at": now(), "avatar": None, "price_display": "$3,210"},
        ]})

    await db.quotes.insert_one({
        "id": str(uuid.uuid4()), "owner_id": home_id, "owner_name": "Alex Morgan", "property_id": prop_id,
        "property_name": DEMO_PROPERTY_NAME, "finding_id": findings[1]["id"],
        "title": "Example water-heater review", "category": "Plumbing",
        "description": "Demo/sample only.",
        "seriousness": "low", "target_timeframe": "14 days", "desired_start": "Jun 2026", "status": "open",
        "data_origin": "demo", "truth_status": "sample_only",
        "routed_to": [contractors[1]["id"]], "created_at": now(), "contractor_responses": []})

    await db.reviews.insert_many([
        {"id": str(uuid.uuid4()), "contractor_id": contractors[0]["id"], "author_id": home_id,
         "author_name": "Alex Morgan", "rating": 5, "title": "Sample verified-style review",
         "body": "Demo/sample review content only.", "photos": [],
         "source": "stratex_verified", "verified": True, "created_at": now()},
        {"id": str(uuid.uuid4()), "contractor_id": contractors[1]["id"], "author_id": home_id,
         "author_name": "Jordan Lee", "rating": 4, "title": "Sample review",
         "body": "Demo/sample review content only.", "photos": [],
         "source": "stratex_verified", "verified": True, "created_at": now()},
    ])

    await db.documents.insert_many([
        {"id": str(uuid.uuid4()), "name": "Sample Property Disclosure.pdf", "type": "document", "size": "1.2 MB",
         "created_at": now(), "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "name": "Sample Insurance Policy.pdf", "type": "document", "size": "880 KB",
         "created_at": now(), "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "name": "Sample Warranty.pdf", "type": "document", "size": "640 KB",
         "created_at": now(), "data_origin": "demo"},
    ])

    await db.reports.insert_many([
        {"id": str(uuid.uuid4()), "name": "Sample Property Overview — demo", "type": "scan", "scan_date": "2026-06-10",
         "version": "demo", "status": "sample_only", "source": "demo", "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "name": "Sample Thermal Category — demo", "type": "thermal", "scan_date": "2026-06-10",
         "version": "demo", "status": "sample_only", "source": "demo", "data_origin": "demo"},
        {"id": str(uuid.uuid4()), "name": "Sample Energy Category — demo", "type": "energy", "scan_date": "2026-05-02",
         "version": "demo", "status": "sample_only", "source": "demo", "data_origin": "demo"},
    ])

    await db.sync_log.insert_one({"id": str(uuid.uuid4()), "ts": now(), "by": admin_id,
                                  "action": "publish", "source": "stratex_core"})
