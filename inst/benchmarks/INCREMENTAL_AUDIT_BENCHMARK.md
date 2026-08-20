# Incremental Audit Benchmark

This analysis separates generic classifier uncertainty from NicheTypeR-specific
conflict information. All trained audit models use leave-one-dataset-out
prediction: the held-out dataset is never used to fit audit-risk weights.

## Denominators

- Raw eligible model-call rows: 489,988
- Unique dataset-cell/spot units: 45,104
- Source datasets: 12
- Raw rows are not independent because the same cell or spot can appear under
  multiple annotation models. Unique-cell summaries are therefore the primary
  review-triage unit.

## Overall Results

| unit | score | n | wrong rate | AUROC | AUPRC | top 10% precision |
|---|---|---:|---:|---:|---:|---:|
| call | margin | 489,988 | 0.459 | 0.743 | 0.675 | 0.756 |
| call | one_minus_confidence | 489,988 | 0.459 | 0.731 | 0.662 | 0.716 |
| call | baseline_logo | 489,988 | 0.459 | 0.738 | 0.662 | 0.715 |
| call | baseline_plus_conflicts | 489,988 | 0.459 | 0.738 | 0.659 | 0.716 |
| call | nonmargin_conflict_flag | 489,988 | 0.459 | 0.500 | 0.459 | 0.453 |
| unique_cell | margin | 45,104 | 0.701 | 0.879 | 0.937 | 0.981 |
| unique_cell | one_minus_confidence | 45,104 | 0.701 | 0.803 | 0.888 | 0.943 |
| unique_cell | baseline_logo | 45,104 | 0.701 | 0.832 | 0.901 | 0.944 |
| unique_cell | baseline_plus_conflicts | 45,104 | 0.701 | 0.859 | 0.926 | 0.986 |
| unique_cell | nonmargin_conflict_flag | 45,104 | 0.701 | 0.492 | 0.698 | 0.892 |

## Dataset-Cluster Bootstrap Deltas

| unit | metric | comparison | delta | 95% CI | datasets |
|---|---|---|---:|---|---:|
| call | auroc | baseline_plus_conflicts - baseline_logo | -0.0014 | [-0.0027, 0.0000] | 12 |
| call | auroc | baseline_plus_conflicts - margin | -0.0015 | [-0.0073, 0.0040] | 12 |
| call | auprc | baseline_plus_conflicts - baseline_logo | -0.0103 | [-0.0153, -0.0059] | 12 |
| call | auprc | baseline_plus_conflicts - margin | -0.0014 | [-0.0084, 0.0052] | 12 |
| call | top10_precision | baseline_plus_conflicts - baseline_logo | -0.0138 | [-0.0210, -0.0069] | 12 |
| call | top10_precision | baseline_plus_conflicts - margin | 0.0031 | [-0.0089, 0.0154] | 12 |
| unique_cell | auroc | baseline_plus_conflicts - baseline_logo | 0.0293 | [0.0175, 0.0427] | 12 |
| unique_cell | auroc | baseline_plus_conflicts - margin | -0.0095 | [-0.0295, 0.0101] | 12 |
| unique_cell | auprc | baseline_plus_conflicts - baseline_logo | 0.0203 | [0.0108, 0.0306] | 12 |
| unique_cell | auprc | baseline_plus_conflicts - margin | -0.0032 | [-0.0115, 0.0041] | 12 |
| unique_cell | top10_precision | baseline_plus_conflicts - baseline_logo | 0.0163 | [0.0001, 0.0340] | 12 |
| unique_cell | top10_precision | baseline_plus_conflicts - margin | 0.0048 | [-0.0112, 0.0191] | 12 |

## Interpretation

The baseline margin score remains a generic uncertainty baseline and should
not be described as a NicheTypeR-specific contribution. The relevant
increment is the cross-dataset improvement from adding non-margin conflict
features to margin and confidence. If that delta is near zero or the
dataset-cluster confidence interval overlaps zero, the manuscript should
frame NicheTypeR's current empirical support as conservative triage and
calibration rather than as a validated multi-evidence error detector.

Available call tables do not contain separate numeric ligand-receptor,
pathway/program or negative-marker residual features, so this benchmark
cannot support independent five-evidence-layer claims. Those claims should
either be removed from the main empirical contribution or backed by new
layer-specific call tables.

## Compact Takeaway

- Call-level margin AUROC: 0.743
- Call-level augmented AUROC: 0.738
- Unique-cell margin AUROC: 0.879
- Unique-cell augmented AUROC: 0.859
