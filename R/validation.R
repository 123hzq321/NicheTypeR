.macro_f1_vec <- function(predicted, truth) {
  labels <- sort(unique(c(predicted, truth)))
  f1 <- numeric(length(labels))
  for (i in seq_along(labels)) {
    label <- labels[i]
    tp <- sum(predicted == label & truth == label, na.rm = TRUE)
    fp <- sum(predicted == label & truth != label, na.rm = TRUE)
    fn <- sum(predicted != label & truth == label, na.rm = TRUE)
    precision <- if ((tp + fp) > 0) tp / (tp + fp) else NA_real_
    recall <- if ((tp + fn) > 0) tp / (tp + fn) else NA_real_
    f1[i] <- if (is.finite(precision + recall) && (precision + recall) > 0) {
      2 * precision * recall / (precision + recall)
    } else {
      NA_real_
    }
  }
  mean(f1, na.rm = TRUE)
}

#' Compare two paired call sets against known labels
#'
#' @param calls_a Baseline call table or named character vector.
#' @param calls_b Comparator call table or named character vector.
#' @param truth Known labels. Must be named by cell ID unless both call inputs
#'   are data frames with `cell_id`.
#' @param n_boot Number of bootstrap resamples for paired metric differences.
#' @param seed Random seed.
#' @return A list with summary metrics, McNemar-style exact binomial test, and
#'   bootstrap confidence intervals for accuracy and macro F1 differences.
#' @export
compare_call_sets <- function(calls_a,
                              calls_b,
                              truth,
                              n_boot = 2000,
                              seed = 1) {
  pred_a <- .extract_pred_vector(calls_a)
  pred_b <- .extract_pred_vector(calls_b)
  common <- Reduce(intersect, list(names(pred_a), names(pred_b), names(truth)))
  if (length(common) == 0) {
    stop("No overlapping named cells across calls and truth.", call. = FALSE)
  }
  pred_a <- as.character(pred_a[common])
  pred_b <- as.character(pred_b[common])
  truth <- as.character(truth[common])

  a_correct <- pred_a == truth
  b_correct <- pred_b == truth
  a_wrong_b_right <- sum(!a_correct & b_correct)
  a_right_b_wrong <- sum(a_correct & !b_correct)
  discordant <- a_wrong_b_right + a_right_b_wrong
  p_value <- if (discordant > 0) {
    stats::binom.test(min(a_wrong_b_right, a_right_b_wrong), discordant, p = 0.5)$p.value
  } else {
    1
  }

  metric_diff <- function(pa, pb, tr) {
    c(
      accuracy = mean(pb == tr) - mean(pa == tr),
      macro_f1 = .macro_f1_vec(pb, tr) - .macro_f1_vec(pa, tr)
    )
  }
  observed <- metric_diff(pred_a, pred_b, truth)

  set.seed(seed)
  boot <- replicate(n_boot, {
    idx <- sample.int(length(truth), length(truth), replace = TRUE)
    metric_diff(pred_a[idx], pred_b[idx], truth[idx])
  })
  ci <- t(apply(boot, 1, stats::quantile, probs = c(0.025, 0.975), na.rm = TRUE))
  colnames(ci) <- c("ci_low", "ci_high")

  list(
    n = length(common),
    metrics = data.frame(
      metric = names(observed),
      diff = as.numeric(observed),
      ci_low = ci[, "ci_low"],
      ci_high = ci[, "ci_high"],
      stringsAsFactors = FALSE
    ),
    paired = data.frame(
      baseline_wrong_comparator_right = a_wrong_b_right,
      baseline_right_comparator_wrong = a_right_b_wrong,
      discordant = discordant,
      exact_p = p_value,
      stringsAsFactors = FALSE
    )
  )
}

.extract_pred_vector <- function(calls) {
  if (is.data.frame(calls)) {
    required <- c("cell_id", "label")
    missing <- setdiff(required, colnames(calls))
    if (length(missing) > 0) {
      stop("Call data frames must contain `cell_id` and `label`.", call. = FALSE)
    }
    out <- as.character(calls$label)
    names(out) <- calls$cell_id
    out
  } else {
    out <- as.character(calls)
    if (is.null(names(out))) {
      stop("Call vectors must be named by cell ID.", call. = FALSE)
    }
    out
  }
}

#' Make group-blocked folds
#'
#' Creates folds where all cells from the same group are assigned to the same
#' fold. This is intended for leave-FOV, leave-slide, or leave-replicate
#' validation.
#'
#' @param labels Named cell labels.
#' @param groups Named group IDs, such as FOV, section, slide, or replicate.
#' @param k Number of folds.
#' @param seed Random seed.
#' @return A list of folds, each with `train` and `test` cell IDs.
#' @export
make_group_folds <- function(labels, groups, k = 5, seed = 1) {
  if (is.null(names(labels)) || is.null(names(groups))) {
    stop("`labels` and `groups` must be named by cell ID.", call. = FALSE)
  }
  cells <- intersect(names(labels), names(groups))
  labels <- labels[cells]
  groups <- groups[cells]
  group_ids <- unique(groups)
  set.seed(seed)
  group_ids <- sample(group_ids)

  group_size <- stats::setNames(as.numeric(table(groups)[group_ids]), group_ids)
  fold_groups <- vector("list", k)
  fold_sizes <- rep(0, k)
  for (group in group_ids[order(group_size, decreasing = TRUE)]) {
    idx <- which.min(fold_sizes)
    fold_groups[[idx]] <- c(fold_groups[[idx]], group)
    fold_sizes[idx] <- fold_sizes[idx] + group_size[group]
  }

  lapply(seq_len(k), function(i) {
    test <- cells[groups %in% fold_groups[[i]]]
    train <- setdiff(cells, test)
    list(train = train, test = test, groups = fold_groups[[i]])
  })
}

#' Generate a random spatial null graph within groups
#'
#' Preserves the out-degree of each cell but replaces neighbors with random
#' cells from the same group.
#'
#' @param edges Edge table with `from` and `to`.
#' @param coords Coordinate table with `cell_id` and `group_col`.
#' @param group_col Column used to restrict random neighbors.
#' @param seed Random seed.
#' @return Randomized edge table.
#' @export
spatial_null_edges <- function(edges, coords, group_col, seed = 1) {
  required_edges <- c("from", "to")
  missing_edges <- setdiff(required_edges, colnames(edges))
  if (length(missing_edges) > 0) {
    stop("`edges` is missing columns: ", paste(missing_edges, collapse = ", "), call. = FALSE)
  }
  if (!all(c("cell_id", group_col) %in% colnames(coords))) {
    stop("`coords` must contain `cell_id` and `group_col`.", call. = FALSE)
  }
  set.seed(seed)
  degree <- table(edges$from)
  group_by_cell <- stats::setNames(as.character(coords[[group_col]]), coords$cell_id)
  cells_by_group <- split(coords$cell_id, coords[[group_col]])

  pieces <- lapply(names(degree), function(cell) {
    group <- group_by_cell[cell]
    candidates <- setdiff(cells_by_group[[group]], cell)
    if (length(candidates) == 0) {
      return(NULL)
    }
    n <- as.integer(degree[cell])
    data.frame(
      from = cell,
      to = sample(candidates, n, replace = length(candidates) < n),
      distance = NA_real_,
      stringsAsFactors = FALSE
    )
  })
  out <- do.call(rbind, pieces)
  rownames(out) <- NULL
  out
}

#' Permute a learned niche prior
#'
#' Randomly permutes cell type names in a niche prior while keeping weight values
#' intact. Useful as a learned-prior null control.
#'
#' @param niche_db Niche prior table.
#' @param seed Random seed.
#' @return Permuted niche prior table.
#' @export
permute_niche_prior <- function(niche_db, seed = 1) {
  required <- c("cell_type", "neighbor_type", "weight")
  missing <- setdiff(required, colnames(niche_db))
  if (length(missing) > 0) {
    stop("`niche_db` is missing columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  set.seed(seed)
  labels <- sort(unique(c(niche_db$cell_type, niche_db$neighbor_type)))
  mapping <- stats::setNames(sample(labels), labels)
  out <- niche_db
  out$cell_type <- unname(mapping[out$cell_type])
  out$neighbor_type <- unname(mapping[out$neighbor_type])
  out
}
