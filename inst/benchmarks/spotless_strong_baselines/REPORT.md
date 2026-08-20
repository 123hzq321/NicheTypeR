# Spotless imaging-derived gold-standard validation

## Scope

Two official Spotless seqFISH+ gold-standard tasks were reconstructed from the original Eng et al. single-cell imaging files: cortex/SVZ and olfactory bulb. Each contains seven FOVs and 63 Visium-like spots with exactly known cell-type composition.

This evaluates a hypothesis-aligned marker / learned-neighborhood / CSAE-like reference implementation. Four stronger expression-only classifiers (regularized multinomial logistic regression, linear SVM, PCA-kNN, and ExtraTrees) and a native SingleR baseline were added, and the spatial modules were also attached directly to the logistic model. It is not a locked-software run of a released NicheTypeR package, and Spotless is a spot-composition benchmark rather than an orthogonal protein-imaging assay.

## Leakage controls

- Every cell prediction is leave-one-FOV-out: marker signatures, expression classifiers, PCA transforms, and label-compatibility priors are learned from the other six FOVs.
- Native SingleR is run fold-by-fold in R: the six training FOVs form the reference and the held-out FOV is never included in the reference.
- Ground-truth cell labels and spot compositions from the held-out FOV are used only for evaluation.
- Random-neighbor and permuted-compatibility controls test specificity.
- In addition to fixed 50:50 fusion across all cells, a pre-specified gated analysis changes only the lowest marker-margin quartile in each held-out FOV; its null controls use the identical gate.
- Nested logistic-spatial models select their spatial weight only inside the six outer-training FOVs. The candidate grid includes weight 0, and a positive spatial weight is accepted only when the inner-training objective improves over logistic alone.
- Paired inference first collapses spot effects within each FOV, leaving seven spatially independent blocks per dataset.

## Results

| dataset | model | cells | labels | spots | accuracy | macro F1 | RMSE | mean JSD | AUPR | guardrail |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seqFISH+ cortex/SVZ | marker_only | 861 | 11 | 63 | 0.318 | 0.297 | 0.202 | 0.490 | 0.523 | n/a |
| seqFISH+ cortex/SVZ | logreg_only | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | n/a |
| seqFISH+ cortex/SVZ | linear_svm | 861 | 11 | 63 | 0.626 | 0.483 | 0.097 | 0.163 | 0.767 | n/a |
| seqFISH+ cortex/SVZ | pca_knn | 861 | 11 | 63 | 0.683 | 0.503 | 0.104 | 0.148 | 0.764 | n/a |
| seqFISH+ cortex/SVZ | extra_trees | 861 | 11 | 63 | 0.692 | 0.545 | 0.114 | 0.146 | 0.763 | n/a |
| seqFISH+ cortex/SVZ | singler_native | 861 | 11 | 63 | 0.718 | 0.534 | 0.084 | 0.106 | 0.842 | n/a |
| seqFISH+ cortex/SVZ | spatial_smoothing | 861 | 11 | 63 | 0.295 | 0.268 | 0.223 | 0.507 | 0.570 | n/a |
| seqFISH+ cortex/SVZ | spatial_smoothing_random_graph | 861 | 11 | 63 | 0.286 | 0.274 | 0.216 | 0.516 | 0.540 | n/a |
| seqFISH+ cortex/SVZ | learned_neighborhood | 861 | 11 | 63 | 0.264 | 0.264 | 0.223 | 0.564 | 0.439 | no |
| seqFISH+ cortex/SVZ | learned_random_graph | 861 | 11 | 63 | 0.283 | 0.282 | 0.210 | 0.546 | 0.440 | n/a |
| seqFISH+ cortex/SVZ | learned_permuted_prior | 861 | 11 | 63 | 0.289 | 0.281 | 0.219 | 0.513 | 0.488 | n/a |
| seqFISH+ cortex/SVZ | context_specific | 861 | 11 | 63 | 0.279 | 0.276 | 0.220 | 0.559 | 0.422 | no |
| seqFISH+ cortex/SVZ | gated_spatial_smoothing | 861 | 11 | 63 | 0.308 | 0.285 | 0.213 | 0.501 | 0.552 | n/a |
| seqFISH+ cortex/SVZ | gated_spatial_smoothing_random_graph | 861 | 11 | 63 | 0.305 | 0.288 | 0.209 | 0.504 | 0.537 | n/a |
| seqFISH+ cortex/SVZ | gated_learned_neighborhood | 861 | 11 | 63 | 0.300 | 0.287 | 0.209 | 0.506 | 0.502 | no |
| seqFISH+ cortex/SVZ | gated_learned_random_graph | 861 | 11 | 63 | 0.302 | 0.294 | 0.207 | 0.523 | 0.491 | n/a |
| seqFISH+ cortex/SVZ | gated_learned_permuted_prior | 861 | 11 | 63 | 0.312 | 0.299 | 0.208 | 0.501 | 0.522 | n/a |
| seqFISH+ cortex/SVZ | gated_context_specific | 861 | 11 | 63 | 0.307 | 0.292 | 0.206 | 0.504 | 0.510 | no |
| seqFISH+ cortex/SVZ | logreg_learned_neighborhood | 861 | 11 | 63 | 0.343 | 0.317 | 0.200 | 0.446 | 0.508 | no |
| seqFISH+ cortex/SVZ | logreg_learned_random_graph | 861 | 11 | 63 | 0.332 | 0.324 | 0.194 | 0.453 | 0.460 | n/a |
| seqFISH+ cortex/SVZ | logreg_learned_permuted_prior | 861 | 11 | 63 | 0.305 | 0.287 | 0.211 | 0.478 | 0.494 | n/a |
| seqFISH+ cortex/SVZ | logreg_context_specific | 861 | 11 | 63 | 0.315 | 0.315 | 0.200 | 0.478 | 0.452 | no |
| seqFISH+ cortex/SVZ | gated_logreg_learned_neighborhood | 861 | 11 | 63 | 0.373 | 0.341 | 0.175 | 0.365 | 0.613 | no |
| seqFISH+ cortex/SVZ | gated_logreg_learned_random_graph | 861 | 11 | 63 | 0.376 | 0.348 | 0.174 | 0.375 | 0.586 | n/a |
| seqFISH+ cortex/SVZ | gated_logreg_learned_permuted_prior | 861 | 11 | 63 | 0.370 | 0.338 | 0.174 | 0.368 | 0.610 | n/a |
| seqFISH+ cortex/SVZ | gated_logreg_context_specific | 861 | 11 | 63 | 0.379 | 0.356 | 0.175 | 0.370 | 0.592 | no |
| seqFISH+ cortex/SVZ | nested_logreg_learned_neighborhood | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | no |
| seqFISH+ cortex/SVZ | nested_logreg_learned_random_graph | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | n/a |
| seqFISH+ cortex/SVZ | nested_logreg_learned_permuted_prior | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | n/a |
| seqFISH+ cortex/SVZ | nested_logreg_context_specific | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | no |
| seqFISH+ cortex/SVZ | nested_gated_logreg_learned_neighborhood | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | no |
| seqFISH+ cortex/SVZ | nested_gated_logreg_learned_random_graph | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | n/a |
| seqFISH+ cortex/SVZ | nested_gated_logreg_learned_permuted_prior | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | n/a |
| seqFISH+ cortex/SVZ | nested_gated_logreg_context_specific | 861 | 11 | 63 | 0.691 | 0.547 | 0.088 | 0.123 | 0.822 | no |
| seqFISH+ olfactory bulb | marker_only | 2026 | 8 | 62 | 0.364 | 0.381 | 0.191 | 0.333 | 0.704 | n/a |
| seqFISH+ olfactory bulb | logreg_only | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | n/a |
| seqFISH+ olfactory bulb | linear_svm | 2026 | 8 | 62 | 0.664 | 0.684 | 0.091 | 0.073 | 0.942 | n/a |
| seqFISH+ olfactory bulb | pca_knn | 2026 | 8 | 62 | 0.754 | 0.761 | 0.072 | 0.052 | 0.914 | n/a |
| seqFISH+ olfactory bulb | extra_trees | 2026 | 8 | 62 | 0.785 | 0.801 | 0.070 | 0.040 | 0.954 | n/a |
| seqFISH+ olfactory bulb | singler_native | 2026 | 8 | 62 | 0.725 | 0.755 | 0.069 | 0.044 | 0.942 | n/a |
| seqFISH+ olfactory bulb | spatial_smoothing | 2026 | 8 | 62 | 0.347 | 0.381 | 0.206 | 0.358 | 0.712 | n/a |
| seqFISH+ olfactory bulb | spatial_smoothing_random_graph | 2026 | 8 | 62 | 0.337 | 0.366 | 0.208 | 0.381 | 0.666 | n/a |
| seqFISH+ olfactory bulb | learned_neighborhood | 2026 | 8 | 62 | 0.307 | 0.329 | 0.219 | 0.405 | 0.646 | no |
| seqFISH+ olfactory bulb | learned_random_graph | 2026 | 8 | 62 | 0.309 | 0.326 | 0.207 | 0.402 | 0.642 | n/a |
| seqFISH+ olfactory bulb | learned_permuted_prior | 2026 | 8 | 62 | 0.330 | 0.346 | 0.211 | 0.390 | 0.678 | n/a |
| seqFISH+ olfactory bulb | context_specific | 2026 | 8 | 62 | 0.322 | 0.345 | 0.209 | 0.385 | 0.655 | no |
| seqFISH+ olfactory bulb | gated_spatial_smoothing | 2026 | 8 | 62 | 0.357 | 0.382 | 0.198 | 0.349 | 0.707 | n/a |
| seqFISH+ olfactory bulb | gated_spatial_smoothing_random_graph | 2026 | 8 | 62 | 0.350 | 0.374 | 0.200 | 0.358 | 0.683 | n/a |
| seqFISH+ olfactory bulb | gated_learned_neighborhood | 2026 | 8 | 62 | 0.345 | 0.366 | 0.202 | 0.363 | 0.668 | no |
| seqFISH+ olfactory bulb | gated_learned_random_graph | 2026 | 8 | 62 | 0.346 | 0.365 | 0.199 | 0.366 | 0.672 | n/a |
| seqFISH+ olfactory bulb | gated_learned_permuted_prior | 2026 | 8 | 62 | 0.357 | 0.376 | 0.200 | 0.364 | 0.691 | n/a |
| seqFISH+ olfactory bulb | gated_context_specific | 2026 | 8 | 62 | 0.349 | 0.370 | 0.197 | 0.352 | 0.681 | no |
| seqFISH+ olfactory bulb | logreg_learned_neighborhood | 2026 | 8 | 62 | 0.387 | 0.383 | 0.188 | 0.304 | 0.770 | no |
| seqFISH+ olfactory bulb | logreg_learned_random_graph | 2026 | 8 | 62 | 0.347 | 0.338 | 0.185 | 0.324 | 0.735 | n/a |
| seqFISH+ olfactory bulb | logreg_learned_permuted_prior | 2026 | 8 | 62 | 0.343 | 0.332 | 0.195 | 0.346 | 0.700 | n/a |
| seqFISH+ olfactory bulb | logreg_context_specific | 2026 | 8 | 62 | 0.356 | 0.357 | 0.197 | 0.336 | 0.732 | no |
| seqFISH+ olfactory bulb | gated_logreg_learned_neighborhood | 2026 | 8 | 62 | 0.432 | 0.422 | 0.169 | 0.258 | 0.820 | no |
| seqFISH+ olfactory bulb | gated_logreg_learned_random_graph | 2026 | 8 | 62 | 0.422 | 0.415 | 0.167 | 0.261 | 0.836 | n/a |
| seqFISH+ olfactory bulb | gated_logreg_learned_permuted_prior | 2026 | 8 | 62 | 0.427 | 0.413 | 0.167 | 0.259 | 0.808 | n/a |
| seqFISH+ olfactory bulb | gated_logreg_context_specific | 2026 | 8 | 62 | 0.428 | 0.414 | 0.166 | 0.251 | 0.836 | no |
| seqFISH+ olfactory bulb | nested_logreg_learned_neighborhood | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | no |
| seqFISH+ olfactory bulb | nested_logreg_learned_random_graph | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | n/a |
| seqFISH+ olfactory bulb | nested_logreg_learned_permuted_prior | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | n/a |
| seqFISH+ olfactory bulb | nested_logreg_context_specific | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | no |
| seqFISH+ olfactory bulb | nested_gated_logreg_learned_neighborhood | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | no |
| seqFISH+ olfactory bulb | nested_gated_logreg_learned_random_graph | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | n/a |
| seqFISH+ olfactory bulb | nested_gated_logreg_learned_permuted_prior | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | n/a |
| seqFISH+ olfactory bulb | nested_gated_logreg_context_specific | 2026 | 8 | 62 | 0.686 | 0.768 | 0.087 | 0.055 | 0.953 | no |

A learned-neighborhood pass requires better FOV-level median Pearson correlation and JSD than its matched expression-only, random-neighbor, and permuted-prior controls, with two-sided Wilcoxon p < 0.05 for both endpoints. CSAE-like must additionally beat learned-neighborhood. Gated models are judged only against controls using the identical low-margin gate.

## Interpretation

Fixed learned-neighborhood passed in **0/2** datasets and fixed CSAE-like in **0/2**. Restricting intervention to the lowest marker-margin quartile did not reverse the result: gated learned-neighborhood passed in **0/2** and gated CSAE-like in **0/2**.

Against the stronger paired logistic baseline, fixed learned-neighborhood passed in **0/2** and fixed CSAE-like in **0/2**; low-margin gated versions passed in **0/2** and **0/2**, respectively. These paired results are the relevant test of incremental spatial value after a competent expression classifier, while the four expression-only models show how sensitive the conclusion is to baseline strength.

Nested weight selection provides an explicit rejection mechanism: learned-neighborhood passed in **0/2** datasets and CSAE-like in **0/2** after selecting the logistic-spatial weight inside the outer training FOVs. The identical low-margin nested gate passed in **0/2** and **0/2** datasets, respectively. Across all held-out FOVs and nested families, positive spatial weights were selected in **0/56** selections; the remaining selections automatically reverted to the logistic-only baseline.

## Limitations

- The seqFISH+ cell-type labels were derived from the same targeted transcript measurements using clustering and marker interpretation. The spot composition is exact, but the cell-type naming is not an independent protein/pathology truth.
- This run covers 2/3 Spotless gold standards. The STARmap task is only distributed inside the official 6.9 GB sequential archive and was not included in this compact reconstruction.
- There are seven FOV blocks per dataset, so power for strict dual-endpoint tests is limited.
- Results establish behavior of the reference mechanism, not final software performance.

## Reproducibility

- `spotless_summary.csv`: aggregate cell and spot metrics.
- `spotless_pairwise_comparisons.csv`: FOV-block paired tests and bootstrap intervals.
- `spotless_spot_metrics.csv`: per-spot Pearson r, JSD, and RMSE.
- `spotless_crossfit_calls_*.csv.gz`: all held-out cell predictions.
- `spotless_spot_compositions_*.csv.gz`: true and predicted spot compositions.
- `spotless_nested_weight_selection.csv`: inner-fold candidate weights, objectives, and selected weights.
- `spotless_selected_markers.csv.gz`: fold-specific markers.
- `data_manifest.csv` and `run_metadata.json`: source hashes, parameters, and coverage.
