from __future__ import annotations

import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote

import anndata as ad
import pandas as pd
import requests


DEFAULT_SERVER = "https://gene.ai.tencent.com/SpatialOmics/api/pysodb"
CELLTYPE_NAME_RE = re.compile(
    r"(cell[_. -]?types?|celltype|manual.*annot|annot.*cell|predicted[_. -]?labels?|"
    r"majority[_. -]?voting|cell[_. -]?identity|lineage|subclass)",
    re.I,
)
GENERIC_LABEL_RE = re.compile(r"(^|[_. -])(annotation|annot|labels?|class)($|[_. -])", re.I)
DOMAIN_NAME_RE = re.compile(r"(cluster|leiden|louvain|domain|region|layer|zone)", re.I)
GROUP_NAME_RE = re.compile(r"(sample|donor|patient|slide|section|fov|replicate|batch)", re.I)
BAD_LABELS = {
    "",
    "nan",
    "none",
    "na",
    "unknown",
    "unassigned",
    "ambiguous",
    "other",
    "low quality",
    "low_quality",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory SODB spatial-transcriptomics files and audit small representative "
            "H5ADs for expression, coordinates and semantic cell-type labels."
        )
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--download-root", type=Path, required=True)
    parser.add_argument("--server", default=DEFAULT_SERVER)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--max-download-mb", type=float, default=250.0)
    parser.add_argument("--representatives-per-dataset", type=int, default=1)
    parser.add_argument("--size-only", action="store_true")
    parser.add_argument("--dataset-limit", type=int, default=0)
    parser.add_argument("--force-inventory", action="store_true")
    return parser.parse_args()


def download_url(server: str, dataset_name: str, experiment_name: str) -> str:
    dataset = quote(str(dataset_name), safe="")
    experiment = quote(str(experiment_name), safe="")
    return f"{server.rstrip('/')}/download/{dataset}/{experiment}"


def fetch_catalog(server: str, timeout: float) -> pd.DataFrame:
    response = requests.get(f"{server.rstrip('/')}/info", timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"SODB info endpoint returned code={payload.get('code')}")
    frame = pd.DataFrame(
        payload.get("data", []),
        columns=["biotech_category", "dataset_name", "experiment_name"],
    )
    return frame.loc[frame["biotech_category"].eq("Spatial Transcriptomics")].copy()


def probe_size(row: dict, server: str, timeout: float) -> dict:
    url = download_url(server, row["dataset_name"], row["experiment_name"])
    result = {**row, "url": url, "http_status": None, "size_bytes": None, "error": ""}
    for attempt in range(3):
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            result["http_status"] = response.status_code
            length = response.headers.get("content-length")
            if response.ok and length is not None:
                result["size_bytes"] = int(length)
                return result
            with requests.get(
                url,
                headers={"Range": "bytes=0-0"},
                timeout=timeout,
                allow_redirects=True,
                stream=True,
            ) as ranged:
                result["http_status"] = ranged.status_code
                content_range = ranged.headers.get("content-range", "")
                match = re.search(r"/(\d+)$", content_range)
                if match:
                    result["size_bytes"] = int(match.group(1))
                    return result
                length = ranged.headers.get("content-length")
                if ranged.ok and length is not None and ranged.status_code == 200:
                    result["size_bytes"] = int(length)
                    return result
                ranged.raise_for_status()
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            if attempt < 2:
                time.sleep(1.0 + attempt)
    return result


def build_inventory(args: argparse.Namespace) -> pd.DataFrame:
    inventory_path = args.output_dir / "SODB_SPATIAL_FILE_INVENTORY.csv"
    if inventory_path.exists() and not args.force_inventory:
        inventory = pd.read_csv(inventory_path)
        required = {"dataset_name", "experiment_name", "size_bytes"}
        if required.issubset(inventory.columns):
            return inventory

    catalog = fetch_catalog(args.server, args.timeout)
    records = catalog.to_dict("records")
    completed: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [
            pool.submit(probe_size, record, args.server, args.timeout)
            for record in records
        ]
        for index, future in enumerate(as_completed(futures), start=1):
            completed.append(future.result())
            if index % 100 == 0 or index == len(futures):
                print(f"inventory_progress={index}/{len(futures)}", flush=True)

    inventory = pd.DataFrame(completed)
    inventory["size_mb"] = pd.to_numeric(inventory["size_bytes"], errors="coerce") / 1_000_000
    inventory = inventory.sort_values(["dataset_name", "size_bytes", "experiment_name"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(inventory_path, index=False)
    return inventory


def safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("._")
    return cleaned[:140] or "unnamed"


def download_file(row: pd.Series, root: Path, timeout: float) -> tuple[Path | None, str]:
    folder = root / safe_component(row["dataset_name"])
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"{safe_component(row['experiment_name'])}.h5ad"
    expected = int(row["size_bytes"])
    if destination.exists() and destination.stat().st_size == expected:
        return destination, ""

    partial = destination.with_suffix(".h5ad.part")
    for attempt in range(3):
        try:
            with requests.get(row["url"], stream=True, timeout=(30, timeout)) as response:
                response.raise_for_status()
                with partial.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
            if partial.stat().st_size != expected:
                raise IOError(
                    f"size mismatch: expected {expected}, received {partial.stat().st_size}"
                )
            os.replace(partial, destination)
            return destination, ""
        except Exception as exc:
            if partial.exists():
                partial.unlink()
            if attempt == 2:
                return None, f"{type(exc).__name__}: {exc}"
            time.sleep(2.0 + attempt)
    return None, "download failed"


def label_summary(series: pd.Series) -> tuple[bool, int, str]:
    values = series.dropna().astype(str).str.strip()
    values = values.loc[~values.str.lower().isin(BAD_LABELS)]
    values = values.loc[~values.str.fullmatch(r"[A-Za-z]", na=False)]
    n = int(values.shape[0])
    unique = values.drop_duplicates()
    n_unique = int(unique.shape[0])
    if n == 0 or n_unique < 2:
        return False, n_unique, ""
    numeric_fraction = pd.to_numeric(values, errors="coerce").notna().mean()
    identifier_fraction = values.str.match(
        r"^(cell|spot|barcode|AAAC|[A-Z]{2,}\d)[A-Za-z0-9_.:-]*$", case=False
    ).mean()
    too_many = n_unique > min(300, max(30, int(n * 0.25)))
    valid = numeric_fraction < 0.9 and identifier_fraction < 0.8 and not too_many
    examples = " | ".join(unique.head(8).tolist())
    return bool(valid), n_unique, examples


def coordinate_mode(adata: ad.AnnData) -> str:
    for key in adata.obsm.keys():
        shape = getattr(adata.obsm[key], "shape", ())
        if "spatial" in str(key).lower() and len(shape) == 2 and shape[1] >= 2:
            return f"obsm:{key}"
    lower = {str(column).lower(): str(column) for column in adata.obs.columns}
    pairs = [
        ("x", "y"),
        ("x_centroid", "y_centroid"),
        ("center_x", "center_y"),
        ("array_col", "array_row"),
        ("spatial_x", "spatial_y"),
        ("xcoord", "ycoord"),
        ("x_coord", "y_coord"),
    ]
    for x_name, y_name in pairs:
        if x_name in lower and y_name in lower:
            return f"obs:{lower[x_name]},{lower[y_name]}"
    return ""


def rank_label_columns(obs: pd.DataFrame) -> list[dict]:
    candidates: list[dict] = []
    for column in obs.columns:
        name = str(column)
        valid, n_unique, examples = label_summary(obs[column])
        if not valid:
            continue
        if CELLTYPE_NAME_RE.search(name):
            score, task = 100, "cell_type"
        elif GENERIC_LABEL_RE.search(name):
            score, task = 70, "possible_cell_type"
        elif DOMAIN_NAME_RE.search(name):
            score, task = 20, "domain_or_cluster"
        else:
            continue
        candidates.append(
            {
                "column": name,
                "n_labels": n_unique,
                "examples": examples,
                "score": score,
                "task": task,
            }
        )
    return sorted(candidates, key=lambda item: (item["score"], item["n_labels"]), reverse=True)


def all_categorical_columns(obs: pd.DataFrame) -> list[dict]:
    candidates: list[dict] = []
    for column in obs.columns:
        valid, n_unique, examples = label_summary(obs[column])
        if not valid or n_unique > 100:
            continue
        candidates.append(
            {
                "column": str(column),
                "n_values": n_unique,
                "examples": examples,
            }
        )
    return sorted(candidates, key=lambda item: (item["n_values"], item["column"]))


def group_columns(obs: pd.DataFrame) -> str:
    columns: list[str] = []
    for column in obs.columns:
        if not GROUP_NAME_RE.search(str(column)):
            continue
        n_unique = obs[column].nunique(dropna=True)
        if 2 <= n_unique <= max(500, int(len(obs) * 0.2)):
            columns.append(f"{column}:{n_unique}")
    return " | ".join(columns[:12])


def audit_h5ad(row: pd.Series, path: Path) -> dict:
    result = {
        "dataset_name": row["dataset_name"],
        "experiment_name": row["experiment_name"],
        "file_path": str(path),
        "size_mb": round(path.stat().st_size / 1_000_000, 3),
        "n_obs": None,
        "n_vars": None,
        "coordinate_mode": "",
        "label_col": "",
        "n_labels": 0,
        "label_examples": "",
        "label_task": "",
        "group_columns": "",
        "obs_columns": "",
        "obsm_keys": "",
        "candidate_labels_json": "[]",
        "all_categorical_json": "[]",
        "benchmark_ready_celltype": False,
        "benchmark_ready_other_annotation": False,
        "error": "",
    }
    adata = None
    try:
        adata = ad.read_h5ad(path, backed="r")
        result["n_obs"], result["n_vars"] = map(int, adata.shape)
        result["obs_columns"] = " | ".join(map(str, adata.obs.columns))
        result["obsm_keys"] = " | ".join(map(str, adata.obsm.keys()))
        result["coordinate_mode"] = coordinate_mode(adata)
        result["group_columns"] = group_columns(adata.obs)
        candidates = rank_label_columns(adata.obs)
        result["candidate_labels_json"] = json.dumps(candidates, ensure_ascii=False)
        result["all_categorical_json"] = json.dumps(
            all_categorical_columns(adata.obs), ensure_ascii=False
        )
        if candidates:
            best = candidates[0]
            result["label_col"] = best["column"]
            result["n_labels"] = best["n_labels"]
            result["label_examples"] = best["examples"]
            result["label_task"] = best["task"]
        common_ready = bool(
            result["coordinate_mode"]
            and result["label_col"]
            and int(result["n_obs"] or 0) >= 200
            and int(result["n_vars"] or 0) >= 20
        )
        result["benchmark_ready_celltype"] = common_ready and result["label_task"] == "cell_type"
        result["benchmark_ready_other_annotation"] = common_ready and result["label_task"] != "cell_type"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if adata is not None and getattr(adata, "file", None) is not None:
            adata.file.close()
    return result


def choose_representatives(inventory: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    usable = inventory.copy()
    usable["size_bytes"] = pd.to_numeric(usable["size_bytes"], errors="coerce")
    usable = usable.dropna(subset=["size_bytes"])
    # SODB currently exposes a few 11-byte missing-file placeholders with HTTP 200.
    usable = usable.loc[usable["size_bytes"] >= 100_000]
    usable = usable.loc[usable["size_bytes"] <= args.max_download_mb * 1_000_000]
    usable = usable.sort_values(["dataset_name", "size_bytes", "experiment_name"])
    representatives = usable.groupby("dataset_name", as_index=False).head(
        max(1, args.representatives_per_dataset)
    )
    if args.dataset_limit > 0:
        selected = sorted(representatives["dataset_name"].drop_duplicates())[: args.dataset_limit]
        representatives = representatives.loc[representatives["dataset_name"].isin(selected)]
    return representatives


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.download_root.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(args)
    inventory["size_bytes"] = pd.to_numeric(inventory["size_bytes"], errors="coerce")

    summary = {
        "spatial_transcriptomics_experiments": int(len(inventory)),
        "spatial_transcriptomics_datasets": int(inventory["dataset_name"].nunique()),
        "files_with_known_size": int(inventory["size_bytes"].notna().sum()),
        "total_size_gb": round(float(inventory["size_bytes"].sum() / 1_000_000_000), 3),
        "max_download_mb": args.max_download_mb,
    }
    print(json.dumps(summary, indent=2))
    if args.size_only:
        (args.output_dir / "SODB_SPATIAL_INVENTORY_SUMMARY.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        return

    representatives = choose_representatives(inventory, args)
    representatives.to_csv(args.output_dir / "SODB_REPRESENTATIVE_SELECTION.csv", index=False)
    print(
        f"selected_representatives={len(representatives)} "
        f"selected_datasets={representatives['dataset_name'].nunique()}",
        flush=True,
    )

    audit_rows: list[dict] = []
    for index, (_, row) in enumerate(representatives.iterrows(), start=1):
        path, error = download_file(row, args.download_root, args.timeout * 4)
        if path is None:
            audit_rows.append(
                {
                    "dataset_name": row["dataset_name"],
                    "experiment_name": row["experiment_name"],
                    "file_path": "",
                    "size_mb": round(float(row["size_bytes"]) / 1_000_000, 3),
                    "benchmark_ready_celltype": False,
                    "benchmark_ready_other_annotation": False,
                    "error": error,
                }
            )
        else:
            audit_rows.append(audit_h5ad(row, path))
        print(f"audit_progress={index}/{len(representatives)}", flush=True)

    audit = pd.DataFrame(audit_rows)
    audit.to_csv(args.output_dir / "SODB_REPRESENTATIVE_METADATA_AUDIT.csv", index=False)
    categorical_rows: list[dict] = []
    for _, audited in audit.iterrows():
        try:
            columns = json.loads(str(audited.get("all_categorical_json", "[]")))
        except json.JSONDecodeError:
            columns = []
        for column in columns:
            categorical_rows.append(
                {
                    "dataset_name": audited["dataset_name"],
                    "experiment_name": audited["experiment_name"],
                    "n_obs": audited.get("n_obs"),
                    "n_vars": audited.get("n_vars"),
                    "coordinate_mode": audited.get("coordinate_mode", ""),
                    **column,
                }
            )
    pd.DataFrame(categorical_rows).to_csv(
        args.output_dir / "SODB_LOW_CARDINALITY_OBS_COLUMNS.csv", index=False
    )
    ready_celltype = audit.loc[audit["benchmark_ready_celltype"].fillna(False)]
    ready_other = audit.loc[audit["benchmark_ready_other_annotation"].fillna(False)]
    summary.update(
        {
            "audited_representatives": int(len(audit)),
            "audited_datasets": int(audit["dataset_name"].nunique()),
            "celltype_ready_representatives": int(len(ready_celltype)),
            "celltype_ready_datasets": int(ready_celltype["dataset_name"].nunique()),
            "other_annotation_ready_representatives": int(len(ready_other)),
            "other_annotation_ready_datasets": int(ready_other["dataset_name"].nunique()),
        }
    )
    (args.output_dir / "SODB_SPATIAL_INVENTORY_SUMMARY.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if not ready_celltype.empty:
        print(
            ready_celltype[
                [
                    "dataset_name",
                    "experiment_name",
                    "n_obs",
                    "n_vars",
                    "label_col",
                    "n_labels",
                    "coordinate_mode",
                    "label_examples",
                ]
            ].to_string(index=False, max_colwidth=80)
        )


if __name__ == "__main__":
    main()
