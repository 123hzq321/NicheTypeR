from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from run_multidataset_blocked_benchmark import (
    SEED,
    build_edges,
    dataset_configs,
    infer,
    learn_marker_scores,
    learn_niche_prior,
    learn_reference_profile_scores,
    make_folds,
    metric_summary,
    paired_comparison,
    read_expression,
    read_metadata,
    score_neighborhood,
    subset_scores,
    z_by_feature_train,
)


ROOT = Path(__file__).resolve().parent
OLD_CALLS = ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv"
CALLS_OUT = ROOT / "REFERENCE_PROFILE_BASELINE_calls.csv"
SUMMARY_OUT = ROOT / "REFERENCE_PROFILE_BASELINE_summary.csv"
PAIRWISE_OUT = ROOT / "REFERENCE_PROFILE_BASELINE_pairwise.csv"
REPORT_OUT = ROOT / "REFERENCE_PROFILE_BASELINE.md"


FIXED_MODELS = {
    "reference_profile": {
        "score_names": ["reference"],
        "weights": {"reference": 1.0},
    },
    "marker_reference_profile": {
        "score_names": ["marker", "reference"],
        "weights": {"marker": 1.5, "reference": 1.5},
    },
    "reference_profile_learned_neighborhood": {
        "score_names": ["reference", "learned_neighborhood"],
        "weights": {"reference": 1.5, "learned_neighborhood": 0.5},
    },
}


def predict_fixed(
    dataset_id: str,
    fold: int,
    model_name: str,
    scores: dict[str, pd.DataFrame],
    weights: dict[str, float],
    truth: pd.Series,
    test_cells: list[str],
) -> pd.DataFrame:
    fit = infer(subset_scores(scores, test_cells), weights)
    calls = fit["calls"].copy()
    calls["truth"] = truth.loc[calls["cell_id"]].to_numpy()
    calls["correct"] = calls["label"].to_numpy() == calls["truth"].to_numpy()
    calls["dataset_id"] = dataset_id
    calls["fold"] = fold
    calls["model"] = model_name
    for key, value in weights.items():
        calls[f"w_{key}"] = value
    return calls


def evaluate_reference_baselines() -> pd.DataFrame:
    all_calls = []
    for config in dataset_configs():
        print(f"\n=== {config.dataset_id} reference-profile add-on ===")
        expr = read_expression(config.expression_path)
        metadata = read_metadata(config, list(expr.columns))
        truth = metadata.set_index("cell_id")["label"].astype(str)
        groups = metadata.set_index("cell_id")["fov_group"].astype(str)
        edges = build_edges(metadata, k=10)
        folds = make_folds(truth, groups, config.max_folds, SEED)

        for fold_id, (train_idx, test_idx) in enumerate(folds, start=1):
            train_cells = truth.index[train_idx].tolist()
            test_cells = truth.index[test_idx].tolist()
            print(f"fold {fold_id}: train={len(train_cells)} test={len(test_cells)}")

            z = z_by_feature_train(expr, train_cells)
            marker, _ = learn_marker_scores(
                z,
                truth,
                train_cells,
                top_n=config.top_markers_per_label,
            )
            reference = learn_reference_profile_scores(
                z,
                truth,
                train_cells,
                candidate_labels=list(marker.columns),
            )
            niche_weights = learn_niche_prior(edges, truth, train_cells, list(marker.columns))
            reference_learned = score_neighborhood(edges, reference, niche_weights)

            score_pool = {
                "marker": marker,
                "reference": reference,
                "learned_neighborhood": reference_learned,
            }
            for model_name, spec in FIXED_MODELS.items():
                scores = {name: score_pool[name] for name in spec["score_names"]}
                calls = predict_fixed(
                    config.dataset_id,
                    fold_id,
                    model_name,
                    scores,
                    spec["weights"],
                    truth,
                    test_cells,
                )
                all_calls.append(calls)

    return pd.concat(all_calls, ignore_index=True)


def summarize_reference(calls: pd.DataFrame, old_calls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    for (dataset_id, model), df in calls.groupby(["dataset_id", "model"], sort=False):
        truth = df.set_index("cell_id")["truth"].astype(str)
        summary, _ = metric_summary(
            df[["cell_id", "label", "confidence", "margin", "conflict_reason"]],
            truth,
        )
        summary_rows.append({"dataset_id": dataset_id, "model": model, **summary})
    summary = pd.DataFrame(summary_rows)

    combined = pd.concat([
        old_calls[old_calls["model"] == "marker_only"],
        calls,
    ], ignore_index=True, sort=False)
    pair_rows = []
    for dataset_id in calls["dataset_id"].drop_duplicates():
        for comparator in FIXED_MODELS:
            pair_rows.append(paired_comparison(combined, dataset_id, "marker_only", comparator))
    return summary, pd.DataFrame(pair_rows)


def write_report(summary: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    lines = [
        "# Reference-Profile Baseline Add-On",
        "",
        "This add-on benchmark adds a dependency-free reference-profile baseline",
        "to the existing blocked 12-dataset benchmark. Label centroids are learned",
        "inside training spatial blocks and scored on held-out blocks by cosine",
        "similarity. This is a lightweight reference-style comparator, not a claim",
        "that NicheTypeR reimplements SingleR, Seurat label transfer, CellTypist or",
        "scmap.",
        "",
        "Models:",
        "",
        "- `reference_profile`: reference centroid similarity only",
        "- `marker_reference_profile`: fixed fusion of marker and reference evidence",
        "- `reference_profile_learned_neighborhood`: reference evidence audited with a learned neighborhood prior",
        "",
        "## Summary",
        "",
        "| dataset | model | accuracy | macro-F1 | conflict rate |",
        "|---|---|---:|---:|---:|",
    ]
    for row in summary.sort_values(["dataset_id", "model"]).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.model} | {row.accuracy:.4f} | "
            f"{row.macro_f1:.4f} | {row.conflict_rate:.4f} |"
        )

    lines.extend([
        "",
        "## Paired Comparisons vs Marker-Only",
        "",
        "| dataset | comparator | accuracy diff | marker wrong, comparator right | marker right, comparator wrong | McNemar p |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for row in pairwise.sort_values(["dataset_id", "comparator_model"]).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.comparator_model} | {row.accuracy_diff:+.4f} | "
            f"{row.baseline_wrong_comparator_right} | {row.baseline_right_comparator_wrong} | "
            f"{row.mcnemar_exact_p:.4g} |"
        )

    best = summary.sort_values(["dataset_id", "macro_f1", "accuracy"], ascending=[True, False, False]).groupby("dataset_id").head(1)
    lines.extend([
        "",
        "## Best Reference-Style Add-On Per Dataset",
        "",
        "| dataset | best model | accuracy | macro-F1 |",
        "|---|---|---:|---:|",
    ])
    for row in best.itertuples(index=False):
        lines.append(f"| {row.dataset_id} | {row.model} | {row.accuracy:.4f} | {row.macro_f1:.4f} |")

    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    old_calls = pd.read_csv(OLD_CALLS)
    calls = evaluate_reference_baselines()
    summary, pairwise = summarize_reference(calls, old_calls)
    calls.to_csv(CALLS_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    write_report(summary, pairwise)
    report = {
        "models": FIXED_MODELS,
        "summary": json.loads(summary.to_json(orient="records")),
        "pairwise": json.loads(pairwise.to_json(orient="records")),
    }
    (ROOT / "REFERENCE_PROFILE_BASELINE_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(summary.sort_values(["dataset_id", "model"]).to_string(index=False))


if __name__ == "__main__":
    main()
