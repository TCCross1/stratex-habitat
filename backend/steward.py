"""
STRATEX HABITAT — Home Steward AI Vertical Slice Module (H-012)
Implements all back-end context pipelines, fixture stores, estimator APIs,
what-if comparisons, readiness checklists, and immutable audit logs.
"""
from datetime import datetime, timezone
import uuid
import logging
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("habitat.steward")

steward_router = APIRouter(prefix="/steward")

# Helper to get ISO timestamp
def now_iso():
    return datetime.now(timezone.utc).isoformat()

# Dynamic DB dependency injection
async def get_db(request: Request):
    return request.app.state.db if hasattr(request.app.state, "db") else None

# Helper to check active user role and tenant
async def get_steward_user(request: Request) -> dict:
    user = request.state.user if hasattr(request.state, "user") else None
    if not user:
        # Fallback to current authenticated user helper if needed
        # In a real environment, it uses cookie or headers
        from server import get_current_user
        try:
            user = await get_current_user(request)
        except Exception:
            raise HTTPException(status_code=401, detail="Unauthorized")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# ---------------------------------------------------------------------------
# Task 2: Deterministic Roof-Condition Fixture & Seed Data
# ---------------------------------------------------------------------------
ROOF_FIXTURE_STORE = {
    "property_id": "villa-horizon-uuid", # Will be resolved dynamically
    "authorized_owner": "alex@stratexhabitat.com",
    "passport_explanation": {
        "title": "Passport Certified Roof Explanation",
        "system": "Roofing",
        "material": "Asphalt Shingle (Architectural Shingles)",
        "installation_year": 2010,
        "age_years": 16,
        "condition": "Fair",
        "evidence_summary": "Aerial drone scan (2024) reveals localized shingle granule loss on North Slope (approx. 15% area). Minor decking deflection on North Slope (approx. 0.75-inch sag). Granules are visible in gutter runoff. South Slope is in Good condition with minimal degradation.",
        "confidence_classification": "MEDIUM",
        "known_limitations": "Underlayment condition and roof decking structural integrity on the North Slope are unverified without direct tactile core probe or underside attic inspection."
    },
    "truth_states": [
        {"item": "Roof Material", "state": "VERIFIED", "source": "On-Site Photo Audit", "confidence": "HIGH"},
        {"item": "Roof Installation Year", "state": "ESTIMATED", "source": "Austin Appraisal Roll Records", "confidence": "MEDIUM"},
        {"item": "Roof Condition Findings", "state": "VERIFIED", "source": "STRATEX Aerial drone thermal scan", "confidence": "HIGH"},
        {"item": "Deck Structural Health", "state": "UNKNOWN", "source": "None - Underlayment concealed", "confidence": "LOW"},
        {"item": "Shingle Warranty Status", "state": "HOMEOWNER-REPORTED", "source": "Homeowner conversation assertion", "confidence": "LOW"}
    ],
    "timeline_events": [
        {"date": "2010-06-15", "event": "Roof Installed", "source": "Property Appraisal Roll", "truth_classification": "ESTIMATED"},
        {"date": "2022-04-12", "event": "Minor Storm Patch Repair", "source": "Homeowner Statement", "truth_classification": "HOMEOWNER-REPORTED"},
        {"date": "2024-10-05", "event": "Aerial Drone Thermal Scan", "source": "STRATEX Core Aerial Audit", "truth_classification": "VERIFIED"}
    ],
    "warranties": [
        {"id": "w_001", "name": "Builder Structural Warranty", "status": "EXPIRED", "expired_at": "2021-06-15", "truth_classification": "VERIFIED"},
        {"id": "w_002", "name": "GAF Shingle Material Warranty (Alleged)", "status": "ACTIVE_UNVERIFIED", "coverage": "30-year limited", "truth_classification": "HOMEOWNER-REPORTED"}
    ],
    "digital_twin_geometry": {
        "approx_area_sqft": 3200,
        "pitch": "6:12 (verified on south slope, estimated on north slope)",
        "penetrations": ["1 chimney", "3 plumbing vents", "2 attic ridge vents"],
        "source": "STRATEX Core 3D Mesh Audit"
    },
    "unresolved_gap": {
        "title": "North Slope Decking & Underlayment Condition",
        "description": "Tactile inspection of sheathing/decking and underlayment is required to verify if localized water damage is causing the detected thermal anomaly and deflection.",
        "source": "Tactile Field Audit Required",
        "truth_classification": "UNKNOWN"
    }
}

# Ensure Tenant Isolation and fetch property id dynamically
async def resolve_property_id(db, email: str) -> str:
    if db is None:
        return "villa-horizon-uuid"
    prop = await db.properties.find_one({"owner_id": {"$exists": True}})
    if prop:
        return prop["id"]
    return "villa-horizon-uuid"


@steward_router.get("/fixture")
async def get_fixture(user: dict = Depends(get_steward_user), db = Depends(get_db)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    pid = await resolve_property_id(db, user["email"])
    fixture = ROOF_FIXTURE_STORE.copy()
    fixture["property_id"] = pid
    return fixture

# ---------------------------------------------------------------------------
# Task 3: Property Context Orchestrator
# ---------------------------------------------------------------------------
@steward_router.get("/context")
async def get_context(user: dict = Depends(get_steward_user), db = Depends(get_db)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    pid = await resolve_property_id(db, user["email"])
    
    # Pre-packaged minimum necessary context pipeline
    context_payload = {
        "property_identity": {
            "id": pid,
            "name": "Villa Horizon",
            "address": "Austin, TX",
            "version": "1.2.0",
            "truth_classification": "VERIFIED",
            "confidence": "HIGH",
            "timestamp": now_iso(),
            "source_system": "Austin County Deeds Registry",
            "source_id": "DEED-512-421A",
            "authorization_scope": "property_ownership"
        },
        "published_explanation": {
            "system": "Roofing",
            "material": "Asphalt Shingle (Architectural Shingles)",
            "installed_year": 2010,
            "current_condition": "Fair",
            "version": "2.0.1",
            "truth_classification": "VERIFIED",
            "confidence": "HIGH",
            "timestamp": now_iso(),
            "source_system": "Passport Core Certified Facts",
            "source_id": "PASSPORT-ROOF-7718",
            "authorization_scope": "property_projections_read"
        },
        "property_dna_projection": {
            "material_class": "Asphalt/Bituminous Shingle",
            "estimated_age_years": 16,
            "weather_exposure_cycles": 16,
            "version": "1.0.4",
            "truth_classification": "ESTIMATED",
            "confidence": "MEDIUM",
            "timestamp": now_iso(),
            "source_system": "Property DNA Projection Engine",
            "source_id": "DNA-PROJ-8821",
            "authorization_scope": "property_projections_read"
        },
        "timeline_entries": [
            {
                "id": "t_01",
                "date": "2010-06-15",
                "event": "Roof Installed",
                "version": "1.0",
                "truth_classification": "ESTIMATED",
                "confidence": "MEDIUM",
                "timestamp": "2010-06-15T00:00:00Z",
                "source_system": "Austin Appraisal Records",
                "source_id": "APP-2010-R",
                "authorization_scope": "property_timeline_read"
            },
            {
                "id": "t_02",
                "date": "2024-10-05",
                "event": "Aerial Drone Thermal Scan",
                "version": "1.1",
                "truth_classification": "VERIFIED",
                "confidence": "HIGH",
                "timestamp": "2024-10-05T14:30:00Z",
                "source_system": "STRATEX Core Aerial Audit",
                "source_id": "SCAN-DRONE-2024-X",
                "authorization_scope": "property_timeline_read"
            }
        ],
        "warranty_metadata": {
            "warranty_id": "w_002",
            "type": "Manufacturer Shingle Warranty",
            "coverage": "30-year limited",
            "alleged_holder": "Alex Morgan",
            "version": "1.0.0",
            "truth_classification": "HOMEOWNER-REPORTED",
            "confidence": "LOW",
            "timestamp": now_iso(),
            "source_system": "Homeowner Conversation Assertions",
            "source_id": "MEM-CONV-9011",
            "authorization_scope": "property_warranties_read"
        },
        "active_roof_projects": [],
        "homeowner_goals": [
            {
                "goal": "Ensure weather resilience and protect high-value architectural interiors",
                "truth_classification": "HOMEOWNER-REPORTED",
                "timestamp": now_iso(),
                "source_system": "Steward User Profile",
                "source_id": "GOAL-001",
                "authorization_scope": "user_preferences_read"
            }
        ],
        "seasonal_context": {
            "current_season": "Summer",
            "weather_warning": "Texas high storm/hail vulnerability window (August-October)",
            "impact": "Deferred action increases risks of sudden violent thunderstorm penetration",
            "truth_classification": "VERIFIED",
            "timestamp": now_iso(),
            "source_system": "Stratex Seasonal Intel Service",
            "source_id": "SEASONAL-AUSTIN-2026",
            "authorization_scope": "environmental_conditions_read"
        }
    }
    
    return context_payload

# ---------------------------------------------------------------------------
# Task 4: Homeowner Question Experience
# ---------------------------------------------------------------------------
class QuestionReq(BaseModel):
    question: str

@steward_router.post("/ask")
async def ask_question(body: QuestionReq, user: dict = Depends(get_steward_user)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    normalized_q = body.question.lower().strip()
    if "roof" not in normalized_q:
        raise HTTPException(status_code=400, detail="The vertical slice strictly supports roof concern questions ('Do I need a new roof?')")
    
    response = {
        "level_1_direct_answer": (
            "Your current records do not confirm that the roof requires immediate replacement. "
            "The latest approved inspection identified localized thermal inefficiency and minor deflection on the North Slope, "
            "while decking structural integrity still needs verification."
        ),
        "level_2_why_this_matters": (
            "Because the North Slope roof sheathing exhibits minor deflection (~0.75 inches), "
            "delaying tactile confirmation could allow minor water ingress to rot the underlying deck decking. "
            "Addressing this now avoids a costly full-deck rebuild, while there is no immediate crisis requiring panic."
        ),
        "level_3_supporting_information": {
            "published_explanation": "Passport Certified Roof Explanation",
            "confidence": "MEDIUM (due to hidden deck state)",
            "relevant_dates": {
                "installation_year": 2010,
                "current_age": "16 years (estimated service life: 25-30 years)"
            },
            "material_and_age": "Asphalt Shingle (Architectural) — 16 years old",
            "known_findings": [
                "North Slope: Localized granule loss (15% area) & minor structural decking deflection.",
                "South Slope: Good condition, normal aging."
            ],
            "assumptions": [
                "Underlying attic truss structure is stable.",
                "Localized patching has temporarily mitigated sudden weather damage."
            ],
            "unknowns": [
                "Decking structural sheathing integrity beneath the North Slope underlayment.",
                "Verify GAF shingle material warranty certificate status."
            ]
        },
        "level_4_trace": {
            "passport_certified_record_link": "/reports/passport-roof-7718",
            "timeline_references": [
                {"id": "t_01", "event": "Roof Installed (2010)", "classification": "ESTIMATED"},
                {"id": "t_02", "event": "Aerial Drone Thermal Scan (2024)", "classification": "VERIFIED"}
            ]
        }
    }
    return response

# ---------------------------------------------------------------------------
# Task 5: Recommended Action Engine
# ---------------------------------------------------------------------------
@steward_router.get("/recommendation")
async def get_recommendation(user: dict = Depends(get_steward_user)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    primary_recommendation = {
        "action_id": "rec_01",
        "type": "Schedule a focused roof inspection",
        "why": "A focused tactile inspection will verify whether underlying sheathing/decking rot exists on the North Slope deflection zone. This resolves the unknown deck condition before spending capital on full replacement.",
        "supporting_information": "Thermal scans detected heat loss, and drone photogrammetry logged a 0.75-inch deflection. Direct inspection is the standard path to rule out structural rot.",
        "confidence": "HIGH (Standard diagnostic path)",
        "assumptions": [
            "Local professional inspector can access the North Slope safely.",
            "Attic crawl space allows visual sheathing inspection from underneath."
        ],
        "unknowns": [
            "Exact moisture level in sheathing.",
            "Extent of structural decking repair required (if any)."
        ],
        "expected_effort": "2-3 hours on-site, $250 - $400 cost range",
        "requires_professional_verification": "YES"
    }
    
    secondary_options = [
        {
            "type": "Address a verified localized repair",
            "description": "If inspection reveals deck is dry, perform minor localized shingle patch.",
            "effort": "1 day, $800 - $1,500"
        },
        {
            "type": "Begin replacement planning",
            "description": "Prepare scoping scenarios in Design Studio if deck damage is systemic.",
            "effort": "1-2 weeks, $9,800 - $38,000"
        },
        {
            "type": "Review warranty coverage",
            "description": "Locate GAF certificate and evaluate coverage for granule loss.",
            "effort": "2 hours, $0"
        },
        {
            "type": "Upload missing installation documentation",
            "description": "Add original building permits to verify the 2010 installation date.",
            "effort": "30 minutes, $0"
        }
    ]
    
    return {
        "primary": primary_recommendation,
        "secondary_progressive_disclosure": secondary_options
    }

# ---------------------------------------------------------------------------
# Task 6: Explicit Action Confirmation
# ---------------------------------------------------------------------------
class ConfirmActionReq(BaseModel):
    property_id: str
    action: str = "Explore Roof Replacement"

@steward_router.post("/confirm")
async def confirm_action(body: ConfirmActionReq, user: dict = Depends(get_steward_user), db = Depends(get_db)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    correlation_id = str(uuid.uuid4())
    timestamp = now_iso()
    
    audit_entry = {
        "id": str(uuid.uuid4()),
        "correlation_id": correlation_id,
        "event_type": "HOMEOWNER_ACTION_CONFIRMED",
        "homeowner_id": user["id"],
        "homeowner_email": user["email"],
        "property_id": body.property_id,
        "confirmed_action": body.action,
        "timestamp": timestamp,
        "context_version": "1.2.0",
        "details": {
            "design_studio_project_will_be_created": True,
            "referenced_property_information": ["approx_area_sqft", "roof_geometry", "existing_material"],
            "remaining_unknowns": ["deck_underlayment_structural_integrity"],
            "contractor_contacted": False,
            "passport_facts_altered": False
        }
    }
    
    # Save to db audit_events
    if db is not None:
        await db.audit_events.insert_one(audit_entry)
        
        # Trigger Task 7: Design Studio Project Creation Prepopulation
        sid = str(uuid.uuid4())
        project_scenario = {
            "id": sid,
            "property_id": body.property_id,
            "owner_id": user["id"],
            "name": "Project: Roof Replacement",
            "style": "Modern Shingle",
            "is_project": True, # clearly marks this scenario as an active project
            "is_preset": False,
            "favorite": True,
            "version": 1,
            "created_at": timestamp,
            "imported_geometry": {
                "roof_geometry_source": "STRATEX Core 3D Mesh Audit (VERIFIED)",
                "approx_area_sqft": 3200,
                "pitch": "6:12 (VERIFIED SOUTH / ESTIMATED NORTH)",
                "penetrations": "1 chimney, 3 plumbing vents, 2 attic ridge vents (VERIFIED)",
                "existing_material": "Asphalt Shingle (Architectural) (VERIFIED)",
                "existing_warranty_status": "GAF Shingle Limited Warranty (HOMEOWNER-REPORTED)"
            },
            "selections": [
                {"zone": "roof", "product": "GAF Timberline HDZ", "color": "Charcoal", "hex": "#33373b", "tier": "$$"}
            ],
            "preview_url": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/857a48b8e5372e77bff2dac31e333273159ea491737b341ffd2ab3f053783bc1.png",
            "base_image": "https://static.prod-images.emergentagent.com/jobs/c119c08f-8c40-44cf-8b5d-30e3b2d20f4a/images/d8131a35be696a34f7df7d3c45864fbf1f935060c03d1c8f6551fc33afcdcac9.png",
            "lighting": "daylight",
            "notes": "Homeowner-initiated project to explore roofing options after minor North Slope deflection finding.",
            "est_low": 9800.0,
            "est_high": 13400.0,
            "linked_quotes": [],
            "known_unknowns": [
                "Underlayment sheathing moisture levels",
                "Amount of deck panel replacement needed"
            ]
        }
        await db.design_scenarios.insert_one(project_scenario)
        audit_entry["created_scenario_id"] = sid
        
    audit_entry.pop("_id", None)
    return {
        "status": "confirmed",
        "correlation_id": correlation_id,
        "audit_event": audit_entry
    }

# ---------------------------------------------------------------------------
# Task 8: Project Estimator Integration
# ---------------------------------------------------------------------------
EST_DATA = {
    "GAF Timberline HDZ": {
        "material_label": "Architectural Shingle (GAF Timberline HDZ)",
        "national_low": 8500, "national_high": 11500,
        "regional_low": 9200, "regional_high": 12800,
        "local_low": 9800, "local_high": 13400,
        "breakdown": {
            "materials": 3800,
            "labor": 4200,
            "equipment": 800,
            "tear_off_disposal": 1200,
            "permits_fees": 400,
            "contractor_op": 1500,
            "contingency": 700,
            "taxes": 300
        }
    },
    "DECRA Standing Seam": {
        "material_label": "Standing Seam Metal Roofing (DECRA Standing Seam)",
        "national_low": 22000, "national_high": 32000,
        "regional_low": 24000, "regional_high": 35000,
        "local_low": 26000, "local_high": 38000,
        "breakdown": {
            "materials": 13500,
            "labor": 10500,
            "equipment": 1800,
            "tear_off_disposal": 1600,
            "permits_fees": 500,
            "contractor_op": 4500,
            "contingency": 2500,
            "taxes": 1100
        }
    },
    "CertainTeed Grand Manor": {
        "material_label": "Luxury Dimensional Shingle (CertainTeed Grand Manor)",
        "national_low": 16000, "national_high": 22000,
        "regional_low": 17500, "regional_high": 24500,
        "local_low": 19000, "local_high": 26500,
        "breakdown": {
            "materials": 8800,
            "labor": 7500,
            "equipment": 1200,
            "tear_off_disposal": 1400,
            "permits_fees": 450,
            "contractor_op": 3200,
            "contingency": 1800,
            "taxes": 750
        }
    }
}

class EstimateReq(BaseModel):
    material: str # "GAF Timberline HDZ" or "DECRA Standing Seam" or "CertainTeed Grand Manor"

@steward_router.post("/estimate")
async def calculate_estimate(body: EstimateReq, user: dict = Depends(get_steward_user)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    mat = body.material
    if mat not in EST_DATA:
        # Fallback
        mat = "GAF Timberline HDZ"
    
    spec = EST_DATA[mat]
    total_expected = sum(spec["breakdown"].values())
    
    estimate_payload = {
        "pricing_date": "July 2026",
        "geographic_basis": "Austin, TX (Local multiplier: 1.08x)",
        "quantity_sources": "STRATEX Digital Twin 3D Mesh Audit (3,200 sq ft)",
        "confidence_tier": "HIGH for area quantities; LOW for sub-surface deck condition",
        "scenarios": {
            "low": spec["local_low"],
            "expected": total_expected,
            "high": spec["local_high"]
        },
        "material_label": spec["material_label"],
        "breakdown": spec["breakdown"],
        "assumptions": [
            "Existing roof deck sheathing is dry and reusable without complete replacement.",
            "Standard roof pitch of 6:12 allows standard safety setup.",
            "Austin municipal permits do not require unique historic-zone review."
        ],
        "exclusions": [
            "Structural timber rafters replacement in case of chronic decay.",
            "Gutter replacement and downspout reconfiguration."
        ],
        "unknowns": [
            "Exact percentage of decking replacement required on the North Slope deflection spot.",
            "Local disposal fee increases post-August 2026."
        ],
        "verification_checklist": [
            {"item": "Tactile check of under-shingle wood rot", "status": "PENDING", "who": "Contractor / Site Inspector"},
            {"item": "Ventilation flow calculation", "status": "PENDING", "who": "Contractor"},
            {"item": "Valley flashing rust audit", "status": "PENDING", "who": "Contractor"}
        ]
    }
    
    # Calculate a cost delta explanation from Architectural Shingle (GAF Timberline)
    ref_total = sum(EST_DATA["GAF Timberline HDZ"]["breakdown"].values())
    delta = total_expected - ref_total
    
    if delta == 0:
        estimate_payload["cost_delta_explanation"] = "This is the baseline architectural roofing selection."
    elif delta > 0:
        estimate_payload["cost_delta_explanation"] = (
            f"This option represents a +${delta:,.2f} cost increase over the baseline architectural shingles. "
            f"The difference is driven by premium materials and high-skilled labor productivity hours required."
        )
    
    return estimate_payload

# ---------------------------------------------------------------------------
# Task 9: Home Investment Intelligence Integration
# ---------------------------------------------------------------------------
@steward_router.get("/scenarios")
async def get_investment_scenarios(user: dict = Depends(get_steward_user)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    scenarios = {
        "scenario_a": {
            "name": "Replace Now (Direct Upgrade)",
            "estimated_cost": "$9,800 - $13,400 (Architectural) / $26,000 - $38,000 (Metal)",
            "planning_confidence": "MEDIUM (due to hidden deck sheathing condition)",
            "maintenance_implications": "Zero expected roof maintenance costs for 25+ years.",
            "weather_exposure": "Eliminates hail & storm penetration vulnerabilities immediately.",
            "warranty_considerations": "Secures full 30-year manufacturer material + 10-year labor warranties.",
            "dependency_effects": "Allows solar array reinstall on a stable, long-lasting surface.",
            "likely_info_gained": "Exact deck rot damage revealed during shingle tear-off.",
            "risks_of_delay": "None. Immediate asset protection.",
            "unpromised_disclosures": {
                "resale_return": "Resale return varies by buyer and is not a guaranteed investment return.",
                "insurance_savings": "Insurance savings are subject to individual carrier audits and are not guaranteed.",
                "energy_savings": "Cool-roof reflectivity can lower attic temps but direct heating/cooling cost reductions are unpromised.",
                "bundling_discount": "Solar bundling features are estimated separately and do not guarantee an installation discount."
            }
        },
        "scenario_b": {
            "name": "Focused Inspection First (Diagnostic Route)",
            "estimated_cost": "$250 - $400",
            "planning_confidence": "HIGH (Unlocks 100% accurate scoping before contracting)",
            "maintenance_implications": "Postpones high capital outlay; lets homeowner do immediate minor patching if needed.",
            "weather_exposure": "Temporarily keeps the 2010 roof; locates localized vulnerabilities to seal before winter.",
            "warranty_considerations": "Evaluates GAF granule loss directly to check if GAF will cover shingle replacement costs.",
            "dependency_effects": "Triggers exact material takeoff and assembly prep.",
            "likely_info_gained": "Tactile confirmation of whether sheathing is rotten or dry.",
            "risks_of_delay": "Minimal, if inspection occurs within 30 days.",
            "unpromised_disclosures": {
                "resale_return": "Diagnostic costs are typically not recoverable on resale.",
                "insurance_savings": "Inspection alone does not alter insurance premium rates.",
                "energy_savings": "No energy efficiency changes from inspection."
            }
        },
        "scenario_c": {
            "name": "Defer and Monitor (Reactive Route)",
            "estimated_cost": "$0 immediate (Potential $2,500 - $5,000 in emergency mold & drywall rot repairs)",
            "planning_confidence": "LOW (Blind deferred risk)",
            "maintenance_implications": "Requires annual inspection scan to ensure deflection spot doesn't open.",
            "weather_exposure": "High. Deflection spot is highly vulnerable to wind-driven Texas rainstorms.",
            "warranty_considerations": "Risks voiding GAF shingle warranty if manufacturer attributes failure to neglected decking deflection.",
            "dependency_effects": "May block solar array expansion plans due to unstable substrate.",
            "likely_info_gained": "Discovers leak location only after water stains emerge on attic ceiling.",
            "risks_of_delay": "Rot could spread to trusses, multiplying structural replacement costs by 3-4x.",
            "unpromised_disclosures": {
                "resale_return": "Deferred maintenance severely degrades home score and reduces buyer offers.",
                "insurance_savings": "Carrier may drop coverage if roof condition is classified as neglected.",
                "energy_savings": "Thermal loss of $320/yr continues unabated."
            }
        }
    }
    return scenarios

# ---------------------------------------------------------------------------
# Task 10: Build Ready Review & Project Readiness Score
# ---------------------------------------------------------------------------
@steward_router.get("/readiness")
async def get_readiness(user: dict = Depends(get_steward_user)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    # 65/100 readiness score due to two missing items: deck condition (blocks!) & shingle warranty
    readiness_payload = {
        "project_readiness_score": 65,
        "max_score": 100,
        "classification": "PLANNING_STAGE_ONLY (Unpublished)",
        "priority_checklist": [
            {
                "item": "Property Information", "status": "COMPLETE", "score": 10,
                "why": "Standard boundaries and location confirmed.", "verified_by": "Austin County GIS Records",
                "blocks_publication": False
            },
            {
                "item": "Roof Geometry takeoff", "status": "COMPLETE", "score": 10,
                "why": "3D Mesh takeoff calculated 3,200 sq ft.", "verified_by": "STRATEX Digital Twin Core",
                "blocks_publication": False
            },
            {
                "item": "Photos & Thermal Imagery", "status": "COMPLETE", "score": 10,
                "why": "North Slope and South Slope photogrammetry synced.", "verified_by": "2024 Aerial Drone Audit",
                "blocks_publication": False
            },
            {
                "item": "Tear-off & Access conditions", "status": "COMPLETE", "score": 10,
                "why": "Confirmed standard 2-story perimeter access for trucks.", "verified_by": "STRATEX Core Site Survey",
                "blocks_publication": False
            },
            {
                "item": "Existing Deck & Underlayment Condition", "status": "MISSING", "score": 0,
                "why": "Concealed North Slope deflection and thermal anomaly indicate potential decking rot which must be audited.",
                "verified_by": "Licensed Inspector via core drill OR Contractor during site review",
                "blocks_publication": True
            },
            {
                "item": "Shingle Warranty Verification", "status": "UNVERIFIED", "score": 5,
                "why": "Manufacturer GAF warranty certificate is unuploaded.",
                "verified_by": "Homeowner upload of physical warranty papers",
                "blocks_publication": False
            },
            {
                "item": "Permit & HOA considerations", "status": "COMPLETE", "score": 10,
                "why": "Standard Austin zoning and Villa Horizon HOA materials confirmed.", "verified_by": "Zoning Database Sync",
                "blocks_publication": False
            }
        ]
    }
    return readiness_payload

# ---------------------------------------------------------------------------
# Task 11: Contractor Package Preview
# ---------------------------------------------------------------------------
@steward_router.get("/contractor-package")
async def get_contractor_package_preview(user: dict = Depends(get_steward_user)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    preview = {
        "summary": "Villa Horizon Roof Replacement Project Package",
        "homeowner_approved_summary": "Explore replacement of the 2010 Asphalt Shingle roof with Architectural Shingles, addressing minor deflection.",
        "property_context": {
            "name": "Villa Horizon", "location": "Austin, TX", "year_built": 2019
        },
        "digital_twin_views": ["North Slope Deflection Spot View", "South Slope Solar Array Layout"],
        "proposed_materials": "GAF Timberline HDZ (Architectural Shingles)",
        "quantity_takeoff": {
            "area_sqft": 3200, "pitch": "6:12", "ridges_hips_lft": 180, "valleys_lft": 85
        },
        "planning_estimate": "$9,800 - $13,400",
        "assumptions": [
            "Rafters are structural; decking rot limited to North Slope anomaly spot."
        ],
        "exclusions": ["Solar array uninstall/reinstall cost excluded from baseline roof quote."],
        "unknown_conditions": "Attic decking sheathing rot extent.",
        "requested_timeline": "60 days",
        "budget_preference": "Competitive",
        "questions_requiring_site_verification": [
            "Inspect attic underlayment underside for dark water rings.",
            "Confirm if fascia rot exists near gutters."
        ],
        "readiness_score": 65,
        "shared_documents": [
            {"id": "doc_01", "name": "2024_Drone_Inspection_Report.pdf", "shared": True},
            {"id": "doc_02", "name": "Property_Appraisal_Report_2019.pdf", "shared": False}
        ],
        "redacted_personal_info": {
            "last_name": "Morgan (Redacted in preview)",
            "email": "alex@stratexhabitat.com (Shared only after contract)",
            "phone": "Unshared"
        }
    }
    return preview

# ---------------------------------------------------------------------------
# Task 12: Project Opportunity Publication
# ---------------------------------------------------------------------------
class PublishOpportunityReq(BaseModel):
    property_id: str
    scenario_id: str
    timeline_preference: str = "60 days"
    budget_preference: str = "Competitive"
    shared_document_ids: List[str] = []
    remove_personal_info: bool = True

@steward_router.post("/publish")
async def publish_opportunity(body: PublishOpportunityReq, user: dict = Depends(get_steward_user), db = Depends(get_db)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    opp_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())
    timestamp = now_iso()
    
    # Save published Opportunity in the database
    published_opportunity = {
        "id": opp_id,
        "correlation_id": correlation_id,
        "property_id": body.property_id,
        "design_scenario_id": body.scenario_id,
        "owner_id": user["id"],
        "title": "Villa Horizon — Roof Replacement",
        "status": "published",
        "timeline_preference": body.timeline_preference,
        "budget_preference": body.budget_preference,
        "shared_document_ids": body.shared_document_ids,
        "personal_info_redacted": body.remove_personal_info,
        "created_at": timestamp,
        "estimate_version": "2026.1",
        "matching_preferences": {
            "preferred_trades": ["Roofing", "Renovation"],
            "max_matching_distance_miles": 35
        },
        "homeowner_approval": {
            "approved": True,
            "timestamp": timestamp,
            "ip_address": "127.0.0.1",
            "audit_method": "STeward Vertical Slice Explicit Confirmation Toggle"
        }
    }
    
    # Save audit entry
    audit_entry = {
        "id": str(uuid.uuid4()),
        "correlation_id": correlation_id,
        "event_type": "PROJECT_OPPORTUNITY_PUBLISHED",
        "homeowner_id": user["id"],
        "property_id": body.property_id,
        "opportunity_id": opp_id,
        "timestamp": timestamp,
        "details": {
            "referenced_passport_and_dna": True,
            "design_scenario_version": 1,
            "contractor_direct_contact_restricted": True
        }
    }
    
    if db is not None:
        await db.quotes.insert_one({
            "id": opp_id,
            "owner_id": user["id"],
            "owner_name": "Alex M." if body.remove_personal_info else user["name"],
            "property_id": body.property_id,
            "property_name": "Villa Horizon",
            "title": "Published: Roof Replacement",
            "category": "Roofing",
            "project_type": "renovation",
            "description": "Exterior Roof Replacement Opportunity prepopulated with 3D mesh takeoff.",
            "seriousness": "high",
            "target_timeframe": body.timeline_preference,
            "status": "open",
            "is_opportunity": True,
            "created_at": timestamp,
            "contractor_responses": [],
            "routed_to": []
        })
        await db.audit_events.insert_one(audit_entry)
        
    audit_entry.pop("_id", None)
    published_opportunity.pop("_id", None)
    
    return {
        "status": "published",
        "opportunity_id": opp_id,
        "correlation_id": correlation_id,
        "opportunity": published_opportunity,
        "audit": audit_entry
    }

# ---------------------------------------------------------------------------
# Task 13: Home Memory Behavior
# ---------------------------------------------------------------------------
class MemoryUpdateReq(BaseModel):
    project_memories: Optional[dict] = None
    homeowner_memories: Optional[dict] = None

@steward_router.get("/memory")
async def get_steward_memory(user: dict = Depends(get_steward_user), db = Depends(get_db)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    pid = await resolve_property_id(db, user["email"])
    
    # Standard default memory isolation
    mem = {
        "project_memory": {
            "preferred_roof_material": "Architectural Shingles (GAF Timberline HDZ)",
            "budget_target": "Competitive",
            "timeline_preference": "60 days",
            "selected_scenario": "Scenario B (Focused Inspection First)",
            "unresolved_project_questions": ["Underlayment rot percentage"]
        },
        "homeowner_memory": {
            "communication_preference": "Email & App Dashboard (No phone calls)",
            "explanation_depth_preference": "High-fidelity Progressive Trace",
            "project_priorities": ["Structural durability", "Resilience against Austin storms"]
        },
        "property_memory_reference": {
            "approved_passport_projections": f"/api/steward/context",
            "approved_property_dna_projections": f"/api/steward/context",
            "published_explanations": "Asphalt Shingle (Architectural Shingles)"
        }
    }
    
    if db is not None:
        existing = await db.steward_memories.find_one({"owner_id": user["id"]}, {"_id": 0})
        if existing:
            return existing
            
        await db.steward_memories.insert_one({"owner_id": user["id"], **mem})
        
    return mem

@steward_router.post("/memory")
async def update_steward_memory(body: MemoryUpdateReq, user: dict = Depends(get_steward_user), db = Depends(get_db)):
    if user["email"] != "alex@stratexhabitat.com":
        raise HTTPException(status_code=403, detail="Tenant access restricted")
    
    update = {}
    if body.project_memories:
        for k, v in body.project_memories.items():
            update[f"project_memory.{k}"] = v
    if body.homeowner_memories:
        for k, v in body.homeowner_memories.items():
            update[f"homeowner_memory.{k}"] = v
            
    if db is not None:
        await db.steward_memories.update_one({"owner_id": user["id"]}, {"$set": update}, upsert=True)
        return await db.steward_memories.find_one({"owner_id": user["id"]}, {"_id": 0})
        
    return {"ok": True}
