# NicheTypeR

`NicheTypeR` is a lightweight research package for interpretable
context-aware annotation auditing in spatial transcriptomics.

The goal is not to replace biological review. The goal is to make review more
explicit:

```text
cell type call =
  marker evidence
  + reference similarity
  + pathway / metabolic program support
  + spatial niche compatibility
  + ligand-receptor consistency
  - negative marker conflicts
```

Instead of returning only a label, the package returns a label, confidence,
margin, and a conflict reason when evidence sources disagree.

## Why this exists

Traditional marker-based annotation often asks:

> Does this cell or cluster express the expected markers?

`NicheTypeR` asks a broader, more cautious question:

> Is this candidate identity consistent with its expression, function, spatial
> neighborhood, and local interaction context?

That framing is useful for spatial transcriptomics, where cell identity and
tissue architecture should often agree. The package should not be presented as a
state-of-the-art classifier yet; the current evidence supports an auditable
evidence-fusion layer and conflict reporter.

## Current status

This is a submission-oriented research software prototype. It currently supports
base R matrices and data frames:

- gene-by-cell expression matrix
- cell coordinate table
- marker database
- pathway gene sets
- spatial niche priors
- ligand-receptor priors

Basic adapters for `Seurat` and `SpatialExperiment` are included. The intended
publication framing is a Bioinformatics-style Application Note: an auditable
software framework with conservative benchmarking, not a universal
state-of-the-art cell type classifier.

The current benchmark snapshot uses a tiered 100-source portfolio. Primary
label-bearing validation contains 61 named public sources represented by 68
configurations and 1,239,332 source-deduplicated observations. A separate 39
source panel with repository-standardized Leiden clusters is used only for
operational and matched-null calibration. The 100-source count is therefore a
processing-coverage statement, not a claim of 100 independent gold-standard
cohorts. Held-out author or curator-provided labels remain reference labels for
discordance detection, while audit conflicts are hypotheses for re-adjudication.

## Installation

```r
install.packages("remotes")
remotes::install_github("123hzq321/NicheTypeR", upgrade = "never")
```

For a local checkout:

```r
remotes::install_local(".", upgrade = "never")
```

## Lightweight footprint

The core package is dependency-light by design. Hard imports are limited to
`stats`, `graphics`, and `utils`; `SeuratObject`, `SpatialExperiment`,
`SummarizedExperiment`, and `FNN` are optional `Suggests`. The package source is
small (about 75 KB of R code in the current submission snapshot), and inputs are
plain matrices and data frames rather than mandatory large object classes.

Spatial graph construction uses `backend = "auto"` by default. When the optional
`FNN` package is installed, `build_niche_graph()` uses it for faster nearest
neighbor search; otherwise it falls back to an exact base R `dist` backend. This
keeps the default installation light while allowing faster graph construction on
larger preview datasets.

## Preparing priors

```r
write_nichetype_templates("nichetype_priors")
```

This writes CSV templates for markers, pathway mappings, pathway gene sets,
spatial niche expectations, and ligand-receptor expectations. See
`inst/SCHEMA.md` for the column contracts.

## Quick start

```r
library(NicheTypeR)

toy <- simulate_nichetype_data(n_per_type = 40, seed = 1)

result <- run_nichetype_workflow(
  expr = toy$expr,
  coords = toy$coords,
  metadata = toy$metadata,
  marker_db = toy$marker_db,
  pathway_sets = toy$pathway_sets,
  label_pathways = toy$label_pathways,
  niche_db = toy$niche_db,
  lr_db = toy$lr_db,
  graph_group_col = NULL,
  weights = c(
    marker = 1.5,
    pathway = 1,
    neighborhood = 0.8,
    ligand_receptor = 0.7
  )
)

fit <- result$fit
head(fit$calls)
```

Optional reference evidence can be added when labeled reference cells are
available:

```r
reference_profiles <- make_reference_profiles(toy$expr, toy$metadata$true_label)
reference <- score_reference_similarity(toy$expr, reference_profiles)
```

External annotation tools can also be used as the reference layer. Run SingleR,
Seurat label transfer, CellTypist, scmap, or another atlas mapper outside
NicheTypeR, then convert its labels or score matrix into auditable reference
evidence:

```r
external_predictions <- data.frame(
  cell_id = rownames(toy$metadata),
  label = toy$metadata$true_label,
  confidence = 0.9
)

external_reference <- score_external_labels(
  external_predictions,
  candidate_labels = colnames(result$evidence$marker),
  confidence_col = "confidence"
)

audited <- audit_external_annotation(
  external_reference,
  marker = result$evidence$marker,
  pathway = result$evidence$pathway,
  neighborhood = result$evidence$neighborhood,
  ligand_receptor = result$evidence$ligand_receptor,
  weights = c(
    reference = 1.5,
    marker = 1,
    pathway = 0.5,
    neighborhood = 0.5,
    ligand_receptor = 0.5
  )
)

head(summarize_evidence_conflicts(audited))
```

This is the intended relationship to SingleR-like tools: the external method
proposes a label, while NicheTypeR reports whether marker, pathway, local niche
and ligand-receptor evidence support or challenge that proposal.

## Context-Specific Annotation Evidence

The deeper method layer is Context-Specific Annotation Evidence (CSAE). CSAE
does not ask whether a spatial signal exists. It asks whether the support for a
candidate label exceeds explicit null explanations such as random spatial
graphs, permuted niche priors, or shuffled context evidence.

```r
csae <- score_context_specific_annotation(
  candidate_scores = external_reference,
  context_scores = list(
    marker = result$evidence$marker,
    pathway = result$evidence$pathway,
    neighborhood = result$evidence$neighborhood,
    ligand_receptor = result$evidence$ligand_receptor
  ),
  null_scores = list(
    random_graph = list(
      marker = result$evidence$marker,
      pathway = result$evidence$pathway,
      neighborhood = random_graph_neighborhood,
      ligand_receptor = result$evidence$ligand_receptor
    ),
    permuted_prior = list(
      marker = result$evidence$marker,
      pathway = result$evidence$pathway,
      neighborhood = permuted_prior_neighborhood,
      ligand_receptor = result$evidence$ligand_receptor
    )
  ),
  weights = c(marker = 1, pathway = 0.5, neighborhood = 0.5, ligand_receptor = 0.5)
)

head(csae$audit)
```

The `audit` table reports whether the candidate label is
`context_supported`, `context_conflict`, `context_not_specific`, or
`context_ambiguous`. This reframes spatial annotation as falsification and
calibration rather than another label-transfer vote.

## Proving the contribution

The package includes leave-one-evidence-out ablation so the spatial and
functional layers can be tested directly.

```r
truth <- toy$metadata$true_label
names(truth) <- rownames(toy$metadata)

evaluate_calls(fit$calls, truth)$summary

ablation <- ablate_evidence(
  scores = result$evidence,
  truth = truth,
  weights = c(
    marker = 1.5,
    pathway = 1,
    neighborhood = 0.8,
    ligand_receptor = 0.7
  )
)

ablation$summary
```

If removing `neighborhood`, `pathway`, or `ligand_receptor` reduces accuracy,
margin, or conflict resolution, that is direct evidence that the contextual
layers add value beyond markers.

Always include a simple spatial smoothing comparator before claiming that a
curated or learned niche prior adds biological information:

```r
smoothing <- score_spatial_smoothing(
  edges = result$edges,
  prior_scores = result$evidence$marker,
  alpha = 0.5
)

neighbor_vote <- score_neighbor_majority(
  edges = result$edges,
  prior_scores = result$evidence$marker
)
```

When trusted labels are available, tune evidence weights before applying the
model to unlabeled data:

```r
tuning <- tune_evidence_weights(
  scores = result$evidence,
  truth = truth
)

head(tuning$summary)
tuning$best_weights
```

For spatial data with trusted training labels, learn the label-label spatial
compatibility matrix instead of relying on hand-written niche rules:

```r
learned <- learn_niche_prior(
  edges = result$edges,
  labels = truth,
  train_cells = train_cells,
  method = "log_enrichment"
)

learned_neighborhood <- score_neighborhood(
  result$edges,
  prior_scores = result$evidence$marker,
  niche_db = learned$niche_db
)
```

For reviewer-grade evaluation, avoid random cell splits when spatial context is
part of the model. Use FOV/slide/replicate-blocked folds, spatial null graphs,
and paired statistics:

```r
folds <- make_group_folds(
  labels = truth,
  groups = metadata$fov_group,
  k = 5
)

null_edges <- spatial_null_edges(
  edges = result$edges,
  coords = result$input$coords,
  group_col = "fov_group"
)

comparison <- compare_call_sets(
  calls_a = baseline_calls,
  calls_b = learned_calls,
  truth = truth
)
```

## Reviewing conflicts

```r
head(summarize_evidence_conflicts(fit), 20)

clusters <- paste0("cluster_", toy$metadata$true_label)
names(clusters) <- rownames(toy$metadata)
summarize_cluster_calls(fit, clusters)
```

## Benchmark data panel

The repository includes benchmark summaries under `inst/benchmarks/`. The full
raw spatial transcriptomics datasets are not bundled because several are large
public GEO or hosted example-data files; dataset accessions and source notes are
listed in the benchmark registry.

The package-level smoke workflow is self-contained and uses simulated data:

```r
source(system.file("examples", "smoke_workflow.R", package = "NicheTypeR"))
```

Benchmark registry and result summaries:

```text
inst/benchmarks/BENCHMARK_DATASETS.md
inst/benchmarks/BENCHMARK_INDEPENDENCE_AND_TRUTH.md
inst/benchmarks/DATASET_REGISTRY.csv
inst/benchmarks/MULTIDATASET_BLOCKED_BENCHMARK.md
inst/benchmarks/RUNTIME_MEMORY_BENCHMARK.md
```

The added panel includes direct GEO MERSCOPE/MERFISH, CosMx, and Visium domain
datasets plus seqFISH, MERFISH, Slide-seqV2, Visium, MIBI-TOF, and IMC examples
converted into a common preview format with expression, spatial coordinates,
labels, and spatial validation groups.

The runtime benchmark measures one blocked fold per preview dataset and writes
dataset-stage timing summaries. In the current run, the 12-dataset one-fold
panel completed in 178.4 seconds of summed dataset-stage wall time, with a
median of 12.0 seconds per dataset and a maximum observed RSS of 385.3 MB. This
supports a lightweight computational footprint claim, but not a direct
speed-superiority claim over non-equivalent external tools.

The benchmark scripts used for the application-note snapshot are distributed
with the manuscript supplementary materials and mirrored in the project archive
when the accompanying data files are available.

An additional reference-profile baseline add-on is included in
`inst/benchmarks/REFERENCE_PROFILE_BASELINE.md`. It learns label centroids only
inside training spatial blocks and scores held-out cells by cosine similarity.
This gives a dependency-free reference-style comparator in the same broad
family as SingleR, Seurat label transfer, CellTypist and scmap, without claiming
to reimplement those tools.

A separate external-method comparator based on Seurat label transfer is included
in `inst/benchmarks/SEURAT_LABEL_TRANSFER_BASELINE.md`. It runs blocked
reference-to-query transfer on the RNA preview panel and reports the same
`cell_id`/`label`/`confidence` schema that `score_external_labels()` accepts.
`inst/benchmarks/EXTERNAL_METHOD_BASELINES.md` extends this comparison with
three blocked algorithmic proxy mappers: SingleR-style Spearman pseudo-bulk
mapping, scmap-style cosine nearest-neighbor transfer, and CellTypist-style
logistic classification. These are stress tests of the external-label audit
interface, not official package runs. In the current workspace, R/Bioconductor
packages and CellTypist model assets were unavailable, so the report includes an
explicit official-tool status table for those broad RNA-panel comparisons.
Across Seurat plus the three proxy families, generic margin risk remained
informative for external labels: 162,992 external calls yielded AUROC 0.735 and
AUPRC 0.685 for held-out reference-label discordance; the official Seurat run
alone reached AUROC 0.823.

`inst/benchmarks/INCREMENTAL_AUDIT_BENCHMARK.md` tests whether current
NicheTypeR-specific conflict flags add error-detection value beyond raw
classifier uncertainty. They do not yet: call-level raw margin AUROC is 0.743
versus 0.738 for margin plus conflict flags, and unique-cell raw margin AUROC is
0.879 versus 0.859 for the augmented score. This negative result is part of the
submission snapshot and should be cited when describing the current empirical
scope.

`inst/benchmarks/spotless_strong_baselines/REPORT.md` adds two official
Spotless seqFISH+ imaging-derived gold-standard tasks with strong expression
baselines and native R/Bioconductor SingleR. In leave-one-FOV validation,
native SingleR reaches 0.718 accuracy and 0.084 spot RMSE on cortex/SVZ, while
ExtraTrees reaches 0.785 accuracy and native SingleR 0.069 spot RMSE on
olfactory bulb. Nested logistic-spatial fusion selected positive spatial weight
in 0 of 56 fold/family selections, so the accepted nested spatial models revert
to logistic-only.

The audit case-study summary in
`inst/benchmarks/ANNOTATION_AUDIT_CASE_STUDY.md` reports per-cell events where
context or reference evidence rescues a marker-only error, harms a correct
marker-only call, or changes a still-incorrect call. This is the most direct
evidence for the package's intended role as an annotation-audit layer.

Current cross-dataset result: learned neighborhood passes the strict
matched-null guardrail in 9 of 68 label-bearing validation configurations.
The six expanded passes are GSE263450, GSE308952, expanded GSE327581 and the
SODB Fang2022Conservation, wang2021easi and Zeng2023Integrative sources. The
null-corrected context-specific residual passes in 1 of 68 configurations,
SODB he2020integrating; this is a tumour/non-tumour spatial-domain task rather
than a cell-type benchmark. Most datasets therefore show no specific context
gain, or are better explained by generic spatial smoothing/domain structure.
This supports a selective audit-framework claim, not a state-of-the-art
classifier claim.

The biological audit casebook in
`inst/benchmarks/BIOLOGICAL_AUDIT_CASEBOOK.md` converts audit flags into
reviewable annotation problems. In the current snapshot, 256,941 predictions
were audit-flagged and 153,847 were discordant with held-out reference labels,
representing 29,480 unique cells or spots after duplicate model calls were
removed. The prioritized 300-event table includes local-neighborhood
summaries so users can inspect whether the predicted label is spatially
plausible. This is retrospective evidence for annotation triage, not a
prospective pathology re-annotation experiment.

The expanded-scale stress test now covers 56 configurations and 1,226,225
configuration-level cells or spots. Learned neighborhood passes the strict
matched-null guardrail in 6 configurations and the context-specific residual
in 1 spatial-domain configuration.

For label-level audit granularity, `inst/benchmarks/LABEL_TASK_BENCHMARK.md`
summarizes 1,283 dataset-label validation tasks across the 12 preview and 56
expanded benchmark configurations. Learned-neighborhood evidence has positive
matched-null specific deltas in 425 tasks and exceeds a 0.01 label-F1 delta in
139 tasks. CSAE is positive in 209 tasks and exceeds 0.01 in 29. These are
label-level audit tasks, not independent cohort counts.

`inst/benchmarks/FOLD_LABEL_TASK_BENCHMARK.md` further decomposes predictions
into 2,984 eligible fold-label validation tasks with at least 10 held-out cells
or spots per label. Learned-neighborhood evidence passes fold-level guardrails
in 349 tasks, and 54 dataset-label tasks are reproducible across at least two
held-out folds.

The package also includes an initial null-corrected context-specific score:

```r
context_specific <- score_context_specific_neighborhood(
  edges = result$edges,
  prior_scores = result$evidence$marker,
  niche_db = learned$niche_db,
  null_edges = null_edges,
  null_niche_db = permute_niche_prior(learned$niche_db)
)
```

This score subtracts random-graph and permuted-prior explanations from the
observed learned-neighborhood score. In the current benchmark it is more useful
as an audit statistic than as a universally better classifier layer.

In the strictest current FOV-blocked setting, marker-only remains the strongest
simple baseline.
Learned neighborhood improves accuracy slightly over marker + pathway + LR, but
does not improve macro-F1 and the confidence interval crosses zero. A simple
spatial smoothing layer is assigned zero weight during training. Treat spatial
context as an audit/calibration signal until stronger cross-dataset evidence is
available.

## Output fields

`fit$calls` contains:

- `cell_id`: cell barcode or ID
- `label`: fused context-aware cell type call
- `confidence`: uncalibrated softmax-derived score of the top label
- `margin`: confidence gap between the top two labels
- `conflict_reason`: evidence sources that disagree with the final call

## Design notes

The first version intentionally uses interpretable scoring rather than a deep
model. This makes it easier to audit cases where marker evidence and spatial
context disagree.

Good next steps:

- harden Seurat and SpatialExperiment adapters on real objects
- add a direct SingleCellExperiment adapter
- add real curated marker/pathway/LR resources
- add cluster-level consensus calling
- benchmark against SingleR, CellTypist, Azimuth, BANKSY, and scANVI/scArches
- support user-trained evidence weights with held-out annotated spatial data
