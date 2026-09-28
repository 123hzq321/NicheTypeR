from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and aggregate all prepared SODB benchmarks.")
    parser.add_argument("--registry", type=Path, default=ROOT / "EXPANDED_SCALE_DATASETS.csv")
    parser.add_argument("--aggregate-prefix", default="SODB_SCALE_LEAN_BENCHMARK")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--only", default="")
    return parser.parse_args()


def prefix_for(dataset_id: str) -> str:
    return dataset_id.removesuffix("_EXPANDED") + "_LEAN_BENCHMARK"


def completed(prefix: str) -> bool:
    required = [
        ROOT / f"{prefix}_summary.csv",
        ROOT / f"{prefix}_guardrail.csv",
        ROOT / f"{prefix}_pairwise.csv",
        ROOT / f"{prefix}_report.json",
    ]
    return all(path.exists() and path.stat().st_size > 0 for path in required)


def run_one(dataset_id: str, prefix: str, registry: Path) -> tuple[bool, str]:
    command = [
        sys.executable,
        str(ROOT / "run_single_expanded_lean_benchmark.py"),
        "--dataset-id",
        dataset_id,
        "--prefix",
        prefix,
        "--registry",
        str(registry.resolve()),
    ]
    result = subprocess.run(
        command,
        cwd=ROOT.parent.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    log_path = ROOT / f"{prefix}.log"
    log_path.write_text(
        result.stdout + ("\nSTDERR\n" + result.stderr if result.stderr else ""),
        encoding="utf-8",
    )
    if result.returncode != 0:
        tail = (result.stderr or result.stdout)[-1000:]
        return False, tail.replace("\n", " ")
    return True, ""


def aggregate(registry: pd.DataFrame, status: pd.DataFrame, aggregate_prefix: str) -> dict:
    summary_frames: list[pd.DataFrame] = []
    guardrail_frames: list[pd.DataFrame] = []
    for row in status.loc[status["completed"]].itertuples(index=False):
        summary_frames.append(pd.read_csv(ROOT / f"{row.prefix}_summary.csv"))
        guardrail_frames.append(pd.read_csv(ROOT / f"{row.prefix}_guardrail.csv"))
    summary = pd.concat(summary_frames, ignore_index=True) if summary_frames else pd.DataFrame()
    guardrail = pd.concat(guardrail_frames, ignore_index=True) if guardrail_frames else pd.DataFrame()
    summary.to_csv(ROOT / f"{aggregate_prefix}_summary.csv", index=False)
    guardrail.to_csv(ROOT / f"{aggregate_prefix}_guardrail.csv", index=False)

    completed_ids = set(status.loc[status["completed"], "dataset_id"])
    completed_registry = registry.loc[registry["dataset_id"].isin(completed_ids)]
    learned_passes = (
        int(guardrail["learned_passes_guardrail"].astype(bool).sum())
        if not guardrail.empty
        else 0
    )
    context_passes = (
        int(guardrail["context_specific_passes_guardrail"].astype(bool).sum())
        if not guardrail.empty
        else 0
    )
    report = {
        "prepared_sodb_configurations": int(len(registry)),
        "completed_sodb_configurations": int(len(completed_registry)),
        "completed_sodb_source_ids": int(completed_registry["source_dataset_id"].nunique()),
        "completed_unique_cells_or_spots": int(completed_registry["expanded_cells"].sum()),
        "learned_neighborhood_strict_passes": learned_passes,
        "context_specific_strict_passes": context_passes,
    }
    (ROOT / f"{aggregate_prefix}_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    lines = [
        f"# {aggregate_prefix.replace('_', ' ').title()}",
        "",
        "This table reports source-level configurations prepared after a complete representative-file audit of the downloadable SODB spatial-transcriptomics catalog. Multiple experiments from one publication remain one source ID.",
        "",
        f"- Completed configurations: **{report['completed_sodb_configurations']}**",
        f"- Completed source IDs: **{report['completed_sodb_source_ids']}**",
        f"- Unique cells/spots: **{report['completed_unique_cells_or_spots']:,}**",
        f"- Learned-neighborhood strict passes: **{learned_passes}/{len(guardrail)}**",
        f"- Context-specific strict passes: **{context_passes}/{len(guardrail)}**",
        "",
        "| dataset | task | cells/spots | labels | groups | marker F1 | learned F1 | learned strict | CSAE strict |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for registry_row in completed_registry.sort_values("dataset_id").itertuples(index=False):
        dataset_summary = summary.loc[summary["dataset_id"].eq(registry_row.dataset_id)]
        dataset_guardrail = guardrail.loc[guardrail["dataset_id"].eq(registry_row.dataset_id)]
        marker = dataset_summary.loc[dataset_summary["model"].eq("marker_only"), "macro_f1"]
        learned = dataset_summary.loc[
            dataset_summary["model"].eq("marker_learned_neighborhood"), "macro_f1"
        ]
        guard = dataset_guardrail.iloc[0]
        task = "spatial domain" if "spatial_domain" in str(registry_row.biological_context) else "cell type"
        lines.append(
            f"| {registry_row.source_dataset_id} | {task} | {int(registry_row.expanded_cells):,} | "
            f"{int(registry_row.n_labels)} | {int(registry_row.n_fov_groups)} | "
            f"{float(marker.iloc[0]):.4f} | {float(learned.iloc[0]):.4f} | "
            f"{'yes' if bool(guard.learned_passes_guardrail) else 'no'} | "
            f"{'yes' if bool(guard.context_specific_passes_guardrail) else 'no'} |"
        )
    (ROOT / f"{aggregate_prefix}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    args = parse_args()
    registry = pd.read_csv(args.registry)
    registry = registry.loc[registry["dataset_id"].astype(str).str.startswith("SODB_")].copy()
    if args.only:
        requested = {item.strip() for item in args.only.split(",") if item.strip()}
        registry = registry.loc[
            registry["dataset_id"].isin(requested)
            | registry["source_dataset_id"].isin(requested)
        ]
    status_rows: list[dict] = []
    for index, row in enumerate(registry.sort_values("dataset_id").itertuples(index=False), start=1):
        prefix = prefix_for(str(row.dataset_id))
        was_complete = completed(prefix)
        print(
            f"benchmark_start={index}/{len(registry)} dataset={row.dataset_id} cached={was_complete}",
            flush=True,
        )
        error = ""
        if args.force or not was_complete:
            ok, error = run_one(str(row.dataset_id), prefix, args.registry)
        else:
            ok = True
        status_rows.append(
            {
                "dataset_id": row.dataset_id,
                "source_dataset_id": row.source_dataset_id,
                "prefix": prefix,
                "completed": bool(ok and completed(prefix)),
                "reused_cached_result": bool(was_complete and not args.force),
                "error": error,
            }
        )
        print(
            f"benchmark_done={row.dataset_id} completed={status_rows[-1]['completed']}",
            flush=True,
        )
    status = pd.DataFrame(status_rows)
    status.to_csv(ROOT / f"{args.aggregate_prefix}_status.csv", index=False)
    report = aggregate(registry, status, args.aggregate_prefix)
    print(status.to_string(index=False, max_colwidth=100))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
