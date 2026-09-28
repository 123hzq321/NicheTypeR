from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent


def main() -> None:
    validation_sources = pd.read_csv(ROOT / "SOURCE_INDEPENDENCE_REGISTRY.csv")
    validation_report = json.loads(
        (ROOT / "SOURCE_INDEPENDENCE_REPORT.json").read_text(encoding="utf-8")
    )
    calibration_registry = pd.read_csv(ROOT / "SODB_CALIBRATION_DATASETS.csv")
    calibration_report = json.loads(
        (ROOT / "SODB_CALIBRATION_LEAN_BENCHMARK_report.json").read_text(
            encoding="utf-8"
        )
    )
    main_guardrail = pd.concat(
        [
            pd.read_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv"),
            pd.read_csv(ROOT / "EXPANDED_SCALE_LEAN_BENCHMARK_guardrail.csv"),
        ],
        ignore_index=True,
    )
    calibration_guardrail = pd.read_csv(
        ROOT / "SODB_CALIBRATION_LEAN_BENCHMARK_guardrail.csv"
    )

    validation = validation_sources[
        [
            "source_dataset_id",
            "publication_family",
            "n_configurations",
            "source_deduplicated_units",
        ]
    ].copy()
    validation["panel"] = "label_bearing_validation"
    validation["claim_role"] = "eligible for task-appropriate validation with label-evidence caveats"
    validation["semantic_truth_status"] = "mixed: author, reference-mapped, domain or external annotations"

    calibration = calibration_registry[
        ["source_dataset_id", "expanded_cells"]
    ].copy()
    calibration["publication_family"] = "publication-level deduplication not asserted"
    calibration["n_configurations"] = 1
    calibration = calibration.rename(
        columns={"expanded_cells": "source_deduplicated_units"}
    )
    calibration["panel"] = "cluster_only_calibration"
    calibration["claim_role"] = "operational and matched-null calibration only"
    calibration["semantic_truth_status"] = "SODB standardized Leiden cluster; not semantic truth"

    overlap = set(validation["source_dataset_id"]) & set(calibration["source_dataset_id"])
    if overlap:
        raise ValueError(f"Validation/calibration source overlap: {sorted(overlap)}")
    portfolio = pd.concat([validation, calibration], ignore_index=True)
    if portfolio["source_dataset_id"].nunique() != 100:
        raise ValueError(
            f"Expected exactly 100 source IDs, found {portfolio['source_dataset_id'].nunique()}"
        )
    portfolio.to_csv(ROOT / "HUNDRED_SOURCE_PORTFOLIO.csv", index=False)

    summary = {
        "processed_public_source_ids": int(portfolio["source_dataset_id"].nunique()),
        "label_bearing_validation_source_ids": int(len(validation)),
        "cluster_only_calibration_source_ids": int(len(calibration)),
        "label_bearing_benchmark_configurations": int(
            validation_report["benchmark_configurations"]
        ),
        "cluster_only_calibration_configurations": int(len(calibration_registry)),
        "total_processed_configurations": int(
            validation_report["benchmark_configurations"] + len(calibration_registry)
        ),
        "validation_configuration_level_units": int(
            validation_report["configuration_level_units"]
        ),
        "validation_source_deduplicated_units": int(
            validation_report["source_deduplicated_units"]
        ),
        "calibration_units": int(calibration_registry["expanded_cells"].sum()),
        "total_configuration_level_units": int(
            validation_report["configuration_level_units"]
            + calibration_registry["expanded_cells"].sum()
        ),
        "main_learned_strict_passes": int(
            main_guardrail["learned_passes_guardrail"].astype(bool).sum()
        ),
        "main_context_specific_strict_passes": int(
            main_guardrail["context_specific_passes_guardrail"].astype(bool).sum()
        ),
        "calibration_learned_strict_passes": int(
            calibration_guardrail["learned_passes_guardrail"].astype(bool).sum()
        ),
        "calibration_context_specific_strict_passes": int(
            calibration_guardrail["context_specific_passes_guardrail"].astype(bool).sum()
        ),
        "known_validation_publication_families": int(
            validation_report["known_publication_families"]
        ),
        "calibration_publication_family_deduplication_complete": False,
    }
    (ROOT / "HUNDRED_SOURCE_PORTFOLIO.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    lines = [
        "# NicheTypeR 100-source portfolio",
        "",
        f"- Processed public source IDs: **{summary['processed_public_source_ids']}**",
        f"- Label-bearing validation sources: **{summary['label_bearing_validation_source_ids']}** across **{summary['label_bearing_benchmark_configurations']}** configurations",
        f"- Cluster-only calibration sources: **{summary['cluster_only_calibration_source_ids']}** across **{summary['cluster_only_calibration_configurations']}** configurations",
        f"- Total processed configurations: **{summary['total_processed_configurations']}**",
        f"- Total configuration-level observation units: **{summary['total_configuration_level_units']:,}**",
        f"- Source-deduplicated units in the validation panel: **{summary['validation_source_deduplicated_units']:,}**",
        "",
        "## Results kept separate",
        "",
        f"- Label-bearing validation: learned-neighborhood strict pass **{summary['main_learned_strict_passes']}/{summary['label_bearing_benchmark_configurations']}**; CSAE strict pass **{summary['main_context_specific_strict_passes']}/{summary['label_bearing_benchmark_configurations']}**.",
        f"- Cluster-only calibration: learned-neighborhood strict pass **{summary['calibration_learned_strict_passes']}/{summary['cluster_only_calibration_configurations']}**; CSAE strict pass **{summary['calibration_context_specific_strict_passes']}/{summary['cluster_only_calibration_configurations']}**.",
        "",
        "The 39 calibration sources use SODB-standardized Leiden clusters. They test ingestion, blocked execution and matched-null behavior, but they are not biological cell-type ground truth and are excluded from the primary efficacy denominator. The 100-source figure is therefore a processing-coverage statement, not a claim of 100 independent gold-standard cohorts. The validation panel contains 61 named sources and 59 known publication families; donor/slide/FOV independence is reported separately.",
        "",
        "## Panel table",
        "",
        "| source ID | panel | configurations | units | claim role |",
        "|---|---|---:|---:|---|",
    ]
    for row in portfolio.sort_values(["panel", "source_dataset_id"]).itertuples(index=False):
        lines.append(
            f"| {row.source_dataset_id} | {row.panel} | {int(row.n_configurations)} | "
            f"{int(row.source_deduplicated_units):,} | {row.claim_role} |"
        )
    (ROOT / "HUNDRED_SOURCE_PORTFOLIO.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
