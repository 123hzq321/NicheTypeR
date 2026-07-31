#' Summarize evidence conflicts for each cell
#'
#' @param fit Result from `infer_context_type`.
#' @param top_n Optional number of most conflicted cells to return.
#' @return A data frame containing final labels, confidence, component winners,
#'   and conflict counts.
#' @export
summarize_evidence_conflicts <- function(fit, top_n = Inf) {
  if (is.null(fit$calls) || is.null(fit$components)) {
    stop("`fit` must be returned by `infer_context_type`.", call. = FALSE)
  }
  calls <- fit$calls
  component_labels <- lapply(fit$components, .top_labels)
  out <- calls[, c("cell_id", "label", "confidence", "margin", "conflict_reason"),
               drop = FALSE]
  for (nm in names(component_labels)) {
    out[[paste0(nm, "_label")]] <- component_labels[[nm]][out$cell_id]
  }
  evidence_cols <- paste0(names(component_labels), "_label")
  evidence_matrix <- as.matrix(out[, evidence_cols, drop = FALSE])
  out$n_conflicts <- rowSums(evidence_matrix != out$label)
  out <- out[order(out$n_conflicts, -out$confidence, decreasing = TRUE), , drop = FALSE]
  if (is.finite(top_n)) {
    out <- utils::head(out, top_n)
  }
  rownames(out) <- out$cell_id
  out
}

#' Summarize cell calls into cluster-level consensus calls
#'
#' @param fit Result from `infer_context_type`.
#' @param clusters Cluster assignments. Either a named vector keyed by cell ID or
#'   a vector in the same order as `fit$calls`.
#' @param min_fraction Minimum top-label fraction required for a high-confidence
#'   cluster consensus.
#' @return A data frame with one row per cluster.
#' @export
summarize_cluster_calls <- function(fit, clusters, min_fraction = 0.6) {
  if (is.null(fit$calls)) {
    stop("`fit` must be returned by `infer_context_type`.", call. = FALSE)
  }
  calls <- fit$calls
  if (is.null(names(clusters))) {
    if (length(clusters) != nrow(calls)) {
      stop("Unnamed `clusters` must have length `nrow(fit$calls)`.", call. = FALSE)
    }
    names(clusters) <- calls$cell_id
  }
  clusters <- clusters[calls$cell_id]
  keep <- !is.na(clusters)
  calls <- calls[keep, , drop = FALSE]
  clusters <- as.character(clusters[keep])

  split_calls <- split(calls, clusters)
  pieces <- lapply(names(split_calls), function(cluster_id) {
    df <- split_calls[[cluster_id]]
    tab <- sort(table(df$label), decreasing = TRUE)
    top_label <- names(tab)[1]
    top_fraction <- as.numeric(tab[1]) / nrow(df)
    conflict_rate <- mean(df$conflict_reason != "consistent")
    data.frame(
      cluster_id = cluster_id,
      label = top_label,
      n_cells = nrow(df),
      label_fraction = top_fraction,
      median_confidence = stats::median(df$confidence, na.rm = TRUE),
      median_margin = stats::median(df$margin, na.rm = TRUE),
      conflict_rate = conflict_rate,
      consensus = ifelse(top_fraction >= min_fraction, "high", "ambiguous"),
      stringsAsFactors = FALSE
    )
  })
  out <- do.call(rbind, pieces)
  rownames(out) <- out$cluster_id
  out[order(out$cluster_id), , drop = FALSE]
}
