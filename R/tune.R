#' Tune evidence weights against known labels
#'
#' Searches a user-supplied or default grid of evidence weights and ranks models
#' by accuracy or macro F1. This is intended for benchmark datasets and for
#' calibrating context layers before applying them to unlabeled spatial data.
#'
#' @param scores Named list of cell-by-label evidence score matrices.
#' @param truth Known labels. Either a named vector keyed by cell ID or a vector
#'   in the same order as score rows.
#' @param weight_grid Optional data frame with one column per evidence name.
#' @param metric Ranking metric: `macro_f1` or `accuracy`.
#' @param temperature Softmax temperature passed to `infer_context_type`.
#' @param min_margin Minimum final-call margin passed to `infer_context_type`.
#' @param component_min_margin Minimum component margin passed to
#'   `infer_context_type`.
#' @return A list with the ranked tuning table, best weights, and best fit.
#' @export
tune_evidence_weights <- function(scores,
                                  truth,
                                  weight_grid = NULL,
                                  metric = c("macro_f1", "accuracy"),
                                  temperature = 1,
                                  min_margin = 0.08,
                                  component_min_margin = 0.05) {
  metric <- match.arg(metric)
  scores <- .align_score_list(scores)
  evidence_names <- names(scores)
  if (is.null(weight_grid)) {
    grids <- lapply(evidence_names, .default_weight_grid)
    names(grids) <- evidence_names
    weight_grid <- expand.grid(grids, KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE)
  }
  missing <- setdiff(evidence_names, colnames(weight_grid))
  if (length(missing) > 0) {
    stop("`weight_grid` is missing evidence columns: ",
         paste(missing, collapse = ", "),
         call. = FALSE)
  }

  rows <- vector("list", nrow(weight_grid))
  fits <- vector("list", nrow(weight_grid))
  for (i in seq_len(nrow(weight_grid))) {
    weights <- as.numeric(weight_grid[i, evidence_names, drop = TRUE])
    names(weights) <- evidence_names
    fit <- infer_context_type(
      scores = scores,
      weights = weights,
      temperature = temperature,
      min_margin = min_margin,
      component_min_margin = component_min_margin
    )
    ev <- evaluate_calls(fit$calls, truth)
    calls <- fit$calls
    rows[[i]] <- data.frame(
      model_id = i,
      weight_grid[i, evidence_names, drop = FALSE],
      accuracy = ev$summary$accuracy,
      macro_f1 = ev$summary$macro_f1,
      mean_confidence = mean(calls$confidence, na.rm = TRUE),
      mean_margin = mean(calls$margin, na.rm = TRUE),
      conflict_rate = mean(calls$conflict_reason != "consistent"),
      stringsAsFactors = FALSE
    )
    fits[[i]] <- fit
  }

  summary <- do.call(rbind, rows)
  summary <- summary[order(summary[[metric]], summary$accuracy, decreasing = TRUE), , drop = FALSE]
  rownames(summary) <- NULL
  best_id <- summary$model_id[1]
  best_weights <- as.numeric(summary[1, evidence_names, drop = TRUE])
  names(best_weights) <- evidence_names

  list(
    summary = summary,
    best_weights = best_weights,
    best_fit = fits[[best_id]]
  )
}

.default_weight_grid <- function(evidence_name) {
  switch(
    evidence_name,
    marker = c(1, 1.5, 2),
    reference = c(0, 0.5, 1),
    pathway = c(0, 0.5, 1),
    neighborhood = c(0, 0.05, 0.1, 0.2, 0.5),
    ligand_receptor = c(0, 0.25, 0.5, 0.75, 1),
    c(0, 0.5, 1)
  )
}
