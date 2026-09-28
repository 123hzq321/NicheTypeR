#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(Seurat)
})

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
if (!length(script_file)) {
  stop("Unable to determine script path from commandArgs().")
}
ROOT <- normalizePath(dirname(script_file[1]), winslash = "/", mustWork = TRUE)
SEED <- 20260725

CALLS_IN <- file.path(ROOT, "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv")
CALLS_OUT <- file.path(ROOT, "SEURAT_LABEL_TRANSFER_BASELINE_calls.csv")
SUMMARY_OUT <- file.path(ROOT, "SEURAT_LABEL_TRANSFER_BASELINE_summary.csv")
PAIRWISE_OUT <- file.path(ROOT, "SEURAT_LABEL_TRANSFER_BASELINE_pairwise.csv")
STATUS_OUT <- file.path(ROOT, "SEURAT_LABEL_TRANSFER_BASELINE_status.csv")
REPORT_OUT <- file.path(ROOT, "SEURAT_LABEL_TRANSFER_BASELINE.md")

message_ts <- function(...) {
  cat(format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "-", ..., "\n")
  flush.console()
}

as_int_env <- function(name, default = NA_integer_) {
  value <- Sys.getenv(name, unset = "")
  if (!nzchar(value)) {
    return(default)
  }
  parsed <- suppressWarnings(as.integer(value))
  if (is.na(parsed)) {
    default
  } else {
    parsed
  }
}

split_env <- function(name) {
  value <- Sys.getenv(name, unset = "")
  if (!nzchar(value)) {
    return(character())
  }
  trimws(strsplit(value, ",", fixed = TRUE)[[1]])
}

build_configs <- function(root = ROOT) {
  configs <- data.frame(
    dataset_id = "GSE202623_LESION",
    expression_path = file.path(root, "GSE202623", "GSE202623_lesion_preview_expression.tsv.gz"),
    metadata_path = file.path(root, "GSE202623", "GSE202623_lesion_preview_metadata.tsv"),
    cell_id_col = "cellID",
    label_col = "cell.type_manual",
    modality = "MERFISH_RNA_single_cell",
    include = TRUE,
    stringsAsFactors = FALSE
  )

  registry_path <- file.path(root, "DATASET_REGISTRY.csv")
  if (file.exists(registry_path)) {
    registry <- read.csv(registry_path, stringsAsFactors = FALSE, check.names = FALSE)
    registry_configs <- data.frame(
      dataset_id = registry$dataset_id,
      expression_path = file.path(root, registry$dataset_id, paste0(registry$dataset_id, "_preview_expression.tsv.gz")),
      metadata_path = file.path(root, registry$dataset_id, paste0(registry$dataset_id, "_preview_metadata.tsv")),
      cell_id_col = "cell_id",
      label_col = registry$label_col,
      modality = registry$modality,
      include = grepl("RNA|transcriptomics", registry$modality, ignore.case = TRUE) &
        !grepl("proteomics|protein|MIBI|IMC", registry$modality, ignore.case = TRUE),
      stringsAsFactors = FALSE
    )
    configs <- rbind(configs, registry_configs)
  }

  geo_registry_path <- file.path(root, "GEO_DIRECT_DATASETS.csv")
  if (file.exists(geo_registry_path)) {
    geo_registry <- read.csv(geo_registry_path, stringsAsFactors = FALSE, check.names = FALSE)
    geo_registry <- geo_registry[geo_registry$status == "benchmark_ready" & nzchar(geo_registry$dataset_id), , drop = FALSE]
    geo_configs <- data.frame(
      dataset_id = geo_registry$dataset_id,
      expression_path = file.path(root, geo_registry$dataset_id, paste0(geo_registry$dataset_id, "_preview_expression.tsv.gz")),
      metadata_path = file.path(root, geo_registry$dataset_id, paste0(geo_registry$dataset_id, "_preview_metadata.tsv")),
      cell_id_col = "cell_id",
      label_col = "label",
      modality = "GEO_direct_spatial_transcriptomics",
      include = TRUE,
      stringsAsFactors = FALSE
    )
    configs <- rbind(configs, geo_configs)
  }

  configs <- configs[!duplicated(configs$dataset_id), , drop = FALSE]
  requested <- split_env("NICHE_SEURAT_DATASETS")
  if (length(requested)) {
    configs <- configs[configs$dataset_id %in% requested, , drop = FALSE]
  }
  max_datasets <- as_int_env("NICHE_SEURAT_MAX_DATASETS")
  if (!is.na(max_datasets) && nrow(configs) > max_datasets) {
    configs <- configs[seq_len(max_datasets), , drop = FALSE]
  }
  configs
}

read_expression <- function(path) {
  expr <- read.delim(path, row.names = 1, check.names = FALSE)
  expr <- as.matrix(expr)
  storage.mode(expr) <- "double"
  rownames(expr) <- make.unique(as.character(rownames(expr)))
  colnames(expr) <- as.character(colnames(expr))
  expr[!is.finite(expr)] <- 0
  expr
}

read_metadata <- function(config, cells) {
  meta <- read.delim(config$metadata_path, stringsAsFactors = FALSE, check.names = FALSE)
  required <- c(config$cell_id_col, config$label_col)
  missing <- setdiff(required, colnames(meta))
  if (length(missing)) {
    stop("missing metadata columns: ", paste(missing, collapse = ", "))
  }
  meta$cell_id <- as.character(meta[[config$cell_id_col]])
  meta$label <- as.character(meta[[config$label_col]])
  meta <- meta[!is.na(meta$cell_id) & nzchar(meta$cell_id) & !is.na(meta$label) & nzchar(meta$label), , drop = FALSE]
  meta <- meta[!duplicated(meta$cell_id), , drop = FALSE]
  common <- intersect(cells, meta$cell_id)
  meta <- meta[match(common, meta$cell_id), , drop = FALSE]
  meta
}

prepare_seurat <- function(counts, labels = NULL, nfeatures = 1500, npcs = 20) {
  object <- CreateSeuratObject(counts = counts, assay = "RNA", min.cells = 0, min.features = 0)
  if (!is.null(labels)) {
    object$reference_label <- factor(labels)
  }
  object <- NormalizeData(object, verbose = FALSE)
  object <- FindVariableFeatures(
    object,
    selection.method = "vst",
    nfeatures = min(nfeatures, nrow(object)),
    verbose = FALSE
  )
  features <- VariableFeatures(object)
  if (length(features) < 2) {
    stop("too few variable features for PCA")
  }
  object <- ScaleData(object, features = features, verbose = FALSE)
  max_pcs <- min(npcs, length(features) - 1L, ncol(object) - 1L)
  if (max_pcs < 2L) {
    stop("too few cells or features for PCA")
  }
  object <- RunPCA(object, features = features, npcs = max_pcs, verbose = FALSE)
  object
}

run_transfer <- function(expr, labels, test_cells, nfeatures = 1500, npcs = 20) {
  train_cells <- setdiff(colnames(expr), test_cells)
  train_labels <- labels[train_cells]
  keep_train <- !is.na(train_labels) & nzchar(train_labels)
  train_cells <- train_cells[keep_train]
  train_labels <- train_labels[train_cells]

  if (length(train_cells) < 20L || length(test_cells) < 5L) {
    stop("too few train or test cells")
  }
  if (length(unique(train_labels)) < 2L) {
    stop("too few training labels")
  }

  ref <- prepare_seurat(expr[, train_cells, drop = FALSE], labels = train_labels, nfeatures = nfeatures, npcs = npcs)
  query <- CreateSeuratObject(counts = expr[, test_cells, drop = FALSE], assay = "RNA", min.cells = 0, min.features = 0)
  query <- NormalizeData(query, verbose = FALSE)

  dims <- seq_len(ncol(Embeddings(ref, "pca")))
  anchors <- FindTransferAnchors(
    reference = ref,
    query = query,
    dims = dims,
    reference.reduction = "pca",
    verbose = FALSE
  )

  last_error <- NULL
  for (k_weight in c(50L, 25L, 10L, 5L, 1L)) {
    prediction <- tryCatch(
      TransferData(
        anchorset = anchors,
        refdata = ref$reference_label,
        dims = dims,
        k.weight = min(k_weight, length(train_cells)),
        verbose = FALSE
      ),
      error = function(e) {
        last_error <<- e
        NULL
      }
    )
    if (!is.null(prediction)) {
      prediction$k_weight <- k_weight
      prediction$n_anchors <- nrow(anchors@anchors)
      return(prediction)
    }
  }
  stop(conditionMessage(last_error))
}

prediction_calls <- function(prediction, truth, dataset_id, fold, elapsed_sec) {
  score_cols <- setdiff(grep("^prediction.score\\.", colnames(prediction), value = TRUE), "prediction.score.max")
  score_matrix <- as.matrix(prediction[, score_cols, drop = FALSE])
  if ("prediction.score.max" %in% colnames(prediction)) {
    confidence <- as.numeric(prediction$prediction.score.max)
  } else if (ncol(score_matrix) == 0L) {
    confidence <- rep(NA_real_, nrow(prediction))
  } else if (ncol(score_matrix) == 1L) {
    confidence <- as.numeric(score_matrix[, 1L])
  } else {
    confidence <- as.numeric(apply(score_matrix, 1L, max, na.rm = TRUE))
  }
  if (ncol(score_matrix) == 0L) {
    margin <- rep(NA_real_, nrow(prediction))
  } else if (ncol(score_matrix) == 1L) {
    margin <- confidence
  } else {
    sorted_scores <- t(apply(score_matrix, 1L, sort, decreasing = TRUE))
    margin <- as.numeric(sorted_scores[, 1L] - sorted_scores[, 2L])
  }

  cell_id <- rownames(prediction)
  label <- as.character(prediction$predicted.id)
  label[is.na(label) | !nzchar(label)] <- "unknown"
  out <- data.frame(
    cell_id = cell_id,
    label = label,
    confidence = confidence,
    margin = margin,
    conflict_reason = ifelse(is.na(margin) | margin < 0.08, "low_margin", "consistent"),
    truth = as.character(truth[cell_id]),
    correct = label == as.character(truth[cell_id]),
    dataset_id = dataset_id,
    fold = fold,
    model = "seurat_label_transfer",
    k_weight = unique(prediction$k_weight)[1],
    n_anchors = unique(prediction$n_anchors)[1],
    elapsed_sec = elapsed_sec,
    stringsAsFactors = FALSE
  )
  out
}

macro_f1 <- function(pred, truth) {
  labels <- sort(unique(c(pred, truth)))
  f1 <- vapply(labels, function(label) {
    tp <- sum(pred == label & truth == label)
    fp <- sum(pred == label & truth != label)
    fn <- sum(pred != label & truth == label)
    precision <- if ((tp + fp) > 0) tp / (tp + fp) else NA_real_
    recall <- if ((tp + fn) > 0) tp / (tp + fn) else NA_real_
    if (is.na(precision) || is.na(recall) || (precision + recall) == 0) {
      NA_real_
    } else {
      2 * precision * recall / (precision + recall)
    }
  }, numeric(1))
  mean(f1, na.rm = TRUE)
}

summarize_calls <- function(calls) {
  pieces <- split(calls, calls$dataset_id)
  do.call(rbind, lapply(pieces, function(df) {
    pred <- as.character(df$label)
    truth <- as.character(df$truth)
    data.frame(
      dataset_id = unique(df$dataset_id),
      model = "seurat_label_transfer",
      n = nrow(df),
      accuracy = mean(pred == truth),
      macro_f1 = macro_f1(pred, truth),
      mean_confidence = mean(df$confidence, na.rm = TRUE),
      mean_margin = mean(df$margin, na.rm = TRUE),
      conflict_rate = mean(df$conflict_reason != "consistent", na.rm = TRUE),
      mean_elapsed_sec_per_fold = mean(tapply(df$elapsed_sec, df$fold, unique)),
      stringsAsFactors = FALSE
    )
  }))
}

pairwise_vs_marker <- function(seurat_calls, marker_calls) {
  marker_calls <- marker_calls[marker_calls$model == "marker_only", , drop = FALSE]
  pairs <- merge(
    marker_calls[, c("dataset_id", "fold", "cell_id", "label", "truth", "correct")],
    seurat_calls[, c("dataset_id", "fold", "cell_id", "label", "truth", "correct")],
    by = c("dataset_id", "fold", "cell_id"),
    suffixes = c("_marker", "_seurat")
  )
  pieces <- split(pairs, pairs$dataset_id)
  do.call(rbind, lapply(pieces, function(df) {
    marker_correct <- as.logical(df$correct_marker)
    seurat_correct <- as.logical(df$correct_seurat)
    data.frame(
      dataset_id = unique(df$dataset_id),
      comparator_model = "seurat_label_transfer",
      n = nrow(df),
      marker_accuracy = mean(marker_correct),
      comparator_accuracy = mean(seurat_correct),
      accuracy_diff = mean(seurat_correct) - mean(marker_correct),
      marker_wrong_comparator_right = sum(!marker_correct & seurat_correct),
      marker_right_comparator_wrong = sum(marker_correct & !seurat_correct),
      both_correct = sum(marker_correct & seurat_correct),
      both_wrong = sum(!marker_correct & !seurat_correct),
      stringsAsFactors = FALSE
    )
  }))
}

write_report <- function(summary, pairwise, status) {
  lines <- c(
    "# Seurat Label Transfer External Baseline",
    "",
    "This report adds a true external-method comparator to the NicheTypeR benchmark.",
    "Seurat label transfer is run on the same preview expression matrices and on",
    "the same held-out spatial blocks used by `MULTIDATASET_BLOCKED_BENCHMARK_calls.csv`.",
    "Training cells come only from training spatial blocks; held-out FOV/slide blocks",
    "are never used for reference labels.",
    "",
    "This is not a claim that NicheTypeR reimplements Seurat. The output table is",
    "stored in the same `cell_id`, `label`, `confidence` schema accepted by",
    "`score_external_labels()`, so Seurat calls can be audited as external reference",
    "evidence by NicheTypeR.",
    "",
    "Protein-only stress-test datasets are skipped for this RNA label-transfer",
    "baseline.",
    "",
    "## Summary",
    "",
    "| dataset | n | accuracy | macro-F1 | mean confidence | conflict rate | sec/fold |",
    "|---|---:|---:|---:|---:|---:|---:|"
  )
  if (nrow(summary)) {
    for (i in seq_len(nrow(summary))) {
      row <- summary[i, ]
      lines <- c(lines, sprintf(
        "| %s | %d | %.4f | %.4f | %.4f | %.4f | %.1f |",
        row$dataset_id, row$n, row$accuracy, row$macro_f1,
        row$mean_confidence, row$conflict_rate, row$mean_elapsed_sec_per_fold
      ))
    }
  }

  lines <- c(lines, "", "## Paired Comparison vs Marker-Only", "",
             "| dataset | accuracy diff | marker wrong, Seurat right | marker right, Seurat wrong |",
             "|---|---:|---:|---:|")
  if (nrow(pairwise)) {
    for (i in seq_len(nrow(pairwise))) {
      row <- pairwise[i, ]
      lines <- c(lines, sprintf(
        "| %s | %+.4f | %d | %d |",
        row$dataset_id, row$accuracy_diff,
        row$marker_wrong_comparator_right,
        row$marker_right_comparator_wrong
      ))
    }
  }

  if (nrow(status)) {
    lines <- c(lines, "", "## Status", "",
               "| dataset | fold | status | reason |",
               "|---|---:|---|---|")
    for (i in seq_len(nrow(status))) {
      row <- status[i, ]
      lines <- c(lines, sprintf("| %s | %s | %s | %s |",
                                row$dataset_id, row$fold, row$status, row$reason))
    }
  }

  lines <- c(lines, "", "## Files", "",
             "- `SEURAT_LABEL_TRANSFER_BASELINE_calls.csv`",
             "- `SEURAT_LABEL_TRANSFER_BASELINE_summary.csv`",
             "- `SEURAT_LABEL_TRANSFER_BASELINE_pairwise.csv`",
             "- `SEURAT_LABEL_TRANSFER_BASELINE_status.csv`")
  writeLines(lines, REPORT_OUT, useBytes = TRUE)
}

main <- function() {
  set.seed(SEED)
  if (!file.exists(CALLS_IN)) {
    stop("Missing benchmark calls table: ", CALLS_IN)
  }

  all_calls <- read.csv(CALLS_IN, stringsAsFactors = FALSE, check.names = FALSE)
  configs <- build_configs()
  max_folds <- as_int_env("NICHE_SEURAT_MAX_FOLDS")
  nfeatures <- as_int_env("NICHE_SEURAT_NFEATURES", default = 1500L)
  npcs <- as_int_env("NICHE_SEURAT_NPCS", default = 20L)

  call_rows <- list()
  status_rows <- list()

  for (row_idx in seq_len(nrow(configs))) {
    config <- configs[row_idx, , drop = FALSE]
    dataset_id <- config$dataset_id
    if (!isTRUE(config$include)) {
      message_ts(dataset_id, "skipped: non-RNA modality")
      status_rows[[length(status_rows) + 1L]] <- data.frame(
        dataset_id = dataset_id,
        fold = NA_integer_,
        status = "skipped",
        reason = "non-RNA modality",
        stringsAsFactors = FALSE
      )
      next
    }
    if (!file.exists(config$expression_path) || !file.exists(config$metadata_path)) {
      message_ts(dataset_id, "skipped: missing preview files")
      status_rows[[length(status_rows) + 1L]] <- data.frame(
        dataset_id = dataset_id,
        fold = NA_integer_,
        status = "skipped",
        reason = "missing preview files",
        stringsAsFactors = FALSE
      )
      next
    }

    message_ts(dataset_id, "reading preview data")
    dataset_result <- tryCatch({
      expr <- read_expression(config$expression_path)
      meta <- read_metadata(config, colnames(expr))
      labels <- setNames(meta$label, meta$cell_id)
      expr <- expr[, meta$cell_id, drop = FALSE]

      fold_calls <- all_calls[all_calls$dataset_id == dataset_id & all_calls$model == "marker_only", , drop = FALSE]
      folds <- sort(unique(fold_calls$fold))
      if (!is.na(max_folds)) {
        folds <- head(folds, max_folds)
      }
      if (!length(folds)) {
        stop("no benchmark folds found")
      }

      for (fold in folds) {
        test_cells <- unique(fold_calls$cell_id[fold_calls$fold == fold])
        test_cells <- intersect(test_cells, colnames(expr))
        if (length(test_cells) < 5L) {
          status_rows[[length(status_rows) + 1L]] <- data.frame(
            dataset_id = dataset_id,
            fold = fold,
            status = "skipped",
            reason = "too few test cells",
            stringsAsFactors = FALSE
          )
          next
        }

        message_ts(dataset_id, "fold", fold, "train", ncol(expr) - length(test_cells), "test", length(test_cells))
        fold_result <- tryCatch({
          started <- proc.time()[["elapsed"]]
          prediction <- run_transfer(expr, labels, test_cells, nfeatures = nfeatures, npcs = npcs)
          elapsed <- proc.time()[["elapsed"]] - started
          list(ok = TRUE, prediction = prediction, elapsed = elapsed)
        }, error = function(e) {
          list(ok = FALSE, error = e)
        })

        if (!isTRUE(fold_result$ok)) {
          status_rows[[length(status_rows) + 1L]] <- data.frame(
            dataset_id = dataset_id,
            fold = fold,
            status = "failed",
            reason = conditionMessage(fold_result$error),
            stringsAsFactors = FALSE
          )
          message_ts(dataset_id, "fold", fold, "failed:", conditionMessage(fold_result$error))
          next
        }

        fold_out <- prediction_calls(fold_result$prediction, labels, dataset_id, fold, fold_result$elapsed)
        call_rows[[length(call_rows) + 1L]] <- fold_out
        status_rows[[length(status_rows) + 1L]] <- data.frame(
          dataset_id = dataset_id,
          fold = fold,
          status = "completed",
          reason = sprintf("n=%d; elapsed=%.1f sec", nrow(fold_out), fold_result$elapsed),
          stringsAsFactors = FALSE
        )
      }
      TRUE
    }, error = function(e) {
      status_rows[[length(status_rows) + 1L]] <<- data.frame(
        dataset_id = dataset_id,
        fold = NA_integer_,
        status = "failed",
        reason = conditionMessage(e),
        stringsAsFactors = FALSE
      )
      message_ts(dataset_id, "failed:", conditionMessage(e))
      FALSE
    })

    invisible(dataset_result)
    gc(verbose = FALSE)
  }

  status <- if (length(status_rows)) do.call(rbind, status_rows) else data.frame()
  write.csv(status, STATUS_OUT, row.names = FALSE)

  if (!length(call_rows)) {
    stop("No Seurat label-transfer calls were produced; see ", STATUS_OUT)
  }

  seurat_calls <- do.call(rbind, call_rows)
  summary <- summarize_calls(seurat_calls)
  pairwise <- pairwise_vs_marker(seurat_calls, all_calls)

  write.csv(seurat_calls, CALLS_OUT, row.names = FALSE)
  write.csv(summary, SUMMARY_OUT, row.names = FALSE)
  write.csv(pairwise, PAIRWISE_OUT, row.names = FALSE)
  write_report(summary, pairwise, status)

  message_ts("wrote", CALLS_OUT)
  message_ts("wrote", SUMMARY_OUT)
  print(summary)
}

main()
