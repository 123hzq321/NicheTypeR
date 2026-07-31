#' Plot evidence scores for one cell or average evidence for one label
#'
#' @param fit Result from `infer_context_type`.
#' @param cell_id Optional cell identifier to inspect.
#' @param label Optional label to inspect. If `cell_id` is supplied, defaults to
#'   the assigned label for that cell.
#' @return Invisibly returns the plotted values.
#' @export
plot_annotation_evidence <- function(fit, cell_id = NULL, label = NULL) {
  if (is.null(fit$components) || is.null(fit$calls)) {
    stop("`fit` must be returned by `infer_context_type`.", call. = FALSE)
  }
  if (!is.null(cell_id)) {
    if (!cell_id %in% rownames(fit$calls)) {
      stop("Unknown `cell_id`.", call. = FALSE)
    }
    if (is.null(label)) {
      label <- fit$calls[cell_id, "label"]
    }
    vals <- vapply(fit$components, function(x) x[cell_id, label], numeric(1))
    main <- paste(cell_id, label, sep = " | ")
  } else {
    if (is.null(label)) {
      stop("Supply either `cell_id` or `label`.", call. = FALSE)
    }
    vals <- vapply(fit$components, function(x) mean(x[, label], na.rm = TRUE), numeric(1))
    main <- paste("Average evidence for", label)
  }
  graphics::plot(
    seq_along(vals), vals,
    xaxt = "n", xlab = "Evidence", ylab = "Standardized score",
    pch = 19, type = "b", main = main
  )
  graphics::axis(1, at = seq_along(vals), labels = names(vals), las = 2)
  invisible(vals)
}

#' Plot spatial cell type calls
#'
#' @param coords Data frame with `cell_id`, `x`, and `y`.
#' @param calls Call table from `infer_context_type`.
#' @return Invisibly returns the plotting data.
#' @export
plot_spatial_calls <- function(coords, calls) {
  if (!"cell_id" %in% colnames(coords)) {
    coords$cell_id <- rownames(coords)
  }
  plot_df <- merge(coords, calls, by = "cell_id")
  labels <- unique(plot_df$label)
  pal <- stats::setNames(seq_along(labels), labels)
  graphics::plot(
    plot_df$x, plot_df$y,
    col = pal[plot_df$label],
    pch = 19,
    xlab = "x", ylab = "y",
    main = "NicheTypeR calls"
  )
  graphics::legend("topright", legend = labels, col = pal, pch = 19, bty = "n")
  invisible(plot_df)
}
