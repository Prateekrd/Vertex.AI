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
from pydantic import BaseModel

from app.config import settings
from app.dependencies import get_db_session
from app.schemas import ProcessStatus
from app.services.preprocessing import preprocess_material
from app.services.embedding import embedding_service, get_embedding_service
from app.services.clustering import clustering_service, get_clustering_service
from app.services.metrics import compute_cluster_metrics, load_ground_truth_from_file
from app.api.websocket import ws_manager

router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory job store (maps job_id → status / results)
# ---------------------------------------------------------------------------
_jobs: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------
class StartRequest(BaseModel):
    upload_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper: load records for a job
# ---------------------------------------------------------------------------
def _load_records_for_upload(upload_id: str) -> List[Dict[str, Any]]:
    """Try to find records: first from an uploaded file, then from a specific sample dataset."""
    if not upload_id or not upload_id.strip():
        return []

    clean_id = upload_id.strip()

    # 0. Check in-memory upload registry first (most reliable — set right after upload)
    from app.api.routes.upload import upload_registry
    if clean_id in upload_registry:
        reg_path = upload_registry[clean_id]
        if reg_path.exists():
            print(f"[processing] Found upload via registry: {reg_path}")
            return _parse_csv(reg_path)

    # 1. Check uploads directory for a file matching the upload_id
    print(f"[processing] Searching UPLOAD_DIR={settings.UPLOAD_DIR} for '{clean_id}_*.csv'")
    for f in settings.UPLOAD_DIR.glob(f"{clean_id}_*"):
        if f.suffix.lower() == ".csv":
            print(f"[processing] Found upload via glob: {f}")
            return _parse_csv(f)

    # 2. Check if clean_id directly names a sample file in data directory
    if settings.DATA_DIR.exists():
        candidates = [
            settings.DATA_DIR / f"{clean_id}.csv",
            settings.DATA_DIR / f"{clean_id}_materials.csv",
        ]
        if clean_id.startswith("sample_"):
            sub_id = clean_id.replace("sample_", "", 1)
            candidates.extend([
                settings.DATA_DIR / f"{sub_id}.csv",
                settings.DATA_DIR / f"{sub_id}_materials.csv",
            ])
        for c in candidates:
            if c.exists() and c.is_file():
                return _parse_csv(c)

        for f in settings.DATA_DIR.glob("cpse_*_materials.csv"):
            if f.stem == clean_id:
                return _parse_csv(f)

    # Do not silently load all sample datasets! Return empty if not found.
    return []


def _parse_csv(path: Path) -> List[Dict[str, Any]]:
    """Parse a CSV file into a list of dicts."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "source_cpse_id": row.get("source_cpse_id") or row.get("cpse_id", "unknown"),
                "source_material_id": row.get("source_material_id") or row.get("material_id", str(uuid.uuid4())),
                "description": row.get("description", ""),
                "unit": row.get("unit", ""),
                "material_group": row.get("material_group", ""),
                "plant": row.get("plant", ""),
            })
    return records


# ---------------------------------------------------------------------------
# POST /start  — kick off processing, return job_id immediately
# ---------------------------------------------------------------------------
@router.post("/start")
async def start_processing(body: StartRequest, background_tasks: BackgroundTasks):
    """Start the processing pipeline.  Returns a job_id for WebSocket progress."""
    upload_id = (body.upload_id or "").strip()
    if not upload_id:
        raise HTTPException(
            status_code=400,
            detail="No dataset uploaded or selected. Please upload a CSV file or choose a sample dataset first."
        )

    records = _load_records_for_upload(upload_id)
    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No dataset records found for upload ID '{upload_id}'. Please upload a file first."
        )

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    _jobs[job_id] = {"status": "running", "total_records": len(records)}

    # Run pipeline in background so the HTTP response returns immediately
    background_tasks.add_task(_run_pipeline_background, job_id, records)

    return {"job_id": job_id, "total_records": len(records)}


# ---------------------------------------------------------------------------
# GET /status/{job_id}  — polling fallback
# ---------------------------------------------------------------------------
@router.get("/status/{job_id}")
def get_status(job_id: str):
    """Check processing status (polling fallback)."""
    info = _jobs.get(job_id, {"status": "unknown"})
    return {"job_id": job_id, **info}


# ---------------------------------------------------------------------------
# WebSocket /ws/{job_id}  — live progress stream
# ---------------------------------------------------------------------------
@router.websocket("/ws/{job_id}")
async def process_stream(websocket: WebSocket, job_id: str):
    """Stream processing progress via WebSocket."""
    await ws_manager.connect(websocket, job_id)
    try:
        # Keep alive: loop until client disconnects
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)
    except Exception:
        ws_manager.disconnect(websocket, job_id)


# ---------------------------------------------------------------------------
# Background pipeline runner
# ---------------------------------------------------------------------------
async def _run_pipeline_background(job_id: str, records: List[Dict[str, Any]]):
    """Wrapper that runs the full pipeline and broadcasts progress."""
    # Give the WebSocket client a moment to connect before we start sending
    await asyncio.sleep(1.5)
    try:
        result = await run_processing_pipeline(job_id, records)
        _jobs[job_id] = {"status": "done", "result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        _jobs[job_id] = {"status": "error", "error": str(e)}
        await ws_manager.send_progress(job_id, {
            "type": "error",
            "message": f"Pipeline error: {e}",
        })


# ---------------------------------------------------------------------------
# Full pipeline: preprocess → embed → cluster → map codes
# ---------------------------------------------------------------------------
async def run_processing_pipeline(
    job_id: str,
    records: List[Dict[str, Any]],
):
    """
    Full pipeline: preprocess → embed → cluster → map codes → emit events.
    All progress is broadcast via ws_manager so any connected WebSocket receives it.
    CPU-heavy steps are run in a thread executor to avoid blocking the event loop.
    """
    loop = asyncio.get_event_loop()
    es = get_embedding_service()
    cs = get_clustering_service()
    total = len(records)

    # Helper: broadcast a message to all WS clients for this job
    async def send(msg: Dict[str, Any]):
        await ws_manager.send_progress(job_id, msg)
        await asyncio.sleep(0)  # yield so WS messages can flush

    # ── Init ──────────────────────────────────────────────────────────────
    await send({"type": "init", "job_id": job_id, "total_records": total})

    # ── Stage 1: Preprocess ───────────────────────────────────────────────
    await send({"type": "stage_start", "stage": "preprocessing", "details": f"Parsing {total} records…"})

    def _preprocess_sync():
        processed = []
        for rec in records:
            p = preprocess_material(rec)
            p["source_material_id_full"] = f"{rec['source_cpse_id']}_{rec['source_material_id']}"
            processed.append(p)
        return processed

    processed_records = await loop.run_in_executor(None, _preprocess_sync)

    await send({"type": "progress", "stage": "preprocessing", "progress": 100, "details": f"Preprocessed {total} records", "items": total})
    await send({"type": "stage_done", "stage": "preprocessing", "details": "Preprocessing complete", "items": total})

    # ── Stage 2: Embeddings ───────────────────────────────────────────────
    await send({"type": "stage_start", "stage": "embedding", "details": "Loading sentence-transformer model…"})

    descriptions = [r["cleaned_description"] for r in processed_records]

    def _embed_sync():
        return es.encode(descriptions)

    embeddings = await loop.run_in_executor(None, _embed_sync)

    for i, rec in enumerate(processed_records):
        rec["embedding"] = embeddings[i].tolist()

    # Build FAISS index
    material_ids = [r["source_material_id_full"] for r in processed_records]

    def _build_index_sync():
        es.build_index(material_ids, embeddings)

    await loop.run_in_executor(None, _build_index_sync)

    await send({"type": "progress", "stage": "embedding", "progress": 100, "details": f"Encoded {total} descriptions", "items": total})
    await send({"type": "stage_done", "stage": "embedding", "details": "Embeddings & FAISS index built", "items": total})

    # ── Stage 3: Clustering ───────────────────────────────────────────────
    await send({"type": "stage_start", "stage": "clustering", "details": "Computing similarity matrix…"})

    attrs_list = [r.get("extracted_attrs", {}) for r in processed_records]

    def _cluster_sync():
        return cs.cluster_materials(material_ids, embeddings, descriptions=descriptions, attrs_list=attrs_list)

    cluster_result = await loop.run_in_executor(None, _cluster_sync)

    await send({"type": "progress", "stage": "clustering", "progress": 60, "details": f"Found {len(cluster_result)} clusters", "items": len(cluster_result)})

    # Build cluster objects (lighter work, can stay in main thread)
    clusters_data = []
    for cluster_ids in cluster_result:
        cluster_members = [processed_records[idx] for idx in cluster_ids]
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

    await send({"type": "stage_done", "stage": "clustering", "details": f"{len(clusters_data)} clusters finalized", "items": len(clusters_data)})

    # ── Stage 4: Standard code mapping ────────────────────────────────────
    await send({"type": "stage_start", "stage": "mapping", "details": "Mapping clusters to standard codes…"})

    from app.services.standard_catalog import standard_code_catalog

    for idx, cluster in enumerate(clusters_data):
        results = standard_code_catalog.find_closest(cluster["representative"])
        if results:
            cluster["standard_code"] = results[0]["code"]
            cluster["standard_label"] = results[0]["label"]
        else:
            cluster["standard_code"] = "00000000"
            cluster["standard_label"] = "Uncategorized"

        if (idx + 1) % max(len(clusters_data) // 5, 1) == 0:
            pct = int(((idx + 1) / len(clusters_data)) * 100)
            await send({
                "type": "progress",
                "stage": "mapping",
                "progress": pct,
                "details": f"Mapped {idx + 1}/{len(clusters_data)} clusters",
                "items": idx + 1,
            })

    await send({"type": "stage_done", "stage": "mapping", "details": "Code mapping complete", "items": len(clusters_data)})

    # ── Metrics ───────────────────────────────────────────────────────────
    gt_path = settings.DATA_DIR / "ground_truth.json"
    if gt_path.exists():
        gt = load_ground_truth_from_file(str(gt_path))
        quality_metrics = compute_cluster_metrics(
            [c["member_ids"] for c in clusters_data],
            gt,
        )
    else:
        quality_metrics = {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}

    conf_high = sum(1 for c in clusters_data if c["confidence"] == "high")
    conf_med = sum(1 for c in clusters_data if c["confidence"] == "medium")

    final_metrics = {
        "total_records": total,
        "cleaned_records": total,
        "embeddings_generated": total,
        "clusters_found": len(clusters_data),
        "codes_mapped": len(clusters_data),
        "confidence_high": conf_high,
        "confidence_medium": conf_med,
        **quality_metrics,
    }

    # ── Done ──────────────────────────────────────────────────────────────
    await send({
        "type": "done",
        "job_id": job_id,
        "total_records": total,
        "clusters": len(clusters_data),
        "metrics": final_metrics,
        "details": f"Harmonization complete — {len(clusters_data)} clusters from {total} records",
    })

    return {
        "records": processed_records,
        "clusters": clusters_data,
        "metrics": quality_metrics,
    }


# ---------------------------------------------------------------------------
# Legacy POST /process endpoint (kept for backwards compat)
# ---------------------------------------------------------------------------
@router.post("/process")
async def process_uploads(
    background_tasks: BackgroundTasks,
    record_ids: List[str],
):
    """Process uploaded records by ID (placeholder for real implementation)."""
    return JSONResponse(content={"message": "Processing started", "job_id": "demo_job_1"})

