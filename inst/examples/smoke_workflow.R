library(NicheTypeR)

toy <- simulate_nichetype_data(n_per_type = 25, seed = 7)

result <- run_nichetype_workflow(
  expr = toy$expr,
  coords = toy$coords,
  metadata = toy$metadata,
  marker_db = toy$marker_db,
  pathway_sets = toy$pathway_sets,
  label_pathways = toy$label_pathways,
  niche_db = toy$niche_db,
  lr_db = toy$lr_db,
  weights = c(
    marker = 1.5,
    pathway = 1,
    neighborhood = 0.8,
    ligand_receptor = 0.7
  )
)

fit <- result$fit
print(head(fit$calls))

truth <- toy$metadata$true_label
names(truth) <- rownames(toy$metadata)
print(evaluate_calls(fit$calls, truth)$summary)
print(ablate_evidence(result$evidence, truth = truth)$summary)
