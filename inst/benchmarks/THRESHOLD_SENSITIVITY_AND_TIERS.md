# Threshold Sensitivity and Tiered Support

This analysis does not change the primary strict guardrail. It adds an
interpretive sensitivity analysis so that the benchmark is not reduced to
one pass/fail threshold. The prespecified strict dataset-level criterion
remains macro-F1 specific delta > 0.005 together with positive accuracy
delta and matched-null improvement.

## Dataset-Level Threshold Sensitivity

| macro-F1 delta threshold | learned-neighborhood configs | context-residual configs |
|---:|---:|---:|
| 0 | 24/68 | 7/68 |
| 0.001 | 16/68 | 3/68 |
| 0.0025 | 14/68 | 1/68 |
| 0.005 | 9/68 | 1/68 |
| 0.0075 | 7/68 | 0/68 |
| 0.01 | 3/68 | 0/68 |
| 0.02 | 1/68 | 0/68 |

Interpretation: the strict 0.005 cutoff gives 9/68 learned-neighborhood
configurations and 1/68 context-residual configurations. As an
exploratory directional readout, a zero cutoff gives 24/68 and 7/68,
respectively. This should be described as sensitivity, not as a new
success criterion.

## Dataset-Level Tiered Support

| evidence_layer | n_dataset_configs | strict_support | directional_support | no_directional_support |
| --- | --- | --- | --- | --- |
| learned_neighborhood | 68 | 9 | 15 | 44 |
| context_residual | 68 | 1 | 6 | 61 |

## Label-Task Threshold Sensitivity

Label tasks are dataset-label pairs. They are useful for review triage
and case-study selection, but they are not independent cohorts.

| label-task F1 delta threshold | learned-neighborhood tasks | context-residual tasks |
|---:|---:|---:|
| 0 | 425/1283 | 209/1283 |
| 0.001 | 359/1283 | 169/1283 |
| 0.0025 | 298/1283 | 122/1283 |
| 0.005 | 219/1283 | 69/1283 |
| 0.01 | 139/1283 | 29/1283 |
| 0.02 | 82/1283 | 12/1283 |
| 0.05 | 17/1283 | 3/1283 |

## Label-Task Tiered Support

| evidence_layer | n_label_tasks | n_eligible_label_tasks | strong_support_delta_gt_0_01 | suggestive_support_delta_0_to_0_01 | no_gain_or_harm | missing_matched_null_delta |
| --- | --- | --- | --- | --- | --- | --- |
| learned_neighborhood | 1283 | 1283 | 139 | 286 | 858 | 0 |
| context_residual | 1283 | 1283 | 29 | 180 | 1074 | 0 |

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
