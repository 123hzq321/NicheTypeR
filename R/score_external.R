#' Convert external annotation labels into a NicheTypeR score matrix
#'
#' This helper lets labels from tools such as SingleR, Seurat label transfer,
#' CellTypist or scmap enter NicheTypeR as reference evidence without adding
#' those tools as hard dependencies. The external tool is run by the user; this
#' function converts its predicted labels and optional confidence scores into a
#' cell-by-label score matrix that can be fused with marker, pathway,
#' neighborhood and ligand-receptor evidence.
#'
#' @param predictions Data frame containing one row per cell or spot.
#' @param candidate_labels Optional full label universe. Defaults to labels
#'   observed in `predictions`.
#' @param cell_id_col Column containing cell or spot IDs.
#' @param label_col Column containing predicted labels.
#' @param score_col Optional numeric score column. If supplied, it is used as
#'   the score assigned to the predicted label.
#' @param confidence_col Optional numeric confidence column used when
#'   `score_col` is not supplied.
#' @param predicted_score Score assigned to the predicted label when neither
#'   `score_col` nor `confidence_col` is supplied.
#' @param background_score Score assigned to non-predicted candidate labels.
#' @param unknown_labels Labels to ignore, such as unassigned or unknown calls.
#' @return A cell-by-label score matrix.
#' @export
score_external_labels <- function(predictions,
                                  candidate_labels = NULL,
                                  cell_id_col = "cell_id",
                                  label_col = "label",
                                  score_col = NULL,
                                  confidence_col = NULL,
                                  predicted_score = 1,
                                  background_score = 0,
                                  unknown_labels = c("unknown", "unassigned", "ambiguous", "NA")) {
  if (!is.data.frame(predictions)) {
    stop("`predictions` must be a data frame.", call. = FALSE)
  }
  required <- c(cell_id_col, label_col)
  missing <- setdiff(required, colnames(predictions))
  if (length(missing) > 0) {
    stop("Missing required prediction columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  if (!is.null(score_col) && !score_col %in% colnames(predictions)) {
    stop("`score_col` was not found in `predictions`.", call. = FALSE)
  }
  if (!is.null(confidence_col) && !confidence_col %in% colnames(predictions)) {
    stop("`confidence_col` was not found in `predictions`.", call. = FALSE)
  }

  cell_ids <- as.character(predictions[[cell_id_col]])
  labels <- as.character(predictions[[label_col]])
  unknown <- tolower(labels) %in% tolower(unknown_labels) | is.na(labels) | labels == ""
  if (is.null(candidate_labels)) {
    candidate_labels <- sort(unique(labels[!unknown]))
  } else {
    candidate_labels <- as.character(candidate_labels)
  }
  if (length(candidate_labels) == 0) {
    stop("No candidate labels are available.", call. = FALSE)
  }

  scores <- rep(as.numeric(predicted_score), length(labels))
  if (!is.null(score_col)) {
    scores <- suppressWarnings(as.numeric(predictions[[score_col]]))
  } else if (!is.null(confidence_col)) {
    scores <- suppressWarnings(as.numeric(predictions[[confidence_col]]))
  }
  scores[!is.finite(scores)] <- as.numeric(predicted_score)

  out <- matrix(
    as.numeric(background_score),
    nrow = length(cell_ids),
    ncol = length(candidate_labels),
    dimnames = list(cell_ids, candidate_labels)
  )
  label_index <- match(labels, candidate_labels)
  keep <- !unknown & !is.na(label_index) & !duplicated(cell_ids)
  out[cbind(seq_along(cell_ids)[keep], label_index[keep])] <- scores[keep]
  duplicated_cells <- duplicated(rownames(out))
  if (any(duplicated_cells)) {
    out <- out[!duplicated_cells, , drop = FALSE]
  }
  out
}

#' Import an external cell-by-label score matrix
#'
#' @param score_matrix Numeric matrix-like object with cell IDs as rows and
#'   candidate labels as columns.
#' @param cells Optional cell IDs to retain or add.
#' @param candidate_labels Optional label universe to retain or add.
#' @param fill_missing Score used for missing cells or labels.
#' @return A cell-by-label score matrix aligned to requested cells and labels.
#' @export
score_external_matrix <- function(score_matrix,
                                  cells = NULL,
                                  candidate_labels = NULL,
                                  fill_missing = 0) {
  score_matrix <- .check_score_matrix(score_matrix, "external score matrix")
  if (is.null(cells)) {
    cells <- rownames(score_matrix)
  } else {
    cells <- as.character(cells)
  }
  if (is.null(candidate_labels)) {
    candidate_labels <- colnames(score_matrix)
  } else {
    candidate_labels <- as.character(candidate_labels)
  }
  out <- matrix(
    as.numeric(fill_missing),
    nrow = length(cells),
    ncol = length(candidate_labels),
    dimnames = list(cells, candidate_labels)
  )
  common_cells <- intersect(cells, rownames(score_matrix))
  common_labels <- intersect(candidate_labels, colnames(score_matrix))
  out[common_cells, common_labels] <- score_matrix[common_cells, common_labels, drop = FALSE]
  out
}

#' Audit an external annotation with additional NicheTypeR evidence
#'
#' @param external_scores Cell-by-label score matrix from an external annotation
#'   tool or from `score_external_labels`.
#' @param ... Additional named NicheTypeR evidence matrices, such as `marker`,
#'   `pathway`, `neighborhood`, or `ligand_receptor`.
#' @param reference_name Name assigned to the external score matrix.
#' @param weights Optional evidence weights passed to `infer_context_type`.
#' @param temperature Softmax temperature.
#' @param min_margin Minimum top-vs-second probability margin.
#' @param component_min_margin Minimum component margin required for conflicts.
#' @return Output from `infer_context_type`.
#' @export
audit_external_annotation <- function(external_scores,
                                      ...,
                                      reference_name = "reference",
                                      weights = NULL,
                                      temperature = 1,
                                      min_margin = 0.08,
                                      component_min_margin = 0.05) {
  scores <- list(...)
  scores[[reference_name]] <- score_external_matrix(external_scores)
  scores <- scores[c(reference_name, setdiff(names(scores), reference_name))]
  infer_context_type(
    scores = scores,
    weights = weights,
    temperature = temperature,
    min_margin = min_margin,
    component_min_margin = component_min_margin
  )
}
