# Benchmark Snapshot

This directory contains the benchmark registry and summary artifacts used for
the Bioinformatics application-note submission snapshot.

The full raw and processed spatial transcriptomics matrices are not bundled in
the R package repository because several source files are large public GEO or
hosted example-data objects. Dataset sources and accessions are recorded in:

- `BENCHMARK_DATASETS.md`
- `DATASET_REGISTRY.csv`
- `GEO_DIRECT_DATASETS.md`

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

For an installation-free smoke test, use the simulated-data workflow:

```r
source(system.file("examples", "smoke_workflow.R", package = "NicheTypeR"))
```
