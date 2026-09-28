from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd

import run_expanded_scale_lean_benchmark as lean


ROOT = Path(__file__).resolve().parent
WORKDIR = ROOT.parents[1]
DEFAULT_DOWNLOAD_ROOT = Path(r"D:\NicheTypeR_GEO_100_QUEUE")
DEFAULT_PREPARED_ROOT = DEFAULT_DOWNLOAD_ROOT / "prepared"
MAIN_PREFIX = "EXPANDED_SCALE_LEAN_BENCHMARK"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download, prepare, benchmark and merge one GEO accession.")
    parser.add_argument("--accession", required=True)
    parser.add_argument("--download-root", default=str(DEFAULT_DOWNLOAD_ROOT))
    parser.add_argument("--prepared-root", default=str(DEFAULT_PREPARED_ROOT))
    parser.add_argument("--file-limit-per-accession", type=int, default=80)
    parser.add_argument("--max-file-mb", type=float, default=1000.0)
    parser.add_argument("--max-total-mb", type=float, default=1500.0)
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-merge", action="store_true")
    return parser.parse_args()


def run_command(cmd: list[str], timeout: int | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(WORKDIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout or ""


def parse_prepare_json(output: str) -> dict:
    start = output.rfind("{")
    if start < 0:
        return {"prepared": False, "reason": "no JSON object in prepare output"}
    return json.loads(output[start:])


def merge_single(prefix: str, dataset_id: str) -> dict:
    calls_path = ROOT / f"{MAIN_PREFIX}_calls.csv.gz"
    markers_path = ROOT / f"{MAIN_PREFIX}_learned_markers.csv"
    folds_path = ROOT / f"{MAIN_PREFIX}_folds.json"
    new_calls_path = ROOT / f"{prefix}_calls.csv.gz"
    new_markers_path = ROOT / f"{prefix}_learned_markers.csv"
    new_folds_path = ROOT / f"{prefix}_folds.json"

    calls = pd.read_csv(calls_path, low_memory=False)
    new_calls = pd.read_csv(new_calls_path, low_memory=False)
    for df in (calls, new_calls):
        for col in ["dataset_id", "model", "cell_id", "truth", "label", "conflict_reason"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
    calls = calls[calls["dataset_id"] != dataset_id]
    merged_calls = pd.concat([calls, new_calls], ignore_index=True)
    summary, per_label, pairwise, guardrail = lean.summarize_all(merged_calls)

    markers = pd.read_csv(markers_path, low_memory=False)
    new_markers = pd.read_csv(new_markers_path, low_memory=False)
    if "dataset_id" in markers.columns:
        markers = markers[markers["dataset_id"] != dataset_id]
    merged_markers = pd.concat([markers, new_markers], ignore_index=True)

    fold_reports = []
    if folds_path.exists():
        fold_reports.extend(json.loads(folds_path.read_text(encoding="utf-8")))
    fold_reports = [row for row in fold_reports if str(row.get("dataset_id")) != dataset_id]
    fold_reports.extend(json.loads(new_folds_path.read_text(encoding="utf-8")))

    configs = []
    for config in lean.dataset_configs():
        item = asdict(config)
        for key, value in list(item.items()):
            if isinstance(value, Path):
                item[key] = str(value)
        configs.append(item)

    merged_calls.to_csv(calls_path, index=False)
    merged_markers.to_csv(markers_path, index=False)
    summary.to_csv(ROOT / f"{MAIN_PREFIX}_summary.csv", index=False)
    per_label.to_csv(ROOT / f"{MAIN_PREFIX}_per_label.csv", index=False)
    pairwise.to_csv(ROOT / f"{MAIN_PREFIX}_pairwise.csv", index=False)
    guardrail.to_csv(ROOT / f"{MAIN_PREFIX}_guardrail.csv", index=False)
    folds_path.write_text(json.dumps(fold_reports, indent=2), encoding="utf-8")
    lean.write_report(summary, pairwise, guardrail, fold_reports, configs)
    (ROOT / f"{MAIN_PREFIX}_report.json").write_text(
        json.dumps(
            {
                "n_datasets": int(summary["dataset_id"].nunique()),
                "n_cells_model_calls": int(len(merged_calls) // merged_calls["model"].nunique()),
                "models": sorted(map(str, merged_calls["model"].unique())),
                "learned_passes_guardrail": int(guardrail["learned_passes_guardrail"].sum()),
                "context_specific_passes_guardrail": int(guardrail["context_specific_passes_guardrail"].sum()),
                "appended_dataset": dataset_id,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "merged_dataset": dataset_id,
        "expanded_configs": int(summary["dataset_id"].nunique()),
        "expanded_cells_spots": int(len(merged_calls) // merged_calls["model"].nunique()),
        "expanded_learned_passes_guardrail": int(guardrail["learned_passes_guardrail"].sum()),
        "expanded_context_passes_guardrail": int(guardrail["context_specific_passes_guardrail"].sum()),
    }


def main() -> None:
    args = parse_args()
    result: dict = {"accession": args.accession}
    if not args.skip_download:
        code, output = run_command(
            [
                sys.executable,
                str(ROOT / "download_hundred_dataset_queue.py"),
                "--out",
                args.download_root,
                "--accession",
                args.accession,
                "--file-limit-per-accession",
                str(args.file_limit_per_accession),
                "--max-file-mb",
                str(args.max_file_mb),
                "--max-total-mb",
                str(args.max_total_mb),
                "--download",
                "--decompress-h5ad",
            ],
            timeout=60 * 60 * 6,
        )
        result["download_code"] = code
        result["download_tail"] = output[-3000:]
        if code != 0:
            print(json.dumps(result, indent=2))
            raise SystemExit(code)

    code, output = run_command(
        [
            sys.executable,
            str(ROOT / "prepare_geo100_generic_dataset.py"),
            "--accession",
            args.accession,
            "--download-root",
            args.download_root,
            "--prepared-root",
            args.prepared_root,
        ],
        timeout=60 * 60 * 2,
    )
    prepared = parse_prepare_json(output)
    result["prepare_code"] = code
    result["prepare"] = prepared
    if code != 0 or not prepared.get("prepared"):
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if code == 0 else code)

    dataset_id = str(prepared["dataset_id"])
    prefix = f"GEO100_{args.accession}_LEAN_BENCHMARK"
    code, output = run_command(
        [
            sys.executable,
            str(ROOT / "run_single_expanded_lean_benchmark.py"),
            "--dataset-id",
            dataset_id,
            "--prefix",
            prefix,
        ],
        timeout=60 * 60 * 6,
    )
    result["benchmark_code"] = code
    result["benchmark_tail"] = output[-3000:]
    if code != 0:
        print(json.dumps(result, indent=2))
        raise SystemExit(code)

    if not args.skip_merge:
        result["merge"] = merge_single(prefix, dataset_id)
        run_command([sys.executable, str(ROOT / "build_hundred_dataset_expansion_queue.py")], timeout=300)
        run_command([sys.executable, str(ROOT / "build_label_task_benchmark.py")], timeout=300)
        run_command([sys.executable, str(ROOT / "build_fold_label_task_benchmark.py")], timeout=600)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
