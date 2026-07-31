# NicheTypeR Design Notes

## Core biological claim

Cell type annotation in spatial transcriptomics should be treated as an
evidence-fusion problem rather than a single marker lookup.

Current evidence supports `NicheTypeR` as an annotation audit and calibration
framework, not as a state-of-the-art classifier. Claims should emphasize
interpretable evidence decomposition, confidence, margin, conflict reasons,
spatial null controls, and learned context calibration.

The current GSE202623 FOV-blocked benchmark shows that simple spatial smoothing
is assigned zero weight during tuning, and learned spatial compatibility is not
yet a robust macro-F1 improvement. This should be used to keep the manuscript
claim conservative.

The expanded 8-dataset blocked benchmark gives a more nuanced picture: learned
neighborhood passes null-control specificity in GSE202623_LESION and
SQUIDPY_SEQFISH, but most datasets either fail context specificity controls or
show generic smoothing/domain effects. This supports NicheTypeR as a validation
and audit framework rather than a universal classifier.

The first null-corrected context-specific score, implemented as
`score_context_specific_neighborhood()`, subtracts random-graph and
permuted-prior null scores from the observed learned-neighborhood score. In the
current benchmark, it is conservative and does not pass the strict guardrail on
any dataset. This is an important methodological finding: null correction needs
calibration before it can be claimed as a predictive improvement.

The package currently separates five evidence layers:

1. marker evidence
2. reference similarity
3. pathway support
4. spatial niche compatibility
5. ligand-receptor consistency

Each layer returns a cell-by-label score matrix. `infer_context_type()` aligns
the matrices, robustly standardizes each layer, applies user-controlled weights,
and returns fused probabilities plus conflict reasons.

## First intended user workflow

1. Start from a normalized expression matrix and spatial coordinates.
2. Provide a curated marker table and optional negative markers.
3. Provide pathway sets that support specific candidate labels.
4. Build a spatial graph from coordinates.
5. Score neighborhood compatibility from prior label probabilities.
6. Score local ligand-receptor consistency.
7. Fuse evidence into labels, confidence, margin, and conflict flags.

## Important distinction

Spatial context should not be described as proving that a marker is correct.
The stricter phrasing is:

> Spatial and functional context tests whether the cell identity suggested by
> marker evidence is biologically self-consistent.

That avoids circular reasoning while preserving the biological motivation.

## Near-term extensions

- Harden Seurat adapter: expression, metadata, reductions, and image coordinates.
- Harden SpatialExperiment adapter: `assay()`, `spatialCoords()`, `colData()`.
- Add cluster-level consensus calling.
- Add curated human and mouse marker resources.
- Add curated ligand-receptor presets from OmniPath/CellPhoneDB-style tables.
- Add benchmark scripts against SingleR, CellTypist, Azimuth, BANKSY, and
  scANVI/scArches.

## Contribution experiments

The package should be evaluated with three experiment families:

1. Accuracy benchmark against existing annotation tools on datasets with trusted
   labels.
2. Leave-one-evidence-out ablation to quantify how much spatial, pathway, and
   ligand-receptor evidence improve the final call.
3. Simple spatial smoothing, random graph, and permuted-prior controls to test
   whether context layers contain biological information beyond generic local
   autocorrelation.
4. Conflict case studies where marker-only annotation is plausible but spatial
   or functional evidence reveals doublets, contamination, or ambiguous states.

Reviewer-facing validation should prefer FOV/slide/replicate-blocked splits over
random cell splits. Random splits overstate spatial generalization because train
and test cells can share the same local tissue composition. Every spatial
context result should include a null graph or permuted learned-prior control.
