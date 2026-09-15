"""Verify preprocessing after regex fix."""
import sys
sys.path.insert(0, 'backend')

from app.services.preprocessing import preprocess_material, extract_attributes

tests = [
    {
        'desc': 'SS Pipe 10mm x 5m',
        'input': {'description': 'SS Pipe 10mm x 5m', 'unit': 'pc', 'material_group': 'Pipes', 'plant': 'Plant_01'},
        'expect_dia': 10.0,
        'expect_len': 5.0,
        'expect_mat': 'stainless_steel',
    },
    {
        'desc': 'stainless steel pipe 10mm dia 5 meter len',
        'input': {'description': 'stainless steel pipe 10mm dia 5 meter len', 'unit': 'm', 'material_group': 'Steel', 'plant': 'Plant_02'},
        'expect_dia': 10.0,
        'expect_len': 5.0,
        'expect_mat': 'stainless_steel',
    },
    {
        'desc': 'Copper Pipe 15mm x 6m',
        'input': {'description': 'Copper Pipe 15mm x 6m', 'unit': 'm', 'material_group': 'Pipes', 'plant': 'Plant_03'},
        'expect_dia': 15.0,
        'expect_len': 6.0,
        'expect_mat': 'copper',
    },
]

all_passed = True
for test in tests:
    result = preprocess_material(test['input'])
    attrs = result['extracted_attrs']
    dia = attrs.get('diameter')
    length = attrs.get('length')
    mat = attrs.get('material_type')
    desc = test['desc']
    print(f'Input: {desc}')
    print(f'  Material={mat}, Diameter={dia}, Length={length}')

    errors = []
    if test.get('expect_mat'):
        if mat != test['expect_mat']:
            errors.append(f"Material: expected {test['expect_mat']}, got {mat}")
    if test.get('expect_dia'):
        if dia != test['expect_dia']:
            errors.append(f"Diameter: expected {test['expect_dia']}, got {dia}")
    if test.get('expect_len'):
        if length != test['expect_len']:
            errors.append(f"Length: expected {test['expect_len']}, got {length}")

    if errors:
        print(f'  FAILED:')
        for err in errors:
            print(f'    - {err}')
        all_passed = False
    else:
        print(f'  PASS')
    print()

if all_passed:
    print('ALL TESTS PASSED!')
else:
    print('SOME TESTS FAILED!')
    sys.exit(1)
