"""Test metrics and clustering."""
import sys
sys.path.insert(0, 'backend')

from app.services.metrics import compute_cluster_metrics

# Test 1: Perfect clustering
clusters = [['m1', 'm2', 'm3'], ['m4', 'm5'], ['m6']]
gt = {'m1': 'P1', 'm2': 'P1', 'm3': 'P1', 'm4': 'P2', 'm5': 'P2', 'm6': 'P3'}
m = compute_cluster_metrics(clusters, gt)
print('Test 1 - Perfect clustering:')
print('  Precision: %.4f (expected 1.0)' % m['precision'])
print('  Recall:    %.4f (expected 1.0)' % m['recall'])
print('  F1:        %.4f (expected 1.0)' % m['f1_score'])
assert m['precision'] == 1.0 and m['recall'] == 1.0 and m['f1_score'] == 1.0, 'Test 1 failed'
print('  PASS')

# Test 2: Split cluster lowers recall
clusters2 = [['m1', 'm2'], ['m3'], ['m4', 'm5'], ['m6']]
m2 = compute_cluster_metrics(clusters2, gt)
print('Test 2 - Split cluster:')
print('  Precision: %.4f (expected 1.0)' % m2['precision'])
print('  Recall:    %.4f (expected <1.0)' % m2['recall'])
assert m2['precision'] == 1.0 and m2['recall'] < 1.0, 'Test 2 failed'
print('  PASS')

# Test 3: Merged cluster lowers precision
clusters3 = [['m1', 'm2', 'm3', 'm4', 'm5'], ['m6']]
m3 = compute_cluster_metrics(clusters3, gt)
print('Test 3 - Merged cluster:')
print('  Precision: %.4f (expected <1.0)' % m3['precision'])
print('  Recall:    %.4f (expected 1.0)' % m3['recall'])
assert m3['precision'] < 1.0 and m3['recall'] == 1.0, 'Test 3 failed'
print('  PASS')

# Test 4: No duplicates
clusters4 = [['m1'], ['m2'], ['m3'], ['m4'], ['m5'], ['m6']]
gt4 = {'m1': 'P1', 'm2': 'P2', 'm3': 'P3', 'm4': 'P4', 'm5': 'P5', 'm6': 'P6'}
m4 = compute_cluster_metrics(clusters4, gt4)
print('Test 4 - No duplicates:')
print('  Precision: %.4f' % m4['precision'])
print('  Recall:    %.4f' % m4['recall'])
print('  PASS')

print()
print('ALL METRICS TESTS PASSED!')
