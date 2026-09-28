from __future__ import annotations

import math
from pathlib import Path

import anndata as ad
import pandas as pd


ROOT = Path(__file__).resolve().parent
TARGET = 39
EXCLUDE_DATASETS = {
    "lohoff2021integration",
    "moffitt2018molecular",
    "zhang2021spatially",
}


def main() -> None:
    audit = pd.read_csv(
        ROOT / "sodb_audit_multi3" / "SODB_REPRESENTATIVE_METADATA_AUDIT.csv"
    ).fillna("")
    registry = pd.read_csv(ROOT / "EXPANDED_SCALE_DATASETS.csv")
    used = {
        value.split(":", 1)[1]
        for value in registry["source_dataset_id"].astype(str)
        if value.startswith("SODB:")
    }
    used |= EXCLUDE_DATASETS

    candidates: list[dict] = []
    for dataset_name, group in audit.sort_values(
        ["dataset_name", "size_mb", "experiment_name"]
    ).groupby("dataset_name"):
        if dataset_name in used:
            continue
        row = group.iloc[0]
        n_obs = int(row["n_obs"] or 0)
        n_vars = int(row["n_vars"] or 0)
        if n_obs < 200 or n_vars < 50 or not str(row["coordinate_mode"]):
            continue
        path = Path(str(row["file_path"]))
        if not path.exists():
            continue
        adata = None
        try:
            adata = ad.read_h5ad(path, backed="r")
            if "leiden" not in adata.obs.columns:
                continue
            n_clusters = int(adata.obs["leiden"].nunique(dropna=True))
            if not 2 <= n_clusters <= 80:
                continue
        except Exception:
            continue
        finally:
            if adata is not None and getattr(adata, "file", None) is not None:
                adata.file.close()
        candidates.append(
            {
                "dataset_name": dataset_name,
                "experiment_name": row["experiment_name"],
                "file_path": row["file_path"],
                "n_obs": n_obs,
                "n_vars": n_vars,
                "n_clusters": n_clusters,
                "size_mb": float(row["size_mb"]),
                "selection_score": min(n_obs, 10_000) * math.log1p(n_vars),
            }
        )

    selection = pd.DataFrame(candidates).sort_values(
        ["selection_score", "dataset_name"], ascending=[False, True]
    )
    if len(selection) < TARGET:
        raise RuntimeError(f"Only {len(selection)} eligible calibration sources; need {TARGET}")
    selection["selected"] = False
    selection.iloc[:TARGET, selection.columns.get_loc("selected")] = True
    selection["rank"] = range(1, len(selection) + 1)
    selection.to_csv(ROOT / "SODB_CALIBRATION_SELECTION.csv", index=False)

    chosen = selection.loc[selection["selected"]]
    manifest = pd.DataFrame(
        {
            "dataset_name": chosen["dataset_name"],
            "experiment_mode": "representative",
            "label_col": "leiden",
            "task_type": "cluster_calibration",
            "label_evidence": "SODB_standardized_unsupervised_Leiden_not_semantic_truth",
            "preferred_group_col": "",
            "include_primary": "yes",
            "duplicate_of": "",
            "note": "Operational and matched-null calibration only; excluded from biological annotation accuracy claims",
        }
    )
    manifest.to_csv(ROOT / "SODB_CALIBRATION_CANDIDATES.csv", index=False)
    print(
        chosen[
            [
                "rank",
                "dataset_name",
                "experiment_name",
                "n_obs",
                "n_vars",
                "n_clusters",
                "size_mb",
            ]
        ].to_string(index=False)
    )
    print(f"selected_sources={len(chosen)} eligible_sources={len(selection)}")


if __name__ == "__main__":
    main()
