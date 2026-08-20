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

#' Score context-specific annotation evidence
#'
#' Computes Context-Specific Annotation Evidence (CSAE) for candidate cell type
#' labels. CSAE asks whether the biological context supporting a candidate label
#' exceeds what would be expected under explicit null controls, such as random
#' spatial graphs, permuted niche priors, or shuffled pathway/LR evidence.
#'
#' This is an audit statistic, not a replacement classifier. It is intended to
#' test whether a candidate label proposed by SingleR, Seurat label transfer,
#' Azimuth, CellTypist, scmap, marker scoring, or another source is supported by
#' marker, pathway, spatial niche, and ligand-receptor evidence beyond null
#' expectations.
#'
#' @param candidate_scores Cell-by-label matrix containing candidate annotation
#'   scores, usually from `score_external_labels()` or a reference mapper.
#' @param context_scores Matrix or named list of observed cell-by-label context
#'   evidence matrices.
#' @param null_scores List of null context score matrices or lists. Each element
#'   should represent one null replicate, such as a random graph or permuted
#'   prior run.
#' @param candidate_labels Optional candidate label vector named by cell ID.
#'   Defaults to the top label in `candidate_scores`.
#' @param weights Optional named weights for context evidence.
#' @param statistic `residual` returns observed minus null mean. `z` returns
#'   residual divided by null standard deviation.
#' @param standardize Whether to robust-standardize each evidence matrix before
#'   fusion. Use only when observed and null score scales are comparable after
#'   standardization.
#' @param support_threshold Minimum candidate CSAE score for support.
#' @param min_context_margin Minimum top-vs-second CSAE margin for a supported
#'   call.
#' @param conflict_delta Minimum best-context minus candidate-context score gap
#'   required to mark a candidate as context-conflicting.
#' @param min_null_sd Minimum null standard deviation used for z-scores.
#' @return A list with CSAE score matrices, null summaries, candidate
#'   probabilities, and an `audit` data frame.
#' @export
score_context_specific_annotation <- function(candidate_scores,
                                              context_scores,
                                              null_scores,
                                              candidate_labels = NULL,
                                              weights = NULL,
                                              statistic = c("residual", "z"),
                                              standardize = FALSE,
                                              support_threshold = 0,
                                              min_context_margin = 0.05,
                                              conflict_delta = 0.1,
                                              min_null_sd = 1e-6) {
  statistic <- match.arg(statistic)
  candidate_scores <- .check_score_matrix(candidate_scores, "candidate score matrix")
  observed <- .fuse_score_input(
    context_scores,
    weights = weights,
    standardize = standardize,
    input_name = "context_scores"
  )

  null_scores <- .as_list(null_scores)
  if (length(null_scores) == 0) {
    stop("Provide at least one null context score replicate.", call. = FALSE)
  }
  null_fused <- lapply(seq_along(null_scores), function(i) {
    .fuse_score_input(
      null_scores[[i]],
      weights = weights,
      standardize = standardize,
      input_name = paste0("null_scores_", i)
    )
  })
  names(null_fused) <- paste0("null_", seq_along(null_fused))

  aligned <- .align_score_list(c(
    list(candidate = candidate_scores, observed = observed),
    null_fused
  ))
  candidate_scores <- aligned$candidate
  observed <- aligned$observed
  null_fused <- aligned[names(null_fused)]

  null_array <- array(
    unlist(null_fused, use.names = FALSE),
    dim = c(nrow(observed), ncol(observed), length(null_fused)),
    dimnames = list(rownames(observed), colnames(observed), names(null_fused))
  )
  null_mean <- apply(null_array, c(1, 2), mean, na.rm = TRUE)
  null_sd <- apply(null_array, c(1, 2), stats::sd, na.rm = TRUE)
  null_sd[!is.finite(null_sd) | null_sd < min_null_sd] <- min_null_sd
  dimnames(null_mean) <- dimnames(observed)
  dimnames(null_sd) <- dimnames(observed)

  residual <- observed - null_mean
  z <- residual / null_sd
  dimnames(residual) <- dimnames(observed)
  dimnames(z) <- dimnames(observed)
  scores <- if (identical(statistic, "z")) z else residual

  null_ge_observed <- sweep(null_array, c(1, 2), observed, FUN = ">=")
  empirical_p_value <- (1 + apply(null_ge_observed, c(1, 2), sum, na.rm = TRUE)) /
    (length(null_fused) + 1)
  dimnames(empirical_p_value) <- dimnames(observed)

  candidate_prob <- .softmax_rows(candidate_scores)
  candidate_label <- .resolve_candidate_labels(candidate_labels, candidate_scores)
  audit <- .context_specific_audit_table(
    candidate_scores = candidate_scores,
    candidate_prob = candidate_prob,
    scores = scores,
    observed = observed,
    null_mean = null_mean,
    null_sd = null_sd,
    residual = residual,
    z = z,
    empirical_p_value = empirical_p_value,
    candidate_label = candidate_label,
    support_threshold = support_threshold,
    min_context_margin = min_context_margin,
    conflict_delta = conflict_delta
  )

  list(
    scores = scores,
    observed = observed,
    null_mean = null_mean,
    null_sd = null_sd,
    residual = residual,
    z = z,
    empirical_p_value = empirical_p_value,
    candidate_scores = candidate_scores,
    candidate_probabilities = candidate_prob,
    audit = audit,
    statistic = statistic,
    n_null = length(null_fused),
    null_sources = names(null_fused),
    thresholds = list(
      support_threshold = support_threshold,
      min_context_margin = min_context_margin,
      conflict_delta = conflict_delta
    )
  )
}

.as_list <- function(x) {
  if (is.list(x) && !is.data.frame(x)) {
    x
  } else {
    list(x)
  }
}

.fuse_score_input <- function(score_input,
                              weights = NULL,
                              standardize = FALSE,
                              input_name = "scores") {
  scores <- .as_list(score_input)
  if (is.null(names(scores)) || any(names(scores) == "")) {
    names(scores) <- paste0(input_name, "_", seq_along(scores))
  }
  scores <- .align_score_list(scores)
  if (isTRUE(standardize)) {
    scores <- lapply(scores, .standardize_score)
  }
  score_names <- names(scores)
  if (is.null(weights)) {
    weights <- stats::setNames(rep(1, length(scores)), score_names)
  }
  missing_weights <- setdiff(score_names, names(weights))
  if (length(missing_weights) > 0) {
    weights[missing_weights] <- 1
  }
  weights <- weights[score_names]
  weights[is.na(weights)] <- 1
  weights[!is.finite(weights)] <- 0

  fused <- scores[[1]] * weights[1]
  if (length(scores) > 1) {
    for (i in 2:length(scores)) {
      fused <- fused + scores[[i]] * weights[i]
    }
  }
  denom <- sum(abs(weights))
  if (denom > 0) {
    fused <- fused / denom
  }
  fused
}

.resolve_candidate_labels <- function(candidate_labels, candidate_scores) {
  if (is.null(candidate_labels)) {
    candidate_label <- .top_labels(candidate_scores)
  } else {
    candidate_names <- names(candidate_labels)
    candidate_label <- as.character(candidate_labels)
    names(candidate_label) <- candidate_names
    if (!is.null(names(candidate_labels))) {
      candidate_label <- candidate_label[rownames(candidate_scores)]
    } else {
      if (length(candidate_label) != nrow(candidate_scores)) {
        stop("`candidate_labels` must be named by cell ID or match the number of score rows.", call. = FALSE)
      }
      names(candidate_label) <- rownames(candidate_scores)
    }
    if (any(is.na(candidate_label))) {
      stop("`candidate_labels` is missing labels for one or more aligned cells.", call. = FALSE)
    }
  }
  missing_labels <- setdiff(unique(candidate_label), colnames(candidate_scores))
  if (length(missing_labels) > 0) {
    stop("Candidate labels not present in score columns: ", paste(missing_labels, collapse = ", "), call. = FALSE)
  }
  candidate_label
}

.context_specific_audit_table <- function(candidate_scores,
                                          candidate_prob,
                                          scores,
                                          observed,
                                          null_mean,
                                          null_sd,
                                          residual,
                                          z,
                                          empirical_p_value,
                                          candidate_label,
                                          support_threshold,
                                          min_context_margin,
                                          conflict_delta) {
  top <- .row_top_stats(scores)
  candidate_context_score <- .row_label_values(scores, candidate_label)
  candidate_gap <- top$score - candidate_context_score
  state <- rep("context_ambiguous", nrow(scores))
  supported <- candidate_label == top$label &
    candidate_context_score >= support_threshold &
    top$margin >= min_context_margin
  conflicted <- candidate_label != top$label & candidate_gap >= conflict_delta
  not_specific <- candidate_context_score < support_threshold & !conflicted
  state[supported] <- "context_supported"
  state[conflicted] <- "context_conflict"
  state[not_specific] <- "context_not_specific"

  out <- data.frame(
    cell_id = rownames(scores),
    candidate_label = as.character(candidate_label),
    candidate_probability = as.numeric(.row_label_values(candidate_prob, candidate_label)),
    candidate_score = as.numeric(.row_label_values(candidate_scores, candidate_label)),
    context_label = as.character(top$label),
    context_score = as.numeric(top$score),
    candidate_context_score = as.numeric(candidate_context_score),
    context_margin = as.numeric(top$margin),
    context_gap = as.numeric(candidate_gap),
    candidate_observed = as.numeric(.row_label_values(observed, candidate_label)),
    candidate_null_mean = as.numeric(.row_label_values(null_mean, candidate_label)),
    candidate_null_sd = as.numeric(.row_label_values(null_sd, candidate_label)),
    candidate_residual = as.numeric(.row_label_values(residual, candidate_label)),
    candidate_z = as.numeric(.row_label_values(z, candidate_label)),
    candidate_empirical_p = as.numeric(.row_label_values(empirical_p_value, candidate_label)),
    support_state = state,
    stringsAsFactors = FALSE
  )
  rownames(out) <- out$cell_id
  out
}

.row_label_values <- function(mat, labels) {
  idx <- match(labels, colnames(mat))
  out <- rep(NA_real_, length(labels))
  keep <- !is.na(idx)
  out[keep] <- mat[cbind(seq_along(labels)[keep], idx[keep])]
  names(out) <- rownames(mat)
  out
}

.row_top_stats <- function(mat) {
  label <- .top_labels(mat)
  score <- mat[cbind(seq_len(nrow(mat)), match(label, colnames(mat)))]
  if (ncol(mat) > 1) {
    sorted <- t(apply(mat, 1, sort, decreasing = TRUE))
    margin <- sorted[, 1] - sorted[, 2]
  } else {
    margin <- score
  }
  list(label = label, score = as.numeric(score), margin = as.numeric(margin))
}
