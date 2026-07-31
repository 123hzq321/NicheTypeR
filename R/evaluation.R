#' Evaluate predicted calls against known labels
#'
#' @param calls Call table from `infer_context_type` or a character vector of
#'   predicted labels.
#' @param truth True labels. Either a named vector keyed by cell ID or a vector
#'   in the same order as `calls`.
#' @return A list with summary metrics, per-label metrics, and a confusion table.
#' @export
evaluate_calls <- function(calls, truth) {
  if (is.data.frame(calls)) {
    predicted <- calls$label
    names(predicted) <- calls$cell_id
  } else {
    predicted <- as.character(calls)
    if (is.null(names(predicted))) {
      names(predicted) <- seq_along(predicted)
    }
  }

  if (is.null(names(truth))) {
    if (length(truth) != length(predicted)) {
      stop("Unnamed `truth` must have the same length as predictions.", call. = FALSE)
    }
    names(truth) <- names(predicted)
  }
  truth <- as.character(truth[names(predicted)])
  predicted <- as.character(predicted)
  keep <- !is.na(truth) & !is.na(predicted)
  truth <- truth[keep]
  predicted <- predicted[keep]
  if (length(truth) == 0) {
    stop("No comparable predictions and truth labels.", call. = FALSE)
  }

  labels <- sort(unique(c(truth, predicted)))
  confusion <- table(
    truth = factor(truth, levels = labels),
    predicted = factor(predicted, levels = labels)
  )
  accuracy <- sum(diag(confusion)) / sum(confusion)

  per_label <- data.frame(
    label = labels,
    precision = NA_real_,
    recall = NA_real_,
    f1 = NA_real_,
    support = as.integer(rowSums(confusion)),
    stringsAsFactors = FALSE
  )
  for (label in labels) {
    tp <- confusion[label, label]
    fp <- sum(confusion[, label]) - tp
    fn <- sum(confusion[label, ]) - tp
    precision <- if ((tp + fp) > 0) tp / (tp + fp) else NA_real_
    recall <- if ((tp + fn) > 0) tp / (tp + fn) else NA_real_
    f1 <- if (is.finite(precision + recall) && (precision + recall) > 0) {
      2 * precision * recall / (precision + recall)
    } else {
      NA_real_
    }
    idx <- match(label, per_label$label)
    per_label$precision[idx] <- precision
    per_label$recall[idx] <- recall
    per_label$f1[idx] <- f1
  }

  list(
    summary = data.frame(
      n = length(truth),
      accuracy = accuracy,
      macro_f1 = mean(per_label$f1, na.rm = TRUE),
      stringsAsFactors = FALSE
    ),
    per_label = per_label,
    confusion = confusion
  )
}

#' Run leave-one-evidence-out ablation
#'
#' @param scores Named list of cell-by-label evidence score matrices.
#' @param truth Optional known labels used to compute accuracy and macro F1.
#' @param weights Optional evidence weights.
#' @param temperature Softmax temperature.
#' @param min_margin Minimum margin passed to `infer_context_type`.
#' @return A list containing an ablation summary table and fitted models.
#' @export
ablate_evidence <- function(scores,
                            truth = NULL,
                            weights = NULL,
                            temperature = 1,
                            min_margin = 0.08,
                            component_min_margin = 0.05) {
  if (!is.list(scores) || length(scores) < 2) {
    stop("`scores` must contain at least two evidence matrices.", call. = FALSE)
  }
  if (is.null(names(scores)) || any(names(scores) == "")) {
    names(scores) <- paste0("evidence_", seq_along(scores))
  }
  evidence_names <- names(scores)
  fit_names <- c("full", paste0("without_", evidence_names))
  fits <- vector("list", length(fit_names))
  names(fits) <- fit_names

  fit_one <- function(active_scores) {
    active_weights <- weights
    if (!is.null(active_weights)) {
      active_weights <- active_weights[names(active_scores)]
    }
    infer_context_type(
      scores = active_scores,
      weights = active_weights,
      temperature = temperature,
      min_margin = min_margin,
      component_min_margin = component_min_margin
    )
  }

  fits$full <- fit_one(scores)
  for (nm in evidence_names) {
    fits[[paste0("without_", nm)]] <- fit_one(scores[setdiff(evidence_names, nm)])
  }

  summary <- do.call(rbind, lapply(names(fits), function(model) {
    calls <- fits[[model]]$calls
    row <- data.frame(
      model = model,
      n = nrow(calls),
      mean_confidence = mean(calls$confidence, na.rm = TRUE),
      mean_margin = mean(calls$margin, na.rm = TRUE),
      conflict_rate = mean(calls$conflict_reason != "consistent"),
      stringsAsFactors = FALSE
    )
    if (!is.null(truth)) {
      ev <- evaluate_calls(calls, truth)
      row$accuracy <- ev$summary$accuracy
      row$macro_f1 <- ev$summary$macro_f1
    }
    row
  }))
  rownames(summary) <- summary$model

  list(summary = summary, fits = fits)
}
