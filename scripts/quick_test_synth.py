"""Quick standalone test for synthetic data generation (no ML imports)."""
import sys
import os
import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProductSpec:
    canonical_id: str
    name: str
    material_type: str
    diameter: float = 0.0
    length: float = 0.0
    width: float = 0.0
    thickness: float = 0.0
    grade: str = ''
    standard_code: str = ''
    unit: str = 'pc'
    category: str = ''


PRODUCTS = [
    ProductSpec('M_001', 'Stainless Steel Pipe 10mm x 5m', 'stainless_steel', 10, 5, standard_code='10101503', unit='m', category='Steel'),
    ProductSpec('M_002', 'Stainless Steel Pipe 25mm x 6m', 'stainless_steel', 25, 6, standard_code='10101503', unit='m', category='Steel'),
    ProductSpec('M_003', 'Carbon Steel Plate 12mm', 'carbon_steel', thickness=12, standard_code='10101501', unit='kg', category='Steel'),
    ProductSpec('F_001', 'Hex Bolt M10x50 Grade 8.8', 'carbon_steel', 10, 0.05, grade='8.8', standard_code='12101501', unit='pc', category='Fasteners'),
    ProductSpec('F_002', 'Hex Bolt M12x60 Grade 10.9', 'carbon_steel', 12, 0.06, grade='10.9', standard_code='12101501', unit='pc', category='Fasteners'),
    ProductSpec('F_003', 'Hex Nut M10', 'carbon_steel', 10, 0, grade='8', standard_code='12101503', unit='pc', category='Fasteners'),
    ProductSpec('F_004', 'Spring Washer M10', 'carbon_steel', 10, 0, standard_code='12101504', unit='pc', category='Fasteners'),
    ProductSpec('E_001', 'Copper Cable 2.5mm2 3-core', 'copper', width=2.5, standard_code='11101502', unit='m', category='Electrical'),
    ProductSpec('E_002', 'MCB 32A 3-pole C-curve', 'stainless_steel', 32, 0, standard_code='11151502', unit='pc', category='Electrical'),
    ProductSpec('S_001', 'Safety Helmet White EN397', 'stainless_steel', standard_code='16101501', unit='pc', category='Safety'),
    ProductSpec('S_002', 'Safety Gloves Cut-resistant EN388', 'nylon', standard_code='16101503', unit='pc', category='Safety'),
    ProductSpec('ME_001', 'Ball Bearing 6205 25x52x15', 'stainless_steel', 25, 0, standard_code='12151501', unit='pc', category='Mechanical'),
    ProductSpec('ME_002', 'O-Ring NBR 50mm ID', 'rubber', 50, 0, standard_code='14151502', unit='pc', category='Mechanical'),
    ProductSpec('C_001', 'Lubricating Oil ISO VG 68 (20L)', 'stainless_steel', standard_code='17101501', unit='l', category='Chemicals'),
    ProductSpec('C_002', 'Threadlocker Blue 50ml', 'stainless_steel', standard_code='17201503', unit='pc', category='Chemicals'),
]


def abbreviate_name(name):
    replacements = {
        'Stainless Steel': 'SS', 'Carbon Steel': 'CS',
        'Millimeter': 'mm', 'Meter': 'MTR', 'Diameter': 'DIA',
        'Grade': 'Gr', 'Length': 'LEN', 'Quantity': 'QTY',
    }
    out = name
    for k, v in replacements.items():
        out = out.replace(k, v)
        out = out.replace(k.lower(), v)
    return out


def generate_description(product, style):
    if style == 'verbose':
        return product.name
    elif style == 'abbreviated':
        return abbreviate_name(product.name)
    elif style == 'compact':
        return abbreviate_name(product.name).replace(' ', '-')
    elif style == 'reversed':
        words = product.name.split()
        if len(words) >= 3:
            words[-1], words[-2] = words[-2], words[-1]
        return ' '.join(words)
    return product.name


VARIANT_LABELS = ['verbose', 'abbreviated', 'compact', 'reversed']


def build_dataset(cpse_id, n_records=400, dup_frac=0.25):
    records = []
    ground_truth = []
    next_id = 1
    n_unique = max(1, int(n_records * (1 - dup_frac) / 1.5))
    unique_products = random.sample(PRODUCTS, k=min(n_unique, len(PRODUCTS)))
    for prod in unique_products:
        style = random.choice(VARIANT_LABELS)
        desc = generate_description(prod, style)
        records.append({
            'source_cpse_id': cpse_id,
            'source_material_id': f'MAT{cpse_id.upper()}{next_id:05d}',
            'description': desc,
            'unit': prod.unit,
            'material_group': prod.category,
            'plant': f'Plant_{cpse_id}_{random.randint(1, 3):02d}',
        })
        ground_truth.append({
            'cpse_id': cpse_id,
            'raw_id': records[-1]['source_material_id'],
            'canonical_product_id': prod.canonical_id,
            'standard_code': prod.standard_code,
            'category': prod.category,
        })
        next_id += 1
    n_dup = int(n_records * dup_frac)
    duplicate_pool = random.choices(PRODUCTS, k=n_dup)
    for prod in duplicate_pool:
        style = random.choice(VARIANT_LABELS)
        desc = generate_description(prod, style)
        records.append({
            'source_cpse_id': cpse_id,
            'source_material_id': f'MAT{cpse_id.upper()}{next_id:05d}',
            'description': desc,
            'unit': prod.unit,
            'material_group': prod.category,
            'plant': f'Plant_{cpse_id}_{random.randint(1, 3):02d}',
        })
        ground_truth.append({
            'cpse_id': cpse_id,
            'raw_id': records[-1]['source_material_id'],
            'canonical_product_id': prod.canonical_id,
            'standard_code': prod.standard_code,
            'category': prod.category,
        })
        next_id += 1
    return records, ground_truth


if __name__ == '__main__':
    random.seed(42)
    data_dir = Path('E:/Projects/SIH 26/data')
    data_dir.mkdir(exist_ok=True)

    all_gt = []
    for cpse_id in ['cpse_a', 'cpse_b', 'cpse_c']:
        records, gt = build_dataset(cpse_id, 400)
        csv_path = data_dir / f'{cpse_id}_materials.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['source_cpse_id', 'source_material_id', 'description', 'unit', 'material_group', 'plant'])
            writer.writeheader()
            writer.writerows(records)
        all_gt.extend(gt)
        first = records[0]['description']
        last = records[-1]['description']
        print(f'Written {len(records)} records to {csv_path.name}')
        print(f'  Sample first:  {first}')
        print(f'  Sample last:   {last}')

    gt_path = data_dir / 'ground_truth.json'
    with open(gt_path, 'w', encoding='utf-8') as f:
        json.dump(all_gt, f, indent=2)
    print(f'Written {len(all_gt)} ground truth entries')
    print('SUCCESS: Synthetic data generated!')
