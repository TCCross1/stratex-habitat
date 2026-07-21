# CENTCOM DIRECTIVE H-009: ESTIMATE DATA MODEL
## CANONICAL SCHEMAS, JSON DEFINITIONS, & IMMUTABILITY CONTRACTS
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Overview & Data Model Design Philosophy

To guarantee the engineering law of **Reproducibility**, the estimating system utilizes a strictly structured, immutable data model. An estimate is not a volatile spreadsheet; it is an immutable snapshot of historical calculations. If a homeowner alters their design, a new versioned estimate record is created. 

Every single estimate must contain:
1. **The Core Header Block**: Stamping version, timestamp, geography, and general confidence indices.
2. **The Direct Cost Ledger**: Itemized physical inputs.
3. **The Contractor Operational Overlay**: Overhead allocation.
4. **The Selling Price Summary**: Profit, contingencies, tax, and calculated pricing ranges.
5. **The Line-Item and Assembly Arrays**: Highly nested structures tracing quantities back to their sources.
6. **The Inputs Snapshot**: The exact state of dimensions, selected SKUs, and rules in play during calculation.

---

## 2. JSON Schema: Project Estimate Document

This schema defines the full payload structure of a Habitat Design Studio project estimate.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "HabitatProjectEstimate",
  "type": "object",
  "required": [
    "estimate_id",
    "project_id",
    "version",
    "pricing_date",
    "geographic_basis",
    "price_book_version",
    "confidence_summary",
    "direct_costs",
    "contractor_costs",
    "selling_price",
    "assemblies",
    "exclusions",
    "assumptions",
    "reproducibility_snapshot"
  ],
  "properties": {
    "estimate_id": { "type": "string", "pattern": "^EST-[0-9]{8}-[A-F0-9]{4}$" },
    "project_id": { "type": "string", "pattern": "^PRJ-[0-9]{6}$" },
    "version": { "type": "integer", "minimum": 1 },
    "pricing_date": { "type": "string", "format": "date-time" },
    "geographic_basis": {
      "type": "object",
      "required": ["zip_code", "latitude", "longitude", "region_name"],
      "properties": {
        "zip_code": { "type": "string", "pattern": "^[0-9]{5}$" },
        "latitude": { "type": "number", "minimum": -90, "maximum": 90 },
        "longitude": { "type": "number", "minimum": -180, "maximum": 180 },
        "region_name": { "type": "string" }
      }
    },
    "price_book_version": { "type": "string", "pattern": "^v[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "confidence_summary": {
      "type": "object",
      "required": ["overall_tier", "numerical_score", "verified_items_count", "total_items_count"],
      "properties": {
        "overall_tier": { "type": "string", "enum": ["VERIFIED", "ESTIMATED", "SUGGESTED", "PRELIMINARY"] },
        "numerical_score": { "type": "number", "minimum": 0, "maximum": 100 },
        "verified_items_count": { "type": "integer" },
        "total_items_count": { "type": "integer" }
      }
    },
    "direct_costs": {
      "type": "object",
      "required": ["materials_subtotal", "labor_subtotal", "equipment_subtotal", "subcontractors_subtotal", "mobilization_subtotal", "permits_fees_subtotal", "waste_adjustments_subtotal", "direct_costs_total"],
      "properties": {
        "materials_subtotal": { "type": "number" },
        "labor_subtotal": { "type": "number" },
        "equipment_subtotal": { "type": "number" },
        "subcontractors_subtotal": { "type": "number" },
        "mobilization_subtotal": { "type": "number" },
        "permits_fees_subtotal": { "type": "number" },
        "waste_adjustments_subtotal": { "type": "number" },
        "direct_costs_total": { "type": "number" }
      }
    },
    "contractor_costs": {
      "type": "object",
      "required": ["direct_costs_total", "general_overhead_allowance", "project_overhead_allowance", "contractor_cost_total"],
      "properties": {
        "direct_costs_total": { "type": "number" },
        "general_overhead_allowance": { "type": "number" },
        "project_overhead_allowance": { "type": "number" },
        "contractor_cost_total": { "type": "number" }
      }
    },
    "selling_price": {
      "type": "object",
      "required": ["contractor_cost_total", "profit_allowance", "contingency_allowance", "applicable_taxes", "selling_price_expected", "selling_price_low", "selling_price_high"],
      "properties": {
        "contractor_cost_total": { "type": "number" },
        "profit_allowance": { "type": "number" },
        "contingency_allowance": { "type": "number" },
        "applicable_taxes": { "type": "number" },
        "selling_price_expected": { "type": "number" },
        "selling_price_low": { "type": "number" },
        "selling_price_high": { "type": "number" }
      }
    },
    "assemblies": {
      "type": "array",
      "items": { "$ref": "#/$defs/assembly_item" }
    },
    "exclusions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "assumptions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["category", "text", "source"],
        "properties": {
          "category": { "type": "string" },
          "text": { "type": "string" },
          "source": { "type": "string" }
        }
      }
    },
    "reproducibility_snapshot": {
      "type": "object",
      "required": ["input_dimensions", "selected_skus", "rules_and_factors_version"],
      "properties": {
        "input_dimensions": { "type": "object" },
        "selected_skus": {
          "type": "array",
          "items": { "type": "string" }
        },
        "rules_and_factors_version": { "type": "string" }
      }
    }
  },
  "$defs": {
    "assembly_item": {
      "type": "object",
      "required": ["assembly_id", "assembly_name", "quantity", "unit_of_measure", "confidence_tier", "direct_cost_summary", "components"],
      "properties": {
        "assembly_id": { "type": "string" },
        "assembly_name": { "type": "string" },
        "quantity": { "type": "number" },
        "unit_of_measure": { "type": "string" },
        "confidence_tier": { "type": "string", "enum": ["VERIFIED", "ESTIMATED", "SUGGESTED", "PRELIMINARY"] },
        "direct_cost_summary": {
          "type": "object",
          "required": ["materials", "labor", "equipment", "total"],
          "properties": {
            "materials": { "type": "number" },
            "labor": { "type": "number" },
            "equipment": { "type": "number" },
            "total": { "type": "number" }
          }
        },
        "components": {
          "type": "array",
          "items": { "$ref": "#/$defs/component_item" }
        }
      }
    },
    "component_item": {
      "type": "object",
      "required": ["component_id", "component_type", "description", "quantity", "unit_of_measure", "source_declaration", "unit_cost", "total_cost", "waste_factor"],
      "properties": {
        "component_id": { "type": "string" },
        "component_type": { "type": "string", "enum": ["material", "labor_activity", "equipment_rental", "subcontractor_fee", "permit"] },
        "description": { "type": "string" },
        "quantity": { "type": "number" },
        "unit_of_measure": { "type": "string" },
        "source_declaration": {
          "type": "object",
          "required": ["source_category", "measurement_date", "referenced_file_or_field"],
          "properties": {
            "source_category": { "type": "string", "enum": ["Verified Property Data", "Digital Twin Measurement", "Homeowner Input", "AI-Derived Measurement", "Template Allowance", "Unknown"] },
            "measurement_date": { "type": "string", "format": "date-time" },
            "referenced_file_or_field": { "type": "string" }
          }
        },
        "unit_cost": { "type": "number" },
        "waste_factor": { "type": "number" },
        "total_cost": { "type": "number" }
      }
    }
  }
}
```

---

## 3. Core Entities Mapping & Attributes

### 3.1. Entity: `ProjectEstimate` (The Root Document)
Represents the finalized, immutable planning record generated inside Design Studio 2.0.
* **`version` (int)**: Starts at `1` for the first run, incremented sequentially.
* **`pricing_date` (datetime)**: The exact calculation timestamp. Ensures the "no estimate without a pricing date" law.
* **`price_book_version` (string)**: Refers to the version of the national SKU database used (e.g., `v2026.3.1`). Enables strict reproduction of material pricing.

### 3.2. Entity: `AssemblyItem` (Nested Grouping)
Corresponds to a structural building block of the project (e.g., *Slab-on-Grade Foundation*, *Gable Roof Shingle Decking*). It resolves into a list of nested components.
* **`assembly_id` (string)**: Matches the ID in the master assembly directory (`ASB-CONC-PATIO`).
* **`quantity` (float)**: The computed structural coverage (e.g., `450.00` sqft).

### 3.3. Entity: `ComponentItem` (Line Item)
The molecular unit of the estimate, mapping to a specific SKU, labor trade hour, or machinery rate.
* **`source_declaration` (object)**: Governs the "No quantity without a declared source" engineering law.
* **`waste_factor` (float)**: Material-specific scrap buffers (e.g., `0.10` for a 10% shingle overage).

---

## 4. Scenario-Based Pricing Range Rules

An estimate cannot be represented as a single static price. The data model enforces three distinct cost targets representing environmental variables:

1. **`selling_price_low` (Optimistic Scenario)**:
   * Condition: Minimum complexity multipliers ($C_k = 1.0$), low material waste factor, no unforeseen condition allowances, regional labor index in the 25th percentile.
2. **`selling_price_expected` (Likeliest Scenario)**:
   * Condition: Normal material waste buffers, standard crew productivity rates, mid-percentile regional labor rates, average structural complexity.
3. **`selling_price_high` (Conservative Scenario)**:
   * Condition: Premium material tier selected, high site-access difficulty multipliers ($C_k = 1.25$), seasonal productivity penalties, and elevated structural risk buffers.

---

## 5. Immutability & Reproducibility Contract

Every estimate stored in the database must include the `reproducibility_snapshot` object. This block guarantees that if the exact same JSON record is loaded by the estimating engine years later under a "simulation run," the resulting expected cost range is identical. 

```
                                ESTIMATE SNAPSHOT
                                        |
      +---------------------------------+---------------------------------+
      |                                 |                                 |
      v                                 v                                 v
[ Dimensions JSON ]             [ Selected SKUs Array ]         [ Formula Factors DB ]
- "wall_area": 1250             - "JHM-8041-FC"                 - "regional_labor_75201": 0.94
- "roof_pitch": 6:12            - "TRX-4492-CD"                 - "base_burden_factor": 1.30
- "excavation_yd3": 12          - "SMC-5091-MR"                 - "permit_flat_fee": 350.00
```

By encapsulating these factors, any historic planning record can be audit-checked without drifting values caused by future market inflation or price book updates.
