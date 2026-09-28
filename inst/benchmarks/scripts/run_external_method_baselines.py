from __future__ import annotations

import importlib.util
import json
import shutil
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

from run_multidataset_blocked_benchmark import (
    SEED,
    dataset_configs,
    make_folds,
    metric_summary,
    paired_comparison,
    read_expression,
    read_metadata,
    softmax_rows,
    z_by_feature_train,
)


ROOT = Path(__file__).resolve().parent
OLD_CALLS = ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv"
SEURAT_CALLS = ROOT / "SEURAT_LABEL_TRANSFER_BASELINE_calls.csv"
SEURAT_SUMMARY = ROOT / "SEURAT_LABEL_TRANSFER_BASELINE_summary.csv"

CALLS_OUT = ROOT / "EXTERNAL_METHOD_BASELINES_proxy_calls.csv"
SUMMARY_OUT = ROOT / "EXTERNAL_METHOD_BASELINES_summary.csv"
PAIRWISE_OUT = ROOT / "EXTERNAL_METHOD_BASELINES_pairwise.csv"
STATUS_OUT = ROOT / "EXTERNAL_METHOD_BASELINES_status.csv"
REPORT_OUT = ROOT / "EXTERNAL_METHOD_BASELINES.md"
REPORT_JSON_OUT = ROOT / "EXTERNAL_METHOD_BASELINES_report.json"

MAX_FEATURES = 750
KNN_K = 15


def is_rna_config(config) -> bool:
    modality = str(config.modality).lower()
    if "proteomics" in modality or "protein" in modality or "mibi" in modality or "imc" in modality:
        return False
    return "rna" in modality or "transcript" in modality or "merfish" in modality or "merscope" in modality


def select_features(z: pd.DataFrame, train_cells: list[str], max_features: int = MAX_FEATURES) -> list[str]:
    train = z.loc[:, train_cells]
    variance = train.var(axis=1).replace([np.inf, -np.inf], np.nan).fillna(0)
    keep = variance.sort_values(ascending=False).head(min(max_features, len(variance))).index.astype(str).tolist()
    return keep


def rank_rows(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, axis=1, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    rows = np.arange(x.shape[0])[:, None]
    ranks[rows, order] = np.arange(x.shape[1], dtype=float)
    ranks -= ranks.mean(axis=1, keepdims=True)
    denom = np.linalg.norm(ranks, axis=1, keepdims=True)
    denom[~np.isfinite(denom) | (denom == 0)] = 1.0
    return ranks / denom


def calls_from_scores(
    scores: pd.DataFrame,
    truth: pd.Series,
    dataset_id: str,
    fold: int,
    model: str,
    elapsed_sec: float,
    n_features: int,
) -> pd.DataFrame:
    probs = softmax_rows(scores)
    labels = probs.idxmax(axis=1).astype(str)
    sorted_probs = np.sort(probs.to_numpy(dtype=float), axis=1)[:, ::-1]
    confidence = sorted_probs[:, 0]
    if sorted_probs.shape[1] > 1:
        margin = sorted_probs[:, 0] - sorted_probs[:, 1]
    else:
        margin = sorted_probs[:, 0]
    out = pd.DataFrame(
        {
            "cell_id": probs.index.astype(str),
            "label": labels.to_numpy(),
            "confidence": confidence,
            "margin": margin,
            "conflict_reason": np.where(margin < 0.08, "low_margin", "consistent"),
            "truth": truth.loc[probs.index].astype(str).to_numpy(),
            "dataset_id": dataset_id,
            "fold": fold,
            "model": model,
            "implementation": "algorithmic_proxy",
            "n_features": n_features,
            "elapsed_sec": elapsed_sec,
        }
    )
    out["correct"] = out["label"].astype(str).to_numpy() == out["truth"].astype(str).to_numpy()
    return out


def singler_style_spearman(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    labels: list[str],
) -> pd.DataFrame:
    """Blocked pseudo-bulk Spearman mapper inspired by SingleR."""
    profiles = []
    for label in labels:
        cells = y_train.index[y_train == label].tolist()
        profiles.append(x_train.loc[cells].mean(axis=0).to_numpy(dtype=float))
    profile_matrix = np.vstack(profiles)
    test_rank = rank_rows(x_test.to_numpy(dtype=float))
    profile_rank = rank_rows(profile_matrix)
    score = test_rank @ profile_rank.T
    score[~np.isfinite(score)] = 0.0
    return pd.DataFrame(score, index=x_test.index, columns=labels)


def scmap_style_knn(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    labels: list[str],
    k: int = KNN_K,
) -> pd.DataFrame:
    """Cosine nearest-neighbor label transfer inspired by scmap-cell."""
    n_neighbors = max(1, min(k, len(x_train)))
    model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine", algorithm="brute")
    model.fit(x_train.to_numpy(dtype=float))
    distances, indices = model.kneighbors(x_test.to_numpy(dtype=float))
    label_to_idx = {label: i for i, label in enumerate(labels)}
    score = np.zeros((len(x_test), len(labels)), dtype=float)
    train_labels = y_train.to_numpy(dtype=str)
    for i in range(len(x_test)):
        weights = 1.0 - distances[i]
        weights[~np.isfinite(weights)] = 0.0
        weights = np.clip(weights, 0.0, None)
        if weights.sum() == 0:
            weights = np.ones_like(weights)
        for weight, train_idx in zip(weights, indices[i]):
            score[i, label_to_idx[train_labels[train_idx]]] += float(weight)
    denom = score.sum(axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    score = score / denom
    return pd.DataFrame(score, index=x_test.index, columns=labels)


def celltypist_style_logistic(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    labels: list[str],
) -> pd.DataFrame:
    """Multinomial logistic reference mapper inspired by CellTypist."""
    encoder = LabelEncoder()
    y = encoder.fit_transform(y_train.to_numpy(dtype=str))
    classifier = LogisticRegression(
        max_iter=250,
        solver="lbfgs",
        class_weight="balanced",
        multi_class="auto",
    )
    classifier.fit(x_train.to_numpy(dtype=float), y)
    probabilities = classifier.predict_proba(x_test.to_numpy(dtype=float))
    score = np.zeros((len(x_test), len(labels)), dtype=float)
    for j, class_name in enumerate(encoder.classes_):
        if class_name in labels:
            score[:, labels.index(class_name)] = probabilities[:, j]
    return pd.DataFrame(score, index=x_test.index, columns=labels)


PROXY_MODELS = {
    "singler_style_spearman": singler_style_spearman,
    "scmap_style_knn": scmap_style_knn,
    "celltypist_style_logistic": celltypist_style_logistic,
}


def official_tool_status() -> list[dict]:
    rscript = shutil.which("Rscript")
    r_available = bool(rscript)
    return [
        {
            "tool": "Seurat label transfer",
            "official_status": "completed" if SEURAT_CALLS.exists() else "not_completed",
            "local_requirement": "R/Seurat",
            "proxy_model": "",
            "note": "Existing blocked Seurat label-transfer results are used as the official anchor-transfer baseline.",
        },
        {
            "tool": "SingleR",
            "official_status": "not_run",
            "local_requirement": "R/Bioconductor SingleR",
            "proxy_model": "singler_style_spearman",
            "note": "Rscript unavailable in this workspace." if not r_available else "SingleR package was not invoked by this script.",
        },
        {
            "tool": "scmap",
            "official_status": "not_run",
            "local_requirement": "R/Bioconductor scmap",
            "proxy_model": "scmap_style_knn",
            "note": "Rscript unavailable in this workspace." if not r_available else "scmap package was not invoked by this script.",
        },
        {
            "tool": "CellTypist",
            "official_status": "not_run",
            "local_requirement": "Python celltypist package and model download",
            "proxy_model": "celltypist_style_logistic",
            "note": "celltypist is not installed locally." if importlib.util.find_spec("celltypist") is None else "celltypist package was not invoked by this script.",
        },
        {
            "tool": "Azimuth",
            "official_status": "not_run",
            "local_requirement": "R/Seurat Azimuth plus compatible reference maps",
            "proxy_model": "seurat_label_transfer",
            "note": "Treated as an anchor-mapping family comparison through the completed Seurat label-transfer baseline.",
        },
    ]


def evaluate_proxies() -> tuple[pd.DataFrame, pd.DataFrame]:
    all_calls = []
    status_rows = []
    for config in dataset_configs():
        if not is_rna_config(config):
            status_rows.append(
                {
                    "dataset_id": config.dataset_id,
                    "model": "all_proxy_models",
                    "status": "skipped",
                    "reason": f"non-RNA modality: {config.modality}",
                }
            )
            continue
        if not config.expression_path.exists() or not config.metadata_path.exists():
            status_rows.append(
                {
                    "dataset_id": config.dataset_id,
                    "model": "all_proxy_models",
                    "status": "skipped",
                    "reason": "missing expression or metadata file",
                }
            )
            continue

        print(f"\n=== {config.dataset_id} external proxy baselines ===")
        expr = read_expression(config.expression_path)
        metadata = read_metadata(config, list(expr.columns))
        truth = metadata.set_index("cell_id")["label"].astype(str)
        groups = metadata.set_index("cell_id")["fov_group"].astype(str)
        folds = make_folds(truth, groups, config.max_folds, SEED)

        for fold_id, (train_idx, test_idx) in enumerate(folds, start=1):
            train_cells = truth.index[train_idx].astype(str).tolist()
            test_cells = truth.index[test_idx].astype(str).tolist()
            y_train = truth.loc[train_cells].astype(str)
            labels = sorted(y_train.unique().tolist())
            if len(labels) < 2 or len(test_cells) < 5:
                status_rows.append(
                    {
                        "dataset_id": config.dataset_id,
                        "fold": fold_id,
                        "model": "all_proxy_models",
                        "status": "skipped",
                        "reason": "too few labels or test cells",
                    }
                )
                continue

            z = z_by_feature_train(expr, train_cells)
            features = select_features(z, train_cells)
            x_train = z.loc[features, train_cells].T.astype(float)
            x_test = z.loc[features, test_cells].T.astype(float)
            print(f"fold {fold_id}: train={len(train_cells)} test={len(test_cells)} features={len(features)}")

            for model_name, fn in PROXY_MODELS.items():
                start = time.perf_counter()
                try:
                    scores = fn(x_train, y_train, x_test, labels)
                    elapsed = time.perf_counter() - start
                    calls = calls_from_scores(
                        scores=scores,
                        truth=truth,
                        dataset_id=config.dataset_id,
                        fold=fold_id,
                        model=model_name,
                        elapsed_sec=elapsed,
                        n_features=len(features),
                    )
                    all_calls.append(calls)
                    status_rows.append(
                        {
                            "dataset_id": config.dataset_id,
                            "fold": fold_id,
                            "model": model_name,
                            "status": "completed",
                            "reason": f"n={len(calls)}; elapsed={elapsed:.2f} sec",
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - report per-fold failures without stopping other baselines.
                    status_rows.append(
                        {
                            "dataset_id": config.dataset_id,
                            "fold": fold_id,
                            "model": model_name,
                            "status": "failed",
                            "reason": str(exc),
                        }
                    )
                    print(f"{model_name} failed on {config.dataset_id} fold {fold_id}: {exc}")

    calls = pd.concat(all_calls, ignore_index=True, sort=False) if all_calls else pd.DataFrame()
    status = pd.DataFrame(status_rows)
    return calls, status


def summarize(calls: pd.DataFrame, old_calls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    if SEURAT_SUMMARY.exists():
        seurat_summary = pd.read_csv(SEURAT_SUMMARY)
        seurat_summary["implementation"] = "official_package"
        summary_rows.extend(json.loads(seurat_summary.to_json(orient="records")))

    for (dataset_id, model), df in calls.groupby(["dataset_id", "model"], sort=False):
        truth = df.set_index("cell_id")["truth"].astype(str)
        summary, _ = metric_summary(
            df[["cell_id", "label", "confidence", "margin", "conflict_reason"]],
            truth,
        )
        summary_rows.append(
            {
                "dataset_id": dataset_id,
                "model": model,
                "implementation": "algorithmic_proxy",
                **summary,
                "mean_elapsed_sec_per_fold": float(df.groupby("fold")["elapsed_sec"].first().mean()),
                "mean_n_features": float(df["n_features"].mean()),
            }
        )

    summary = pd.DataFrame(summary_rows)
    combined = pd.concat(
        [
            old_calls[old_calls["model"] == "marker_only"],
            calls,
            pd.read_csv(SEURAT_CALLS) if SEURAT_CALLS.exists() else pd.DataFrame(),
        ],
        ignore_index=True,
        sort=False,
    )
    pair_rows = []
    for dataset_id in sorted(calls["dataset_id"].dropna().unique().tolist()):
        for comparator in sorted(calls["model"].dropna().unique().tolist()):
            sub = combined[(combined["dataset_id"] == dataset_id) & (combined["model"].isin(["marker_only", comparator]))]
            if sub["model"].nunique() == 2:
                pair_rows.append(paired_comparison(combined, dataset_id, "marker_only", comparator))
        if SEURAT_CALLS.exists() and "seurat_label_transfer" in set(combined.loc[combined["dataset_id"] == dataset_id, "model"]):
            pair_rows.append(paired_comparison(combined, dataset_id, "marker_only", "seurat_label_transfer"))
    pairwise = pd.DataFrame(pair_rows).drop_duplicates(["dataset_id", "baseline_model", "comparator_model"])
    return summary, pairwise


def write_report(summary: pd.DataFrame, pairwise: pd.DataFrame, status: pd.DataFrame) -> None:
    lines = [
        "# External Annotation Method Baselines",
        "",
        "This benchmark extends the Seurat label-transfer baseline with blocked",
        "algorithmic proxy mappers that mimic common external annotation families.",
        "The proxy models are included to test NicheTypeR's audit interface and",
        "error triage under diverse external label sources. They are not claimed to",
        "be official SingleR, scmap or CellTypist package runs.",
        "",
        "## Official tool status",
        "",
        "| tool | official status | local requirement | proxy used | note |",
        "|---|---|---|---|---|",
    ]
    for row in official_tool_status():
        lines.append(
            f"| {row['tool']} | {row['official_status']} | {row['local_requirement']} | "
            f"{row['proxy_model']} | {row['note']} |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| dataset | model | implementation | accuracy | macro-F1 | conflict rate |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in summary.sort_values(["dataset_id", "implementation", "model"]).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.model} | {row.implementation} | "
            f"{row.accuracy:.4f} | {row.macro_f1:.4f} | {row.conflict_rate:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Paired comparisons against marker-only",
            "",
            "| dataset | comparator | accuracy diff | marker wrong, comparator right | marker right, comparator wrong | McNemar p |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in pairwise.sort_values(["dataset_id", "comparator_model"]).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.comparator_model} | {row.accuracy_diff:+.4f} | "
            f"{row.baseline_wrong_comparator_right} | {row.baseline_right_comparator_wrong} | "
            f"{row.mcnemar_exact_p:.4g} |"
        )

    completed = status[status["status"] == "completed"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The proxy benchmark completed {len(completed)} dataset-fold-model tasks.",
            "Together with the completed Seurat label-transfer run, this reduces the",
            "risk that NicheTypeR is only demonstrated on one handcrafted reference",
            "source. The remaining limitation is explicit: official SingleR, scmap,",
            "CellTypist and Azimuth package runs require their native packages and",
            "reference assets, which were not available in this local workspace.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    old_calls = pd.read_csv(OLD_CALLS, dtype={"cell_id": str}, low_memory=False)
    calls, status = evaluate_proxies()
    if calls.empty:
        raise RuntimeError("No external proxy calls were generated.")
    summary, pairwise = summarize(calls, old_calls)
    calls.to_csv(CALLS_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    status.to_csv(STATUS_OUT, index=False)
    write_report(summary, pairwise, status)
    REPORT_JSON_OUT.write_text(
        json.dumps(
            {
                "official_tool_status": official_tool_status(),
                "summary": json.loads(summary.to_json(orient="records")),
                "pairwise": json.loads(pairwise.to_json(orient="records")),
                "status": json.loads(status.to_json(orient="records")),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(summary.sort_values(["dataset_id", "model"]).to_string(index=False))
    print(f"\nWrote {len(calls):,} proxy calls.")


if __name__ == "__main__":
    main()
