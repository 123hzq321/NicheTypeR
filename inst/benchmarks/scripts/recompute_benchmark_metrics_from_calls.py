from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

import pandas as pd

import run_expanded_scale_lean_benchmark as lean
import run_multidataset_blocked_benchmark as base
import run_single_expanded_lean_benchmark as single


ROOT = Path(__file__).resolve().parent
PREVIEW_PREFIX = "MULTIDATASET_BLOCKED_BENCHMARK"
EXPANDED_PREFIX = "EXPANDED_SCALE_LEAN_BENCHMARK"


def bool_values(values: pd.Series) -> pd.Series:
    if values.dtype == bool:
        return values.astype(int)
    return values.astype(str).str.strip().str.lower().isin({"true", "1", "yes"}).astype(int)


def stream_metric_tables(path: Path, chunk_size: int = 200_000) -> tuple[pd.DataFrame, pd.DataFrame]:
    aggregate: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"n": 0, "correct": 0, "confidence": 0.0, "margin": 0.0, "conflict": 0}
    )
    confusion: Counter[tuple[str, str, str, str]] = Counter()
    labels: dict[tuple[str, str], set[str]] = defaultdict(set)

    columns = [
        "dataset_id",
        "model",
        "label",
        "truth",
        "correct",
        "confidence",
        "margin",
        "conflict_reason",
    ]
    for chunk in pd.read_csv(path, usecols=columns, chunksize=chunk_size, keep_default_na=False):
        for column in ["dataset_id", "model", "label", "truth", "conflict_reason"]:
            chunk[column] = chunk[column].astype(str)
        chunk["correct_value"] = bool_values(chunk["correct"])
        chunk["conflict_value"] = chunk["conflict_reason"].ne("consistent").astype(int)
        chunk["confidence"] = pd.to_numeric(chunk["confidence"], errors="coerce").fillna(0.0)
        chunk["margin"] = pd.to_numeric(chunk["margin"], errors="coerce").fillna(0.0)

        grouped = chunk.groupby(["dataset_id", "model"], sort=False).agg(
            n=("correct_value", "size"),
            correct=("correct_value", "sum"),
            confidence=("confidence", "sum"),
            margin=("margin", "sum"),
            conflict=("conflict_value", "sum"),
        )
        for key, row in grouped.iterrows():
            item = aggregate[(str(key[0]), str(key[1]))]
            for field in item:
                item[field] += float(row[field])

        counts = (
            chunk.groupby(["dataset_id", "model", "truth", "label"], sort=False)
            .size()
            .rename("count")
        )
        for (dataset_id, model, truth, prediction), count in counts.items():
            key = (str(dataset_id), str(model))
            truth = str(truth)
            prediction = str(prediction)
            confusion[(key[0], key[1], truth, prediction)] += int(count)
            labels[key].update((truth, prediction))

    truth_counts: Counter[tuple[str, str, str]] = Counter()
    prediction_counts: Counter[tuple[str, str, str]] = Counter()
    true_positives: Counter[tuple[str, str, str]] = Counter()
    for (dataset_id, model, truth, prediction), count in confusion.items():
        truth_counts[(dataset_id, model, truth)] += count
        prediction_counts[(dataset_id, model, prediction)] += count
        if truth == prediction:
            true_positives[(dataset_id, model, truth)] += count

    summary_rows = []
    per_label_rows = []
    for dataset_id, model in sorted(aggregate):
        f1_values = []
        for label in sorted(labels[(dataset_id, model)]):
            tp = true_positives[(dataset_id, model, label)]
            predicted = prediction_counts[(dataset_id, model, label)]
            support = truth_counts[(dataset_id, model, label)]
            precision = tp / predicted if predicted else 0.0
            recall = tp / support if support else 0.0
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            f1_values.append(f1)
            per_label_rows.append(
                {
                    "dataset_id": dataset_id,
                    "model": model,
                    "label": label,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "support": support,
                }
            )

        item = aggregate[(dataset_id, model)]
        n = int(item["n"])
        summary_rows.append(
            {
                "dataset_id": dataset_id,
                "model": model,
                "n": n,
                "accuracy": item["correct"] / n,
                "macro_f1": sum(f1_values) / len(f1_values),
                "mean_confidence": item["confidence"] / n,
                "mean_margin": item["margin"] / n,
                "conflict_rate": item["conflict"] / n,
            }
        )
    return pd.DataFrame(summary_rows), pd.DataFrame(per_label_rows)


def expanded_guardrail(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset_id, frame in summary.groupby("dataset_id", sort=False):
        metrics = frame.set_index("model")
        marker = metrics.loc["marker_only"]
        learned = metrics.loc["marker_learned_neighborhood"]
        random_graph = metrics.loc["learned_random_graph"]
        permuted = metrics.loc["learned_permuted_prior"]
        context = metrics.loc["marker_context_specific_neighborhood"]
        learned_delta = float(
            learned["macro_f1"]
            - max(marker["macro_f1"], random_graph["macro_f1"], permuted["macro_f1"])
        )
        learned_accuracy_delta = float(
            learned["accuracy"]
            - max(marker["accuracy"], random_graph["accuracy"], permuted["accuracy"])
        )
        context_delta = float(
            context["macro_f1"]
            - max(
                marker["macro_f1"],
                learned["macro_f1"],
                random_graph["macro_f1"],
                permuted["macro_f1"],
            )
        )
        context_accuracy_delta = float(
            context["accuracy"]
            - max(
                marker["accuracy"],
                learned["accuracy"],
                random_graph["accuracy"],
                permuted["accuracy"],
            )
        )
        learned_pass = learned_delta > 0.005 and learned_accuracy_delta > 0
        context_pass = context_delta > 0.005 and context_accuracy_delta > 0
        rows.append(
            {
                "dataset_id": dataset_id,
                "marker_macro_f1": float(marker["macro_f1"]),
                "learned_macro_f1": float(learned["macro_f1"]),
                "learned_random_macro_f1": float(random_graph["macro_f1"]),
                "learned_permuted_macro_f1": float(permuted["macro_f1"]),
                "learned_specific_macro_f1_delta": learned_delta,
                "learned_specific_accuracy_delta": learned_accuracy_delta,
                "learned_passes_guardrail": learned_pass,
                "context_specific_macro_f1": float(context["macro_f1"]),
                "context_specific_accuracy": float(context["accuracy"]),
                "context_specific_macro_f1_delta": context_delta,
                "context_specific_accuracy_delta": context_accuracy_delta,
                "context_specific_passes_guardrail": context_pass,
                "interpretation": (
                    "context-specific signal passes null guardrail"
                    if context_pass
                    else "learned neighborhood passes null guardrail"
                    if learned_pass
                    else "context signal is not specific under null controls"
                ),
            }
        )
    return pd.DataFrame(rows)


def recompute_preview() -> tuple[pd.DataFrame, pd.DataFrame]:
    calls_path = ROOT / f"{PREVIEW_PREFIX}_calls.csv"
    summary, per_label = stream_metric_tables(calls_path)
    calls = pd.read_csv(
        calls_path,
        keep_default_na=False,
        low_memory=False,
        dtype={
            "cell_id": str,
            "dataset_id": str,
            "model": str,
            "label": str,
            "truth": str,
        },
    )
    calls["correct"] = bool_values(calls["correct"]).astype(bool)
    pair_rows = []
    for dataset_id, frame in calls.groupby("dataset_id", sort=False):
        comparators = sorted(set(frame["model"].astype(str)) - {"marker_only"})
        for comparator in comparators:
            pair_rows.append(base.paired_comparison(calls, dataset_id, "marker_only", comparator))
    pairwise = pd.DataFrame(pair_rows)
    guardrail = base.guardrail_analysis(summary)
    summary.to_csv(ROOT / f"{PREVIEW_PREFIX}_summary.csv", index=False)
    per_label.to_csv(ROOT / f"{PREVIEW_PREFIX}_per_label.csv", index=False)
    pairwise.to_csv(ROOT / f"{PREVIEW_PREFIX}_pairwise.csv", index=False)
    guardrail.to_csv(ROOT / f"{PREVIEW_PREFIX}_guardrail.csv", index=False)

    report_path = ROOT / f"{PREVIEW_PREFIX}_report.json"
    previous = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    configs = previous.get("datasets", [])
    base.write_markdown_report(summary, pairwise, guardrail, configs)
    previous.update(
        {
            "summary": json.loads(summary.to_json(orient="records")),
            "pairwise": json.loads(pairwise.to_json(orient="records")),
            "guardrail": json.loads(guardrail.to_json(orient="records")),
            "metric_definition": "zero_division=0 for per-label precision, recall and F1",
        }
    )
    report_path.write_text(json.dumps(previous, indent=2), encoding="utf-8")
    return summary, guardrail


def recompute_expanded() -> tuple[pd.DataFrame, pd.DataFrame]:
    calls_path = ROOT / f"{EXPANDED_PREFIX}_calls.csv.gz"
    summary, per_label = stream_metric_tables(calls_path)
    guardrail = expanded_guardrail(summary)
    pairwise = pd.read_csv(ROOT / f"{EXPANDED_PREFIX}_pairwise.csv")
    summary.to_csv(ROOT / f"{EXPANDED_PREFIX}_summary.csv", index=False)
    per_label.to_csv(ROOT / f"{EXPANDED_PREFIX}_per_label.csv", index=False)
    guardrail.to_csv(ROOT / f"{EXPANDED_PREFIX}_guardrail.csv", index=False)

    folds = json.loads((ROOT / f"{EXPANDED_PREFIX}_folds.json").read_text(encoding="utf-8"))
    registry = pd.read_csv(ROOT / "EXPANDED_SCALE_DATASETS.csv")
    lean.write_report(summary, pairwise, guardrail, folds, registry.to_dict(orient="records"))
    report = {
        "dataset_configurations": int(summary["dataset_id"].nunique()),
        "unique_cells_or_spots": int(summary.loc[summary["model"].eq("marker_only"), "n"].sum()),
        "metric_definition": "zero_division=0 for per-label precision, recall and F1",
        "summary": json.loads(summary.to_json(orient="records")),
        "guardrail": json.loads(guardrail.to_json(orient="records")),
    }
    (ROOT / f"{EXPANDED_PREFIX}_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    suffix = "_summary.csv"
    for summary_path in sorted(ROOT.glob("*_LEAN_BENCHMARK_summary.csv")):
        if summary_path.name.startswith(EXPANDED_PREFIX):
            continue
        previous_summary = pd.read_csv(summary_path, usecols=["dataset_id"], nrows=1)
        if previous_summary.empty:
            continue
        dataset_id = str(previous_summary.iloc[0]["dataset_id"])
        dataset_summary = summary.loc[summary["dataset_id"].eq(dataset_id)].copy()
        dataset_labels = per_label.loc[per_label["dataset_id"].eq(dataset_id)].copy()
        dataset_guardrail = guardrail.loc[guardrail["dataset_id"].eq(dataset_id)].copy()
        if dataset_summary.empty:
            continue

        prefix = summary_path.name[: -len(suffix)]
        dataset_summary.to_csv(summary_path, index=False)
        dataset_labels.to_csv(ROOT / f"{prefix}_per_label.csv", index=False)
        dataset_guardrail.to_csv(ROOT / f"{prefix}_guardrail.csv", index=False)

        report_path = ROOT / f"{prefix}_report.json"
        item = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        item.update(
            {
                "summary": json.loads(dataset_summary.to_json(orient="records")),
                "guardrail": json.loads(dataset_guardrail.to_json(orient="records")),
                "metric_definition": "zero_division=0 for per-label precision, recall and F1",
            }
        )
        report_path.write_text(json.dumps(item, indent=2), encoding="utf-8")

        pairwise_path = ROOT / f"{prefix}_pairwise.csv"
        folds_path = ROOT / f"{prefix}_folds.json"
        if pairwise_path.exists() and folds_path.exists() and item.get("dataset"):
            dataset_pairwise = pd.read_csv(pairwise_path)
            dataset_folds = json.loads(folds_path.read_text(encoding="utf-8"))
            single.write_report(
                prefix,
                dataset_summary,
                dataset_pairwise,
                dataset_guardrail,
                dataset_folds,
                item["dataset"],
            )
    return summary, guardrail


def main() -> None:
    preview_summary, preview_guardrail = recompute_preview()
    expanded_summary, expanded_guardrail_table = recompute_expanded()
    print(
        json.dumps(
            {
                "preview_configs": int(preview_summary["dataset_id"].nunique()),
                "preview_learned_passes": int(preview_guardrail["learned_passes_guardrail"].sum()),
                "preview_context_passes": int(preview_guardrail["context_specific_passes_guardrail"].sum()),
                "expanded_configs": int(expanded_summary["dataset_id"].nunique()),
                "expanded_cells": int(
                    expanded_summary.loc[expanded_summary["model"].eq("marker_only"), "n"].sum()
                ),
                "expanded_learned_passes": int(
                    expanded_guardrail_table["learned_passes_guardrail"].sum()
                ),
                "expanded_context_passes": int(
                    expanded_guardrail_table["context_specific_passes_guardrail"].sum()
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
