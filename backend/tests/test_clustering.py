"""Tests for clustering/similarity module."""
import pytest
import numpy as np
from app.services.clustering import (
    composite_similarity,
    fuzzy_similarity,
    attribute_overlap,
)


class TestFuzzySimilarity:
    def test_identical_strings(self):
        assert fuzzy_similarity("stainless steel pipe", "stainless steel pipe") == 1.0

    def test_similar_strings(self):
        score = fuzzy_similarity("SS pipe 10mm", "Stainless Steel Pipe 10mm")
        assert score > 0.7

    def test_different_strings(self):
        score = fuzzy_similarity("SS pipe 10mm", "Hex Bolt M12")
        assert score < 0.3


class TestAttributeOverlap:
    def test_matching_attributes(self):
        attrs1 = {"material_type": "stainless_steel", "diameter": 10, "length": 5, "unit": "m"}
        attrs2 = {"material_type": "stainless_steel", "diameter": 10, "length": 5, "unit": "m"}
        score = attribute_overlap(attrs1, attrs2)
        assert score > 0.9

    def test_different_materials(self):
        attrs1 = {"material_type": "stainless_steel", "diameter": 10}
        attrs2 = {"material_type": "carbon_steel", "diameter": 10}
        score = attribute_overlap(attrs1, attrs2)
        assert score < 0.8  # not matching material

    def test_empty_attributes(self):
        assert attribute_overlap({}, {}) == 0.0


class TestCompositeSimilarity:
    def test_identical_descriptions(self):
        emb = np.array([0.5, 0.5, 0.5])
        attrs = {"material_type": "stainless_steel", "diameter": 10, "length": 5, "unit": "m"}
        result = composite_similarity(
            "SS pipe 10mm x 5m",
            "SS pipe 10mm x 5m",
            attrs, attrs,
            emb, emb,
        )
        assert result["composite"] > 0.9
        assert result["confidence"] == "high"

    def test_completely_different(self):
        emb1 = np.array([1.0, 0.0, 0.0])
        emb2 = np.array([0.0, 1.0, 0.0])
        attrs1 = {"material_type": "stainless_steel", "diameter": 10}
        attrs2 = {"material_type": "pvc", "diameter": 50}
        result = composite_similarity(
            "SS pipe 10mm",
            "PVC pipe 50mm",
            attrs1, attrs2,
            emb1, emb2,
        )
        assert result["composite"] < 0.5
        assert result["confidence"] == "low"

    def test_partial_match(self):
        emb = np.array([0.5, 0.5, 0.5])
        attrs1 = {"material_type": "stainless_steel", "diameter": 10, "length": 5, "unit": "m"}
        attrs2 = {"material_type": "stainless_steel", "diameter": 25, "length": 5, "unit": "m"}
        result = composite_similarity(
            "SS pipe 10mm x 5m",
            "SS pipe 25mm x 5m",
            attrs1, attrs2,
            emb, emb,
        )
        # Should be medium - material matches but diameter different
        assert 0.5 < result["composite"] < 0.95
