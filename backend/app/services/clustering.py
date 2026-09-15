"""Agglomerative clustering + composite similarity scoring."""
from __future__ import annotations

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from rapidfuzz import fuzz, process

from app.config import settings
from app.services.embedding import EmbeddingService


def fuzzy_similarity(s1: str, s2: str) -> float:
    """Token-set ratio similarity via RapidFuzz (range 0-100)."""
    return fuzz.token_set_ratio(s1.lower(), s2.lower()) / 100.0


def attribute_overlap(attrs1: Dict[str, Any], attrs2: Dict[str, Any]) -> float:
    """Overlap score on extracted structured attributes."""
    if not attrs1 or not attrs2:
        return 0.0

    score = 0.0
    count = 0

    # Material type must match
    if attrs1.get("material_type") and attrs2.get("material_type"):
        count += 1
        if attrs1["material_type"].lower() == attrs2["material_type"].lower():
            score += 1

    # Numeric attribute proximity (diameter, length, width, thickness)
    numeric_fields = ["diameter", "length", "width", "thickness"]
    for f in numeric_fields:
        v1, v2 = attrs1.get(f), attrs2.get(f)
        if v1 is not None and v2 is not None and v1 != 0 and v2 != 0:
            count += 1
            ratio = min(float(v1), float(v2)) / max(float(v1), float(v2))
            score += ratio

    # Unit match
    if attrs1.get("unit") and attrs2.get("unit"):
        count += 1
        if normalize_unit_str(attrs1["unit"]) == normalize_unit_str(attrs2["unit"]):
            score += 1

    return score / max(count, 1)


def normalize_unit_str(u: str) -> str:
    """Normalize unit string for comparison."""
    mapping = {
        "millimeter": "mm", "mm": "mm",
        "centimeter": "cm", "cm": "cm", "centimetre": "cm",
        "meter": "m", "metre": "m", "mtr": "m", "mt": "m",
        "foot": "ft", "in": "in", "inch": "in",
        "kg": "kg", "kilogram": "kg",
        "g": "g", "gram": "g",
        "l": "l", "liter": "l", "litre": "l",
    }
    return mapping.get(u.lower().strip(), u.lower().strip())


class ClusteringService:
    """Composite similarity + hierarchical clustering for duplicate detection."""

    WEIGHTS = {
        "embedding": 0.45,
        "fuzzy": 0.30,
        "attribute": 0.25,
    }

    def __init__(self, embedding_service: EmbeddingService = None):
        self.embedding = embedding_service or EmbeddingService()

    def composite_similarity(
        self,
        desc1: str,
        desc2: str,
        attrs1: Optional[Dict[str, Any]],
        attrs2: Optional[Dict[str, Any]],
        emb1: Optional[np.ndarray] = None,
        emb2: Optional[np.ndarray] = None,
    ) -> Dict[str, float]:
        """Compute composite similarity between two materials."""
        # Cosine similarity
        if emb1 is not None and emb2 is not None:
            cos_sim = float(np.dot(emb1, emb2))
        else:
            cos_sim = 0.0

        # Fuzzy similarity
        fuzzy = fuzzy_similarity(desc1, desc2)

        # Attribute overlap
        attr = attribute_overlap(attrs1 or {}, attrs2 or {})

        # Weighted blend
        composite = (
            self.WEIGHTS["embedding"] * cos_sim +
            self.WEIGHTS["fuzzy"] * fuzzy +
            self.WEIGHTS["attribute"] * attr
        )

        return {
            "cosine": cos_sim,
            "fuzzy": fuzzy,
            "attribute": attr,
            "composite": composite,
            "confidence": "high" if composite >= settings.HIGH_CONFIDENCE
                         else ("medium" if composite >= settings.MEDIUM_CONFIDENCE else "low"),
        }

    def find_duplicates(
        self,
        material_ids: List[str],
        descriptions: List[str],
        attrs_list: List[Dict[str, Any]],
        embeddings: np.ndarray,
        threshold: float = None,
    ) -> List[Tuple[str, str, float, str]]:
        """Return list of (id1, id2, score, confidence) duplicate pairs."""
        threshold = threshold or settings.CLUSTER_THRESHOLD
        n = len(material_ids)
        results: List[Tuple[str, str, float, str]] = []

        for i in range(n):
            for j in range(i + 1, n):
                sim = self.composite_similarity(
                    descriptions[i], descriptions[j],
                    attrs_list[i], attrs_list[j],
                    embeddings[i], embeddings[j],
                )
                if sim["composite"] >= threshold:
                    results.append((
                        material_ids[i], material_ids[j],
                        sim["composite"], sim["confidence"]
                    ))
        return results

    def cluster_materials(
        self,
        material_ids: List[str],
        embeddings: np.ndarray,
        threshold: float = None,
        descriptions: List[str] = None,
        attrs_list: List[Dict[str, Any]] = None,
    ) -> List[List[int]]:
        """Cluster materials using agglomerative clustering with composite similarity."""
        threshold = threshold or settings.CLUSTER_THRESHOLD
        n = len(material_ids)
        if n < 2:
            return [[0]] if material_ids else []

        # Cap to keep pairwise distance computation feasible
        n_samples = min(n, 500)
        if n > 500:
            idx = np.random.choice(n, n_samples, replace=False)
            embeddings_sub = embeddings[idx]
            if descriptions is not None:
                descriptions_sub = [descriptions[i] for i in idx]
            if attrs_list is not None:
                attrs_sub = [attrs_list[i] for i in idx]
        else:
            embeddings_sub = embeddings
            descriptions_sub = descriptions
            attrs_sub = attrs_list

        # Build composite similarity matrix
        sim_matrix = np.zeros((n_samples, n_samples), dtype=np.float32)
        for i in range(n_samples):
            sim_matrix[i, i] = 1.0
            for j in range(i + 1, n_samples):
                sim = self.composite_similarity(
                    descriptions_sub[i] if descriptions_sub else "",
                    descriptions_sub[j] if descriptions_sub else "",
                    attrs_sub[i] if attrs_sub else None,
                    attrs_sub[j] if attrs_sub else None,
                    embeddings_sub[i],
                    embeddings_sub[j],
                )
                sim_matrix[i, j] = sim["composite"]
                sim_matrix[j, i] = sim["composite"]

        dist_matrix = 1 - np.clip(sim_matrix, 0, 1)
        np.fill_diagonal(dist_matrix, 0)

        cluster = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1 - threshold,
            metric="precomputed",
            linkage="average",
        )
        labels = cluster.fit_predict(dist_matrix)

        # Group indices by label
        clusters: Dict[int, List[int]] = {}
        for idx, label in enumerate(labels):
            clusters.setdefault(label, []).append(idx)

        # Map back to original indices if subsampled
        if n > 500:
            original_indices = [int(idx) for idx in idx]
            result = []
            for label_indices in clusters.values():
                result.append([original_indices[i] for i in label_indices])
            return result

        return list(clusters.values())

    def score_cluster(
        self,
        material_ids: List[str],
        descriptions: List[str],
        attrs_list: List[Dict[str, Any]],
        embeddings: np.ndarray,
    ) -> float:
        """Average pairwise similarity within a cluster."""
        if len(material_ids) < 2:
            return 1.0
        scores = []
        for i in range(len(material_ids)):
            for j in range(i + 1, len(material_ids)):
                sim = self.composite_similarity(
                    descriptions[i], descriptions[j],
                    attrs_list[i], attrs_list[j],
                    embeddings[i], embeddings[j],
                )
                scores.append(sim["composite"])
        return float(np.mean(scores)) if scores else 0.0


clustering_service = ClusteringService()


def get_clustering_service() -> ClusteringService:
    return clustering_service