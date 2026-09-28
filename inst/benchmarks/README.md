# Benchmark Snapshot

This directory contains the benchmark registry, reproducibility scripts and
summary artifacts used for the NicheTypeR 0.0.7 Bioinformatics submission
snapshot (2026-09-28).

The full raw and processed spatial transcriptomics matrices are not bundled in
the R package repository because several source files are large public GEO or
hosted example-data objects. Dataset sources and accessions are recorded in:

- `BENCHMARK_DATASETS.md`
- `DATASET_REGISTRY.csv`
- `GEO_DIRECT_DATASETS.md`
- `BENCHMARK_INDEPENDENCE_AND_TRUTH.md`

The main blocked-validation result tables are:

- `MULTIDATASET_BLOCKED_BENCHMARK.md`
- `MULTIDATASET_BLOCKED_BENCHMARK_summary.csv`
- `MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv`
- `MULTIDATASET_BLOCKED_BENCHMARK_pairwise.csv`
- `MULTIDATASET_BLOCKED_BENCHMARK_per_label.csv`

The runtime and memory snapshot is:

- `RUNTIME_MEMORY_BENCHMARK.md`
- `RUNTIME_MEMORY_BENCHMARK_dataset_summary.csv`
- `RUNTIME_MEMORY_BENCHMARK_stage_times.csv`

The expanded-scale stress-test snapshot is:

- `EXPANDED_SCALE_DATASETS.csv`
- `EXPANDED_SCALE_LEAN_BENCHMARK.md`
- `EXPANDED_SCALE_LEAN_BENCHMARK_summary.csv`
- `EXPANDED_SCALE_LEAN_BENCHMARK_guardrail.csv`
- `EXPANDED_SCALE_LEAN_BENCHMARK_pairwise.csv`
- `EXPANDED_SCALE_LEAN_BENCHMARK_per_label.csv`

The current expanded-scale run covers 56 configurations and 1,226,225
configuration-level cells or spots. Across the complete primary snapshot, 68
configurations correspond to 61 named public sources, 59 known publication
families and 1,239,332 source-deduplicated observations. A separate 39-source
cluster-only SODB panel brings processing coverage to 100 source IDs but is
excluded from the efficacy denominator. `BENCHMARK_INDEPENDENCE_AND_TRUTH.md`
records this accounting and explains that held-out author or curator-provided
labels are reproducible reference labels rather than flawless biological truth.

The label-task audit snapshot is:

- `LABEL_TASK_BENCHMARK.md`
- `LABEL_TASK_BENCHMARK.csv`
- `LABEL_TASK_BENCHMARK_summary.csv`
- `LABEL_TASK_BENCHMARK_support_bins.csv`

It summarizes 1,283 dataset-label validation tasks across the preview and
expanded benchmark configurations. These tasks increase audit granularity but
are not counted as independent datasets.

The threshold-sensitivity and tiered-support snapshot is:

- `THRESHOLD_SENSITIVITY_AND_TIERS.md`
- `THRESHOLD_SENSITIVITY_dataset_level.csv`
- `THRESHOLD_SENSITIVITY_dataset_tiers.csv`
- `THRESHOLD_SENSITIVITY_label_tasks.csv`
- `THRESHOLD_SENSITIVITY_label_task_tiers.csv`
- `figure_threshold_sensitivity.svg`
- `figure_threshold_sensitivity.eps`

It keeps the strict dataset-level result as the primary claim, but adds
exploratory sensitivity summaries. Learned-neighborhood evidence passes the
strict guardrail in 9 of 68 configurations and CSAE residual evidence in 1 of
68. The CSAE event is a tumour/non-tumour spatial-domain task rather than a
cell-type benchmark. At the directional dataset-level cutoff \(\Delta>0\), the
corresponding counts are 24 of 68 and 7 of 68. At dataset-label resolution,
learned-neighborhood evidence is positive in 425 of 1,283 tasks and CSAE
residual evidence is positive in 209 of 1,283.

Source accounting and the 100-source portfolio are:

- `CONFIGURATION_SOURCE_MAP.csv`
- `SOURCE_INDEPENDENCE_REGISTRY.csv`
- `SOURCE_INDEPENDENCE_REPORT.md`
- `HUNDRED_SOURCE_PORTFOLIO.md`
- `HUNDRED_SOURCE_PORTFOLIO.csv`

The portfolio separates 61 label-bearing validation sources from 39
cluster-only calibration sources. The latter are reported in
`SODB_CALIBRATION_LEAN_BENCHMARK.md` and are never added to the primary
efficacy denominator. The 20 label-bearing SODB configurations are reported in
`SODB_SCALE_LEAN_BENCHMARK.md`.

The fold-label stability audit is:

- `FOLD_LABEL_TASK_BENCHMARK.md`
- `FOLD_LABEL_TASK_BENCHMARK.csv`
- `FOLD_LABEL_TASK_BENCHMARK_summary.csv`
- `FOLD_LABEL_TASK_BENCHMARK_reproducibility.csv`
- `FOLD_LABEL_TASK_BENCHMARK_reproducibility_summary.csv`

It summarizes 2,984 eligible held-out fold-label validation tasks, including 54
dataset-label tasks with reproducible learned-neighborhood support and 12 with
reproducible CSAE-residual support across at least two folds.

The local GEO ingestion audit is:

- `LOCAL_GEO_INGESTION_AUDIT.md`
- `LOCAL_GEO_INGESTION_AUDIT.csv`
- `LOCAL_GEO_INGESTION_AUDIT_summary.csv`

Reference-style and audit-event add-ons are:

- `REFERENCE_PROFILE_BASELINE.md`
- `REFERENCE_PROFILE_BASELINE_summary.csv`
- `REFERENCE_PROFILE_BASELINE_pairwise.csv`
- `SEURAT_LABEL_TRANSFER_BASELINE.md`
- `SEURAT_LABEL_TRANSFER_BASELINE_summary.csv`
- `SEURAT_LABEL_TRANSFER_BASELINE_pairwise.csv`
- `SEURAT_LABEL_TRANSFER_BASELINE_status.csv`
- `EXTERNAL_METHOD_BASELINES.md`
- `EXTERNAL_METHOD_BASELINES_summary.csv`
- `EXTERNAL_METHOD_BASELINES_pairwise.csv`
- `EXTERNAL_METHOD_BASELINES_status.csv`
- `EXTERNAL_METHOD_AUDIT_VALIDITY.md`
- `EXTERNAL_METHOD_AUDIT_VALIDITY_summary.csv`
- `EXTERNAL_METHOD_AUDIT_VALIDITY_thresholds.csv`
- `INCREMENTAL_AUDIT_BENCHMARK.md`
- `INCREMENTAL_AUDIT_BENCHMARK_summary.csv`
- `INCREMENTAL_AUDIT_BENCHMARK_dataset_cluster_ci.csv`
- `ANNOTATION_AUDIT_CASE_STUDY.md`
- `ANNOTATION_AUDIT_CASE_STUDY_summary.csv`
- `ANNOTATION_AUDIT_CASE_STUDY_examples.csv`

The external-method baseline snapshot contains one official package comparison
(Seurat label transfer) plus three algorithmic proxy mappers used as
installation-independent stress tests of the external annotation audit
interface. The proxy mappers are explicitly not claimed to be official SingleR,
scmap or CellTypist runs.

The incremental audit benchmark separates generic classifier uncertainty from
NicheTypeR-specific conflict features. Raw margin is the strongest current
wrong-call risk score: call-level margin AUROC is 0.743 versus 0.738 after
adding conflict flags, and unique-cell margin AUROC is 0.879 versus 0.859 after
adding conflict flags. These results should be interpreted as a negative
incremental audit result, not as evidence that CSAE or multi-layer conflicts
outperform a raw uncertainty baseline.

The imaging-derived gold-standard validation snapshot is stored in:

- `spotless_strong_baselines/REPORT.md`
- `spotless_strong_baselines/run_spotless_seqfish_gold_validation_v2.py`
- `spotless_strong_baselines/spotless_summary.csv`
- `spotless_strong_baselines/spotless_pairwise_comparisons.csv`
- `spotless_strong_baselines/spotless_nested_weight_selection.csv`

It covers two official Spotless seqFISH+ tasks with leave-one-FOV validation,
strong expression-only baselines and native R/Bioconductor SingleR. Nested
logistic-spatial fusion selected positive spatial weight in 0 of 56 fold/family
selections, so the accepted nested models revert to logistic-only.

For an installation-free smoke test, use the simulated-data workflow:

```r
source(system.file("examples", "smoke_workflow.R", package = "NicheTypeR"))
```

The scripts used to build the blocked, expanded, label-task, fold-label,
threshold-sensitivity, external-method and manuscript-figure outputs are copied
under `scripts/`. `SHA256SUMS.csv` records hashes for the released benchmark
artifacts and scripts, and `SESSION_INFO.txt` records the R and Python runtime
used for the release check. Large public expression matrices and the
198-million-byte expanded call table are intentionally not bundled; they are
regenerated from the public sources and scripts above.
