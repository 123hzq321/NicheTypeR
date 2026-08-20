# External Method Audit Validity

This report asks whether NicheTypeR-style margin risk remains useful when
candidate labels come from external reference mappers rather than only
marker/context models.

## Summary

| group | calls | wrong rate | AUROC | AUPRC |
|---|---:|---:|---:|---:|
| all_external_methods | 162,992 | 0.445 | 0.735 | 0.685 |
| celltypist_style_logistic | 41,348 | 0.337 | 0.735 | 0.600 |
| scmap_style_knn | 41,348 | 0.482 | 0.795 | 0.761 |
| seurat_label_transfer | 38,948 | 0.390 | 0.823 | 0.689 |
| singler_style_spearman | 41,348 | 0.568 | 0.737 | 0.751 |

## Top-risk precision

| group | top fraction | calls | precision | recall | lift |
|---|---:|---:|---:|---:|---:|
| all_external_methods | 5% | 8,150 | 0.822 | 0.092 | 1.85 |
| all_external_methods | 10% | 16,300 | 0.794 | 0.179 | 1.79 |
| all_external_methods | 20% | 32,599 | 0.763 | 0.343 | 1.71 |
| all_external_methods | 30% | 48,898 | 0.715 | 0.482 | 1.61 |
| celltypist_style_logistic | 5% | 2,068 | 0.766 | 0.114 | 2.28 |
| celltypist_style_logistic | 10% | 4,135 | 0.728 | 0.216 | 2.16 |
| celltypist_style_logistic | 20% | 8,270 | 0.674 | 0.400 | 2.00 |
| celltypist_style_logistic | 30% | 12,405 | 0.601 | 0.536 | 1.79 |
| scmap_style_knn | 5% | 2,068 | 0.883 | 0.092 | 1.83 |
| scmap_style_knn | 10% | 4,135 | 0.826 | 0.171 | 1.71 |
| scmap_style_knn | 20% | 8,270 | 0.817 | 0.339 | 1.69 |
| scmap_style_knn | 30% | 12,405 | 0.793 | 0.493 | 1.64 |
| seurat_label_transfer | 5% | 1,948 | 0.756 | 0.097 | 1.94 |
| seurat_label_transfer | 10% | 3,895 | 0.746 | 0.191 | 1.91 |
| seurat_label_transfer | 20% | 7,790 | 0.724 | 0.372 | 1.86 |
| seurat_label_transfer | 30% | 11,685 | 0.699 | 0.538 | 1.79 |
| singler_style_spearman | 5% | 2,068 | 0.804 | 0.071 | 1.42 |
| singler_style_spearman | 10% | 4,135 | 0.807 | 0.142 | 1.42 |
| singler_style_spearman | 20% | 8,270 | 0.793 | 0.279 | 1.40 |
| singler_style_spearman | 30% | 12,405 | 0.778 | 0.411 | 1.37 |

## Interpretation

The audit score remains informative on external annotation outputs.
This supports the package design: NicheTypeR can be used after a strong
reference mapper to prioritize calls whose confidence margin suggests
higher error risk.
