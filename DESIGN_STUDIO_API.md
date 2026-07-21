# DESIGN STUDIO 2.0 API CONTRACT & EVENT SCHEMAS
## REST ENDPOINTS, WEBSOCKET INTERACTION PROTOCOLS, & DATA PAYLOADS
**Version:** 2.0  
**Classification:** HABITAT-CONFIDENTIAL

This specification defines the backend FastAPI endpoints and real-time WebSocket protocol contracts that power the collaborative workspace, AI Design Assistant, and Dynamic Estimator in Habitat Design Studio 2.0.

---

## 1. RESTful ENDPOINT REGISTER

All HTTP endpoints use a base path of `/api/v2/design-studio/`. Inputs and outputs are encoded in strict UTF-8 JSON.

```
+---------------------------------------------------------------------------------+
|                       DESIGN STUDIO REST API OVERVIEW                           |
+---------------------------------------------------------------------------------+
|  POST /sessions               ---> Initialize design canvas state.              |
|  GET  /materials              ---> Query, search, and filter PBR materials.      |
|  POST /scenarios              ---> Save design selections to Mongo.             |
|  POST /scenarios/{id}/versions ---> Commit a new history version.               |
|  POST /budget/calculate       ---> Fetch ZIP-tuned confidence estimates.         |
|  POST /packages/export         ---> Compile contractor RFP packages.             |
+---------------------------------------------------------------------------------+
```

---

## 2. DETAIL SPECIFICATIONS FOR CORE ENDPOINTS

### Endpoint 1: Initialize Customization Session
- **Path**: `POST /sessions`
- **Description**: Bootstraps the interactive workspace by fetching properties, active modules, and existing scans.
- **Request Payload**:
  ```json
  {
    "property_id": "prop-4492-co",
    "module_id": "outdoor-living"
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "session_id": "ds-sess-9214-xo",
    "property_id": "prop-4492-co",
    "module_config": {
      "id": "outdoor-living",
      "name": "Outdoor Living Studio",
      "zones": [
        { "id": "patio_decking", "label": "Patio Decking Material", "accepts": ["composite_decking", "timber_decking"] }
      ]
    },
    "existing_twin_assets": {
      "scan_base_url": "https://assets.habitat.sh/scans/prop-4492-co.obj",
      "boundary_vertices_geojson": { "type": "Polygon", "coordinates": [] }
    }
  }
  ```

### Endpoint 2: Material Search & Filter
- **Path**: `GET /materials`
- **Description**: Sifting materials based on zone requirements, cost levels, and durability.
- **Query Parameters**:
  - `zone_id` (string, required) — e.g. `patio_decking`
  - `price_tiers` (comma-separated list, optional) — e.g. `$,$$`
  - `search_query` (string, optional) — e.g. `Trex`
- **Response Payload (200 OK)**:
  ```json
  {
    "zone_id": "patio_decking",
    "results_count": 1,
    "materials": [
      {
        "sku_id": "TRX-4492-CD",
        "manufacturer": "Trex",
        "brand_name": "Transcend",
        "product_line": "Lineage High-Performance Decking",
        "base_cost_per_sqft": 7.50,
        "colors": [
          { "name": "Carmel Cool Ash", "hex": "#807E7B" }
        ],
        "pbr_constants": {
          "roughness": 0.70,
          "metallic": 0.02
        }
      }
    ]
  }
  ```

### Endpoint 3: Lock Scenario & Create Version
- **Path**: `POST /scenarios`
- **Description**: Saves the design state as a persistent scenario or commits a new incremental version record.
- **Request Payload**:
  ```json
  {
    "property_id": "prop-4492-co",
    "name": " v1: High-Contrast Deck",
    "module_id": "outdoor-living",
    "selections": [
      { "zone_id": "patio_decking", "product_id": "TRX-4492-CD", "color_name": "Carmel Cool Ash" }
    ],
    "spatial_data": {
      "calculated_area_sqft": 192.0
    }
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "scenario_id": "scen-8893-wq",
    "version_committed": 1,
    "created_at": "2026-07-21T11:08:31.000Z",
    "status": "saved"
  }
  ```

### Endpoint 4: Calculate Live Localized Budget
- **Path**: `POST /budget/calculate`
- **Description**: Evaluates material volume and localized labor indices to produce itemized tier costs.
- **Request Payload**:
  ```json
  {
    "scenario_id": "scen-8893-wq",
    "zip_code": "80202"
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "scenario_id": "scen-8893-wq",
    "zip_code": "80202",
    "labor_index": 1.12,
    "tax_multiplier": 0.0881,
    "itemized_ledger": [
      {
        "id": "item-001",
        "label": "Trex Transcend Decking Boards (Materials)",
        "cost": 2880.00,
        "confidence": "verified",
        "category": "material"
      },
      {
        "id": "item-002",
        "label": "Tuned Decking Framing Labor (Denver average)",
        "cost": 5100.00,
        "confidence": "estimated",
        "category": "labor"
      }
    ],
    "total_range_low": 7980.00,
    "total_range_high": 8450.00
  }
  ```

---

## 3. WEBSOCKET REAL-TIME SYNC PROTOCOL (`ws://api.habitat.sh/v2/design-studio/session-sync`)

WebSockets are utilized to provide latency-free updates for collaborative co-design, spatial placements, and conversational AI streams.

```
                           +------------------------+
                           |  WS EVENT COORDINATOR  |
                           +-----------+------------+
                                       |
          +----------------------------+----------------------------+
          |                            |                            |
          v                            v                            v
[ SPATIAL_DRAG ]             [ AI_PROMPT ]                [ VALIDATION_ALERTS ]
- Coordinates (X,Y,Z).       - Conversational stream.     - Collision notifications.
- Anchor alignment.          - Dynamic UI controls.       - Red-border warnings.
```

### Event Message Payloads (Server-to-Client)

#### 1. Real-Time Spatial Translation Event (`SPATIAL_MOVE`)
Sent when a user translates or rotates an object on the 3D grid. Updates coordinate matrices in local cache.
```json
{
  "event_type": "SPATIAL_MOVE",
  "payload": {
    "session_id": "ds-sess-9214-xo",
    "object_id": "obj-adu-01",
    "coordinates": { "x": 12.5, "y": 0.0, "z": -8.0 },
    "rotation_degrees": 45.0,
    "scale_factor": 1.0
  }
}
```

#### 2. Spatial Collision Alert (`VALIDATION_ALERT`)
Sent when a translation overlaps a lot boundary, existing structure, or utility easement zone.
```json
{
  "event_type": "VALIDATION_ALERT",
  "payload": {
    "session_id": "ds-sess-9214-xo",
    "object_id": "obj-adu-01",
    "status": "violating",
    "rule_id": "setback_limit_rear",
    "error_message": "Accessory Dwelling Unit (ADU) overlaps rear property 5-foot setback boundary.",
    "boundary_lines_intersected": [ { "x1": 5.0, "z1": -10.0, "x2": 25.0, "z2": -10.0 } ]
  }
}
```

#### 3. AI Assistant Chat Streaming Event (`AI_STREAM`)
Delivers incremental assistant responses for fluid real-time chat displays.
```json
{
  "event_type": "AI_STREAM",
  "payload": {
    "session_id": "ds-sess-9214-xo",
    "chunk_index": 42,
    "is_complete": false,
    "chunk_content": "Trex Transcend Carmel Cool Ash composite decking. This "
  }
}
```
---

## 4. DESIGN STUDIO CLIENT SYNC & STATE-MACHINE

When disconnected, the React workspace queues interactions locally. Upon WebSocket reconnection, the client dispatches a batch `CLIENT_SYNC` event to the API Gateway, synchronizing the server-side scenario draft with zero user disruption.
