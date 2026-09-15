"""Ground truth metrics: precision, recall, F1 for cluster quality."""
from __future__ import annotations

from typing import Dict, List, Set, Tuple
from collections import defaultdict


def compute_cluster_metrics(
    clusters: List[List[str]],  # cluster_id -> material_ids
    ground_truth: Dict[str, str],  # material_id -> canonical_product_id
) -> Dict[str, float]:
    """
    Compute precision, recall, F1 for clustering vs ground truth.

    Precision: of all the materials we grouped together, how many should have been?
    Recall: of all materials that should have been grouped, did we get them?
    """
    # Build: ground truth equivalence classes
    gt_groups: Dict[str, Set[str]] = defaultdict(set)
    for mat_id, canon_id in ground_truth.items():
        gt_groups[canon_id].add(mat_id)

    # Build: predicted equivalence classes
    pred_groups: List[Set[str]] = [
        set(c) for c in clusters if len(c) > 1
    ]
    singleton_count = sum(1 for c in clusters if len(c) == 1)

    # Pairwise precision/recall
    # For each predicted cluster, count pairs that are in same GT group
    tp = 0   # pairs correctly predicted to be together
    fp = 0   # pairs predicted together but actually different
    fn = 0   # pairs should be together but predicted different

    pred_pairs = set()
    for pred_cluster in pred_groups:
        mat_list = list(pred_cluster)
        for i in range(len(mat_list)):
            for j in range(i + 1, len(mat_list)):
                pair = tuple(sorted([mat_list[i], mat_list[j]]))
                pred_pairs.add(pair)

    # Get all GT pairs
    gt_pairs = set()
    for canon_id, mat_set in gt_groups.items():
        if len(mat_set) < 2:
            continue
        mat_list = list(mat_set)
        for i in range(len(mat_list)):
            for j in range(i + 1, len(mat_list)):
                pair = tuple(sorted([mat_list[i], mat_list[j]]))
                gt_pairs.add(pair)

    # Compute counts
    tp = len(pred_pairs & gt_pairs)
    fp = len(pred_pairs - gt_pairs)
    fn = len(gt_pairs - pred_pairs)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "true_positive_pairs": tp,
        "false_positive_pairs": fp,
        "false_negative_pairs": fn,
        "n_clusters_predicted": len(pred_groups),
        "n_clusters_ground_truth": len([g for g in gt_groups.values() if len(g) > 1]),
        "n_singletons": singleton_count,
    }


def load_ground_truth_from_file(path: str) -> Dict[str, str]:
    """Load ground truth from JSON file, return material_id -> canonical_id mapping."""
    import json
    with open(path, "r", encoding="utf-8") as f:
        gt_list = json.load(f)

    # Each entry has cpse_id, raw_id, canonical_product_id
    return {
        f"{entry['cpse_id']}_{entry['raw_id']}": entry["canonical_product_id"]
        for entry in gt_list
    }