# Cubee parameter tuning summary

## Method

- Board size: `4`
- Training checkpoints: `[10000, 25000, 50000, 100000, 200000]`
- Evaluation games per checkpoint: `2000`
- Seeds: `[1, 2, 3]`
- Epsilon decay coefficient: `0.999985`
- Minimum epsilon: `0.05`
- Reference Q-table: `C:\Users\bouck\OneDrive - Haute Ecole de Namur-Liege-Luxembourg\Documents\CoursHenallux\ProjetConceptionIA\GitHub\ProjetIAJohnHugo\games\cubee\cubee_reference_4x4_qtable.json`

Each alpha/gamma pair is trained once per seed and evaluated at several checkpoints.
The main metric is the learning score, which averages win rate over all checkpoints.
This makes alpha easier to compare because alpha mainly affects learning speed.

## Best result

| Metric | Value |
|---|---:|
| Alpha | 0.4 |
| Gamma | 0.8 |
| Learning score | 0.4661 |
| Learning score margin | 0.9725 |
| Final win rate | 0.5037 |
| Final loss rate | 0.0000 |
| Final draw rate | 0.4963 |
| Final score margin | 1.0073 |

## All parameter combinations

| Rank | Alpha | Gamma | Learning score | Final win | Final loss | Final draw | Final margin | Final std |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.4 | 0.8 | 0.4661 | 0.5037 | 0.0000 | 0.4963 | 1.0073 | 0.0120 |
| 2 | 0.2 | 0.8 | 0.3962 | 0.5037 | 0.0000 | 0.4963 | 1.0073 | 0.0120 |
| 3 | 0.1 | 0.8 | 0.3348 | 0.5037 | 0.0000 | 0.4963 | 1.0073 | 0.0120 |
| 4 | 0.05 | 0.8 | 0.2840 | 0.5042 | 0.0000 | 0.4958 | 1.0083 | 0.0116 |
| 5 | 0.2 | 0.6 | 0.1619 | 0.2102 | 0.5028 | 0.2870 | -1.1640 | 0.0088 |
| 6 | 0.1 | 0.6 | 0.1614 | 0.1968 | 0.5045 | 0.2987 | -1.1650 | 0.0160 |
| 7 | 0.2 | 0.4 | 0.1611 | 0.1912 | 0.5015 | 0.3073 | -1.0860 | 0.0093 |
| 8 | 0.05 | 0.4 | 0.1601 | 0.1912 | 0.5015 | 0.3073 | -1.0860 | 0.0093 |
| 9 | 0.4 | 0.4 | 0.1557 | 0.1873 | 0.5085 | 0.3042 | -1.1763 | 0.0034 |
| 10 | 0.05 | 0.6 | 0.1545 | 0.2055 | 0.4953 | 0.2992 | -1.0977 | 0.0247 |
| 11 | 0.4 | 0.6 | 0.1530 | 0.2008 | 0.5055 | 0.2937 | -1.1867 | 0.0070 |
| 12 | 0.1 | 0.2 | 0.1480 | 0.1912 | 0.5015 | 0.3073 | -1.0860 | 0.0093 |
| 13 | 0.05 | 0.2 | 0.1478 | 0.1912 | 0.5015 | 0.3073 | -1.0860 | 0.0093 |
| 14 | 0.1 | 0.4 | 0.1466 | 0.1963 | 0.5038 | 0.2998 | -1.0910 | 0.0069 |
| 15 | 0.2 | 0.2 | 0.1421 | 0.1912 | 0.5015 | 0.3073 | -1.0860 | 0.0093 |
| 16 | 0.4 | 0.2 | 0.1366 | 0.1458 | 0.5030 | 0.3512 | -1.3567 | 0.0896 |
