# Threshold Sensitivity and Tiered Support

This analysis does not change the primary strict guardrail. It adds an
interpretive sensitivity analysis so that the benchmark is not reduced to
one pass/fail threshold. The prespecified strict dataset-level criterion
remains macro-F1 specific delta > 0.005 together with positive accuracy
delta and matched-null improvement.

## Dataset-Level Threshold Sensitivity

| macro-F1 delta threshold | learned-neighborhood configs | context-residual configs |
|---:|---:|---:|
| 0 | 17/48 | 5/48 |
| 0.001 | 11/48 | 2/48 |
| 0.0025 | 10/48 | 0/48 |
| 0.005 | 6/48 | 0/48 |
| 0.0075 | 5/48 | 0/48 |
| 0.01 | 1/48 | 0/48 |
| 0.02 | 0/48 | 0/48 |

Interpretation: the strict 0.005 cutoff gives 6/48 learned-neighborhood
configurations and 0/48 context-residual configurations. As an
exploratory directional readout, a zero cutoff gives 17/48 and 5/48,
respectively. This should be described as sensitivity, not as a new
success criterion.

## Dataset-Level Tiered Support

| evidence_layer | n_dataset_configs | strict_support | directional_support | no_directional_support |
| --- | --- | --- | --- | --- |
| learned_neighborhood | 48 | 6 | 11 | 31 |
| context_residual | 48 | 0 | 5 | 43 |

## Label-Task Threshold Sensitivity

Label tasks are dataset-label pairs. They are useful for review triage
and case-study selection, but they are not independent cohorts.

| label-task F1 delta threshold | learned-neighborhood tasks | context-residual tasks |
|---:|---:|---:|
| 0 | 310/941 | 167/941 |
| 0.001 | 251/941 | 138/941 |
| 0.0025 | 204/941 | 96/941 |
| 0.005 | 142/941 | 56/941 |
| 0.01 | 83/941 | 22/941 |
| 0.02 | 44/941 | 11/941 |
| 0.05 | 8/941 | 3/941 |

## Label-Task Tiered Support

| evidence_layer | n_label_tasks | n_eligible_label_tasks | strong_support_delta_gt_0_01 | suggestive_support_delta_0_to_0_01 | no_gain_or_harm | missing_matched_null_delta |
| --- | --- | --- | --- | --- | --- | --- |
| learned_neighborhood | 941 | 941 | 83 | 227 | 631 | 0 |
| context_residual | 941 | 941 | 22 | 145 | 774 | 0 |

## Manuscript Wording

Recommended main-text framing:

> The prespecified strict dataset-level guardrail identified a small set
> of strong learned-neighborhood gains. Threshold-sensitivity analyses
> showed additional directional support under exploratory cutoffs, and
> label-task analyses identified many candidate labels where context
> evidence was useful for triage. We therefore report strict guardrails
> as the primary generalization result and tiered support as a review-
> prioritization analysis.

Avoid presenting exploratory thresholds as if they replace the strict
guardrail. The clean hierarchy is: strict dataset-level result for
generalization; threshold sensitivity for robustness; label-task tiers
for practical review triage.
