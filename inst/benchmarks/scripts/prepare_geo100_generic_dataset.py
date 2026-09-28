from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import tarfile
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import sparse
from scipy.io import mmread


ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "EXPANDED_SCALE_DATASETS.csv"
DEFAULT_DOWNLOAD_ROOT = Path(os.environ.get("NICHETYPER_GEO100_ROOT", r"D:\NicheTypeR_GEO_100_QUEUE"))
DEFAULT_PREPARED_ROOT = DEFAULT_DOWNLOAD_ROOT / "prepared"
SEED = 20260725

LABEL_PRIORITY = [
    "manual_anno",
    "predicted_labels",
    "majority_voting",
    "coarse_cell_type",
    "cell_type",
    "celltype",
    "cell.type",
    "cell_type_final",
    "ct",
    "insitutypeids",
    "insitu_type",
    "annotation",
    "anno",
    "annot",
    "label",
    "class",
    "subclass",
    "cluster",
    "leiden",
    "louvain",
    "region",
    "domain",
    "zone",
    "tls",
]
BAD_LABELS = {
    "",
    "nan",
    "none",
    "na",
    "unknown",
    "ambiguous",
    "unassigned",
    "other",
    "others",
    "low quality",
    "low_quality",
    "discard",
}
LABEL_ALIASES_BY_ACCESSION = {
    "GSE308167": {
        "B_mem": "B cell",
        "B_naive": "B cell",
        "B_activated": "B cell",
        "B_Cycling": "B cell",
        "B_plasma": "B cell",
        "B_GC": "B cell",
        "Other B cells": "B cell",
        "Large B cells": "B cell",
        "T_CD4+": "T cell",
        "T_CD8+": "T cell",
        "T_Treg": "T cell",
        "T_CD4+_naive": "T cell",
        "T_CD8+_naive": "T cell",
        "T cells": "T cell",
        "NK": "NK cell",
        "NK cells": "NK cell",
        "NKT": "NKT cell",
        "NKT cells": "NKT cell",
        "DC": "dendritic cell",
        "Dendritic cells": "dendritic cell",
        "Endo": "endothelial cell",
        "Endothelial cells": "endothelial cell",
        "Monocytes": "monocyte",
        "Macrophages": "macrophage",
    }
}
IMMUNE_RECEPTOR_RE = re.compile(
    r"(filtered[_-]?contig|all[_-]?contig|contig[_-]?annotations?|consensus[_-]?annotations?|"
    r"vdj[_-]?[bt]?|bcr|tcr|clonotype|airr)",
    re.I,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare one downloaded GEO accession as a NicheTypeR benchmark if possible.")
    parser.add_argument("--accession", required=True)
    parser.add_argument("--download-root", default=str(DEFAULT_DOWNLOAD_ROOT))
    parser.add_argument("--prepared-root", default=str(DEFAULT_PREPARED_ROOT))
    parser.add_argument("--max-per-label", type=int, default=2500)
    parser.add_argument("--min-per-label", type=int, default=25)
    parser.add_argument("--max-features", type=int, default=2000)
    return parser.parse_args()


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()


def write_gzip_tsv(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as handle:
        df.to_csv(handle, sep="\t")
    tmp.replace(path)


def read_gzip_parquet(path: Path) -> pd.DataFrame:
    with gzip.open(path, "rb") as handle:
        payload = handle.read()
    return pq.read_table(pa.BufferReader(payload)).to_pandas()


def read_csv_maybe_tar(path: Path, **kwargs) -> pd.DataFrame:
    try:
        if tarfile.is_tarfile(path):
            with tarfile.open(path, "r:*") as tar:
                members = [
                    member
                    for member in tar.getmembers()
                    if member.isfile() and re.search(r"\.(csv|tsv|txt)$", member.name, re.I)
                ]
                if not members:
                    members = [member for member in tar.getmembers() if member.isfile()]
                if not members:
                    raise ValueError(f"no tabular file inside {path}")
                handle = tar.extractfile(members[0])
                if handle is None:
                    raise ValueError(f"could not extract {members[0].name} from {path}")
                return pd.read_csv(handle, **kwargs)
    except tarfile.TarError:
        pass
    return pd.read_csv(path, **kwargs)


def read_table_auto(path: Path, **kwargs) -> pd.DataFrame:
    if path.name.endswith(".parquet.gz"):
        df = read_gzip_parquet(path)
        if kwargs.get("dtype") is str:
            return df.astype(str)
        return df
    if "sep" not in kwargs:
        kwargs["sep"] = "\t" if re.search(r"\.(tsv|txt)(\.gz)?$", path.name, re.I) else ","
    return read_csv_maybe_tar(path, **kwargs)


def clean_label_mask(labels: pd.Series) -> pd.Series:
    values = labels.astype(str).str.strip()
    return ~values.str.lower().isin(BAD_LABELS) & ~values.str.fullmatch(r"[A-Za-z]", na=False)


def label_score(series: pd.Series, allow_numeric: bool = False) -> tuple[bool, int]:
    clean = series.astype(str).str.strip()
    clean = clean[~clean.str.lower().isin(BAD_LABELS) & ~clean.str.fullmatch(r"[A-Za-z]", na=False)]
    n_unique = int(clean.nunique())
    n = int(clean.shape[0])
    if n_unique < 2:
        return False, n_unique
    numeric_fraction = pd.to_numeric(clean, errors="coerce").notna().mean()
    if not allow_numeric and numeric_fraction > 0.9:
        return False, n_unique
    if n_unique > min(300, max(20, int(n * 0.5))):
        return False, n_unique
    return True, n_unique


def pick_label_col(df: pd.DataFrame, allow_numeric: bool = False) -> tuple[str | None, dict[str, int]]:
    candidates = {}
    lower_to_col = {str(col).lower(): str(col) for col in df.columns}
    level_columns = []
    for col in df.columns:
        match = re.fullmatch(r"level[_ .-]?(\d+)[_ .-]?annotations?", str(col), re.I)
        if match:
            ok, n_unique = label_score(df[col], allow_numeric=allow_numeric)
            if ok:
                candidates[str(col)] = n_unique
                level_columns.append((int(match.group(1)), str(col)))
    if level_columns:
        level_columns.sort(reverse=True)
        return level_columns[0][1], candidates
    for preferred in LABEL_PRIORITY:
        for lower, col in lower_to_col.items():
            if preferred == lower or (len(preferred) > 3 and preferred in lower):
                ok, n_unique = label_score(df[col], allow_numeric=allow_numeric)
                if ok:
                    candidates[col] = n_unique
    if candidates:
        for preferred in LABEL_PRIORITY:
            matching = [
                col
                for col in candidates
                if preferred == col.lower() or (len(preferred) > 3 and preferred in col.lower())
            ]
            if matching:
                matching.sort(
                    key=lambda col: (
                        1.0 - pd.to_numeric(df[col], errors="coerce").notna().mean(),
                        candidates[col],
                    ),
                    reverse=True,
                )
                return matching[0], candidates
    return None, candidates


def pick_id_col(df: pd.DataFrame) -> str | None:
    for col in [
        "singlesample_cell_id",
        "cell_barcode",
        "cell_id",
        "cell_ID",
        "Cell_ID",
        "barcode",
        "cell",
        "CellID",
        "cellID",
    ]:
        if col in df.columns:
            return col
    for col in df.columns:
        if re.search(r"cell.*(id|barcode)|barcode", str(col), re.I):
            return str(col)
    return None


def pick_coord_cols(df: pd.DataFrame) -> tuple[str | None, str | None]:
    pairs = [
        ("x_centroid", "y_centroid"),
        ("x_FOV_px", "y_FOV_px"),
        ("x_slide_mm", "y_slide_mm"),
        ("x", "y"),
        ("X", "Y"),
        ("center_x", "center_y"),
        ("x_tform", "y_tform"),
        ("x_pos", "y_pos"),
        ("CenterX_global_px", "CenterY_global_px"),
        ("CenterX_local_px", "CenterY_local_px"),
        ("array_col", "array_row"),
    ]
    for x_col, y_col in pairs:
        if x_col in df.columns and y_col in df.columns:
            return x_col, y_col
    x_like = [
        col
        for col in df.columns
        if re.search(r"(^x$|x_centroid|centerx|coord.*x|^x[_\.].*(px|mm)$)", str(col), re.I)
    ]
    y_like = [
        col
        for col in df.columns
        if re.search(r"(^y$|y_centroid|centery|coord.*y|^y[_\.].*(px|mm)$)", str(col), re.I)
    ]
    if x_like and y_like:
        return str(x_like[0]), str(y_like[0])
    return None, None


def choose_balanced(metadata: pd.DataFrame, max_per_label: int, min_per_label: int) -> list[str]:
    rng = np.random.default_rng(SEED)
    clean = metadata.loc[clean_label_mask(metadata["label"])].copy()
    counts = clean["label"].value_counts()
    keep_labels = set(counts[counts >= min_per_label].index.astype(str))
    clean = clean.loc[clean["label"].isin(keep_labels)].copy()
    chosen: list[str] = []
    for _, group in clean.groupby("label", sort=True):
        cells = group["cell_id"].astype(str).to_numpy()
        if len(cells) > max_per_label:
            cells = rng.choice(cells, size=max_per_label, replace=False)
        chosen.extend(map(str, cells))
    return sorted(chosen)


def feature_names(features: pd.DataFrame) -> list[str]:
    names = features.iloc[:, 1].astype(str).tolist() if features.shape[1] >= 2 else features.iloc[:, 0].astype(str).tolist()
    seen: dict[str, int] = {}
    out = []
    for idx, name in enumerate(names):
        clean = re.sub(r"\s+", "_", str(name).strip()) or f"feature_{idx + 1}"
        if clean in seen:
            seen[clean] += 1
            clean = f"{clean}_{seen[clean]}"
        else:
            seen[clean] = 1
        out.append(clean)
    return out


def clean_feature_names(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for idx, name in enumerate(names):
        clean = re.sub(r"\s+", "_", str(name).strip()) or f"feature_{idx + 1}"
        if clean in seen:
            seen[clean] += 1
            clean = f"{clean}_{seen[clean]}"
        else:
            seen[clean] = 1
        out.append(clean)
    return out


def expression_feature_subset(expr: pd.DataFrame, max_features: int) -> pd.DataFrame:
    if expr.shape[0] <= max_features:
        return expr
    means = expr.mean(axis=1).sort_values(ascending=False)
    keep = sorted(means.head(max_features).index.astype(str))
    return expr.loc[keep]


def try_import_anndata():
    try:
        import anndata as ad  # type: ignore

        return ad, None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def decode_h5_values(values) -> list:
    arr = np.asarray(values)
    out = []
    for value in arr:
        if isinstance(value, bytes):
            out.append(value.decode("utf-8", errors="replace"))
        else:
            out.append(value.item() if hasattr(value, "item") else value)
    return out


def read_h5ad_column_light(node) -> list:
    if hasattr(node, "keys") and "codes" in node.keys() and "categories" in node.keys():
        codes = np.asarray(node["codes"][()])
        categories = decode_h5_values(node["categories"][()])
        return [categories[int(code)] if int(code) >= 0 and int(code) < len(categories) else "" for code in codes]
    return decode_h5_values(node[()])


def read_h5ad_dataframe_light(group) -> pd.DataFrame:
    index_key = group.attrs.get("_index", "_index")
    if isinstance(index_key, bytes):
        index_key = index_key.decode("utf-8", errors="replace")
    column_order = group.attrs.get("column-order", [])
    columns = [col.decode("utf-8", errors="replace") if isinstance(col, bytes) else str(col) for col in column_order]
    keys = [key for key in [str(index_key), *columns] if key in group.keys()]
    data = {key: read_h5ad_column_light(group[key]) for key in keys}
    df = pd.DataFrame(data)
    if str(index_key) in df.columns:
        df.index = df[str(index_key)].astype(str)
    return df


def read_h5ad_matrix_light(h5, row_index: np.ndarray):
    x = h5["X"]
    if hasattr(x, "keys"):
        encoding = x.attrs.get("encoding-type", "")
        if isinstance(encoding, bytes):
            encoding = encoding.decode("utf-8", errors="replace")
        shape = tuple(map(int, x.attrs.get("shape", x.get("shape", [0, 0]))))
        data = x["data"][()]
        indices = x["indices"][()]
        indptr = x["indptr"][()]
        if encoding == "csc_matrix":
            mat = sparse.csc_matrix((data, indices, indptr), shape=shape)
        else:
            mat = sparse.csr_matrix((data, indices, indptr), shape=shape)
        return mat[row_index, :]
    return np.asarray(x[row_index, :])


def prepare_h5ad_light(accession: str, raw: Path, prepared_root: Path, max_per_label: int, min_per_label: int, max_features: int) -> tuple[str | None, str]:
    try:
        import h5py  # type: ignore
    except Exception as exc:
        return None, f"h5ad unavailable: anndata import failed and h5py unavailable ({type(exc).__name__}: {exc})"

    for path in sorted(raw.glob("*.h5ad")):
        try:
            with h5py.File(path, "r") as h5:
                if "obs" not in h5 or "var" not in h5 or "X" not in h5:
                    continue
                obs = read_h5ad_dataframe_light(h5["obs"])
                label_col, _ = pick_label_col(obs)
                if label_col is None:
                    continue
                has_spatial = "obsm" in h5 and "spatial" in h5["obsm"]
                x_col, y_col = pick_coord_cols(obs)
                if not has_spatial and not (x_col and y_col):
                    continue
                obs["source_cell_id"] = obs.index.astype(str)
                obs["cell_id"] = path.stem + "::" + obs["source_cell_id"].astype(str)
                obs["label"] = obs[label_col].astype(str)
                if has_spatial:
                    coords = np.asarray(h5["obsm"]["spatial"], dtype=float)
                    obs["x"] = coords[:, 0]
                    obs["y"] = coords[:, 1]
                else:
                    obs["x"] = pd.to_numeric(obs[x_col], errors="coerce")
                    obs["y"] = pd.to_numeric(obs[y_col], errors="coerce")
                obs["sample_id"] = path.stem
                obs["fov_group"] = spatial_blocks(obs["x"], obs["y"], bins=8)
                obs["source_accession"] = accession
                metadata_full = obs.dropna(subset=["x", "y"]).copy()
                selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
                if len(selected_cells) < 200 or metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique() < 2:
                    continue
                selected_obs_names = [cell.split("::", 1)[1] for cell in selected_cells]
                obs_index = pd.Index(obs.index.astype(str)).get_indexer(selected_obs_names)
                if np.any(obs_index < 0):
                    continue
                mat = read_h5ad_matrix_light(h5, obs_index)
                dense = mat.toarray() if sparse.issparse(mat) else np.asarray(mat)
                var = read_h5ad_dataframe_light(h5["var"])
                feature_ids = list(map(str, var.index))
                expr = pd.DataFrame(dense.T, index=feature_ids, columns=selected_cells)
                expr = expression_feature_subset(expr, max_features)
                metadata = metadata_full.set_index("cell_id", drop=False).loc[selected_cells].reset_index(drop=True)
        except Exception:
            continue

        dataset_id = f"GEO_{accession}_GENERIC_H5AD_EXPANDED"
        out = prepared_root / dataset_id
        out.mkdir(parents=True, exist_ok=True)
        meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
        expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
        metadata.to_csv(meta_path, sep="\t", index=False)
        write_gzip_tsv(expr, expr_path)
        summary = {
            "dataset_id": dataset_id,
            "source_accession": accession,
            "parser": "generic_h5ad_light_spatial_label_parser",
            "label_col": label_col,
            "n_cells_full": int(metadata_full.shape[0]),
            "n_features_full": int(len(feature_ids)),
            "expanded_cells": int(expr.shape[1]),
            "expanded_features": int(expr.shape[0]),
            "n_labels": int(metadata["label"].nunique()),
            "n_fov_groups": int(metadata["fov_group"].nunique()),
            "label_counts": metadata["label"].value_counts().to_dict(),
        }
        (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic h5ad light parser")
        return dataset_id, "prepared generic h5ad spatial-label dataset with light h5py parser"

    return None, "no h5ad with both spatial coordinates and usable label column"


def spatial_blocks(x: pd.Series, y: pd.Series, bins: int = 8) -> pd.Series:
    x_rank = x.rank(method="first")
    y_rank = y.rank(method="first")
    x_bin = pd.qcut(x_rank, q=min(bins, x_rank.nunique()), labels=False, duplicates="drop")
    y_bin = pd.qcut(y_rank, q=min(bins, y_rank.nunique()), labels=False, duplicates="drop")
    return "block_" + x_bin.astype(str) + "_" + y_bin.astype(str)


def annotation_base(path: Path) -> str:
    name = path.name
    name = re.sub(r"(_TLS)?_annotations?\.csv\.gz$", "", name, flags=re.I)
    return name


def find_one(raw: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        hits = sorted(raw.glob(pattern))
        if hits:
            return hits[0]
    return None


def tenx_h5_base(path: Path) -> str:
    name = path.name
    name = re.sub(r"_(filtered|raw)[_-]feature[_-]bc[_-]matrix\.h5(\.gz)?$", "", name, flags=re.I)
    name = re.sub(r"_(filtered|raw)_feature_bc_matrix\.h5(\.gz)?$", "", name, flags=re.I)
    name = re.sub(r"\.h5(\.gz)?$", "", name, flags=re.I)
    return name


def annotation_family(base: str, path: Path) -> str:
    stem = drop_table_suffix(path.name)
    if stem.lower().startswith(base.lower()):
        stem = stem[len(base):]
    stem = re.sub(r"^[_\-.]+", "", stem)
    return stem or "annotation"


def discover_visium_10x_h5_like(raw: Path) -> list[dict]:
    samples = []
    for matrix_path in sorted(raw.glob("*filtered*feature*bc*matrix.h5")):
        base = tenx_h5_base(matrix_path)
        position_path = find_one(
            raw,
            [
                f"{base}*tissue_positions*.csv.gz",
                f"{base}*tissue_positions*.csv",
                f"{base}*positions*.csv.gz",
                f"{base}*positions*.csv",
                f"{base}*spatial*.csv.gz",
                f"{base}*spatial*.csv",
            ],
        )
        if position_path is None:
            continue
        ann_paths = [
            path
            for path in sorted(raw.glob(f"{base}*annotation*.csv*"))
            if path.is_file() and not IMMUNE_RECEPTOR_RE.search(path.name)
        ]
        if not ann_paths:
            ann_paths = [
                path
                for path in sorted(raw.glob(f"{base}*label*.csv*"))
                if path.is_file() and not IMMUNE_RECEPTOR_RE.search(path.name)
            ]
        if not ann_paths:
            continue
        samples.append(
            {
                "base": base,
                "matrix": matrix_path,
                "positions": position_path,
                "annotations": {annotation_family(base, path): path for path in ann_paths},
            }
        )
    return samples


def read_10x_h5(path: Path) -> tuple[sparse.csc_matrix, list[str], list[str]]:
    import h5py  # type: ignore

    with h5py.File(path, "r") as h5:
        group = h5["matrix"]
        data = group["data"][()]
        indices = group["indices"][()]
        indptr = group["indptr"][()]
        shape = tuple(map(int, group["shape"][()]))
        barcodes = [
            value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
            for value in group["barcodes"][()]
        ]
        features_group = group["features"]
        feature_node = features_group["name"] if "name" in features_group else features_group["id"]
        features = [
            value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
            for value in feature_node[()]
        ]
    return sparse.csc_matrix((data, indices, indptr), shape=shape), barcodes, clean_feature_names(features)


def read_10x_barcodes_features(path: Path) -> tuple[list[str], list[str]]:
    import h5py  # type: ignore

    with h5py.File(path, "r") as h5:
        group = h5["matrix"]
        barcodes = [
            value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
            for value in group["barcodes"][()]
        ]
        features_group = group["features"]
        feature_node = features_group["name"] if "name" in features_group else features_group["id"]
        features = [
            value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
            for value in feature_node[()]
        ]
    return barcodes, clean_feature_names(features)


def load_tissue_positions(path: Path) -> pd.DataFrame:
    table = read_table_auto(path, dtype=str)
    lower = {str(col).lower(): str(col) for col in table.columns}
    if "barcode" not in lower and table.shape[1] >= 6:
        table = read_table_auto(path, dtype=str, header=None)
        table = table.iloc[:, :6]
        table.columns = [
            "barcode",
            "in_tissue",
            "array_row",
            "array_col",
            "pxl_row_in_fullres",
            "pxl_col_in_fullres",
        ]
    lower = {str(col).lower(): str(col) for col in table.columns}
    barcode_col = lower.get("barcode") or lower.get("cell_barcode") or pick_id_col(table) or str(table.columns[0])
    x_col = lower.get("pxl_col_in_fullres") or lower.get("imagecol") or lower.get("array_col")
    y_col = lower.get("pxl_row_in_fullres") or lower.get("imagerow") or lower.get("array_row")
    if x_col is None or y_col is None:
        x_col, y_col = pick_coord_cols(table)
    if x_col is None or y_col is None:
        raise ValueError(f"no coordinate columns in {path}")
    out = pd.DataFrame(
        {
            "barcode": table[barcode_col].astype(str),
            "x": pd.to_numeric(table[x_col], errors="coerce"),
            "y": pd.to_numeric(table[y_col], errors="coerce"),
        }
    )
    if "in_tissue" in lower:
        in_tissue = table[lower["in_tissue"]].astype(str).str.lower()
        out = out.loc[in_tissue.isin({"1", "true", "yes"})].copy()
    return out.dropna(subset=["x", "y"]).drop_duplicates("barcode")


def pick_annotation_label_col(df: pd.DataFrame, id_col: str | None) -> str | None:
    label_col, _ = pick_label_col(df)
    if label_col is not None:
        return label_col
    excluded = {
        str(id_col).lower() if id_col else "",
        "barcode",
        "cell_barcode",
        "cell_id",
        "spot",
        "x",
        "y",
        "array_row",
        "array_col",
        "pxl_row_in_fullres",
        "pxl_col_in_fullres",
        "imagerow",
        "imagecol",
    }
    scored = []
    for col in df.columns:
        col_text = str(col)
        if col_text.lower() in excluded:
            continue
        ok, n_unique = label_score(df[col])
        if not ok:
            continue
        numeric = pd.to_numeric(df[col], errors="coerce").notna().mean() > 0.95
        name_bonus = 1 if re.search(r"annotation|label|type|class|cluster|region|domain|zone|tls|tumou?r", col_text, re.I) else 0
        if numeric and not name_bonus:
            continue
        scored.append((name_bonus, -n_unique, col_text))
    if not scored:
        return None
    scored.sort(reverse=True)
    return scored[0][2]


def discover_xenium_like(raw: Path) -> list[dict]:
    samples = []
    annotation_paths = {
        *raw.glob("*annotation*.csv.gz"),
        *raw.glob("*metadata*.csv.gz"),
        *raw.glob("*Metadata*.txt.gz"),
        *raw.glob("*metadata*.txt.gz"),
    }
    for ann_path in sorted(annotation_paths):
        if IMMUNE_RECEPTOR_RE.search(ann_path.name):
            continue
        annotation_stem = annotation_base(ann_path)
        gsm_match = re.match(r"^(GSM\d+)", ann_path.name, flags=re.I)
        bases = [annotation_stem]
        if gsm_match and gsm_match.group(1) not in bases:
            bases.append(gsm_match.group(1))
        base = bases[0]
        matrix_path = barcodes_path = features_path = h5_path = cells_path = None
        for candidate_base in bases:
            matrix_path = find_one(raw, [f"{candidate_base}*cell_feature_matrix_matrix.mtx.gz", f"{candidate_base}*matrix.mtx.gz"])
            barcodes_path = find_one(raw, [f"{candidate_base}*cell_feature_matrix_barcodes.tsv.gz", f"{candidate_base}*barcodes.tsv.gz"])
            features_path = find_one(raw, [f"{candidate_base}*cell_feature_matrix_features.tsv.gz", f"{candidate_base}*features.tsv.gz", f"{candidate_base}*genes.tsv.gz"])
            h5_path = find_one(raw, [f"{candidate_base}*cell_feature_matrix.h5"])
            cells_path = find_one(
                raw,
                [
                    f"{candidate_base}*cells.parquet.gz",
                    f"{candidate_base}*metadata*.csv.gz",
                    f"{candidate_base}*cell_boundaries.csv.gz",
                ],
            )
            if cells_path and (h5_path or (matrix_path and barcodes_path and features_path)):
                base = candidate_base
                break
        matrix_kind = "h5" if h5_path else "mtx"
        complete_matrix = bool(h5_path or (matrix_path and barcodes_path and features_path))
        if complete_matrix and cells_path:
            samples.append(
                {
                    "base": base,
                    "annotation": ann_path,
                    "matrix": h5_path or matrix_path,
                    "barcodes": barcodes_path,
                    "features": features_path,
                    "cells": cells_path,
                    "matrix_kind": matrix_kind,
                }
            )
    return samples


def load_cell_table(path: Path) -> pd.DataFrame:
    if path.name.endswith(".parquet.gz"):
        return read_gzip_parquet(path)
    table = read_csv_maybe_tar(path, dtype=str)
    if {"cell_id", "vertex_x", "vertex_y"}.issubset(table.columns):
        table["vertex_x"] = pd.to_numeric(table["vertex_x"], errors="coerce")
        table["vertex_y"] = pd.to_numeric(table["vertex_y"], errors="coerce")
        table = (
            table.dropna(subset=["vertex_x", "vertex_y"])
            .groupby("cell_id", as_index=False)
            .agg(x_centroid=("vertex_x", "mean"), y_centroid=("vertex_y", "mean"))
        )
    return table


def cosmx_csv_base(path: Path, suffix: str) -> str:
    return re.sub(re.escape(suffix) + r"$", "", path.name, flags=re.I)


def cosmx_cell_component(values: pd.Series) -> pd.Series:
    text = values.astype(str)
    composite = text.str.startswith("c_")
    result = text.copy()
    result.loc[composite] = text.loc[composite].str.rsplit("_", n=1).str[-1]
    return result


def discover_cosmx_csv_like(raw: Path) -> list[dict]:
    samples = []
    for expr_path in sorted(raw.glob("*exprMat_file.csv.gz")):
        base = cosmx_csv_base(expr_path, "_exprMat_file.csv.gz")
        metadata_candidates = [
            raw / f"{base}_metadata_for_seurat.csv.gz",
            raw / f"{base}_metadata_file.csv.gz",
        ]
        metadata_path = next((path for path in metadata_candidates if path.exists()), None)
        if metadata_path is not None:
            samples.append({"base": base, "expression": expr_path, "metadata": metadata_path})
    return samples


def discover_cosmx_tsv_like(raw: Path) -> list[dict]:
    samples: dict[str, dict] = {}
    for path in sorted(raw.glob("GSM*_*.tsv.gz")):
        match = re.match(r"^(GSM\d+)_(CellClusters|Cells|Counts)-", path.name, flags=re.I)
        if not match:
            continue
        gsm, kind = match.group(1), match.group(2).lower()
        samples.setdefault(gsm, {"base": gsm})[kind] = path
    return [
        item
        for item in samples.values()
        if {"cellclusters", "cells", "counts"}.issubset(item)
    ]


def table_row_ids(df: pd.DataFrame) -> pd.Series:
    if not isinstance(df.index, pd.RangeIndex):
        return pd.Series(df.index.astype(str), index=df.index)
    id_col = pick_id_col(df)
    if id_col is not None:
        return df[id_col].astype(str)
    return pd.Series(df.index.astype(str), index=df.index)


def prepare_cosmx_tsv_like(
    accession: str,
    raw: Path,
    prepared_root: Path,
    max_per_label: int,
    min_per_label: int,
    max_features: int,
) -> tuple[str | None, str]:
    samples = discover_cosmx_tsv_like(raw)
    if not samples:
        return None, "no complete Counts/Cells/CellClusters TSV samples"

    meta_parts = []
    counts_by_base: dict[str, pd.DataFrame] = {}
    for item in samples:
        try:
            counts = read_table_auto(item["counts"])
            cells = read_table_auto(item["cells"])
            clusters = read_table_auto(item["cellclusters"], dtype=str)
        except Exception:
            continue
        x_col, y_col = pick_coord_cols(cells)
        label_col = pick_label_col(clusters)[0]
        cluster_id_col = pick_id_col(clusters) or ("Cell" if "Cell" in clusters.columns else None)
        if x_col is None or y_col is None or label_col is None or cluster_id_col is None:
            continue

        count_ids = table_row_ids(counts).astype(str)
        cell_ids = table_row_ids(cells).astype(str)
        count_map = {cell_id: idx for idx, cell_id in enumerate(count_ids)}
        cell_map = {cell_id: idx for idx, cell_id in enumerate(cell_ids)}
        cluster_map = dict(
            zip(clusters[cluster_id_col].astype(str), clusters[label_col].astype(str))
        )
        common_ids = sorted(set(count_map) & set(cell_map) & set(cluster_map))
        if len(common_ids) < 200:
            continue

        base = str(item["base"])
        cell_rows = cells.iloc[[cell_map[cell_id] for cell_id in common_ids]].copy()
        metadata = pd.DataFrame(
            {
                "source_cell_id": common_ids,
                "cell_id": [f"{base}::{cell_id}" for cell_id in common_ids],
                "label": [cluster_map[cell_id] for cell_id in common_ids],
                "x": pd.to_numeric(cell_rows[x_col], errors="coerce").to_numpy(),
                "y": pd.to_numeric(cell_rows[y_col], errors="coerce").to_numpy(),
            }
        ).dropna(subset=["x", "y"])
        metadata = metadata.loc[clean_label_mask(metadata["label"])].copy()
        if metadata["label"].nunique() < 2:
            continue
        metadata["sample_id"] = base
        metadata["fov_group"] = base + "::" + spatial_blocks(metadata["x"], metadata["y"], bins=8).astype(str)
        metadata["source_accession"] = accession
        meta_parts.append(metadata)

        counts = counts.iloc[[count_map[cell_id] for cell_id in common_ids]].copy()
        counts.index = common_ids
        counts_by_base[base] = counts

    if not meta_parts:
        return None, "TSV triples found but no expression/coordinate/label intersection"

    metadata_full = pd.concat(meta_parts, ignore_index=True)
    selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
    if len(selected_cells) < 200:
        return None, "too few selected labeled cells after TSV filtering"

    pieces = []
    for base, counts in counts_by_base.items():
        selected_source = [
            cell.split("::", 1)[1]
            for cell in selected_cells
            if cell.startswith(base + "::")
        ]
        selected_source = [cell for cell in selected_source if cell in counts.index]
        if not selected_source:
            continue
        piece = counts.loc[selected_source].apply(pd.to_numeric, errors="coerce").fillna(0).T
        piece.columns = [f"{base}::{cell}" for cell in selected_source]
        pieces.append(piece)
    if not pieces:
        return None, "no selected TSV cells matched expression rows"

    expression = pd.concat(pieces, axis=1).fillna(0)
    available_cells = [cell for cell in selected_cells if cell in expression.columns]
    if len(available_cells) < 200:
        return None, "too few selected TSV cells matched expression"
    expression = expression.loc[:, available_cells]
    expression = expression_feature_subset(expression, max_features)
    metadata = metadata_full.set_index("cell_id", drop=False).loc[available_cells].reset_index(drop=True)

    dataset_id = f"GEO_{accession}_GENERIC_COSMX_TSV_EXPANDED"
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expression, expr_path)
    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": "generic_cosmx_counts_cells_clusters_tsv",
        "label_col": "Cluster",
        "n_cells_full": int(metadata_full.shape[0]),
        "n_features_full": int(expression.shape[0]),
        "expanded_cells": int(expression.shape[1]),
        "expanded_features": int(expression.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic CosMx TSV triple parser")
    return dataset_id, "prepared generic CosMx Counts/Cells/CellClusters TSV dataset"


GENERIC_EXPRESSION_RE = re.compile(
    r"(exprmat[_-]?file|cell[_-]?by[_-]?gene|digital[_-]?expression|normalized[_-]?matrix|"
    r"exp[_-]?mtx[_-]?count|count[_-]?matrix|counts?[_-]?and[_-]?metadata|counts?)[^\\/]*\.(csv|tsv|txt)(\.gz)?$",
    re.I,
)
GENERIC_METADATA_RE = re.compile(
    r"(metadata[_-]?file|cell[_-]?metadata|metadata|meta[_-]?data|samplemetadata)[^\\/]*"
    r"\.(csv|tsv|txt|parquet)(\.gz)?$",
    re.I,
)


def drop_table_suffix(name: str) -> str:
    return re.sub(r"\.(csv|tsv|txt|parquet)(\.gz)?$", "", name, flags=re.I)


def generic_pair_base(name: str) -> str:
    base = drop_table_suffix(name)
    base = re.sub(
        r"([_.-]?(exprmat[_-]?file|cell[_-]?by[_-]?gene|digital[_-]?expression|normalized[_-]?matrix|"
        r"exp[_-]?mtx[_-]?count|count[_-]?matrix|counts?|metadata[_-]?file|cell[_-]?metadata|"
        r"metadata|meta[_-]?data|samplemetadata))$",
        "",
        base,
        flags=re.I,
    )
    return re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").lower()


def pair_score(expr_path: Path, meta_path: Path, single_metadata: bool) -> float:
    expr_base = generic_pair_base(expr_path.name)
    meta_base = generic_pair_base(meta_path.name)
    if expr_base and expr_base == meta_base:
        return 1.0
    expr_gsm = re.match(r"^(GSM\d+)", expr_path.name)
    meta_gsm = re.match(r"^(GSM\d+)", meta_path.name)
    if expr_gsm and meta_gsm and expr_gsm.group(1) == meta_gsm.group(1):
        return 0.95
    if expr_base and meta_base and (expr_base.startswith(meta_base) or meta_base.startswith(expr_base)):
        return 0.9
    if single_metadata:
        return 0.55
    return SequenceMatcher(None, expr_base, meta_base).ratio()


def discover_generic_csv_pairs(raw: Path) -> list[dict]:
    expr_paths = [
        path
        for path in sorted(raw.iterdir())
        if path.is_file() and GENERIC_EXPRESSION_RE.search(path.name) and not IMMUNE_RECEPTOR_RE.search(path.name)
    ]
    meta_paths = [
        path
        for path in sorted(raw.iterdir())
        if path.is_file() and GENERIC_METADATA_RE.search(path.name) and not IMMUNE_RECEPTOR_RE.search(path.name)
    ]
    samples = []
    for expr_path in expr_paths:
        scored = sorted(
            ((pair_score(expr_path, meta_path, len(meta_paths) == 1), meta_path) for meta_path in meta_paths),
            key=lambda item: item[0],
            reverse=True,
        )
        if not scored or scored[0][0] < 0.5:
            continue
        meta_path = scored[0][1]
        samples.append(
            {
                "base": generic_pair_base(expr_path.name) or drop_table_suffix(expr_path.name),
                "expression": expr_path,
                "metadata": meta_path,
            }
        )
    return samples


def normalize_cell_token(value: str) -> str:
    text = str(value).strip()
    match = re.match(r"^c_(?:\d+_)+(\d+)$", text, flags=re.I)
    if match:
        return match.group(1)
    return text


def embedded_fov_cell_token(value: str) -> str | None:
    text = str(value).strip()
    match = re.match(r"^c_(?:\d+_)*(\d+)_(\d+)$", text, flags=re.I)
    if match:
        return f"{match.group(1)}::{match.group(2)}"
    return None


def source_id_from_columns(df: pd.DataFrame, id_col: str | None) -> pd.Series:
    if "fov" in df.columns and "cell_ID" in df.columns:
        raw = df["cell_ID"].astype(str).str.strip()
        fallback = df["fov"].astype(str) + "::" + df["cell_ID"].map(normalize_cell_token).astype(str)
        encoded = raw.str.match(r"^c_(?:\d+_)+\d+$", case=False, na=False)
        return raw.where(encoded, fallback).astype(str)
    if "fov" in df.columns and "cell_id" in df.columns:
        raw = df["cell_id"].astype(str).str.strip()
        fallback = df["fov"].astype(str) + "::" + df["cell_id"].map(normalize_cell_token).astype(str)
        encoded = raw.str.match(r"^c_(?:\d+_)+\d+$", case=False, na=False)
        return raw.where(encoded, fallback).astype(str)
    if id_col and id_col in df.columns:
        return df[id_col].astype(str).str.strip()
    return pd.Series(df.index.astype(str), index=df.index)


def expression_piece_from_table(expr: pd.DataFrame, base: str, selected_source: set[str]) -> pd.DataFrame | None:
    id_col = pick_id_col(expr)
    x_col, y_col = pick_coord_cols(expr)
    source = source_id_from_columns(expr, id_col)
    overlap = set(source.astype(str)) & selected_source
    if overlap:
        expr = expr.copy()
        expr["source_cell_id"] = source.astype(str)
        expr["cell_id"] = base + "::" + expr["source_cell_id"]
        exclude = {"source_cell_id", "cell_id"}
        exclude.update(str(col) for col in [id_col, x_col, y_col] if col)
        exclude.update(col for col in expr.columns if str(col).lower() in {"fov", "cell_id", "cell_id.1", "cell_id_x", "cell_id_y", "cell_id "})
        gene_cols = [col for col in expr.columns if col not in exclude]
        keep_rows = expr["source_cell_id"].astype(str).isin(selected_source)
        if not gene_cols or not keep_rows.any():
            return None
        sub = expr.loc[keep_rows, gene_cols].apply(pd.to_numeric, errors="coerce")
        sub = sub.dropna(axis=1, how="all").fillna(0)
        if sub.empty:
            return None
        sub.index = expr.loc[keep_rows, "cell_id"].astype(str).tolist()
        return sub.T

    first_col = str(expr.columns[0]) if len(expr.columns) else ""
    column_source = {col: str(col) for col in expr.columns if str(col) in selected_source}
    split_columns = []
    for col in expr.columns[1:]:
        match = re.fullmatch(r"([^_]+)_([^_]+)", str(col))
        if match:
            split_columns.append((col, match.group(1), match.group(2)))
    if split_columns and not column_source:
        as_fov_cell = sum(f"{left}::{right}" in selected_source for _, left, right in split_columns)
        as_cell_fov = sum(f"{right}::{left}" in selected_source for _, left, right in split_columns)
        swap = as_cell_fov > as_fov_cell
        for col, left, right in split_columns:
            source = f"{right}::{left}" if swap else f"{left}::{right}"
            if source in selected_source:
                column_source[col] = source
    column_overlap = list(column_source)
    if first_col and column_overlap:
        gene_ids = expr[first_col].astype(str)
        sub = expr.loc[:, column_overlap].apply(pd.to_numeric, errors="coerce").fillna(0)
        sub.index = gene_ids
        sub.columns = [base + "::" + column_source[col] for col in column_overlap]
        return sub
    return None


def discover_external_label_tables(raw: Path) -> list[dict]:
    candidates = []
    for pattern in ["*metadata*.csv.gz", "*metadata*.tsv.gz", "*metadata*.txt.gz", "*annotation*.csv.gz", "*celltype*.csv.gz"]:
        candidates.extend(sorted(raw.glob(pattern)))
    tables = []
    seen = set()
    for path in candidates:
        if path in seen or IMMUNE_RECEPTOR_RE.search(path.name) or re.search(r"celllabels|compartmentlabels", path.name, re.I):
            continue
        seen.add(path)
        if path.stat().st_size > 180_000_000:
            continue
        try:
            table = read_table_auto(path, dtype=str)
        except Exception:
            continue
        label_col, _ = pick_label_col(table)
        id_col = pick_id_col(table)
        if label_col is None:
            continue
        table = table.copy()
        table["source_cell_id"] = source_id_from_columns(table, id_col).astype(str)
        labels = table[["source_cell_id", label_col]].dropna()
        labels = labels.loc[clean_label_mask(labels[label_col])]
        labels = labels.drop_duplicates("source_cell_id", keep=False)
        if labels.empty:
            continue
        tables.append({"path": path, "label_col": label_col, "labels": labels})
    return tables


def merge_external_labels(meta: pd.DataFrame, label_tables: list[dict]) -> tuple[pd.Series | None, str | None]:
    source = meta["source_cell_id"].astype(str)
    best_series = None
    best_name = None
    best_matches = 0
    for item in label_tables:
        labels = item["labels"]
        label_map = dict(zip(labels["source_cell_id"].astype(str), labels[item["label_col"]].astype(str)))
        mapped = source.map(label_map)
        matches = int(mapped.notna().sum())
        if matches > best_matches:
            best_matches = matches
            best_series = mapped
            best_name = f"{item['path'].name}:{item['label_col']}"
    if best_series is None or best_matches < 200:
        return None, None
    ok, _ = label_score(best_series.fillna(""))
    if not ok:
        return None, None
    return best_series, best_name


def prepare_generic_csv_pair_like(
    accession: str,
    raw: Path,
    prepared_root: Path,
    max_per_label: int,
    min_per_label: int,
    max_features: int,
) -> tuple[str | None, str]:
    samples = discover_generic_csv_pairs(raw)
    if not samples:
        return None, "no generic expression/metadata CSV-like pairs"

    external_label_tables = discover_external_label_tables(raw)
    meta_parts = []
    usable_samples = []
    label_col_used = None
    for item in samples:
        try:
            meta = read_table_auto(item["metadata"], dtype=str)
        except Exception:
            continue
        label_col, _ = pick_label_col(meta)
        x_col, y_col = pick_coord_cols(meta)
        id_col = pick_id_col(meta)
        if x_col is None or y_col is None:
            continue
        base = item["base"]
        meta = meta.copy()
        meta["source_cell_id"] = source_id_from_columns(meta, id_col).astype(str)
        if label_col is None:
            merged_label, merged_name = merge_external_labels(meta, external_label_tables)
            if merged_label is None:
                continue
            meta["_merged_label"] = merged_label
            label_col = "_merged_label"
            label_col_used = merged_name
        meta["cell_id"] = base + "::" + meta["source_cell_id"]
        meta["label"] = meta[label_col].astype(str)
        meta["x"] = pd.to_numeric(meta[x_col], errors="coerce")
        meta["y"] = pd.to_numeric(meta[y_col], errors="coerce")
        meta["sample_id"] = base
        if "fov" in meta.columns:
            meta["fov_group"] = base + "::fov_" + meta["fov"].astype(str)
        else:
            meta["fov_group"] = base + "::" + spatial_blocks(meta["x"], meta["y"], bins=8).astype(str)
        meta["source_accession"] = accession
        meta = meta.dropna(subset=["x", "y"])
        if meta["label"].nunique() < 2:
            continue
        meta_parts.append(meta)
        usable_samples.append(item)
        if label_col_used is None:
            label_col_used = label_col

    if not meta_parts:
        return None, "generic CSV pairs found but no usable label/coordinate metadata"

    metadata_full = pd.concat(meta_parts, ignore_index=True)
    selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
    if len(selected_cells) < 200 or metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique() < 2:
        return None, "too few selected labeled cells after generic CSV filtering"
    selected_by_base: dict[str, set[str]] = {}
    for cell in selected_cells:
        base, source = cell.split("::", 1)
        selected_by_base.setdefault(base, set()).add(source)

    pieces = []
    for item in usable_samples:
        base = item["base"]
        selected_source = selected_by_base.get(base, set())
        if not selected_source:
            continue
        try:
            expr = read_table_auto(item["expression"])
        except Exception:
            continue
        piece = expression_piece_from_table(expr, base, selected_source)
        if piece is not None and not piece.empty:
            pieces.append(piece)
    if not pieces:
        return None, "no expression rows matched selected generic CSV metadata cells"

    expression = pd.concat(pieces, axis=1).fillna(0)
    available_cells = [cell for cell in selected_cells if cell in expression.columns]
    if len(available_cells) < 200:
        return None, "too few selected generic CSV cells matched expression columns"
    metadata = metadata_full.set_index("cell_id", drop=False).loc[available_cells].reset_index(drop=True)
    if metadata["label"].nunique() < 2:
        return None, "too few labels after matching generic CSV expression"
    expression = expression.loc[:, available_cells]
    expression = expression_feature_subset(expression, max_features)

    dataset_id = f"GEO_{accession}_GENERIC_CSV_PAIR_EXPANDED"
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expression, expr_path)

    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": "generic_csv_expression_metadata_pair",
        "label_col": label_col_used,
        "n_cells_full": int(metadata_full.shape[0]),
        "n_features_full": int(expression.shape[0]),
        "expanded_cells": int(expression.shape[1]),
        "expanded_features": int(expression.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic CSV expression+metadata pair parser")
    return dataset_id, "prepared generic CSV expression+metadata pair dataset"


def prepare_visium_10x_h5_like(
    accession: str,
    raw: Path,
    prepared_root: Path,
    max_per_label: int,
    min_per_label: int,
    max_features: int,
) -> tuple[str | None, str]:
    samples = discover_visium_10x_h5_like(raw)
    if not samples:
        return None, "no filtered 10x h5 + tissue positions + annotation samples"

    families = sorted({family for item in samples for family in item["annotations"]})
    candidates = []
    for family in families:
        meta_parts = []
        usable_samples = []
        label_col_used = None
        for item in samples:
            ann_path = item["annotations"].get(family)
            if ann_path is None:
                continue
            try:
                ann = read_table_auto(ann_path, dtype=str)
                positions = load_tissue_positions(item["positions"])
                barcodes, _ = read_10x_barcodes_features(item["matrix"])
            except Exception:
                continue
            id_col = pick_id_col(ann) or str(ann.columns[0])
            label_col = pick_annotation_label_col(ann, id_col)
            if label_col is None:
                continue
            ann = ann.copy()
            ann["_barcode"] = ann[id_col].astype(str)
            positions = positions.loc[positions["barcode"].isin(set(barcodes))].copy()
            meta = ann.merge(positions, left_on="_barcode", right_on="barcode", how="inner")
            if meta.empty:
                continue
            base = item["base"]
            meta["source_cell_id"] = meta["_barcode"].astype(str)
            meta["cell_id"] = base + "::" + meta["source_cell_id"]
            meta["label"] = meta[label_col].astype(str)
            meta["sample_id"] = base
            meta["fov_group"] = base + "::" + spatial_blocks(meta["x"], meta["y"], bins=8).astype(str)
            meta["source_accession"] = accession
            meta = meta.dropna(subset=["x", "y"])
            if meta["label"].nunique() < 2:
                continue
            meta_parts.append(meta)
            usable_samples.append(item)
            label_col_used = f"{family}:{label_col}"
        if not meta_parts:
            continue
        metadata_full = pd.concat(meta_parts, ignore_index=True)
        selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
        selected_labels = metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique()
        if len(selected_cells) < 200 or selected_labels < 2:
            continue
        candidates.append(
            {
                "family": family,
                "metadata_full": metadata_full,
                "selected_cells": selected_cells,
                "usable_samples": usable_samples,
                "label_col_used": label_col_used,
            }
        )

    if not candidates:
        return None, "10x h5 samples found but no usable annotation/coordinate merge"

    best = max(
        candidates,
        key=lambda item: (
            len(item["selected_cells"]),
            item["metadata_full"].loc[item["metadata_full"]["cell_id"].isin(item["selected_cells"]), "label"].nunique(),
            item["family"],
        ),
    )
    selected_cells = best["selected_cells"]
    selected_by_base: dict[str, set[str]] = {}
    for cell in selected_cells:
        base, barcode = cell.split("::", 1)
        selected_by_base.setdefault(base, set()).add(barcode)

    feature_maps = {}
    common_features: set[str] | None = None
    for item in best["usable_samples"]:
        try:
            _, features = read_10x_barcodes_features(item["matrix"])
        except Exception:
            continue
        feature_maps[item["base"]] = features
        common_features = set(features) if common_features is None else common_features & set(features)
    if not common_features:
        return None, "no common features across usable 10x h5 samples"
    common = sorted(common_features)

    pieces = []
    for item in best["usable_samples"]:
        base = item["base"]
        selected_source = selected_by_base.get(base, set())
        if not selected_source or base not in feature_maps:
            continue
        try:
            mat, barcodes, features = read_10x_h5(item["matrix"])
        except Exception:
            continue
        prefixed = [f"{base}::{barcode}" for barcode in barcodes]
        keep_idx = [idx for idx, cell in enumerate(prefixed) if cell in set(selected_cells)]
        if not keep_idx:
            continue
        feature_index = {feature: i for i, feature in enumerate(features)}
        feature_idx = [feature_index[feature] for feature in common if feature in feature_index]
        sub = mat[feature_idx, :][:, keep_idx]
        dense = sub.toarray() if sparse.issparse(sub) else np.asarray(sub)
        cols = [prefixed[idx] for idx in keep_idx]
        rows = [common[idx] for idx, feature in enumerate(common) if feature in feature_index]
        pieces.append(pd.DataFrame(dense, index=rows, columns=cols))
    if not pieces:
        return None, "no expression columns matched selected 10x h5 spots"

    expression = pd.concat(pieces, axis=1).fillna(0)
    available_cells = [cell for cell in selected_cells if cell in expression.columns]
    if len(available_cells) < 200:
        return None, "too few selected 10x h5 spots matched expression columns"
    metadata = best["metadata_full"].set_index("cell_id", drop=False).loc[available_cells].reset_index(drop=True)
    if metadata["label"].nunique() < 2:
        return None, "too few labels after matching 10x h5 expression"
    expression = expression.loc[:, available_cells]
    expression = expression_feature_subset(expression, max_features)

    dataset_id = f"GEO_{accession}_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED"
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expression, expr_path)

    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": "generic_visium_10x_h5_annotation",
        "label_col": best["label_col_used"],
        "n_cells_full": int(best["metadata_full"].shape[0]),
        "n_features_full": int(len(common)),
        "expanded_cells": int(expression.shape[1]),
        "expanded_features": int(expression.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic Visium 10x h5 + annotation parser")
    return dataset_id, "prepared generic Visium 10x h5 + annotation dataset"


def prepare_cosmx_csv_like(accession: str, raw: Path, prepared_root: Path, max_per_label: int, min_per_label: int, max_features: int) -> tuple[str | None, str]:
    samples = discover_cosmx_csv_like(raw)
    if not samples:
        return None, "no exprMat/metadata CSV-like samples"

    meta_parts = []
    usable_samples = []
    label_col_used = None
    for item in samples:
        try:
            meta = read_csv_maybe_tar(item["metadata"], dtype=str)
        except Exception:
            continue
        label_col, _ = pick_label_col(meta)
        x_col, y_col = pick_coord_cols(meta)
        if label_col is None or x_col is None or y_col is None:
            continue
        if "fov" not in meta.columns or "cell_ID" not in meta.columns:
            continue
        base = item["base"]
        meta["source_cell_id"] = meta["fov"].astype(str) + "::" + cosmx_cell_component(meta["cell_ID"])
        meta["cell_id"] = base + "::" + meta["source_cell_id"]
        meta["label"] = meta[label_col].astype(str)
        meta["x"] = pd.to_numeric(meta[x_col], errors="coerce")
        meta["y"] = pd.to_numeric(meta[y_col], errors="coerce")
        meta["sample_id"] = base
        meta["fov_group"] = base + "::fov_" + meta["fov"].astype(str)
        meta["source_accession"] = accession
        meta = meta.dropna(subset=["x", "y"])
        if meta["label"].nunique() < 2:
            continue
        meta_parts.append(meta)
        usable_samples.append(item)
        label_col_used = label_col

    if not meta_parts:
        return None, "CSV-like samples found but no usable label/coordinate metadata"

    metadata_full = pd.concat(meta_parts, ignore_index=True)
    selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
    if len(selected_cells) < 200 or metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique() < 2:
        return None, "too few selected labeled cells after CSV-like filtering"
    selected = set(selected_cells)
    metadata = metadata_full.set_index("cell_id", drop=False).loc[selected_cells].reset_index(drop=True)

    common_features: set[str] | None = None
    feature_maps = {}
    for item in usable_samples:
        try:
            header = read_csv_maybe_tar(item["expression"], nrows=0)
        except Exception:
            continue
        genes = [str(col) for col in header.columns if str(col) not in {"fov", "cell_ID"}]
        if not genes:
            continue
        feature_maps[item["base"]] = genes
        common_features = set(genes) if common_features is None else common_features & set(genes)
    if not common_features:
        return None, "no common expression features across CSV-like samples"
    common = sorted(common_features)

    pieces = []
    for item in usable_samples:
        base = item["base"]
        if base not in feature_maps:
            continue
        expr = read_csv_maybe_tar(item["expression"])
        if "fov" not in expr.columns or "cell_ID" not in expr.columns:
            continue
        expr["cell_id"] = base + "::" + expr["fov"].astype(str) + "::" + cosmx_cell_component(expr["cell_ID"])
        keep = [cell for cell in selected_cells if cell in selected and cell.startswith(base + "::")]
        if not keep:
            continue
        expr = expr.set_index("cell_id", drop=False)
        keep = [cell for cell in keep if cell in expr.index]
        if not keep:
            continue
        sub = expr.loc[keep, common].apply(pd.to_numeric, errors="coerce").fillna(0).T
        pieces.append(sub)
    if not pieces:
        return None, "no expression columns matched selected CSV-like cells"

    expression = pd.concat(pieces, axis=1)
    available_cells = [cell for cell in selected_cells if cell in expression.columns]
    if len(available_cells) < 200:
        return None, "too few selected CSV-like cells matched expression columns"
    metadata = metadata.set_index("cell_id", drop=False).loc[available_cells].reset_index(drop=True)
    if metadata["label"].nunique() < 2:
        return None, "too few labels after matching CSV-like expression"
    expression = expression.loc[:, available_cells]
    expression = expression_feature_subset(expression, max_features)

    dataset_id = f"GEO_{accession}_GENERIC_COSMX_CSV_EXPANDED"
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expression, expr_path)

    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": "generic_cosmx_csv_metadata_expression",
        "label_col": label_col_used,
        "n_cells_full": int(metadata_full.shape[0]),
        "n_features_full": int(len(common)),
        "expanded_cells": int(expression.shape[1]),
        "expanded_features": int(expression.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic CosMx CSV expression+metadata parser")
    return dataset_id, "prepared generic CosMx CSV expression+metadata dataset"


def prepare_xenium_like(accession: str, raw: Path, prepared_root: Path, max_per_label: int, min_per_label: int, max_features: int) -> tuple[str | None, str]:
    samples = discover_xenium_like(raw)
    if not samples:
        return None, "no complete annotation/matrix/barcode/feature/cell-table samples"

    meta_parts = []
    usable_samples = []
    label_col_used = None
    for item in samples:
        ann = read_table_auto(item["annotation"], dtype=str)
        label_col, _ = pick_label_col(ann, allow_numeric=True)
        id_col = pick_id_col(ann)
        if label_col is None or id_col is None:
            continue
        numeric_fraction = pd.to_numeric(ann[label_col], errors="coerce").notna().mean()
        if numeric_fraction > 0.9:
            for mapping_path in sorted(raw.glob("*annotation*ct_name*.csv.gz")):
                mapping = pd.read_csv(mapping_path, dtype=str)
                if not {"clusterID", "clusterName"}.issubset(mapping.columns):
                    continue
                label_map = dict(zip(mapping["clusterID"].astype(str), mapping["clusterName"].astype(str)))
                resolved = ann[label_col].astype(str).map(label_map)
                if resolved.notna().sum() >= 200:
                    ann["_resolved_label"] = resolved
                    label_col = "_resolved_label"
                    break
        if pd.to_numeric(ann[label_col], errors="coerce").notna().mean() > 0.9:
            continue
        cells = load_cell_table(item["cells"])
        cell_id_col = pick_id_col(cells)
        x_col, y_col = pick_coord_cols(cells)
        if cell_id_col is None or x_col is None or y_col is None:
            continue
        ann[id_col] = ann[id_col].astype(str)
        cells[cell_id_col] = cells[cell_id_col].astype(str)
        meta = ann.merge(cells, left_on=id_col, right_on=cell_id_col, how="inner")
        if meta.empty:
            continue
        base = item["base"]
        meta["source_cell_id"] = meta[id_col].astype(str)
        meta["cell_id"] = base + "::" + meta["source_cell_id"]
        meta["label"] = meta[label_col].astype(str)
        meta["x"] = pd.to_numeric(meta[x_col], errors="coerce")
        meta["y"] = pd.to_numeric(meta[y_col], errors="coerce")
        meta["fov_group"] = base
        meta["sample_id"] = base
        meta["source_accession"] = accession
        meta = meta.dropna(subset=["x", "y"])
        if meta["label"].nunique() < 2:
            continue
        meta_parts.append(meta)
        usable_samples.append(item)
        label_col_used = label_col

    if not meta_parts:
        return None, "annotation files found but no usable label/coordinate merge"

    metadata_full = pd.concat(meta_parts, ignore_index=True)
    group_mode = "sample"
    if metadata_full["fov_group"].nunique() < 2:
        metadata_full["fov_group"] = (
            metadata_full["sample_id"].astype(str)
            + "::"
            + spatial_blocks(metadata_full["x"], metadata_full["y"], bins=6).astype(str)
        )
        group_mode = "within-sample spatial block"
    selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
    if len(selected_cells) < 200 or metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique() < 2:
        return None, "too few selected labeled cells after filtering"
    selected = set(selected_cells)
    metadata = metadata_full.set_index("cell_id", drop=False).loc[selected_cells].reset_index(drop=True)

    feature_maps = {}
    common_features: set[str] | None = None
    for item in usable_samples:
        if item["matrix_kind"] == "h5":
            _, names = read_10x_barcodes_features(item["matrix"])
        else:
            features = pd.read_csv(item["features"], sep="\t", header=None, dtype=str)
            names = feature_names(features)
        feature_maps[item["base"]] = names
        common_features = set(names) if common_features is None else common_features & set(names)
    if not common_features:
        return None, "no common features across usable samples"
    common = sorted(common_features)

    pieces = []
    for item in usable_samples:
        base = item["base"]
        if item["matrix_kind"] == "h5":
            mat, barcodes, names = read_10x_h5(item["matrix"])
        else:
            barcodes = pd.read_csv(item["barcodes"], sep="\t", header=None, dtype=str).iloc[:, 0].astype(str).tolist()
            names = feature_maps[base]
            mat = mmread(item["matrix"]).tocsr()
        prefixed = [f"{base}::{bc}" for bc in barcodes]
        keep_idx = [idx for idx, cell in enumerate(prefixed) if cell in selected]
        if not keep_idx:
            continue
        feature_index = {feature: i for i, feature in enumerate(names)}
        feature_idx = [feature_index[feature] for feature in common]
        sub = mat[feature_idx, :][:, keep_idx]
        dense = sub.toarray() if sparse.issparse(sub) else np.asarray(sub)
        cols = [prefixed[idx] for idx in keep_idx]
        pieces.append(pd.DataFrame(dense, index=common, columns=cols))
    if not pieces:
        return None, "no expression columns matched selected cells"

    expression = pd.concat(pieces, axis=1)
    expression = expression.loc[:, selected_cells]
    expression = expression_feature_subset(expression, max_features)

    dataset_id = f"GEO_{accession}_GENERIC_XENIUM_EXPANDED"
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expression, expr_path)

    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": "generic_xenium_matrix_annotation",
        "matrix_formats": sorted({item["matrix_kind"] for item in usable_samples}),
        "label_col": label_col_used,
        "n_cells_full": int(metadata_full.shape[0]),
        "n_features_full": int(len(common)),
        "expanded_cells": int(expression.shape[1]),
        "expanded_features": int(expression.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "group_mode": group_mode,
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic Xenium matrix+annotation parser")
    return dataset_id, "prepared generic Xenium matrix+annotation dataset"


def sidecar_id_col(table: pd.DataFrame) -> str | None:
    id_col = pick_id_col(table)
    if id_col is not None:
        return id_col
    for col in ["Unnamed: 0", "index", "spot_id", "bin_id"]:
        if col in table.columns and table[col].astype(str).nunique() == len(table):
            return col
    if len(table.columns):
        first = str(table.columns[0])
        if table[first].astype(str).nunique() == len(table):
            return first
    return None


def discover_h5ad_sidecar_pairs(raw: Path, ad) -> list[dict]:
    pairs = []
    for path in sorted(raw.glob("*.h5ad")):
        gsm_match = re.match(r"^(GSM\d+)", path.name, flags=re.I)
        if gsm_match is None:
            continue
        gsm = gsm_match.group(1)
        annotation_paths = sorted(
            {
                *raw.glob(f"{gsm}*anno*.csv.gz"),
                *raw.glob(f"{gsm}*annotation*.csv.gz"),
                *raw.glob(f"{gsm}*label*.csv.gz"),
            }
        )
        try:
            a = ad.read_h5ad(path, backed="r")
            spatial_keys = [key for key in a.obsm.keys() if "spatial" in str(key).lower()]
            x_col, y_col = pick_coord_cols(a.obs)
            coord_mode = f"obsm:{spatial_keys[0]}" if spatial_keys else (f"obs:{x_col},{y_col}" if x_col and y_col else None)
            obs_names = pd.Index(a.obs_names.astype(str))
            internal_label_col, _ = pick_label_col(a.obs)
            composition_key = next(
                (
                    key
                    for key in ["ctype_props", "cell_type_proportions", "celltype_proportions"]
                    if key in a.obsm.keys() and isinstance(a.obsm[key], pd.DataFrame) and a.obsm[key].shape[1] >= 2
                ),
                None,
            )
            a.file.close()
        except Exception:
            continue
        if coord_mode is None:
            continue
        matched_sidecar = False
        for annotation_path in annotation_paths:
            try:
                annotation = read_table_auto(annotation_path, dtype=str)
                label_col, _ = pick_label_col(annotation)
                id_col = sidecar_id_col(annotation)
                if label_col is None or id_col is None:
                    continue
                annotation_ids = pd.Index(annotation[id_col].astype(str))
                overlap = int(obs_names.isin(annotation_ids).sum())
                if overlap < 200:
                    continue
                pairs.append(
                    {
                        "path": path,
                        "annotation": annotation_path,
                        "label_col": label_col,
                        "id_col": id_col,
                        "coord_mode": coord_mode,
                        "overlap": overlap,
                        "composition_key": None,
                        "internal_label_col": None,
                    }
                )
                matched_sidecar = True
                break
            except Exception:
                continue
        if not matched_sidecar and composition_key is not None:
            pairs.append(
                {
                    "path": path,
                    "annotation": None,
                    "label_col": f"argmax({composition_key})",
                    "id_col": None,
                    "coord_mode": coord_mode,
                    "overlap": int(len(obs_names)),
                    "composition_key": composition_key,
                    "internal_label_col": None,
                }
            )
        elif not matched_sidecar and internal_label_col is not None:
            pairs.append(
                {
                    "path": path,
                    "annotation": None,
                    "label_col": internal_label_col,
                    "id_col": None,
                    "coord_mode": coord_mode,
                    "overlap": int(len(obs_names)),
                    "composition_key": None,
                    "internal_label_col": internal_label_col,
                }
            )
    return pairs


def prepare_h5ad_sidecar_collection(
    accession: str,
    raw: Path,
    prepared_root: Path,
    max_per_label: int,
    min_per_label: int,
    max_features: int,
    ad,
) -> tuple[str | None, str]:
    pairs = discover_h5ad_sidecar_pairs(raw, ad)
    if not pairs:
        return None, "no H5AD plus semantic sidecar-annotation pairs"

    metadata_parts = []
    for item in pairs:
        a = ad.read_h5ad(item["path"], backed="r")
        source_ids = pd.Index(a.obs_names.astype(str))
        if item.get("internal_label_col") is not None:
            labels = a.obs[item["internal_label_col"]].astype(str).reset_index(drop=True)
            labels = labels.replace(LABEL_ALIASES_BY_ACCESSION.get(accession, {}))
            keep = labels.notna().to_numpy()
        elif item.get("composition_key") is not None:
            composition = a.obsm[item["composition_key"]]
            labels = composition.idxmax(axis=1).astype(str).reset_index(drop=True)
            keep = composition.fillna(0).sum(axis=1).gt(0).to_numpy()
        else:
            annotation = read_table_auto(item["annotation"], dtype=str)
            annotation = annotation.drop_duplicates(item["id_col"]).copy()
            label_map = dict(zip(annotation[item["id_col"]].astype(str), annotation[item["label_col"]].astype(str)))
            labels = pd.Series(source_ids.map(label_map), index=np.arange(len(source_ids)), dtype="object")
            keep = labels.notna().to_numpy()
        if item["coord_mode"].startswith("obsm:"):
            key = item["coord_mode"].split(":", 1)[1]
            coords = np.asarray(a.obsm[key], dtype=float)
            x = coords[:, 0]
            y = coords[:, 1]
        else:
            x_col, y_col = item["coord_mode"].replace("obs:", "").split(",")
            x = pd.to_numeric(a.obs[x_col], errors="coerce").to_numpy()
            y = pd.to_numeric(a.obs[y_col], errors="coerce").to_numpy()
        sample_id = item["path"].stem
        metadata_parts.append(
            pd.DataFrame(
                {
                    "source_cell_id": source_ids[keep].astype(str),
                    "cell_id": sample_id + "::" + source_ids[keep].astype(str),
                    "label": labels.loc[keep].astype(str).to_numpy(),
                    "x": x[keep],
                    "y": y[keep],
                    "sample_id": sample_id,
                    "fov_group": sample_id,
                    "source_accession": accession,
                }
            )
        )
        a.file.close()

    metadata_full = pd.concat(metadata_parts, ignore_index=True).dropna(subset=["x", "y"])
    group_mode = "source H5AD sample"
    if metadata_full["fov_group"].nunique() < 2:
        metadata_full["fov_group"] = (
            metadata_full["sample_id"].astype(str)
            + "::"
            + spatial_blocks(metadata_full["x"], metadata_full["y"], bins=6).astype(str)
        )
        group_mode = "within-sample spatial block"
    selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
    if len(selected_cells) < 200 or metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique() < 2:
        return None, "too few selected labeled cells after sidecar filtering"
    selected = set(selected_cells)
    metadata = metadata_full.set_index("cell_id", drop=False).loc[selected_cells].reset_index(drop=True)

    common_features: set[str] | None = None
    for item in pairs:
        a = ad.read_h5ad(item["path"], backed="r")
        features = set(map(str, a.var_names))
        common_features = features if common_features is None else common_features & features
        a.file.close()
    if not common_features:
        return None, "no common H5AD features across sidecar-annotated samples"
    common = sorted(common_features)

    feature_sums = np.zeros(len(common), dtype=float)
    n_expression_cells = 0
    for item in pairs:
        sample_id = item["path"].stem
        sample_cells = metadata.loc[metadata["sample_id"].eq(sample_id), "cell_id"].astype(str).tolist()
        if not sample_cells:
            continue
        source_ids = [cell.split("::", 1)[1] for cell in sample_cells]
        a = ad.read_h5ad(item["path"], backed="r")
        obs_index = pd.Index(a.obs_names.astype(str)).get_indexer(source_ids)
        valid = obs_index >= 0
        obs_index = obs_index[valid]
        if not len(obs_index):
            a.file.close()
            continue
        obs_index = np.sort(obs_index)
        matrix = a.X[obs_index, :]
        feature_index = pd.Index(a.var_names.astype(str)).get_indexer(common)
        matrix = matrix[:, feature_index]
        feature_sums += np.asarray(matrix.sum(axis=0)).ravel()
        n_expression_cells += int(matrix.shape[0])
        a.file.close()
    if n_expression_cells == 0:
        return None, "no H5AD expression rows matched selected sidecar cells"
    keep_count = min(max_features, len(common))
    top = np.argsort(-feature_sums, kind="stable")[:keep_count]
    keep_features = sorted(common[idx] for idx in top)

    pieces = []
    for item in pairs:
        sample_id = item["path"].stem
        sample_cells = metadata.loc[metadata["sample_id"].eq(sample_id), "cell_id"].astype(str).tolist()
        if not sample_cells:
            continue
        source_ids = [cell.split("::", 1)[1] for cell in sample_cells]
        a = ad.read_h5ad(item["path"], backed="r")
        obs_index = pd.Index(a.obs_names.astype(str)).get_indexer(source_ids)
        valid_pairs = [(cell, idx) for cell, idx in zip(sample_cells, obs_index) if idx >= 0]
        valid_pairs.sort(key=lambda pair: pair[1])
        ordered_cells = [pair[0] for pair in valid_pairs]
        ordered_index = np.asarray([pair[1] for pair in valid_pairs], dtype=int)
        feature_index = pd.Index(a.var_names.astype(str)).get_indexer(keep_features)
        matrix = a.X[ordered_index, :]
        matrix = matrix[:, feature_index]
        dense = matrix.toarray() if sparse.issparse(matrix) else np.asarray(matrix)
        pieces.append(pd.DataFrame(dense.T, index=keep_features, columns=ordered_cells))
        a.file.close()
    if not pieces:
        return None, "no expression pieces produced from H5AD sidecar pairs"
    expression = pd.concat(pieces, axis=1).loc[:, selected_cells]

    composition_mode = all(item.get("composition_key") is not None for item in pairs)
    internal_mode = all(item.get("internal_label_col") is not None for item in pairs)
    dataset_id = (
        f"GEO_{accession}_H5AD_COMPOSITION_EXPANDED"
        if composition_mode
        else (
            f"GEO_{accession}_H5AD_INTERNAL_LABEL_EXPANDED"
            if internal_mode
            else f"GEO_{accession}_H5AD_SIDECAR_EXPANDED"
        )
    )
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expression, expr_path)
    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": (
            "multi_h5ad_composition_argmax"
            if composition_mode
            else ("multi_h5ad_internal_label" if internal_mode else "multi_h5ad_sidecar_annotation")
        ),
        "annotation_evidence_type": (
            "external_composition_argmax"
            if composition_mode
            else (
                "external_model_label"
                if internal_mode
                and re.search(r"predicted|majority|transfer|single.?r", str(pairs[0]["label_col"]), re.I)
                else ("author_internal_annotation" if internal_mode else "external_sidecar_annotation")
            )
        ),
        "label_col": (
            "obsm:"
            if composition_mode
            else ("obs:" if internal_mode else "sidecar:")
        )
        + str(pairs[0]["label_col"]),
        "n_cells_full": int(metadata_full.shape[0]),
        "n_features_full": int(len(common)),
        "expanded_cells": int(expression.shape[1]),
        "expanded_features": int(expression.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "group_mode": group_mode,
        "source_h5ad_files": [item["path"].name for item in pairs],
        "source_annotation_files": [
            item["annotation"].name
            if item["annotation"] is not None
            else (
                f"obs:{item['internal_label_col']}"
                if item.get("internal_label_col") is not None
                else f"obsm:{item['composition_key']}"
            )
            for item in pairs
        ],
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    parser_note = (
        "multi-H5AD composition-argmax parser"
        if composition_mode
        else ("multi-H5AD internal-label parser" if internal_mode else "multi-H5AD sidecar-annotation parser")
    )
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, parser_note)
    label_mode = "composition" if composition_mode else ("internal" if internal_mode else "sidecar")
    return dataset_id, f"prepared multi-H5AD dataset with sample-blocked {label_mode} annotations"


def h5ad_candidates(raw: Path) -> list[tuple[Path, str, str | None, str]]:
    ad, _ = try_import_anndata()
    if ad is None:
        return []
    candidates = []
    for path in sorted(raw.glob("*.h5ad")):
        try:
            a = ad.read_h5ad(path, backed="r")
            label_col, _ = pick_label_col(a.obs)
            has_spatial = "spatial" in a.obsm.keys()
            x_col, y_col = pick_coord_cols(a.obs)
            if label_col and (has_spatial or (x_col and y_col)):
                coord_mode = "obsm_spatial" if has_spatial else f"obs:{x_col},{y_col}"
                candidates.append((path, label_col, coord_mode, str(a.shape)))
            a.file.close()
        except Exception:
            continue
    return candidates


def prepare_h5ad(accession: str, raw: Path, prepared_root: Path, max_per_label: int, min_per_label: int, max_features: int) -> tuple[str | None, str]:
    ad, anndata_error = try_import_anndata()
    if ad is None:
        dataset_id, reason = prepare_h5ad_light(accession, raw, prepared_root, max_per_label, min_per_label, max_features)
        if dataset_id is not None:
            return dataset_id, reason
        return None, f"{reason}; anndata import failed ({anndata_error})"
    sidecar_dataset_id, sidecar_reason = prepare_h5ad_sidecar_collection(
        accession,
        raw,
        prepared_root,
        max_per_label,
        min_per_label,
        max_features,
        ad,
    )
    if sidecar_dataset_id is not None:
        return sidecar_dataset_id, sidecar_reason
    candidates = h5ad_candidates(raw)
    if not candidates:
        dataset_id, reason = prepare_h5ad_light(accession, raw, prepared_root, max_per_label, min_per_label, max_features)
        if dataset_id is not None:
            return dataset_id, reason
        return None, f"{reason}; sidecar collection: {sidecar_reason}"
    path, label_col, coord_mode, _ = candidates[0]
    a = ad.read_h5ad(path)
    obs = a.obs.copy()
    obs["source_cell_id"] = a.obs_names.astype(str)
    obs["cell_id"] = path.stem + "::" + obs["source_cell_id"].astype(str)
    obs["label"] = obs[label_col].astype(str)
    if coord_mode == "obsm_spatial":
        coords = np.asarray(a.obsm["spatial"], dtype=float)
        obs["x"] = coords[:, 0]
        obs["y"] = coords[:, 1]
    else:
        x_col, y_col = coord_mode.replace("obs:", "").split(",")
        obs["x"] = pd.to_numeric(obs[x_col], errors="coerce")
        obs["y"] = pd.to_numeric(obs[y_col], errors="coerce")
    obs["sample_id"] = path.stem
    obs["fov_group"] = spatial_blocks(obs["x"], obs["y"], bins=8)
    obs["source_accession"] = accession
    metadata_full = obs.dropna(subset=["x", "y"]).copy()
    selected_cells = choose_balanced(metadata_full, max_per_label, min_per_label)
    if len(selected_cells) < 200 or metadata_full.loc[metadata_full["cell_id"].isin(selected_cells), "label"].nunique() < 2:
        return None, "too few selected labeled cells after h5ad filtering"

    selected_obs_names = [cell.split("::", 1)[1] for cell in selected_cells]
    obs_index = pd.Index(a.obs_names.astype(str)).get_indexer(selected_obs_names)
    mat = a.X[obs_index, :]
    dense = mat.toarray() if sparse.issparse(mat) else np.asarray(mat)
    feature_ids = list(map(str, a.var_names))
    expr = pd.DataFrame(dense.T, index=feature_ids, columns=selected_cells)
    expr = expression_feature_subset(expr, max_features)
    metadata = metadata_full.set_index("cell_id", drop=False).loc[selected_cells].reset_index(drop=True)

    dataset_id = f"GEO_{accession}_GENERIC_H5AD_EXPANDED"
    out = prepared_root / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / f"{dataset_id}_expanded_metadata.tsv"
    expr_path = out / f"{dataset_id}_expanded_expression.tsv.gz"
    metadata.to_csv(meta_path, sep="\t", index=False)
    write_gzip_tsv(expr, expr_path)
    summary = {
        "dataset_id": dataset_id,
        "source_accession": accession,
        "parser": "generic_h5ad_spatial_label_parser",
        "label_col": label_col,
        "n_cells_full": int(metadata_full.shape[0]),
        "n_features_full": int(a.n_vars),
        "expanded_cells": int(expr.shape[1]),
        "expanded_features": int(expr.shape[0]),
        "n_labels": int(metadata["label"].nunique()),
        "n_fov_groups": int(metadata["fov_group"].nunique()),
        "label_counts": metadata["label"].value_counts().to_dict(),
    }
    (out / f"{dataset_id}_expanded_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    register_dataset(dataset_id, accession, expr_path, meta_path, summary, "generic h5ad parser")
    return dataset_id, "prepared generic h5ad spatial-label dataset"


def register_dataset(dataset_id: str, accession: str, expr_path: Path, meta_path: Path, summary: dict, parser_note: str) -> None:
    row = {
        "dataset_id": dataset_id,
        "source_dataset_id": accession,
        "modality": summary.get("parser", "generic_spatial_transcriptomics"),
        "biological_context": f"{accession} prepared by {parser_note}",
        "sampling": f"balanced labels, max_per_label applied; label_col={summary.get('label_col', '')}",
        "n_cells_full": summary["n_cells_full"],
        "n_features_full": summary["n_features_full"],
        "expanded_cells": summary["expanded_cells"],
        "expanded_features": summary["expanded_features"],
        "n_labels": summary["n_labels"],
        "n_fov_groups": summary["n_fov_groups"],
        "expression_path": str(expr_path.resolve()),
        "metadata_path": str(meta_path.resolve()),
        "cell_id_col": "cell_id",
        "label_col": "label",
        "group_col": "fov_group",
        "x_col": "x",
        "y_col": "y",
    }
    registry = pd.read_csv(REGISTRY) if REGISTRY.exists() else pd.DataFrame()
    if not registry.empty:
        registry = registry[registry["dataset_id"] != dataset_id]
    registry = pd.concat([registry, pd.DataFrame([row])], ignore_index=True)
    registry.to_csv(REGISTRY, index=False)


def main() -> None:
    args = parse_args()
    raw = Path(args.download_root) / args.accession / "raw"
    prepared_root = Path(args.prepared_root)
    if not raw.exists():
        print(json.dumps({"accession": args.accession, "prepared": False, "reason": f"missing raw dir: {raw}"}, indent=2))
        return
    reasons = []
    dataset_id, reason = prepare_xenium_like(
        args.accession,
        raw,
        prepared_root,
        args.max_per_label,
        args.min_per_label,
        args.max_features,
    )
    if dataset_id is None:
        reasons.append(f"xenium_like: {reason}")
    if dataset_id is None:
        dataset_id, reason = prepare_visium_10x_h5_like(
            args.accession,
            raw,
            prepared_root,
            args.max_per_label,
            args.min_per_label,
            args.max_features,
        )
        if dataset_id is None:
            reasons.append(f"visium_10x_h5_like: {reason}")
    if dataset_id is None:
        dataset_id, reason = prepare_cosmx_tsv_like(
            args.accession,
            raw,
            prepared_root,
            args.max_per_label,
            args.min_per_label,
            args.max_features,
        )
        if dataset_id is None:
            reasons.append(f"cosmx_tsv_like: {reason}")
    if dataset_id is None:
        dataset_id, reason = prepare_cosmx_csv_like(
            args.accession,
            raw,
            prepared_root,
            args.max_per_label,
            args.min_per_label,
            args.max_features,
        )
        if dataset_id is None:
            reasons.append(f"cosmx_csv_like: {reason}")
    if dataset_id is None:
        dataset_id, reason = prepare_generic_csv_pair_like(
            args.accession,
            raw,
            prepared_root,
            args.max_per_label,
            args.min_per_label,
            args.max_features,
        )
        if dataset_id is None:
            reasons.append(f"generic_csv_pair_like: {reason}")
    if dataset_id is None:
        dataset_id, reason = prepare_h5ad(
            args.accession,
            raw,
            prepared_root,
            args.max_per_label,
            args.min_per_label,
            args.max_features,
        )
        if dataset_id is None:
            reasons.append(f"h5ad: {reason}")
    if dataset_id is None and reasons:
        reason = "; ".join(reasons)
    print(json.dumps({"accession": args.accession, "prepared": dataset_id is not None, "dataset_id": dataset_id, "reason": reason}, indent=2))


if __name__ == "__main__":
    main()
