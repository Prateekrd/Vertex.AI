"""Quick test of preprocessing module."""
import sys
sys.path.insert(0, 'app')

from app.services.preprocessing import (
    expand_abbreviations, extract_attributes, clean_description,
    normalize_unit, preprocess_material,
)

# Test 1: Abbreviation expansion
result = expand_abbreviations('SS Pipe 10mm x 5mtr')
print('Test 1 - Abbreviation expansion:')
print(f'  Input: SS Pipe 10mm x 5mtr')
print(f'  Output: {result}')
assert 'stainless steel' in result, f"Expected 'stainless steel' in result, got: {result}"
assert 'meter' in result, f"Expected 'meter' in result"
print('  PASS')

# Test 2: Unit normalization
assert normalize_unit('mm') == 'mm'
assert normalize_unit('MTR') == 'm'
assert normalize_unit('kilogram') == 'kg'
print('Test 2 - Unit normalization: PASS')

# Test 3: Attribute extraction
attrs = extract_attributes('SS pipe 10mm dia 5m length')
print('Test 3 - Attribute extraction:')
print(f'  Diameter: {attrs.diameter}')
print(f'  Length: {attrs.length}')
print(f'  Material type: {attrs.material_type}')
assert attrs.diameter == 10, f"Expected diameter 10, got {attrs.diameter}"
assert attrs.material_type == 'stainless_steel'
print('  PASS')

# Test 4: Full preprocessing
rec = {'description': 'SS Pipe 10mm x 5m', 'unit': 'pc', 'material_group': 'Pipes', 'plant': 'Plant_01'}
result = preprocess_material(rec)
print('Test 4 - Full pipeline:')
print(f'  Cleaned: {result["cleaned_description"]}')
assert 'stainless steel' in result['cleaned_description']
print('  PASS')

# Test 5: Edge case - grade extraction
rec2 = {'description': 'Stainless Steel 304 Plate 12mm thick', 'unit': 'kg', 'material_group': 'Steel', 'plant': 'Plant_02'}
result2 = preprocess_material(rec2)
print('Test 5 - Grade extraction:')
print(f'  Material type: {result2["extracted_attrs"]["material_type"]}')
print(f'  Thickness: {result2["extracted_attrs"]["thickness"]}')
print(f'  Grade: {result2["extracted_attrs"]["grade"]}')
assert result2['extracted_attrs']['material_type'] == 'stainless_steel'
print('  PASS')

print('\nAll preprocessing tests PASSED!')
