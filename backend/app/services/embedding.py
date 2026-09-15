"""Embedding generation + FAISS index for fast ANN search."""
from __future__ import annotations

import json
from typing import List, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingService:
    """Manages sentence-transformer model and FAISS index."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model: Optional[SentenceTransformer] = None
        self._index: Optional[faiss.Index] = None
        self._ids: List[str] = []  # maps index position -> material_id
        self._embeddings: Optional[np.ndarray] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        emb = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        if normalize:
            norms = np.linalg.norm(emb, axis=1, keepdims=True)
            norms[norms == 0] = 1
            emb = emb / norms
        return emb.astype(np.float32)

    def build_index(self, material_ids: List[str], embeddings: np.ndarray) -> None:
        """Build FAISS index from material embeddings."""
        if embeddings.shape[0] == 0:
            self._index = faiss.IndexFlatIP(embeddings.shape[1] if embeddings.ndim > 1 else 384)
            self._ids = []
            self._embeddings = np.zeros((0, 384), dtype=np.float32)
            return

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(embeddings)
        self._ids = material_ids
        self._embeddings = embeddings

    def add_materials(self, material_ids: List[str], embeddings: np.ndarray) -> None:
        """Incrementally add new materials to the index."""
        if self._index is None:
            self.build_index(material_ids, embeddings)
        else:
            self._index.add(embeddings)
            self._ids.extend(material_ids)
            if self._embeddings is not None:
                self._embeddings = np.vstack([self._embeddings, embeddings])

    def search(self, query_emb: np.ndarray, k: int = 10) -> Tuple[np.ndarray, List[str]]:
        """Search FAISS index for top-k nearest neighbors."""
        if self._index is None or self._index.ntotal == 0:
            return np.array([]), []

        scores, idxs = self._index.search(query_emb.reshape(1, -1), min(k, self._index.ntotal))
        neighbor_ids = [self._ids[i] for i in idxs[0] if i < len(self._ids)]
        return scores[0], neighbor_ids

    def get_embedding(self, material_id: str) -> Optional[np.ndarray]:
        """Get stored embedding for a material by ID."""
        if self._embeddings is not None:
            try:
                idx = self._ids.index(material_id)
                return self._embeddings[idx]
            except ValueError:
                return None
        return None

    def save_index(self, path: str) -> None:
        """Persist index and metadata to disk."""
        if self._index is not None:
            faiss.write_index(self._index, f"{path}.faiss")
            np.save(f"{path}_emb.npy", self._embeddings)
            with open(f"{path}_ids.json", "w") as f:
                json.dump(self._ids, f)

    def load_index(self, path: str) -> bool:
        """Load index from disk. Returns True on success."""
        try:
            self._index = faiss.read_index(f"{path}.faiss")
            self._embeddings = np.load(f"{path}_emb.npy")
            with open(f"{path}_ids.json", "r") as f:
                self._ids = json.load(f)
            return True
        except Exception:
            return False


# Global singleton
embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    return embedding_service