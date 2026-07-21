# CENTCOM DIRECTIVE H-009: QUANTITY TAKEOFF ENGINE
## AUTOMATED DIMENSIONAL EXTRACTION & METRIC SOURCING PIPELINE
**Version:** 1.0  
**Classification:** HABITAT-CONFIDENTIAL  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. Architectural Mission

The **Quantity Takeoff Engine (QTE)** is responsible for programmatically parsing physical dimensions from Design Studio designs and property profiles. It isolates the homeowner from complex mathematical takeoffs, translating high-level concepts into exact construction units (e.g., squares of shingles, cubic yards of concrete, board feet of lumber).

Every quantity processed must abide by the **Third Engineering Law of Habitat**: *No quantity without a declared source.* This prevents deceptive precision and outlines precisely what is a physical measurement versus a placeholder estimate.

---

## 2. Quantity Sourcing Taxonomy & Fallback Pipeline

To maintain strict integrity, the QTE tracks the pedigree of every dimensional point. We define six hierarchical sourcing classifications:

```
               +-------------------------------------------------+
               |              QTE DATA FALLBACK PIPELINE         |
               +-------------------------------------------------+
               |  1. VERIFIED PROPERTY DATA                      |
               |     (Immutable GIS records, physical surveys)   |
               |                                                 |
               |  2. DIGITAL TWIN MEASUREMENT                    |
               |     (Three.js vertex coordinate calculations)   |
               |                                                 |
               |  3. AI-DERIVED MEASUREMENT                      |
               |     (Computer-vision image segmentation bounds) |
               |                                                 |
               |  4. HOMEOWNER INPUT                             |
               |     (Manual overrides or sliders in workspace)  |
               |                                                 |
               |  5. TEMPLATE ALLOWANCE                          |
               |     (Fallback averages from project library)    |
               |                                                 |
               |  6. UNKNOWN                                     |
               |     (Requires field verification / site visit)  |
               +-------------------------------------------------+
```

### 2.1. Sourcing Hierarchy Rules
The engine executes a cascading fallback sequence. If a higher-tier source is unavailable or invalidated, it falls back to the next tier:
1. **Verified Property Data**: Certified municipal property records, LIDAR flyovers, or structural drawings saved in the Passport.
2. **Digital Twin Measurement**: Scaled coordinate vectors captured on the active 3D model in the Design Studio canvas.
3. **AI-Derived Measurement**: Segmented pixel boundaries translated to real-world measurements by multiplying camera focal lengths with known reference scales (e.g., standard window heights).
4. **Homeowner Input**: Homeowner-adjusted sliders representing custom physical bounds (e.g., "I want a 15x20 patio").
5. **Template Allowance**: Standard planning parameters retrieved from the Project Template Library (e.g., standard double-garage footprint of 440 sqft).
6. **Unknown**: Declared whenever there are zero data boundaries, triggering high contingency buffers and a recommended contractor verification action.

---

## 3. Mathematical Takeoff Formulas

The QTE maps spatial dimensions to structural purchase orders using standardized mathematical operations.

### 3.1. Roofing Deck & Shingle Quantity

$$\text{Roof Area (sqft)} = \text{Footprint Area} \times \text{Pitch Factor}$$

Where the Pitch Factor is defined by the roof slope ($x$ in 12):

$$\text{Pitch Factor} = \frac{\sqrt{x^2 + 12^2}}{12}$$

$$\text{Squares of Shingles} = \text{ceil} \left( \frac{\text{Roof Area}}{100} \times (1 + \mathcal{W}_{\text{roof}}) \right)$$

*   *Unit*: **Square (SQ)** (1 SQ = 100 square feet of coverage).
*   *Waste Factor ($\mathcal{W}_{\text{roof}}$)*: Default `0.10` (10%) for gable roofs; `0.15` (15%) for multi-hip roofs.

### 3.2. Siding & Trim Quantities

$$\text{Net Siding Area (sqft)} = \sum \left( \text{Wall Height} \times \text{Wall Length} \right) - \sum \left( \text{Aperture Area}_{\text{windows/doors}} \right)$$

$$\text{Purchase Area} = \text{Net Siding Area} \times (1 + \mathcal{W}_{\text{siding}})$$

*   *Unit*: **Square Feet (SQFT)**.
*   *Waste Factor ($\mathcal{W}_{\text{siding}}$)*: Default `0.08` (8%) for horizontal lap; `0.12` (12%) for vertical board and batten.
*   *Linear Trim*: Measured in **Linear Feet (LF)** encompassing corner boards, frieze boards, and fascia.

### 3.3. Concrete Volume (Patios, Footings, Slabs)

$$\text{Volume (yd}^3\text{)} = \frac{\text{Slab Area (sqft)} \times \left( \frac{\text{Thickness (inches)}}{12} \right)}{27} \times (1 + \mathcal{W}_{\text{concrete}})$$

*   *Unit*: **Cubic Yard (CY)**.
*   *Waste Factor ($\mathcal{W}_{\text{concrete}}$)*: Default `0.05` (5%) for pump/chute pours to offset subbase absorption and forming flex.

### 3.4. Framing Board Feet Calculation

$$\text{Board Footage (BF)} = \frac{\text{Thickness (inches)} \times \text{Width (inches)} \times \text{Length (feet)}}{12} \times \text{Count}$$

*   *Unit*: **Board Foot (FBM / BF)**.
*   *Framing Formula for Studs (16" On-Center)*:

$$\text{Stud Count} = \text{ceil} \left( \frac{\text{Wall Length (feet)} \times 12}{16} \right) + \text{Corners}_c + \text{Jambs}_j$$

---

## 4. Takeoff Formula Map

The following map defines standard inputs, outputs, and default sourcing paths across key project types:

| Assembly Type | Input Source (Primary) | QTE Formula | Output Unit | Default Waste ($\mathcal{W}$) |
| :--- | :--- | :--- | :--- | :--- |
| **Roofing shingles** | Digital Twin Mesh | $\text{Roof SQFT} / 100$ | SQ | 10% (Gable) / 15% (Hip) |
| **Siding panels** | AI Segmented Façade | $\text{Wall SQFT} - \text{Aperture SQFT}$ | SQFT | 8% (Lap) / 12% (Shingle) |
| **Gutters & Downspouts**| Digital Twin Mesh | Edge length perimeter summation | LF | 5% (Seamless extrusion) |
| **Concrete Slab** | Homeowner Input | $\text{Area} \times \text{Thickness} / 324$ | CY | 5% (Standard) |
| **Decking boards** | Digital Twin Mesh | $\text{Deck Floor SQFT} \times 1.05$ | SQFT | 5% (Linear) / 10% (Diagonal)|
| **Excavation Soil** | AI Soil Profile | $\text{Area} \times \text{Depth} / 27$ | CY (Swell) | 15% (Swell factor expansion)|
| **Interior Painting** | Template Allowance | $(\text{Floor Area} \times 2.5) + \text{Floor Area}$| SQFT | 10% (Paintable ceiling/wall) |

---

## 5. Geometric Extraction Algorithm (Pseudo-Code)

Below is the JavaScript logic executed inside the Design Studio Three.js pipeline to resolve a 3D polygonal surface selection into a real-world quantity payload.

```javascript
/**
 * Resolves 3D Canvas geometry selections into physical takeoff quantities.
 * @param {THREE.Mesh} activeMesh - The highlighted 3D object on the canvas.
 * @param {string} sourceCategory - The verified pedigree of the source data.
 * @returns {Object} Takeoff Quantity payload.
 */
function calculateTakeoffFromMesh(activeMesh, sourceCategory) {
  // 1. Extract scale and vertices
  const geometry = activeMesh.geometry;
  const scale = activeMesh.scale;
  
  let totalArea = 0;
  
  // 2. Loop through face buffer arrays to compute surface area
  const position = geometry.attributes.position;
  const index = geometry.index;
  
  if (index) {
    for (let i = 0; i < index.count; i += 3) {
      const a = index.getX(i);
      const b = index.getX(i + 1);
      const c = index.getX(i + 2);
      
      const vA = new THREE.Vector3(position.getX(a), position.getY(a), position.getZ(a)).multiply(scale);
      const vB = new THREE.Vector3(position.getX(b), position.getY(b), position.getZ(b)).multiply(scale);
      const vC = new THREE.Vector3(position.getX(c), position.getY(c), position.getZ(c)).multiply(scale);
      
      const triangle = new THREE.Triangle(vA, vB, vC);
      totalArea += triangle.getArea();
    }
  }

  // 3. Apply scale mapping (1 Three.js unit = 1 meter or 1 foot based on scene config)
  const convertedAreaSqFt = totalArea * (scene.config.unitsPerMeter === 3.28084 ? 10.7639 : 1.0);

  return {
    quantity: parseFloat(convertedAreaSqFt.toFixed(2)),
    unit: "sqft",
    source_declaration: {
      source_category: sourceCategory || "Digital Twin Measurement",
      measurement_date: new Date().toISOString(),
      referenced_file_or_field: `mesh_uuid_${activeMesh.uuid}`
    }
  };
}
```

Through this mechanism, the takeoff parameters are completely grounded in the underlying geometric architecture, maintaining a continuous thread between visual canvas state and mathematical ledger costs.
