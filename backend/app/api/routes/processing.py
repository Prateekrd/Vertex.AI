"""Processing endpoint: CSV parsing, embedding, clustering, live progress."""
from __future__ import annotations

import asyncio
import csv
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.dependencies import get_db_session
from app.schemas import ProcessStatus
from app.services.preprocessing import preprocess_material
from app.services.embedding import embedding_service, get_embedding_service
from app.services.clustering import clustering_service, get_clustering_service
from app.services.metrics import compute_cluster_metrics, load_ground_truth_from_file
from app.api.websocket import ws_manager

router = APIRouter()


@router.get("/status/{job_id}")
def get_status(job_id: str):
    """Check processing status (polling fallback)."""
    return {"job_id": job_id, "status": "pending"}


@router.websocket("/ws/{job_id}")
async def process_stream(websocket: WebSocket, job_id: str):
    """Stream processing progress via WebSocket."""
    await ws_manager.connect(websocket, job_id)
    try:
        await websocket.receive_text()  # Wait for any message to keep connection open
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)


async def run_processing_pipeline(
    job_id: str,
    records: List[Dict[str, Any]],
    websocket: WebSocket = None,
):
    """
    Full pipeline: preprocess → embed → cluster → map codes → emit events.
    """
    es = get_embedding_service()
    cs = get_clustering_service()

    async def send_progress(stage: str, progress: int, details: str = None):
        msg = {
            "type": "progress",
            "stage": stage,
            "progress": progress,
            "details": details,
        }
        if websocket:
            try:
                await websocket.send_text(json.dumps(msg))
            except Exception:
                pass

    # Stage 1: Preprocess
    await send_progress("preprocessing", 10, f"Parsing {len(records)} records...")
    processed_records = []
    for i, rec in enumerate(records):
        processed = preprocess_material(rec)
        processed["source_material_id_full"] = f"{rec['source_cpse_id']}_{rec['source_material_id']}"
        processed_records.append(processed)

    # Stage 2: Generate embeddings
    await send_progress("embedding", 40, "Generating sentence embeddings...")
    descriptions = [r["cleaned_description"] for r in processed_records]
    embeddings = es.encode(descriptions)
    for i, rec in enumerate(processed_records):
        rec["embedding"] = embeddings[i].tolist()

    # Stage 3: Cluster
    await send_progress("clustering", 70, "Finding duplicate clusters...")
    material_ids = [r["source_material_id_full"] for r in processed_records]
    attrs_list = [r.get("extracted_attrs", {}) for r in processed_records]

    cluster_result = cs.cluster_materials(material_ids, embeddings)

    # Build cluster objects
    clusters_data = []
    for cluster_ids in cluster_result:
        cluster_members = [processed_records[i] for i in cluster_ids]
        scores = []
        for i in range(len(cluster_ids)):
            for j in range(i + 1, len(cluster_ids)):
                sim = cs.composite_similarity(
                    cluster_members[i]["cleaned_description"],
                    cluster_members[j]["cleaned_description"],
                    cluster_members[i].get("extracted_attrs"),
                    cluster_members[j].get("extracted_attrs"),
                    embeddings[cluster_ids[i]],
                    embeddings[cluster_ids[j]],
                )
                scores.append(sim["composite"])

        avg_score = sum(scores) / len(scores) if scores else 1.0
        confidence = "high" if avg_score >= 0.9 else ("medium" if avg_score >= 0.7 else "low")

        clusters_data.append({
            "cluster_id": f"cluster_{uuid.uuid4().hex[:8]}",
            "member_ids": cluster_ids,
            "representative": cluster_members[0]["cleaned_description"],
            "avg_similarity": avg_score,
            "confidence": confidence,
            "members": cluster_members,
        })

    # Stage 4: Map to standard codes + ground truth
    await send_progress("mapping", 90, "Mapping to standard codes...")
    from app.services.standard_catalog import standard_code_catalog

    for cluster in clusters_data:
        results = standard_code_catalog.find_closest(cluster["representative"])
        if results:
            cluster["standard_code"] = results[0]["code"]
            cluster["standard_label"] = results[0]["label"]
        else:
            cluster["standard_code"] = "00000000"
            cluster["standard_label"] = "Uncategorized"

    # Load ground truth and compute metrics
    gt_path = settings.DATA_DIR / "ground_truth.json"
    if gt_path.exists():
        gt = load_ground_truth_from_file(str(gt_path))
        metrics = compute_cluster_metrics(
            [c["member_ids"] for c in clusters_data],
            gt,
        )
    else:
        metrics = {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}

    await send_progress("done", 100, f"Found {len(clusters_data)} clusters")

    return {
        "records": processed_records,
        "clusters": clusters_data,
        "metrics": metrics,
    }


@router.post("/process")
async def process_uploads(
    background_tasks: BackgroundTasks,
    record_ids: List[str],
):
    """Process uploaded records by ID (placeholder for real implementation)."""
    return JSONResponse(content={"message": "Processing started", "job_id": "demo_job_1"})
