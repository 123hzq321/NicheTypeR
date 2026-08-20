from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
FILES = [
    ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv",
    ROOT / "REFERENCE_PROFILE_BASELINE_calls.csv",
    ROOT / "SEURAT_LABEL_TRANSFER_BASELINE_calls.csv",
]

OUT_PREFIX = ROOT / "INCREMENTAL_AUDIT_BENCHMARK"

BASE_FEATURES = ["risk_margin", "risk_confidence"]
CONFLICT_FEATURES = [
    "flag_marker_conflict",
    "flag_reference_conflict",
    "flag_spatial_smoothing_conflict",
    "flag_learned_neighborhood_conflict",
    "flag_context_specific_conflict",
    "flag_nonmargin_conflict",
    "severity_nonmargin",
]


def safe_auc(y_true: pd.Series | np.ndarray, score: pd.Series | np.ndarray) -> float:
    y = np.asarray(y_true, dtype=int)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, np.asarray(score, dtype=float)))


def safe_ap(y_true: pd.Series | np.ndarray, score: pd.Series | np.ndarray) -> float:
    y = np.asarray(y_true, dtype=int)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(average_precision_score(y, np.asarray(score, dtype=float)))


def add_risk_features(calls: pd.DataFrame) -> pd.DataFrame:
    calls = calls.copy()
    reason = calls["conflict_reason"].fillna("consistent").astype(str)
    calls["wrong"] = (~calls["correct"].astype(bool)).astype(int)
    calls["risk_margin"] = -calls["margin"].astype(float)
    calls["risk_confidence"] = 1.0 - calls["confidence"].astype(float)
    calls["flag_low_margin"] = reason.str.contains("low_margin", regex=False).astype(int)
    calls["flag_marker_conflict"] = reason.str.contains("marker_conflict", regex=False).astype(int)
    calls["flag_reference_conflict"] = reason.str.contains("reference_conflict", regex=False).astype(int)
    calls["flag_spatial_smoothing_conflict"] = reason.str.contains("spatial_smoothing_conflict", regex=False).astype(int)
    calls["flag_learned_neighborhood_conflict"] = reason.str.contains("learned_neighborhood_conflict", regex=False).astype(int)
    calls["flag_context_specific_conflict"] = reason.str.contains("context_specific_conflict", regex=False).astype(int)
    nonmargin = [
        "flag_marker_conflict",
        "flag_reference_conflict",
        "flag_spatial_smoothing_conflict",
        "flag_learned_neighborhood_conflict",
        "flag_context_specific_conflict",
    ]
    calls["flag_nonmargin_conflict"] = (calls[nonmargin].sum(axis=1) > 0).astype(int)
    calls["severity_nonmargin"] = (
        0.75 * calls["flag_marker_conflict"]
        + 0.40 * calls["flag_reference_conflict"]
        + 0.20 * calls["flag_spatial_smoothing_conflict"]
        + 0.35 * calls["flag_learned_neighborhood_conflict"]
        + 0.50 * calls["flag_context_specific_conflict"]
    ).clip(upper=1.0)
    return calls


def load_calls() -> pd.DataFrame:
    frames = []
    for path in FILES:
        if not path.exists():
            continue
        frame = pd.read_csv(
            path,
            usecols=[
                "cell_id",
                "dataset_id",
                "model",
                "correct",
                "confidence",
                "margin",
                "conflict_reason",
            ],
            low_memory=False,
        )
        if path.name == "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv":
            source = "blocked_multidataset"
        elif path.name == "REFERENCE_PROFILE_BASELINE_calls.csv":
            source = "reference_profile_baseline"
        else:
            source = "seurat_label_transfer_baseline"
        frame["source_set"] = source
        frames.append(frame)
    if not frames:
        raise FileNotFoundError("No audit call tables were found.")
    calls = pd.concat(frames, ignore_index=True)
    calls = add_risk_features(calls)
    finite = np.isfinite(calls[["risk_margin", "risk_confidence"]].to_numpy()).all(axis=1)
    return calls.loc[finite].reset_index(drop=True)


def logo_predict(calls: pd.DataFrame, features: list[str], score_name: str) -> pd.Series:
    scores = pd.Series(np.nan, index=calls.index, dtype=float)
    for dataset_id in sorted(calls["dataset_id"].unique()):
        test = calls["dataset_id"].eq(dataset_id)
        train = ~test
        y_train = calls.loc[train, "wrong"].astype(int)
        if y_train.nunique() < 2:
            continue
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced", solver="lbfgs"),
        )
        model.fit(calls.loc[train, features], y_train)
        scores.loc[test] = model.predict_proba(calls.loc[test, features])[:, 1]
    if scores.isna().any():
        missing = calls.loc[scores.isna(), "dataset_id"].unique().tolist()
        raise RuntimeError(f"Missing LOGO predictions for {score_name}: {missing}")
    return scores


def top_precision(y: pd.Series, score: pd.Series, fraction: float = 0.10) -> float:
    if len(y) == 0:
        return float("nan")
    n_top = max(1, int(np.ceil(len(y) * fraction)))
    order = np.argsort(-score.to_numpy(dtype=float), kind="mergesort")[:n_top]
    return float(y.iloc[order].mean())


def summarize(frame: pd.DataFrame, score_cols: dict[str, str], unit: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    dataset_rows = []
    y = frame["wrong"].astype(int)
    for label, col in score_cols.items():
        overall_rows.append(
            {
                "unit": unit,
                "score": label,
                "n_units": int(len(frame)),
                "n_datasets": int(frame["dataset_id"].nunique()),
                "wrong_rate": float(y.mean()),
                "auroc": safe_auc(y, frame[col]),
                "auprc": safe_ap(y, frame[col]),
                "top10_precision": top_precision(y, frame[col], 0.10),
            }
        )
        for dataset_id, sub in frame.groupby("dataset_id", sort=True):
            yy = sub["wrong"].astype(int)
            dataset_rows.append(
                {
                    "unit": unit,
                    "dataset_id": dataset_id,
                    "score": label,
                    "n_units": int(len(sub)),
                    "wrong_rate": float(yy.mean()),
                    "auroc": safe_auc(yy, sub[col]),
                    "auprc": safe_ap(yy, sub[col]),
                    "top10_precision": top_precision(yy, sub[col], 0.10),
                }
            )
    return pd.DataFrame(overall_rows), pd.DataFrame(dataset_rows)


def aggregate_unique_cells(calls: pd.DataFrame, score_cols: dict[str, str]) -> pd.DataFrame:
    aggregations = {
        "wrong": "max",
        "source_set": lambda x: ";".join(sorted(set(map(str, x)))),
        "model": lambda x: ";".join(sorted(set(map(str, x)))),
    }
    for col in score_cols.values():
        aggregations[col] = "max"
    return (
        calls.groupby(["dataset_id", "cell_id"], as_index=False)
        .agg(aggregations)
        .reset_index(drop=True)
    )


def bootstrap_dataset_ci(dataset_metrics: pd.DataFrame, score_a: str, score_b: str, metric: str, seed: int = 20260820) -> dict:
    pivot = dataset_metrics.pivot_table(index="dataset_id", columns="score", values=metric, aggfunc="mean")
    pivot = pivot[[score_a, score_b]].dropna()
    rng = np.random.default_rng(seed)
    datasets = pivot.index.to_numpy()
    if len(datasets) == 0:
        return {
            "metric": metric,
            "score_a": score_a,
            "score_b": score_b,
            "n_datasets": 0,
            "delta_mean": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
        }
    deltas = []
    for _ in range(4000):
        sample = rng.choice(datasets, size=len(datasets), replace=True)
        diff = pivot.loc[sample, score_b].to_numpy() - pivot.loc[sample, score_a].to_numpy()
        deltas.append(float(np.nanmean(diff)))
    observed = float(np.nanmean(pivot[score_b] - pivot[score_a]))
    return {
        "metric": metric,
        "score_a": score_a,
        "score_b": score_b,
        "n_datasets": int(len(datasets)),
        "delta_mean": observed,
        "ci_low": float(np.nanquantile(deltas, 0.025)),
        "ci_high": float(np.nanquantile(deltas, 0.975)),
    }


def write_report(
    calls: pd.DataFrame,
    unique_cells: pd.DataFrame,
    overall: pd.DataFrame,
    dataset_metrics: pd.DataFrame,
    ci: pd.DataFrame,
) -> None:
    call_summary = overall[overall["unit"] == "call"].set_index("score")
    unique_summary = overall[overall["unit"] == "unique_cell"].set_index("score")
    lines = [
        "# Incremental Audit Benchmark",
        "",
        "This analysis separates generic classifier uncertainty from NicheTypeR-specific",
        "conflict information. All trained audit models use leave-one-dataset-out",
        "prediction: the held-out dataset is never used to fit audit-risk weights.",
        "",
        "## Denominators",
        "",
        f"- Raw eligible model-call rows: {len(calls):,}",
        f"- Unique dataset-cell/spot units: {len(unique_cells):,}",
        f"- Source datasets: {calls['dataset_id'].nunique()}",
        "- Raw rows are not independent because the same cell or spot can appear under",
        "  multiple annotation models. Unique-cell summaries are therefore the primary",
        "  review-triage unit.",
        "",
        "## Overall Results",
        "",
        "| unit | score | n | wrong rate | AUROC | AUPRC | top 10% precision |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in overall.itertuples(index=False):
        lines.append(
            f"| {row.unit} | {row.score} | {row.n_units:,} | {row.wrong_rate:.3f} | "
            f"{row.auroc:.3f} | {row.auprc:.3f} | {row.top10_precision:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Dataset-Cluster Bootstrap Deltas",
            "",
            "| unit | metric | comparison | delta | 95% CI | datasets |",
            "|---|---|---|---:|---|---:|",
        ]
    )
    for row in ci.itertuples(index=False):
        lines.append(
            f"| {row.unit} | {row.metric} | {row.score_b} - {row.score_a} | "
            f"{row.delta_mean:.4f} | [{row.ci_low:.4f}, {row.ci_high:.4f}] | {row.n_datasets} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The baseline margin score remains a generic uncertainty baseline and should",
            "not be described as a NicheTypeR-specific contribution. The relevant",
            "increment is the cross-dataset improvement from adding non-margin conflict",
            "features to margin and confidence. If that delta is near zero or the",
            "dataset-cluster confidence interval overlaps zero, the manuscript should",
            "frame NicheTypeR's current empirical support as conservative triage and",
            "calibration rather than as a validated multi-evidence error detector.",
            "",
            "Available call tables do not contain separate numeric ligand-receptor,",
            "pathway/program or negative-marker residual features, so this benchmark",
            "cannot support independent five-evidence-layer claims. Those claims should",
            "either be removed from the main empirical contribution or backed by new",
            "layer-specific call tables.",
            "",
            "## Compact Takeaway",
            "",
            f"- Call-level margin AUROC: {call_summary.loc['margin', 'auroc']:.3f}",
            f"- Call-level augmented AUROC: {call_summary.loc['baseline_plus_conflicts', 'auroc']:.3f}",
            f"- Unique-cell margin AUROC: {unique_summary.loc['margin', 'auroc']:.3f}",
            f"- Unique-cell augmented AUROC: {unique_summary.loc['baseline_plus_conflicts', 'auroc']:.3f}",
        ]
    )
    (OUT_PREFIX.with_suffix(".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    calls = load_calls()
    calls["risk_baseline_logo"] = logo_predict(calls, BASE_FEATURES, "baseline")
    calls["risk_augmented_logo"] = logo_predict(calls, BASE_FEATURES + CONFLICT_FEATURES, "augmented")

    score_cols = {
        "margin": "risk_margin",
        "one_minus_confidence": "risk_confidence",
        "baseline_logo": "risk_baseline_logo",
        "baseline_plus_conflicts": "risk_augmented_logo",
        "nonmargin_conflict_flag": "flag_nonmargin_conflict",
    }
    call_overall, call_dataset = summarize(calls, score_cols, "call")
    unique_cells = aggregate_unique_cells(calls, score_cols)
    unique_overall, unique_dataset = summarize(unique_cells, score_cols, "unique_cell")

    overall = pd.concat([call_overall, unique_overall], ignore_index=True)
    dataset_metrics = pd.concat([call_dataset, unique_dataset], ignore_index=True)

    ci_rows = []
    for unit, sub in dataset_metrics.groupby("unit", sort=False):
        for metric in ["auroc", "auprc", "top10_precision"]:
            ci_rows.append(
                {
                    "unit": unit,
                    **bootstrap_dataset_ci(sub, "baseline_logo", "baseline_plus_conflicts", metric),
                }
            )
            ci_rows.append(
                {
                    "unit": unit,
                    **bootstrap_dataset_ci(sub, "margin", "baseline_plus_conflicts", metric),
                }
            )
    ci = pd.DataFrame(ci_rows)

    calls.to_csv(OUT_PREFIX.with_name(OUT_PREFIX.name + "_call_predictions.csv.gz"), index=False, compression="gzip")
    unique_cells.to_csv(OUT_PREFIX.with_name(OUT_PREFIX.name + "_unique_cell_predictions.csv.gz"), index=False, compression="gzip")
    overall.to_csv(OUT_PREFIX.with_name(OUT_PREFIX.name + "_summary.csv"), index=False)
    dataset_metrics.to_csv(OUT_PREFIX.with_name(OUT_PREFIX.name + "_by_dataset.csv"), index=False)
    ci.to_csv(OUT_PREFIX.with_name(OUT_PREFIX.name + "_dataset_cluster_ci.csv"), index=False)
    write_report(calls, unique_cells, overall, dataset_metrics, ci)
    print(overall.to_string(index=False))
    print()
    print(ci.to_string(index=False))


if __name__ == "__main__":
    main()
