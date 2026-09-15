"""Tests for ground truth metrics."""
import pytest
from app.services.metrics import compute_cluster_metrics


def test_perfect_clustering():
    """Clustering matches ground truth exactly."""
    clusters = [["m1", "m2", "m3"], ["m4", "m5"], ["m6"]]
    ground_truth = {
        "m1": "P1", "m2": "P1", "m3": "P1",
        "m4": "P2", "m5": "P2",
        "m6": "P3",
    }
    metrics = compute_cluster_metrics(clusters, ground_truth)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0


def test_split_cluster_lowers_recall():
    """A correct cluster is split into 2 -> recall < 1."""
    clusters = [["m1", "m2"], ["m3"], ["m4", "m5"], ["m6"]]
    ground_truth = {
        "m1": "P1", "m2": "P1", "m3": "P1",
        "m4": "P2", "m5": "P2",
        "m6": "P3",
    }
    metrics = compute_cluster_metrics(clusters, ground_truth)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] < 1.0


def test_merged_cluster_lowers_precision():
    """A wrong cluster merge -> precision < 1."""
    clusters = [["m1", "m2", "m3", "m4", "m5"], ["m6"]]
    ground_truth = {
        "m1": "P1", "m2": "P1", "m3": "P1",
        "m4": "P2", "m5": "P2",
        "m6": "P3",
    }
    metrics = compute_cluster_metrics(clusters, ground_truth)
    assert metrics["precision"] < 1.0
    assert metrics["recall"] == 1.0


def test_no_duplicates_in_ground_truth():
    """When GT has no duplicates, perfect cluster = singletons."""
    clusters = [["m1"], ["m2"], ["m3"]]
    ground_truth = {"m1": "P1", "m2": "P2", "m3": "P3"}
    metrics = compute_cluster_metrics(clusters, ground_truth)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0


def test_empty_input():
    metrics = compute_cluster_metrics([], {})
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
