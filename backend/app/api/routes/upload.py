"""Upload endpoint: CSV/Excel ingestion."""
from __future__ import annotations

import asyncio
import csv
import json
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Generator

from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.config import settings
from app.dependencies import get_db_session
from app.schemas import UploadResponse, ProcessStatus

router = APIRouter()


def parse_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse CSV file into list of dicts."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize column names
            record = {
                "source_cpse_id": row.get("source_cpse_id") or row.get("cpse_id", "unknown"),
                "source_material_id": row.get("source_material_id") or row.get("material_id", str(uuid.uuid4())),
                "description": row.get("description", ""),
                "unit": row.get("unit", ""),
                "material_group": row.get("material_group", ""),
                "plant": row.get("plant", ""),
            }
            records.append(record)
    return records


async def save_upload_file(file: UploadFile, upload_id: str) -> Path:
    """Save uploaded file to disk."""
    upload_path = settings.UPLOAD_DIR / f"{upload_id}_{file.filename}"
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)
    return upload_path


@router.post("/", response_model=UploadResponse)
async def upload_materials(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a CSV/Excel file with raw material master data."""
    upload_id = str(uuid.uuid4())[:8]

    # Save file
    upload_path = await save_upload_file(file, upload_id)

    # Parse records
    records = parse_csv_file(upload_path)

    return UploadResponse(
        upload_id=upload_id,
        total_records=len(records),
        processed=0,
        message=f"Uploaded {len(records)} records from {file.filename}",
    )


@router.get("/samples")
def get_sample_datasets():
    """List available sample datasets."""
    data_dir = settings.DATA_DIR
    if data_dir.exists():
        samples = []
        for f in data_dir.glob("cpse_*_materials.csv"):
            samples.append({
                "id": f.stem,
                "file": f.name,
            })
        return {"samples": samples}
    return {"samples": [], "message": "Data directory empty"}


@router.post("/load-sample/{sample_id}")
def load_sample(sample_id: str):
    """Load a sample dataset."""
    sample_file = settings.DATA_DIR / f"{sample_id}_materials.csv"
    if not sample_file.exists():
        return JSONResponse(status_code=404, content={"error": "Sample not found"})

    records = parse_csv_file(sample_file)
    return {
        "sample_id": sample_id,
        "total_records": len(records),
        "message": f"Loaded {len(records)} records from sample",
        "first_record": records[0] if records else None,
    }