#' Score candidate labels from ligand-receptor context
#'
#' Uses prior neighbor identity probabilities and local expression of ligands and
#' receptors to ask whether a candidate label has biologically plausible
#' interactions with nearby cells.
#'
#' @param expr Gene-by-cell expression matrix.
#' @param edges Data frame from `build_niche_graph`.
#' @param prior_scores Cell-by-label score matrix used to estimate neighbor
#'   identities.
#' @param lr_db Data frame with `sender_type`, `receiver_type`, `ligand`,
#'   `receptor`, and optional `weight`.
#' @param temperature Softmax temperature for converting prior scores to
#'   probabilities.
#' @return A cell-by-label ligand-receptor consistency matrix.
#' @export
score_lr_context <- function(expr, edges, prior_scores, lr_db, temperature = 1) {
  expr <- .check_expr(expr)
  prior_scores <- .check_score_matrix(prior_scores, "prior_scores")
  required <- c("sender_type", "receiver_type", "ligand", "receptor")
  missing <- setdiff(required, colnames(lr_db))
  if (length(missing) > 0) {
    stop("`lr_db` is missing columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  if (!"weight" %in% colnames(lr_db)) {
    lr_db$weight <- 1
  }

  labels <- colnames(prior_scores)
  cells <- intersect(colnames(expr), rownames(prior_scores))
  edges <- edges[edges$from %in% cells & edges$to %in% cells, , drop = FALSE]
  probs <- .softmax_rows(prior_scores[cells, , drop = FALSE], temperature = temperature)
  expr <- log1p(expr[, cells, drop = FALSE])

  score <- matrix(0, nrow = length(cells), ncol = length(labels),
                  dimnames = list(cells, labels))
  if (nrow(edges) == 0 || nrow(lr_db) == 0) {
    return(score)
  }

  lr_db <- lr_db[lr_db$ligand %in% rownames(expr) &
                   lr_db$receptor %in% rownames(expr) &
                   lr_db$sender_type %in% labels &
                   lr_db$receiver_type %in% labels, , drop = FALSE]
  if (nrow(lr_db) == 0) {
    return(score)
  }

  by_from <- split(edges$to, edges$from)
  for (cell in names(by_from)) {
    neigh <- intersect(by_from[[cell]], cells)
    if (length(neigh) == 0) {
      next
    }
    for (label in labels) {
      outgoing <- lr_db[lr_db$sender_type == label, , drop = FALSE]
      incoming <- lr_db[lr_db$receiver_type == label, , drop = FALSE]

      total <- 0
      denom <- 0
      if (nrow(outgoing) > 0) {
        for (r in seq_len(nrow(outgoing))) {
          receiver <- outgoing$receiver_type[r]
          neighbor_prob <- probs[neigh, receiver]
          ligand_expr <- expr[outgoing$ligand[r], cell]
          receptor_expr <- expr[outgoing$receptor[r], neigh]
          total <- total + outgoing$weight[r] * mean(ligand_expr * receptor_expr * neighbor_prob)
          denom <- denom + abs(outgoing$weight[r])
        }
      }
      if (nrow(incoming) > 0) {
        for (r in seq_len(nrow(incoming))) {
          sender <- incoming$sender_type[r]
          neighbor_prob <- probs[neigh, sender]
          ligand_expr <- expr[incoming$ligand[r], neigh]
          receptor_expr <- expr[incoming$receptor[r], cell]
          total <- total + incoming$weight[r] * mean(ligand_expr * receptor_expr * neighbor_prob)
          denom <- denom + abs(incoming$weight[r])
        }
      }
      if (denom > 0) {
        score[cell, label] <- total / denom
      }
    }
  }
  score
}
