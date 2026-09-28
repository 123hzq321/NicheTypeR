from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
PREFIX = "LABEL_TASK_BENCHMARK"


INPUTS = [
    ("preview", ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_per_label.csv"),
    ("expanded", ROOT / "EXPANDED_SCALE_LEAN_BENCHMARK_per_label.csv"),
]


def load_per_label() -> pd.DataFrame:
    frames = []
    for scale, path in INPUTS:
        df = pd.read_csv(path, keep_default_na=False)
        df.insert(0, "scale", scale)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def pivot_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    return (
        df.pivot_table(
            index=["scale", "dataset_id", "label", "support"],
            columns="model",
            values=metric,
            aggfunc="first",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )


def build_task_table(per_label: pd.DataFrame) -> pd.DataFrame:
    f1 = pivot_metric(per_label, "f1")
    precision = pivot_metric(per_label, "precision")
    recall = pivot_metric(per_label, "recall")

    rows = f1[["scale", "dataset_id", "label", "support"]].copy()
    rows["task_id"] = rows["scale"] + "::" + rows["dataset_id"] + "::" + rows["label"].astype(str)
    rows["marker_f1"] = f1.get("marker_only")
    rows["learned_f1"] = f1.get("marker_learned_neighborhood")
    rows["random_graph_f1"] = f1.get("learned_random_graph")
    rows["permuted_prior_f1"] = f1.get("learned_permuted_prior")
    rows["context_specific_f1"] = f1.get("marker_context_specific_neighborhood")
    rows["smoothing_f1"] = f1.get("marker_spatial_smoothing", np.nan)
    rows["smoothing_random_f1"] = f1.get("marker_spatial_smoothing_random_graph", np.nan)
    rows["reference_profile_f1"] = f1.get("reference_profile", np.nan)
    rows["marker_reference_f1"] = f1.get("marker_reference_profile", np.nan)

    rows["marker_precision"] = precision.get("marker_only")
    rows["marker_recall"] = recall.get("marker_only")
    rows["learned_precision"] = precision.get("marker_learned_neighborhood")
    rows["learned_recall"] = recall.get("marker_learned_neighborhood")

    learned_control = rows[["marker_f1", "random_graph_f1", "permuted_prior_f1"]].max(axis=1)
    context_control = rows[["marker_f1", "learned_f1", "random_graph_f1", "permuted_prior_f1"]].max(axis=1)
    rows["learned_delta_vs_marker"] = rows["learned_f1"] - rows["marker_f1"]
    rows["learned_specific_f1_delta"] = rows["learned_f1"] - learned_control
    rows["context_delta_vs_marker"] = rows["context_specific_f1"] - rows["marker_f1"]
    rows["context_specific_f1_delta"] = rows["context_specific_f1"] - context_control
    rows["smoothing_delta_vs_marker"] = rows["smoothing_f1"] - rows["marker_f1"]
    rows["smoothing_specific_f1_delta"] = rows["smoothing_f1"] - rows[["marker_f1", "smoothing_random_f1"]].max(axis=1)
    rows["reference_delta_vs_marker"] = rows["reference_profile_f1"] - rows["marker_f1"]
    rows["marker_reference_delta_vs_marker"] = rows["marker_reference_f1"] - rows["marker_f1"]

    rows["learned_label_guardrail"] = rows["learned_specific_f1_delta"] > 0.01
    rows["context_label_guardrail"] = rows["context_specific_f1_delta"] > 0.01
    rows["smoothing_label_guardrail"] = rows["smoothing_specific_f1_delta"] > 0.01
    rows["learned_improved_over_marker"] = rows["learned_delta_vs_marker"] > 0.01
    rows["learned_harmed_vs_marker"] = rows["learned_delta_vs_marker"] < -0.01
    rows["context_improved_over_marker"] = rows["context_delta_vs_marker"] > 0.01
    rows["context_harmed_vs_marker"] = rows["context_delta_vs_marker"] < -0.01
    rows["support_bin"] = pd.cut(
        rows["support"],
        bins=[0, 25, 100, 500, 1000, np.inf],
        labels=["1-25", "26-100", "101-500", "501-1000", ">1000"],
        include_lowest=True,
    ).astype(str)
    return rows[
        [
            "task_id",
            "scale",
            "dataset_id",
            "label",
            "support",
            "support_bin",
            "marker_f1",
            "learned_f1",
            "random_graph_f1",
            "permuted_prior_f1",
            "context_specific_f1",
            "smoothing_f1",
            "reference_profile_f1",
            "marker_reference_f1",
            "learned_delta_vs_marker",
            "learned_specific_f1_delta",
            "context_delta_vs_marker",
            "context_specific_f1_delta",
            "smoothing_delta_vs_marker",
            "smoothing_specific_f1_delta",
            "reference_delta_vs_marker",
            "marker_reference_delta_vs_marker",
            "learned_label_guardrail",
            "context_label_guardrail",
            "smoothing_label_guardrail",
            "learned_improved_over_marker",
            "learned_harmed_vs_marker",
            "context_improved_over_marker",
            "context_harmed_vs_marker",
            "marker_precision",
            "marker_recall",
            "learned_precision",
            "learned_recall",
        ]
    ]


def summarize_tasks(tasks: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_name, df in [("all", tasks)] + [(scale, group) for scale, group in tasks.groupby("scale")]:
        rows.append({
            "scale": group_name,
            "n_label_tasks": int(df.shape[0]),
            "n_dataset_configs": int(df["dataset_id"].nunique()),
            "total_support": int(df["support"].sum()),
            "median_support": float(df["support"].median()),
            "learned_improved_tasks": int(df["learned_improved_over_marker"].sum()),
            "learned_harmed_tasks": int(df["learned_harmed_vs_marker"].sum()),
            "learned_guardrail_tasks": int(df["learned_label_guardrail"].sum()),
            "context_improved_tasks": int(df["context_improved_over_marker"].sum()),
            "context_harmed_tasks": int(df["context_harmed_vs_marker"].sum()),
            "context_guardrail_tasks": int(df["context_label_guardrail"].sum()),
            "smoothing_guardrail_tasks": int(df["smoothing_label_guardrail"].fillna(False).sum()),
            "median_learned_delta_vs_marker": float(df["learned_delta_vs_marker"].median()),
            "median_context_delta_vs_marker": float(df["context_delta_vs_marker"].median()),
        })
    return pd.DataFrame(rows)


def summarize_by_support(tasks: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scale, support_bin), df in tasks.groupby(["scale", "support_bin"], dropna=False):
        rows.append({
            "scale": scale,
            "support_bin": support_bin,
            "n_label_tasks": int(df.shape[0]),
            "learned_improved_tasks": int(df["learned_improved_over_marker"].sum()),
            "learned_harmed_tasks": int(df["learned_harmed_vs_marker"].sum()),
            "learned_guardrail_tasks": int(df["learned_label_guardrail"].sum()),
            "context_guardrail_tasks": int(df["context_label_guardrail"].sum()),
            "median_learned_delta_vs_marker": float(df["learned_delta_vs_marker"].median()),
            "median_context_delta_vs_marker": float(df["context_delta_vs_marker"].median()),
        })
    return pd.DataFrame(rows)


def write_report(tasks: pd.DataFrame, summary: pd.DataFrame, support_summary: pd.DataFrame) -> None:
    top_learned = tasks.sort_values("learned_specific_f1_delta", ascending=False).head(20)
    top_context = tasks.sort_values("context_specific_f1_delta", ascending=False).head(20)
    lines = [
        "# Label-Task Benchmark",
        "",
        "This analysis treats each dataset-label pair as a validation task. It does not",
        "increase the number of independent public datasets; instead it reports the",
        "granularity at which annotation audit tools are actually used: whether a",
        "specific label in a specific tissue dataset is rescued, harmed or supported",
        "by context beyond matched null controls.",
        "",
        "## Summary",
        "",
        "| scale | dataset configs | label tasks | total support | learned improved | learned harmed | learned guardrail | context guardrail |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.scale} | {row.n_dataset_configs} | {row.n_label_tasks} | "
            f"{row.total_support} | {row.learned_improved_tasks} | {row.learned_harmed_tasks} | "
            f"{row.learned_guardrail_tasks} | {row.context_guardrail_tasks} |"
        )
    lines.extend([
        "",
        "## Support Bins",
        "",
        "| scale | support bin | label tasks | learned improved | learned harmed | learned guardrail | context guardrail | median learned delta |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in support_summary.itertuples(index=False):
        lines.append(
            f"| {row.scale} | {row.support_bin} | {row.n_label_tasks} | "
            f"{row.learned_improved_tasks} | {row.learned_harmed_tasks} | "
            f"{row.learned_guardrail_tasks} | {row.context_guardrail_tasks} | "
            f"{row.median_learned_delta_vs_marker:+.4f} |"
        )
    lines.extend([
        "",
        "## Top Learned-Neighborhood Label Tasks",
        "",
        "| task | support | marker F1 | learned F1 | specific delta |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in top_learned.itertuples(index=False):
        lines.append(
            f"| {row.scale} / {row.dataset_id} / {row.label} | {int(row.support)} | "
            f"{row.marker_f1:.3f} | {row.learned_f1:.3f} | {row.learned_specific_f1_delta:+.3f} |"
        )
    lines.extend([
        "",
        "## Top Context-Specific Label Tasks",
        "",
        "| task | support | marker F1 | context F1 | specific delta |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in top_context.itertuples(index=False):
        lines.append(
            f"| {row.scale} / {row.dataset_id} / {row.label} | {int(row.support)} | "
            f"{row.marker_f1:.3f} | {row.context_specific_f1:.3f} | {row.context_specific_f1_delta:+.3f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The label-task view increases validation granularity, but not the number of",
        "independent cohorts. Positive label-level guardrails are useful for triage and",
        "case-study selection; dataset-level guardrails remain the primary claim for",
        "general performance.",
        "",
    ])
    (ROOT / f"{PREFIX}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    per_label = load_per_label()
    tasks = build_task_table(per_label)
    summary = summarize_tasks(tasks)
    support_summary = summarize_by_support(tasks)
    tasks.to_csv(ROOT / f"{PREFIX}.csv", index=False)
    summary.to_csv(ROOT / f"{PREFIX}_summary.csv", index=False)
    support_summary.to_csv(ROOT / f"{PREFIX}_support_bins.csv", index=False)
    (ROOT / f"{PREFIX}_report.json").write_text(
        json.dumps({
            "summary": json.loads(summary.to_json(orient="records")),
            "support_bins": json.loads(support_summary.to_json(orient="records")),
            "top_learned": json.loads(tasks.sort_values("learned_specific_f1_delta", ascending=False).head(50).to_json(orient="records")),
            "top_context": json.loads(tasks.sort_values("context_specific_f1_delta", ascending=False).head(50).to_json(orient="records")),
        }, indent=2),
        encoding="utf-8",
    )
    write_report(tasks, summary, support_summary)
    print(summary.to_string(index=False))
    print(f"Wrote {ROOT / f'{PREFIX}.md'}")


if __name__ == "__main__":
    main()
