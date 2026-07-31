#' Score candidate labels by reference profile similarity
#'
#' @param expr Gene-by-cell query expression matrix.
#' @param reference_profiles Gene-by-label matrix of reference expression
#'   profiles.
#' @param method Correlation method passed to `stats::cor`.
#' @return A cell-by-label similarity matrix.
#' @export
score_reference_similarity <- function(expr, reference_profiles, method = "spearman") {
  expr <- .check_expr(expr)
  reference_profiles <- .check_expr(reference_profiles)
  genes <- intersect(rownames(expr), rownames(reference_profiles))
  if (length(genes) < 5) {
    stop("Need at least five overlapping genes for reference similarity.", call. = FALSE)
  }

  score <- matrix(NA_real_, nrow = ncol(expr), ncol = ncol(reference_profiles),
                  dimnames = list(colnames(expr), colnames(reference_profiles)))
  for (label in colnames(reference_profiles)) {
    ref <- reference_profiles[genes, label]
    score[, label] <- apply(expr[genes, , drop = FALSE], 2, function(cell_expr) {
      suppressWarnings(stats::cor(cell_expr, ref, method = method, use = "pairwise.complete.obs"))
    })
  }
  score[!is.finite(score)] <- 0
  score
}
