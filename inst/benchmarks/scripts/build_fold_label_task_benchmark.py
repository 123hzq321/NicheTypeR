from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
PREFIX = "FOLD_LABEL_TASK_BENCHMARK"
MIN_SUPPORT_FOR_GUARDRAIL = 10

INPUTS = [
    ("preview", ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv"),
    ("expanded", ROOT / "EXPANDED_SCALE_LEAN_BENCHMARK_calls.csv.gz"),
]


def metric_frame(calls: pd.DataFrame, scale: str) -> pd.DataFrame:
    keys = ["dataset_id", "fold"]
    truth_once = calls[["dataset_id", "fold", "cell_id", "truth"]].drop_duplicates()
    truth_counts = (
        truth_once.groupby(keys + ["truth"], sort=False)
        .size()
        .rename("support")
        .reset_index()
        .rename(columns={"truth": "label"})
    )
    pred_counts = (
        calls.groupby(keys + ["model", "label"], sort=False)
        .size()
        .rename("predicted")
        .reset_index()
    )
    true_positive = (
        calls.loc[calls["label"].astype(str) == calls["truth"].astype(str)]
        .groupby(keys + ["model", "truth"], sort=False)
        .size()
        .rename("tp")
        .reset_index()
        .rename(columns={"truth": "label"})
    )
    models = calls["model"].drop_duplicates().astype(str).tolist()
    model_index = pd.DataFrame({"model": models})
    base = truth_counts.merge(model_index, how="cross")
    out = (
        base.merge(pred_counts, on=keys + ["model", "label"], how="left")
        .merge(true_positive, on=keys + ["model", "label"], how="left")
    )
    out[["predicted", "tp"]] = out[["predicted", "tp"]].fillna(0)
    out["precision"] = out["tp"] / out["predicted"].replace(0, np.nan)
    out["recall"] = out["tp"] / out["support"].replace(0, np.nan)
    denom = out["precision"] + out["recall"]
    out["f1"] = np.where(denom > 0, 2 * out["precision"] * out["recall"] / denom, 0.0)
    out["precision"] = out["precision"].fillna(0.0)
    out["recall"] = out["recall"].fillna(0.0)
    out.insert(0, "scale", scale)
    return out


def load_fold_metrics() -> pd.DataFrame:
    frames = []
    for scale, path in INPUTS:
        print(f"Loading {path.name}", flush=True)
        calls = pd.read_csv(
            path,
            usecols=["cell_id", "dataset_id", "fold", "model", "label", "truth"],
            low_memory=False,
            keep_default_na=False,
        )
        for col in ["dataset_id", "model", "label", "truth"]:
            calls[col] = calls[col].astype(str)
        frames.append(metric_frame(calls, scale))
    return pd.concat(frames, ignore_index=True)


def pivot_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    return (
        df.pivot_table(
            index=["scale", "dataset_id", "fold", "label", "support"],
            columns="model",
            values=metric,
            aggfunc="first",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )


def build_fold_tasks(metrics: pd.DataFrame) -> pd.DataFrame:
    f1 = pivot_metric(metrics, "f1")
    rows = f1[["scale", "dataset_id", "fold", "label", "support"]].copy()
    rows["task_id"] = (
        rows["scale"]
        + "::"
        + rows["dataset_id"]
        + "::fold_"
        + rows["fold"].astype(str)
        + "::"
        + rows["label"].astype(str)
    )
    rows["marker_f1"] = f1.get("marker_only")
    rows["learned_f1"] = f1.get("marker_learned_neighborhood")
    rows["random_graph_f1"] = f1.get("learned_random_graph")
    rows["permuted_prior_f1"] = f1.get("learned_permuted_prior")
    rows["context_specific_f1"] = f1.get("marker_context_specific_neighborhood")
    rows["smoothing_f1"] = f1.get("marker_spatial_smoothing", np.nan)
    rows["smoothing_random_f1"] = f1.get("marker_spatial_smoothing_random_graph", np.nan)
    rows["reference_profile_f1"] = f1.get("reference_profile", np.nan)
    rows["marker_reference_f1"] = f1.get("marker_reference_profile", np.nan)

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

    enough = rows["support"] >= MIN_SUPPORT_FOR_GUARDRAIL
    rows["learned_fold_guardrail"] = enough & (rows["learned_specific_f1_delta"] > 0.01)
    rows["context_fold_guardrail"] = enough & (rows["context_specific_f1_delta"] > 0.01)
    rows["smoothing_fold_guardrail"] = enough & (rows["smoothing_specific_f1_delta"] > 0.01)
    rows["learned_improved_over_marker"] = enough & (rows["learned_delta_vs_marker"] > 0.01)
    rows["learned_harmed_vs_marker"] = enough & (rows["learned_delta_vs_marker"] < -0.01)
    rows["context_improved_over_marker"] = enough & (rows["context_delta_vs_marker"] > 0.01)
    rows["context_harmed_vs_marker"] = enough & (rows["context_delta_vs_marker"] < -0.01)
    return rows


def summarize_fold_tasks(tasks: pd.DataFrame) -> pd.DataFrame:
    rows = []
    eligible = tasks[tasks["support"] >= MIN_SUPPORT_FOR_GUARDRAIL]
    for group_name, df in [("all", eligible)] + [(scale, group) for scale, group in eligible.groupby("scale")]:
        rows.append({
            "scale": group_name,
            "n_fold_label_tasks": int(df.shape[0]),
            "n_dataset_configs": int(df["dataset_id"].nunique()),
            "total_support": int(df["support"].sum()),
            "median_support": float(df["support"].median()),
            "learned_improved_tasks": int(df["learned_improved_over_marker"].sum()),
            "learned_harmed_tasks": int(df["learned_harmed_vs_marker"].sum()),
            "learned_guardrail_tasks": int(df["learned_fold_guardrail"].sum()),
            "context_improved_tasks": int(df["context_improved_over_marker"].sum()),
            "context_harmed_tasks": int(df["context_harmed_vs_marker"].sum()),
            "context_guardrail_tasks": int(df["context_fold_guardrail"].sum()),
            "smoothing_guardrail_tasks": int(df["smoothing_fold_guardrail"].fillna(False).sum()),
            "median_learned_delta_vs_marker": float(df["learned_delta_vs_marker"].median()),
            "median_context_delta_vs_marker": float(df["context_delta_vs_marker"].median()),
        })
    return pd.DataFrame(rows)


def summarize_reproducibility(tasks: pd.DataFrame) -> pd.DataFrame:
    eligible = tasks[tasks["support"] >= MIN_SUPPORT_FOR_GUARDRAIL].copy()
    rows = []
    for (scale, dataset_id, label), df in eligible.groupby(["scale", "dataset_id", "label"], sort=False):
        learned_folds = int(df["learned_fold_guardrail"].sum())
        context_folds = int(df["context_fold_guardrail"].sum())
        n_folds = int(df["fold"].nunique())
        rows.append({
            "scale": scale,
            "dataset_id": dataset_id,
            "label": label,
            "n_eligible_folds": n_folds,
            "total_support": int(df["support"].sum()),
            "median_support": float(df["support"].median()),
            "learned_guardrail_folds": learned_folds,
            "context_guardrail_folds": context_folds,
            "smoothing_guardrail_folds": int(df["smoothing_fold_guardrail"].fillna(False).sum()),
            "median_learned_specific_f1_delta": float(df["learned_specific_f1_delta"].median()),
            "median_context_specific_f1_delta": float(df["context_specific_f1_delta"].median()),
            "learned_reproducible": learned_folds >= 2 and float(df["learned_specific_f1_delta"].median()) > 0.01,
            "context_reproducible": context_folds >= 2 and float(df["context_specific_f1_delta"].median()) > 0.01,
        })
    return pd.DataFrame(rows)


def summarize_repro(repro: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_name, df in [("all", repro)] + [(scale, group) for scale, group in repro.groupby("scale")]:
        rows.append({
            "scale": group_name,
            "n_dataset_label_tasks_with_eligible_folds": int(df.shape[0]),
            "learned_reproducible_tasks": int(df["learned_reproducible"].sum()),
            "context_reproducible_tasks": int(df["context_reproducible"].sum()),
            "median_eligible_folds": float(df["n_eligible_folds"].median()),
            "median_learned_guardrail_folds": float(df["learned_guardrail_folds"].median()),
            "median_context_guardrail_folds": float(df["context_guardrail_folds"].median()),
        })
    return pd.DataFrame(rows)


def write_report(tasks: pd.DataFrame, summary: pd.DataFrame, repro: pd.DataFrame, repro_summary: pd.DataFrame) -> None:
    top_fold = tasks[tasks["support"] >= MIN_SUPPORT_FOR_GUARDRAIL].sort_values("learned_specific_f1_delta", ascending=False).head(25)
    top_repro = repro.sort_values(["learned_reproducible", "learned_guardrail_folds", "median_learned_specific_f1_delta"], ascending=False).head(25)
    lines = [
        "# Fold-Label Task Benchmark",
        "",
        "This analysis decomposes each benchmark into fold-level dataset-label tasks.",
        "It asks whether a label-level context gain appears in held-out folds rather",
        "than only after aggregation. Fold-label tasks are validation units, not",
        "independent public datasets.",
        "",
        f"Guardrail counts use fold-label tasks with support >= {MIN_SUPPORT_FOR_GUARDRAIL}.",
        "",
        "## Fold-Label Summary",
        "",
        "| scale | dataset configs | fold-label tasks | total support | learned improved | learned harmed | learned guardrail | context guardrail |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.scale} | {row.n_dataset_configs} | {row.n_fold_label_tasks} | "
            f"{row.total_support} | {row.learned_improved_tasks} | {row.learned_harmed_tasks} | "
            f"{row.learned_guardrail_tasks} | {row.context_guardrail_tasks} |"
        )
    lines.extend([
        "",
        "## Reproducible Dataset-Label Tasks",
        "",
        "| scale | eligible dataset-label tasks | learned reproducible | context reproducible | median eligible folds |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in repro_summary.itertuples(index=False):
        lines.append(
            f"| {row.scale} | {row.n_dataset_label_tasks_with_eligible_folds} | "
            f"{row.learned_reproducible_tasks} | {row.context_reproducible_tasks} | "
            f"{row.median_eligible_folds:.1f} |"
        )
    lines.extend([
        "",
        "## Top Fold-Level Learned-Neighborhood Tasks",
        "",
        "| task | support | marker F1 | learned F1 | specific delta |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in top_fold.itertuples(index=False):
        lines.append(
            f"| {row.scale} / {row.dataset_id} / fold {row.fold} / {row.label} | "
            f"{int(row.support)} | {row.marker_f1:.3f} | {row.learned_f1:.3f} | "
            f"{row.learned_specific_f1_delta:+.3f} |"
        )
    lines.extend([
        "",
        "## Top Reproducible Dataset-Label Tasks",
        "",
        "| task | eligible folds | learned guardrail folds | median learned specific delta | total support |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in top_repro.itertuples(index=False):
        lines.append(
            f"| {row.scale} / {row.dataset_id} / {row.label} | "
            f"{row.n_eligible_folds} | {row.learned_guardrail_folds} | "
            f"{row.median_learned_specific_f1_delta:+.3f} | {row.total_support} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Fold-label analysis is useful for stress-testing whether label-level context",
        "signals recur across blocked splits. It strengthens audit evidence for",
        "candidate case studies, but dataset-level guardrails remain the primary",
        "generalization claim.",
        "",
    ])
    (ROOT / f"{PREFIX}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    metrics = load_fold_metrics()
    tasks = build_fold_tasks(metrics)
    summary = summarize_fold_tasks(tasks)
    repro = summarize_reproducibility(tasks)
    repro_summary = summarize_repro(repro)

    metrics.to_csv(ROOT / f"{PREFIX}_per_model_metrics.csv", index=False)
    tasks.to_csv(ROOT / f"{PREFIX}.csv", index=False)
    summary.to_csv(ROOT / f"{PREFIX}_summary.csv", index=False)
    repro.to_csv(ROOT / f"{PREFIX}_reproducibility.csv", index=False)
    repro_summary.to_csv(ROOT / f"{PREFIX}_reproducibility_summary.csv", index=False)
    (ROOT / f"{PREFIX}_report.json").write_text(
        json.dumps({
            "summary": json.loads(summary.to_json(orient="records")),
            "reproducibility_summary": json.loads(repro_summary.to_json(orient="records")),
            "top_fold_tasks": json.loads(tasks.sort_values("learned_specific_f1_delta", ascending=False).head(50).to_json(orient="records")),
            "top_reproducible_tasks": json.loads(repro.sort_values(["learned_reproducible", "learned_guardrail_folds", "median_learned_specific_f1_delta"], ascending=False).head(50).to_json(orient="records")),
        }, indent=2),
        encoding="utf-8",
    )
    write_report(tasks, summary, repro, repro_summary)
    print(summary.to_string(index=False))
    print(repro_summary.to_string(index=False))
    print(f"Wrote {ROOT / f'{PREFIX}.md'}")


if __name__ == "__main__":
    main()
