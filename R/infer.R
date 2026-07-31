#' Fuse evidence matrices into context-aware cell type calls
#'
#' @param scores Named list of cell-by-label score matrices. Typical names are
#'   `marker`, `reference`, `pathway`, `neighborhood`, and `ligand_receptor`.
#' @param weights Optional named numeric vector. Missing evidence names receive
#'   weight 1.
#' @param temperature Softmax temperature used for final probabilities.
#' @param min_margin Minimum probability difference between the best and second
#'   best labels before a call is marked as low-margin.
#' @return A list with fused scores, probabilities, calls, and aligned component
#'   score matrices.
#' @export
infer_context_type <- function(scores,
                               weights = NULL,
                               temperature = 1,
                               min_margin = 0.08,
                               component_min_margin = 0.05) {
  scores <- .align_score_list(scores)
  evidence_names <- names(scores)
  if (is.null(weights)) {
    weights <- stats::setNames(rep(1, length(scores)), evidence_names)
  }
  missing_weights <- setdiff(evidence_names, names(weights))
  if (length(missing_weights) > 0) {
    weights[missing_weights] <- 1
  }
  weights <- weights[evidence_names]
  weights[is.na(weights)] <- 1
  weights[!is.finite(weights)] <- 0

  standardized <- lapply(scores, .standardize_score)
  fused <- standardized[[1]] * weights[1]
  if (length(standardized) > 1) {
    for (i in 2:length(standardized)) {
      fused <- fused + standardized[[i]] * weights[i]
    }
  }
  denom <- sum(abs(weights))
  if (denom > 0) {
    fused <- fused / denom
  }

  prob <- .softmax_rows(fused, temperature = temperature)
  label <- .top_labels(prob)
  sorted <- t(apply(prob, 1, sort, decreasing = TRUE))
  confidence <- sorted[, 1]
  margin <- if (ncol(sorted) > 1) sorted[, 1] - sorted[, 2] else sorted[, 1]

  component_prob <- lapply(standardized, .softmax_rows)
  component_best <- lapply(component_prob, .top_labels)
  component_margin <- lapply(component_prob, function(x) {
    sorted_component <- t(apply(x, 1, sort, decreasing = TRUE))
    if (ncol(sorted_component) > 1) {
      sorted_component[, 1] - sorted_component[, 2]
    } else {
      sorted_component[, 1]
    }
  })
  conflict_reason <- character(nrow(prob))
  for (i in seq_len(nrow(prob))) {
    conflicts <- names(component_best)[vapply(names(component_best), function(nm) {
      !identical(component_best[[nm]][i], label[i]) &&
        component_margin[[nm]][i] >= component_min_margin
    }, logical(1))]
    reason <- if (length(conflicts) == 0) "consistent" else paste0(conflicts, "_conflict", collapse = ";")
    if (margin[i] < min_margin) {
      reason <- paste(c(reason, "low_margin"), collapse = ";")
    }
    conflict_reason[i] <- reason
  }

  calls <- data.frame(
    cell_id = rownames(prob),
    label = label,
    confidence = as.numeric(confidence),
    margin = as.numeric(margin),
    conflict_reason = conflict_reason,
    stringsAsFactors = FALSE
  )
  rownames(calls) <- calls$cell_id

  list(
    scores = fused,
    probabilities = prob,
    calls = calls,
    components = standardized,
    raw_components = scores,
    weights = weights
  )
}
