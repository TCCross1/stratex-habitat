# CENTCOM DIRECTIVE H-009: ESTIMATOR API SPECIFICATION
## RESTFUL ENDPOINTS, FASTAPI ROUTE DEFINITIONS, & RESPONSE SCHEMAS
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. API Architecture Overview

The **Habitat Project Estimator™ API** is a high-performance, stateless microservice built using FastAPI. It acts as the financial computation engine for the Design Studio 2.0. 

All endpoints execute within strict constraints:
*   **Performance Budget**: Recalculations must complete and return a JSON payload in $<200$ milliseconds.
*   **Security**: All endpoints require a bearer JWT token matching the authenticated homeowner's session.
*   **Strict Validation**: Input parameters are schema-checked using Pydantic, enforcing the mandatory presence of geographic ZIP codes and pricing dates.

---

## 2. Endpoint Registry

```
  POST /api/v1/estimates/calculate          - Run Full Cost Pipeline
  GET  /api/v1/estimates/assemblies         - Query Assembly Library
  POST /api/v1/estimates/deltas             - Generate Delta NL Explanations
  POST /api/v1/estimates/compare-proposals  - Compute Contractor Bid Variance
```

---

## 3. Detailed Route Specifications

### 3.1. POST `/api/v1/estimates/calculate`
Runs the entire spatial takeoff, assembly mapping, regional cost index lookup, and overhead surcharge calculation pipeline.

*   **Headers**:
    *   `Authorization: ******
*   **Request Payload Schema (JSON)**:
```json
{
  "project_id": "PRJ-904128",
  "pricing_date": "2026-07-21T12:00:00Z",
  "zip_code": "80202",
  "price_book_version": "v2026.3.1",
  "dimensions": {
    "roof_footprint_sqft": 1200,
    "roof_pitch": "6:12",
    "siding_wall_sqft": 2400,
    "apertures_sqft": 350,
    "site_slope_degrees": 5.2
  },
  "materials_selected": [
    {
      "zone_id": "roof",
      "sku_id": "SMC-5091-MR",
      "color_name": "Matte Black"
    },
    {
      "zone_id": "siding_main",
      "sku_id": "JHM-8041-FC",
      "color_name": "Iron Gray"
    }
  ],
  "site_overrides": {
    "occupied_home": true,
    "side_gate_width_inches": 32.0,
    "soil_bearing_capacity_verified": false
  }
}
```

*   **Response Payload Schema (JSON - Status 200 OK)**:
```json
{
  "estimate_id": "EST-20260721-AC81",
  "version": 1,
  "confidence_summary": {
    "overall_tier": "ESTIMATED",
    "numerical_score": 84.5
  },
  "selling_price": {
    "selling_price_expected": 32450.00,
    "selling_price_low": 29800.00,
    "selling_price_high": 36100.00
  },
  "direct_costs": {
    "materials_subtotal": 14250.00,
    "labor_subtotal": 8500.00,
    "equipment_subtotal": 1200.00,
    "direct_costs_total": 23950.00
  },
  "contractor_costs": {
    "general_overhead_allowance": 2395.00,
    "supervision_allowance": 958.00,
    "insurance_and_licensing": 359.25,
    "contractor_cost_total": 27662.25
  },
  "operations_and_profit_total": 8500.00
}
```

---

### 3.2. GET `/api/v1/estimates/assemblies`
Retrieves registered assemblies and default parameters from the master library.

*   **Query Parameters**:
    *   `category`: e.g. `roofing`, `concrete`, `cladding` (Optional)
*   **Response (JSON - Status 200 OK)**:
```json
{
  "assemblies": [
    {
      "assembly_id": "ASB-CONC-STAMPED",
      "assembly_name": "Stamped Concrete Patio",
      "base_unit": "SQFT",
      "default_productivity_rate_per_shift": 350.00,
      "required_crew_composition": [
        "Concrete Finisher",
        "Concrete Laborer",
        "Skilled Laborer"
      ]
    }
  ]
}
```

---

### 3.3. POST `/api/v1/estimates/deltas`
Compares two versioned planning estimates and returns a structured delta list and natural language explanations.

*   **Request Payload**:
```json
{
  "previous_estimate_id": "EST-20260721-AC81",
  "current_estimate_id": "EST-20260721-BF90"
}
```
*   **Response (JSON - Status 200 OK)**:
```json
{
  "comparison_summary": {
    "price_change": 2420.00,
    "direction": "increase"
  },
  "explanations": [
    {
      "component": "Patio Decking",
      "change_type": "dimensional",
      "impact": 2420.00,
      "narrative": "Patio cost increased because the area changed from 420 to 610 square feet."
    }
  ]
}
```

---

### 3.4. POST `/api/v1/estimates/compare-proposals`
Compares an incoming contractor proposal sheet against the baseline Habitat planning estimate.

*   **Request Payload**:
```json
{
  "baseline_estimate_id": "EST-20260721-AC81",
  "contractor_proposal": {
    "proposal_id": "PROP-90412",
    "contractor_name": "Peak Custom Builders",
    "total_bid_price": 34800.00,
    "line_items": [
      {
        "description": "Concrete Slab Pouring",
        "cost": 15800.00,
        "is_allowance": false
      },
      {
        "description": "Premium Shingle Install",
        "cost": 14000.00,
        "is_allowance": false
      },
      {
        "description": "Electrical Fixtures Allowance",
        "cost": 2000.00,
        "is_allowance": true
      }
    ],
    "declared_exclusions": [
      "Municipal building permit filing",
      "Post-project soil landscaping recovery"
    ]
  }
}
```
*   **Response (JSON - Status 200 OK)**:
```json
{
  "variance_summary": {
    "total_deviation_percent": 7.24,
    "status": "ALIGNMENT_OK"
  },
  "vector_analysis": {
    "scope_completeness": {
      "score": 92.0,
      "omitted_elements": ["Municipal permit submission fees"],
      "impact_narrative": "Bid excludes local permit filing ($1,200 standard municipality fee)."
    },
    "allowance_realism": {
      "score": 44.4,
      "underfunded_items": [
        {
          "item": "Electrical Fixtures",
          "bid_allowance": 2000.00,
          "designed_cost": 4500.00,
          "probable_overage": 2500.00
        }
      ]
    }
  }
}
```

---

## 4. Error Handling & Validation Codes

The API returns standard HTTP status codes with high-contrast, diagnostic details in the JSON body.

*   **422 Unprocessable Entity (Missing Geography)**:
    *   *Trigger*: Request payload lacks `zip_code` or contains an invalid non-numeric ZIP.
    *   *Body*:
```json
{
  "error_code": "ERR_MISSING_GEOGRAPHIC_BASIS",
  "detail": "No estimate can be generated without a valid 5-digit ZIP code to resolve regional cost factors.",
  "timestamp": "2026-07-21T12:00:01Z"
}
```

*   **422 Unprocessable Entity (Expired Pricing Date)**:
    *   *Trigger*: `pricing_date` parameter is more than 90 days in the past.
    *   *Body*:
```json
{
  "error_code": "ERR_EXPIRED_PRICING_DATE",
  "detail": "The requested pricing date is older than the 90-day volatility limit. Please supply current timestamp.",
  "timestamp": "2026-07-21T12:00:01Z"
}
```
