#' Score candidate labels from spatial niche compatibility
#'
#' @param edges Data frame from `build_niche_graph`.
#' @param prior_scores Cell-by-label score matrix used to estimate neighbor
#'   identities.
#' @param niche_db Data frame with `cell_type`, `neighbor_type`, and optional
#'   `weight`.
#' @param temperature Softmax temperature for converting prior scores to
#'   probabilities.
#' @return A cell-by-label spatial niche compatibility matrix.
#' @export
score_neighborhood <- function(edges, prior_scores, niche_db, temperature = 1) {
  prior_scores <- .check_score_matrix(prior_scores, "prior_scores")
  required_edges <- c("from", "to")
  missing_edges <- setdiff(required_edges, colnames(edges))
  if (length(missing_edges) > 0) {
    stop("`edges` is missing columns: ", paste(missing_edges, collapse = ", "), call. = FALSE)
  }
  required_niche <- c("cell_type", "neighbor_type")
  missing_niche <- setdiff(required_niche, colnames(niche_db))
  if (length(missing_niche) > 0) {
    stop("`niche_db` is missing columns: ", paste(missing_niche, collapse = ", "), call. = FALSE)
  }
  if (!"weight" %in% colnames(niche_db)) {
    niche_db$weight <- 1
  }

  labels <- colnames(prior_scores)
  cells <- rownames(prior_scores)
  edges <- edges[edges$from %in% cells & edges$to %in% cells, , drop = FALSE]
  probs <- .softmax_rows(prior_scores, temperature = temperature)

  compat <- matrix(0, nrow = length(labels), ncol = length(labels),
                   dimnames = list(labels, labels))
  for (i in seq_len(nrow(niche_db))) {
    a <- niche_db$cell_type[i]
    b <- niche_db$neighbor_type[i]
    if (a %in% labels && b %in% labels) {
      compat[a, b] <- compat[a, b] + niche_db$weight[i]
    }
  }

  score <- matrix(0, nrow = length(cells), ncol = length(labels),
                  dimnames = list(cells, labels))
  if (nrow(edges) == 0) {
    return(score)
  }

  split_edges <- split(edges$to, edges$from)
  for (cell in names(split_edges)) {
    neigh <- intersect(split_edges[[cell]], rownames(probs))
    if (length(neigh) == 0) {
      next
    }
    neighbor_mix <- colMeans(probs[neigh, , drop = FALSE])
    score[cell, ] <- as.numeric(compat %*% neighbor_mix)
  }
  score
}
