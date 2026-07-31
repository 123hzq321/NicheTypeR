.check_expr <- function(expr) {
  if (!is.matrix(expr)) {
    expr <- as.matrix(expr)
  }
  if (is.null(rownames(expr)) || is.null(colnames(expr))) {
    stop("`expr` must have gene row names and cell column names.", call. = FALSE)
  }
  storage.mode(expr) <- "double"
  expr
}

.check_score_matrix <- function(x, name = "score matrix") {
  if (!is.matrix(x)) {
    x <- as.matrix(x)
  }
  if (is.null(rownames(x)) || is.null(colnames(x))) {
    stop("Each ", name, " must have cell row names and label column names.", call. = FALSE)
  }
  storage.mode(x) <- "double"
  x
}

.z_by_gene <- function(expr, cap = 3) {
  expr <- .check_expr(expr)
  mu <- rowMeans(expr, na.rm = TRUE)
  sigma <- apply(expr, 1, stats::sd, na.rm = TRUE)
  sigma[!is.finite(sigma) | sigma == 0] <- 1
  z <- sweep(expr, 1, mu, "-")
  z <- sweep(z, 1, sigma, "/")
  z[z > cap] <- cap
  z[z < -cap] <- -cap
  z
}

.weighted_col_mean <- function(mat, weights = NULL) {
  if (nrow(mat) == 0) {
    return(rep(NA_real_, ncol(mat)))
  }
  if (is.null(weights)) {
    return(colMeans(mat, na.rm = TRUE))
  }
  weights <- as.numeric(weights)
  if (length(weights) != nrow(mat)) {
    stop("`weights` length must match number of rows in `mat`.", call. = FALSE)
  }
  weights[!is.finite(weights)] <- 0
  denom <- sum(abs(weights))
  if (denom == 0) {
    return(rep(NA_real_, ncol(mat)))
  }
  as.numeric(crossprod(weights, mat) / denom)
}

.minmax01 <- function(x) {
  rng <- range(x, finite = TRUE)
  if (!all(is.finite(rng)) || diff(rng) == 0) {
    return(rep(0.5, length(x)))
  }
  (x - rng[1]) / diff(rng)
}

.softmax_rows <- function(x, temperature = 1) {
  x <- as.matrix(x)
  temperature <- max(temperature, .Machine$double.eps)
  z <- x / temperature
  z <- z - apply(z, 1, max, na.rm = TRUE)
  ez <- exp(z)
  denom <- rowSums(ez, na.rm = TRUE)
  denom[!is.finite(denom) | denom == 0] <- 1
  sweep(ez, 1, denom, "/")
}

.standardize_score <- function(x) {
  x <- as.matrix(x)
  out <- x
  for (j in seq_len(ncol(x))) {
    vals <- x[, j]
    med <- stats::median(vals, na.rm = TRUE)
    madv <- stats::mad(vals, constant = 1.4826, na.rm = TRUE)
    if (!is.finite(madv) || madv == 0) {
      sdv <- stats::sd(vals, na.rm = TRUE)
      madv <- if (is.finite(sdv) && sdv > 0) sdv else 1
    }
    out[, j] <- (vals - med) / madv
  }
  out[!is.finite(out)] <- 0
  out
}

.align_score_list <- function(scores) {
  if (!is.list(scores) || length(scores) == 0) {
    stop("`scores` must be a non-empty named list of score matrices.", call. = FALSE)
  }
  if (is.null(names(scores)) || any(names(scores) == "")) {
    names(scores) <- paste0("evidence_", seq_along(scores))
  }
  score_names <- names(scores)
  scores <- lapply(seq_along(scores), function(i) {
    .check_score_matrix(scores[[i]], score_names[i])
  })
  names(scores) <- score_names
  cells <- Reduce(intersect, lapply(scores, rownames))
  labels <- Reduce(intersect, lapply(scores, colnames))
  if (length(cells) == 0 || length(labels) == 0) {
    stop("Score matrices must share at least one cell and one label.", call. = FALSE)
  }
  lapply(scores, function(x) x[cells, labels, drop = FALSE])
}

.top_labels <- function(score) {
  labels <- colnames(score)
  out <- labels[max.col(score, ties.method = "first")]
  names(out) <- rownames(score)
  out
}
