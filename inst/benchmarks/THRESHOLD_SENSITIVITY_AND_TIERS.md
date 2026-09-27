# Threshold Sensitivity and Tiered Support

This analysis does not change the primary strict guardrail. It adds an
interpretive sensitivity analysis so that the benchmark is not reduced to
one pass/fail threshold. The prespecified strict dataset-level criterion
remains macro-F1 specific delta > 0.005 together with positive accuracy
delta and matched-null improvement.

## Dataset-Level Threshold Sensitivity

| macro-F1 delta threshold | learned-neighborhood configs | context-residual configs |
|---:|---:|---:|
| 0 | 8/19 | 1/19 |
| 0.001 | 5/19 | 1/19 |
| 0.0025 | 5/19 | 0/19 |
| 0.005 | 4/19 | 0/19 |
| 0.0075 | 4/19 | 0/19 |
| 0.01 | 0/19 | 0/19 |
| 0.02 | 0/19 | 0/19 |

Interpretation: the strict 0.005 cutoff gives 5/34 learned-neighborhood
configurations and 0/34 context-residual configurations. As an
exploratory directional readout, a zero cutoff gives 14/34 and 2/34,
respectively. This should be described as sensitivity, not as a new
success criterion.

## Dataset-Level Tiered Support

| evidence_layer | n_dataset_configs | strict_support | directional_support | no_directional_support |
| --- | --- | --- | --- | --- |
| learned_neighborhood | 19 | 4 | 4 | 11 |
| context_residual | 19 | 0 | 1 | 18 |

## Label-Task Threshold Sensitivity

Label tasks are dataset-label pairs. They are useful for review triage
and case-study selection, but they are not independent cohorts.

| label-task F1 delta threshold | learned-neighborhood tasks | context-residual tasks |
|---:|---:|---:|
| 0 | 156/408 | 92/408 |
| 0.001 | 133/408 | 78/408 |
| 0.0025 | 118/408 | 56/408 |
| 0.005 | 89/408 | 36/408 |
| 0.01 | 57/408 | 15/408 |
| 0.02 | 34/408 | 8/408 |
| 0.05 | 7/408 | 3/408 |

## Label-Task Tiered Support

| evidence_layer | n_label_tasks | n_eligible_label_tasks | strong_support_delta_gt_0_01 | suggestive_support_delta_0_to_0_01 | no_gain_or_harm | missing_matched_null_delta |
| --- | --- | --- | --- | --- | --- | --- |
| learned_neighborhood | 408 | 407 | 57 | 99 | 251 | 1 |
| context_residual | 408 | 407 | 15 | 77 | 315 | 1 |

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
