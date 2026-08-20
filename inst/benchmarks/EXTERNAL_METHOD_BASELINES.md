# External Annotation Method Baselines

This benchmark extends the Seurat label-transfer baseline with blocked
algorithmic proxy mappers that mimic common external annotation families.
The proxy models are included to test NicheTypeR's audit interface and
error triage under diverse external label sources. They are not claimed to
be official SingleR, scmap or CellTypist package runs.

## Official tool status

| tool | official status | local requirement | proxy used | note |
|---|---|---|---|---|
| Seurat label transfer | completed | R/Seurat |  | Existing blocked Seurat label-transfer results are used as the official anchor-transfer baseline. |
| SingleR | not_run | R/Bioconductor SingleR | singler_style_spearman | Rscript unavailable in this workspace. |
| scmap | not_run | R/Bioconductor scmap | scmap_style_knn | Rscript unavailable in this workspace. |
| CellTypist | not_run | Python celltypist package and model download | celltypist_style_logistic | celltypist is not installed locally. |
| Azimuth | not_run | R/Seurat Azimuth plus compatible reference maps | seurat_label_transfer | Treated as an anchor-mapping family comparison through the completed Seurat label-transfer baseline. |

## Summary

| dataset | model | implementation | accuracy | macro-F1 | conflict rate |
|---|---|---|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | celltypist_style_logistic | algorithmic_proxy | 0.6054 | 0.5025 | 0.3575 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | scmap_style_knn | algorithmic_proxy | 0.3747 | 0.2813 | 0.6893 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | singler_style_spearman | algorithmic_proxy | 0.4207 | 0.3447 | 1.0000 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | seurat_label_transfer | official_package | 0.6110 | 0.5146 | 0.1394 |
| GEO_GSE284005_MERSCOPE_MS | celltypist_style_logistic | algorithmic_proxy | 0.6378 | 0.6420 | 1.0000 |
| GEO_GSE284005_MERSCOPE_MS | scmap_style_knn | algorithmic_proxy | 0.4029 | 0.4079 | 1.0000 |
| GEO_GSE284005_MERSCOPE_MS | singler_style_spearman | algorithmic_proxy | 0.1789 | 0.1572 | 1.0000 |
| GEO_GSE284005_MERSCOPE_MS | seurat_label_transfer | official_package | 0.4315 | 0.4229 | 0.3224 |
| GEO_GSE327581_COSMX_AD_BRAIN | celltypist_style_logistic | algorithmic_proxy | 0.4351 | 0.4483 | 1.0000 |
| GEO_GSE327581_COSMX_AD_BRAIN | scmap_style_knn | algorithmic_proxy | 0.2647 | 0.2814 | 1.0000 |
| GEO_GSE327581_COSMX_AD_BRAIN | singler_style_spearman | algorithmic_proxy | 0.3058 | 0.3613 | 1.0000 |
| GEO_GSE327581_COSMX_AD_BRAIN | seurat_label_transfer | official_package | 0.4936 | 0.4743 | 0.3124 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | celltypist_style_logistic | algorithmic_proxy | 0.7321 | 0.7311 | 0.0667 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | scmap_style_knn | algorithmic_proxy | 0.7163 | 0.7064 | 0.4017 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | singler_style_spearman | algorithmic_proxy | 0.6158 | 0.5777 | 0.9358 |
| GSE202623_LESION | celltypist_style_logistic | algorithmic_proxy | 0.9163 | 0.8263 | 0.0853 |
| GSE202623_LESION | scmap_style_knn | algorithmic_proxy | 0.8423 | 0.6802 | 0.1453 |
| GSE202623_LESION | singler_style_spearman | algorithmic_proxy | 0.6608 | 0.5142 | 0.9924 |
| GSE202623_LESION | seurat_label_transfer | official_package | 0.9272 | 0.7347 | 0.0133 |
| SQUIDPY_MERFISH | celltypist_style_logistic | algorithmic_proxy | 0.8866 | 0.8706 | 0.2007 |
| SQUIDPY_MERFISH | scmap_style_knn | algorithmic_proxy | 0.8330 | 0.7577 | 0.5181 |
| SQUIDPY_MERFISH | singler_style_spearman | algorithmic_proxy | 0.6385 | 0.5814 | 1.0000 |
| SQUIDPY_MERFISH | seurat_label_transfer | official_package | 0.7529 | 0.7483 | 0.0998 |
| SQUIDPY_SEQFISH | celltypist_style_logistic | algorithmic_proxy | 0.6933 | 0.6458 | 1.0000 |
| SQUIDPY_SEQFISH | scmap_style_knn | algorithmic_proxy | 0.5777 | 0.5133 | 1.0000 |
| SQUIDPY_SEQFISH | singler_style_spearman | algorithmic_proxy | 0.4569 | 0.4468 | 1.0000 |
| SQUIDPY_SEQFISH | seurat_label_transfer | official_package | 0.6717 | 0.5909 | 0.1188 |
| SQUIDPY_SLIDESEQV2 | celltypist_style_logistic | algorithmic_proxy | 0.3079 | 0.3115 | 0.5736 |
| SQUIDPY_SLIDESEQV2 | scmap_style_knn | algorithmic_proxy | 0.3032 | 0.2880 | 0.9421 |
| SQUIDPY_SLIDESEQV2 | singler_style_spearman | algorithmic_proxy | 0.1764 | 0.1484 | 1.0000 |
| SQUIDPY_SLIDESEQV2 | seurat_label_transfer | official_package | 0.3646 | 0.3503 | 0.4329 |
| SQUIDPY_VISIUM_FLUO | celltypist_style_logistic | algorithmic_proxy | 0.7948 | 0.7436 | 0.3502 |
| SQUIDPY_VISIUM_FLUO | scmap_style_knn | algorithmic_proxy | 0.6360 | 0.5508 | 0.7261 |
| SQUIDPY_VISIUM_FLUO | singler_style_spearman | algorithmic_proxy | 0.7770 | 0.7621 | 1.0000 |
| SQUIDPY_VISIUM_FLUO | seurat_label_transfer | official_package | 0.8463 | 0.8339 | 0.0527 |
| SQUIDPY_VISIUM_HNE | celltypist_style_logistic | algorithmic_proxy | 0.8512 | 0.8525 | 0.3043 |
| SQUIDPY_VISIUM_HNE | scmap_style_knn | algorithmic_proxy | 0.6752 | 0.6511 | 0.7158 |
| SQUIDPY_VISIUM_HNE | singler_style_spearman | algorithmic_proxy | 0.7723 | 0.7545 | 1.0000 |
| SQUIDPY_VISIUM_HNE | seurat_label_transfer | official_package | 0.8568 | 0.8482 | 0.0543 |

## Paired comparisons against marker-only

| dataset | comparator | accuracy diff | marker wrong, comparator right | marker right, comparator wrong | McNemar p |
|---|---|---:|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | celltypist_style_logistic | +0.2657 | 1398 | 359 | 1.815e-144 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | scmap_style_knn | +0.0350 | 819 | 682 | 0.0004438 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | seurat_label_transfer | +0.2714 | 1425 | 364 | 5.606e-148 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | singler_style_spearman | +0.0811 | 875 | 558 | 5.222e-17 |
| GEO_GSE284005_MERSCOPE_MS | celltypist_style_logistic | +0.1382 | 2141 | 843 | 8.535e-129 |
| GEO_GSE284005_MERSCOPE_MS | scmap_style_knn | -0.0968 | 1027 | 1936 | 1.876e-63 |
| GEO_GSE284005_MERSCOPE_MS | seurat_label_transfer | -0.0681 | 1271 | 1911 | 6.156e-30 |
| GEO_GSE284005_MERSCOPE_MS | singler_style_spearman | -0.3208 | 601 | 3614 | 0 |
| GEO_GSE327581_COSMX_AD_BRAIN | celltypist_style_logistic | -0.0589 | 848 | 1172 | 5.942e-13 |
| GEO_GSE327581_COSMX_AD_BRAIN | scmap_style_knn | -0.2293 | 469 | 1730 | 5.545e-169 |
| GEO_GSE327581_COSMX_AD_BRAIN | seurat_label_transfer | -0.0004 | 923 | 925 | 0.9814 |
| GEO_GSE327581_COSMX_AD_BRAIN | singler_style_spearman | -0.1882 | 597 | 1632 | 2.016e-110 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | celltypist_style_logistic | -0.0275 | 249 | 315 | 0.006151 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | scmap_style_knn | -0.0433 | 183 | 287 | 1.847e-06 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | singler_style_spearman | -0.1438 | 195 | 540 | 2.702e-38 |
| GSE202623_LESION | celltypist_style_logistic | +0.2121 | 585 | 58 | 1.373e-110 |
| GSE202623_LESION | scmap_style_knn | +0.1380 | 561 | 218 | 1.174e-35 |
| GSE202623_LESION | seurat_label_transfer | +0.2229 | 653 | 99 | 6.928e-101 |
| GSE202623_LESION | singler_style_spearman | -0.0435 | 204 | 312 | 2.281e-06 |
| SQUIDPY_MERFISH | celltypist_style_logistic | +0.1032 | 570 | 154 | 5.943e-57 |
| SQUIDPY_MERFISH | scmap_style_knn | +0.0496 | 425 | 225 | 3.618e-15 |
| SQUIDPY_MERFISH | seurat_label_transfer | -0.0305 | 352 | 475 | 2.141e-05 |
| SQUIDPY_MERFISH | singler_style_spearman | -0.1449 | 342 | 926 | 1.71e-62 |
| SQUIDPY_SEQFISH | celltypist_style_logistic | +0.0445 | 781 | 541 | 4.369e-11 |
| SQUIDPY_SEQFISH | scmap_style_knn | -0.0711 | 518 | 901 | 1.921e-24 |
| SQUIDPY_SEQFISH | seurat_label_transfer | +0.0230 | 700 | 576 | 0.0005694 |
| SQUIDPY_SEQFISH | singler_style_spearman | -0.1919 | 424 | 1458 | 2.121e-132 |
| SQUIDPY_SLIDESEQV2 | celltypist_style_logistic | -0.0875 | 236 | 481 | 3.478e-20 |
| SQUIDPY_SLIDESEQV2 | scmap_style_knn | -0.0921 | 227 | 485 | 2.033e-22 |
| SQUIDPY_SLIDESEQV2 | seurat_label_transfer | -0.0307 | 301 | 387 | 0.001177 |
| SQUIDPY_SLIDESEQV2 | singler_style_spearman | -0.2189 | 94 | 707 | 4.731e-117 |
| SQUIDPY_VISIUM_FLUO | celltypist_style_logistic | +0.2354 | 839 | 191 | 2.319e-97 |
| SQUIDPY_VISIUM_FLUO | scmap_style_knn | +0.0766 | 509 | 298 | 1.051e-13 |
| SQUIDPY_VISIUM_FLUO | seurat_label_transfer | +0.2870 | 904 | 114 | 3.409e-153 |
| SQUIDPY_VISIUM_FLUO | singler_style_spearman | +0.2176 | 785 | 186 | 4.148e-88 |
| SQUIDPY_VISIUM_HNE | celltypist_style_logistic | +0.3363 | 1024 | 120 | 2.25e-179 |
| SQUIDPY_VISIUM_HNE | scmap_style_knn | +0.1603 | 731 | 300 | 4.109e-42 |
| SQUIDPY_VISIUM_HNE | seurat_label_transfer | +0.3419 | 1050 | 131 | 1.336e-178 |
| SQUIDPY_VISIUM_HNE | singler_style_spearman | +0.2574 | 924 | 232 | 4.048e-98 |

## Interpretation

The proxy benchmark completed 150 dataset-fold-model tasks.
Together with the completed Seurat label-transfer run, this reduces the
risk that NicheTypeR is only demonstrated on one handcrafted reference
source. The remaining limitation is explicit: official SingleR, scmap,
CellTypist and Azimuth package runs require their native packages and
reference assets, which were not available in this local workspace.
