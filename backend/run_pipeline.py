"""End-to-end pipeline runner — generates synthetic data, processes it, and prints metrics.

Run this before starting the demo to:
1. Generate the 3 synthetic CPSE datasets + ground truth
2. Process them through the full pipeline
3. Compute and print precision/recall against ground truth
4. Seed the review queue

Usage: python -m app.run_pipeline
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

# Initialize services (do this after setting up env)
from app.config import settings
from app.synthetic_data import save_datasets_to_disk, PRODUCTS, generate_all_cpses
from app.services.preprocessing import preprocess_material
from app.services.embedding import get_embedding_service
from app.services.clustering import get_clustering_service
from app.services.metrics import compute_cluster_metrics, load_ground_truth_from_file
from app.services.standard_catalog import standard_code_catalog


def main():
    print("=" * 70)
    print("SIH 26099 — Material Harmonization Pipeline")
    print("=" * 70)

    # Step 1: Generate synthetic data
    print("\n[1/5] Generating synthetic CPSE datasets...")
    info = save_datasets_to_disk()
    print(f"  ✓ Generated: {info['total_records']} total records")
    print(f"  ✓ CSV files: {[Path(f).name for f in info['csv_files']]}")
    print(f"  ✓ Ground truth: {Path(info['ground_truth_file']).name}")

    # Step 2: Load data
    print("\n[2/5] Loading datasets...")
    all_records = []
    for cpse_id in ["cpse_a", "cpse_b", "cpse_c"]:
        csv_path = settings.DATA_DIR / f"{cpse_id}_materials.csv"
        with open(csv_path, "r", encoding="utf-8") as f:
            import csv as csvmod
            reader = csvmod.DictReader(f)
            for row in reader:
                row["full_id"] = f"{row['source_cpse_id']}_{row['source_material_id']}"
                all_records.append(row)
    print(f"  ✓ Loaded {len(all_records)} raw records")

    # Step 3: Preprocess
    print("\n[3/5] Preprocessing records...")
    processed = []
    for rec in all_records:
        p = preprocess_material(rec)
        p["full_id"] = rec["full_id"]
        p["source_cpse_id"] = rec["source_cpse_id"]
        p["source_material_id"] = rec["source_material_id"]
        processed.append(p)
    print(f"  ✓ Preprocessed {len(processed)} records")
    sample = processed[0]
    print(f"  ✓ Sample: '{sample['cleaned_description']}'")
    if sample.get("extracted_attrs"):
        attrs = sample["extracted_attrs"]
        print(f"    material_type={attrs.get('material_type')}, diameter={attrs.get('diameter')}")

    # Step 4: Embed & cluster
    print("\n[4/5] Generating embeddings and clustering...")
    es = get_embedding_service()
    cs = get_clustering_service()

    descriptions = [p["cleaned_description"] for p in processed]
    embeddings = es.encode(descriptions)
    print(f"  ✓ Generated {embeddings.shape} embeddings")

    material_ids = [p["full_id"] for p in processed]
    attrs_list = [p.get("extracted_attrs", {}) for p in processed]

    clusters = cs.cluster_materials(material_ids, embeddings, descriptions=descriptions, attrs_list=attrs_list)
    n_singletons = sum(1 for c in clusters if len(c) == 1)
    n_multi = sum(1 for c in clusters if len(c) > 1)
    print(f"  ✓ Found {n_multi} duplicate clusters, {n_singletons} singletons")

    # Step 5: Map to standard codes + compute metrics
    print("\n[5/5] Mapping to standard codes + computing metrics...")
    clusters_with_codes = []
    for cluster_indices in clusters:
        if len(cluster_indices) < 2:
            continue
        member_records = [processed[i] for i in cluster_indices]
        # Average embedding
        avg_emb = np.mean([embeddings[i] for i in cluster_indices], axis=0)
        # Find standard code
        matches = standard_code_catalog.find_closest(
            member_records[0]["cleaned_description"],
            cluster_embedding=avg_emb,
            top_k=1,
        )
        code = matches[0]["code"] if matches else "00000000"
        label = matches[0]["label"] if matches else "Uncategorized"

        clusters_with_codes.append({
            "member_ids": [material_ids[i] for i in cluster_indices],
            "representative": member_records[0]["cleaned_description"],
            "standard_code": code,
            "standard_label": label,
            "members": member_records,
        })

    # Compute metrics against ground truth
    gt = load_ground_truth_from_file(str(settings.DATA_DIR / "ground_truth.json"))
    gt_clusters = list(set(gt.values()))
    metrics = compute_cluster_metrics(
        [c["member_ids"] for c in clusters_with_codes],
        gt,
    )

    print(f"\n{'=' * 70}")
    print("PIPELINE RESULTS")
    print(f"{'=' * 70}")
    print(f"  Total raw records:        {len(all_records):,}")
    print(f"  Total unique products:    {len(gt_clusters):,}")
    print(f"  Duplicate clusters found: {len(clusters_with_codes):,}")
    print()
    print(f"  PRECISION:                {metrics['precision'] * 100:.1f}%")
    print(f"  RECALL:                   {metrics['recall'] * 100:.1f}%")
    print(f"  F1 SCORE:                 {metrics['f1_score'] * 100:.1f}%")
    print()
    print(f"  True positive pairs:      {metrics['true_positive_pairs']}")
    print(f"  False positive pairs:     {metrics['false_positive_pairs']}")
    print(f"  False negative pairs:     {metrics['false_negative_pairs']}")
    print(f"{'=' * 70}")

    # Save metrics for the dashboard
    metrics_path = settings.DATA_DIR / "last_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  ✓ Metrics saved to: {metrics_path}")

    # Save clusters for the review queue
    clusters_path = settings.DATA_DIR / "clusters.json"
    with open(clusters_path, "w") as f:
        # Convert numpy types to python types for JSON
        safe_clusters = []
        for c in clusters_with_codes[:30]:  # top 30 for review
            safe_clusters.append({
                "cluster_id": f"cluster_{c['member_ids'][0]}",
                "representative": c["representative"],
                "member_ids": c["member_ids"],
                "standard_code": c["standard_code"],
                "standard_label": c["standard_label"],
                "members": [
                    {
                        "id": m["full_id"],
                        "cleaned_description": m["cleaned_description"],
                        "extracted_attrs": m.get("extracted_attrs", {}),
                        "source_cpse_id": m["source_cpse_id"],
                    }
                    for m in c["members"]
                ],
            })
        json.dump(safe_clusters, f, indent=2, default=str)
    print(f"  ✓ Clusters saved to: {clusters_path}")
    print()
    print("Done! Now start the API server:")
    print("  $ uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
