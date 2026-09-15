"""SQLAlchemy ORM models for materials, clusters, reviews, and standard codes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean, Table,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import relationship, Mapped

from app.database import Base


# ---------------------------------------------------------------------------
# Association: material -> harmonized cluster
# ---------------------------------------------------------------------------
material_cluster = Table(
    "material_cluster",
    Base.metadata,
    Column("material_id", String, ForeignKey("materials.id"), primary_key=True),
    Column("cluster_id", String, ForeignKey("clusters.id"), primary_key=True),
)


class Material(Base):
    __tablename__ = "materials"

    id = Column(String, primary_key=True)  # source CPSE + raw id, e.g. "cpse_a_001"
    source_cpse_id = Column(String, nullable=False)
    source_material_id = Column(String, nullable=False)
    raw_description = Column(Text, nullable=False)
    cleaned_description = Column(Text, nullable=False)
    unit = Column(String, nullable=True)
    material_group = Column(String, nullable=True)
    plant = Column(String, nullable=True)
    extracted_attrs = Column(JSON, nullable=True)   # dict from regex/spaCy
    embedding = Column(JSON, nullable=True)         # list[float]
    created_at = Column(DATETIME, default=lambda: datetime.now(timezone.utc))

    clusters = relationship("Cluster", secondary=material_cluster, back_populates="materials")
    reviews = relationship("ReviewDecision", back_populates="material")


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(String, primary_key=True)
    representative_description = Column(Text, nullable=True)
    standard_code = Column(String, nullable=True)
    standard_label = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    review_status = Column(String, default="pending")  # pending | approved | rejected | edited
    created_at = Column(DATETIME, default=lambda: datetime.now(timezone.utc))

    materials = relationship("Material", secondary=material_cluster, back_populates="clusters")
    reviews = relationship("ReviewDecision", back_populates="cluster")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String, ForeignKey("materials.id"), nullable=False)
    cluster_id = Column(String, ForeignKey("clusters.id"), nullable=True)
    action = Column(String, nullable=False)  # approved | rejected | edited
    merged_cluster_id = Column(String, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DATETIME, default=lambda: datetime.now(timezone.utc))

    material = relationship("Material", back_populates="reviews")
    cluster = relationship("Cluster", back_populates="reviews")


class StandardCode(Base):
    """Reference UNSPSC-style catalog."""
    __tablename__ = "standard_codes"

    code = Column(String, primary_key=True)          # e.g. "10151501"
    label = Column(String, nullable=False)
    parent_code = Column(String, nullable=True)
    level = Column(Integer, nullable=False)          # 1..4 hierarchical
    embedding = Column(JSON, nullable=True)          # vector of the label
    description = Column(Text, nullable=True)
