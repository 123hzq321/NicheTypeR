from __future__ import annotations

import glob
import json
import os
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
PREFIX = "EXPANDED_SCALE_LEAN_BENCHMARK"


def individual_files(kind: str) -> list[Path]:
    paths = [Path(path) for path in glob.glob(str(ROOT / f"SODB_*_LEAN_BENCHMARK_{kind}"))]
    return sorted(path for path in paths if "SODB_SCALE_" not in path.name)


def merge_table(kind: str) -> pd.DataFrame:
    target = ROOT / f"{PREFIX}_{kind}.csv"
    base = pd.read_csv(target)
    base = base.loc[~base["dataset_id"].astype(str).str.startswith("SODB_")]
    additions = [pd.read_csv(path) for path in individual_files(f"{kind}.csv")]
    merged = pd.concat([base, *additions], ignore_index=True)
    merged.to_csv(target, index=False)
    return merged


def merge_markers() -> None:
    target = ROOT / f"{PREFIX}_learned_markers.csv"
    base = pd.read_csv(target)
    if "dataset_id" in base:
        base = base.loc[~base["dataset_id"].astype(str).str.startswith("SODB_")]
    additions = [pd.read_csv(path) for path in individual_files("learned_markers.csv")]
    pd.concat([base, *additions], ignore_index=True).to_csv(target, index=False)


def merge_folds() -> list[dict]:
    target = ROOT / f"{PREFIX}_folds.json"
    base = json.loads(target.read_text(encoding="utf-8"))
    base = [row for row in base if not str(row.get("dataset_id", "")).startswith("SODB_")]
    additions: list[dict] = []
    for path in individual_files("folds.json"):
        additions.extend(json.loads(path.read_text(encoding="utf-8")))
    merged = base + additions
    target.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def merge_calls() -> None:
    target = ROOT / f"{PREFIX}_calls.csv.gz"
    temporary = target.with_name(target.name + ".tmp")
    first = True
    for chunk in pd.read_csv(target, chunksize=250_000, low_memory=False):
        chunk = chunk.loc[~chunk["dataset_id"].astype(str).str.startswith("SODB_")]
        if chunk.empty:
            continue
        chunk.to_csv(
            temporary,
            mode="w" if first else "a",
            header=first,
            index=False,
            compression="gzip",
        )
        first = False
    for path in individual_files("calls.csv.gz"):
        frame = pd.read_csv(path)
        frame.to_csv(
            temporary,
            mode="a",
            header=first,
            index=False,
            compression="gzip",
        )
        first = False
    os.replace(temporary, target)


def write_report(summary: pd.DataFrame, guardrail: pd.DataFrame) -> dict:
    registry = pd.read_csv(ROOT / "EXPANDED_SCALE_DATASETS.csv")
    report = {
        "dataset_configurations": int(registry["dataset_id"].nunique()),
        "unique_cells_or_spots": int(registry["expanded_cells"].sum()),
        "metric_definition": "zero_division=0 for per-label precision, recall and F1",
        "summary": json.loads(summary.to_json(orient="records")),
        "guardrail": json.loads(guardrail.to_json(orient="records")),
    }
    (ROOT / f"{PREFIX}_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    learned_passes = int(guardrail["learned_passes_guardrail"].astype(bool).sum())
    context_passes = int(guardrail["context_specific_passes_guardrail"].astype(bool).sum())
    lines = [
        "# Expanded-scale lean benchmark",
        "",
        f"- Completed configurations: **{report['dataset_configurations']}**",
        f"- Configuration-level unique cells/spots: **{report['unique_cells_or_spots']:,}**",
        f"- Learned-neighborhood strict passes: **{learned_passes}/{len(guardrail)}**",
        f"- Context-specific strict passes: **{context_passes}/{len(guardrail)}**",
        "",
        "The total is configuration-level. Source IDs, publications, donors, slides and FOVs are reported separately and must not be treated as interchangeable independent cohorts.",
        "",
        "| dataset | marker F1 | learned F1 | random F1 | permuted F1 | learned strict | CSAE F1 | CSAE strict |",
        "|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for row in guardrail.sort_values("dataset_id").itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.marker_macro_f1:.4f} | {row.learned_macro_f1:.4f} | "
            f"{row.learned_random_macro_f1:.4f} | {row.learned_permuted_macro_f1:.4f} | "
            f"{'yes' if bool(row.learned_passes_guardrail) else 'no'} | "
            f"{row.context_specific_macro_f1:.4f} | "
            f"{'yes' if bool(row.context_specific_passes_guardrail) else 'no'} |"
        )
    (ROOT / f"{PREFIX}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    report_path = ROOT / f"{PREFIX}_report.json"
    summary = merge_table("summary")
    guardrail = merge_table("guardrail")
    merge_table("pairwise")
    merge_table("per_label")
    merge_markers()
    merge_folds()
    merge_calls()
    report = write_report(summary, guardrail)
    print(json.dumps(report | {
        "learned_neighborhood_strict_passes": int(
            guardrail["learned_passes_guardrail"].astype(bool).sum()
        ),
        "context_specific_strict_passes": int(
            guardrail["context_specific_passes_guardrail"].astype(bool).sum()
        ),
    }, indent=2)[:2000])


if __name__ == "__main__":
    main()
