#' Score candidate labels from pathway activity
#'
#' @param expr Gene-by-cell expression matrix.
#' @param pathway_sets Named list of pathway gene vectors.
#' @param label_pathways Data frame with `cell_type`, `pathway`, and optional
#'   `weight` columns describing which pathways support each label.
#' @param cap Z-score cap used before module scoring.
#' @return A list with pathway activity and cell-by-label pathway support.
#' @export
score_pathway_context <- function(expr, pathway_sets, label_pathways, cap = 3) {
  expr <- .check_expr(expr)
  if (is.null(names(pathway_sets)) || any(names(pathway_sets) == "")) {
    stop("`pathway_sets` must be a named list.", call. = FALSE)
  }
  required <- c("cell_type", "pathway")
  missing <- setdiff(required, colnames(label_pathways))
  if (length(missing) > 0) {
    stop("`label_pathways` is missing columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  if (!"weight" %in% colnames(label_pathways)) {
    label_pathways$weight <- 1
  }

  z <- .z_by_gene(expr, cap = cap)
  pathway_score <- matrix(0, nrow = ncol(expr), ncol = length(pathway_sets),
                          dimnames = list(colnames(expr), names(pathway_sets)))
  coverage <- data.frame(
    pathway = names(pathway_sets),
    genes_present = 0L,
    genes_total = lengths(pathway_sets),
    stringsAsFactors = FALSE
  )

  for (pathway in names(pathway_sets)) {
    genes <- intersect(pathway_sets[[pathway]], rownames(z))
    coverage$genes_present[coverage$pathway == pathway] <- length(genes)
    pathway_score[, pathway] <- if (length(genes) > 0) {
      colMeans(z[genes, , drop = FALSE], na.rm = TRUE)
    } else {
      0
    }
  }

  labels <- unique(label_pathways$cell_type)
  label_score <- matrix(0, nrow = ncol(expr), ncol = length(labels),
                        dimnames = list(colnames(expr), labels))
  for (label in labels) {
    db <- label_pathways[label_pathways$cell_type == label, , drop = FALSE]
    paths <- intersect(db$pathway, colnames(pathway_score))
    if (length(paths) == 0) {
      next
    }
    w <- db$weight[match(paths, db$pathway)]
    label_score[, label] <- .weighted_col_mean(t(pathway_score[, paths, drop = FALSE]), w)
  }

  list(scores = label_score, pathway_activity = pathway_score, coverage = coverage)
}
