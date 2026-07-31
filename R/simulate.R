#' Simulate a small spatial transcriptomics dataset
#'
#' Creates a toy gene-by-cell expression matrix with spatial coordinates, true
#' labels, marker definitions, pathway definitions, niche priors, and
#' ligand-receptor priors. The data are intentionally simple and are meant for
#' package development, examples, and smoke tests.
#'
#' @param n_per_type Number of cells to simulate for each cell type.
#' @param seed Random seed.
#' @return A named list containing expression, metadata, coordinates, and small
#'   biological prior tables.
#' @export
simulate_nichetype_data <- function(n_per_type = 60, seed = 1) {
  set.seed(seed)

  cell_types <- c("macrophage", "fibroblast", "epithelial", "endothelial", "T_cell")
  markers <- list(
    macrophage = c("LYZ", "LST1", "AIF1", "C1QA", "CD68"),
    fibroblast = c("COL1A1", "COL1A2", "DCN", "LUM", "PDGFRA"),
    epithelial = c("EPCAM", "KRT8", "KRT18", "MUC1", "CDH1"),
    endothelial = c("PECAM1", "VWF", "KDR", "EMCN", "ESAM"),
    T_cell = c("CD3D", "CD3E", "TRAC", "IL7R", "NKG7")
  )
  pathway_sets <- list(
    antigen_presentation = c("HLA-DRA", "HLA-DPA1", "HLA-DPB1", "CD74", "B2M"),
    matrix_remodeling = c("COL1A1", "COL1A2", "MMP2", "TIMP1", "FN1"),
    epithelial_barrier = c("EPCAM", "KRT8", "KRT18", "CDH1", "CLDN4"),
    angiogenesis = c("PECAM1", "VWF", "KDR", "ENG", "FLT1"),
    cytotoxic_activation = c("CD3D", "TRAC", "NKG7", "GZMB", "PRF1")
  )
  lr_genes <- c("TGFB1", "TGFBR2", "PDGFA", "PDGFRA", "CSF1", "CSF1R",
                "CXCL12", "CXCR4", "VEGFA", "KDR", "CCL5", "CCR5")
  background <- paste0("GENE", sprintf("%03d", seq_len(80)))
  genes <- unique(c(unlist(markers), unlist(pathway_sets), lr_genes, background))

  centers <- data.frame(
    cell_type = cell_types,
    x = c(0, 2.1, 4.2, 1.2, 3.6),
    y = c(0.3, 1.6, 0.2, 3.5, 3.2),
    stringsAsFactors = FALSE
  )

  cell_ids <- unlist(lapply(cell_types, function(ct) {
    paste(ct, seq_len(n_per_type), sep = "_")
  }), use.names = FALSE)
  labels <- rep(cell_types, each = n_per_type)

  coords <- do.call(rbind, lapply(cell_types, function(ct) {
    center <- centers[centers$cell_type == ct, ]
    data.frame(
      cell_id = paste(ct, seq_len(n_per_type), sep = "_"),
      x = stats::rnorm(n_per_type, center$x, 0.48),
      y = stats::rnorm(n_per_type, center$y, 0.48),
      stringsAsFactors = FALSE
    )
  }))
  rownames(coords) <- coords$cell_id

  expr <- matrix(stats::rpois(length(genes) * length(cell_ids), lambda = 1),
                 nrow = length(genes),
                 dimnames = list(genes, cell_ids))

  boost <- function(cell_type, gene_set, lambda) {
    cells <- cell_ids[labels == cell_type]
    present <- intersect(gene_set, rownames(expr))
    expr[present, cells] <<- expr[present, cells, drop = FALSE] +
      matrix(stats::rpois(length(present) * length(cells), lambda = lambda),
             nrow = length(present))
  }

  for (ct in cell_types) {
    boost(ct, markers[[ct]], lambda = 8)
  }
  boost("macrophage", pathway_sets$antigen_presentation, lambda = 6)
  boost("fibroblast", pathway_sets$matrix_remodeling, lambda = 6)
  boost("epithelial", pathway_sets$epithelial_barrier, lambda = 6)
  boost("endothelial", pathway_sets$angiogenesis, lambda = 6)
  boost("T_cell", pathway_sets$cytotoxic_activation, lambda = 6)

  boost("macrophage", c("TGFB1", "CSF1R", "CCL5"), lambda = 4)
  boost("fibroblast", c("TGFBR2", "PDGFRA", "CXCL12"), lambda = 4)
  boost("epithelial", c("TGFB1", "VEGFA"), lambda = 3)
  boost("endothelial", c("KDR", "VEGFA"), lambda = 4)
  boost("T_cell", c("CCR5", "CXCR4", "CCL5"), lambda = 4)

  marker_db <- do.call(rbind, lapply(names(markers), function(ct) {
    positives <- data.frame(
      cell_type = ct,
      gene = markers[[ct]],
      direction = "positive",
      weight = 1,
      stringsAsFactors = FALSE
    )
    negatives <- data.frame(
      cell_type = ct,
      gene = setdiff(unique(unlist(markers)), markers[[ct]]),
      direction = "negative",
      weight = 0.35,
      stringsAsFactors = FALSE
    )
    rbind(positives, negatives)
  }))

  label_pathways <- data.frame(
    cell_type = cell_types,
    pathway = names(pathway_sets),
    weight = 1,
    stringsAsFactors = FALSE
  )

  niche_db <- data.frame(
    cell_type = c("macrophage", "macrophage", "fibroblast", "fibroblast",
                  "epithelial", "endothelial", "T_cell", "T_cell"),
    neighbor_type = c("fibroblast", "epithelial", "macrophage", "epithelial",
                      "fibroblast", "epithelial", "macrophage", "endothelial"),
    weight = c(1.0, 0.7, 1.0, 0.8, 0.8, 0.7, 0.8, 0.5),
    stringsAsFactors = FALSE
  )

  lr_db <- data.frame(
    sender_type = c("macrophage", "epithelial", "fibroblast", "T_cell",
                    "fibroblast", "macrophage"),
    receiver_type = c("fibroblast", "endothelial", "macrophage", "macrophage",
                      "T_cell", "T_cell"),
    ligand = c("TGFB1", "VEGFA", "CSF1", "CCL5", "CXCL12", "CCL5"),
    receptor = c("TGFBR2", "KDR", "CSF1R", "CCR5", "CXCR4", "CCR5"),
    weight = c(1, 1, 0.8, 0.8, 0.7, 0.7),
    stringsAsFactors = FALSE
  )

  metadata <- data.frame(
    cell_id = cell_ids,
    true_label = labels,
    stringsAsFactors = FALSE
  )
  rownames(metadata) <- metadata$cell_id

  list(
    expr = expr,
    metadata = metadata,
    coords = coords,
    marker_db = marker_db,
    pathway_sets = pathway_sets,
    label_pathways = label_pathways,
    niche_db = niche_db,
    lr_db = lr_db
  )
}
