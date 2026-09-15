"""Standard codes endpoint: browse and search UNSPSC-style catalog."""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.standard_catalog import STANDARD_CODES, standard_code_catalog

router = APIRouter()


@router.get("/")
def list_codes(
    category: Optional[str] = Query(None),
    limit: int = 200,
    offset: int = 0,
):
    """List standard codes, optionally filtered by category."""
    codes = STANDARD_CODES
    if category:
        codes = [c for c in codes if category.lower() in c["label"].lower() or category.lower() in c.get("description", "").lower()]

    return {
        "codes": codes[offset:offset + limit],
        "total": len(codes),
    }


@router.get("/{code}")
def get_code(code: str):
    """Get a specific standard code by code value."""
    result = standard_code_catalog.get_by_code(code)
    if not result:
        raise HTTPException(status_code=404, detail=f"Code {code} not found")
    return result


@router.post("/match")
def match_description(description: str):
    """Find the closest standard codes for a description."""
    results = standard_code_catalog.find_closest(description, top_k=5)
    return {"description": description, "matches": results}
