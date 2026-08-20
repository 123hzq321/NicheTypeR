#!/usr/bin/env python
"""Spatial-context validation on two imaging-derived Spotless gold standards.

The analysis reconstructs the Visium-like seqFISH+ gold-standard spots from the
original Eng et al. single-cell imaging files, while generating every prediction
by leave-one-FOV-out cross-fitting.  Ground-truth cell labels and spot
compositions are used only after prediction for evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import pearsonr, wilcoxon
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, f1_score
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from sklearn.svm import LinearSVC


MODEL_COLUMNS = [
    "marker_only",
    "logreg_only",
    "linear_svm",
    "pca_knn",
    "extra_trees",
    "singler_native",
    "spatial_smoothing",
    "spatial_smoothing_random_graph",
    "learned_neighborhood",
    "learned_random_graph",
    "learned_permuted_prior",
    "context_specific",
    "gated_spatial_smoothing",
    "gated_spatial_smoothing_random_graph",
    "gated_learned_neighborhood",
    "gated_learned_random_graph",
    "gated_learned_permuted_prior",
    "gated_context_specific",
    "logreg_learned_neighborhood",
    "logreg_learned_random_graph",
    "logreg_learned_permuted_prior",
    "logreg_context_specific",
    "gated_logreg_learned_neighborhood",
    "gated_logreg_learned_random_graph",
    "gated_logreg_learned_permuted_prior",
    "gated_logreg_context_specific",
    "nested_logreg_learned_neighborhood",
    "nested_logreg_learned_random_graph",
    "nested_logreg_learned_permuted_prior",
    "nested_logreg_context_specific",
    "nested_gated_logreg_learned_neighborhood",
    "nested_gated_logreg_learned_random_graph",
    "nested_gated_logreg_learned_permuted_prior",
    "nested_gated_logreg_context_specific",
]


SINGLER_RUNNER = r"""
suppressPackageStartupMessages({
  library(SingleCellExperiment)
  library(SingleR)
})

args <- commandArgs(trailingOnly = TRUE)
train_path <- args[[1]]
test_path <- args[[2]]
labels_path <- args[[3]]
out_path <- args[[4]]

train <- as.matrix(read.delim(train_path, row.names = 1, check.names = FALSE))
test <- as.matrix(read.delim(test_path, row.names = 1, check.names = FALSE))
label_frame <- read.delim(labels_path, check.names = FALSE, stringsAsFactors = FALSE)

sce_train <- SingleCellExperiment(list(logcounts = train))
sce_test <- SingleCellExperiment(list(logcounts = test))
colData(sce_train)$source_label <- label_frame$source_label

pred <- SingleR(
  test = sce_test,
  ref = sce_train,
  labels = colData(sce_train)$source_label,
  de.method = "wilcox"
)

pruned <- pred$pruned.labels
if (is.null(pruned)) {
  pruned <- pred$labels
}
out <- data.frame(
  cell_id = colnames(test),
  singler_native = as.character(pred$labels),
  singler_pruned_label = as.character(pruned),
  stringsAsFactors = FALSE
)
write.table(out, out_path, sep = "\t", quote = FALSE, row.names = FALSE)
"""


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    annotation_file: str
    counts_file: str
    coordinates_file: str
    sheet_name: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("work/spotless_seqfish_raw"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/spotless_gold_standard_validation"),
    )
    parser.add_argument("--neighbors", type=int, default=10)
    parser.add_argument("--top-markers", type=int, default=20)
    parser.add_argument("--max-train-per-label", type=int, default=500)
    parser.add_argument("--min-label-cells", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260819)
    parser.add_argument(
        "--nested-weights",
        type=float,
        nargs="+",
        default=[0.0, 0.05, 0.10, 0.20, 0.35, 0.50],
        help="Candidate spatial weights selected inside the outer training FOVs.",
    )
    parser.add_argument(
        "--disable-singler",
        action="store_true",
        help="Skip the native SingleR baseline.",
    )
    parser.add_argument(
        "--rscript",
        type=Path,
        default=None,
        help="Path to Rscript. If omitted, conda run -n spatial-r-baselines Rscript is used when available.",
    )
    parser.add_argument(
        "--conda-exe",
        type=Path,
        default=Path(r"C:\Users\user\miniconda3\Scripts\conda.exe"),
        help="Conda executable used for the bundled R environment.",
    )
    parser.add_argument("--r-conda-env", type=str, default="spatial-r-baselines")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_label(value: object) -> str:
    label = " ".join(str(value).strip().split())
    low = label.lower()
    if low == "unannotated":
        return "Unannotated"
    if "interneuron" in low:
        return "Interneurons"
    if low.startswith("excitatory"):
        return "Excitatory neurons"
    if low in {"neuroblast", "neuroblasts"}:
        return "Neuroblasts"
    if low == "astrocytes superficial" or low == "astrocytes deep" or low == "astrocytes":
        return "Astrocytes"
    return label[:1].upper() + label[1:]


def cluster_mapping(xlsx: Path, sheet_name: str, annotation_clusters: pd.Series) -> dict[int, str]:
    raw = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)
    cluster_ids = pd.to_numeric(raw.iloc[0], errors="coerce")
    labels = raw.iloc[-1]
    mapping = {
        int(cluster): canonical_label(label)
        for cluster, label in zip(cluster_ids, labels)
        if pd.notna(cluster) and pd.notna(label)
    }
    observed = pd.to_numeric(annotation_clusters, errors="raise").astype(int)
    if observed.min() == 0 and min(mapping) == 1:
        mapping = {cluster - 1: label for cluster, label in mapping.items()}
    missing = sorted(set(observed.unique()) - set(mapping))
    if missing:
        raise ValueError(f"Missing cluster labels in {sheet_name}: {missing}")
    return mapping


def load_dataset(root: Path, config: DatasetConfig) -> tuple[np.ndarray, pd.DataFrame, list[str], dict]:
    annotation_path = root / "celltype_annotations" / config.annotation_file
    count_path = root / "sourcedata" / "sourcedata" / config.counts_file
    coordinate_path = root / "sourcedata" / "sourcedata" / config.coordinates_file
    xlsx_path = root / "cluster_annotations.xlsx"

    annotation = pd.read_csv(annotation_path).sort_values("index").reset_index(drop=True)
    coordinates = pd.read_csv(coordinate_path).reset_index(drop=True)
    counts = pd.read_csv(count_path, dtype=np.float32)
    if not (len(annotation) == len(coordinates) == len(counts)):
        raise ValueError(f"Row mismatch in {config.name}")

    mapping = cluster_mapping(xlsx_path, config.sheet_name, annotation["louvain"])
    labels = annotation["louvain"].astype(int).map(mapping).map(canonical_label)
    metadata = pd.DataFrame(
        {
            "cell_id": [f"{config.name}_cell_{i}" for i in annotation["index"].astype(int)],
            "fov": coordinates["Field of View"].astype(int),
            "x": pd.to_numeric(coordinates["X"]),
            "y": pd.to_numeric(coordinates["Y"]),
            "source_label": labels,
        }
    )
    keep = metadata["source_label"].ne("Unannotated") & metadata["source_label"].notna()
    counts_array = counts.loc[keep].to_numpy(dtype=np.float32, copy=True)
    metadata = metadata.loc[keep].reset_index(drop=True)
    genes = counts.columns.astype(str).tolist()
    provenance = {
        "annotation": annotation_path,
        "counts": count_path,
        "coordinates": coordinate_path,
        "cluster_annotations": xlsx_path,
    }
    return counts_array, metadata, genes, provenance


def log_normalize(counts: np.ndarray) -> np.ndarray:
    library = counts.sum(axis=1, keepdims=True)
    library[library <= 0] = 1
    return np.log1p(counts / library * 10_000).astype(np.float32)


def make_rscript_command(args: argparse.Namespace) -> list[str]:
    if args.rscript is not None:
        return [str(args.rscript)]
    if args.conda_exe.exists():
        return [str(args.conda_exe), "run", "-n", args.r_conda_env, "Rscript"]
    return ["Rscript"]


def write_singler_runner(output_dir: Path) -> Path:
    script_path = output_dir / "_singler_tmp" / "run_native_singler_fold.R"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(SINGLER_RUNNER.strip() + "\n", encoding="utf-8")
    return script_path


def run_singler_fold(
    expression: np.ndarray,
    train_rows: np.ndarray,
    test_rows: np.ndarray,
    labels: np.ndarray,
    genes: list[str],
    output_dir: Path,
    dataset_slug: str,
    fov: int,
    rscript_command: list[str],
    singler_script: Path,
) -> np.ndarray:
    fold_dir = output_dir / "_singler_tmp" / dataset_slug / f"fov_{int(fov)}"
    fold_dir.mkdir(parents=True, exist_ok=True)
    train_path = fold_dir / "train_logcounts.tsv.gz"
    test_path = fold_dir / "test_logcounts.tsv.gz"
    labels_path = fold_dir / "train_labels.tsv"
    out_path = fold_dir / "singler_predictions.tsv"

    train_cell_ids = [f"train_{int(row)}" for row in train_rows]
    test_cell_ids = [f"test_{int(row)}" for row in test_rows]
    if not out_path.exists():
        if not train_path.exists():
            pd.DataFrame(
                expression[train_rows].T,
                index=genes,
                columns=train_cell_ids,
            ).to_csv(train_path, sep="\t", compression="gzip")
        if not test_path.exists():
            pd.DataFrame(
                expression[test_rows].T,
                index=genes,
                columns=test_cell_ids,
            ).to_csv(test_path, sep="\t", compression="gzip")
        if not labels_path.exists():
            pd.DataFrame(
                {"cell_id": train_cell_ids, "source_label": labels[train_rows]}
            ).to_csv(labels_path, sep="\t", index=False)
        command = [
            *rscript_command,
            str(singler_script),
            str(train_path),
            str(test_path),
            str(labels_path),
            str(out_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                "Native SingleR failed for "
                f"{dataset_slug} FOV {int(fov)}.\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    result = pd.read_csv(out_path, sep="\t")
    prediction = result.set_index("cell_id")["singler_native"].reindex(test_cell_ids)
    if prediction.isna().any():
        missing = prediction[prediction.isna()].index.tolist()[:5]
        raise RuntimeError(f"SingleR output missing predictions for {missing}")
    return prediction.to_numpy(dtype=object)


def robust_standardize(scores: np.ndarray) -> np.ndarray:
    median = np.median(scores, axis=0, keepdims=True)
    mad = np.median(np.abs(scores - median), axis=0, keepdims=True)
    scale = 1.4826 * mad
    fallback = scores.std(axis=0, keepdims=True)
    scale[scale < 1e-6] = fallback[scale < 1e-6]
    scale[scale < 1e-6] = 1
    return ((scores - median) / scale).astype(np.float32)


def softmax(scores: np.ndarray) -> np.ndarray:
    shifted = scores - scores.max(axis=1, keepdims=True)
    ex = np.exp(np.clip(shifted, -50, 50))
    return ex / np.maximum(ex.sum(axis=1, keepdims=True), 1e-8)


def balanced_indices(indices: np.ndarray, labels: np.ndarray, maximum: int, rng: np.random.Generator) -> np.ndarray:
    selected = []
    for label in sorted(set(labels[indices])):
        candidates = indices[labels[indices] == label]
        if len(candidates) > maximum:
            candidates = rng.choice(candidates, size=maximum, replace=False)
        selected.extend(candidates.tolist())
    return np.asarray(selected, dtype=int)


def learn_marker_model(
    expression: np.ndarray,
    train_indices: np.ndarray,
    labels: np.ndarray,
    candidate_labels: list[str],
    top_markers: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    train = expression[train_indices]
    mu = train.mean(axis=0)
    sd = train.std(axis=0)
    sd[sd < 1e-4] = 1
    standardized = (train - mu) / sd
    contrasts = np.zeros((len(candidate_labels), expression.shape[1]), dtype=np.float32)
    records = []
    selected_set: set[int] = set()
    train_labels = labels[train_indices]
    for code, label in enumerate(candidate_labels):
        positive = train_labels == label
        if not positive.any() or positive.all():
            continue
        contrast = standardized[positive].mean(axis=0) - standardized[~positive].mean(axis=0)
        contrasts[code] = contrast
        positive_idx = np.argpartition(contrast, -min(top_markers, len(contrast)))[-top_markers:]
        negative_idx = np.argpartition(contrast, min(top_markers, len(contrast)) - 1)[:top_markers]
        for direction, feature_indices in [("positive", positive_idx), ("negative", negative_idx)]:
            for feature in feature_indices:
                selected_set.add(int(feature))
                records.append(
                    {
                        "label": label,
                        "direction": direction,
                        "feature_index": int(feature),
                        "contrast": float(contrast[feature]),
                    }
                )
    selected = np.asarray(sorted(selected_set), dtype=int)
    weights = contrasts[:, selected]
    norms = np.linalg.norm(weights, axis=1, keepdims=True)
    norms[norms < 1e-8] = 1
    weights = (weights / norms).astype(np.float32)
    return selected, mu[selected], sd[selected], weights, records


def score_marker(expression: np.ndarray, rows: np.ndarray, selected: np.ndarray, mu: np.ndarray, sd: np.ndarray, weights: np.ndarray) -> np.ndarray:
    standardized = (expression[np.ix_(rows, selected)] - mu) / sd
    return (standardized @ weights.T).astype(np.float32)


def align_class_matrix(
    values: np.ndarray,
    classes: np.ndarray,
    candidate_labels: list[str],
    fill: float,
) -> np.ndarray:
    values = np.asarray(values)
    if values.ndim == 1:
        values = np.column_stack([-values, values])
    aligned = np.full((values.shape[0], len(candidate_labels)), fill, dtype=np.float32)
    destination = {label: index for index, label in enumerate(candidate_labels)}
    for source_index, label in enumerate(classes.astype(str)):
        aligned[:, destination[label]] = values[:, source_index]
    return aligned


def train_logreg_scores(
    expression: np.ndarray,
    train_rows: np.ndarray,
    test_rows: np.ndarray,
    labels: np.ndarray,
    candidate_labels: list[str],
    selected: np.ndarray,
    mu: np.ndarray,
    sd: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    x_train = ((expression[np.ix_(train_rows, selected)] - mu) / sd).astype(np.float32)
    x_test = ((expression[np.ix_(test_rows, selected)] - mu) / sd).astype(np.float32)
    y_train = labels[train_rows]

    logreg = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=2000,
        solver="lbfgs",
        random_state=seed,
    ).fit(x_train, y_train)
    logreg_prob = align_class_matrix(
        logreg.predict_proba(x_test), logreg.classes_, candidate_labels, 0.0
    )
    logreg_prob /= np.maximum(logreg_prob.sum(axis=1, keepdims=True), 1e-8)
    return np.log(np.clip(logreg_prob, 1e-8, 1)), logreg_prob


def train_strong_expression_models(
    expression: np.ndarray,
    train_rows: np.ndarray,
    test_rows: np.ndarray,
    labels: np.ndarray,
    candidate_labels: list[str],
    selected: np.ndarray,
    mu: np.ndarray,
    sd: np.ndarray,
    seed: int,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    x_train = ((expression[np.ix_(train_rows, selected)] - mu) / sd).astype(np.float32)
    x_test = ((expression[np.ix_(test_rows, selected)] - mu) / sd).astype(np.float32)
    y_train = labels[train_rows]
    logreg_scores, logreg_prob = train_logreg_scores(
        expression,
        train_rows,
        test_rows,
        labels,
        candidate_labels,
        selected,
        mu,
        sd,
        seed,
    )

    svm = LinearSVC(
        C=1.0,
        class_weight="balanced",
        dual=False,
        max_iter=5000,
        random_state=seed,
    ).fit(x_train, y_train)
    svm_scores = align_class_matrix(
        svm.decision_function(x_test), svm.classes_, candidate_labels, -1e6
    )

    n_components = max(1, min(50, x_train.shape[1], x_train.shape[0] - 1))
    pca = PCA(n_components=n_components, random_state=seed, svd_solver="randomized")
    x_train_pca = pca.fit_transform(x_train)
    x_test_pca = pca.transform(x_test)
    knn = KNeighborsClassifier(
        n_neighbors=min(15, len(x_train)), weights="distance", n_jobs=-1
    ).fit(x_train_pca, y_train)
    knn_prob = align_class_matrix(
        knn.predict_proba(x_test_pca), knn.classes_, candidate_labels, 0.0
    )

    forest = ExtraTreesClassifier(
        n_estimators=300,
        class_weight="balanced",
        max_features="sqrt",
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=seed,
    ).fit(x_train, y_train)
    forest_prob = align_class_matrix(
        forest.predict_proba(x_test), forest.classes_, candidate_labels, 0.0
    )

    scores = {
        "logreg_only": logreg_scores,
        "linear_svm": svm_scores,
        "pca_knn": np.log(np.clip(knn_prob, 1e-8, 1)),
        "extra_trees": np.log(np.clip(forest_prob, 1e-8, 1)),
    }
    return scores, logreg_prob


def neighbor_average(probabilities: np.ndarray, neighbors: np.ndarray) -> np.ndarray:
    return probabilities[neighbors].mean(axis=1).astype(np.float32)


def within_group_neighbors(coords: np.ndarray, groups: np.ndarray, k: int) -> np.ndarray:
    result = np.full((len(coords), k), -1, dtype=int)
    for group in sorted(set(groups)):
        idx = np.flatnonzero(groups == group)
        n_neighbors = min(k + 1, len(idx))
        if n_neighbors <= 1:
            result[idx] = idx[:, None]
            continue
        local = NearestNeighbors(n_neighbors=n_neighbors, algorithm="kd_tree").fit(coords[idx])
        local_neighbors = local.kneighbors(coords[idx], return_distance=False)[:, 1:]
        global_neighbors = idx[local_neighbors]
        if global_neighbors.shape[1] < k:
            pad = np.repeat(global_neighbors[:, -1:], k - global_neighbors.shape[1], axis=1)
            global_neighbors = np.hstack([global_neighbors, pad])
        result[idx] = global_neighbors
    return result


def learn_compatibility(
    neighbors: np.ndarray,
    train_mask: np.ndarray,
    label_codes: np.ndarray,
    n_labels: int,
    pseudocount: float = 1.0,
) -> np.ndarray:
    counts = np.full((n_labels, n_labels), pseudocount, dtype=np.float64)
    sources = np.arange(len(train_mask))
    for column in range(neighbors.shape[1]):
        targets = neighbors[:, column]
        valid = train_mask & train_mask[targets]
        np.add.at(counts, (label_codes[sources[valid]], label_codes[targets[valid]]), 1)
    conditional = counts / counts.sum(axis=1, keepdims=True)
    background = counts.sum(axis=0) / counts.sum()
    return np.clip(np.log(conditional / background[None, :]), -3, 3).astype(np.float32)


def fuse_scores(base_scores: np.ndarray, spatial_scores: np.ndarray, weight: float) -> np.ndarray:
    if weight <= 0:
        return base_scores.copy()
    base = robust_standardize(base_scores)
    spatial = robust_standardize(spatial_scores)
    return ((1.0 - weight) * base + weight * spatial).astype(np.float32)


def low_margin_mask(probabilities: np.ndarray, quantile: float = 0.25) -> np.ndarray:
    sorted_prob = np.sort(probabilities, axis=1)
    margin = sorted_prob[:, -1] - sorted_prob[:, -2]
    return margin <= np.quantile(margin, quantile)


def apply_gate(base_scores: np.ndarray, alternative_scores: np.ndarray, mask: np.ndarray) -> np.ndarray:
    output = base_scores.copy()
    output[mask] = alternative_scores[mask]
    return output


def validation_objective(
    accuracy: float,
    macro_f1: float,
    rmse: float,
    mean_jsd: float,
    aupr_micro: float,
) -> float:
    return float(macro_f1 + aupr_micro - rmse - mean_jsd + 0.25 * accuracy)


def select_nested_logreg_weights(
    expression: np.ndarray,
    metadata: pd.DataFrame,
    labels: np.ndarray,
    fovs: np.ndarray,
    global_neighbors: np.ndarray,
    label_codes: np.ndarray,
    candidate_labels: list[str],
    outer_train: np.ndarray,
    weight_grid: list[float],
    top_markers: int,
    max_train_per_label: int,
    seed: int,
    held_out_fov: int,
) -> tuple[dict[str, float], list[dict]]:
    rng = np.random.default_rng(seed)
    weights_to_try = sorted({round(float(weight), 6) for weight in weight_grid} | {0.0})
    families = {
        "nested_logreg_learned_neighborhood": "learned",
        "nested_logreg_context_specific": "context",
        "nested_gated_logreg_learned_neighborhood": "gated_learned",
        "nested_gated_logreg_context_specific": "gated_context",
    }
    validation_model_names = ["logreg_only"]
    for family in families:
        for weight in weights_to_try:
            validation_model_names.append(f"{family}__w{weight:.3f}")

    validation_calls = []
    label_array = np.asarray(candidate_labels, dtype=object)
    inner_fovs = sorted(set(fovs[outer_train]))
    for inner_index, inner_fov in enumerate(inner_fovs):
        valid = outer_train[fovs[outer_train] == inner_fov]
        train = outer_train[fovs[outer_train] != inner_fov]
        sample = balanced_indices(train, labels, max_train_per_label, rng)
        selected, mu, sd, weights, _ = learn_marker_model(
            expression, sample, labels, candidate_labels, top_markers
        )
        logreg_scores, logreg_prob = train_logreg_scores(
            expression,
            sample,
            valid,
            labels,
            candidate_labels,
            selected,
            mu,
            sd,
            seed + inner_index + int(inner_fov),
        )

        lookup = np.full(len(labels), -1, dtype=int)
        lookup[valid] = np.arange(len(valid))
        validation_neighbors = lookup[global_neighbors[valid]]
        if (validation_neighbors < 0).any():
            raise RuntimeError("An inner-validation cell has a neighbor outside its FOV")
        random_neighbors = rng.integers(0, len(valid), size=validation_neighbors.shape)
        neighbor_prob = neighbor_average(logreg_prob, validation_neighbors)
        random_prob = neighbor_average(logreg_prob, random_neighbors)

        inner_train_mask = np.zeros(len(labels), dtype=bool)
        inner_train_mask[train] = True
        compatibility = learn_compatibility(
            global_neighbors, inner_train_mask, label_codes, len(candidate_labels)
        )
        permutation = rng.permutation(len(candidate_labels))
        permuted = compatibility[np.ix_(permutation, permutation)]
        learned = neighbor_prob @ compatibility.T
        learned_random = random_prob @ compatibility.T
        learned_permuted = neighbor_prob @ permuted.T
        context = learned - 0.5 * (learned_random + learned_permuted)

        base_scores = logreg_scores
        gate = low_margin_mask(logreg_prob)
        frame = metadata.iloc[valid][["cell_id", "fov", "x", "y", "source_label"]].copy()
        frame["logreg_only"] = label_array[np.argmax(base_scores, axis=1)]
        for weight in weights_to_try:
            learned_scores = fuse_scores(base_scores, learned, weight)
            context_scores = fuse_scores(base_scores, context, weight)
            family_scores = {
                "nested_logreg_learned_neighborhood": learned_scores,
                "nested_logreg_context_specific": context_scores,
                "nested_gated_logreg_learned_neighborhood": apply_gate(base_scores, learned_scores, gate),
                "nested_gated_logreg_context_specific": apply_gate(base_scores, context_scores, gate),
            }
            for family, scores in family_scores.items():
                frame[f"{family}__w{weight:.3f}"] = label_array[np.argmax(scores, axis=1)]
        validation_calls.append(frame)

    validation = pd.concat(validation_calls, ignore_index=True)
    compositions, _ = make_spots(validation, candidate_labels, models=validation_model_names)
    _, aggregate = evaluate_spots(compositions, candidate_labels, models=validation_model_names)
    aggregate = aggregate.set_index("model")
    baseline_metrics = aggregate.loc["logreg_only"]
    baseline_accuracy = accuracy_score(validation["source_label"], validation["logreg_only"])
    baseline_macro_f1 = f1_score(
        validation["source_label"], validation["logreg_only"], average="macro", zero_division=0
    )
    baseline_objective = validation_objective(
        baseline_accuracy,
        baseline_macro_f1,
        float(baseline_metrics["rmse"]),
        float(baseline_metrics["mean_jsd"]),
        float(baseline_metrics["aupr_micro"]),
    )

    selected = {}
    records = []
    for family in families:
        best_weight = 0.0
        best_objective = baseline_objective
        best_row = None
        for weight in weights_to_try:
            model = f"{family}__w{weight:.3f}"
            metrics = aggregate.loc[model]
            acc = accuracy_score(validation["source_label"], validation[model])
            macro = f1_score(validation["source_label"], validation[model], average="macro", zero_division=0)
            objective = validation_objective(
                acc,
                macro,
                float(metrics["rmse"]),
                float(metrics["mean_jsd"]),
                float(metrics["aupr_micro"]),
            )
            row = {
                "held_out_fov": int(held_out_fov),
                "family": family,
                "weight": float(weight),
                "accuracy": float(acc),
                "macro_f1": float(macro),
                "rmse": float(metrics["rmse"]),
                "mean_jsd": float(metrics["mean_jsd"]),
                "aupr_micro": float(metrics["aupr_micro"]),
                "objective": float(objective),
                "baseline_objective": float(baseline_objective),
            }
            records.append(row)
            if objective > best_objective + 1e-8:
                best_weight = float(weight)
                best_objective = float(objective)
                best_row = row
        if best_row is None:
            selected[family] = 0.0
        else:
            selected[family] = float(best_weight)

    for row in records:
        row["selected"] = bool(row["weight"] == selected[row["family"]])
        row["selected_weight"] = float(selected[row["family"]])
        row["auto_rejected_spatial"] = bool(selected[row["family"]] == 0.0)
    return selected, records


def predict_dataset(
    expression: np.ndarray,
    metadata: pd.DataFrame,
    genes: list[str],
    output_dir: Path,
    dataset_slug: str,
    neighbors: int,
    top_markers: int,
    max_train_per_label: int,
    min_label_cells: int,
    seed: int,
    nested_weights: list[float],
    run_singler: bool,
    rscript_command: list[str],
    singler_script: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    labels_all = metadata["source_label"].astype(str).to_numpy()
    fovs_all = metadata["fov"].to_numpy(dtype=int)
    counts = pd.Series(labels_all).value_counts()
    candidate_labels = sorted(counts[counts >= min_label_cells].index.tolist())
    candidate_labels = [
        label
        for label in candidate_labels
        if sum((labels_all[fovs_all != fov] == label).any() for fov in sorted(set(fovs_all))) == len(set(fovs_all))
    ]
    modeled = np.isin(labels_all, candidate_labels)
    expression = expression[modeled]
    metadata = metadata.loc[modeled].reset_index(drop=True)
    labels = metadata["source_label"].astype(str).to_numpy()
    fovs = metadata["fov"].to_numpy(dtype=int)
    coords = metadata[["x", "y"]].to_numpy(dtype=np.float32)
    global_neighbors = within_group_neighbors(coords, fovs, neighbors)
    label_to_code = {label: code for code, label in enumerate(candidate_labels)}
    label_codes = np.asarray([label_to_code[label] for label in labels], dtype=int)
    active_model_columns = [
        model for model in MODEL_COLUMNS if run_singler or model != "singler_native"
    ]
    predictions = {model: np.empty(len(labels), dtype=object) for model in active_model_columns}
    marker_rows = []
    fold_rows = []
    nested_weight_rows = []

    for fov in sorted(set(fovs)):
        test = np.flatnonzero(fovs == fov)
        train = np.flatnonzero(fovs != fov)
        sample = balanced_indices(train, labels, max_train_per_label, rng)
        selected, mu, sd, weights, records = learn_marker_model(
            expression, sample, labels, candidate_labels, top_markers
        )
        for record in records:
            record.update({"fov": int(fov), "gene": genes[record["feature_index"]]})
        marker_rows.extend(records)
        marker_scores = robust_standardize(score_marker(expression, test, selected, mu, sd, weights))
        marker_prob = softmax(marker_scores)
        strong_scores, logreg_prob = train_strong_expression_models(
            expression,
            sample,
            test,
            labels,
            candidate_labels,
            selected,
            mu,
            sd,
            seed + int(fov),
        )
        if run_singler:
            predictions["singler_native"][test] = run_singler_fold(
                expression,
                train,
                test,
                labels,
                genes,
                output_dir,
                dataset_slug,
                int(fov),
                rscript_command,
                singler_script,
            )

        lookup = np.full(len(labels), -1, dtype=int)
        lookup[test] = np.arange(len(test))
        test_neighbors = lookup[global_neighbors[test]]
        if (test_neighbors < 0).any():
            raise RuntimeError("A test cell has a neighbor outside the held-out FOV")
        neighbor_prob = neighbor_average(marker_prob, test_neighbors)
        random_neighbors = rng.integers(0, len(test), size=test_neighbors.shape)
        random_prob = neighbor_average(marker_prob, random_neighbors)
        logreg_neighbor_prob = neighbor_average(logreg_prob, test_neighbors)
        logreg_random_prob = neighbor_average(logreg_prob, random_neighbors)

        train_mask = fovs != fov
        compatibility = learn_compatibility(
            global_neighbors, train_mask, label_codes, len(candidate_labels)
        )
        permutation = rng.permutation(len(candidate_labels))
        permuted = compatibility[np.ix_(permutation, permutation)]
        learned = neighbor_prob @ compatibility.T
        learned_random = random_prob @ compatibility.T
        learned_permuted = neighbor_prob @ permuted.T
        context = learned - 0.5 * (learned_random + learned_permuted)
        logreg_learned = logreg_neighbor_prob @ compatibility.T
        logreg_learned_random = logreg_random_prob @ compatibility.T
        logreg_learned_permuted = logreg_neighbor_prob @ permuted.T
        logreg_context = logreg_learned - 0.5 * (
            logreg_learned_random + logreg_learned_permuted
        )

        selected_nested, nested_records = select_nested_logreg_weights(
            expression,
            metadata,
            labels,
            fovs,
            global_neighbors,
            label_codes,
            candidate_labels,
            train,
            nested_weights,
            top_markers,
            max_train_per_label,
            seed + 10_000 + int(fov),
            int(fov),
        )
        nested_weight_rows.extend(nested_records)

        smooth = 0.5 * marker_prob + 0.5 * neighbor_prob
        smooth_random = 0.5 * marker_prob + 0.5 * random_prob
        learned_fused = 0.5 * marker_scores + 0.5 * robust_standardize(learned)
        learned_random_fused = 0.5 * marker_scores + 0.5 * robust_standardize(learned_random)
        learned_permuted_fused = 0.5 * marker_scores + 0.5 * robust_standardize(learned_permuted)
        context_fused = 0.5 * marker_scores + 0.5 * robust_standardize(context)
        logreg_base_scores = robust_standardize(strong_scores["logreg_only"])
        logreg_learned_fused = 0.5 * logreg_base_scores + 0.5 * robust_standardize(logreg_learned)
        logreg_learned_random_fused = 0.5 * logreg_base_scores + 0.5 * robust_standardize(logreg_learned_random)
        logreg_learned_permuted_fused = 0.5 * logreg_base_scores + 0.5 * robust_standardize(logreg_learned_permuted)
        logreg_context_fused = 0.5 * logreg_base_scores + 0.5 * robust_standardize(logreg_context)
        logreg_raw_scores = strong_scores["logreg_only"]
        nested_logreg_learned_fused = fuse_scores(
            logreg_raw_scores,
            logreg_learned,
            selected_nested["nested_logreg_learned_neighborhood"],
        )
        nested_logreg_learned_random_fused = fuse_scores(
            logreg_raw_scores,
            logreg_learned_random,
            selected_nested["nested_logreg_learned_neighborhood"],
        )
        nested_logreg_learned_permuted_fused = fuse_scores(
            logreg_raw_scores,
            logreg_learned_permuted,
            selected_nested["nested_logreg_learned_neighborhood"],
        )
        nested_logreg_context_fused = fuse_scores(
            logreg_raw_scores,
            logreg_context,
            selected_nested["nested_logreg_context_specific"],
        )
        nested_gated_logreg_learned_fused = fuse_scores(
            logreg_raw_scores,
            logreg_learned,
            selected_nested["nested_gated_logreg_learned_neighborhood"],
        )
        nested_gated_logreg_learned_random_fused = fuse_scores(
            logreg_raw_scores,
            logreg_learned_random,
            selected_nested["nested_gated_logreg_learned_neighborhood"],
        )
        nested_gated_logreg_learned_permuted_fused = fuse_scores(
            logreg_raw_scores,
            logreg_learned_permuted,
            selected_nested["nested_gated_logreg_learned_neighborhood"],
        )
        nested_gated_logreg_context_fused = fuse_scores(
            logreg_raw_scores,
            logreg_context,
            selected_nested["nested_gated_logreg_context_specific"],
        )
        smooth_scores = np.log(np.clip(smooth, 1e-8, 1))
        smooth_random_scores = np.log(np.clip(smooth_random, 1e-8, 1))
        sorted_marker = np.sort(marker_scores, axis=1)
        marker_margin = sorted_marker[:, -1] - sorted_marker[:, -2]
        low_margin = marker_margin <= np.quantile(marker_margin, 0.25)

        def gated(alternative: np.ndarray) -> np.ndarray:
            output = marker_scores.copy()
            output[low_margin] = alternative[low_margin]
            return output

        low_logreg_margin = low_margin_mask(logreg_prob)

        def gated_logreg(alternative: np.ndarray) -> np.ndarray:
            output = logreg_base_scores.copy()
            output[low_logreg_margin] = alternative[low_logreg_margin]
            return output

        def gated_nested_logreg(alternative: np.ndarray) -> np.ndarray:
            output = logreg_raw_scores.copy()
            output[low_logreg_margin] = alternative[low_logreg_margin]
            return output

        model_scores = {
            "marker_only": marker_scores,
            **strong_scores,
            "spatial_smoothing": smooth_scores,
            "spatial_smoothing_random_graph": smooth_random_scores,
            "learned_neighborhood": learned_fused,
            "learned_random_graph": learned_random_fused,
            "learned_permuted_prior": learned_permuted_fused,
            "context_specific": context_fused,
            "gated_spatial_smoothing": gated(smooth_scores),
            "gated_spatial_smoothing_random_graph": gated(smooth_random_scores),
            "gated_learned_neighborhood": gated(learned_fused),
            "gated_learned_random_graph": gated(learned_random_fused),
            "gated_learned_permuted_prior": gated(learned_permuted_fused),
            "gated_context_specific": gated(context_fused),
            "logreg_learned_neighborhood": logreg_learned_fused,
            "logreg_learned_random_graph": logreg_learned_random_fused,
            "logreg_learned_permuted_prior": logreg_learned_permuted_fused,
            "logreg_context_specific": logreg_context_fused,
            "gated_logreg_learned_neighborhood": gated_logreg(logreg_learned_fused),
            "gated_logreg_learned_random_graph": gated_logreg(logreg_learned_random_fused),
            "gated_logreg_learned_permuted_prior": gated_logreg(logreg_learned_permuted_fused),
            "gated_logreg_context_specific": gated_logreg(logreg_context_fused),
            "nested_logreg_learned_neighborhood": nested_logreg_learned_fused,
            "nested_logreg_learned_random_graph": nested_logreg_learned_random_fused,
            "nested_logreg_learned_permuted_prior": nested_logreg_learned_permuted_fused,
            "nested_logreg_context_specific": nested_logreg_context_fused,
            "nested_gated_logreg_learned_neighborhood": gated_nested_logreg(nested_gated_logreg_learned_fused),
            "nested_gated_logreg_learned_random_graph": gated_nested_logreg(nested_gated_logreg_learned_random_fused),
            "nested_gated_logreg_learned_permuted_prior": gated_nested_logreg(nested_gated_logreg_learned_permuted_fused),
            "nested_gated_logreg_context_specific": gated_nested_logreg(nested_gated_logreg_context_fused),
        }
        label_array = np.asarray(candidate_labels, dtype=object)
        for model, scores in model_scores.items():
            predictions[model][test] = label_array[np.argmax(scores, axis=1)]
        fold_rows.append(
            {
                "held_out_fov": int(fov),
                "train_cells": int(len(train)),
                "test_cells": int(len(test)),
                "marker_training_sample": int(len(sample)),
                "selected_features": int(len(selected)),
                "nested_learned_weight": float(selected_nested["nested_logreg_learned_neighborhood"]),
                "nested_context_weight": float(selected_nested["nested_logreg_context_specific"]),
                "nested_gated_learned_weight": float(selected_nested["nested_gated_logreg_learned_neighborhood"]),
                "nested_gated_context_weight": float(selected_nested["nested_gated_logreg_context_specific"]),
            }
        )

    calls = metadata.copy()
    for model, values in predictions.items():
        calls[model] = values
    diagnostics = []
    for model in active_model_columns:
        diagnostics.append(
            {
                "model": model,
                "accuracy": accuracy_score(labels, calls[model]),
                "macro_f1": f1_score(labels, calls[model], average="macro", zero_division=0),
                "cells": len(calls),
                "labels": len(candidate_labels),
            }
        )
    info = {
        "total_annotated_cells": int(len(labels_all)),
        "modeled_cells": int(len(calls)),
        "modeled_fraction": float(len(calls) / len(labels_all)),
        "candidate_labels": candidate_labels,
        "folds": fold_rows,
        "model_columns": active_model_columns,
    }
    return calls, pd.DataFrame(marker_rows), {
        "diagnostics": diagnostics,
        "info": info,
        "nested_weights": pd.DataFrame(nested_weight_rows),
    }


def make_spots(
    calls: pd.DataFrame,
    categories: list[str],
    models: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if models is None:
        models = MODEL_COLUMNS
    fov_size = 2000.0
    spot_diameter = 55 / 0.103
    n_spots = int(np.floor(fov_size / spot_diameter))
    start = (fov_size - n_spots * spot_diameter) / 2
    centers = start + spot_diameter / 2 + spot_diameter * np.arange(n_spots)
    assignments = []
    spot_id = 0
    for fov in sorted(calls["fov"].unique()):
        local = calls[calls["fov"] == fov]
        for xi, cx in enumerate(centers):
            for yi, cy in enumerate(centers):
                spot_id += 1
                inside = (local["x"] - cx) ** 2 + (local["y"] - cy) ** 2 <= (spot_diameter / 2) ** 2
                for cell_id in local.loc[inside, "cell_id"]:
                    assignments.append({"cell_id": cell_id, "fov": int(fov), "spot": spot_id, "spot_x": xi, "spot_y": yi})
    membership = pd.DataFrame(assignments)
    joined = membership.merge(calls, on=["cell_id", "fov"], how="left", validate="many_to_one")
    rows = []
    for model in ["source_label", *models]:
        counts = pd.crosstab(joined["spot"], joined[model]).reindex(columns=categories, fill_value=0)
        totals = counts.sum(axis=1)
        proportions = counts.div(totals, axis=0)
        for spot, values in proportions.iterrows():
            row = {"spot": int(spot), "model": model, "cells": int(totals.loc[spot])}
            row.update({category: float(values[category]) for category in categories})
            rows.append(row)
    return pd.DataFrame(rows), membership


def evaluate_spots(
    compositions: pd.DataFrame,
    categories: list[str],
    models: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if models is None:
        models = MODEL_COLUMNS
    truth = compositions[compositions["model"] == "source_label"].set_index("spot")
    spot_rows = []
    aggregate_rows = []
    for model in models:
        pred = compositions[compositions["model"] == model].set_index("spot")
        common = truth.index.intersection(pred.index)
        true_values = truth.loc[common, categories].to_numpy()
        pred_values = pred.loc[common, categories].to_numpy()
        for row_index, spot in enumerate(common):
            true = true_values[row_index]
            estimate = pred_values[row_index]
            r = pearsonr(true, estimate).statistic if np.std(true) > 0 and np.std(estimate) > 0 else np.nan
            spot_rows.append(
                {
                    "model": model,
                    "spot": int(spot),
                    "fov": int(truth.loc[spot, "cells"] * 0 + ((int(spot) - 1) // 9)),
                    "pearson_r": float(r),
                    "jsd": float(jensenshannon(true, estimate, base=2) ** 2),
                    "rmse": float(np.sqrt(np.mean((true - estimate) ** 2))),
                    "cells": int(truth.loc[spot, "cells"]),
                }
            )
        aggregate_rows.append(
            {
                "model": model,
                "spots": int(len(common)),
                "rmse": float(np.sqrt(np.mean((true_values - pred_values) ** 2))),
                "mean_jsd": float(np.mean([jensenshannon(a, b, base=2) ** 2 for a, b in zip(true_values, pred_values)])),
                "aupr_micro": float(average_precision_score((true_values > 0).ravel(), pred_values.ravel())),
            }
        )
    return pd.DataFrame(spot_rows), pd.DataFrame(aggregate_rows)


def bootstrap_median(values: np.ndarray, rng: np.random.Generator, n_boot: int = 4000) -> tuple[float, float]:
    draws = np.asarray([np.median(rng.choice(values, len(values), replace=True)) for _ in range(n_boot)])
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def paired_comparisons(spot_metrics: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    models = sorted(spot_metrics["model"].unique())
    for model in models:
        current = spot_metrics[spot_metrics["model"] == model].set_index("spot")
        for control in models:
            if model == control:
                continue
            other = spot_metrics[spot_metrics["model"] == control].set_index("spot")
            common = current.index.intersection(other.index)
            paired = pd.DataFrame(
                {
                    "fov": current.loc[common, "fov"].astype(int),
                    "r_delta": current.loc[common, "pearson_r"].to_numpy() - other.loc[common, "pearson_r"].to_numpy(),
                    "jsd_delta": current.loc[common, "jsd"].to_numpy() - other.loc[common, "jsd"].to_numpy(),
                },
                index=common,
            )
            block = paired.groupby("fov")[["r_delta", "jsd_delta"]].median()
            r_delta = block["r_delta"].dropna().to_numpy()
            jsd_delta = block["jsd_delta"].dropna().to_numpy()
            r_ci = bootstrap_median(r_delta, rng)
            jsd_ci = bootstrap_median(jsd_delta, rng)
            rows.append(
                {
                    "model": model,
                    "control": control,
                    "paired_spots": len(common),
                    "fov_blocks": len(block),
                    "median_r_delta": float(np.median(r_delta)),
                    "r_ci_low": r_ci[0],
                    "r_ci_high": r_ci[1],
                    "r_wilcoxon_p": float(wilcoxon(r_delta).pvalue) if np.any(r_delta != 0) else 1.0,
                    "median_jsd_delta": float(np.median(jsd_delta)),
                    "jsd_ci_low": jsd_ci[0],
                    "jsd_ci_high": jsd_ci[1],
                    "jsd_wilcoxon_p": float(wilcoxon(jsd_delta).pvalue) if np.any(jsd_delta != 0) else 1.0,
                }
            )
    return pd.DataFrame(rows)


def add_guardrails(aggregate: pd.DataFrame, pairwise: pd.DataFrame) -> pd.DataFrame:
    aggregate = aggregate.copy()
    aggregate["guardrail_pass"] = False
    checks = {
        "learned_neighborhood": ["marker_only", "learned_random_graph", "learned_permuted_prior"],
        "context_specific": [
            "marker_only",
            "learned_neighborhood",
            "learned_random_graph",
            "learned_permuted_prior",
            "spatial_smoothing_random_graph",
        ],
        "gated_learned_neighborhood": [
            "marker_only",
            "gated_learned_random_graph",
            "gated_learned_permuted_prior",
        ],
        "gated_context_specific": [
            "marker_only",
            "gated_learned_neighborhood",
            "gated_learned_random_graph",
            "gated_learned_permuted_prior",
            "gated_spatial_smoothing_random_graph",
        ],
        "logreg_learned_neighborhood": [
            "logreg_only",
            "logreg_learned_random_graph",
            "logreg_learned_permuted_prior",
        ],
        "logreg_context_specific": [
            "logreg_only",
            "logreg_learned_neighborhood",
            "logreg_learned_random_graph",
            "logreg_learned_permuted_prior",
        ],
        "gated_logreg_learned_neighborhood": [
            "logreg_only",
            "gated_logreg_learned_random_graph",
            "gated_logreg_learned_permuted_prior",
        ],
        "gated_logreg_context_specific": [
            "logreg_only",
            "gated_logreg_learned_neighborhood",
            "gated_logreg_learned_random_graph",
            "gated_logreg_learned_permuted_prior",
        ],
        "nested_logreg_learned_neighborhood": [
            "logreg_only",
            "nested_logreg_learned_random_graph",
            "nested_logreg_learned_permuted_prior",
        ],
        "nested_logreg_context_specific": [
            "logreg_only",
            "nested_logreg_learned_neighborhood",
            "nested_logreg_learned_random_graph",
            "nested_logreg_learned_permuted_prior",
        ],
        "nested_gated_logreg_learned_neighborhood": [
            "logreg_only",
            "nested_gated_logreg_learned_random_graph",
            "nested_gated_logreg_learned_permuted_prior",
        ],
        "nested_gated_logreg_context_specific": [
            "logreg_only",
            "nested_gated_logreg_learned_neighborhood",
            "nested_gated_logreg_learned_random_graph",
            "nested_gated_logreg_learned_permuted_prior",
        ],
    }
    for model, controls in checks.items():
        relevant = pairwise[(pairwise["model"] == model) & pairwise["control"].isin(controls)]
        passed = len(relevant) == len(controls) and bool(
            (
                (relevant["median_r_delta"] > 0)
                & (relevant["r_wilcoxon_p"] < 0.05)
                & (relevant["median_jsd_delta"] < 0)
                & (relevant["jsd_wilcoxon_p"] < 0.05)
            ).all()
        )
        aggregate.loc[aggregate["model"] == model, "guardrail_pass"] = passed
    return aggregate


def make_figure(summary: pd.DataFrame, output_path: Path) -> None:
    focus = [
        "marker_only",
        "logreg_only",
        "singler_native",
        "logreg_learned_neighborhood",
        "logreg_context_specific",
        "nested_logreg_learned_neighborhood",
        "nested_logreg_context_specific",
    ]
    labels = ["marker", "logistic", "SingleR", "fixed + learned", "fixed + CSAE", "nested + learned", "nested + CSAE"]
    colors = ["#2F6BFF", "#1B7F5A", "#4B5563", "#D97706", "#B04492", "#F0A43A", "#D66BB4"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    for ax, (dataset, frame) in zip(axes, summary.groupby("dataset", sort=False)):
        panel = frame.set_index("model").reindex(focus)
        ax.bar(np.arange(len(focus)), panel["aupr_micro"], color=colors)
        ax.set_xticks(np.arange(len(focus)), labels, rotation=20, ha="right")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Spot-composition AUPR")
        ax.set_title(dataset)
    fig.suptitle("Spotless imaging-derived seqFISH+ gold standards")
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def write_report(
    output_dir: Path,
    summary: pd.DataFrame,
    pairwise: pd.DataFrame,
    diagnostics: pd.DataFrame,
    metadata: dict,
    nested_weights: pd.DataFrame | None = None,
) -> None:
    dataset_count = int(summary["dataset"].nunique())
    fixed_learned_passes = int(summary.loc[summary["model"] == "learned_neighborhood", "guardrail_pass"].sum())
    fixed_context_passes = int(summary.loc[summary["model"] == "context_specific", "guardrail_pass"].sum())
    gated_learned_passes = int(summary.loc[summary["model"] == "gated_learned_neighborhood", "guardrail_pass"].sum())
    gated_context_passes = int(summary.loc[summary["model"] == "gated_context_specific", "guardrail_pass"].sum())
    logreg_learned_passes = int(summary.loc[summary["model"] == "logreg_learned_neighborhood", "guardrail_pass"].sum())
    logreg_context_passes = int(summary.loc[summary["model"] == "logreg_context_specific", "guardrail_pass"].sum())
    gated_logreg_learned_passes = int(summary.loc[summary["model"] == "gated_logreg_learned_neighborhood", "guardrail_pass"].sum())
    gated_logreg_context_passes = int(summary.loc[summary["model"] == "gated_logreg_context_specific", "guardrail_pass"].sum())
    nested_logreg_learned_passes = int(summary.loc[summary["model"] == "nested_logreg_learned_neighborhood", "guardrail_pass"].sum())
    nested_logreg_context_passes = int(summary.loc[summary["model"] == "nested_logreg_context_specific", "guardrail_pass"].sum())
    nested_gated_logreg_learned_passes = int(summary.loc[summary["model"] == "nested_gated_logreg_learned_neighborhood", "guardrail_pass"].sum())
    nested_gated_logreg_context_passes = int(summary.loc[summary["model"] == "nested_gated_logreg_context_specific", "guardrail_pass"].sum())
    nested_selected = ""
    if nested_weights is not None and not nested_weights.empty:
        selected_rows = nested_weights[nested_weights["selected"].astype(bool)]
        positive = int((selected_rows["selected_weight"].astype(float) > 0).sum())
        total = int(len(selected_rows))
        nested_selected = (
            f" Across all held-out FOVs and nested families, positive spatial weights were selected in "
            f"**{positive}/{total}** selections; the remaining selections automatically reverted to the logistic-only baseline."
        )
    lines = [
        "# Spotless imaging-derived gold-standard validation",
        "",
        "## Scope",
        "",
        "Two official Spotless seqFISH+ gold-standard tasks were reconstructed from the original Eng et al. single-cell imaging files: cortex/SVZ and olfactory bulb. Each contains seven FOVs and 63 Visium-like spots with exactly known cell-type composition.",
        "",
        "This evaluates a hypothesis-aligned marker / learned-neighborhood / CSAE-like reference implementation. Four stronger expression-only classifiers (regularized multinomial logistic regression, linear SVM, PCA-kNN, and ExtraTrees) and a native SingleR baseline were added, and the spatial modules were also attached directly to the logistic model. It is not a locked-software run of a released NicheTypeR package, and Spotless is a spot-composition benchmark rather than an orthogonal protein-imaging assay.",
        "",
        "## Leakage controls",
        "",
        "- Every cell prediction is leave-one-FOV-out: marker signatures, expression classifiers, PCA transforms, and label-compatibility priors are learned from the other six FOVs.",
        "- Native SingleR is run fold-by-fold in R: the six training FOVs form the reference and the held-out FOV is never included in the reference.",
        "- Ground-truth cell labels and spot compositions from the held-out FOV are used only for evaluation.",
        "- Random-neighbor and permuted-compatibility controls test specificity.",
        "- In addition to fixed 50:50 fusion across all cells, a pre-specified gated analysis changes only the lowest marker-margin quartile in each held-out FOV; its null controls use the identical gate.",
        "- Nested logistic-spatial models select their spatial weight only inside the six outer-training FOVs. The candidate grid includes weight 0, and a positive spatial weight is accepted only when the inner-training objective improves over logistic alone.",
        "- Paired inference first collapses spot effects within each FOV, leaving seven spatially independent blocks per dataset.",
        "",
        "## Results",
        "",
        "| dataset | model | cells | labels | spots | accuracy | macro F1 | RMSE | mean JSD | AUPR | guardrail |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary.itertuples(index=False):
        tested_models = {
            "learned_neighborhood", "context_specific",
            "gated_learned_neighborhood", "gated_context_specific",
            "logreg_learned_neighborhood", "logreg_context_specific",
            "gated_logreg_learned_neighborhood", "gated_logreg_context_specific",
            "nested_logreg_learned_neighborhood", "nested_logreg_context_specific",
            "nested_gated_logreg_learned_neighborhood", "nested_gated_logreg_context_specific",
        }
        guard = "yes" if bool(row.guardrail_pass) else ("no" if row.model in tested_models else "n/a")
        lines.append(
            f"| {row.dataset} | {row.model} | {row.cells} | {row.labels} | {row.spots} | {row.accuracy:.3f} | {row.macro_f1:.3f} | {row.rmse:.3f} | {row.mean_jsd:.3f} | {row.aupr_micro:.3f} | {guard} |"
        )
    lines.extend(
        [
            "",
            "A learned-neighborhood pass requires better FOV-level median Pearson correlation and JSD than its matched expression-only, random-neighbor, and permuted-prior controls, with two-sided Wilcoxon p < 0.05 for both endpoints. CSAE-like must additionally beat learned-neighborhood. Gated models are judged only against controls using the identical low-margin gate.",
            "",
            "## Interpretation",
            "",
            f"Fixed learned-neighborhood passed in **{fixed_learned_passes}/{dataset_count}** datasets and fixed CSAE-like in **{fixed_context_passes}/{dataset_count}**. Restricting intervention to the lowest marker-margin quartile did not reverse the result: gated learned-neighborhood passed in **{gated_learned_passes}/{dataset_count}** and gated CSAE-like in **{gated_context_passes}/{dataset_count}**.",
            "",
            f"Against the stronger paired logistic baseline, fixed learned-neighborhood passed in **{logreg_learned_passes}/{dataset_count}** and fixed CSAE-like in **{logreg_context_passes}/{dataset_count}**; low-margin gated versions passed in **{gated_logreg_learned_passes}/{dataset_count}** and **{gated_logreg_context_passes}/{dataset_count}**, respectively. These paired results are the relevant test of incremental spatial value after a competent expression classifier, while the four expression-only models show how sensitive the conclusion is to baseline strength.",
            "",
            f"Nested weight selection provides an explicit rejection mechanism: learned-neighborhood passed in **{nested_logreg_learned_passes}/{dataset_count}** datasets and CSAE-like in **{nested_logreg_context_passes}/{dataset_count}** after selecting the logistic-spatial weight inside the outer training FOVs. The identical low-margin nested gate passed in **{nested_gated_logreg_learned_passes}/{dataset_count}** and **{nested_gated_logreg_context_passes}/{dataset_count}** datasets, respectively.{nested_selected}",
            "",
            "## Limitations",
            "",
            "- The seqFISH+ cell-type labels were derived from the same targeted transcript measurements using clustering and marker interpretation. The spot composition is exact, but the cell-type naming is not an independent protein/pathology truth.",
            "- This run covers 2/3 Spotless gold standards. The STARmap task is only distributed inside the official 6.9 GB sequential archive and was not included in this compact reconstruction.",
            "- There are seven FOV blocks per dataset, so power for strict dual-endpoint tests is limited.",
            "- Results establish behavior of the reference mechanism, not final software performance.",
            "",
            "## Reproducibility",
            "",
            "- `spotless_summary.csv`: aggregate cell and spot metrics.",
            "- `spotless_pairwise_comparisons.csv`: FOV-block paired tests and bootstrap intervals.",
            "- `spotless_spot_metrics.csv`: per-spot Pearson r, JSD, and RMSE.",
            "- `spotless_crossfit_calls_*.csv.gz`: all held-out cell predictions.",
            "- `spotless_spot_compositions_*.csv.gz`: true and predicted spot compositions.",
            "- `spotless_nested_weight_selection.csv`: inner-fold candidate weights, objectives, and selected weights.",
            "- `spotless_selected_markers.csv.gz`: fold-specific markers.",
            "- `data_manifest.csv` and `run_metadata.json`: source hashes, parameters, and coverage.",
        ]
    )
    (output_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    configs = [
        DatasetConfig(
            "seqFISH+ cortex/SVZ",
            "cortex_svz_cell_type_annotations.csv",
            "cortex_svz_counts.csv",
            "cortex_svz_cellcentroids.csv",
            "Cortex_SVZ",
        ),
        DatasetConfig(
            "seqFISH+ olfactory bulb",
            "OB_cell_type_annotations.csv",
            "ob_counts.csv",
            "ob_cellcentroids.csv",
            "Olfactory bulb",
        ),
    ]
    summaries = []
    all_pairwise = []
    all_spot_metrics = []
    all_markers = []
    all_diagnostics = []
    all_nested_weights = []
    manifest = {}
    rscript_command = make_rscript_command(args)
    singler_script = write_singler_runner(args.output_dir)
    run_meta = {
        "analysis_date": date.today().isoformat(),
        "seed": args.seed,
        "neighbors": args.neighbors,
        "top_markers": args.top_markers,
        "max_train_per_label": args.max_train_per_label,
        "min_label_cells": args.min_label_cells,
        "nested_weights": args.nested_weights,
        "native_singler": not args.disable_singler,
        "rscript_command": rscript_command,
        "source": "Spotless gold standards reconstructed from Eng et al. seqFISH+",
        "spotless_record": "https://doi.org/10.5281/zenodo.13373946",
        "datasets": {},
    }
    for dataset_index, config in enumerate(configs):
        print(f"[{config.name}] loading", flush=True)
        counts, metadata, genes, provenance = load_dataset(args.data_root, config)
        expression = log_normalize(counts)
        slug = "cortex_svz" if dataset_index == 0 else "olfactory_bulb"
        print(f"[{config.name}] leave-one-FOV-out prediction", flush=True)
        calls, markers, details = predict_dataset(
            expression,
            metadata,
            genes,
            args.output_dir,
            slug,
            args.neighbors,
            args.top_markers,
            args.max_train_per_label,
            args.min_label_cells,
            args.seed + dataset_index * 1000,
            args.nested_weights,
            not args.disable_singler,
            rscript_command,
            singler_script,
        )
        categories = details["info"]["candidate_labels"]
        model_columns = details["info"]["model_columns"]
        compositions, membership = make_spots(calls, categories, models=model_columns)
        spot_metrics, aggregate = evaluate_spots(compositions, categories, models=model_columns)
        pairwise = paired_comparisons(spot_metrics, args.seed + dataset_index * 1000)
        aggregate = add_guardrails(aggregate, pairwise)
        diagnostic = pd.DataFrame(details["diagnostics"])
        summary = aggregate.merge(diagnostic, on="model", validate="one_to_one")
        summary.insert(0, "dataset", config.name)

        calls.to_csv(args.output_dir / f"spotless_crossfit_calls_{slug}.csv.gz", index=False, compression="gzip")
        compositions.to_csv(args.output_dir / f"spotless_spot_compositions_{slug}.csv.gz", index=False, compression="gzip")
        membership.to_csv(args.output_dir / f"spotless_spot_membership_{slug}.csv.gz", index=False, compression="gzip")
        markers["dataset"] = config.name
        nested_weights = details["nested_weights"].copy()
        nested_weights.insert(0, "dataset", config.name)
        pairwise.insert(0, "dataset", config.name)
        spot_metrics.insert(0, "dataset", config.name)
        all_markers.append(markers)
        all_nested_weights.append(nested_weights)
        all_pairwise.append(pairwise)
        all_spot_metrics.append(spot_metrics)
        all_diagnostics.append(diagnostic.assign(dataset=config.name))
        summaries.append(summary)
        run_meta["datasets"][config.name] = details["info"]
        for kind, path in provenance.items():
            key = str(path.resolve())
            manifest[key] = {
                "dataset": config.name,
                "kind": kind,
                "file": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }

    summary = pd.concat(summaries, ignore_index=True)
    pairwise = pd.concat(all_pairwise, ignore_index=True)
    spot_metrics = pd.concat(all_spot_metrics, ignore_index=True)
    markers = pd.concat(all_markers, ignore_index=True)
    diagnostics = pd.concat(all_diagnostics, ignore_index=True)
    nested_weights = pd.concat(all_nested_weights, ignore_index=True)
    summary.to_csv(args.output_dir / "spotless_summary.csv", index=False)
    pairwise.to_csv(args.output_dir / "spotless_pairwise_comparisons.csv", index=False)
    spot_metrics.to_csv(args.output_dir / "spotless_spot_metrics.csv", index=False)
    markers.to_csv(args.output_dir / "spotless_selected_markers.csv.gz", index=False, compression="gzip")
    nested_weights.to_csv(args.output_dir / "spotless_nested_weight_selection.csv", index=False)
    diagnostics.to_csv(args.output_dir / "spotless_cell_diagnostics.csv", index=False)
    pd.DataFrame(manifest.values()).to_csv(args.output_dir / "data_manifest.csv", index=False)
    (args.output_dir / "run_metadata.json").write_text(json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    make_figure(summary, args.output_dir / "spotless_gold_results.png")
    write_report(args.output_dir, summary, pairwise, diagnostics, run_meta, nested_weights)
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
