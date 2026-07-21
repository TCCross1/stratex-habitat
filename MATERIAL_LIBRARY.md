# MATERIAL & PBR SPECIFICATION LIBRARY
## HARDWARE SKUs, MATERIAL PROPERTIES, & REALISTIC RENDERING PARAMETERS
**Version:** 2.0  
**Classification:** HABITAT-CONFIDENTIAL

This specification defines the Physically Based Rendering (PBR) material data structures, product SKU schemas, and manufacturers integrated into the Habitat Design Studio 2.0.

---

## 1. PHYSICALLY BASED RENDERING (PBR) STANDARDS

To maintain photographic fidelity on the homeowner's Digital Twin, materials are rendered using a 6-texture map PBR stack.

```
       +--------------------------------------------------------+
       |                  PBR TEXTURE MAP STACK                 |
       +--------------------------------------------------------+
       |  1. ALBEDO (Base Color, Hex/RGB Value)                 |
       |  2. NORMAL (Surface Angles & Relief Detail)            |
       |  3. ROUGHNESS (Micro-Surface Light Diffusion)         |
       |  4. METALLIC (Electromagnetic Reflection, Non/Metal)   |
       |  5. HEIGHT (Displacement & Heavy Relief Profiles)      |
       |  6. AMBIENT OCCLUSION (Crevice and Shadow Detailing)   |
       +--------------------------------------------------------+
```

---

## 2. MATERIAL SKU DATABASE SCHEMA

Every physical material in the catalog is stored in the database as a structured document matching the schema below. This ensures seamless catalog search, cost calculation, and rendering.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MaterialProductSKU",
  "type": "object",
  "required": [
    "sku_id",
    "manufacturer",
    "brand_name",
    "product_line",
    "material_class",
    "pricing_unit",
    "base_cost_per_unit",
    "durability_years",
    "warranty_details",
    "pbr_parameters"
  ],
  "properties": {
    "sku_id": { "type": "string", "pattern": "^[A-Z]{3}-[0-9]{4}-[A-Z]{2}$" },
    "manufacturer": { "type": "string" },
    "brand_name": { "type": "string" },
    "product_line": { "type": "string" },
    "material_class": { "type": "string" },
    "colors_available": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["color_name", "hex_value", "texture_map_overrides"],
        "properties": {
          "color_name": { "type": "string" },
          "hex_value": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" },
          "texture_map_overrides": { "type": "object" }
        }
      }
    },
    "pricing_unit": { "type": "string", "enum": ["sqft", "linear_foot", "unit", "ton"] },
    "base_cost_per_unit": { "type": "number", "minimum": 0 },
    "durability_years": { "type": "integer", "minimum": 1 },
    "warranty_details": {
      "type": "object",
      "required": ["length_years", "type"],
      "properties": {
        "length_years": { "type": "integer" },
        "type": { "type": "string", "enum": ["limited_lifetime", "transferable", "standard_manufacturer"] }
      }
    },
    "pbr_parameters": {
      "type": "object",
      "required": ["roughness", "metallic", "specular", "normal_intensity"],
      "properties": {
        "roughness": { "type": "number", "minimum": 0, "maximum": 1 },
        "metallic": { "type": "number", "minimum": 0, "maximum": 1 },
        "specular": { "type": "number", "minimum": 0, "maximum": 1 },
        "normal_intensity": { "type": "number", "minimum": 0, "maximum": 2 }
      }
    }
  }
}
```

---

## 3. CORE MATERIAL CLASSES & PBR CONSTANTS

These standard physical parameters define light-reflection behavior for key material categories in the Habitat catalog.

| Material Class | Albedo/Diffuse Range | Roughness | Metallic | Normal Intensity | Displacement Height |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fiber Cement Siding** | Matte, Eggshell colors | 0.85 | 0.00 | 0.65 | 1.5mm |
| **Composite Decking** | Rich natural wood tones | 0.75 | 0.05 | 0.80 | 2.0mm |
| **Metal Roofing** | Dark, deep solid tones | 0.35 | 0.90 | 0.40 | 0.5mm |
| **Clay Pavers** | Terracotta, Red, Tan | 0.90 | 0.00 | 1.20 | 3.0mm |
| **Architectural Shingle**| Deep grays, Black, Brown | 0.95 | 0.00 | 1.80 | 5.0mm |
| **Solar Panels** | Deep obsidian blue/black | 0.10 | 0.95 | 0.10 | 0.0mm |

---

## 4. SAMPLE MATERIAL RECORDS (SEED INGESTION DATA)

### Fiber Cement Siding
```json
{
  "sku_id": "JHM-8041-FC",
  "manufacturer": "James Hardie",
  "brand_name": "HardiePlank",
  "product_line": "Select Cedarmill Lap Siding",
  "material_class": "Fiber Cement Siding",
  "colors_available": [
    { "color_name": "Iron Gray", "hex_value": "#424749", "texture_map_overrides": {} },
    { "color_name": "Arctic White", "hex_value": "#F3F4F6", "texture_map_overrides": {} },
    { "color_name": "Boothbay Blue", "hex_value": "#687D8E", "texture_map_overrides": {} }
  ],
  "pricing_unit": "sqft",
  "base_cost_per_unit": 3.85,
  "durability_years": 50,
  "warranty_details": {
    "length_years": 30,
    "type": "transferable"
  },
  "pbr_parameters": {
    "roughness": 0.85,
    "metallic": 0.00,
    "specular": 0.15,
    "normal_intensity": 0.70
  }
}
```

### Composite Decking
```json
{
  "sku_id": "TRX-4492-CD",
  "manufacturer": "Trex",
  "brand_name": "Transcend",
  "product_line": "Lineage High-Performance Decking",
  "material_class": "Composite Decking",
  "colors_available": [
    { "color_name": "Biscayne Warm Honey", "hex_value": "#A67B5B", "texture_map_overrides": {} },
    { "color_name": "Carmel Cool Ash", "hex_value": "#807E7B", "texture_map_overrides": {} }
  ],
  "pricing_unit": "sqft",
  "base_cost_per_unit": 7.50,
  "durability_years": 35,
  "warranty_details": {
    "length_years": 25,
    "type": "limited_lifetime"
  },
  "pbr_parameters": {
    "roughness": 0.70,
    "metallic": 0.02,
    "specular": 0.20,
    "normal_intensity": 1.10
  }
}
```

### Standing Seam Metal Roofing
```json
{
  "sku_id": "SMC-5091-MR",
  "manufacturer": "Sheffield Metals",
  "brand_name": "COOLR",
  "product_line": "Galvalume 24-Gauge Metal Roof",
  "material_class": "Metal Roofing",
  "colors_available": [
    { "color_name": "Matte Black", "hex_value": "#1A1A1C", "texture_map_overrides": {} },
    { "color_name": "Charcoal Gray", "hex_value": "#3C3D42", "texture_map_overrides": {} }
  ],
  "pricing_unit": "sqft",
  "base_cost_per_unit": 9.20,
  "durability_years": 60,
  "warranty_details": {
    "length_years": 40,
    "type": "transferable"
  },
  "pbr_parameters": {
    "roughness": 0.30,
    "metallic": 0.85,
    "specular": 0.60,
    "normal_intensity": 0.30
  }
}
```

---

## 5. REALISTIC PALETTE COMPOSITION (STRATEX COMPLIANT)

Color schemes generated by the AI or selected by the user are validated against **Stratex Aesthetic Principles** to prevent clashing and ensure professional results.

### Architectural Palettes

#### 1. Modern Farmhouse (High-Contrast Command Center)
- **Primary Body**: Arctic White (`#F3F4F6`)
- **Accent Shutters/Trim**: Matte Black (`#1A1A1C`)
- **Metal Accents**: Standing Seam Charcoal (`#3C3D42`)
- **Timber Accent**: Trex Biscayne (`#A67B5B`)

#### 2. Nordic Twilight (Electric Minimalist)
- **Primary Body**: Iron Gray (`#424749`)
- **Accent Trim**: Cool Ash (`#807E7B`)
- **Hardware/Frames**: Cyber Obsidian (`#0F1115`)
- **Landscape Border**: Dark Basalt (`#22252A`)

---

## 6. MATERIAL TO VISUALIZATION RENDER STREAM

When a homeowner selects a material swatch in the UI:
1. **Dynamic ID Lookup**: The React client fetches the product's `pbr_parameters` and the hex value of the selected color.
2. **WebGL Shading Update**: The Three.js PBR shader updates the target geometry (e.g., roof face mesh) with the normal map and height offset associated with the material class.
3. **AI Refinement Rendering**: During an asynchronous high-fidelity preview render, the selected SKU details (e.g., *"Sheffield COOLR Matte Black Standing Seam Roofing, SKU SMC-5091-MR"*) are injected into the Gemini Vision Prompt, producing photorealistic lighting, reflections, and shadowing tailored to the selected material's physical properties.
