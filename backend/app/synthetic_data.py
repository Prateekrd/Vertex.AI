"""Generate 3 synthetic CPSE datasets with overlapping materials + ground truth."""
from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from faker import Faker
import re
import string
import numpy as np
from app.config import settings

random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)


# ---------------------------------------------------------------------------
# Base products with attributes
# ---------------------------------------------------------------------------
@dataclass
class ProductSpec:
    canonical_id: str          # e.g., "M_001"
    name: str
    material_type: str
    diameter: float = 0.0      # mm
    length: float = 0.0         # m
    width: float = 0.0          # mm
    thickness: float = 0.0      # mm
    grade: str = ""
    standard_code: str = ""
    unit: str = "pc"
    category: str = ""


PRODUCTS = [
    # Steel & Metal Stock
    ProductSpec("M_001", "Stainless Steel Pipe 10mm x 5m", "stainless_steel", 10, 5, grade="SS304", standard_code="10101503", unit="m", category="Steel"),
    ProductSpec("M_002", "Stainless Steel Pipe 25mm x 6m", "stainless_steel", 25, 6, grade="SS304", standard_code="10101503", unit="m", category="Steel"),
    ProductSpec("M_003", "Carbon Steel Plate 12mm", "carbon_steel", thickness=12, standard_code="10101501", unit="kg", category="Steel"),
    ProductSpec("M_004", "Aluminum Sheet 2mm x 1m x 2m", "aluminum", width=2000, thickness=2, standard_code="10152001", unit="kg", category="Metals"),
    ProductSpec("M_005", "Copper Pipe 15mm x 6m", "copper", 15, 6, standard_code="15151504", unit="m", category="Metals"),

    # Fasteners
    ProductSpec("F_001", "Hex Bolt M10x50 Grade 8.8", "carbon_steel", 10, 0.05, grade="8.8", standard_code="12101501", unit="pc", category="Fasteners"),
    ProductSpec("F_002", "Hex Bolt M12x60 Grade 10.9", "carbon_steel", 12, 0.06, grade="10.9", standard_code="12101501", unit="pc", category="Fasteners"),
    ProductSpec("F_003", "Hex Nut M10", "carbon_steel", 10, 0, grade="8", standard_code="12101503", unit="pc", category="Fasteners"),
    ProductSpec("F_004", "Spring Washer M10", "carbon_steel", 10, 0, standard_code="12101504", unit="pc", category="Fasteners"),

    # Electrical
    ProductSpec("E_001", "Copper Cable 2.5mm2 3-core", "copper", width=2.5, standard_code="11101502", unit="m", category="Electrical"),
    ProductSpec("E_002", "MCB 32A 3-pole C-curve", "stainless_steel", 32, 0, standard_code="11151502", unit="pc", category="Electrical"),

    # Safety
    ProductSpec("S_001", "Safety Helmet White EN397", "stainless_steel", standard_code="16101501", unit="pc", category="Safety"),
    ProductSpec("S_002", "Safety Gloves Cut-resistant EN388", "nylon", standard_code="16101503", unit="pc", category="Safety"),

    # Mechanical
    ProductSpec("ME_001", "Ball Bearing 6205 25x52x15", "stainless_steel", 25, 0, standard_code="12151501", unit="pc", category="Mechanical"),
    ProductSpec("ME_002", "O-Ring NBR 50mm ID", "rubber", 50, 0, standard_code="14151502", unit="pc", category="Mechanical"),

    # Chemicals
    ProductSpec("C_001", "Lubricating Oil ISO VG 68 20L", "stainless_steel", standard_code="17101501", unit="l", category="Chemicals"),
    ProductSpec("C_002", "Threadlocker Blue 50ml", "stainless_steel", standard_code="17201503", unit="pc", category="Chemicals"),
]


# ---------------------------------------------------------------------------
# Description variants (simulating different CPSE naming styles)
# ---------------------------------------------------------------------------
VARIANT_TEMPLATES = {
    "verbose": "{name}",
    "abbreviated": lambda p: _abbreviate_name(p.name),
    "compact": lambda p: _compact_name(p.name),
    "typo": lambda p: _typo_name(p.name),
    "reversed": lambda p: _reverse_name(p.name),
}


def _abbreviate_name(name: str) -> str:
    """Replace terms with abbreviations."""
    replacements = {
        "Stainless Steel": "SS",
        "Carbon Steel": "CS",
        "Aluminum": "AL",
        "Copper": "CU",
        "Brass": "BR",
        "Stainless": "SS",
        "Millimeter": "mm",
        "Diameter": "DIA",
        "Meter": "MTR",
        "Piece": "pc",
        "Quantity": "QTY",
        "Length": "LEN",
        "Grade": "Gr",
        "Grade 8.8": "8.8",
        "Grade 10.9": "10.9",
        "Schedule": "Sch",
        "Class": "Cl",
        "Number": "No",
        "Standard": "Std",
        "Material": "Mat",
        "Sheets": "Sh",
        "Plates": "Pl",
        "Pipes": "Pipe",
        "Bolts": "Bolt",
        "Nuts": "Nut",
        "Washers": "Wsh",
        "Bars": "Bar",
        "Rods": "Rod",
        "Cables": "Cable",
    }
    out = name
    for k, v in replacements.items():
        out = out.replace(k, v)
        out = out.replace(k.lower(), v)
    return out


def _compact_name(name: str) -> str:
    """Compact name: replace spaces with hyphens, remove connectors."""
    out = _abbreviate_name(name)
    out = out.replace(" ", "-")
    out = out.replace(",", "")
    return out


def _typo_name(name: str) -> str:
    """Introduce a small typo."""
    out = list(name)
    if len(out) > 5:
        # Swap two adjacent characters
        idx = random.randint(2, len(out) - 2)
        out[idx], out[idx + 1] = out[idx + 1], out[idx]
    return "".join(out)


def _reverse_name(name: str) -> str:
    """Reverse word order in part of the name."""
    words = name.split()
    if len(words) >= 3:
        # Swap last two words
        words[-1], words[-2] = words[-2], words[-1]
    return " ".join(words)


def _drop_units(name: str) -> str:
    """Drop unit tokens for one of the variants."""
    return re.sub(r"\b\d+(?:\.\d+)?\s*(mm|cm|m|kg|l|pc|inch)\b", "", name).strip()


VARIANT_LABELS = ["verbose", "abbreviated", "compact"]


def generate_description(product: ProductSpec, style: str) -> str:
    """Generate a description in the given style.

    Only uses 3 styles that represent realistic cross-CPSE variation:
    - verbose: full canonical name (what one CPSE uses)
    - abbreviated: short form (what another CPSE uses)
    - compact: hyphenated form (what a third CPSE uses)
    """
    if style == "verbose":
        return product.name
    elif style == "abbreviated":
        return _abbreviate_name(product.name)
    elif style == "compact":
        return _compact_name(product.name)
    return product.name


def build_dataset(
    cpse_id: str,
    n_records: int = 50,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Build a CPSE dataset.

    Design: Each CPSE has ~50 records drawn from 10 well-distinguished products.
    Each product appears 4-6 times in each CPSE (intra-CPSE duplicates).
    The same products appear in all 3 CPSEs (cross-CPSE duplicates).
    The pipeline must detect both intra-CPSE and cross-CPSE duplicates.

    Returns:
        (records, ground_truth)
        ground_truth: list of {cpse_id, raw_id, canonical_product_id}
    """
    records = []
    ground_truth = []
    next_id = 1

    # Select 10 products for this dataset (use all 10)
    selected_products = PRODUCTS[:10]  # First 10 products
    n = len(selected_products)  # = 10

    # Repeat each product ~5 times to create intra-CPSE duplicates
    repeats_per_product = n_records // n  # ~5
    for prod in selected_products:
        for _ in range(repeats_per_product):
            style = random.choice(VARIANT_LABELS)
            records.append({
                "source_cpse_id": cpse_id,
                "source_material_id": f"MAT{cpse_id.upper()}{next_id:05d}",
                "description": generate_description(prod, style),
                "unit": prod.unit,
                "material_group": prod.category,
                "plant": f"Plant_{cpse_id}_{random.randint(1, 3):02d}",
            })
            ground_truth.append({
                "cpse_id": cpse_id,
                "raw_id": records[-1]["source_material_id"],
                "canonical_product_id": prod.canonical_id,
                "standard_code": prod.standard_code,
                "category": prod.category,
            })
            next_id += 1

    return records, ground_truth


def generate_all_cpses() -> Dict[str, Any]:
    """Generate 3 CPSE datasets with overlapping product sets."""
    cpse_a_records, gt_a = build_dataset("cpse_a", 50)
    cpse_b_records, gt_b = build_dataset("cpse_b", 50)
    cpse_c_records, gt_c = build_dataset("cpse_c", 50)

    # Combined ground truth
    ground_truth = gt_a + gt_b + gt_c

    return {
        "cpse_a": cpse_a_records,
        "cpse_b": cpse_b_records,
        "cpse_c": cpse_c_records,
        "ground_truth": ground_truth,
    }


def save_datasets_to_disk(output_dir: Path = None):
    """Save synthetic datasets as CSV files + ground_truth.json."""
    if output_dir is None:
        output_dir = settings.DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    data = generate_all_cpses()

    for cpse_id in ["cpse_a", "cpse_b", "cpse_c"]:
        csv_path = output_dir / f"{cpse_id}_materials.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "source_cpse_id", "source_material_id", "description",
                "unit", "material_group", "plant"
            ])
            writer.writeheader()
            writer.writerows(data[cpse_id])

    gt_path = output_dir / "ground_truth.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(data["ground_truth"], f, indent=2)

    return {
        "csv_files": [str(p) for p in output_dir.glob("cpse_*_materials.csv")],
        "ground_truth_file": str(gt_path),
        "total_records": sum(len(data[k]) for k in ["cpse_a", "cpse_b", "cpse_c"]),
    }


if __name__ == "__main__":
    info = save_datasets_to_disk()
    print(f"Generated: {info}")
