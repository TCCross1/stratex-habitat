"""Pydantic request schemas for Reality Studio APIs (Phase 11)."""
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class CoordinateFrameCreate(BaseModel):
    frame_type: str
    parent_frame_id: Optional[str] = None
    transform_to_parent: Optional[List[List[float]]] = None
    transform_to_property: Optional[List[List[float]]] = None
    origin_state: str = "PROVISIONAL"
    origin_source: str = "UNKNOWN_SOURCE"
    orientation_source: Optional[str] = None
    elevation_datum_source: Optional[str] = None
    tolerance_class: str = "PLANNING"
    residual_error_m: Optional[float] = None
    confidence: str = "LOW"


class SpatialEntityCreate(BaseModel):
    entity_type: str
    label: Optional[str] = None
    parent_entity_id: Optional[str] = None
    building_id: Optional[str] = None
    coordinate_frame_id: Optional[str] = None
    opening_ref: Optional[str] = None
    geometry_type: str = "NONE"
    geometry_reference: Optional[str] = None
    truth_classification: str = "MEASURED_EXISTING"
    source_classification: str = "HOMEOWNER_INPUT"
    confidence: str = "MEDIUM"
    units: str = "METRIC_M"
    existing_state: str = "EXISTING"
    access_classification: str = "HOMEOWNER"
    unknowns: Optional[List[str]] = None
    dimensions: Optional[Dict[str, Any]] = None


class ScanSessionCreate(BaseModel):
    capture_type: str
    coordinate_frame_id: Optional[str] = None
    device: Optional[Dict[str, Any]] = None
    sensors: Optional[List[str]] = None
    app_version: Optional[str] = None
    capture_mode: Optional[str] = None
    privacy_classification: str = "SENSITIVE_INTERIOR"
    idempotency_key: Optional[str] = None
    expires_in_seconds: Optional[int] = None


class ScanTransition(BaseModel):
    to_state: str
    expected_version: Optional[int] = None
    idempotency_key: Optional[str] = None


class ArtifactManifestCreate(BaseModel):
    artifact_type: str
    checksum_sha256: str
    storage_object_reference: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = 0
    model_version_id: Optional[str] = None
    source_artifact_ids: Optional[List[str]] = None
    derivation: Optional[Dict[str, Any]] = None
    processor: Optional[str] = None
    truth_classification: str = "UNKNOWN"


class ExistingModelCreate(BaseModel):
    source_scan_session_ids: Optional[List[str]] = None
    spatial_entity_ids: Optional[List[str]] = None
    coordinate_frame_version: int = 1
    artifact_ids: Optional[List[str]] = None
    truth_summary: Optional[Dict[str, Any]] = None
    quality_summary: Optional[Dict[str, Any]] = None
    unknown_areas: Optional[List[str]] = None
    previous_version_id: Optional[str] = None


class ExistingModelTransition(BaseModel):
    to_state: str
    expected_version: Optional[int] = None


class DesignModelCreate(BaseModel):
    base_existing_model_version_id: str
    proposed_entities: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    deltas: Optional[Dict[str, Any]] = None
    previous_design_version_id: Optional[str] = None
