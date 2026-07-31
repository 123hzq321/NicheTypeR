#' Score candidate cell types from positive and negative markers
#'
#' @param expr Gene-by-cell expression matrix.
#' @param marker_db Data frame with `cell_type`, `gene`, `direction`, and
#'   optional `weight`. `direction` should be `positive` or `negative`.
#' @param cap Z-score cap used before module scoring.
#' @return A list with a cell-by-label score matrix and marker coverage table.
#' @export
score_markers <- function(expr, marker_db, cap = 3) {
  expr <- .check_expr(expr)
  required <- c("cell_type", "gene", "direction")
  missing <- setdiff(required, colnames(marker_db))
  if (length(missing) > 0) {
    stop("`marker_db` is missing columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  if (!"weight" %in% colnames(marker_db)) {
    marker_db$weight <- 1
  }
  marker_db$direction <- tolower(marker_db$direction)
  labels <- unique(marker_db$cell_type)
  z <- .z_by_gene(expr, cap = cap)

  score <- matrix(0, nrow = ncol(expr), ncol = length(labels),
                  dimnames = list(colnames(expr), labels))
  coverage <- data.frame(
    cell_type = labels,
    positive_present = 0L,
    positive_total = 0L,
    negative_present = 0L,
    negative_total = 0L,
    stringsAsFactors = FALSE
  )

  for (label in labels) {
    db <- marker_db[marker_db$cell_type == label, , drop = FALSE]
    pos <- db[db$direction == "positive", , drop = FALSE]
    neg <- db[db$direction == "negative", , drop = FALSE]

    pos_genes <- intersect(pos$gene, rownames(z))
    neg_genes <- intersect(neg$gene, rownames(z))

    pos_score <- if (length(pos_genes) > 0) {
      w <- pos$weight[match(pos_genes, pos$gene)]
      .weighted_col_mean(z[pos_genes, , drop = FALSE], w)
    } else {
      rep(0, ncol(expr))
    }
    neg_score <- if (length(neg_genes) > 0) {
      w <- neg$weight[match(neg_genes, neg$gene)]
      .weighted_col_mean(z[neg_genes, , drop = FALSE], w)
    } else {
      rep(0, ncol(expr))
    }

    score[, label] <- pos_score - neg_score
    idx <- match(label, coverage$cell_type)
    coverage$positive_present[idx] <- length(pos_genes)
    coverage$positive_total[idx] <- nrow(pos)
    coverage$negative_present[idx] <- length(neg_genes)
    coverage$negative_total[idx] <- nrow(neg)
  }

  list(scores = score, coverage = coverage)
}
