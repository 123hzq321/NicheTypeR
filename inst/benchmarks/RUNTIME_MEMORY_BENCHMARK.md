# Runtime and Memory Benchmark

This report measures the preview benchmark implementation used for the
NicheTypeR multi-dataset analysis. It is a computational-footprint
benchmark for the current reproducible benchmark workflow, not a claim
that NicheTypeR is faster than all external annotation tools.

## Dependency Footprint

- package files: 36
- package bytes: 114,969
- R source files: 21
- R source bytes: 74,511
- hard Imports recorded in DESCRIPTION: stats, graphics, utils
- optional packages in Suggests: FNN, SeuratObject, SpatialExperiment, SummarizedExperiment

## One-Fold Runtime Summary

- datasets measured: 12
- total wall time across datasets: 178.38 s
- median wall time per dataset: 12.02 s
- maximum observed RSS: 385.3 MB

| dataset | cells | features | labels | edges | wall time s | peak RSS MB |
|---|---:|---:|---:|---:|---:|---:|
| SQUIDPY_MIBITOF | 2,012 | 36 | 8 | 20,120 | 5.46 | 158.0 |
| SQUIDPY_IMC | 1,744 | 34 | 11 | 17,440 | 7.35 | 158.4 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | 2,400 | 300 | 4 | 24,000 | 7.36 | 176.2 |
| SQUIDPY_SLIDESEQV2 | 2,800 | 1,500 | 14 | 28,000 | 9.55 | 275.9 |
| SQUIDPY_VISIUM_HNE | 2,688 | 2,000 | 15 | 26,880 | 10.19 | 307.4 |
| GSE202623_LESION | 2,485 | 287 | 8 | 24,840 | 10.97 | 179.9 |
| SQUIDPY_VISIUM_FLUO | 2,753 | 2,000 | 15 | 27,530 | 13.07 | 315.9 |
| SQUIDPY_MERFISH | 4,030 | 161 | 15 | 40,300 | 13.91 | 182.6 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 3,910 | 2,000 | 13 | 39,100 | 14.76 | 370.1 |
| SQUIDPY_SEQFISH | 5,389 | 351 | 21 | 53,890 | 22.14 | 219.7 |
| GEO_GSE327581_COSMX_AD_BRAIN | 5,500 | 1,207 | 55 | 55,000 | 26.25 | 385.3 |
| GEO_GSE284005_MERSCOPE_MS | 9,393 | 500 | 38 | 93,930 | 37.38 | 314.9 |

## Stage-Level Outputs

- `RUNTIME_MEMORY_BENCHMARK_dataset_summary.csv`
- `RUNTIME_MEMORY_BENCHMARK_stage_times.csv`
- `RUNTIME_MEMORY_BENCHMARK_report.json`

## Interpretation

The package itself is dependency-light: the R package imports only base or
recommended R packages (`stats`, `graphics`, and `utils`), while Seurat and
SpatialExperiment support is optional. The measured benchmark completes
one blocked fold across all preview datasets on a desktop Python
environment with sub-second to low-tens-of-seconds per dataset runtimes.
However, these measurements should be framed as computational-footprint
evidence, not as a direct speed superiority claim over SingleR, CellTypist,
Azimuth, Tangram, cell2location, or other non-equivalent tools.
