"""Review queue: fetch pending items, approve/reject/edit."""
from __future__ import annotations

import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# In-memory storage for demo (replace with DB in production)
_pending_reviews: List[Dict[str, Any]] = []
_completed_reviews: List[Dict[str, Any]] = []


class ReviewActionRequest(BaseModel):
    cluster_id: str
    action: str  # approve | reject | edit
    new_standard_code: Optional[str] = None
    notes: Optional[str] = None


@router.get("/queue")
def get_review_queue():
    """Get all pending review items."""
    return {
        "pending": _pending_reviews,
        "count": len(_pending_reviews),
    }


@router.get("/queue/{cluster_id}")
def get_review_item(cluster_id: str):
    """Get a specific review item."""
    for item in _pending_reviews:
        if item.get("cluster_id") == cluster_id:
            return item
    raise HTTPException(status_code=404, detail="Review item not found")


@router.post("/submit")
def submit_review(action: ReviewActionRequest):
    """Submit a review decision (approve/reject/edit)."""
    # Find the cluster
    cluster = None
    for item in _pending_reviews:
        if item.get("cluster_id") == action.cluster_id:
            cluster = item
            break

    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found in queue")

    # Record the decision
    decision = {
        "id": str(uuid.uuid4())[:8],
        "cluster_id": action.cluster_id,
        "action": action.action,
        "new_standard_code": action.new_standard_code,
        "notes": action.notes,
        "timestamp": datetime.utcnow().isoformat(),
        "members": cluster.get("members", []),
    }
    _completed_reviews.append(decision)

    # Remove from pending
    _pending_reviews.remove(cluster)

    return {
        "message": f"Review {action.action}d for cluster {action.cluster_id}",
        "decision_id": decision["id"],
    }


@router.get("/history")
def get_review_history():
    """Get all completed review decisions."""
    return {
        "history": _completed_reviews,
        "count": len(_completed_reviews),
    }


@router.post("/seed")
def seed_review_queue(items: List[Dict[str, Any]]):
    """Seed the review queue with items (used by processing pipeline)."""
    global _pending_reviews
    _pending_reviews = items
    return {"message": f"Seeded {len(items)} items"}
