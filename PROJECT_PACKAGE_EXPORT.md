# CONTRACTOR-READY PROJECT EXPORT & REGULATORY SYSTEMS
## RFP SCHEMAS, PERMIT BUNDLES, & HOA CONSIDERATION SUMMARIES
**Version:** 2.0  
**Classification:** HABITAT-CONFIDENTIAL

This specification outlines the data packaging structures, regulatory evaluation pipelines, and export schemas that compile designed homeowner scenarios into complete, professional RFP packages for local contractors.

---

## 1. THE EXPORT COMPILING FLOW

When a homeowner transitions from design to the bidding stage, the **Export Compilation Engine** aggregates design geometry, material SKUs, site boundaries, and municipal permit histories into a single secure package.

```
+---------------------------------------------------------------------------------+
|                        EXPORT COMPLIANCE ENGINE ENGINE                          |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [ User Selections ]   +----> [ PROPERTY PASSPORT ] +----> [ MUNICIPAL CODES ]  |
|  - Trex SKU            |      - Property Lines       |      - Setback limits    |
|  - Solar panels        |      - Existing Utilities   |      - Zoning rules      |
|                        |                             |                          |
|                        +--------------+--------------+                          |
|                                       |                                         |
|                                       v                                         |
|                         +----------------------------+                          |
|                         |  CONTRACTOR-READY PACKAGE  |                          |
|                         |    (Secure JSON & PDF)     |                          |
|                         +----------------------------+                          |
+---------------------------------------------------------------------------------+
```

---

## 2. THE CONTRACTOR-READY PACKAGE COMPONENT CHECKLIST

Each exported package comprises five key sections, providing contractors with everything they need to quote accurately without unnecessary site visits.

```
       +---------------------------------------------------------+
       |                  CONTRACTOR-READY RFP BUNDLE            |
       +---------------------------------------------------------+
       |  1. COMPREHENSIVE PHOTOS (Before scans & 3D Twin)       |
       |  2. BILLED SPECIFICATIONS (SKUs, quantities, colors)    |
       |  3. SITE CONDITIONS (Soil data, property line vectors)  |
       |  4. PERMIT COMPLIANCE GUIDANCE (Local codes)            |
       |  5. HOA CONSIDERATION SUMMARY (Subdivision guidelines)  |
       +---------------------------------------------------------+
```

### 1. Photo & Twin Visualization Bundle
- **Verified Existing Photo**: High-resolution, multi-angle base photos of the property.
- **AI Concept Rendering**: 3D orthographic and perspective overlays showing the finished project from identical angles.
- **Spatial Measurement Overlay**: Annotated photos with linear dimensions, area calculations, and structural connection lines.

### 2. Bill of Materials (BOM) Sheet
- **Manufacturer SKU & Brands**: Complete product line breakouts (e.g. James Hardie, Trex, Sheffield Metals).
- **Exact Color Swatches**: Sourcing names and Hex identifiers.
- **Estimated Quantities**: Dynamic square footage, linear footage, or unit totals with an automatic waste-margin multiplier.

### 3. Property Site Conditions
- **GIS Boundary Vector**: Exact lines showing where property limits sit.
- **Underground Utility Easements**: Indicated layout zones showing water, gas, electricity, and sewage lines.
- **Soil Classification Profile**: Mapped local geological soil class (e.g., clay, sand, rock) to inform footing depths.

---

## 3. PERMIT COMPLIANCE GUIDANCE BUNDLE

To ensure projects proceed smoothly through local municipal approvals, the platform automatically compiles a **Permit Guidance Report** tailored to the home's location.

```
+---------------------------------------------------------------------------------+
|  MUNICIPAL PERMIT COMPLIANCE SUMMARY: Denver, CO ZIP 80202                      |
+---------------------------------------------------------------------------------+
|  PROJECT SCOPE: 12x16 Elevated Deck                                             |
|                                                                                 |
|  [X] Municipal Permit Required: YES                                             |
|      - Standard Residential Building Permit (IRC Section R105).                 |
|                                                                                 |
|  [X] Local Deck Construction Limits Checklist:                                  |
|      - Elevated structures > 30 inches off grade require safety guardrails.     |
|      - Post footing piers must extend below local frost line (36 inches).       |
|      - Ledger board must be fastened directly to framing (no siding backing).   |
|                                                                                 |
|  [X] Required Submittal Documentation Compiled:                                 |
|      - [PDF] Formatted site plan showing deck footprint and property lines.      |
|      - [PDF] Structural joist/beam framing layout plan.                          |
|      - [PDF] Fastener detail schedule for ledger-to-rim-joist attachment.        |
+---------------------------------------------------------------------------------+
```

---

## 4. HOA CONSIDERATION SUMMARY

Before submitting to municipal boards, the platform checks design parameters against local Homeowners Association (HOA) rules retrieved from subdivision guidelines databases.

```
+---------------------------------------------------------------------------------+
|  HOA CONSIDERATION AUDIT: Cherry Creek Subdivision HOA                          |
+---------------------------------------------------------------------------------+
|  [PASS] COLOR PALETTE: Trex Carmel Cool Ash matches approved earthy neutral      |
|         colors list (Subdivision Bylaw Section 4.2).                            |
|                                                                                 |
|  [WARN] EQUIPMENT NOISE SCREENING: Your proposed pool equipment pad is located  |
|         within 15 feet of the east fence boundary. Cherry Creek guidelines      |
|         require a solid wood or shrub visual screen around pumps.               |
|         * Action Taken: Screen wrap added to the design.                        |
|                                                                                 |
|  [FAIL] HEIGHT EXCEEDANCE: Your proposed gazebo roof height is 16.5 feet.       |
|         HOA bylaws limit detached accessory structures to 15.0 feet.            |
|         * Recommended Fix: Reduce corner post heights by 1.5 feet in the studio.  |
+---------------------------------------------------------------------------------+
```

---

## 5. REUSABLE CONTRACTOR-READY EXPORT SCHEMAS (JSON PAYLOAD)

This secure payload is compiled and sent to local contractors via API or exported as a zip archive containing drawings, reports, and photos.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ContractorReadyRFPPackage",
  "type": "object",
  "required": [
    "rfp_id",
    "property_metadata",
    "project_metadata",
    "bill_of_materials",
    "spatial_data_payload",
    "regulatory_checklists"
  ],
  "properties": {
    "rfp_id": { "type": "string", "pattern": "^RFP-[0-9]{5}-[A-Z]{4}$" },
    "property_metadata": {
      "type": "object",
      "required": ["property_id", "zip_code", "soil_class", "lot_dimensions"],
      "properties": {
        "property_id": { "type": "string" },
        "zip_code": { "type": "string" },
        "soil_class": { "type": "string" },
        "lot_dimensions": { "type": "object" }
      }
    },
    "project_metadata": {
      "type": "object",
      "required": ["project_type", "selected_scenario_id", "target_start_date"],
      "properties": {
        "project_type": { "type": "string" },
        "selected_scenario_id": { "type": "string" },
        "target_start_date": { "type": "string", "format": "date" }
      }
    },
    "bill_of_materials": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["sku_id", "manufacturer", "name", "qty", "unit"],
        "properties": {
          "sku_id": { "type": "string" },
          "manufacturer": { "type": "string" },
          "name": { "type": "string" },
          "qty": { "type": "number" },
          "unit": { "type": "string" },
          "notes": { "type": "string" }
        }
      }
    },
    "spatial_data_payload": {
      "type": "object",
      "required": ["bounding_boxes", "elevation_maps_url"],
      "properties": {
        "bounding_boxes": { "type": "array" },
        "elevation_maps_url": { "type": "string", "format": "uri" }
      }
    },
    "regulatory_checklists": {
      "type": "object",
      "required": ["permits_required", "hoa_compliance_status"],
      "properties": {
        "permits_required": { "type": "boolean" },
        "permit_submittal_urls": { "type": "array", "items": { "type": "string" } },
        "hoa_compliance_status": { "type": "string", "enum": ["compliant", "conditional_warning", "violating"] }
      }
    }
  }
}
```
