"""Pydantic schemas for request/response bodies."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MaterialBase(BaseModel):
    source_cpse_id: str = Field(..., example="cpse_a")
    source_material_id: str = Field(..., example="mat_001")
    raw_description: str = Field(..., example="SS Pipe 10mm x 5m")
    unit: Optional[str] = Field(None, example="m")
    material_group: Optional[str] = Field(None, example="Pipes")
    plant: Optional[str] = Field(None, example="Plant_01")


class MaterialCreate(MaterialBase):
    pass


class Material(MaterialBase):
    id: str
    cleaned_description: str
    extracted_attrs: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClusterBase(BaseModel):
    representative_description: Optional[str] = None
    standard_code: Optional[str] = None
    standard_label: Optional[str] = None
    confidence: Optional[Confidence] = None
    review_status: str = Field(default="pending")


class Cluster(ClusterBase):
    id: str
    materials: List[Material] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


class ReviewDecisionBase(BaseModel):
    material_id: str
    action: ReviewAction
    reviewer_notes: Optional[str] = None


class ReviewDecisionCreate(ReviewDecisionBase):
    pass


class ReviewDecisionOut(ReviewDecisionBase):
    id: int
    merged_cluster_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StandardCodeBase(BaseModel):
    code: str
    label: str
    parent_code: Optional[str] = None
    level: int
    description: Optional[str] = None


class StandardCode(StandardCodeBase):
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    upload_id: str
    total_records: int
    processed: int
    message: str


class ProcessStatus(BaseModel):
    stage: str
    progress: int  # 0-100
    details: Optional[str] = None
    completed: bool = False


class MetricsResponse(BaseModel):
    total_raw: int
    unique_after: int
    duplication_rate: float
    cost_saving_proxy: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    by_category: Dict[str, int] = {}


class SearchResult(BaseModel):
    material: Material
    cluster: Optional[Cluster] = None
    similarity_score: float


# ---------------------------------------------------------------------------
# WebSocket messages for live progress
# ---------------------------------------------------------------------------
class ProgressMessage(BaseModel):
    type: str = "progress"
    stage: str
    progress: int
    details: Optional[str] = None


class ClusterFoundMessage(BaseModel):
    type: str = "cluster_found"
    cluster: Cluster
    materials: List[Material]


class ReviewItemMessage(BaseModel):
    type: str = "review_item"
    materials: List[Material]
    similarity_score: float