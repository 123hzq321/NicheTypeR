#' Score spatial context after explicit null correction
#'
#' Computes a context-specific neighborhood score by subtracting the expected
#' neighborhood compatibility under spatial and/or prior null controls. This is
#' the method-level upgrade from "use spatial context" to "use only the part of
#' spatial context that exceeds random graph or permuted-prior explanations".
#'
#' @param edges Observed spatial graph edge table.
#' @param prior_scores Cell-by-label prior score matrix.
#' @param niche_db Learned or curated niche prior table.
#' @param null_edges Optional null graph or list of null graphs, such as outputs
#'   from `spatial_null_edges()`.
#' @param null_niche_db Optional permuted niche prior or list of permuted niche
#'   priors, such as outputs from `permute_niche_prior()`.
#' @param statistic `residual` returns observed minus null mean. `z` returns the
#'   residual divided by null standard deviation.
#' @param temperature Softmax temperature passed to `score_neighborhood()`.
#' @param min_null_sd Minimum null standard deviation used for z-scores.
#' @return A list with `scores`, `observed`, `null_mean`, `null_sd`, and metadata.
#' @export
score_context_specific_neighborhood <- function(edges,
                                                prior_scores,
                                                niche_db,
                                                null_edges = NULL,
                                                null_niche_db = NULL,
                                                statistic = c("residual", "z"),
                                                temperature = 1,
                                                min_null_sd = 1e-6) {
  statistic <- match.arg(statistic)
  observed <- score_neighborhood(
    edges = edges,
    prior_scores = prior_scores,
    niche_db = niche_db,
    temperature = temperature
  )

  null_scores <- list()
  null_sources <- character()

  if (!is.null(null_edges)) {
    null_edges <- .as_list(null_edges)
    for (i in seq_along(null_edges)) {
      null_scores[[length(null_scores) + 1]] <- score_neighborhood(
        edges = null_edges[[i]],
        prior_scores = prior_scores,
        niche_db = niche_db,
        temperature = temperature
      )
      null_sources <- c(null_sources, paste0("null_edges_", i))
    }
  }

  if (!is.null(null_niche_db)) {
    null_niche_db <- .as_list(null_niche_db)
    for (i in seq_along(null_niche_db)) {
      null_scores[[length(null_scores) + 1]] <- score_neighborhood(
        edges = edges,
        prior_scores = prior_scores,
        niche_db = null_niche_db[[i]],
        temperature = temperature
      )
      null_sources <- c(null_sources, paste0("null_niche_db_", i))
    }
  }

  if (length(null_scores) == 0) {
    stop("Provide at least one `null_edges` or `null_niche_db` control.", call. = FALSE)
  }

  null_scores <- lapply(null_scores, function(x) {
    x <- .check_score_matrix(x, "null score")
    x[rownames(observed), colnames(observed), drop = FALSE]
  })

  null_array <- array(
    unlist(null_scores, use.names = FALSE),
    dim = c(nrow(observed), ncol(observed), length(null_scores)),
    dimnames = list(rownames(observed), colnames(observed), null_sources)
  )
  null_mean <- apply(null_array, c(1, 2), mean, na.rm = TRUE)
  null_sd <- apply(null_array, c(1, 2), stats::sd, na.rm = TRUE)
  null_sd[!is.finite(null_sd) | null_sd < min_null_sd] <- min_null_sd

  residual <- observed - null_mean
  scores <- if (identical(statistic, "z")) {
    residual / null_sd
  } else {
    residual
  }
  dimnames(scores) <- dimnames(observed)

  list(
    scores = scores,
    observed = observed,
    null_mean = null_mean,
    null_sd = null_sd,
    residual = residual,
    statistic = statistic,
    n_null = length(null_scores),
    null_sources = null_sources
  )
}

.as_list <- function(x) {
  if (is.list(x) && !is.data.frame(x)) {
    x
  } else {
    list(x)
  }
}
