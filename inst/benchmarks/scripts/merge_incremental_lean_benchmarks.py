from __future__ import annotations

import gzip
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
PREFIX = "EXPANDED_SCALE_LEAN_BENCHMARK"
TABLE_KEYS = {
    "summary.csv": ["dataset_id", "model"],
    "guardrail.csv": ["dataset_id"],
    "pairwise.csv": ["dataset_id", "baseline_model", "comparator_model"],
    "per_label.csv": ["dataset_id", "model", "label"],
    "learned_markers.csv": ["dataset_id", "fold", "cell_type", "feature", "direction"],
}


def incremental_files(suffix: str) -> list[Path]:
    return sorted(
        path
        for path in ROOT.glob(f"*_LEAN_BENCHMARK_{suffix}")
        if not path.name.startswith(PREFIX)
    )


def merge_table(suffix: str, keys: list[str]) -> tuple[int, int]:
    target = ROOT / f"{PREFIX}_{suffix}"
    frames = [pd.read_csv(target, keep_default_na=False)] if target.exists() else []
    for path in incremental_files(suffix):
        frames.append(pd.read_csv(path, keep_default_na=False))
    if not frames:
        return 0, 0
    before = len(frames[0]) if frames else 0
    merged = pd.concat(frames, ignore_index=True, sort=False)
    present_keys = [key for key in keys if key in merged.columns]
    # CSV inference can represent the same numeric-looking label as ``1`` in
    # one file and ``"1"`` in another.  Deduplicate on normalized keys while
    # preserving the original columns and latest row.
    normalized_keys = []
    for key in present_keys:
        normalized = f"__merge_key_{key}"
        merged[normalized] = merged[key].astype("string").fillna("<NA>")
        normalized_keys.append(normalized)
    merged = merged.drop_duplicates(normalized_keys, keep="last").drop(columns=normalized_keys)
    sort_keys = [key for key in keys if key in merged.columns]
    if sort_keys:
        merged = merged.sort_values(sort_keys).reset_index(drop=True)
    merged.to_csv(target, index=False)
    return before, len(merged)


def merge_folds() -> int:
    target = ROOT / f"{PREFIX}_folds.json"
    rows = json.loads(target.read_text(encoding="utf-8")) if target.exists() else []
    for path in sorted(ROOT.glob("*_LEAN_BENCHMARK_folds.json")):
        if path.name.startswith(PREFIX):
            continue
        rows.extend(json.loads(path.read_text(encoding="utf-8")))
    dedup = {}
    for row in rows:
        dedup[(str(row.get("dataset_id")), int(row.get("fold", 0)))] = row
    merged = [dedup[key] for key in sorted(dedup)]
    target.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return len(merged)


def merge_calls(chunk_size: int = 100_000) -> tuple[int, int]:
    """Stream call-level outputs while replacing rerun datasets atomically."""
    target = ROOT / f"{PREFIX}_calls.csv.gz"
    sources = incremental_files("calls.csv.gz")
    if not sources:
        return 0, 0

    replacements: dict[str, Path] = {}
    for path in sources:
        first = pd.read_csv(path, usecols=["dataset_id"], nrows=1, keep_default_na=False)
        if first.empty:
            continue
        replacements[str(first.iloc[0]["dataset_id"])] = path

    temporary = target.with_name(f"{target.name}.tmp")
    rows_written = 0
    wrote_header = False
    try:
        with gzip.open(temporary, "wt", encoding="utf-8", newline="") as handle:
            if target.exists():
                for chunk in pd.read_csv(
                    target, chunksize=chunk_size, low_memory=False, keep_default_na=False
                ):
                    chunk = chunk.loc[~chunk["dataset_id"].astype(str).isin(replacements)]
                    if chunk.empty:
                        continue
                    chunk.to_csv(handle, index=False, header=not wrote_header)
                    wrote_header = True
                    rows_written += len(chunk)

            for dataset_id, path in sorted(replacements.items()):
                for chunk in pd.read_csv(
                    path, chunksize=chunk_size, low_memory=False, keep_default_na=False
                ):
                    if not chunk["dataset_id"].astype(str).eq(dataset_id).all():
                        raise ValueError(f"{path.name} contains more than one dataset_id")
                    chunk.to_csv(handle, index=False, header=not wrote_header)
                    wrote_header = True
                    rows_written += len(chunk)

        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return rows_written, len(replacements)


def main() -> None:
    for suffix, keys in TABLE_KEYS.items():
        before, after = merge_table(suffix, keys)
        print(f"{suffix}: {before} -> {after}")
    print(f"folds.json: {merge_folds()}")
    call_rows, replaced_datasets = merge_calls()
    print(f"calls.csv.gz: {call_rows} rows; refreshed datasets={replaced_datasets}")
    guardrail = pd.read_csv(ROOT / f"{PREFIX}_guardrail.csv")
    summary = pd.read_csv(ROOT / f"{PREFIX}_summary.csv")
    print(
        json.dumps(
            {
                "expanded_dataset_configurations": int(guardrail["dataset_id"].nunique()),
                "expanded_cells": int(
                    summary.loc[summary["model"].eq("marker_only"), "n"].sum()
                ),
                "learned_guardrail_passes": int(guardrail["learned_passes_guardrail"].astype(bool).sum()),
                "context_guardrail_passes": int(
                    guardrail["context_specific_passes_guardrail"].astype(bool).sum()
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
