test_that("context-aware annotation smoke test runs", {
  toy <- simulate_nichetype_data(n_per_type = 8, seed = 42)
  edges <- build_niche_graph(toy$coords, k = 4)
  edges_dist <- build_niche_graph(toy$coords, k = 4, backend = "dist")
  expect_equal(nrow(edges_dist), nrow(edges))

  marker <- score_markers(toy$expr, toy$marker_db)$scores
  pathway <- score_pathway_context(
    toy$expr,
    toy$pathway_sets,
    toy$label_pathways
  )$scores
  niche <- score_neighborhood(edges, marker, toy$niche_db)
  smoothing <- score_spatial_smoothing(edges, marker, alpha = 0.5)
  neighbor_vote <- score_neighbor_majority(edges, marker)
  lr <- score_lr_context(toy$expr, edges, marker, toy$lr_db)

  fit <- infer_context_type(
    list(marker = marker, pathway = pathway, neighborhood = niche, ligand_receptor = lr),
    weights = c(marker = 1.5, pathway = 1, neighborhood = 0.8, ligand_receptor = 0.7)
  )

  expect_equal(nrow(fit$calls), ncol(toy$expr))
  expect_equal(dim(smoothing), dim(marker))
  expect_equal(dim(neighbor_vote), dim(marker))
  expect_true(all(c("label", "confidence", "conflict_reason") %in% colnames(fit$calls)))
  expect_true(all(fit$calls$confidence >= 0 & fit$calls$confidence <= 1))

  external_predictions <- data.frame(
    cell_id = rownames(toy$metadata),
    label = toy$metadata$true_label,
    confidence = 0.9,
    stringsAsFactors = FALSE
  )
  external <- score_external_labels(
    external_predictions,
    candidate_labels = colnames(marker),
    confidence_col = "confidence"
  )
  external_aligned <- score_external_matrix(
    external,
    cells = rownames(marker),
    candidate_labels = colnames(marker)
  )
  external_fit <- audit_external_annotation(
    external_aligned,
    marker = marker,
    weights = c(reference = 1.5, marker = 0.5)
  )
  external_conflicts <- summarize_evidence_conflicts(external_fit, top_n = 3)
  expect_equal(dim(external_aligned), dim(marker))
  expect_equal(nrow(external_fit$calls), ncol(toy$expr))
  expect_true(all(c("reference_label", "marker_label") %in% colnames(external_conflicts)))

  ev <- evaluate_calls(fit$calls, toy$metadata$true_label)
  expect_true(ev$summary$accuracy > 0.5)

  ab <- ablate_evidence(
    list(marker = marker, pathway = pathway, neighborhood = niche, ligand_receptor = lr),
    truth = toy$metadata$true_label
  )
  expect_true(all(c("full", "without_marker") %in% rownames(ab$summary)))

  clusters <- paste0("cluster_", toy$metadata$true_label)
  names(clusters) <- rownames(toy$metadata)
  cluster_summary <- summarize_cluster_calls(fit, clusters)
  expect_true(nrow(cluster_summary) > 0)

  tune <- tune_evidence_weights(
    list(marker = marker, pathway = pathway, neighborhood = niche, ligand_receptor = lr),
    truth = toy$metadata$true_label,
    weight_grid = expand.grid(
      marker = c(1, 1.5),
      pathway = c(0, 1),
      neighborhood = c(0, 0.1),
      ligand_receptor = c(0, 0.5)
    )
  )
  expect_true(all(c("summary", "best_weights", "best_fit") %in% names(tune)))

  truth <- toy$metadata$true_label
  names(truth) <- rownames(toy$metadata)
  groups <- toy$metadata$true_label
  names(groups) <- rownames(toy$metadata)
  folds <- make_group_folds(truth, groups, k = 3)
  expect_equal(length(folds), 3)

  learned <- learn_niche_prior(
    edges = edges,
    labels = truth,
    train_cells = folds[[1]]$train,
    candidate_labels = colnames(marker)
  )
  expect_true(all(c("niche_db", "counts", "weights") %in% names(learned)))

  null_edges <- spatial_null_edges(
    edges,
    data.frame(
      cell_id = rownames(toy$metadata),
      group = toy$metadata$true_label,
      stringsAsFactors = FALSE
    ),
    group_col = "group"
  )
  expect_true(all(c("from", "to") %in% colnames(null_edges)))

  permuted <- permute_niche_prior(learned$niche_db)
  expect_equal(nrow(permuted), nrow(learned$niche_db))

  context_specific <- score_context_specific_neighborhood(
    edges = edges,
    prior_scores = marker,
    niche_db = learned$niche_db,
    null_edges = null_edges,
    null_niche_db = permuted
  )
  expect_equal(dim(context_specific$scores), dim(marker))
  expect_equal(context_specific$n_null, 2)

  cmp <- compare_call_sets(fit$calls, fit$calls, truth, n_boot = 10)
  expect_true(all(c("metrics", "paired") %in% names(cmp)))
})
