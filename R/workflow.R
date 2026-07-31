#' Run the core context-aware annotation workflow
#'
#' This convenience wrapper computes marker, optional reference, optional
#' pathway, optional neighborhood, and optional ligand-receptor evidence before
#' calling `infer_context_type()`.
#'
#' @param expr Gene-by-cell expression matrix.
#' @param coords Coordinate data frame.
#' @param marker_db Marker table used by `score_markers`.
#' @param metadata Optional cell metadata.
#' @param reference_profiles Optional gene-by-label reference profile matrix.
#' @param pathway_sets Optional named list of pathway or metabolic gene sets.
#' @param label_pathways Optional table mapping labels to pathways.
#' @param niche_db Optional spatial niche prior table.
#' @param lr_db Optional ligand-receptor prior table.
#' @param k Number of spatial nearest neighbors.
#' @param radius Optional spatial graph radius.
#' @param graph_group_col Optional coordinate column used to build independent
#'   spatial graphs within each sample, section, replicate, or field of view.
#' @param weights Optional evidence weights.
#' @param temperature Softmax temperature for fusion and context scoring.
#' @param min_margin Minimum top-vs-second probability margin.
#' @param component_min_margin Minimum evidence-layer margin required before an
#'   evidence layer can be counted as conflicting with the final call.
#' @return A list containing aligned input, graph edges, evidence score matrices,
#'   and the fused annotation result.
#' @export
run_nichetype_workflow <- function(expr,
                                   coords,
                                   marker_db,
                                   metadata = NULL,
                                   reference_profiles = NULL,
                                   pathway_sets = NULL,
                                   label_pathways = NULL,
                                   niche_db = NULL,
                                   lr_db = NULL,
                                   k = 8,
                                   radius = NULL,
                                   graph_group_col = NULL,
                                   weights = NULL,
                                   temperature = 1,
                                   min_margin = 0.08,
                                   component_min_margin = 0.05) {
  input <- prepare_nichetype_input(expr, coords, metadata)
  edges <- build_niche_graph(
    input$coords,
    k = k,
    radius = radius,
    group_col = graph_group_col
  )

  evidence <- list()
  marker_result <- score_markers(input$expr, marker_db)
  evidence$marker <- marker_result$scores

  if (!is.null(reference_profiles)) {
    evidence$reference <- score_reference_similarity(input$expr, reference_profiles)
  }

  if (!is.null(pathway_sets) && !is.null(label_pathways)) {
    pathway_result <- score_pathway_context(input$expr, pathway_sets, label_pathways)
    evidence$pathway <- pathway_result$scores
  } else {
    pathway_result <- NULL
  }

  prior_scores <- .initial_context_prior(evidence)

  if (!is.null(niche_db)) {
    evidence$neighborhood <- score_neighborhood(
      edges = edges,
      prior_scores = prior_scores,
      niche_db = niche_db,
      temperature = temperature
    )
  }

  if (!is.null(lr_db)) {
    evidence$ligand_receptor <- score_lr_context(
      expr = input$expr,
      edges = edges,
      prior_scores = prior_scores,
      lr_db = lr_db,
      temperature = temperature
    )
  }

  fit <- infer_context_type(
    scores = evidence,
    weights = weights,
    temperature = temperature,
    min_margin = min_margin,
    component_min_margin = component_min_margin
  )

  list(
    input = input,
    edges = edges,
    evidence = evidence,
    fit = fit,
    marker = marker_result,
    pathway = pathway_result
  )
}

.initial_context_prior <- function(evidence) {
  initial_names <- intersect(names(evidence), c("marker", "reference", "pathway"))
  if (length(initial_names) == 0) {
    stop("At least marker, reference, or pathway evidence is required.", call. = FALSE)
  }
  aligned <- .align_score_list(evidence[initial_names])
  standardized <- lapply(aligned, .standardize_score)
  prior <- standardized[[1]]
  if (length(standardized) > 1) {
    for (i in 2:length(standardized)) {
      prior <- prior + standardized[[i]]
    }
    prior <- prior / length(standardized)
  }
  prior
}
