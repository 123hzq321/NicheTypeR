\name{NicheTypeR-core}
\alias{audit_external_annotation}
\alias{build_niche_graph}
\alias{compare_call_sets}
\alias{evaluate_calls}
\alias{infer_context_type}
\alias{learn_niche_prior}
\alias{make_reference_profiles}
\alias{make_group_folds}
\alias{permute_niche_prior}
\alias{plot_annotation_evidence}
\alias{plot_spatial_calls}
\alias{prepare_from_seurat}
\alias{prepare_from_spatial_experiment}
\alias{prepare_nichetype_input}
\alias{run_nichetype_workflow}
\alias{ablate_evidence}
\alias{score_lr_context}
\alias{score_markers}
\alias{score_context_specific_neighborhood}
\alias{score_context_specific_annotation}
\alias{score_external_labels}
\alias{score_external_matrix}
\alias{score_neighborhood}
\alias{score_neighbor_majority}
\alias{score_pathway_context}
\alias{score_reference_similarity}
\alias{score_spatial_smoothing}
\alias{simulate_nichetype_data}
\alias{spatial_null_edges}
\alias{summarize_cluster_calls}
\alias{summarize_evidence_conflicts}
\alias{tune_evidence_weights}
\alias{write_nichetype_templates}
\title{Core NicheTypeR functions}
\description{
Core functions for a prototype context-aware cell type annotation workflow.
The package combines marker, reference, pathway or metabolic program, spatial
niche, and ligand-receptor evidence into interpretable cell type calls and
null-corrected context-specific annotation evidence.
}
\usage{
simulate_nichetype_data(n_per_type = 60, seed = 1)

prepare_nichetype_input(expr, coords, metadata = NULL,
  cell_id_col = "cell_id", coord_cols = c("x", "y"))

make_reference_profiles(expr, labels, min_cells = 3)

build_niche_graph(coords, k = 8, radius = NULL, group_col = NULL,
  backend = c("auto", "FNN", "dist"))

make_group_folds(labels, groups, k = 5, seed = 1)

spatial_null_edges(edges, coords, group_col, seed = 1)

permute_niche_prior(niche_db, seed = 1)

compare_call_sets(calls_a, calls_b, truth, n_boot = 2000, seed = 1)

learn_niche_prior(edges, labels, train_cells = NULL, candidate_labels = NULL,
  pseudocount = 1, method = c("log_enrichment", "conditional", "pmi"),
  clip = 3)

score_markers(expr, marker_db, cap = 3)

score_reference_similarity(expr, reference_profiles, method = "spearman")

score_external_labels(predictions, candidate_labels = NULL,
  cell_id_col = "cell_id", label_col = "label", score_col = NULL,
  confidence_col = NULL, predicted_score = 1, background_score = 0,
  unknown_labels = c("unknown", "unassigned", "ambiguous", "NA"))

score_external_matrix(score_matrix, cells = NULL, candidate_labels = NULL,
  fill_missing = 0)

audit_external_annotation(external_scores, ..., reference_name = "reference",
  weights = NULL, temperature = 1, min_margin = 0.08,
  component_min_margin = 0.05)

score_pathway_context(expr, pathway_sets, label_pathways, cap = 3)

score_neighborhood(edges, prior_scores, niche_db, temperature = 1)

score_context_specific_neighborhood(edges, prior_scores, niche_db,
  null_edges = NULL, null_niche_db = NULL, statistic = c("residual", "z"),
  temperature = 1, min_null_sd = 1e-6)

score_context_specific_annotation(candidate_scores, context_scores,
  null_scores, candidate_labels = NULL, weights = NULL,
  statistic = c("residual", "z"), standardize = FALSE,
  support_threshold = 0, min_context_margin = 0.05,
  conflict_delta = 0.1, min_null_sd = 1e-6)

score_spatial_smoothing(edges, prior_scores, alpha = 0.5,
  temperature = 1, return_log = TRUE)

score_neighbor_majority(edges, prior_scores, temperature = 1,
  return_log = TRUE)

score_lr_context(expr, edges, prior_scores, lr_db, temperature = 1)

infer_context_type(scores, weights = NULL, temperature = 1,
  min_margin = 0.08, component_min_margin = 0.05)

run_nichetype_workflow(expr, coords, marker_db, metadata = NULL,
  reference_profiles = NULL, pathway_sets = NULL, label_pathways = NULL,
  niche_db = NULL, lr_db = NULL, k = 8, radius = NULL,
  graph_group_col = NULL, weights = NULL, temperature = 1,
  min_margin = 0.08, component_min_margin = 0.05)

evaluate_calls(calls, truth)

ablate_evidence(scores, truth = NULL, weights = NULL, temperature = 1,
  min_margin = 0.08, component_min_margin = 0.05)

summarize_evidence_conflicts(fit, top_n = Inf)

summarize_cluster_calls(fit, clusters, min_fraction = 0.6)

tune_evidence_weights(scores, truth, weight_grid = NULL,
  metric = c("macro_f1", "accuracy"), temperature = 1,
  min_margin = 0.08, component_min_margin = 0.05)

prepare_from_seurat(object, assay = NULL, layer = "data", slot = "data",
  coords = NULL, metadata = NULL, coord_cols = c("x", "y"))

prepare_from_spatial_experiment(object, assay = "logcounts", metadata = NULL)

write_nichetype_templates(out_dir = ".", overwrite = FALSE)

plot_annotation_evidence(fit, cell_id = NULL, label = NULL)

plot_spatial_calls(coords, calls)
}
\arguments{
\item{expr}{Gene-by-cell expression matrix.}
\item{coords}{Coordinate data frame with cell IDs and x/y columns.}
\item{metadata}{Optional cell metadata data frame.}
\item{cell_id_col}{Column containing cell IDs.}
\item{coord_cols}{Length-two vector naming x/y coordinate columns.}
\item{labels}{Cell labels for building reference profiles.}
\item{groups}{Named group IDs for block validation.}
\item{calls_a}{Baseline call table or named character vector.}
\item{calls_b}{Comparator call table or named character vector.}
\item{n_boot}{Number of bootstrap resamples.}
\item{train_cells}{Optional training cell IDs used for learning spatial
compatibility.}
\item{candidate_labels}{Optional label universe or candidate label vector,
depending on the function.}
\item{pseudocount}{Additive smoothing for learned label-label counts.}
\item{clip}{Optional absolute cap for learned weights.}
\item{min_cells}{Minimum cells required per reference label.}
\item{k}{Number of nearest neighbors.}
\item{radius}{Optional distance cutoff.}
\item{group_col}{Optional coordinate column used to build independent graphs.}
\item{backend}{Nearest-neighbor backend. \code{auto} uses the optional \code{FNN}
package when available and otherwise falls back to base R \code{dist}.}
\item{marker_db}{Marker table with cell_type, gene, direction, and optional weight.}
\item{cap}{Z-score cap for module scoring.}
\item{reference_profiles}{Gene-by-label reference profile matrix.}
\item{predictions}{External annotation result table with one row per cell.}
\item{label_col}{Column containing predicted labels.}
\item{score_col}{Optional external score column.}
\item{confidence_col}{Optional external confidence column.}
\item{predicted_score}{Score assigned to predicted labels when no score column
is supplied.}
\item{background_score}{Score assigned to non-predicted labels.}
\item{unknown_labels}{External labels treated as unassigned.}
\item{score_matrix}{External cell-by-label score matrix.}
\item{cells}{Optional cell IDs to retain or add when aligning an external
score matrix.}
\item{fill_missing}{Score used for missing cells or labels.}
\item{external_scores}{External cell-by-label score matrix to audit.}
\item{...}{Additional named NicheTypeR evidence matrices supplied to
\code{audit_external_annotation}.}
\item{reference_name}{Evidence name assigned to external scores.}
\item{method}{Method argument for the relevant function, such as correlation
method for reference similarity or weighting method for learned niche priors.}
\item{pathway_sets}{Named list of pathway or metabolic gene sets.}
\item{label_pathways}{Table mapping candidate labels to supporting pathways.}
\item{edges}{Spatial graph edge table.}
\item{prior_scores}{Cell-by-label prior score matrix.}
\item{niche_db}{Table of expected cell type and neighbor type relationships.}
\item{null_edges}{Optional null graph or list of null graphs.}
\item{null_niche_db}{Optional permuted niche prior or list of permuted niche
priors.}
\item{statistic}{Null-corrected context statistic: residual or z-score.}
\item{candidate_scores}{Cell-by-label candidate annotation score matrix used
as the label proposal to audit.}
\item{context_scores}{Observed context evidence matrix or named list of
cell-by-label evidence matrices.}
\item{null_scores}{List of null context score matrices or named evidence lists.}
\item{standardize}{Whether to robust-standardize context evidence matrices
before fusion.}
\item{support_threshold}{Minimum context-specific annotation evidence required
before a candidate label is called supported.}
\item{min_context_margin}{Minimum top-vs-second context-specific margin for a
supported candidate label.}
\item{conflict_delta}{Minimum best-context minus candidate-context score gap
required to mark a candidate as context-conflicting.}
\item{min_null_sd}{Minimum null standard deviation for z-scores.}
\item{alpha}{Weight assigned to the neighborhood average for spatial smoothing.}
\item{return_log}{Whether spatial smoothing functions return log-probability
scores instead of probabilities.}
\item{temperature}{Softmax temperature.}
\item{lr_db}{Ligand-receptor prior table.}
\item{scores}{Named list of cell-by-label evidence score matrices.}
\item{weights}{Optional evidence weights.}
\item{graph_group_col}{Optional coordinate column used to build independent
spatial graphs.}
\item{min_margin}{Minimum top-vs-second probability margin.}
\item{component_min_margin}{Minimum evidence-layer margin required before an
evidence layer can be counted as conflicting with the final call.}
\item{fit}{Result from \code{infer_context_type}.}
\item{cell_id}{Optional cell ID to inspect.}
\item{label}{Optional label to inspect.}
\item{calls}{Call table from \code{infer_context_type}.}
\item{n_per_type}{Number of simulated cells per type.}
\item{seed}{Random seed.}
\item{truth}{Known labels for evaluation.}
\item{object}{Seurat or SpatialExperiment object.}
\item{assay}{Assay name.}
\item{layer}{Seurat layer name.}
\item{slot}{Seurat slot fallback.}
\item{top_n}{Number of conflict rows to return.}
\item{clusters}{Cluster assignment vector.}
\item{min_fraction}{Minimum top-label fraction for cluster consensus.}
\item{out_dir}{Directory for writing prior templates.}
\item{overwrite}{Whether to replace existing template files.}
\item{weight_grid}{Optional data frame with one column per evidence source.}
\item{metric}{Metric used to rank tuned models.}
}
\value{
Functions return expression-ready toy data, aligned input objects, evidence
score matrices, or fused annotation results depending on the function called.
}
\examples{
toy <- simulate_nichetype_data(n_per_type = 10, seed = 1)
edges <- build_niche_graph(toy$coords, k = 4)
marker <- score_markers(toy$expr, toy$marker_db)$scores
pathway <- score_pathway_context(toy$expr, toy$pathway_sets,
  toy$label_pathways)$scores
niche <- score_neighborhood(edges, marker, toy$niche_db)
fit <- infer_context_type(list(marker = marker, pathway = pathway,
  neighborhood = niche))
head(fit$calls)
evaluate_calls(fit$calls, toy$metadata$true_label)$summary
}
