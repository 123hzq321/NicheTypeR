#' Score labels by smoothing prior probabilities over spatial neighbors
#'
#' `score_spatial_smoothing()` is a simple spatial baseline: it converts a
#' cell-by-label prior score matrix into probabilities, averages neighboring
#' probabilities, and mixes each cell's own prior with its neighborhood prior.
#' Use it as a reviewer-facing comparator for learned or curated niche priors.
#'
#' @param edges Data frame from `build_niche_graph` with `from` and `to`
#'   columns.
#' @param prior_scores Cell-by-label score matrix.
#' @param alpha Weight assigned to the neighborhood average. `0` returns the
#'   cell prior, `1` returns a pure neighbor vote.
#' @param temperature Softmax temperature used to convert prior scores to
#'   probabilities.
#' @param return_log Whether to return log-probability scores. If `FALSE`,
#'   returns probabilities.
#' @return A cell-by-label matrix of spatial smoothing scores.
#' @export
score_spatial_smoothing <- function(edges,
                                    prior_scores,
                                    alpha = 0.5,
                                    temperature = 1,
                                    return_log = TRUE) {
  prior_scores <- .check_score_matrix(prior_scores, "prior_scores")
  required_edges <- c("from", "to")
  missing_edges <- setdiff(required_edges, colnames(edges))
  if (length(missing_edges) > 0) {
    stop("`edges` is missing columns: ", paste(missing_edges, collapse = ", "), call. = FALSE)
  }

  alpha <- as.numeric(alpha)[1]
  if (!is.finite(alpha)) {
    stop("`alpha` must be finite.", call. = FALSE)
  }
  alpha <- min(max(alpha, 0), 1)

  cells <- rownames(prior_scores)
  labels <- colnames(prior_scores)
  edges <- edges[edges$from %in% cells & edges$to %in% cells, , drop = FALSE]

  probs <- .softmax_rows(prior_scores, temperature = temperature)
  neighbor_probs <- probs
  if (nrow(edges) > 0) {
    neighbor_probs[,] <- 0
    split_edges <- split(edges$to, edges$from)
    for (cell in names(split_edges)) {
      neigh <- intersect(split_edges[[cell]], rownames(probs))
      if (length(neigh) > 0) {
        neighbor_probs[cell, ] <- colMeans(probs[neigh, , drop = FALSE])
      }
    }
    missing_neighbors <- rowSums(neighbor_probs) == 0
    neighbor_probs[missing_neighbors, ] <- probs[missing_neighbors, , drop = FALSE]
  }

  smoothed <- (1 - alpha) * probs + alpha * neighbor_probs
  smoothed <- sweep(smoothed, 1, rowSums(smoothed), "/")
  dimnames(smoothed) <- list(cells, labels)
  if (isTRUE(return_log)) {
    smoothed <- log(pmax(smoothed, .Machine$double.eps))
  }
  smoothed
}

#' Score labels by a pure spatial neighbor vote
#'
#' This is a convenience wrapper around `score_spatial_smoothing()` with
#' `alpha = 1`. It is useful as a deliberately simple baseline.
#'
#' @inheritParams score_spatial_smoothing
#' @return A cell-by-label matrix of neighbor-vote scores.
#' @export
score_neighbor_majority <- function(edges,
                                    prior_scores,
                                    temperature = 1,
                                    return_log = TRUE) {
  score_spatial_smoothing(
    edges = edges,
    prior_scores = prior_scores,
    alpha = 1,
    temperature = temperature,
    return_log = return_log
  )
}
