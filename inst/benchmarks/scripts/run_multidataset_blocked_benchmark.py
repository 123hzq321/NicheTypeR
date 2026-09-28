from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parent
SEED = 20260725


@dataclass(frozen=True)
class BenchmarkDataset:
    dataset_id: str
    expression_path: Path
    metadata_path: Path
    label_col: str
    group_col: str
    cell_id_col: str = "cell_id"
    x_col: str = "x"
    y_col: str = "y"
    role: str = "benchmark"
    modality: str = "unknown"
    max_folds: int = 5
    top_markers_per_label: int = 20


def dataset_configs() -> list[BenchmarkDataset]:
    configs = [
        BenchmarkDataset(
            dataset_id="GSE202623_LESION",
            expression_path=ROOT / "GSE202623" / "GSE202623_lesion_preview_expression.tsv.gz",
            metadata_path=ROOT / "GSE202623" / "GSE202623_lesion_preview_metadata.tsv",
            label_col="cell.type_manual",
            group_col="fov_group",
            cell_id_col="cellID",
            x_col="center_x",
            y_col="center_y",
            role="primary_disease_benchmark",
            modality="MERFISH_RNA_single_cell",
        )
    ]

    registry_path = ROOT / "DATASET_REGISTRY.csv"
    if registry_path.exists():
        registry = pd.read_csv(registry_path)
        for row in registry.itertuples(index=False):
            dataset_id = str(row.dataset_id)
            configs.append(
                BenchmarkDataset(
                    dataset_id=dataset_id,
                    expression_path=ROOT / dataset_id / f"{dataset_id}_preview_expression.tsv.gz",
                    metadata_path=ROOT / dataset_id / f"{dataset_id}_preview_metadata.tsv",
                    label_col="label",
                    group_col="fov_group",
                    role=str(row.role),
                    modality=str(row.modality),
                )
            )
    geo_registry_path = ROOT / "GEO_DIRECT_DATASETS.csv"
    if geo_registry_path.exists():
        geo_registry = pd.read_csv(geo_registry_path)
        geo_registry = geo_registry[geo_registry["status"] == "benchmark_ready"]
        for row in geo_registry.itertuples(index=False):
            dataset_id = str(row.dataset_id)
            configs.append(
                BenchmarkDataset(
                    dataset_id=dataset_id,
                    expression_path=ROOT / dataset_id / f"{dataset_id}_preview_expression.tsv.gz",
                    metadata_path=ROOT / dataset_id / f"{dataset_id}_preview_metadata.tsv",
                    label_col="label",
                    group_col="fov_group",
                    role="geo_direct_benchmark",
                    modality="GEO_direct_spatial_transcriptomics",
                )
            )
    return configs


def read_expression(path: Path) -> pd.DataFrame:
    expr = pd.read_csv(path, sep="\t", index_col=0)
    expr.index = expr.index.astype(str)
    expr.columns = expr.columns.astype(str)
    return expr


def read_metadata(config: BenchmarkDataset, expr_cells: list[str]) -> pd.DataFrame:
    meta = pd.read_csv(config.metadata_path, sep="\t", dtype=str)
    if config.cell_id_col not in meta.columns:
        raise ValueError(f"{config.dataset_id}: missing cell ID column {config.cell_id_col}")
    for col in [config.label_col, config.group_col, config.x_col, config.y_col]:
        if col not in meta.columns:
            raise ValueError(f"{config.dataset_id}: missing metadata column {col}")
    meta = meta.copy()
    meta["cell_id"] = meta[config.cell_id_col].astype(str)
    meta["label"] = meta[config.label_col].astype(str)
    meta["fov_group"] = meta[config.group_col].astype(str)
    meta["x"] = meta[config.x_col].astype(float)
    meta["y"] = meta[config.y_col].astype(float)
    meta = meta.set_index("cell_id", drop=False).loc[expr_cells].reset_index(drop=True)
    return meta


def z_by_feature_train(expr: pd.DataFrame, train_cells: list[str], cap: float = 3.0) -> pd.DataFrame:
    train_values = expr.loc[:, train_cells].to_numpy(dtype=float)
    all_values = expr.to_numpy(dtype=float)
    mu = np.nanmean(train_values, axis=1, keepdims=True)
    sd = np.nanstd(train_values, axis=1, ddof=1, keepdims=True)
    sd[~np.isfinite(sd) | (sd == 0)] = 1
    z = (all_values - mu) / sd
    z = np.clip(z, -cap, cap)
    return pd.DataFrame(z, index=expr.index, columns=expr.columns)


def weighted_mean_rows(values: np.ndarray, weights: np.ndarray | None = None) -> np.ndarray:
    if values.shape[0] == 0:
        return np.zeros(values.shape[1])
    if weights is None:
        return np.nanmean(values, axis=0)
    weights = np.asarray(weights, dtype=float)
    weights[~np.isfinite(weights)] = 0
    denom = np.sum(np.abs(weights))
    if denom == 0:
        return np.zeros(values.shape[1])
    return np.asarray(weights @ values / denom).ravel()


def learn_marker_scores(
    z: pd.DataFrame,
    labels: pd.Series,
    train_cells: list[str],
    top_n: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = labels.astype(str)
    candidate_labels = sorted(labels.loc[train_cells].unique())
    z_train = z.loc[:, train_cells]
    scores = pd.DataFrame(0.0, index=z.columns, columns=candidate_labels)
    marker_rows = []

    for label in candidate_labels:
        in_cells = labels.loc[train_cells][labels.loc[train_cells] == label].index.tolist()
        out_cells = labels.loc[train_cells][labels.loc[train_cells] != label].index.tolist()
        if len(in_cells) < 2 or len(out_cells) < 2:
            continue
        mean_in = z_train.loc[:, in_cells].mean(axis=1)
        mean_out = z_train.loc[:, out_cells].mean(axis=1)
        effect = (mean_in - mean_out).replace([np.inf, -np.inf], np.nan).fillna(0)
        pos = effect[effect > 0].sort_values(ascending=False).head(top_n)
        neg = effect[effect < 0].sort_values(ascending=True).head(top_n)

        pos_score = np.zeros(z.shape[1])
        neg_score = np.zeros(z.shape[1])
        if len(pos) > 0:
            pos_score = weighted_mean_rows(z.loc[pos.index].to_numpy(), np.abs(pos.to_numpy()))
            for feature, weight in pos.items():
                marker_rows.append({
                    "cell_type": label,
                    "feature": feature,
                    "direction": "positive",
                    "weight": float(abs(weight)),
                })
        if len(neg) > 0:
            neg_score = weighted_mean_rows(z.loc[neg.index].to_numpy(), np.abs(neg.to_numpy()))
            for feature, weight in neg.items():
                marker_rows.append({
                    "cell_type": label,
                    "feature": feature,
                    "direction": "negative",
                    "weight": float(abs(weight)),
                })
        scores[label] = pos_score - neg_score

    return scores, pd.DataFrame(marker_rows)


def learn_reference_profile_scores(
    z: pd.DataFrame,
    labels: pd.Series,
    train_cells: list[str],
    candidate_labels: list[str],
) -> pd.DataFrame:
    """Score cells by cosine similarity to train-block label centroids.

    This is a lightweight reference-profile baseline in the same broad family
    as atlas label-transfer methods. It is intentionally dependency-free and is
    used as a reviewer-facing comparator, not as a claim that NicheTypeR
    reimplements SingleR, Seurat label transfer, CellTypist or scmap.
    """
    labels = labels.astype(str)
    profiles = []
    for label in candidate_labels:
        label_cells = labels.loc[train_cells][labels.loc[train_cells] == label].index.tolist()
        if len(label_cells) == 0:
            profiles.append(np.zeros(z.shape[0]))
        else:
            profiles.append(z.loc[:, label_cells].mean(axis=1).to_numpy(dtype=float))
    profile_matrix = np.vstack(profiles)
    cell_matrix = z.T.to_numpy(dtype=float)

    profile_norm = np.linalg.norm(profile_matrix, axis=1, keepdims=True)
    profile_norm[~np.isfinite(profile_norm) | (profile_norm == 0)] = 1
    cell_norm = np.linalg.norm(cell_matrix, axis=1, keepdims=True)
    cell_norm[~np.isfinite(cell_norm) | (cell_norm == 0)] = 1

    scores = (cell_matrix / cell_norm) @ (profile_matrix / profile_norm).T
    scores[~np.isfinite(scores)] = 0
    return pd.DataFrame(scores, index=z.columns, columns=candidate_labels)


def build_edges(metadata: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    rows = []
    for group, group_df in metadata.groupby("fov_group", sort=False):
        if len(group_df) < 2:
            continue
        n_neighbors = min(k + 1, len(group_df))
        coords = group_df[["x", "y"]].to_numpy(dtype=float)
        model = NearestNeighbors(n_neighbors=n_neighbors)
        model.fit(coords)
        distances, indices = model.kneighbors(coords)
        cells = group_df["cell_id"].to_numpy(dtype=str)
        for i, source in enumerate(cells):
            for distance, j in zip(distances[i, 1:], indices[i, 1:]):
                rows.append((source, cells[j], float(distance), str(group)))
    return pd.DataFrame(rows, columns=["from", "to", "distance", "fov_group"])


def random_edges_like(edges: pd.DataFrame, metadata: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cells_by_group = metadata.groupby("fov_group")["cell_id"].apply(list).to_dict()
    group_by_cell = metadata.set_index("cell_id")["fov_group"].to_dict()
    degree = edges.groupby("from").size().to_dict()
    rows = []
    for source, n_edges in degree.items():
        group = group_by_cell[source]
        candidates = [cell for cell in cells_by_group[group] if cell != source]
        if not candidates:
            continue
        replace = len(candidates) < n_edges
        targets = rng.choice(candidates, size=n_edges, replace=replace)
        for target in targets:
            rows.append((source, str(target), np.nan, str(group)))
    return pd.DataFrame(rows, columns=["from", "to", "distance", "fov_group"])


def softmax_rows(score: pd.DataFrame, temperature: float = 1.0) -> pd.DataFrame:
    x = score.to_numpy(dtype=float) / max(float(temperature), np.finfo(float).eps)
    x = x - np.nanmax(x, axis=1, keepdims=True)
    ex = np.exp(x)
    denom = np.nansum(ex, axis=1, keepdims=True)
    denom[~np.isfinite(denom) | (denom == 0)] = 1
    return pd.DataFrame(ex / denom, index=score.index, columns=score.columns)


def robust_standardize(score: pd.DataFrame) -> pd.DataFrame:
    out = score.copy().astype(float)
    for col in out.columns:
        vals = out[col].to_numpy(dtype=float)
        med = np.nanmedian(vals)
        mad = np.nanmedian(np.abs(vals - med)) * 1.4826
        if not np.isfinite(mad) or mad == 0:
            mad = np.nanstd(vals)
        if not np.isfinite(mad) or mad == 0:
            mad = 1
        out[col] = (vals - med) / mad
    return out.replace([np.inf, -np.inf], 0).fillna(0)


def align_scores(scores: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cells = sorted(set.intersection(*(set(score.index) for score in scores.values())))
    labels = sorted(set.intersection(*(set(score.columns) for score in scores.values())))
    if not cells or not labels:
        raise ValueError("Score matrices do not share cells and labels")
    return {name: score.loc[cells, labels] for name, score in scores.items()}


def infer(scores: dict[str, pd.DataFrame], weights: dict[str, float]) -> dict:
    scores = align_scores(scores)
    standardized = {name: robust_standardize(score) for name, score in scores.items()}
    names = list(standardized)
    fused = pd.DataFrame(0.0, index=standardized[names[0]].index, columns=standardized[names[0]].columns)
    denom = 0.0
    for name, score in standardized.items():
        w = float(weights.get(name, 1.0))
        fused += score * w
        denom += abs(w)
    if denom > 0:
        fused /= denom
    probs = softmax_rows(fused)
    labels = probs.idxmax(axis=1)
    sorted_probs = np.sort(probs.to_numpy(), axis=1)[:, ::-1]
    confidence = sorted_probs[:, 0]
    margin = sorted_probs[:, 0] - sorted_probs[:, 1] if probs.shape[1] > 1 else sorted_probs[:, 0]

    component_prob = {name: softmax_rows(score) for name, score in standardized.items()}
    component_best = {name: prob.idxmax(axis=1) for name, prob in component_prob.items()}
    component_margin = {}
    for name, prob in component_prob.items():
        sorted_component = np.sort(prob.to_numpy(), axis=1)[:, ::-1]
        component_margin[name] = pd.Series(
            sorted_component[:, 0] - sorted_component[:, 1],
            index=prob.index,
        )

    reasons = []
    for cell in probs.index:
        conflicts = [
            name
            for name, best in component_best.items()
            if best.loc[cell] != labels.loc[cell] and component_margin[name].loc[cell] >= 0.05
        ]
        reason = "consistent" if not conflicts else ";".join(f"{name}_conflict" for name in conflicts)
        if margin[probs.index.get_loc(cell)] < 0.08:
            reason = reason + ";low_margin" if reason else "low_margin"
        reasons.append(reason)

    calls = pd.DataFrame({
        "cell_id": probs.index,
        "label": labels.to_numpy(),
        "confidence": confidence,
        "margin": margin,
        "conflict_reason": reasons,
    })
    return {"scores": fused, "probabilities": probs, "calls": calls, "components": standardized, "weights": weights}


def score_spatial_smoothing(edges: pd.DataFrame, prior: pd.DataFrame, alpha: float = 0.5) -> pd.DataFrame:
    probs = softmax_rows(prior)
    neighbor_probs = probs.copy()
    neighbor_probs.loc[:, :] = 0.0
    by_from = edges.groupby("from")["to"].apply(list).to_dict()
    for cell, neigh in by_from.items():
        if cell not in neighbor_probs.index:
            continue
        neigh = [n for n in neigh if n in probs.index]
        if neigh:
            neighbor_probs.loc[cell] = probs.loc[neigh].mean(axis=0).to_numpy()
    missing = neighbor_probs.sum(axis=1) == 0
    neighbor_probs.loc[missing] = probs.loc[missing]
    smoothed = (1.0 - alpha) * probs + alpha * neighbor_probs
    smoothed = smoothed.div(smoothed.sum(axis=1).replace(0, 1), axis=0)
    return np.log(smoothed.clip(lower=np.finfo(float).eps))


def learn_niche_prior(
    edges: pd.DataFrame,
    labels: pd.Series,
    train_cells: list[str],
    candidate_labels: list[str],
    pseudocount: float = 1.0,
    clip: float = 3.0,
) -> pd.DataFrame:
    train_set = set(train_cells)
    train_edges = edges[edges["from"].isin(train_set) & edges["to"].isin(train_set)].copy()
    counts = pd.DataFrame(pseudocount, index=candidate_labels, columns=candidate_labels)
    if not train_edges.empty:
        labels = labels.astype(str)
        for row in train_edges.itertuples(index=False):
            a = labels.get(row[0], None)
            b = labels.get(row[1], None)
            if a in counts.index and b in counts.columns:
                counts.loc[a, b] += 1
    conditional = counts.div(counts.sum(axis=1), axis=0)
    background = counts.sum(axis=0) / counts.values.sum()
    weights = np.log(conditional.div(background, axis=1))
    weights = weights.clip(lower=-clip, upper=clip)
    return weights


def permute_niche_prior(weights: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    labels = list(weights.index)
    permuted = labels.copy()
    rng.shuffle(permuted)
    out = weights.copy()
    out.index = permuted
    out = out.loc[labels]
    out.columns = permuted
    out = out.loc[:, labels]
    return out


def score_neighborhood(edges: pd.DataFrame, prior: pd.DataFrame, niche_weights: pd.DataFrame) -> pd.DataFrame:
    labels = list(prior.columns)
    probs = softmax_rows(prior)
    compat = niche_weights.reindex(index=labels, columns=labels).fillna(0)
    out = pd.DataFrame(0.0, index=prior.index, columns=labels)
    by_from = edges.groupby("from")["to"].apply(list).to_dict()
    for cell, neigh in by_from.items():
        if cell not in out.index:
            continue
        neigh = [n for n in neigh if n in probs.index]
        if not neigh:
            continue
        neighbor_mix = probs.loc[neigh].mean(axis=0).to_numpy()
        out.loc[cell] = compat.to_numpy() @ neighbor_mix
    return out


def score_context_specific_neighborhood(
    edges: pd.DataFrame,
    prior: pd.DataFrame,
    niche_weights: pd.DataFrame,
    null_edges: list[pd.DataFrame] | None = None,
    null_weights: list[pd.DataFrame] | None = None,
    statistic: str = "residual",
    min_null_sd: float = 1e-6,
) -> pd.DataFrame:
    observed = score_neighborhood(edges, prior, niche_weights)
    null_scores = []
    for edge_null in null_edges or []:
        null_scores.append(score_neighborhood(edge_null, prior, niche_weights))
    for weight_null in null_weights or []:
        null_scores.append(score_neighborhood(edges, prior, weight_null))
    if not null_scores:
        raise ValueError("At least one null graph or null niche prior is required")
    null_values = np.stack([score.loc[observed.index, observed.columns].to_numpy(dtype=float) for score in null_scores], axis=2)
    null_mean = np.nanmean(null_values, axis=2)
    residual = observed.to_numpy(dtype=float) - null_mean
    if statistic == "z":
        null_sd = np.nanstd(null_values, axis=2, ddof=1)
        null_sd[~np.isfinite(null_sd) | (null_sd < min_null_sd)] = min_null_sd
        residual = residual / null_sd
    return pd.DataFrame(residual, index=observed.index, columns=observed.columns)


def make_folds(labels: pd.Series, groups: pd.Series, max_folds: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    n_groups = groups.nunique()
    n_splits = max(2, min(max_folds, int(n_groups)))
    if n_splits < 2:
        raise ValueError("Need at least two spatial groups for blocked validation")
    y = labels.to_numpy()
    x = np.zeros(len(labels))
    g = groups.to_numpy()
    try:
        splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return list(splitter.split(x, y, g))
    except ValueError:
        splitter = GroupKFold(n_splits=n_splits)
        return list(splitter.split(x, y, g))


def metric_summary(calls: pd.DataFrame, truth: pd.Series) -> tuple[dict, pd.DataFrame]:
    truth = truth.loc[calls["cell_id"]].astype(str)
    pred = calls["label"].astype(str).to_numpy()
    truth_vec = truth.to_numpy()
    labels = sorted(set(truth_vec) | set(pred))
    per_label_rows = []
    for label in labels:
        tp = int(np.sum((pred == label) & (truth_vec == label)))
        fp = int(np.sum((pred == label) & (truth_vec != label)))
        fn = int(np.sum((pred != label) & (truth_vec == label)))
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        per_label_rows.append({
            "label": label,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": int(np.sum(truth_vec == label)),
        })
    per_label = pd.DataFrame(per_label_rows)
    summary = {
        "n": len(calls),
        "accuracy": float(np.mean(pred == truth_vec)),
        "macro_f1": float(per_label["f1"].mean()),
        "mean_confidence": float(calls["confidence"].mean()),
        "mean_margin": float(calls["margin"].mean()),
        "conflict_rate": float((calls["conflict_reason"] != "consistent").mean()),
    }
    return summary, per_label


def model_grid(score_names: list[str]) -> pd.DataFrame:
    grids = {}
    for name in score_names:
        if len(score_names) == 1:
            grids[name] = [1.0]
        elif name in {"marker", "reference"}:
            grids[name] = [1.5]
        else:
            grids[name] = [0.0, 0.05, 0.1, 0.2, 0.5, 1.0]
    return pd.MultiIndex.from_product(grids.values(), names=grids.keys()).to_frame(index=False)


def subset_scores(scores: dict[str, pd.DataFrame], cells: list[str]) -> dict[str, pd.DataFrame]:
    return {name: score.loc[cells] for name, score in scores.items()}


def fit_best_weights(scores: dict[str, pd.DataFrame], truth: pd.Series, train_cells: list[str]) -> tuple[dict[str, float], pd.DataFrame]:
    grid = model_grid(list(scores))
    rows = []
    train_scores = subset_scores(scores, train_cells)
    for i, row in grid.iterrows():
        weights = {name: float(row[name]) for name in scores}
        fit = infer(train_scores, weights)
        summary, _ = metric_summary(fit["calls"], truth)
        rows.append({
            "model_id": int(i),
            **weights,
            "train_accuracy": summary["accuracy"],
            "train_macro_f1": summary["macro_f1"],
        })
    tuning = pd.DataFrame(rows).sort_values(["train_macro_f1", "train_accuracy"], ascending=False).reset_index(drop=True)
    best = tuning.iloc[0]
    weights = {name: float(best[name]) for name in scores}
    return weights, tuning


def predict_model(
    dataset_id: str,
    fold: int,
    model_name: str,
    scores: dict[str, pd.DataFrame],
    truth: pd.Series,
    train_cells: list[str],
    test_cells: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    weights, tuning = fit_best_weights(scores, truth.loc[train_cells], train_cells)
    fit = infer(subset_scores(scores, test_cells), weights)
    calls = fit["calls"].copy()
    calls["truth"] = truth.loc[calls["cell_id"]].to_numpy()
    calls["correct"] = calls["label"].to_numpy() == calls["truth"].to_numpy()
    calls["dataset_id"] = dataset_id
    calls["fold"] = fold
    calls["model"] = model_name
    for key, value in weights.items():
        calls[f"w_{key}"] = value
    tuning.insert(0, "model", model_name)
    tuning.insert(0, "fold", fold)
    tuning.insert(0, "dataset_id", dataset_id)
    return calls, tuning


def paired_comparison(calls: pd.DataFrame, dataset_id: str, baseline_model: str, comparator_model: str) -> dict:
    a = calls[(calls["dataset_id"] == dataset_id) & (calls["model"] == baseline_model)].set_index("cell_id").sort_index()
    b = calls[(calls["dataset_id"] == dataset_id) & (calls["model"] == comparator_model)].set_index("cell_id").loc[a.index]
    a_correct = a["correct"].to_numpy(dtype=bool)
    b_correct = b["correct"].to_numpy(dtype=bool)
    a_wrong_b_right = int(np.sum(~a_correct & b_correct))
    a_right_b_wrong = int(np.sum(a_correct & ~b_correct))
    discordant = a_wrong_b_right + a_right_b_wrong
    p_value = 1.0 if discordant == 0 else float(binomtest(min(a_wrong_b_right, a_right_b_wrong), discordant, 0.5).pvalue)
    return {
        "dataset_id": dataset_id,
        "baseline_model": baseline_model,
        "comparator_model": comparator_model,
        "baseline_wrong_comparator_right": a_wrong_b_right,
        "baseline_right_comparator_wrong": a_right_b_wrong,
        "mcnemar_exact_p": p_value,
        "accuracy_diff": float(b["correct"].mean() - a["correct"].mean()),
    }


def evaluate_dataset(config: BenchmarkDataset, seed: int = SEED) -> dict:
    print(f"\n=== {config.dataset_id} ===")
    expr = read_expression(config.expression_path)
    metadata = read_metadata(config, list(expr.columns))
    truth = metadata.set_index("cell_id")["label"].astype(str)
    groups = metadata.set_index("cell_id")["fov_group"].astype(str)
    edges = build_edges(metadata, k=10)
    folds = make_folds(truth, groups, config.max_folds, seed)

    all_calls = []
    all_tuning = []
    all_markers = []
    fold_reports = []

    for fold_id, (train_idx, test_idx) in enumerate(folds, start=1):
        train_cells = truth.index[train_idx].tolist()
        test_cells = truth.index[test_idx].tolist()
        print(f"fold {fold_id}: train={len(train_cells)} test={len(test_cells)}")

        z = z_by_feature_train(expr, train_cells)
        marker, marker_db = learn_marker_scores(
            z,
            truth,
            train_cells,
            top_n=config.top_markers_per_label,
        )
        marker_db.insert(0, "fold", fold_id)
        marker_db.insert(0, "dataset_id", config.dataset_id)
        all_markers.append(marker_db)

        reference = learn_reference_profile_scores(
            z,
            truth,
            train_cells,
            candidate_labels=list(marker.columns),
        )

        smoothing = score_spatial_smoothing(edges, marker, alpha=0.5)
        random_edges = random_edges_like(edges, metadata, seed + fold_id)
        smoothing_random = score_spatial_smoothing(random_edges, marker, alpha=0.5)
        niche_weights = learn_niche_prior(edges, truth, train_cells, list(marker.columns))
        learned = score_neighborhood(edges, marker, niche_weights)
        reference_learned = score_neighborhood(edges, reference, niche_weights)
        learned_random = score_neighborhood(random_edges, marker, niche_weights)
        permuted_weights = permute_niche_prior(niche_weights, seed + 100 + fold_id)
        learned_permuted = score_neighborhood(edges, marker, permuted_weights)
        context_specific = score_context_specific_neighborhood(
            edges=edges,
            prior=marker,
            niche_weights=niche_weights,
            null_edges=[random_edges],
            null_weights=[permuted_weights],
            statistic="residual",
        )

        model_scores = {
            "marker_only": {"marker": marker},
            "reference_profile": {"reference": reference},
            "marker_reference_profile": {
                "marker": marker,
                "reference": reference,
            },
            "marker_spatial_smoothing": {
                "marker": marker,
                "spatial_smoothing": smoothing,
            },
            "marker_spatial_smoothing_random_graph": {
                "marker": marker,
                "spatial_smoothing": smoothing_random,
            },
            "marker_learned_neighborhood": {
                "marker": marker,
                "learned_neighborhood": learned,
            },
            "reference_profile_learned_neighborhood": {
                "reference": reference,
                "learned_neighborhood": reference_learned,
            },
            "marker_context_specific_neighborhood": {
                "marker": marker,
                "context_specific": context_specific,
            },
            "learned_random_graph": {
                "marker": marker,
                "learned_neighborhood": learned_random,
            },
            "learned_permuted_prior": {
                "marker": marker,
                "learned_neighborhood": learned_permuted,
            },
        }

        for model_name, scores in model_scores.items():
            calls, tuning = predict_model(
                config.dataset_id,
                fold_id,
                model_name,
                scores,
                truth,
                train_cells,
                test_cells,
            )
            all_calls.append(calls)
            all_tuning.append(tuning)

        fold_reports.append({
            "dataset_id": config.dataset_id,
            "fold": fold_id,
            "train_cells": len(train_cells),
            "test_cells": len(test_cells),
            "train_groups": int(groups.loc[train_cells].nunique()),
            "test_groups": int(groups.loc[test_cells].nunique()),
            "test_label_counts": truth.loc[test_cells].value_counts().to_dict(),
        })

    calls = pd.concat(all_calls, ignore_index=True)
    tuning = pd.concat(all_tuning, ignore_index=True)
    markers = pd.concat(all_markers, ignore_index=True)
    return {
        "config": asdict(config) | {
            "expression_path": str(config.expression_path),
            "metadata_path": str(config.metadata_path),
        },
        "calls": calls,
        "tuning": tuning,
        "markers": markers,
        "fold_reports": fold_reports,
    }


def summarize_all(calls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    per_label_rows = []
    pair_rows = []
    for (dataset_id, model), df in calls.groupby(["dataset_id", "model"], sort=False):
        truth = df.set_index("cell_id")["truth"].astype(str)
        summary, per_label = metric_summary(df[["cell_id", "label", "confidence", "margin", "conflict_reason"]], truth)
        summary_rows.append({"dataset_id": dataset_id, "model": model, **summary})
        per_label.insert(0, "model", model)
        per_label.insert(0, "dataset_id", dataset_id)
        per_label_rows.append(per_label)

    for dataset_id in calls["dataset_id"].drop_duplicates():
        for comparator in [
            "reference_profile",
            "marker_reference_profile",
            "marker_spatial_smoothing",
            "marker_spatial_smoothing_random_graph",
            "marker_learned_neighborhood",
            "reference_profile_learned_neighborhood",
            "marker_context_specific_neighborhood",
            "learned_random_graph",
            "learned_permuted_prior",
        ]:
            pair_rows.append(paired_comparison(calls, dataset_id, "marker_only", comparator))

    return (
        pd.DataFrame(summary_rows),
        pd.concat(per_label_rows, ignore_index=True),
        pd.DataFrame(pair_rows),
    )


def guardrail_analysis(summary: pd.DataFrame, min_macro_f1_delta: float = 0.005) -> pd.DataFrame:
    rows = []
    for dataset_id, df in summary.groupby("dataset_id", sort=False):
        metrics = df.set_index("model")
        marker = metrics.loc["marker_only"]
        learned = metrics.loc["marker_learned_neighborhood"]
        learned_random = metrics.loc["learned_random_graph"]
        learned_permuted = metrics.loc["learned_permuted_prior"]
        context_specific = metrics.loc["marker_context_specific_neighborhood"]
        smoothing = metrics.loc["marker_spatial_smoothing"]
        smoothing_random = metrics.loc["marker_spatial_smoothing_random_graph"]

        learned_control_macro = max(
            marker["macro_f1"],
            learned_random["macro_f1"],
            learned_permuted["macro_f1"],
        )
        learned_control_accuracy = max(
            marker["accuracy"],
            learned_random["accuracy"],
            learned_permuted["accuracy"],
        )
        smoothing_control_macro = max(marker["macro_f1"], smoothing_random["macro_f1"])
        smoothing_control_accuracy = max(marker["accuracy"], smoothing_random["accuracy"])
        context_control_macro = max(
            marker["macro_f1"],
            learned["macro_f1"],
            learned_random["macro_f1"],
            learned_permuted["macro_f1"],
            smoothing_random["macro_f1"],
        )
        context_control_accuracy = max(
            marker["accuracy"],
            learned["accuracy"],
            learned_random["accuracy"],
            learned_permuted["accuracy"],
            smoothing_random["accuracy"],
        )

        learned_macro_delta = float(learned["macro_f1"] - learned_control_macro)
        learned_accuracy_delta = float(learned["accuracy"] - learned_control_accuracy)
        smoothing_macro_delta = float(smoothing["macro_f1"] - smoothing_control_macro)
        smoothing_accuracy_delta = float(smoothing["accuracy"] - smoothing_control_accuracy)
        context_macro_delta = float(context_specific["macro_f1"] - context_control_macro)
        context_accuracy_delta = float(context_specific["accuracy"] - context_control_accuracy)

        learned_pass = learned_macro_delta > min_macro_f1_delta and learned_accuracy_delta > 0
        smoothing_pass = smoothing_macro_delta > min_macro_f1_delta and smoothing_accuracy_delta > 0
        context_pass = context_macro_delta > min_macro_f1_delta and context_accuracy_delta > 0
        if context_pass:
            interpretation = "null-corrected context-specific signal"
        elif learned_pass:
            interpretation = "learned neighborhood beats marker and null controls"
        elif smoothing_pass:
            interpretation = "simple spatial smoothing beats marker and random smoothing"
        else:
            interpretation = "context signal is not specific under null controls"

        rows.append({
            "dataset_id": dataset_id,
            "marker_macro_f1": float(marker["macro_f1"]),
            "learned_macro_f1": float(learned["macro_f1"]),
            "learned_random_macro_f1": float(learned_random["macro_f1"]),
            "learned_permuted_macro_f1": float(learned_permuted["macro_f1"]),
            "learned_specific_macro_f1_delta": learned_macro_delta,
            "learned_specific_accuracy_delta": learned_accuracy_delta,
            "learned_passes_guardrail": learned_pass,
            "context_specific_macro_f1": float(context_specific["macro_f1"]),
            "context_specific_accuracy": float(context_specific["accuracy"]),
            "context_specific_macro_f1_delta": context_macro_delta,
            "context_specific_accuracy_delta": context_accuracy_delta,
            "context_specific_passes_guardrail": context_pass,
            "smoothing_macro_f1": float(smoothing["macro_f1"]),
            "smoothing_random_macro_f1": float(smoothing_random["macro_f1"]),
            "smoothing_specific_macro_f1_delta": smoothing_macro_delta,
            "smoothing_specific_accuracy_delta": smoothing_accuracy_delta,
            "smoothing_passes_guardrail": smoothing_pass,
            "min_macro_f1_delta": min_macro_f1_delta,
            "interpretation": interpretation,
        })
    return pd.DataFrame(rows)


def write_markdown_report(
    summary: pd.DataFrame,
    pairwise: pd.DataFrame,
    guardrail: pd.DataFrame,
    configs: list[dict],
) -> None:
    lines = [
        "# Multi-Dataset Blocked Benchmark Results",
        "",
        "This benchmark learns marker-like signatures and spatial compatibility",
        "inside each training fold, then evaluates held-out spatial groups.",
        "",
        "Models:",
        "",
        "- `marker_only`",
        "- `reference_profile`",
        "- `marker_reference_profile`",
        "- `marker_spatial_smoothing`",
        "- `marker_spatial_smoothing_random_graph`",
        "- `marker_learned_neighborhood`",
        "- `reference_profile_learned_neighborhood`",
        "- `marker_context_specific_neighborhood`",
        "- `learned_random_graph`",
        "- `learned_permuted_prior`",
        "",
        "## Summary",
        "",
        "| dataset | model | accuracy | macro-F1 | conflict rate |",
        "|---|---|---:|---:|---:|",
    ]
    ordered = summary.sort_values(["dataset_id", "model"])
    for row in ordered.itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.model} | {row.accuracy:.4f} | "
            f"{row.macro_f1:.4f} | {row.conflict_rate:.4f} |"
        )

    lines.extend([
        "",
        "## Specificity Guardrail",
        "",
        "The strongest guardrail is `marker_context_specific_neighborhood`: it",
        "uses observed learned-neighborhood scores after subtracting the mean of",
        "random-graph and permuted-prior null scores.",
        "",
        "A learned-neighborhood gain is counted as specific only if it beats",
        "marker-only, learned-random-graph, and learned-permuted-prior controls.",
        "A smoothing gain is counted as specific only if it beats marker-only and",
        "random-graph smoothing. Both guardrails require macro-F1 delta > 0.005",
        "and positive accuracy delta.",
        "",
        "| dataset | context-specific delta macro-F1 | context pass | learned delta macro-F1 | learned pass | smoothing delta macro-F1 | smoothing pass | interpretation |",
        "|---|---:|---|---:|---|---:|---|---|",
    ])
    for row in guardrail.sort_values("dataset_id").itertuples(index=False):
        context_pass = "yes" if row.context_specific_passes_guardrail else "no"
        learned_pass = "yes" if row.learned_passes_guardrail else "no"
        smoothing_pass = "yes" if row.smoothing_passes_guardrail else "no"
        lines.append(
            f"| {row.dataset_id} | {row.context_specific_macro_f1_delta:+.4f} | "
            f"{context_pass} | {row.learned_specific_macro_f1_delta:+.4f} | "
            f"{learned_pass} | {row.smoothing_specific_macro_f1_delta:+.4f} | "
            f"{smoothing_pass} | {row.interpretation} |"
        )

    best = summary.sort_values(["dataset_id", "macro_f1", "accuracy"], ascending=[True, False, False]).groupby("dataset_id").head(1)
    lines.extend([
        "",
        "## Best Model Per Dataset",
        "",
        "| dataset | best model | accuracy | macro-F1 |",
        "|---|---|---:|---:|",
    ])
    for row in best.itertuples(index=False):
        lines.append(f"| {row.dataset_id} | {row.model} | {row.accuracy:.4f} | {row.macro_f1:.4f} |")

    lines.extend([
        "",
        "## Paired Comparisons vs Marker-Only",
        "",
        "| dataset | comparator | accuracy diff | McNemar p |",
        "|---|---|---:|---:|",
    ])
    for row in pairwise.sort_values(["dataset_id", "comparator_model"]).itertuples(index=False):
        lines.append(f"| {row.dataset_id} | {row.comparator_model} | {row.accuracy_diff:+.4f} | {row.mcnemar_exact_p:.4g} |")

    lines.extend([
        "",
        "## Interpretation Guardrail",
        "",
        "A context layer should only be interpreted as useful when it beats",
        "`marker_only` and its matched random-graph or permuted-prior control",
        "under blocked validation. Equal performance or zero tuned weight should be",
        "reported as evidence for audit value rather than predictive improvement.",
        "",
        "## Dataset Configs",
        "",
        "```json",
        json.dumps(configs, indent=2),
        "```",
        "",
    ])
    (ROOT / "MULTIDATASET_BLOCKED_BENCHMARK.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    configs = dataset_configs()
    outputs = []
    for config in configs:
        outputs.append(evaluate_dataset(config))

    calls = pd.concat([out["calls"] for out in outputs], ignore_index=True)
    tuning = pd.concat([out["tuning"] for out in outputs], ignore_index=True)
    markers = pd.concat([out["markers"] for out in outputs], ignore_index=True)
    fold_reports = [fold for out in outputs for fold in out["fold_reports"]]
    summary, per_label, pairwise = summarize_all(calls)
    guardrail = guardrail_analysis(summary)

    calls.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv", index=False)
    tuning.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_tuning.csv", index=False)
    markers.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_learned_markers.csv", index=False)
    summary.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_summary.csv", index=False)
    per_label.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_per_label.csv", index=False)
    pairwise.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_pairwise.csv", index=False)
    guardrail.to_csv(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv", index=False)
    Path(ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_folds.json").write_text(
        json.dumps(fold_reports, indent=2),
        encoding="utf-8",
    )
    configs_for_report = [out["config"] for out in outputs]
    write_markdown_report(summary, pairwise, guardrail, configs_for_report)

    report = {
        "seed": SEED,
        "n_datasets": len(outputs),
        "datasets": configs_for_report,
        "summary": json.loads(summary.to_json(orient="records")),
        "pairwise": json.loads(pairwise.to_json(orient="records")),
        "guardrail": json.loads(guardrail.to_json(orient="records")),
    }
    (ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nSummary")
    print(summary.sort_values(["dataset_id", "model"]).to_string(index=False))
    print("\nBest per dataset")
    print(
        summary.sort_values(["dataset_id", "macro_f1", "accuracy"], ascending=[True, False, False])
        .groupby("dataset_id")
        .head(1)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
