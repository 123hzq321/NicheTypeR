#' Write CSV templates for NicheTypeR biological priors
#'
#' @param out_dir Directory where template files should be written.
#' @param overwrite Whether to overwrite existing files.
#' @return Invisibly returns a named character vector of written file paths.
#' @export
write_nichetype_templates <- function(out_dir = ".", overwrite = FALSE) {
  if (!dir.exists(out_dir)) {
    dir.create(out_dir, recursive = TRUE)
  }
  templates <- list(
    marker_db = data.frame(
      cell_type = c("macrophage", "macrophage", "fibroblast", "fibroblast"),
      gene = c("LYZ", "EPCAM", "COL1A1", "PTPRC"),
      direction = c("positive", "negative", "positive", "negative"),
      weight = c(1, 0.5, 1, 0.5),
      evidence_note = c("canonical marker", "epithelial exclusion",
                        "matrix marker", "immune exclusion"),
      stringsAsFactors = FALSE
    ),
    label_pathways = data.frame(
      cell_type = c("macrophage", "fibroblast"),
      pathway = c("antigen_presentation", "matrix_remodeling"),
      weight = c(1, 1),
      evidence_note = c("immune function", "ECM program"),
      stringsAsFactors = FALSE
    ),
    pathway_sets = data.frame(
      pathway = c("antigen_presentation", "antigen_presentation",
                  "matrix_remodeling", "matrix_remodeling"),
      gene = c("HLA-DRA", "CD74", "COL1A1", "FN1"),
      weight = c(1, 1, 1, 1),
      stringsAsFactors = FALSE
    ),
    niche_db = data.frame(
      cell_type = c("macrophage", "fibroblast"),
      neighbor_type = c("fibroblast", "macrophage"),
      weight = c(1, 1),
      evidence_note = c("injury-associated niche", "inflammatory niche"),
      stringsAsFactors = FALSE
    ),
    lr_db = data.frame(
      sender_type = c("macrophage", "fibroblast"),
      receiver_type = c("fibroblast", "macrophage"),
      ligand = c("TGFB1", "CSF1"),
      receptor = c("TGFBR2", "CSF1R"),
      weight = c(1, 0.8),
      evidence_note = c("fibroblast activation", "macrophage survival"),
      stringsAsFactors = FALSE
    )
  )

  paths <- character(length(templates))
  names(paths) <- names(templates)
  for (nm in names(templates)) {
    path <- file.path(out_dir, paste0(nm, "_template.csv"))
    if (file.exists(path) && !overwrite) {
      stop("File exists: ", path, ". Use `overwrite = TRUE` to replace it.", call. = FALSE)
    }
    utils::write.csv(templates[[nm]], path, row.names = FALSE)
    paths[[nm]] <- path
  }
  invisible(paths)
}

.pathway_table_to_list <- function(pathway_table) {
  required <- c("pathway", "gene")
  missing <- setdiff(required, colnames(pathway_table))
  if (length(missing) > 0) {
    stop("`pathway_table` is missing columns: ", paste(missing, collapse = ", "),
         call. = FALSE)
  }
  split(pathway_table$gene, pathway_table$pathway)
}
