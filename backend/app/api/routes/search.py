"""Search endpoint: find similar materials by description."""
from __future__ import annotations

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.embedding import get_embedding_service

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


@router.post("/")
def search_materials(request: SearchRequest):
    """Search for materials by description, return similar matches."""
    es = get_embedding_service()

    # Encode the query
    query_emb = es.encode([request.query])[0]

    # Read the in-memory cluster/embedding state (from a cached build)
    # In a real impl, this would query the database/FAISS index
    # For demo, load all materials from CSV files
    materials = []
    embeddings = []
    ids = []

    for csv_file in settings.DATA_DIR.glob("cpse_*_materials.csv"):
        import csv
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc = row["description"]
                full_id = f"{row['source_cpse_id']}_{row['source_material_id']}"
                emb = es.encode([desc])[0]
                materials.append({
                    "id": full_id,
                    "source_cpse_id": row["source_cpse_id"],
                    "source_material_id": row["source_material_id"],
                    "description": desc,
                    "unit": row.get("unit", ""),
                    "material_group": row.get("material_group", ""),
                })
                embeddings.append(emb)
                ids.append(full_id)

    if not materials:
        return {"query": request.query, "results": [], "message": "No materials loaded"}

    # Compute similarities
    emb_matrix = np.array(embeddings)
    similarities = emb_matrix @ query_emb  # dot product on normalized vectors

    # Top-k
    top_indices = np.argsort(similarities)[::-1][:request.top_k]

    results = []
    for idx in top_indices:
        sim = float(similarities[idx])
        if sim < 0.3:  # Threshold
            continue
        results.append({
            "material": materials[idx],
            "similarity_score": sim,
        })

    return {
        "query": request.query,
        "results": results,
        "total_searched": len(materials),
    }


@router.post("/by-code/{standard_code}")
def search_by_standard_code(standard_code: str):
    """Search materials by their assigned standard code."""
    from app.services.standard_catalog import standard_code_catalog

    matches = []
    for code_entry in standard_code_catalog.list_all():
        if standard_code in code_entry["code"]:
            matches.append(code_entry)

    return {
        "standard_code": standard_code,
        "matches": matches,
    }
