from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent

PREVIEW_SOURCE = {
    "GEO_GSE240015_VISIUM_THYMUS_DOMAIN": "GSE240015",
    "GEO_GSE284005_MERSCOPE_MS": "GSE284005",
    "GEO_GSE327581_COSMX_AD_BRAIN": "GSE327581",
    "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR": "GSE333737",
    "GSE202623_LESION": "GSE202623",
    "SQUIDPY_IMC": "SQUIDPY_IMC",
    "SQUIDPY_MERFISH": "SQUIDPY_MERFISH",
    "SQUIDPY_MIBITOF": "SQUIDPY_MIBITOF",
    "SQUIDPY_SEQFISH": "SQUIDPY_SEQFISH",
    "SQUIDPY_SLIDESEQV2": "SQUIDPY_SLIDESEQV2",
    "SQUIDPY_VISIUM_FLUO": "SQUIDPY_VISIUM_FLUO",
    "SQUIDPY_VISIUM_HNE": "SQUIDPY_VISIUM_HNE",
}

PUBLICATION_FAMILY = {
    "SODB:Allen2022Molecular_aging": "SODB:Allen2022Molecular",
    "SODB:Allen2022Molecular_lps": "SODB:Allen2022Molecular",
    "SODB:Marshall2022High_human": "SODB:Marshall2022High",
    "SODB:Marshall2022High_mouse": "SODB:Marshall2022High",
}


def main() -> None:
    preview_summary = pd.read_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_summary.csv")
    preview = preview_summary.loc[preview_summary["model"].eq("marker_only"), ["dataset_id", "n"]].copy()
    preview["source_dataset_id"] = preview["dataset_id"].map(PREVIEW_SOURCE)
    if preview["source_dataset_id"].isna().any():
        missing = preview.loc[preview["source_dataset_id"].isna(), "dataset_id"].tolist()
        raise ValueError(f"Missing preview source mapping: {missing}")
    preview = preview.rename(columns={"n": "configuration_units"})
    preview["scale"] = "preview"
    preview["task_description"] = "preview blocked benchmark"

    expanded_registry = pd.read_csv(ROOT / "EXPANDED_SCALE_DATASETS.csv")
    expanded = expanded_registry[
        ["dataset_id", "source_dataset_id", "expanded_cells", "biological_context"]
    ].copy()
    expanded = expanded.rename(
        columns={
            "expanded_cells": "configuration_units",
            "biological_context": "task_description",
        }
    )
    expanded["scale"] = "expanded"

    configurations = pd.concat(
        [
            preview[["dataset_id", "source_dataset_id", "configuration_units", "scale", "task_description"]],
            expanded[["dataset_id", "source_dataset_id", "configuration_units", "scale", "task_description"]],
        ],
        ignore_index=True,
    )
    configurations["publication_family"] = configurations["source_dataset_id"].map(
        PUBLICATION_FAMILY
    )
    configurations["publication_family"] = configurations["publication_family"].fillna(
        configurations["source_dataset_id"]
    )
    expanded_sources = set(
        configurations.loc[configurations["scale"].eq("expanded"), "source_dataset_id"]
    )
    configurations["excluded_from_source_deduplicated_unit_total"] = (
        configurations["scale"].eq("preview")
        & configurations["source_dataset_id"].isin(expanded_sources)
    )
    configurations.to_csv(ROOT / "CONFIGURATION_SOURCE_MAP.csv", index=False)

    sources: list[dict] = []
    for source_id, group in configurations.groupby("source_dataset_id", sort=True):
        source_units = group.loc[
            ~group["excluded_from_source_deduplicated_unit_total"], "configuration_units"
        ].sum()
        sources.append(
            {
                "source_dataset_id": source_id,
                "publication_family": group["publication_family"].iloc[0],
                "n_configurations": int(len(group)),
                "scales": " | ".join(sorted(group["scale"].unique())),
                "configuration_units_total": int(group["configuration_units"].sum()),
                "source_deduplicated_units": int(source_units),
                "has_preview_subset_and_expanded_configuration": bool(
                    group["excluded_from_source_deduplicated_unit_total"].any()
                ),
                "independence_note": (
                    "named public source ID; not automatically an independent donor/cohort"
                ),
            }
        )
    source_registry = pd.DataFrame(sources)
    source_registry.to_csv(ROOT / "SOURCE_INDEPENDENCE_REGISTRY.csv", index=False)

    report = {
        "benchmark_configurations": int(len(configurations)),
        "public_source_ids": int(source_registry["source_dataset_id"].nunique()),
        "known_publication_families": int(source_registry["publication_family"].nunique()),
        "configuration_level_units": int(configurations["configuration_units"].sum()),
        "source_deduplicated_units": int(source_registry["source_deduplicated_units"].sum()),
        "preview_subset_units_excluded_from_source_deduplicated_total": int(
            configurations.loc[
                configurations["excluded_from_source_deduplicated_unit_total"],
                "configuration_units",
            ].sum()
        ),
        "sources_with_multiple_configurations": int(
            (source_registry["n_configurations"] > 1).sum()
        ),
        "known_cross_source_publication_family_merges": int(
            (source_registry.groupby("publication_family").size() > 1).sum()
        ),
    }
    (ROOT / "SOURCE_INDEPENDENCE_REPORT.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    lines = [
        "# Source independence accounting",
        "",
        f"- Benchmark configurations: **{report['benchmark_configurations']}**",
        f"- Named public source IDs: **{report['public_source_ids']}**",
        f"- Known publication families after merging Allen aging/LPS and Marshall human/mouse cohorts: **{report['known_publication_families']}**",
        f"- Configuration-level observation units: **{report['configuration_level_units']:,}**",
        f"- Source-deduplicated observation units: **{report['source_deduplicated_units']:,}**",
        f"- Preview subset units excluded from the source-deduplicated total: **{report['preview_subset_units_excluded_from_source_deduplicated_total']:,}**",
        "",
        "A source ID is a public dataset accession or named repository dataset, not an assertion of donor-level independence. Publication families, donors, slides, FOVs and generated spatial blocks remain separate levels of evidence. The source-deduplicated unit count removes preview subsets when an expanded configuration from the same source is present; it does not claim that every remaining cell is biologically independent.",
        "",
        "| source ID | publication family | configurations | scales | source-deduplicated units | duplicate preview subset |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in source_registry.sort_values("source_dataset_id").itertuples(index=False):
        lines.append(
            f"| {row.source_dataset_id} | {row.publication_family} | {row.n_configurations} | "
            f"{str(row.scales).replace('|', chr(92) + '|')} | {row.source_deduplicated_units:,} | "
            f"{'yes' if row.has_preview_subset_and_expanded_configuration else 'no'} |"
        )
    (ROOT / "SOURCE_INDEPENDENCE_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
