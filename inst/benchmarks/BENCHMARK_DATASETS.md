# Multi-Dataset Benchmark Expansion

This folder now contains one manually curated disease GEO benchmark, four
additional GEO-direct spatial benchmarks, and seven Squidpy-derived spatial
datasets converted into a common preview format.

The common preview contract is:

- feature-by-cell expression matrix: `*_preview_expression.tsv.gz`
- cell metadata with `cell_id`, `x`, `y`, `label`, and `fov_group`:
  `*_preview_metadata.tsv`
- source and shape summary: `*_summary.json`
- dataset-specific manifest: `*_manifest.md`

## Current Dataset Panel

| dataset | modality | context | cells/spots | features | labels | preview | role |
|---|---|---|---:|---:|---:|---:|---|
| GSE202623 | MERFISH RNA | mouse demyelinating lesion | 280,176 | 287 | manual labels | 2,485 lesion preview | primary disease benchmark |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | Visium RNA | mouse thymus aging spatial domains | 3,910 | 2,000 | 13 | 3,910 x 2,000 | GEO-direct spatial-domain benchmark |
| GEO_GSE284005_MERSCOPE_MS | MERSCOPE/MERFISH RNA | human multiple sclerosis lesion | 401,794 | 500 | 38 | 9,393 x 500 | GEO-direct primary benchmark |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | MERSCOPE/MERFISH RNA | adult human pancreas vascular populations | 24,222 | 300 | 4 | 2,400 x 300 | GEO-direct primary benchmark |
| GEO_GSE327581_COSMX_AD_BRAIN | CosMx SMI RNA | 3xTg-AD mouse brain after fecal microbiota transplant | 738,722 | 1,207 | 55 | 5,500 x 1,207 | GEO-direct primary benchmark |
| SQUIDPY_SEQFISH | seqFISH RNA | mouse organogenesis | 19,416 | 351 | 21 | 5,389 x 351 | primary RNA benchmark |
| SQUIDPY_MERFISH | MERFISH RNA | mouse hypothalamus/preoptic region | 73,655 | 161 | 15 | 4,030 x 161 | primary RNA benchmark |
| SQUIDPY_SLIDESEQV2 | Slide-seqV2 RNA | mouse hippocampus | 41,786 | 4,000 | 14 | 2,800 x 1,500 | secondary RNA benchmark |
| SQUIDPY_VISIUM_FLUO | Visium RNA | fluorescent mouse brain | 2,800 | 16,562 | 15 | 2,753 x 2,000 | spatial domain benchmark |
| SQUIDPY_VISIUM_HNE | Visium RNA | H&E mouse brain | 2,688 | 18,078 | 15 | 2,688 x 2,000 | spatial domain benchmark |
| SQUIDPY_MIBITOF | MIBI-TOF protein | carcinoma | 3,309 | 36 | 8 | 2,012 x 36 | cross-modality stress test |
| SQUIDPY_IMC | IMC protein | breast cancer | 4,668 | 34 | 11 | 1,744 x 34 | cross-modality stress test |

## How To Regenerate

The data-preparation scripts are included in the manuscript supplementary
archive because they depend on large public GEO supplements and hosted example
data files.

The raw Squidpy `.h5ad` files and direct GEO supplements are not bundled in the
R package repository. Converted preview files are stored one directory per
dataset in the full benchmark workspace.

## Publication Use

Use the panel in tiers:

1. Main application-note evidence:
   GSE202623, GEO_GSE284005_MERSCOPE_MS, GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR,
   GEO_GSE327581_COSMX_AD_BRAIN, SQUIDPY_SEQFISH, and SQUIDPY_MERFISH.
2. Secondary robustness:
   SQUIDPY_SLIDESEQV2, because it is bead/spot-like and has broader gene
   coverage.
3. Spatial-domain benchmarks:
   GEO_GSE240015_VISIUM_THYMUS_DOMAIN, SQUIDPY_VISIUM_FLUO, and
   SQUIDPY_VISIUM_HNE. These evaluate region/domain consistency rather than
   single-cell type annotation.
4. Cross-modality stress tests:
   SQUIDPY_MIBITOF and SQUIDPY_IMC. These should not be used to claim RNA
   annotation superiority, but they can test whether the audit framework
   generalizes to marker-like spatial protein panels.

## Next Benchmark Step

This step was implemented in the manuscript supplementary benchmark runner.

The runner learns marker-like feature priors and spatial compatibility only from
training spatial blocks, then evaluates held-out blocks with:

- marker-only
- marker + simple spatial smoothing
- marker + simple spatial smoothing on random graph
- marker + learned neighborhood
- marker + null-corrected context-specific neighborhood
- learned neighborhood on random graph
- learned neighborhood with permuted prior

Key outputs:

- `MULTIDATASET_BLOCKED_BENCHMARK_summary.csv`
- `MULTIDATASET_BLOCKED_BENCHMARK_pairwise.csv`
- `MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv`
- `MULTIDATASET_BLOCKED_BENCHMARK.md`

Current guardrail result after adding GEO-direct datasets and the null-corrected context-specific
neighborhood score:

| dataset | context-specific | learned context | smoothing context | interpretation |
|---|---|---|---|---|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | fail | fail | pass | spatial-domain smoothing signal |
| GEO_GSE284005_MERSCOPE_MS | fail | fail | fail | context not specific after null controls |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | fail | fail | fail | context not specific after null controls |
| GEO_GSE327581_COSMX_AD_BRAIN | fail | pass | fail | learned neighborhood signal |
| GSE202623_LESION | fail | pass | fail | learned neighborhood signal |
| SQUIDPY_SEQFISH | fail | pass | pass | learned neighborhood plus smoothing signal |
| SQUIDPY_MERFISH | fail | fail | fail | context not specific after null controls |
| SQUIDPY_SLIDESEQV2 | fail | fail | fail | tiny context-specific gain, below threshold |
| SQUIDPY_MIBITOF | fail | fail | fail | context not specific after null controls |
| SQUIDPY_VISIUM_FLUO | fail | fail | pass | spatial-domain smoothing signal |
| SQUIDPY_VISIUM_HNE | fail | fail | fail | context not specific after null controls |
| SQUIDPY_IMC | fail | fail | fail | context not specific after null controls |

This supports a cautious application-note claim: NicheTypeR is a useful
framework for blocked validation and context audit. Direct GEO expansion now
contains negative, positive, and domain-control cases: two GEO-direct datasets
do not show a specific learned context gain, the CosMx AD brain dataset passes
the learned-neighborhood guardrail, and the thymus Visium domain benchmark is
best explained by simple spatial smoothing. The first null-corrected
context-specific residual remains useful as a stricter audit statistic, but it
does not yet produce stable classification gains. More method development is
needed before this becomes an original-methods paper.

## Runtime and Memory Benchmark

The computational-footprint benchmark is implemented in the manuscript
supplementary benchmark runner.

It measures one blocked fold per preview dataset in isolated Python child
processes and records wall-clock time, process RSS, dataset dimensions and
stage-level timings. Current outputs are:

- `RUNTIME_MEMORY_BENCHMARK_dataset_summary.csv`
- `RUNTIME_MEMORY_BENCHMARK_stage_times.csv`
- `RUNTIME_MEMORY_BENCHMARK_report.json`
- `RUNTIME_MEMORY_BENCHMARK.md`

Current run summary: 12 datasets, 178.4 seconds of summed dataset-stage wall
time, 12.0 seconds median per dataset and 385.3 MB maximum observed RSS. The
largest preview dataset, GEO_GSE284005_MERSCOPE_MS, contained 9,393 cells and
500 features and completed in 37.4 seconds with 314.9 MB peak RSS. These
measurements support a lightweight computational-footprint claim for the
preview workflow. They should not be interpreted as proof that NicheTypeR is
faster than external reference-mapping, deconvolution or deep-learning tools,
which solve related but non-identical tasks.

## Source Notes

The Squidpy-derived datasets are downloaded from the official scverse example
data host and have matching Squidpy dataset documentation pages:

- `squidpy.datasets.seqfish`
- `squidpy.datasets.merfish`
- `squidpy.datasets.slideseqv2`
- `squidpy.datasets.visium_fluo_adata`
- `squidpy.datasets.visium_hne_adata`
- `squidpy.datasets.mibitof`
- `squidpy.datasets.imc`
