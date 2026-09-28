# Multi-Dataset Blocked Benchmark Results

This benchmark learns marker-like signatures and spatial compatibility
inside each training fold, then evaluates held-out spatial groups.

Models:

- `marker_only`
- `reference_profile`
- `marker_reference_profile`
- `marker_spatial_smoothing`
- `marker_spatial_smoothing_random_graph`
- `marker_learned_neighborhood`
- `reference_profile_learned_neighborhood`
- `marker_context_specific_neighborhood`
- `learned_random_graph`
- `learned_permuted_prior`

## Summary

| dataset | model | accuracy | macro-F1 | conflict rate |
|---|---|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | learned_permuted_prior | 0.3529 | 0.3055 | 0.7294 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | learned_random_graph | 0.3583 | 0.3151 | 0.7491 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_context_specific_neighborhood | 0.3332 | 0.2924 | 0.7074 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_learned_neighborhood | 0.3274 | 0.2955 | 0.7499 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_only | 0.3396 | 0.2971 | 0.6115 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing | 0.3583 | 0.3193 | 0.6358 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing_random_graph | 0.3432 | 0.3095 | 0.6128 |
| GEO_GSE284005_MERSCOPE_MS | learned_permuted_prior | 0.4973 | 0.4786 | 0.6701 |
| GEO_GSE284005_MERSCOPE_MS | learned_random_graph | 0.4973 | 0.4785 | 0.6538 |
| GEO_GSE284005_MERSCOPE_MS | marker_context_specific_neighborhood | 0.5011 | 0.4818 | 0.6917 |
| GEO_GSE284005_MERSCOPE_MS | marker_learned_neighborhood | 0.5009 | 0.4815 | 0.7068 |
| GEO_GSE284005_MERSCOPE_MS | marker_only | 0.4996 | 0.4806 | 0.5861 |
| GEO_GSE284005_MERSCOPE_MS | marker_spatial_smoothing | 0.5034 | 0.4837 | 0.6206 |
| GEO_GSE284005_MERSCOPE_MS | marker_spatial_smoothing_random_graph | 0.5019 | 0.4820 | 0.6129 |
| GEO_GSE327581_COSMX_AD_BRAIN | learned_permuted_prior | 0.4942 | 0.4665 | 0.5893 |
| GEO_GSE327581_COSMX_AD_BRAIN | learned_random_graph | 0.4925 | 0.4653 | 0.5098 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_context_specific_neighborhood | 0.5042 | 0.4772 | 0.6258 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | 0.5058 | 0.4763 | 0.6385 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_only | 0.4940 | 0.4666 | 0.4135 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_spatial_smoothing | 0.4980 | 0.4709 | 0.5216 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_spatial_smoothing_random_graph | 0.5016 | 0.4744 | 0.5113 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | learned_permuted_prior | 0.7554 | 0.7524 | 0.6396 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | learned_random_graph | 0.7558 | 0.7528 | 0.7033 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_context_specific_neighborhood | 0.7579 | 0.7548 | 0.6596 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_learned_neighborhood | 0.7583 | 0.7552 | 0.6483 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_only | 0.7596 | 0.7567 | 0.1671 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_spatial_smoothing | 0.7604 | 0.7575 | 0.1837 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_spatial_smoothing_random_graph | 0.7554 | 0.7525 | 0.1808 |
| GSE202623_LESION | learned_permuted_prior | 0.7091 | 0.5870 | 0.6060 |
| GSE202623_LESION | learned_random_graph | 0.7107 | 0.5855 | 0.5952 |
| GSE202623_LESION | marker_context_specific_neighborhood | 0.7082 | 0.5911 | 0.7095 |
| GSE202623_LESION | marker_learned_neighborhood | 0.7171 | 0.5968 | 0.5960 |
| GSE202623_LESION | marker_only | 0.7042 | 0.5857 | 0.3618 |
| GSE202623_LESION | marker_spatial_smoothing | 0.7038 | 0.5855 | 0.4012 |
| GSE202623_LESION | marker_spatial_smoothing_random_graph | 0.7054 | 0.5866 | 0.4153 |
| SQUIDPY_IMC | learned_permuted_prior | 0.3939 | 0.3669 | 0.7133 |
| SQUIDPY_IMC | learned_random_graph | 0.3933 | 0.3625 | 0.6795 |
| SQUIDPY_IMC | marker_context_specific_neighborhood | 0.4031 | 0.3713 | 0.7041 |
| SQUIDPY_IMC | marker_learned_neighborhood | 0.3916 | 0.3637 | 0.6737 |
| SQUIDPY_IMC | marker_only | 0.3928 | 0.3651 | 0.5849 |
| SQUIDPY_IMC | marker_spatial_smoothing | 0.4014 | 0.3646 | 0.6021 |
| SQUIDPY_IMC | marker_spatial_smoothing_random_graph | 0.4083 | 0.3734 | 0.5786 |
| SQUIDPY_MERFISH | learned_permuted_prior | 0.7851 | 0.7443 | 0.5350 |
| SQUIDPY_MERFISH | learned_random_graph | 0.7821 | 0.7401 | 0.4556 |
| SQUIDPY_MERFISH | marker_context_specific_neighborhood | 0.7864 | 0.7457 | 0.4725 |
| SQUIDPY_MERFISH | marker_learned_neighborhood | 0.7871 | 0.7473 | 0.4330 |
| SQUIDPY_MERFISH | marker_only | 0.7834 | 0.7421 | 0.2283 |
| SQUIDPY_MERFISH | marker_spatial_smoothing | 0.7873 | 0.7474 | 0.2901 |
| SQUIDPY_MERFISH | marker_spatial_smoothing_random_graph | 0.7938 | 0.7551 | 0.2573 |
| SQUIDPY_MIBITOF | learned_permuted_prior | 0.5507 | 0.5173 | 0.5303 |
| SQUIDPY_MIBITOF | learned_random_graph | 0.5358 | 0.5022 | 0.6615 |
| SQUIDPY_MIBITOF | marker_context_specific_neighborhood | 0.5442 | 0.5117 | 0.5283 |
| SQUIDPY_MIBITOF | marker_learned_neighborhood | 0.5447 | 0.5110 | 0.4985 |
| SQUIDPY_MIBITOF | marker_only | 0.5497 | 0.5169 | 0.2704 |
| SQUIDPY_MIBITOF | marker_spatial_smoothing | 0.5457 | 0.5149 | 0.2952 |
| SQUIDPY_MIBITOF | marker_spatial_smoothing_random_graph | 0.5487 | 0.5222 | 0.2674 |
| SQUIDPY_SEQFISH | learned_permuted_prior | 0.6511 | 0.5962 | 0.5016 |
| SQUIDPY_SEQFISH | learned_random_graph | 0.6510 | 0.5968 | 0.5626 |
| SQUIDPY_SEQFISH | marker_context_specific_neighborhood | 0.6523 | 0.5986 | 0.5461 |
| SQUIDPY_SEQFISH | marker_learned_neighborhood | 0.6595 | 0.6060 | 0.4908 |
| SQUIDPY_SEQFISH | marker_only | 0.6487 | 0.5941 | 0.3270 |
| SQUIDPY_SEQFISH | marker_spatial_smoothing | 0.6558 | 0.6020 | 0.3678 |
| SQUIDPY_SEQFISH | marker_spatial_smoothing_random_graph | 0.6498 | 0.5965 | 0.3797 |
| SQUIDPY_SLIDESEQV2 | learned_permuted_prior | 0.3957 | 0.3796 | 0.7064 |
| SQUIDPY_SLIDESEQV2 | learned_random_graph | 0.3950 | 0.3784 | 0.6396 |
| SQUIDPY_SLIDESEQV2 | marker_context_specific_neighborhood | 0.3971 | 0.3826 | 0.6857 |
| SQUIDPY_SLIDESEQV2 | marker_learned_neighborhood | 0.3961 | 0.3801 | 0.6432 |
| SQUIDPY_SLIDESEQV2 | marker_only | 0.3954 | 0.3795 | 0.4989 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing | 0.3954 | 0.3786 | 0.5093 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing_random_graph | 0.3971 | 0.3809 | 0.5157 |
| SQUIDPY_VISIUM_FLUO | learned_permuted_prior | 0.6171 | 0.5367 | 0.5761 |
| SQUIDPY_VISIUM_FLUO | learned_random_graph | 0.5699 | 0.4941 | 0.6023 |
| SQUIDPY_VISIUM_FLUO | marker_context_specific_neighborhood | 0.5688 | 0.4946 | 0.7000 |
| SQUIDPY_VISIUM_FLUO | marker_learned_neighborhood | 0.6179 | 0.5291 | 0.5543 |
| SQUIDPY_VISIUM_FLUO | marker_only | 0.5594 | 0.4859 | 0.3992 |
| SQUIDPY_VISIUM_FLUO | marker_spatial_smoothing | 0.5823 | 0.5089 | 0.4290 |
| SQUIDPY_VISIUM_FLUO | marker_spatial_smoothing_random_graph | 0.5688 | 0.4915 | 0.4631 |
| SQUIDPY_VISIUM_HNE | learned_permuted_prior | 0.6205 | 0.5874 | 0.6897 |
| SQUIDPY_VISIUM_HNE | learned_random_graph | 0.5286 | 0.4970 | 0.7121 |
| SQUIDPY_VISIUM_HNE | marker_context_specific_neighborhood | 0.5458 | 0.5161 | 0.7716 |
| SQUIDPY_VISIUM_HNE | marker_learned_neighborhood | 0.5517 | 0.5183 | 0.6146 |
| SQUIDPY_VISIUM_HNE | marker_only | 0.5149 | 0.4762 | 0.4550 |
| SQUIDPY_VISIUM_HNE | marker_spatial_smoothing | 0.5703 | 0.5410 | 0.4929 |
| SQUIDPY_VISIUM_HNE | marker_spatial_smoothing_random_graph | 0.5632 | 0.5424 | 0.5089 |

## Specificity Guardrail

The strongest guardrail is `marker_context_specific_neighborhood`: it
uses observed learned-neighborhood scores after subtracting the mean of
random-graph and permuted-prior null scores.

A learned-neighborhood gain is counted as specific only if it beats
marker-only, learned-random-graph, and learned-permuted-prior controls.
A smoothing gain is counted as specific only if it beats marker-only and
random-graph smoothing. Both guardrails require macro-F1 delta > 0.005
and positive accuracy delta.

| dataset | context-specific delta macro-F1 | context pass | learned delta macro-F1 | learned pass | smoothing delta macro-F1 | smoothing pass | interpretation |
|---|---:|---|---:|---|---:|---|---|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | -0.0227 | no | -0.0196 | no | +0.0098 | yes | simple spatial smoothing beats marker and random smoothing |
| GEO_GSE284005_MERSCOPE_MS | -0.0002 | no | +0.0008 | no | +0.0017 | no | context signal is not specific under null controls |
| GEO_GSE327581_COSMX_AD_BRAIN | +0.0009 | no | +0.0097 | yes | -0.0035 | no | learned neighborhood beats marker and null controls |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | -0.0019 | no | -0.0015 | no | +0.0008 | no | context signal is not specific under null controls |
| GSE202623_LESION | -0.0058 | no | +0.0099 | yes | -0.0011 | no | learned neighborhood beats marker and null controls |
| SQUIDPY_IMC | -0.0021 | no | -0.0033 | no | -0.0089 | no | context signal is not specific under null controls |
| SQUIDPY_MERFISH | -0.0093 | no | +0.0030 | no | -0.0076 | no | context signal is not specific under null controls |
| SQUIDPY_MIBITOF | -0.0105 | no | -0.0063 | no | -0.0073 | no | context signal is not specific under null controls |
| SQUIDPY_SEQFISH | -0.0074 | no | +0.0092 | yes | +0.0054 | yes | learned neighborhood beats marker and null controls |
| SQUIDPY_SLIDESEQV2 | +0.0017 | no | +0.0004 | no | -0.0023 | no | context signal is not specific under null controls |
| SQUIDPY_VISIUM_FLUO | -0.0421 | no | -0.0075 | no | +0.0174 | yes | simple spatial smoothing beats marker and random smoothing |
| SQUIDPY_VISIUM_HNE | -0.0714 | no | -0.0691 | no | -0.0014 | no | context signal is not specific under null controls |

## Best Model Per Dataset

| dataset | best model | accuracy | macro-F1 |
|---|---|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing | 0.3583 | 0.3193 |
| GEO_GSE284005_MERSCOPE_MS | marker_spatial_smoothing | 0.5034 | 0.4837 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_context_specific_neighborhood | 0.5042 | 0.4772 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_spatial_smoothing | 0.7604 | 0.7575 |
| GSE202623_LESION | marker_learned_neighborhood | 0.7171 | 0.5968 |
| SQUIDPY_IMC | marker_spatial_smoothing_random_graph | 0.4083 | 0.3734 |
| SQUIDPY_MERFISH | marker_spatial_smoothing_random_graph | 0.7938 | 0.7551 |
| SQUIDPY_MIBITOF | marker_spatial_smoothing_random_graph | 0.5487 | 0.5222 |
| SQUIDPY_SEQFISH | marker_learned_neighborhood | 0.6595 | 0.6060 |
| SQUIDPY_SLIDESEQV2 | marker_context_specific_neighborhood | 0.3971 | 0.3826 |
| SQUIDPY_VISIUM_FLUO | learned_permuted_prior | 0.6171 | 0.5367 |
| SQUIDPY_VISIUM_HNE | learned_permuted_prior | 0.6205 | 0.5874 |

## Paired Comparisons vs Marker-Only

| dataset | comparator | accuracy diff | McNemar p |
|---|---|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | learned_permuted_prior | +0.0133 | 0.004408 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | learned_random_graph | +0.0187 | 0.001393 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_context_specific_neighborhood | -0.0064 | 0.01055 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_learned_neighborhood | -0.0123 | 0.03218 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing | +0.0187 | 1.574e-07 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing_random_graph | +0.0036 | 0.411 |
| GEO_GSE284005_MERSCOPE_MS | learned_permuted_prior | -0.0023 | 0.1604 |
| GEO_GSE284005_MERSCOPE_MS | learned_random_graph | -0.0023 | 0.1193 |
| GEO_GSE284005_MERSCOPE_MS | marker_context_specific_neighborhood | +0.0015 | 0.4716 |
| GEO_GSE284005_MERSCOPE_MS | marker_learned_neighborhood | +0.0013 | 0.5155 |
| GEO_GSE284005_MERSCOPE_MS | marker_spatial_smoothing | +0.0037 | 0.06543 |
| GEO_GSE284005_MERSCOPE_MS | marker_spatial_smoothing_random_graph | +0.0022 | 0.2328 |
| GEO_GSE327581_COSMX_AD_BRAIN | learned_permuted_prior | +0.0002 | 1 |
| GEO_GSE327581_COSMX_AD_BRAIN | learned_random_graph | -0.0015 | 0.302 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_context_specific_neighborhood | +0.0102 | 0.0002869 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | +0.0118 | 0.0005104 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_spatial_smoothing | +0.0040 | 0.04087 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_spatial_smoothing_random_graph | +0.0076 | 0.0003986 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | learned_permuted_prior | -0.0042 | 0.1214 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | learned_random_graph | -0.0038 | 0.1078 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_context_specific_neighborhood | -0.0017 | 0.5572 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_learned_neighborhood | -0.0013 | 0.7359 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_spatial_smoothing | +0.0008 | 0.8642 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_spatial_smoothing_random_graph | -0.0042 | 0.2529 |
| GSE202623_LESION | learned_permuted_prior | +0.0048 | 0.0501 |
| GSE202623_LESION | learned_random_graph | +0.0064 | 0.04022 |
| GSE202623_LESION | marker_context_specific_neighborhood | +0.0040 | 0.2203 |
| GSE202623_LESION | marker_learned_neighborhood | +0.0129 | 0.002944 |
| GSE202623_LESION | marker_spatial_smoothing | -0.0004 | 1 |
| GSE202623_LESION | marker_spatial_smoothing_random_graph | +0.0012 | 0.6072 |
| SQUIDPY_IMC | learned_permuted_prior | +0.0011 | 0.8776 |
| SQUIDPY_IMC | learned_random_graph | +0.0006 | 1 |
| SQUIDPY_IMC | marker_context_specific_neighborhood | +0.0103 | 0.03277 |
| SQUIDPY_IMC | marker_learned_neighborhood | -0.0011 | 0.8919 |
| SQUIDPY_IMC | marker_spatial_smoothing | +0.0086 | 0.1591 |
| SQUIDPY_IMC | marker_spatial_smoothing_random_graph | +0.0155 | 0.002799 |
| SQUIDPY_MERFISH | learned_permuted_prior | +0.0017 | 0.3368 |
| SQUIDPY_MERFISH | learned_random_graph | -0.0012 | 0.4049 |
| SQUIDPY_MERFISH | marker_context_specific_neighborhood | +0.0030 | 0.1337 |
| SQUIDPY_MERFISH | marker_learned_neighborhood | +0.0037 | 0.06274 |
| SQUIDPY_MERFISH | marker_spatial_smoothing | +0.0040 | 0.1052 |
| SQUIDPY_MERFISH | marker_spatial_smoothing_random_graph | +0.0104 | 4.657e-05 |
| SQUIDPY_MIBITOF | learned_permuted_prior | +0.0010 | 0.8714 |
| SQUIDPY_MIBITOF | learned_random_graph | -0.0139 | 0.0002344 |
| SQUIDPY_MIBITOF | marker_context_specific_neighborhood | -0.0055 | 0.2 |
| SQUIDPY_MIBITOF | marker_learned_neighborhood | -0.0050 | 0.2288 |
| SQUIDPY_MIBITOF | marker_spatial_smoothing | -0.0040 | 0.3891 |
| SQUIDPY_MIBITOF | marker_spatial_smoothing_random_graph | -0.0010 | 0.9227 |
| SQUIDPY_SEQFISH | learned_permuted_prior | +0.0024 | 0.08543 |
| SQUIDPY_SEQFISH | learned_random_graph | +0.0022 | 0.05761 |
| SQUIDPY_SEQFISH | marker_context_specific_neighborhood | +0.0035 | 0.03954 |
| SQUIDPY_SEQFISH | marker_learned_neighborhood | +0.0108 | 0.0002061 |
| SQUIDPY_SEQFISH | marker_spatial_smoothing | +0.0071 | 1.952e-05 |
| SQUIDPY_SEQFISH | marker_spatial_smoothing_random_graph | +0.0011 | 0.5614 |
| SQUIDPY_SLIDESEQV2 | learned_permuted_prior | +0.0004 | 1 |
| SQUIDPY_SLIDESEQV2 | learned_random_graph | -0.0004 | 1 |
| SQUIDPY_SLIDESEQV2 | marker_context_specific_neighborhood | +0.0018 | 0.5682 |
| SQUIDPY_SLIDESEQV2 | marker_learned_neighborhood | +0.0007 | 0.7539 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing | +0.0000 | 1 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing_random_graph | +0.0018 | 0.4421 |
| SQUIDPY_VISIUM_FLUO | learned_permuted_prior | +0.0578 | 9.366e-14 |
| SQUIDPY_VISIUM_FLUO | learned_random_graph | +0.0105 | 0.08405 |
| SQUIDPY_VISIUM_FLUO | marker_context_specific_neighborhood | +0.0094 | 0.001858 |
| SQUIDPY_VISIUM_FLUO | marker_learned_neighborhood | +0.0585 | 1.168e-22 |
| SQUIDPY_VISIUM_FLUO | marker_spatial_smoothing | +0.0229 | 2.083e-07 |
| SQUIDPY_VISIUM_FLUO | marker_spatial_smoothing_random_graph | +0.0094 | 0.01988 |
| SQUIDPY_VISIUM_HNE | learned_permuted_prior | +0.1057 | 1.663e-35 |
| SQUIDPY_VISIUM_HNE | learned_random_graph | +0.0138 | 0.02021 |
| SQUIDPY_VISIUM_HNE | marker_context_specific_neighborhood | +0.0309 | 2.511e-06 |
| SQUIDPY_VISIUM_HNE | marker_learned_neighborhood | +0.0368 | 1.268e-11 |
| SQUIDPY_VISIUM_HNE | marker_spatial_smoothing | +0.0554 | 3.13e-23 |
| SQUIDPY_VISIUM_HNE | marker_spatial_smoothing_random_graph | +0.0484 | 6.44e-17 |

## Interpretation Guardrail

A context layer should only be interpreted as useful when it beats
`marker_only` and its matched random-graph or permuted-prior control
under blocked validation. Equal performance or zero tuned weight should be
reported as evidence for audit value rather than predictive improvement.

## Dataset Configs

```json
[
  {
    "dataset_id": "GSE202623_LESION",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GSE202623\\GSE202623_lesion_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GSE202623\\GSE202623_lesion_preview_metadata.tsv",
    "label_col": "cell.type_manual",
    "group_col": "fov_group",
    "cell_id_col": "cellID",
    "x_col": "center_x",
    "y_col": "center_y",
    "role": "primary_disease_benchmark",
    "modality": "MERFISH_RNA_single_cell",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_SEQFISH",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SEQFISH\\SQUIDPY_SEQFISH_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SEQFISH\\SQUIDPY_SEQFISH_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "primary_rna_benchmark",
    "modality": "spatial_transcriptomics_single_cell",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_MERFISH",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_MERFISH\\SQUIDPY_MERFISH_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_MERFISH\\SQUIDPY_MERFISH_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "primary_rna_benchmark",
    "modality": "spatial_transcriptomics_single_cell",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_SLIDESEQV2",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SLIDESEQV2\\SQUIDPY_SLIDESEQV2_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_SLIDESEQV2\\SQUIDPY_SLIDESEQV2_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "secondary_rna_benchmark",
    "modality": "spatial_transcriptomics_bead",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_MIBITOF",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_MIBITOF\\SQUIDPY_MIBITOF_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_MIBITOF\\SQUIDPY_MIBITOF_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "cross_modality_stress_test",
    "modality": "spatial_proteomics_single_cell",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_VISIUM_FLUO",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_VISIUM_FLUO\\SQUIDPY_VISIUM_FLUO_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_VISIUM_FLUO\\SQUIDPY_VISIUM_FLUO_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "spatial_domain_benchmark",
    "modality": "spatial_transcriptomics_visium_spot",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_VISIUM_HNE",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_VISIUM_HNE\\SQUIDPY_VISIUM_HNE_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_VISIUM_HNE\\SQUIDPY_VISIUM_HNE_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "spatial_domain_benchmark",
    "modality": "spatial_transcriptomics_visium_spot",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "SQUIDPY_IMC",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_IMC\\SQUIDPY_IMC_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\SQUIDPY_IMC\\SQUIDPY_IMC_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "cross_modality_stress_test",
    "modality": "spatial_proteomics_single_cell",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE240015_VISIUM_THYMUS_DOMAIN",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE240015_VISIUM_THYMUS_DOMAIN\\GEO_GSE240015_VISIUM_THYMUS_DOMAIN_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE240015_VISIUM_THYMUS_DOMAIN\\GEO_GSE240015_VISIUM_THYMUS_DOMAIN_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "geo_direct_benchmark",
    "modality": "GEO_direct_spatial_transcriptomics",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE284005_MERSCOPE_MS",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE284005_MERSCOPE_MS\\GEO_GSE284005_MERSCOPE_MS_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE284005_MERSCOPE_MS\\GEO_GSE284005_MERSCOPE_MS_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "geo_direct_benchmark",
    "modality": "GEO_direct_spatial_transcriptomics",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE327581_COSMX_AD_BRAIN",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE327581_COSMX_AD_BRAIN\\GEO_GSE327581_COSMX_AD_BRAIN_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE327581_COSMX_AD_BRAIN\\GEO_GSE327581_COSMX_AD_BRAIN_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "geo_direct_benchmark",
    "modality": "GEO_direct_spatial_transcriptomics",
    "max_folds": 5,
    "top_markers_per_label": 20
  },
  {
    "dataset_id": "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR",
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_preview_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_preview_metadata.tsv",
    "label_col": "label",
    "group_col": "fov_group",
    "cell_id_col": "cell_id",
    "x_col": "x",
    "y_col": "y",
    "role": "geo_direct_benchmark",
    "modality": "GEO_direct_spatial_transcriptomics",
    "max_folds": 5,
    "top_markers_per_label": 20
  }
]
```
