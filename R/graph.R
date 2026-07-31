#' Build a spatial niche graph
#'
#' @param coords Data frame with `cell_id`, `x`, and `y` columns. Row names are
#'   used as cell identifiers when `cell_id` is absent.
#' @param k Number of nearest neighbors to retain for each cell.
#' @param radius Optional maximum spatial distance. If supplied, neighbors
#'   outside the radius are removed after k-nearest-neighbor selection.
#' @param group_col Optional column name used to build independent graphs within
#'   each sample, section, replicate, or field of view.
#' @param backend Nearest-neighbor backend. `auto` uses the optional `FNN`
#'   package when available and otherwise falls back to the base R `dist`
#'   backend.
#' @return A data frame with `from`, `to`, and `distance` columns.
#' @export
build_niche_graph <- function(coords,
                              k = 8,
                              radius = NULL,
                              group_col = NULL,
                              backend = c("auto", "FNN", "dist")) {
  backend <- match.arg(backend)
  if (!is.data.frame(coords)) {
    coords <- as.data.frame(coords)
  }
  if (!"cell_id" %in% colnames(coords)) {
    if (is.null(rownames(coords))) {
      stop("`coords` must contain `cell_id` or have row names.", call. = FALSE)
    }
    coords$cell_id <- rownames(coords)
  }
  required <- c("cell_id", "x", "y")
  missing <- setdiff(required, colnames(coords))
  if (length(missing) > 0) {
    stop("`coords` is missing columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  if (!is.null(group_col) && !group_col %in% colnames(coords)) {
    stop("`coords` does not contain `group_col`: ", group_col, call. = FALSE)
  }
  keep_cols <- unique(c(required, group_col))
  coords <- coords[!duplicated(coords$cell_id), keep_cols, drop = FALSE]

  if (!is.null(group_col)) {
    pieces <- lapply(split(coords, coords[[group_col]]), function(df) {
      .build_niche_graph_one_group(
        df[, required, drop = FALSE],
        k = k,
        radius = radius,
        backend = backend
      )
    })
    edges <- do.call(rbind, pieces)
    rownames(edges) <- NULL
    return(edges)
  }

  .build_niche_graph_one_group(
    coords[, required, drop = FALSE],
    k = k,
    radius = radius,
    backend = backend
  )
}

.build_niche_graph_one_group <- function(coords,
                                         k = 8,
                                         radius = NULL,
                                         backend = c("auto", "FNN", "dist")) {
  backend <- match.arg(backend)
  rownames(coords) <- coords$cell_id

  xy <- as.matrix(coords[, c("x", "y")])
  storage.mode(xy) <- "double"
  k <- min(as.integer(k), nrow(xy) - 1L)
  if (k < 1) {
    stop("`k` must be at least 1 and there must be at least two cells.", call. = FALSE)
  }

  if (identical(backend, "auto")) {
    backend <- if (requireNamespace("FNN", quietly = TRUE)) "FNN" else "dist"
  }

  if (identical(backend, "FNN")) {
    if (!requireNamespace("FNN", quietly = TRUE)) {
      stop("`backend = \"FNN\"` requires the optional FNN package.", call. = FALSE)
    }
    nn <- FNN::get.knn(xy, k = k)
    edges <- .knn_to_edges(
      cells = rownames(coords),
      nn_index = nn$nn.index,
      nn_distance = nn$nn.dist
    )
  } else {
    d <- as.matrix(stats::dist(xy))
    diag(d) <- Inf
    edge_list <- vector("list", nrow(d))
    for (i in seq_len(nrow(d))) {
      ord <- order(d[i, ], decreasing = FALSE)[seq_len(k)]
      edge_list[[i]] <- data.frame(
        from = rownames(d)[i],
        to = colnames(d)[ord],
        distance = as.numeric(d[i, ord]),
        stringsAsFactors = FALSE
      )
    }
    edges <- do.call(rbind, edge_list)
    rownames(edges) <- NULL
  }
  if (!is.null(radius)) {
    edges <- edges[edges$distance <= radius, , drop = FALSE]
  }
  edges
}

.knn_to_edges <- function(cells, nn_index, nn_distance) {
  rows <- vector("list", nrow(nn_index))
  for (i in seq_len(nrow(nn_index))) {
    rows[[i]] <- data.frame(
      from = cells[i],
      to = cells[nn_index[i, ]],
      distance = as.numeric(nn_distance[i, ]),
      stringsAsFactors = FALSE
    )
  }
  edges <- do.call(rbind, rows)
  rownames(edges) <- NULL
  edges
}
