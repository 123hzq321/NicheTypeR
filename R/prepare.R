#' Prepare a standard NicheTypeR input object
#'
#' Aligns expression, coordinates, and optional metadata to the same cells. This
#' is the small data contract used by the core scoring functions before adding
#' higher-level adapters for Seurat, SpatialExperiment, or AnnData-derived data.
#'
#' @param expr Gene-by-cell expression matrix.
#' @param coords Coordinate data frame.
#' @param metadata Optional cell metadata data frame.
#' @param cell_id_col Column containing cell IDs in `coords` and `metadata`.
#' @param coord_cols Character vector of length two naming x/y coordinate
#'   columns.
#' @return A list with aligned `expr`, `coords`, and `metadata`.
#' @export
prepare_nichetype_input <- function(expr,
                                    coords,
                                    metadata = NULL,
                                    cell_id_col = "cell_id",
                                    coord_cols = c("x", "y")) {
  expr <- .check_expr(expr)
  if (!is.data.frame(coords)) {
    coords <- as.data.frame(coords)
  }
  if (!cell_id_col %in% colnames(coords)) {
    if (is.null(rownames(coords))) {
      stop("`coords` must contain `cell_id_col` or have row names.", call. = FALSE)
    }
    coords[[cell_id_col]] <- rownames(coords)
  }
  if (!all(coord_cols %in% colnames(coords))) {
    stop("`coords` is missing coordinate columns: ",
         paste(setdiff(coord_cols, colnames(coords)), collapse = ", "),
         call. = FALSE)
  }

  coords <- coords[!duplicated(coords[[cell_id_col]]), , drop = FALSE]
  coord_cells <- as.character(coords[[cell_id_col]])
  cells <- intersect(colnames(expr), coord_cells)
  if (length(cells) == 0) {
    stop("No overlapping cells between `expr` and `coords`.", call. = FALSE)
  }

  coords <- coords[match(cells, coord_cells), , drop = FALSE]
  colnames(coords)[match(cell_id_col, colnames(coords))] <- "cell_id"
  colnames(coords)[match(coord_cols, colnames(coords))] <- c("x", "y")
  rownames(coords) <- coords$cell_id

  if (is.null(metadata)) {
    metadata <- data.frame(cell_id = cells, stringsAsFactors = FALSE)
  } else {
    if (!is.data.frame(metadata)) {
      metadata <- as.data.frame(metadata)
    }
    if (!cell_id_col %in% colnames(metadata)) {
      if (is.null(rownames(metadata))) {
        stop("`metadata` must contain `cell_id_col` or have row names.", call. = FALSE)
      }
      metadata[[cell_id_col]] <- rownames(metadata)
    }
    metadata <- metadata[!duplicated(metadata[[cell_id_col]]), , drop = FALSE]
    missing_meta <- setdiff(cells, as.character(metadata[[cell_id_col]]))
    if (length(missing_meta) > 0) {
      stop("`metadata` is missing cells: ",
           paste(utils::head(missing_meta, 5), collapse = ", "),
           if (length(missing_meta) > 5) " ..." else "",
           call. = FALSE)
    }
    metadata <- metadata[match(cells, metadata[[cell_id_col]]), , drop = FALSE]
    colnames(metadata)[match(cell_id_col, colnames(metadata))] <- "cell_id"
  }
  rownames(metadata) <- metadata$cell_id

  list(
    expr = expr[, cells, drop = FALSE],
    coords = coords,
    metadata = metadata
  )
}

#' Build reference profiles from labeled cells
#'
#' @param expr Gene-by-cell expression matrix.
#' @param labels Cell labels. Either a named vector keyed by cell ID or a vector
#'   in the same order as `colnames(expr)`.
#' @param min_cells Minimum number of cells required for a label.
#' @return A gene-by-label reference profile matrix.
#' @export
make_reference_profiles <- function(expr, labels, min_cells = 3) {
  expr <- .check_expr(expr)
  if (is.null(names(labels))) {
    if (length(labels) != ncol(expr)) {
      stop("Unnamed `labels` must have length `ncol(expr)`.", call. = FALSE)
    }
    names(labels) <- colnames(expr)
  }
  labels <- labels[colnames(expr)]
  keep <- !is.na(labels)
  labels <- labels[keep]
  expr <- expr[, names(labels), drop = FALSE]

  groups <- split(names(labels), labels)
  groups <- groups[lengths(groups) >= min_cells]
  if (length(groups) == 0) {
    stop("No label has at least `min_cells` cells.", call. = FALSE)
  }

  profiles <- sapply(groups, function(cells) {
    rowMeans(expr[, cells, drop = FALSE], na.rm = TRUE)
  })
  if (is.null(dim(profiles))) {
    profiles <- matrix(profiles, ncol = 1,
                       dimnames = list(rownames(expr), names(groups)))
  }
  profiles
}
