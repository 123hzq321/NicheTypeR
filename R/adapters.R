#' Prepare NicheTypeR input from a Seurat object
#'
#' This adapter avoids a hard Seurat dependency. It requires `SeuratObject` only
#' when called.
#'
#' @param object Seurat object.
#' @param assay Assay name.
#' @param layer Layer name for Seurat v5 objects.
#' @param slot Slot name fallback for older Seurat objects.
#' @param coords Optional coordinate data frame. If `NULL`, the function tries
#'   common metadata coordinate columns.
#' @param metadata Optional metadata override.
#' @param coord_cols Coordinate columns.
#' @return A standard NicheTypeR input object.
#' @export
prepare_from_seurat <- function(object,
                                assay = NULL,
                                layer = "data",
                                slot = "data",
                                coords = NULL,
                                metadata = NULL,
                                coord_cols = c("x", "y")) {
  if (!requireNamespace("SeuratObject", quietly = TRUE)) {
    stop("`prepare_from_seurat()` requires the SeuratObject package.", call. = FALSE)
  }
  expr <- tryCatch(
    SeuratObject::LayerData(object, assay = assay, layer = layer),
    error = function(e) SeuratObject::GetAssayData(object, assay = assay, slot = slot)
  )
  if (is.null(metadata)) {
    metadata <- object[[]]
    metadata$cell_id <- rownames(metadata)
  }
  if (is.null(coords)) {
    candidates <- list(
      c("x", "y"),
      c("imagerow", "imagecol"),
      c("row", "col"),
      c("spatial_1", "spatial_2")
    )
    found <- NULL
    for (candidate in candidates) {
      if (all(candidate %in% colnames(metadata))) {
        found <- candidate
        break
      }
    }
    if (is.null(found)) {
      stop("Supply `coords` or add coordinate columns to Seurat metadata.", call. = FALSE)
    }
    coords <- metadata[, c("cell_id", found), drop = FALSE]
    colnames(coords) <- c("cell_id", "x", "y")
    coord_cols <- c("x", "y")
  }
  prepare_nichetype_input(expr, coords, metadata, coord_cols = coord_cols)
}

#' Prepare NicheTypeR input from a SpatialExperiment object
#'
#' @param object SpatialExperiment object.
#' @param assay Assay name.
#' @param metadata Optional metadata override.
#' @return A standard NicheTypeR input object.
#' @export
prepare_from_spatial_experiment <- function(object,
                                            assay = "logcounts",
                                            metadata = NULL) {
  if (!requireNamespace("SpatialExperiment", quietly = TRUE)) {
    stop("`prepare_from_spatial_experiment()` requires SpatialExperiment.", call. = FALSE)
  }
  if (!requireNamespace("SummarizedExperiment", quietly = TRUE)) {
    stop("`prepare_from_spatial_experiment()` requires SummarizedExperiment.", call. = FALSE)
  }
  expr <- SummarizedExperiment::assay(object, assay)
  coords <- as.data.frame(SpatialExperiment::spatialCoords(object))
  coords$cell_id <- colnames(expr)
  if (ncol(coords) < 3) {
    stop("SpatialExperiment spatial coordinates must contain at least two columns.", call. = FALSE)
  }
  coord_cols <- colnames(coords)[seq_len(2)]
  coord_cols <- setdiff(coord_cols, "cell_id")
  if (length(coord_cols) < 2) {
    coord_cols <- colnames(coords)[seq_len(2)]
  }
  if (is.null(metadata)) {
    metadata <- as.data.frame(SummarizedExperiment::colData(object))
    metadata$cell_id <- colnames(expr)
  }
  prepare_nichetype_input(expr, coords, metadata, coord_cols = coord_cols[seq_len(2)])
}
