## ----include=FALSE------------------------------------------------------------
knitr::opts_chunk$set(collapse = TRUE, comment = "#>", eval = FALSE)


## -----------------------------------------------------------------------------
library(NicheTypeR)

toy <- simulate_nichetype_data(n_per_type = 40, seed = 1)
edges <- build_niche_graph(toy$coords, k = 8)

marker <- score_markers(toy$expr, toy$marker_db)$scores
pathway <- score_pathway_context(
  toy$expr,
  toy$pathway_sets,
  toy$label_pathways
)$scores
niche <- score_neighborhood(edges, marker, toy$niche_db)
lr <- score_lr_context(toy$expr, edges, marker, toy$lr_db)

fit <- infer_context_type(
  list(
    marker = marker,
    pathway = pathway,
    neighborhood = niche,
    ligand_receptor = lr
  ),
  weights = c(marker = 1.5, pathway = 0.5, neighborhood = 0.1, ligand_receptor = 0.5)
)

head(fit$calls)


## -----------------------------------------------------------------------------
truth <- toy$metadata$true_label
names(truth) <- rownames(toy$metadata)

groups <- toy$metadata$true_label
names(groups) <- rownames(toy$metadata)
folds <- make_group_folds(truth, groups, k = 3)

learned <- learn_niche_prior(
  edges = edges,
  labels = truth,
  train_cells = folds[[1]]$train,
  candidate_labels = colnames(marker)
)

learned_niche <- score_neighborhood(edges, marker, learned$niche_db)

null_edges <- spatial_null_edges(
  edges,
  data.frame(cell_id = rownames(toy$metadata), group = groups),
  group_col = "group"
)

random_niche <- score_neighborhood(null_edges, marker, learned$niche_db)
permuted_niche <- score_neighborhood(edges, marker, permute_niche_prior(learned$niche_db))


## -----------------------------------------------------------------------------
context_specific <- score_context_specific_neighborhood(
  edges = edges,
  prior_scores = marker,
  niche_db = learned$niche_db,
  null_edges = null_edges,
  null_niche_db = permute_niche_prior(learned$niche_db),
  statistic = "residual"
)

fit_context_specific <- infer_context_type(
  list(marker = marker, context_specific = context_specific$scores),
  weights = c(marker = 1.5, context_specific = 0.1)
)


## -----------------------------------------------------------------------------
smoothing <- score_spatial_smoothing(edges, marker, alpha = 0.5)
neighbor_vote <- score_neighbor_majority(edges, marker)

tuned <- tune_evidence_weights(
  list(marker = marker, pathway = pathway, spatial_smoothing = smoothing, ligand_receptor = lr),
  truth = truth
)

tuned$summary[1:5, ]


## -----------------------------------------------------------------------------
conflicts <- summarize_evidence_conflicts(fit)
head(conflicts, 20)

clusters <- paste0("cluster_", toy$metadata$true_label)
names(clusters) <- rownames(toy$metadata)
summarize_cluster_calls(fit, clusters)

