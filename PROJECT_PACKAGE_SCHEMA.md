# CENTCOM DIRECTIVE H-003: PROJECT PACKAGE SCHEMA
## CANONICAL DATA STRUCTURES AND REFERENCES
**Version:** 1.0  
**Author:** Principal Data Engineer  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction

This specification defines the formal **Project Opportunity Package (POP)** schema using standard **JSON Schema (Draft-07)** syntax. 

To maintain system integrity, reduce storage overhead, and prevent data desynchronization, the schema is designed around **referential canonical integrity**. It is a strict architectural requirement that **no duplicate Passport data** and **no duplicate Property DNA** are stored within the project package. All project packages must reference these canonical structures via unique IDs and secure relationship references.

---

## 2. Technical Architectural Principles

```
  +--------------------------------------------------------------------------+
  |                   CANONICAL REFERENTIAL ARCHITECTURE                     |
  +--------------------------------------------------------------------------+
  |                                                                          |
  |    [ Property DNA Registry ]                [ Digital Passport Service ] |
  |    - Structural blueprint                  - Historical health log      |
  |    - Thermal envelope stats                - Previous permits & scans   |
  |    (Stored in Property Collection)         (Stored in Passport Coll.)   |
  |                        ^                                ^                |
  |                        | referenced via ID              | referenced     |
  |                        +----------------+---------------+                |
  |                                         |                                |
  |                                         v                                |
  |                        [ Project Opportunity Package ]                   |
  |                        - Active project details                          |
  |                        - Material selections                             |
  |                        - AI intelligence recommendations                 |
  |                        - Homeowner preferences                           |
  |                                                                          |
  +--------------------------------------------------------------------------+
```

1. **Immutable Property DNA Reference:** The Property DNA contains the physical blueprint, dimensions, and zoning characteristics of the home. The POP stores only a `property_id` and an optional `dna_snapshot_hash` to represent the state of the property at the moment of package creation, preventing flat-file replication.
2. **Referential Passport Access:** The POP stores a read-only `passport_id`. Contractors who are matched to the opportunity are granted time-limited, read-only access to relevant passport layers through secure APIs rather than containing nested copies of the passport history.
3. **No Duplicate Material Schemas:** Material selections must reference canonical product definitions within the **Module Registry** via a unique product SKU, manufacturer ID, and colorway ID.
4. **Mandatory AI Explanations and Confidence Levels:** The schema strictly enforces that every recommendation contains an explanation string (`why`) and every cost estimate is accompanied by an explicit `confidence_level`.

---

## 3. Comprehensive JSON Schema Specification

The following JSON Schema defines the complete, structural validation rules for a Project Opportunity Package:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ProjectOpportunityPackage",
  "description": "The canonical, normalized data package representing a contractor-ready renovation project opportunity.",
  "type": "object",
  "required": [
    "opportunity_id",
    "property_id",
    "passport_id",
    "status",
    "project",
    "design",
    "ai_intelligence",
    "homeowner_preferences"
  ],
  "properties": {
    "opportunity_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique, immutable identifier for the project opportunity."
    },
    "property_id": {
      "type": "string",
      "format": "uuid",
      "description": "Canonical reference to the Property record. Duplication of full Property DNA is strictly prohibited."
    },
    "passport_id": {
      "type": "string",
      "format": "uuid",
      "description": "Canonical reference to the Digital Home Passport. Duplication of Passport logs is strictly prohibited."
    },
    "status": {
      "type": "string",
      "enum": [
        "concept",
        "ai_review",
        "homeowner_approval",
        "publish_opportunity",
        "matched_contractors",
        "questions",
        "proposal_submission",
        "proposal_comparison",
        "contractor_selected",
        "construction",
        "completion_verification",
        "passport_updated"
      ],
      "description": "The current state of the opportunity in the Project Opportunity Lifecycle."
    },
    "project": {
      "type": "object",
      "required": [
        "type",
        "scope_summary"
      ],
      "properties": {
        "type": {
          "type": "string",
          "enum": [
            "garage",
            "deck",
            "patio",
            "pool",
            "room_addition",
            "concrete",
            "pergola",
            "fence",
            "landscape",
            "outdoor_kitchen",
            "adu",
            "roof",
            "windows",
            "doors",
            "solar",
            "custom"
          ],
          "description": "The officially supported functional category of the project."
        },
        "scope_summary": {
          "type": "string",
          "minLength": 10,
          "maxLength": 1000,
          "description": "Brief description of the homeowner's project objectives."
        }
      }
    },
    "design": {
      "type": "object",
      "required": [
        "scenario_id",
        "version",
        "selected_materials",
        "color_palette",
        "version_history"
      ],
      "properties": {
        "scenario_id": {
          "type": "string",
          "format": "uuid",
          "description": "Identifies the active design scenario in the Design Studio."
        },
        "version": {
          "type": "integer",
          "minimum": 1,
          "description": "Active version number of the design."
        },
        "ai_renderings": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "rendering_id",
              "image_url",
              "camera_angle_id",
              "lighting_preset"
            ],
            "properties": {
              "rendering_id": {
                "type": "string",
                "format": "uuid"
              },
              "image_url": {
                "type": "string",
                "format": "uri"
              },
              "camera_angle_id": {
                "type": "string"
              },
              "lighting_preset": {
                "type": "string",
                "enum": [
                  "daylight",
                  "overcast",
                  "sunset",
                  "night"
                ]
              }
            }
          }
        },
        "before_after_views": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "before_image_url",
              "after_image_url",
              "camera_angle_id"
            ],
            "properties": {
              "before_image_url": {
                "type": "string",
                "format": "uri"
              },
              "after_image_url": {
                "type": "string",
                "format": "uri"
              },
              "camera_angle_id": {
                "type": "string"
              }
            }
          }
        },
        "selected_materials": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "zone_id",
              "manufacturer_id",
              "product_sku",
              "colorway_id",
              "quantity_value",
              "quantity_unit"
            ],
            "properties": {
              "zone_id": {
                "type": "string",
                "description": "References a design zone in the Module Registry (e.g. siding_main)."
              },
              "manufacturer_id": {
                "type": "string"
              },
              "product_sku": {
                "type": "string"
              },
              "colorway_id": {
                "type": "string"
              },
              "quantity_value": {
                "type": "number",
                "minimum": 0
              },
              "quantity_unit": {
                "type": "string",
                "enum": [
                  "sq_ft",
                  "lin_ft",
                  "units",
                  "cu_yds"
                ]
              }
            }
          }
        },
        "color_palette": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "hex_code",
              "name",
              "sheen"
            ],
            "properties": {
              "hex_code": {
                "type": "string",
                "pattern": "^#[0-9A-Fa-f]{6}$"
              },
              "name": {
                "type": "string"
              },
              "sheen": {
                "type": "string",
                "enum": [
                  "flat",
                  "satin",
                  "semi_gloss",
                  "gloss"
                ]
              }
            }
          }
        },
        "version_history": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "version",
              "saved_at",
              "saved_by",
              "materials_hash"
            ],
            "properties": {
              "version": {
                "type": "integer"
              },
              "saved_at": {
                "type": "string",
                "format": "date-time"
              },
              "saved_by": {
                "type": "string",
                "format": "uuid"
              },
              "materials_hash": {
                "type": "string"
              }
            }
          }
        }
      }
    },
    "ai_intelligence": {
      "type": "object",
      "required": [
        "compatibility_review",
        "architectural_harmony",
        "material_recommendations",
        "suggested_improvements",
        "estimated_complexity",
        "budget_assumptions"
      ],
      "properties": {
        "compatibility_review": {
          "type": "object",
          "required": [
            "passed",
            "why",
            "checks"
          ],
          "properties": {
            "passed": {
              "type": "boolean"
            },
            "why": {
              "type": "string",
              "description": "Explains why the overall compatibility passed or failed."
            },
            "checks": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "check_name",
                  "status",
                  "why"
                ],
                "properties": {
                  "check_name": {
                    "type": "string"
                  },
                  "status": {
                    "type": "string",
                    "enum": [
                      "pass",
                      "fail",
                      "warning",
                      "manual_review_required"
                    ]
                  },
                  "why": {
                    "type": "string",
                    "description": "Explains the technical evaluation details."
                  }
                }
              }
            }
          }
        },
        "architectural_harmony": {
          "type": "object",
          "required": [
            "harmony_score",
            "style_detected",
            "why"
          ],
          "properties": {
            "harmony_score": {
              "type": "integer",
              "minimum": 0,
              "maximum": 100
            },
            "style_detected": {
              "type": "string"
            },
            "why": {
              "type": "string",
              "description": "Provides architectural reasoning behind the score."
            }
          }
        },
        "material_recommendations": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "target_zone",
              "recommended_sku",
              "why"
            ],
            "properties": {
              "target_zone": {
                "type": "string"
              },
              "recommended_sku": {
                "type": "string"
              },
              "why": {
                "type": "string",
                "description": "Explains why this material is recommended over alternatives."
              }
            }
          }
        },
        "suggested_improvements": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "improvement_type",
              "description",
              "why"
            ],
            "properties": {
              "improvement_type": {
                "type": "string"
              },
              "description": {
                "type": "string"
              },
              "why": {
                "type": "string",
                "description": "Technical justification of why this improvement adds value."
              }
            }
          }
        },
        "estimated_complexity": {
          "type": "object",
          "required": [
            "level",
            "why"
          ],
          "properties": {
            "level": {
              "type": "string",
              "enum": [
                "low",
                "medium",
                "high",
                "extreme"
              ]
            },
            "why": {
              "type": "string",
              "description": "Explains why the project was classified with this complexity level."
            }
          }
        },
        "budget_assumptions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "item_id",
              "label",
              "cost_value",
              "confidence_level",
              "category",
              "why"
            ],
            "properties": {
              "item_id": {
                "type": "string"
              },
              "label": {
                "type": "string"
              },
              "cost_value": {
                "type": "number",
                "minimum": 0
              },
              "confidence_level": {
                "type": "string",
                "enum": [
                  "verified",
                  "estimated",
                  "suggested",
                  "future"
                ],
                "description": "Enforces transparent cost categorization."
              },
              "category": {
                "type": "string",
                "enum": [
                  "material",
                  "labor",
                  "permit",
                  "contingency"
                ]
              },
              "why": {
                "type": "string",
                "description": "Explains the calculation variables, measurements, or unit rates."
              }
            }
          }
        }
      }
    },
    "homeowner_preferences": {
      "type": "object",
      "required": [
        "desired_budget",
        "desired_timeline",
        "must_haves",
        "nice_to_haves",
        "preferred_contractor_distance_miles",
        "communication_preference"
      ],
      "properties": {
        "desired_budget": {
          "type": "object",
          "required": [
            "target",
            "max_cap"
          ],
          "properties": {
            "target": {
              "type": "number",
              "minimum": 0
            },
            "max_cap": {
              "type": "number",
              "minimum": 0
            }
          }
        },
        "desired_timeline": {
          "type": "object",
          "required": [
            "preferred_start_date",
            "must_complete_by"
          ],
          "properties": {
            "preferred_start_date": {
              "type": "string",
              "format": "date"
            },
            "must_complete_by": {
              "type": "string",
              "format": "date"
            }
          }
        },
        "must_haves": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "nice_to_haves": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "special_requests": {
          "type": "string"
        },
        "preferred_contractor_distance_miles": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100
        },
        "communication_preference": {
          "type": "object",
          "required": [
            "preferred_channels",
            "allow_unscheduled_calls"
          ],
          "properties": {
            "preferred_channels": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": [
                  "portal_chat",
                  "sms",
                  "email",
                  "phone"
                ]
              }
            },
            "allow_unscheduled_calls": {
              "type": "boolean"
            }
          }
        },
        "financing_interest": {
          "type": "boolean"
        }
      }
    }
  }
}
```
