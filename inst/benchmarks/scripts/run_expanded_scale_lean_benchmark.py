from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

import run_multidataset_blocked_benchmark as base


ROOT = Path(__file__).resolve().parent
PREFIX = "EXPANDED_SCALE_LEAN_BENCHMARK"
SEED = base.SEED


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def dataset_configs(registry_path: Path | None = None) -> list[base.BenchmarkDataset]:
    registry = pd.read_csv(registry_path or (ROOT / "EXPANDED_SCALE_DATASETS.csv"))
    configs: list[base.BenchmarkDataset] = []
    for row in registry.itertuples(index=False):
        configs.append(
            base.BenchmarkDataset(
                dataset_id=str(row.dataset_id),
                expression_path=resolve_path(str(row.expression_path)),
                metadata_path=resolve_path(str(row.metadata_path)),
                label_col=str(row.label_col),
                group_col=str(row.group_col),
                cell_id_col=str(row.cell_id_col),
                x_col=str(row.x_col),
                y_col=str(row.y_col),
                role="expanded_scale_validation",
                modality=str(row.modality),
                max_folds=3,
                top_markers_per_label=20,
            )
        )
    return configs


def fast_learn_niche_prior(
    edges: pd.DataFrame,
    labels: pd.Series,
    train_cells: list[str],
    candidate_labels: list[str],
    pseudocount: float = 1.0,
    clip: float = 3.0,
) -> pd.DataFrame:
    label_index = {label: i for i, label in enumerate(candidate_labels)}
    train_set = set(train_cells)
    train_edges = edges[edges["from"].isin(train_set) & edges["to"].isin(train_set)]
    counts = np.full((len(candidate_labels), len(candidate_labels)), pseudocount, dtype=float)
    if not train_edges.empty:
        label_by_cell = labels.astype(str).to_dict()
        src_labels = train_edges["from"].map(label_by_cell).map(label_index)
        dst_labels = train_edges["to"].map(label_by_cell).map(label_index)
        valid = src_labels.notna() & dst_labels.notna()
        np.add.at(counts, (src_labels[valid].astype(int).to_numpy(), dst_labels[valid].astype(int).to_numpy()), 1.0)
    conditional = counts / np.maximum(counts.sum(axis=1, keepdims=True), np.finfo(float).eps)
    background = counts.sum(axis=0, keepdims=True) / np.maximum(counts.sum(), np.finfo(float).eps)
    weights = np.log(conditional / np.maximum(background, np.finfo(float).eps))
    weights = np.clip(weights, -clip, clip)
    return pd.DataFrame(weights, index=candidate_labels, columns=candidate_labels)


def fast_neighbor_mix(edges: pd.DataFrame, probs: pd.DataFrame) -> pd.DataFrame:
    cell_index = {cell: i for i, cell in enumerate(probs.index)}
    src = edges["from"].map(cell_index)
    dst = edges["to"].map(cell_index)
    valid = src.notna() & dst.notna()
    src_idx = src[valid].astype(int).to_numpy()
    dst_idx = dst[valid].astype(int).to_numpy()
    values = probs.to_numpy(dtype=float)
    acc = np.zeros_like(values)
    if len(src_idx):
        np.add.at(acc, src_idx, values[dst_idx])
    degree = np.bincount(src_idx, minlength=values.shape[0]).reshape(-1, 1)
    mix = acc / np.maximum(degree, 1)
    missing = degree.ravel() == 0
    mix[missing] = values[missing]
    return pd.DataFrame(mix, index=probs.index, columns=probs.columns)


def fast_score_neighborhood(edges: pd.DataFrame, prior: pd.DataFrame, niche_weights: pd.DataFrame) -> pd.DataFrame:
    labels = list(prior.columns)
    probs = base.softmax_rows(prior)
    neighbor_mix = fast_neighbor_mix(edges, probs)
    compat = niche_weights.reindex(index=labels, columns=labels).fillna(0).to_numpy(dtype=float)
    score = neighbor_mix.to_numpy(dtype=float) @ compat.T
    return pd.DataFrame(score, index=prior.index, columns=labels)


def fast_context_specific(
    edges: pd.DataFrame,
    prior: pd.DataFrame,
    niche_weights: pd.DataFrame,
    null_edges: list[pd.DataFrame],
    null_weights: list[pd.DataFrame],
) -> pd.DataFrame:
    observed = fast_score_neighborhood(edges, prior, niche_weights)
    nulls = [fast_score_neighborhood(item, prior, niche_weights) for item in null_edges]
    nulls.extend(fast_score_neighborhood(edges, prior, item) for item in null_weights)
    null_mean = np.mean([item.loc[observed.index, observed.columns].to_numpy(dtype=float) for item in nulls], axis=0)
    residual = observed.to_numpy(dtype=float) - null_mean
    return pd.DataFrame(residual, index=observed.index, columns=observed.columns)


def fixed_weights(score_names: list[str]) -> dict[str, float]:
    if score_names == ["marker"]:
        return {"marker": 1.0}
    if score_names == ["reference"]:
        return {"reference": 1.0}
    weights = {name: 1.0 for name in score_names}
    if "marker" in weights:
        weights["marker"] = 1.5
    if "reference" in weights:
        weights["reference"] = 1.5
    for name in ["learned_neighborhood", "context_specific"]:
        if name in weights:
            weights[name] = 0.2
    return weights


def predict_fixed(
    dataset_id: str,
    fold: int,
    model_name: str,
    scores: dict[str, pd.DataFrame],
    truth: pd.Series,
    test_cells: list[str],
) -> pd.DataFrame:
    fit = base.infer(base.subset_scores(scores, test_cells), fixed_weights(list(scores)))
    calls = fit["calls"].copy()
    calls["truth"] = truth.loc[calls["cell_id"]].to_numpy()
    calls["correct"] = calls["label"].to_numpy() == calls["truth"].to_numpy()
    calls["dataset_id"] = dataset_id
    calls["fold"] = fold
    calls["model"] = model_name
    return calls


def evaluate_dataset(config: base.BenchmarkDataset) -> dict:
    print(f"\n=== {config.dataset_id} ===", flush=True)
    expr = base.read_expression(config.expression_path)
    metadata = base.read_metadata(config, list(expr.columns))
    truth = metadata.set_index("cell_id")["label"].astype(str)
    groups = metadata.set_index("cell_id")["fov_group"].astype(str)
    edges = base.build_edges(metadata, k=10)
    folds = base.make_folds(truth, groups, config.max_folds, SEED)

    all_calls = []
    all_markers = []
    fold_reports = []
    for fold_id, (train_idx, test_idx) in enumerate(folds, start=1):
        train_cells = truth.index[train_idx].tolist()
        test_cells = truth.index[test_idx].tolist()
        print(f"fold {fold_id}: train={len(train_cells)} test={len(test_cells)}", flush=True)

        z = base.z_by_feature_train(expr, train_cells)
        marker, marker_db = base.learn_marker_scores(z, truth, train_cells, top_n=config.top_markers_per_label)
        marker_db.insert(0, "fold", fold_id)
        marker_db.insert(0, "dataset_id", config.dataset_id)
        all_markers.append(marker_db)
        reference = base.learn_reference_profile_scores(z, truth, train_cells, candidate_labels=list(marker.columns))
        random_edges = base.random_edges_like(edges, metadata, SEED + fold_id)
        niche_weights = fast_learn_niche_prior(edges, truth, train_cells, list(marker.columns))
        learned = fast_score_neighborhood(edges, marker, niche_weights)
        learned_random = fast_score_neighborhood(random_edges, marker, niche_weights)
        permuted_weights = base.permute_niche_prior(niche_weights, SEED + 100 + fold_id)
        learned_permuted = fast_score_neighborhood(edges, marker, permuted_weights)
        context_specific = fast_context_specific(
            edges=edges,
            prior=marker,
            niche_weights=niche_weights,
            null_edges=[random_edges],
            null_weights=[permuted_weights],
        )

        model_scores = {
            "marker_only": {"marker": marker},
            "reference_profile": {"reference": reference},
            "marker_reference_profile": {"marker": marker, "reference": reference},
            "marker_learned_neighborhood": {"marker": marker, "learned_neighborhood": learned},
            "learned_random_graph": {"marker": marker, "learned_neighborhood": learned_random},
            "learned_permuted_prior": {"marker": marker, "learned_neighborhood": learned_permuted},
            "marker_context_specific_neighborhood": {"marker": marker, "context_specific": context_specific},
        }
        for model_name, scores in model_scores.items():
            all_calls.append(predict_fixed(config.dataset_id, fold_id, model_name, scores, truth, test_cells))

        fold_reports.append({
            "dataset_id": config.dataset_id,
            "fold": fold_id,
            "train_cells": len(train_cells),
            "test_cells": len(test_cells),
            "train_groups": int(groups.loc[train_cells].nunique()),
            "test_groups": int(groups.loc[test_cells].nunique()),
            "test_label_counts": truth.loc[test_cells].value_counts().to_dict(),
        })

    return {
        "config": asdict(config) | {
            "expression_path": str(config.expression_path),
            "metadata_path": str(config.metadata_path),
        },
        "calls": pd.concat(all_calls, ignore_index=True),
        "markers": pd.concat(all_markers, ignore_index=True),
        "fold_reports": fold_reports,
    }


def summarize_all(calls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    per_label_rows = []
    pair_rows = []
    guardrail_rows = []
    comparators = [
        "reference_profile",
        "marker_reference_profile",
        "marker_learned_neighborhood",
        "learned_random_graph",
        "learned_permuted_prior",
        "marker_context_specific_neighborhood",
    ]
    for (dataset_id, model), df in calls.groupby(["dataset_id", "model"], sort=False):
        truth = df.set_index("cell_id")["truth"].astype(str)
        summary, per_label = base.metric_summary(df[["cell_id", "label", "confidence", "margin", "conflict_reason"]], truth)
        summary_rows.append({"dataset_id": dataset_id, "model": model, **summary})
        per_label.insert(0, "model", model)
        per_label.insert(0, "dataset_id", dataset_id)
        per_label_rows.append(per_label)
    summary_df = pd.DataFrame(summary_rows)

    for dataset_id in calls["dataset_id"].drop_duplicates():
        for comparator in comparators:
            pair_rows.append(base.paired_comparison(calls, dataset_id, "marker_only", comparator))
        metrics = summary_df[summary_df["dataset_id"] == dataset_id].set_index("model")
        marker = metrics.loc["marker_only"]
        learned = metrics.loc["marker_learned_neighborhood"]
        random_graph = metrics.loc["learned_random_graph"]
        permuted = metrics.loc["learned_permuted_prior"]
        context = metrics.loc["marker_context_specific_neighborhood"]
        learned_control_macro = max(marker["macro_f1"], random_graph["macro_f1"], permuted["macro_f1"])
        learned_control_acc = max(marker["accuracy"], random_graph["accuracy"], permuted["accuracy"])
        context_control_macro = max(marker["macro_f1"], learned["macro_f1"], random_graph["macro_f1"], permuted["macro_f1"])
        context_control_acc = max(marker["accuracy"], learned["accuracy"], random_graph["accuracy"], permuted["accuracy"])
        learned_delta = float(learned["macro_f1"] - learned_control_macro)
        learned_acc_delta = float(learned["accuracy"] - learned_control_acc)
        context_delta = float(context["macro_f1"] - context_control_macro)
        context_acc_delta = float(context["accuracy"] - context_control_acc)
        learned_pass = learned_delta > 0.005 and learned_acc_delta > 0
        context_pass = context_delta > 0.005 and context_acc_delta > 0
        guardrail_rows.append({
            "dataset_id": dataset_id,
            "marker_macro_f1": float(marker["macro_f1"]),
            "learned_macro_f1": float(learned["macro_f1"]),
            "learned_random_macro_f1": float(random_graph["macro_f1"]),
            "learned_permuted_macro_f1": float(permuted["macro_f1"]),
            "learned_specific_macro_f1_delta": learned_delta,
            "learned_specific_accuracy_delta": learned_acc_delta,
            "learned_passes_guardrail": learned_pass,
            "context_specific_macro_f1": float(context["macro_f1"]),
            "context_specific_accuracy": float(context["accuracy"]),
            "context_specific_macro_f1_delta": context_delta,
            "context_specific_accuracy_delta": context_acc_delta,
            "context_specific_passes_guardrail": context_pass,
            "interpretation": (
                "context-specific signal passes null guardrail"
                if context_pass
                else "learned neighborhood passes null guardrail"
                if learned_pass
                else "context signal is not specific under null controls"
            ),
        })

    return (
        summary_df,
        pd.concat(per_label_rows, ignore_index=True),
        pd.DataFrame(pair_rows),
        pd.DataFrame(guardrail_rows),
    )


def write_report(
    summary: pd.DataFrame,
    pairwise: pd.DataFrame,
    guardrail: pd.DataFrame,
    fold_reports: list[dict],
    configs: list[dict],
) -> None:
    registry = pd.read_csv(ROOT / "EXPANDED_SCALE_DATASETS.csv")
    fold_df = pd.DataFrame(fold_reports)
    size_rows = (
        fold_df.groupby("dataset_id")
        .agg(
            folds=("fold", "count"),
            mean_train_cells=("train_cells", "mean"),
            mean_test_cells=("test_cells", "mean"),
            min_test_cells=("test_cells", "min"),
            max_test_cells=("test_cells", "max"),
            mean_train_groups=("train_groups", "mean"),
            mean_test_groups=("test_groups", "mean"),
        )
        .reset_index()
    )
    lines = [
        "# Expanded-Scale Lean Blocked Benchmark",
        "",
        "This stress test uses larger train/test splits than the preview benchmark.",
        "It keeps the core marker, reference-profile, learned-neighborhood, random-graph,",
        "permuted-prior and context-specific residual comparisons, with fixed evidence weights",
        "to avoid turning the scale-control experiment into another tuning benchmark.",
        "",
        "## Dataset Scale",
        "",
        "| dataset | source | cells/spots | features | labels | spatial groups | sampling |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in registry.itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.source_dataset_id} | {int(row.expanded_cells)} | "
            f"{int(row.expanded_features)} | {int(row.n_labels)} | {int(row.n_fov_groups)} | {row.sampling} |"
        )

    lines.extend([
        "",
        "## Fold Size",
        "",
        "| dataset | folds | mean train | mean test | min test | max test | mean train groups | mean test groups |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in size_rows.sort_values("dataset_id").itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {int(row.folds)} | {row.mean_train_cells:.0f} | "
            f"{row.mean_test_cells:.0f} | {int(row.min_test_cells)} | {int(row.max_test_cells)} | "
            f"{row.mean_train_groups:.1f} | {row.mean_test_groups:.1f} |"
        )

    lines.extend([
        "",
        "## Model Summary",
        "",
        "| dataset | model | accuracy | macro-F1 | conflict rate |",
        "|---|---|---:|---:|---:|",
    ])
    for row in summary.sort_values(["dataset_id", "model"]).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.model} | {row.accuracy:.4f} | "
            f"{row.macro_f1:.4f} | {row.conflict_rate:.4f} |"
        )

    lines.extend([
        "",
        "## Specificity Guardrail",
        "",
        "| dataset | context delta macro-F1 | context pass | learned delta macro-F1 | learned pass | interpretation |",
        "|---|---:|---|---:|---|---|",
    ])
    for row in guardrail.sort_values("dataset_id").itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.context_specific_macro_f1_delta:+.4f} | "
            f"{'yes' if row.context_specific_passes_guardrail else 'no'} | "
            f"{row.learned_specific_macro_f1_delta:+.4f} | "
            f"{'yes' if row.learned_passes_guardrail else 'no'} | {row.interpretation} |"
        )

    lines.extend([
        "",
        "## Paired Comparisons vs Marker-Only",
        "",
        "| dataset | comparator | accuracy diff | McNemar p |",
        "|---|---|---:|---:|",
    ])
    for row in pairwise.sort_values(["dataset_id", "comparator_model"]).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.comparator_model} | {row.accuracy_diff:+.4f} | {row.mcnemar_exact_p:.4g} |"
        )

    lines.extend([
        "",
        "## Dataset Configs",
        "",
        "```json",
        json.dumps(configs, indent=2),
        "```",
        "",
    ])
    (ROOT / f"{PREFIX}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    outputs = [evaluate_dataset(config) for config in dataset_configs()]
    calls = pd.concat([item["calls"] for item in outputs], ignore_index=True)
    markers = pd.concat([item["markers"] for item in outputs], ignore_index=True)
    fold_reports = [fold for item in outputs for fold in item["fold_reports"]]
    summary, per_label, pairwise, guardrail = summarize_all(calls)
    configs = [item["config"] for item in outputs]

    calls.to_csv(ROOT / f"{PREFIX}_calls.csv.gz", index=False)
    markers.to_csv(ROOT / f"{PREFIX}_learned_markers.csv", index=False)
    summary.to_csv(ROOT / f"{PREFIX}_summary.csv", index=False)
    per_label.to_csv(ROOT / f"{PREFIX}_per_label.csv", index=False)
    pairwise.to_csv(ROOT / f"{PREFIX}_pairwise.csv", index=False)
    guardrail.to_csv(ROOT / f"{PREFIX}_guardrail.csv", index=False)
    (ROOT / f"{PREFIX}_folds.json").write_text(json.dumps(fold_reports, indent=2), encoding="utf-8")
    write_report(summary, pairwise, guardrail, fold_reports, configs)

    report = {
        "seed": SEED,
        "n_datasets": len(outputs),
        "datasets": configs,
        "folds": fold_reports,
        "summary": json.loads(summary.to_json(orient="records")),
        "pairwise": json.loads(pairwise.to_json(orient="records")),
        "guardrail": json.loads(guardrail.to_json(orient="records")),
    }
    (ROOT / f"{PREFIX}_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nExpanded-scale lean summary", flush=True)
    print(summary.sort_values(["dataset_id", "model"]).to_string(index=False), flush=True)
    print(f"\nWrote {ROOT / (PREFIX + '.md')}", flush=True)


if __name__ == "__main__":
    main()
