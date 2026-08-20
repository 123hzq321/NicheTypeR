#' Learn a spatial niche prior from labeled training cells
#'
#' Estimates candidate cell type and neighbor type compatibility from a spatial
#' graph and trusted labels. The learned table can be passed directly to
#' `score_neighborhood()`.
#'
#' @param edges Data frame from `build_niche_graph`.
#' @param labels Cell labels. Must be a named vector keyed by cell ID.
#' @param train_cells Optional vector of training cell IDs. When supplied, only
#'   edges whose source and target cells are both in `train_cells` are used for
#'   learning.
#' @param candidate_labels Optional label universe. Defaults to labels observed
#'   in `labels`.
#' @param pseudocount Additive smoothing for label-label counts.
#' @param method Weighting method. `log_enrichment` learns whether a neighbor
#'   type is enriched relative to its background frequency. `conditional` learns
#'   P(neighbor type | candidate type). `pmi` learns symmetric pointwise mutual
#'   information.
#' @param clip Optional absolute cap for learned weights.
#' @return A list containing `niche_db`, raw `counts`, and normalized `weights`.
#' @export
learn_niche_prior <- function(edges,
                              labels,
                              train_cells = NULL,
                              candidate_labels = NULL,
                              pseudocount = 1,
                              method = c("log_enrichment", "conditional", "pmi"),
                              clip = 3) {
  method <- match.arg(method)
  required_edges <- c("from", "to")
  missing_edges <- setdiff(required_edges, colnames(edges))
  if (length(missing_edges) > 0) {
    stop("`edges` is missing columns: ", paste(missing_edges, collapse = ", "), call. = FALSE)
  }
  if (is.null(names(labels))) {
    stop("`labels` must be a named vector keyed by cell ID.", call. = FALSE)
  }
  label_names <- names(labels)
  labels <- as.character(labels)
  names(labels) <- label_names
  labels <- labels[!is.na(labels)]
  if (is.null(candidate_labels)) {
    candidate_labels <- sort(unique(labels))
  }
  candidate_labels <- as.character(candidate_labels)
  label_set <- stats::setNames(candidate_labels, candidate_labels)

  edges <- edges[edges$from %in% names(labels) & edges$to %in% names(labels), , drop = FALSE]
  if (!is.null(train_cells)) {
    train_cells <- intersect(as.character(train_cells), names(labels))
    edges <- edges[edges$from %in% train_cells & edges$to %in% train_cells, , drop = FALSE]
  }
  if (nrow(edges) == 0) {
    stop("No labeled training edges are available for niche learning.", call. = FALSE)
  }

  from_label <- labels[edges$from]
  to_label <- labels[edges$to]
  keep <- from_label %in% candidate_labels & to_label %in% candidate_labels
  from_label <- from_label[keep]
  to_label <- to_label[keep]
  if (length(from_label) == 0) {
    stop("No training edges remain after filtering to candidate labels.", call. = FALSE)
  }

  counts <- matrix(
    pseudocount,
    nrow = length(candidate_labels),
    ncol = length(candidate_labels),
    dimnames = list(candidate_labels, candidate_labels)
  )
  tab <- table(
    factor(from_label, levels = candidate_labels),
    factor(to_label, levels = candidate_labels)
  )
  counts <- counts + as.matrix(tab)

  conditional <- sweep(counts, 1, rowSums(counts), "/")
  background <- colSums(counts) / sum(counts)

  weights <- switch(
    method,
    conditional = conditional,
    log_enrichment = log2(sweep(conditional, 2, background, "/")),
    pmi = {
      joint <- counts / sum(counts)
      source <- rowSums(joint)
      target <- colSums(joint)
      log2(joint / (source %o% target))
    }
  )
  weights[!is.finite(weights)] <- 0
  if (!is.null(clip)) {
    weights[weights > clip] <- clip
    weights[weights < -clip] <- -clip
  }

  niche_db <- data.frame(
    cell_type = rep(rownames(weights), times = ncol(weights)),
    neighbor_type = rep(colnames(weights), each = nrow(weights)),
    weight = as.numeric(weights),
    stringsAsFactors = FALSE
  )
  niche_db <- niche_db[order(niche_db$cell_type, niche_db$neighbor_type), , drop = FALSE]
  rownames(niche_db) <- NULL

  list(
    niche_db = niche_db,
    counts = counts,
    weights = weights,
    method = method,
    candidate_labels = label_set
  )
}
