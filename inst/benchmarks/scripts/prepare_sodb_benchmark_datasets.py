from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse

import audit_sodb_spatial_metadata as sodb_audit


ROOT = Path(__file__).resolve().parent
SEED = 20260928
BAD_LABELS = {
    "",
    "nan",
    "none",
    "na",
    "unknown",
    "unassigned",
    "unannotated",
    "ambiguous",
    "other",
    "low quality",
    "low_quality",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare audited SODB H5ADs as blocked NicheTypeR benchmark datasets."
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=ROOT / "SODB_BENCHMARK_CANDIDATES.csv",
    )
    parser.add_argument(
        "--audit",
        type=Path,
        default=ROOT / "sodb_audit" / "SODB_REPRESENTATIVE_METADATA_AUDIT.csv",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=ROOT / "sodb_audit" / "SODB_SPATIAL_FILE_INVENTORY.csv",
    )
    parser.add_argument("--cache-root", type=Path, default=Path(r"D:\NicheTypeR_SODB_CACHE"))
    parser.add_argument(
        "--prepared-root",
        type=Path,
        default=Path(r"D:\NicheTypeR_SODB_CACHE\prepared"),
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=ROOT / "EXPANDED_SCALE_DATASETS.csv",
    )
    parser.add_argument("--max-per-label", type=int, default=1000)
    parser.add_argument("--min-per-label", type=int, default=20)
    parser.add_argument("--max-features", type=int, default=1000)
    parser.add_argument("--max-all-file-mb", type=float, default=25.0)
    parser.add_argument("--only", default="")
    return parser.parse_args()


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_").upper()


def spatial_coordinates(adata: ad.AnnData) -> np.ndarray | None:
    preferred = ["spatial", "X_spatial"]
    keys = list(adata.obsm.keys())
    for key in preferred + [key for key in keys if "spatial" in str(key).lower()]:
        if key not in adata.obsm:
            continue
        values = np.asarray(adata.obsm[key], dtype=float)
        if values.ndim == 2 and values.shape[1] >= 2:
            return values[:, :2]
    lower = {str(column).lower(): str(column) for column in adata.obs.columns}
    pairs = [
        ("x", "y"),
        ("center_x", "center_y"),
        ("global.x", "global.y"),
        ("adjusted.x", "adjusted.y"),
        ("array_col", "array_row"),
        ("spatial_x", "spatial_y"),
    ]
    for x_name, y_name in pairs:
        if x_name in lower and y_name in lower:
            return np.column_stack(
                [
                    pd.to_numeric(adata.obs[lower[x_name]], errors="coerce"),
                    pd.to_numeric(adata.obs[lower[y_name]], errors="coerce"),
                ]
            )
    return None


def spatial_blocks(x: pd.Series, y: pd.Series, bins: int = 6) -> pd.Series:
    n = len(x)
    target_bins = min(bins, max(2, int(math.sqrt(max(n, 1) / 40))))
    xbin = pd.qcut(x.rank(method="first"), q=target_bins, labels=False, duplicates="drop")
    ybin = pd.qcut(y.rank(method="first"), q=target_bins, labels=False, duplicates="drop")
    return "x" + xbin.astype(str) + "_y" + ybin.astype(str)


def clean_label_mask(labels: pd.Series) -> pd.Series:
    values = labels.astype(str).str.strip()
    return (
        ~values.str.lower().isin(BAD_LABELS)
        & ~values.str.fullmatch(r"[A-Za-z]", na=False)
        & values.ne("")
    )


def choose_balanced(
    metadata: pd.DataFrame, max_per_label: int, min_per_label: int
) -> pd.DataFrame:
    eligible = metadata.loc[clean_label_mask(metadata["label"])].copy()
    counts = eligible["label"].value_counts()
    keep = counts.loc[counts >= min_per_label].index
    eligible = eligible.loc[eligible["label"].isin(keep)]
    rng = np.random.default_rng(SEED)
    selected: list[pd.DataFrame] = []
    for _, group in eligible.groupby("label", sort=True):
        if len(group) > max_per_label:
            positions = np.sort(rng.choice(len(group), size=max_per_label, replace=False))
            group = group.iloc[positions]
        selected.append(group)
    if not selected:
        return eligible.iloc[0:0]
    result = pd.concat(selected, ignore_index=True)
    return result.sort_values(["source_file", "source_row"], kind="stable").reset_index(drop=True)


def make_unique(values: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    output: list[str] = []
    for value in values:
        base = str(value) or "feature"
        count = counts.get(base, 0)
        output.append(base if count == 0 else f"{base}__{count + 1}")
        counts[base] = count + 1
    return output


def selected_files(
    candidate: pd.Series,
    audit: pd.DataFrame,
    inventory: pd.DataFrame,
    args: argparse.Namespace,
) -> tuple[list[Path], list[str]]:
    dataset_name = str(candidate["dataset_name"])
    experiment_mode = str(candidate["experiment_mode"])
    if experiment_mode == "representative":
        rows = audit.loc[audit["dataset_name"].eq(dataset_name)]
        if rows.empty:
            return [], ["representative not present in audit table"]
        path = Path(str(rows.iloc[0]["file_path"]))
        return ([path] if path.exists() else []), ([] if path.exists() else [f"missing {path}"])

    if experiment_mode == "audited_multi3":
        rows = audit.loc[audit["dataset_name"].eq(dataset_name)]
        paths = [Path(str(value)) for value in rows["file_path"] if str(value)]
        existing = sorted({path for path in paths if path.exists()}, key=lambda path: str(path))
        missing = [f"missing {path}" for path in paths if not path.exists()]
        return existing, missing

    rows = inventory.loc[inventory["dataset_name"].eq(dataset_name)].copy()
    rows["size_bytes"] = pd.to_numeric(rows["size_bytes"], errors="coerce")
    rows = rows.loc[
        rows["size_bytes"].between(100_000, args.max_all_file_mb * 1_000_000, inclusive="both")
    ].sort_values(["size_bytes", "experiment_name"])
    paths: list[Path] = []
    errors: list[str] = []
    for _, row in rows.iterrows():
        path, error = sodb_audit.download_file(row, args.cache_root, timeout=240.0)
        if path is not None:
            paths.append(path)
        else:
            errors.append(f"{row['experiment_name']}: {error}")
    return paths, errors


def metadata_from_file(path: Path, candidate: pd.Series) -> tuple[pd.DataFrame | None, str]:
    adata = None
    try:
        adata = ad.read_h5ad(path, backed="r")
        label_options = [
            value.strip() for value in str(candidate["label_col"]).split("|") if value.strip()
        ]
        label_col = next((value for value in label_options if value in adata.obs.columns), "")
        if not label_col:
            return None, f"missing label columns {' | '.join(label_options)}"
        coords = spatial_coordinates(adata)
        if coords is None:
            return None, "missing spatial coordinates"
        frame = pd.DataFrame(
            {
                "source_row": np.arange(adata.n_obs, dtype=int),
                "source_obs_name": adata.obs_names.astype(str),
                "label": adata.obs[label_col].astype(str).to_numpy(),
                "x": coords[:, 0],
                "y": coords[:, 1],
            }
        )
        group_col = str(candidate.get("preferred_group_col", "")).strip()
        if group_col and group_col != "__experiment__" and group_col in adata.obs.columns:
            groups = adata.obs[group_col].astype(str).to_numpy()
            if pd.Series(groups).nunique() >= 3:
                frame["fov_group"] = path.stem + "::" + pd.Series(groups).astype(str)
        if "fov_group" not in frame:
            frame["fov_group"] = path.stem
        frame["source_file"] = str(path)
        frame["source_experiment"] = path.stem
        frame["cell_id"] = (
            safe_id(candidate["dataset_name"])
            + "::"
            + path.stem
            + "::"
            + frame["source_obs_name"].astype(str)
        )
        return frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["x", "y"]), ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    finally:
        if adata is not None and getattr(adata, "file", None) is not None:
            adata.file.close()


def add_block_groups(metadata: pd.DataFrame, experiment_mode: str) -> pd.DataFrame:
    result = metadata.copy()
    if result["source_experiment"].nunique() >= 2 and experiment_mode in {
        "all_small",
        "audited_multi3",
    }:
        result["fov_group"] = result["source_experiment"].astype(str)
        return result
    if result["fov_group"].nunique() >= 3:
        return result
    blocks = []
    for source_file, group in result.groupby("source_file", sort=False):
        block = spatial_blocks(group["x"], group["y"])
        blocks.append(
            pd.Series(
                Path(source_file).stem + "::" + block.astype(str).to_numpy(),
                index=group.index,
            )
        )
    result.loc[:, "fov_group"] = pd.concat(blocks).sort_index()
    return result


def common_features(paths: list[Path]) -> list[str]:
    common: set[str] | None = None
    first_order: list[str] = []
    for index, path in enumerate(paths):
        adata = ad.read_h5ad(path, backed="r")
        names = list(map(str, adata.var_names))
        adata.file.close()
        if index == 0:
            first_order = names
            common = set(names)
        else:
            common &= set(names)
    common = common or set()
    return [name for name in first_order if name in common]


def read_selected_expression(
    selected: pd.DataFrame, paths: list[Path], feature_names: list[str]
) -> sparse.csr_matrix:
    matrices: list[sparse.csr_matrix] = []
    observed_order: list[str] = []
    for path in paths:
        subset = selected.loc[selected["source_file"].eq(str(path))]
        if subset.empty:
            continue
        adata = ad.read_h5ad(path, backed="r")
        rows = subset["source_row"].astype(int).to_numpy()
        var_index = pd.Index(adata.var_names.astype(str)).get_indexer(feature_names)
        if (var_index < 0).any():
            adata.file.close()
            raise ValueError(f"feature alignment failed for {path}")
        values = adata.X[rows, :]
        values = values[:, var_index]
        matrix = sparse.csr_matrix(values, dtype=np.float32)
        matrices.append(matrix)
        observed_order.extend(subset["cell_id"].astype(str).tolist())
        adata.file.close()
    if observed_order != selected["cell_id"].astype(str).tolist():
        raise ValueError("selected expression order does not match metadata order")
    return sparse.vstack(matrices, format="csr")


def top_variable_features(matrix: sparse.csr_matrix, max_features: int) -> np.ndarray:
    mean = np.asarray(matrix.mean(axis=0)).ravel()
    mean_sq = np.asarray(matrix.power(2).mean(axis=0)).ravel()
    variance = np.maximum(mean_sq - mean**2, 0.0)
    nonzero = np.flatnonzero(variance > 0)
    if len(nonzero) <= max_features:
        return nonzero
    order = np.argsort(variance[nonzero], kind="stable")[-max_features:]
    return np.sort(nonzero[order])


def write_expression(
    matrix: sparse.csr_matrix,
    features: list[str],
    cells: list[str],
    path: Path,
) -> None:
    frame = pd.DataFrame(
        matrix.T.toarray(),
        index=make_unique(features),
        columns=cells,
    )
    frame.to_csv(path, sep="\t", compression="gzip")


def prepare_candidate(
    candidate: pd.Series,
    files: list[Path],
    args: argparse.Namespace,
) -> tuple[dict | None, str]:
    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    for path in files:
        frame, error = metadata_from_file(path, candidate)
        if frame is not None:
            frames.append(frame)
        else:
            errors.append(f"{path.name}: {error}")
    if not frames:
        return None, "; ".join(errors) or "no readable files"

    metadata_full = pd.concat(frames, ignore_index=True)
    metadata_full = add_block_groups(metadata_full, str(candidate["experiment_mode"]))
    selected = choose_balanced(metadata_full, args.max_per_label, args.min_per_label)
    if len(selected) < 200 or selected["label"].nunique() < 2:
        return None, f"too few eligible cells ({len(selected)}) or labels ({selected['label'].nunique()})"
    if selected["fov_group"].nunique() < 2:
        return None, f"too few validation groups ({selected['fov_group'].nunique()})"

    used_paths = sorted(
        [path for path in files if str(path) in set(selected["source_file"])],
        key=lambda path: str(path),
    )
    feature_names = common_features(used_paths)
    if len(feature_names) < 20:
        return None, f"too few common expression features ({len(feature_names)})"
    matrix = read_selected_expression(selected, used_paths, feature_names)
    feature_index = top_variable_features(matrix, args.max_features)
    if len(feature_index) < 20:
        return None, f"too few variable expression features ({len(feature_index)})"
    matrix = matrix[:, feature_index]
    selected_features = [feature_names[index] for index in feature_index]

    dataset_name = str(candidate["dataset_name"])
    dataset_id = f"SODB_{safe_id(dataset_name)}_EXPANDED"
    output_dir = args.prepared_root / dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)
    expression_path = output_dir / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata_path = output_dir / f"{dataset_id}_expanded_metadata.tsv"
    summary_path = output_dir / f"{dataset_id}_expanded_summary.json"

    metadata = selected[
        [
            "cell_id",
            "label",
            "fov_group",
            "x",
            "y",
            "source_experiment",
            "source_obs_name",
        ]
    ].copy()
    metadata["task_type"] = str(candidate["task_type"])
    metadata["label_evidence"] = str(candidate["label_evidence"])
    metadata.to_csv(metadata_path, sep="\t", index=False)
    write_expression(
        matrix,
        selected_features,
        metadata["cell_id"].astype(str).tolist(),
        expression_path,
    )

    summary = {
        "dataset_id": dataset_id,
        "source_dataset_id": f"SODB:{dataset_name}",
        "dataset_name": dataset_name,
        "task_type": str(candidate["task_type"]),
        "label_evidence": str(candidate["label_evidence"]),
        "label_col": str(candidate["label_col"]),
        "experiment_mode": str(candidate["experiment_mode"]),
        "n_source_files": len(used_paths),
        "source_files": [str(path) for path in used_paths],
        "n_cells_full": int(len(metadata_full)),
        "n_features_full_common": int(len(feature_names)),
        "expanded_cells": int(matrix.shape[0]),
        "expanded_features": int(matrix.shape[1]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "label_counts": metadata["label"].value_counts().to_dict(),
        "file_errors": errors,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    row = {
        "dataset_id": dataset_id,
        "source_dataset_id": summary["source_dataset_id"],
        "modality": "SODB_spatial_transcriptomics",
        "biological_context": (
            f"SODB {dataset_name}; {candidate['task_type']}; "
            f"label evidence={candidate['label_evidence']}"
        ),
        "sampling": (
            f"balanced labels, max_per_label={args.max_per_label}; "
            f"label_col={candidate['label_col']}; experiment_mode={candidate['experiment_mode']}"
        ),
        "n_cells_full": summary["n_cells_full"],
        "n_features_full": summary["n_features_full_common"],
        "expanded_cells": summary["expanded_cells"],
        "expanded_features": summary["expanded_features"],
        "n_labels": summary["n_labels"],
        "n_fov_groups": summary["n_fov_groups"],
        "expression_path": str(expression_path.resolve()),
        "metadata_path": str(metadata_path.resolve()),
        "cell_id_col": "cell_id",
        "label_col": "label",
        "group_col": "fov_group",
        "x_col": "x",
        "y_col": "y",
    }
    return row, ""


def update_registry(path: Path, rows: list[dict]) -> None:
    registry = pd.read_csv(path) if path.exists() else pd.DataFrame()
    ids = {row["dataset_id"] for row in rows}
    if not registry.empty:
        registry = registry.loc[~registry["dataset_id"].isin(ids)]
    registry = pd.concat([registry, pd.DataFrame(rows)], ignore_index=True)
    registry.to_csv(path, index=False)


def main() -> None:
    args = parse_args()
    candidates = pd.read_csv(args.candidates).fillna("")
    candidates = candidates.loc[
        candidates["include_primary"].astype(str).str.lower().eq("yes")
    ].copy()
    if args.only:
        requested = {item.strip() for item in args.only.split(",") if item.strip()}
        candidates = candidates.loc[candidates["dataset_name"].isin(requested)]
    audit = pd.read_csv(args.audit).fillna("")
    inventory = pd.read_csv(args.inventory).fillna("")
    prepared_rows: list[dict] = []
    status_rows: list[dict] = []

    for _, candidate in candidates.iterrows():
        name = str(candidate["dataset_name"])
        print(f"prepare_start={name}", flush=True)
        files, download_errors = selected_files(candidate, audit, inventory, args)
        if files:
            try:
                row, error = prepare_candidate(candidate, files, args)
            except Exception as exc:
                row, error = None, f"{type(exc).__name__}: {exc}"
        else:
            row, error = None, "no files"
        if row is not None:
            prepared_rows.append(row)
        status_rows.append(
            {
                "dataset_name": name,
                "task_type": candidate["task_type"],
                "prepared": row is not None,
                "dataset_id": row["dataset_id"] if row is not None else "",
                "n_files": len(files),
                "error": "; ".join(download_errors + ([error] if error else [])),
            }
        )
        print(
            f"prepare_done={name} prepared={row is not None} files={len(files)} error={error}",
            flush=True,
        )

    if prepared_rows:
        update_registry(args.registry, prepared_rows)
    status = pd.DataFrame(status_rows)
    status.to_csv(ROOT / "SODB_PREPARATION_STATUS.csv", index=False)
    print(status.to_string(index=False, max_colwidth=120))
    print(
        json.dumps(
            {
                "requested": int(len(candidates)),
                "prepared": int(status["prepared"].sum()),
                "failed": int((~status["prepared"]).sum()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
