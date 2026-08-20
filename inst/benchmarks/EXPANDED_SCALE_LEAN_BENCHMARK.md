# Expanded-Scale Lean Blocked Benchmark

This stress test uses larger train/test splits than the preview benchmark.
It keeps the core marker, reference-profile, learned-neighborhood, random-graph,
permuted-prior and context-specific residual comparisons, with fixed evidence weights
to avoid turning the scale-control experiment into another tuning benchmark.

## Dataset Scale

| dataset | source | cells/spots | features | labels | spatial groups | sampling |
|---|---|---:|---:|---:|---:|---|
| GSE202623_CELLTYPE_EXPANDED | GSE202623 | 33760 | 287 | 42 | 3337 | balanced non-doublet cell.type_manual labels, min_per_label=50, max_per_label=1000 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | GSE333737 | 24222 | 300 | 4 | 12 | all labeled cells |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | GSE284005 | 34350 | 500 | 38 | 17 | balanced clean_sub labels, min_per_label=25, max_per_label=1000 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | GSE327581 | 16371 | 1207 | 55 | 5 | balanced InSituType labels, min_per_label=25, max_per_label=300 |
| SQUIDPY_MERFISH_EXPANDED | SQUIDPY_MERFISH | 73655 | 161 | 16 | 12 | all clean labels with >= 25 cells |
| SQUIDPY_SEQFISH_EXPANDED | SQUIDPY_SEQFISH | 19416 | 351 | 22 | 63 | all clean labels with >= 25 cells |
| SQUIDPY_SLIDESEQV2_EXPANDED | SQUIDPY_SLIDESEQV2 | 18842 | 1500 | 14 | 64 | balanced clean labels, min_per_label=25, max_per_label=1500, top mean features=1500 |

## Fold Size

| dataset | folds | mean train | mean test | min test | max test | mean train groups | mean test groups |
|---|---:|---:|---:|---:|---:|---:|---:|
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | 3 | 22900 | 11450 | 9025 | 13699 | 11.3 | 5.7 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | 3 | 10914 | 5457 | 2585 | 7229 | 3.3 | 1.7 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | 3 | 16148 | 8074 | 5645 | 10115 | 8.0 | 4.0 |
| GSE202623_CELLTYPE_EXPANDED | 3 | 22507 | 11253 | 11160 | 11301 | 2224.7 | 1112.3 |
| SQUIDPY_MERFISH_EXPANDED | 3 | 49103 | 24552 | 24399 | 24739 | 8.0 | 4.0 |
| SQUIDPY_SEQFISH_EXPANDED | 3 | 12944 | 6472 | 6111 | 6916 | 42.0 | 21.0 |
| SQUIDPY_SLIDESEQV2_EXPANDED | 3 | 12561 | 6281 | 5610 | 7043 | 42.7 | 21.3 |

## Model Summary

| dataset | model | accuracy | macro-F1 | conflict rate |
|---|---|---:|---:|---:|
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_permuted_prior | 0.4919 | 0.4746 | 0.7336 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_random_graph | 0.5050 | 0.4855 | 0.7018 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_context_specific_neighborhood | 0.5093 | 0.4900 | 0.7155 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_learned_neighborhood | 0.5060 | 0.4876 | 0.7420 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_only | 0.5080 | 0.4889 | 0.5885 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_reference_profile | 0.4511 | 0.4303 | 0.6880 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | reference_profile | 0.3478 | 0.3253 | 0.4831 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_permuted_prior | 0.5322 | 0.5046 | 0.6135 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_random_graph | 0.5285 | 0.5007 | 0.5742 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_context_specific_neighborhood | 0.5411 | 0.5121 | 0.5960 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_learned_neighborhood | 0.5412 | 0.5129 | 0.6004 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_only | 0.5319 | 0.5040 | 0.4127 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_reference_profile | 0.5077 | 0.4900 | 0.6507 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | reference_profile | 0.2614 | 0.2439 | 0.7693 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_permuted_prior | 0.7560 | 0.6848 | 0.5778 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_random_graph | 0.7563 | 0.6786 | 0.6341 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_context_specific_neighborhood | 0.7584 | 0.6866 | 0.5861 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_learned_neighborhood | 0.7588 | 0.6866 | 0.5501 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_only | 0.7632 | 0.6870 | 0.1868 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_reference_profile | 0.7719 | 0.6997 | 0.1829 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | reference_profile | 0.7724 | 0.7034 | 0.1801 |
| GSE202623_CELLTYPE_EXPANDED | learned_permuted_prior | 0.6264 | 0.5755 | 0.6047 |
| GSE202623_CELLTYPE_EXPANDED | learned_random_graph | 0.6397 | 0.5877 | 0.5681 |
| GSE202623_CELLTYPE_EXPANDED | marker_context_specific_neighborhood | 0.6354 | 0.5856 | 0.5797 |
| GSE202623_CELLTYPE_EXPANDED | marker_learned_neighborhood | 0.6402 | 0.5881 | 0.5674 |
| GSE202623_CELLTYPE_EXPANDED | marker_only | 0.6346 | 0.5854 | 0.4451 |
| GSE202623_CELLTYPE_EXPANDED | marker_reference_profile | 0.6339 | 0.5744 | 0.5394 |
| GSE202623_CELLTYPE_EXPANDED | reference_profile | 0.5512 | 0.4913 | 0.5937 |
| SQUIDPY_MERFISH_EXPANDED | learned_permuted_prior | 0.5857 | 0.4853 | 0.6669 |
| SQUIDPY_MERFISH_EXPANDED | learned_random_graph | 0.5911 | 0.5006 | 0.6735 |
| SQUIDPY_MERFISH_EXPANDED | marker_context_specific_neighborhood | 0.5867 | 0.4936 | 0.6530 |
| SQUIDPY_MERFISH_EXPANDED | marker_learned_neighborhood | 0.5876 | 0.4867 | 0.6552 |
| SQUIDPY_MERFISH_EXPANDED | marker_only | 0.5960 | 0.5122 | 0.4335 |
| SQUIDPY_MERFISH_EXPANDED | marker_reference_profile | 0.6008 | 0.4717 | 0.5096 |
| SQUIDPY_MERFISH_EXPANDED | reference_profile | 0.5716 | 0.4325 | 0.4994 |
| SQUIDPY_SEQFISH_EXPANDED | learned_permuted_prior | 0.6136 | 0.5142 | 0.6015 |
| SQUIDPY_SEQFISH_EXPANDED | learned_random_graph | 0.6125 | 0.5068 | 0.5962 |
| SQUIDPY_SEQFISH_EXPANDED | marker_context_specific_neighborhood | 0.6034 | 0.4978 | 0.5919 |
| SQUIDPY_SEQFISH_EXPANDED | marker_learned_neighborhood | 0.6152 | 0.5064 | 0.4992 |
| SQUIDPY_SEQFISH_EXPANDED | marker_only | 0.6060 | 0.5028 | 0.3976 |
| SQUIDPY_SEQFISH_EXPANDED | marker_reference_profile | 0.5569 | 0.4733 | 0.5306 |
| SQUIDPY_SEQFISH_EXPANDED | reference_profile | 0.4069 | 0.3757 | 0.4806 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_permuted_prior | 0.4192 | 0.3962 | 0.6418 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_random_graph | 0.4151 | 0.3921 | 0.6658 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_context_specific_neighborhood | 0.4148 | 0.3936 | 0.6878 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_learned_neighborhood | 0.4189 | 0.3964 | 0.6354 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_only | 0.4170 | 0.3952 | 0.5092 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_reference_profile | 0.4016 | 0.3649 | 0.6230 |
| SQUIDPY_SLIDESEQV2_EXPANDED | reference_profile | 0.3482 | 0.2920 | 0.6117 |

## Specificity Guardrail

| dataset | context delta macro-F1 | context pass | learned delta macro-F1 | learned pass | interpretation |
|---|---:|---|---:|---|---|
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | +0.0011 | no | -0.0013 | no | context signal is not specific under null controls |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | -0.0008 | no | +0.0083 | yes | learned neighborhood passes null guardrail |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | -0.0004 | no | -0.0004 | no | context signal is not specific under null controls |
| GSE202623_CELLTYPE_EXPANDED | -0.0025 | no | +0.0003 | no | context signal is not specific under null controls |
| SQUIDPY_MERFISH_EXPANDED | -0.0186 | no | -0.0255 | no | context signal is not specific under null controls |
| SQUIDPY_SEQFISH_EXPANDED | -0.0164 | no | -0.0078 | no | context signal is not specific under null controls |
| SQUIDPY_SLIDESEQV2_EXPANDED | -0.0028 | no | +0.0002 | no | context signal is not specific under null controls |

## Paired Comparisons vs Marker-Only

| dataset | comparator | accuracy diff | McNemar p |
|---|---|---:|---:|
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_permuted_prior | -0.0161 | 1.346e-25 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_random_graph | -0.0030 | 0.005091 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_context_specific_neighborhood | +0.0014 | 0.2506 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_learned_neighborhood | -0.0020 | 0.06625 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_reference_profile | -0.0569 | 6.068e-96 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | reference_profile | -0.1601 | 0 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_permuted_prior | +0.0002 | 0.9071 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_random_graph | -0.0034 | 0.006532 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_context_specific_neighborhood | +0.0092 | 1.515e-12 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_learned_neighborhood | +0.0093 | 7.502e-13 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_reference_profile | -0.0243 | 3.082e-22 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | reference_profile | -0.2705 | 0 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_permuted_prior | -0.0073 | 6.993e-07 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_random_graph | -0.0070 | 6.198e-06 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_context_specific_neighborhood | -0.0049 | 0.001019 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_learned_neighborhood | -0.0044 | 0.002344 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_reference_profile | +0.0087 | 6.191e-13 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | reference_profile | +0.0092 | 7.294e-08 |
| GSE202623_CELLTYPE_EXPANDED | learned_permuted_prior | -0.0082 | 1.673e-10 |
| GSE202623_CELLTYPE_EXPANDED | learned_random_graph | +0.0052 | 3.436e-08 |
| GSE202623_CELLTYPE_EXPANDED | marker_context_specific_neighborhood | +0.0009 | 0.4322 |
| GSE202623_CELLTYPE_EXPANDED | marker_learned_neighborhood | +0.0056 | 2.352e-09 |
| GSE202623_CELLTYPE_EXPANDED | marker_reference_profile | -0.0007 | 0.7542 |
| GSE202623_CELLTYPE_EXPANDED | reference_profile | -0.0834 | 5.413e-208 |
| SQUIDPY_MERFISH_EXPANDED | learned_permuted_prior | -0.0103 | 1.657e-35 |
| SQUIDPY_MERFISH_EXPANDED | learned_random_graph | -0.0049 | 9.916e-12 |
| SQUIDPY_MERFISH_EXPANDED | marker_context_specific_neighborhood | -0.0093 | 2.991e-31 |
| SQUIDPY_MERFISH_EXPANDED | marker_learned_neighborhood | -0.0084 | 1.81e-29 |
| SQUIDPY_MERFISH_EXPANDED | marker_reference_profile | +0.0048 | 9.965e-07 |
| SQUIDPY_MERFISH_EXPANDED | reference_profile | -0.0244 | 2.399e-77 |
| SQUIDPY_SEQFISH_EXPANDED | learned_permuted_prior | +0.0076 | 3.001e-06 |
| SQUIDPY_SEQFISH_EXPANDED | learned_random_graph | +0.0065 | 1.789e-05 |
| SQUIDPY_SEQFISH_EXPANDED | marker_context_specific_neighborhood | -0.0026 | 0.07021 |
| SQUIDPY_SEQFISH_EXPANDED | marker_learned_neighborhood | +0.0092 | 3.821e-11 |
| SQUIDPY_SEQFISH_EXPANDED | marker_reference_profile | -0.0491 | 4.884e-54 |
| SQUIDPY_SEQFISH_EXPANDED | reference_profile | -0.1991 | 0 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_permuted_prior | +0.0022 | 0.1523 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_random_graph | -0.0019 | 0.1415 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_context_specific_neighborhood | -0.0022 | 0.1107 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_learned_neighborhood | +0.0019 | 0.0981 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_reference_profile | -0.0154 | 1.434e-10 |
| SQUIDPY_SLIDESEQV2_EXPANDED | reference_profile | -0.0688 | 1.52e-88 |

## Dataset Configs

```json
[
  {
    "dataset_id": "GSE202623_CELLTYPE_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GSE202623_CELLTYPE_EXPANDED\\GSE202623_CELLTYPE_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GSE202623_CELLTYPE_EXPANDED\\GSE202623_CELLTYPE_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "MERFISH_RNA_single_cell",
    "max_folds": 3,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "MERSCOPE_MERFISH_RNA_single_cell",
    "max_folds": 3,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE284005_MERSCOPE_MS_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE284005_MERSCOPE_MS_EXPANDED\\GEO_GSE284005_MERSCOPE_MS_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE284005_MERSCOPE_MS_EXPANDED\\GEO_GSE284005_MERSCOPE_MS_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "MERSCOPE_MERFISH_RNA_single_cell",
    "max_folds": 3,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED\\GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED\\GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "CosMx_spatial_molecular_imaging",
    "max_folds": 3,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_MERFISH_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_MERFISH_EXPANDED\\SQUIDPY_MERFISH_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_MERFISH_EXPANDED\\SQUIDPY_MERFISH_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "spatial_transcriptomics_single_cell",
    "max_folds": 3,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_SEQFISH_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SEQFISH_EXPANDED\\SQUIDPY_SEQFISH_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SEQFISH_EXPANDED\\SQUIDPY_SEQFISH_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "spatial_transcriptomics_single_cell",
    "max_folds": 3,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_SLIDESEQV2_EXPANDED",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SLIDESEQV2_EXPANDED\\SQUIDPY_SLIDESEQV2_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SLIDESEQV2_EXPANDED\\SQUIDPY_SLIDESEQV2_EXPANDED_expanded_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "expanded_scale_validation",
    "modality": "spatial_transcriptomics_bead",
    "max_folds": 3,
    "top_markers_per_label": 20
  }
]
```
