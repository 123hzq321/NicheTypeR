# Manuscript Positioning After Internal Review

## Recommended Claim

Use:

> NicheTypeR is an interpretable context-aware annotation audit framework for
> spatial transcriptomics. It decomposes candidate cell identity into marker,
> pathway/state, ligand-receptor, and spatial-neighborhood evidence, then reports
> confidence, margin, and evidence conflicts.

Do not use yet:

> NicheTypeR is a state-of-the-art spatial cell type annotation method.

The FOV-blocked validation does not support that stronger claim.

## Current Evidence Level

Current evidence supports a preprint and a Bioinformatics-style application note
after additional polish. It does not yet support Genome Biology, Nature
Communications, or Nature Methods claims.

The learned-neighborhood layer is biologically plausible and improves random
cell-split evaluation, but under stricter FOV-blocked validation it does not
produce a robust macro-F1 gain. A simple spatial smoothing baseline is assigned
zero weight in the current FOV-blocked benchmark, and random-graph controls are
close to the learned-neighborhood result.

The new multi-dataset blocked benchmark is more encouraging but still
conservative: learned neighborhood passes a null-control guardrail in
GSE202623_LESION, SQUIDPY_SEQFISH, and the GEO-direct
GEO_GSE327581_COSMX_AD_BRAIN dataset, while most other datasets fail
specificity controls or are better explained by simple spatial/domain smoothing.
The GEO-direct GSE240015 thymus Visium domain benchmark is a useful control:
it passes the smoothing guardrail but not the learned-neighborhood guardrail.

Direct GEO expansion added GSE240015, GSE284005, GSE333737, and GSE327581 as
benchmark-ready spatial datasets. GSE284005 and GSE333737 fail the current
context specificity guardrail, GSE327581 passes the learned-neighborhood
guardrail, and GSE240015 passes only the smoothing guardrail. This is stronger
than a single-dataset prototype, but still supports a conservative Application
Note framing rather than an Original Paper claim.

An initial null-corrected context-specific neighborhood score has now been
implemented. It subtracts random-graph and permuted-prior null scores from the
observed learned-neighborhood score. In current results, this residual is useful
as a stricter audit statistic but does not yet provide stable predictive gains.
That means the Original Paper route requires further method development, not
just more datasets.

## Strongest Contribution

The strongest contribution is not raw accuracy. It is:

- explicit multi-evidence decomposition
- negative marker penalties
- confidence and margin
- conflict reasons
- learned or hand-written context priors
- paired model comparison
- FOV/slide-blocked evaluation
- spatial null controls

This makes the tool useful for auditing annotations, prioritizing ambiguous
cells, and diagnosing when marker-only labels disagree with tissue context.

## Required Before Submission

Minimum package and paper requirements:

1. R-native reproduction of the Python mirror benchmark.
2. FOV-blocked or slide-blocked validation as the primary result.
3. Random cell split moved to supplementary or diagnostic status.
4. Spatial null controls: random graph and permuted learned prior.
5. Paired statistics: McNemar/exact binomial and bootstrap confidence intervals.
6. At least one external baseline beyond marker-only. A simple spatial-smoothing
   baseline is now included; SingleR, CellTypist, or Azimuth-style mapping is
   still needed before stronger claims.
7. Multi-dataset benchmark table with specificity guardrails. This is now
   implemented for 12 datasets, but the claim should remain cautious because
   the learned context signal is not universal.

## Best Short-Term Target

Bioinformatics Application Note or preprint.

Position the package as:

> A lightweight R framework for interpretable annotation auditing and context
> calibration in spatial transcriptomics.

Avoid claiming:

- universal accuracy improvement
- superior annotation performance over atlas methods
- first use of spatial context for cell type inference

## Bioinformatics Submission Attempt

A submission workspace has now been created in
`outputs/bioinformatics_submission`. It contains an Application Note draft,
supplementary methods, a cover letter, a reviewer risk register, a checklist,
target notes, and a regenerated Figure 1 based on the 12-dataset blocked
benchmark.

The draft intentionally centers auditability, blocked validation, conflict
reporting, and null controls. It does not claim universal accuracy improvement.

## Six-Month Route To A Stronger Methods Paper

To move beyond an application note:

- improve the null-corrected context-specific model so that it is calibrated and
  predictive, not only conservative
- evaluate at least 5-8 spatial datasets across MERFISH/Xenium/CosMx/Visium-like
  technologies
- use leave-slide, leave-donor, or leave-study validation
- add proper baselines: SingleR, CellTypist, Azimuth/scANVI where possible,
  BANKSY/STELLAR or stronger spatial smoothing baselines
- separate identity evidence from state evidence
- add open-set/unknown/doublet/conflict detection evaluation
- demonstrate a biological case where conflict reporting changes interpretation
  beyond marker-only annotation
