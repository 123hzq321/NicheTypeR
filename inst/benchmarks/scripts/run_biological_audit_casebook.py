from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_PREFIX = ROOT / "BIOLOGICAL_AUDIT_CASEBOOK"

CALL_FILES = [
    ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv",
    ROOT / "REFERENCE_PROFILE_BASELINE_calls.csv",
    ROOT / "SEURAT_LABEL_TRANSFER_BASELINE_calls.csv",
]

MODEL_ORDER = [
    "marker_only",
    "reference_profile",
    "seurat_label_transfer",
    "marker_reference_profile",
    "marker_spatial_smoothing",
    "marker_learned_neighborhood",
    "reference_profile_learned_neighborhood",
    "marker_context_specific_neighborhood",
]


def truthy(values: pd.Series) -> pd.Series:
    return values.astype(str).str.lower().map({"true": True, "false": False}).fillna(False)


def load_calls() -> pd.DataFrame:
    frames = []
    for path in CALL_FILES:
        if path.exists():
            frames.append(pd.read_csv(path, dtype={"cell_id": str}, low_memory=False))
    if not frames:
        raise FileNotFoundError("No call tables were found.")
    calls = pd.concat(frames, ignore_index=True, sort=False)
    calls["correct_bool"] = truthy(calls["correct"])
    calls["confidence"] = pd.to_numeric(calls["confidence"], errors="coerce")
    calls["margin"] = pd.to_numeric(calls["margin"], errors="coerce")
    reason = calls["conflict_reason"].fillna("").astype(str)
    calls["audit_flag"] = reason.ne("consistent")
    calls["explicit_conflict_flag"] = reason.str.contains(
        "neighborhood_conflict|ligand_receptor_conflict|learned_neighborhood_conflict",
        case=False,
        regex=True,
    )
    calls["low_margin_flag"] = reason.str.contains("low_margin", case=False, regex=False)
    calls["expert_confirmed_flagged_error"] = calls["audit_flag"] & ~calls["correct_bool"]
    calls["model_rank"] = calls["model"].map({m: i for i, m in enumerate(MODEL_ORDER)}).fillna(99)
    return calls


def metadata_path(dataset_id: str) -> Path | None:
    special = {
        "GSE202623_LESION": ROOT / "GSE202623" / "GSE202623_lesion_preview_metadata.tsv",
    }
    if dataset_id in special and special[dataset_id].exists():
        return special[dataset_id]
    folder = ROOT / dataset_id
    candidates = [
        folder / f"{dataset_id}_preview_metadata.tsv",
        folder / f"{dataset_id}_metadata.tsv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def normalize_metadata(meta: pd.DataFrame) -> pd.DataFrame | None:
    cell_candidates = ["cell_id", "cellID", "cell_ID", "barcode", "Unnamed: 0"]
    label_candidates = ["label", "cell.type_manual", "cell_type_final", "Cluster", "cluster"]
    x_candidates = ["x", "center_x", "center_colcoord", "X1"]
    y_candidates = ["y", "center_y", "center_rowcoord"]

    def first_existing(candidates: list[str]) -> str | None:
        for col in candidates:
            if col in meta.columns:
                return col
        return None

    cell_col = first_existing(cell_candidates)
    label_col = first_existing(label_candidates)
    x_col = first_existing(x_candidates)
    y_col = first_existing(y_candidates)
    if not all([cell_col, label_col, x_col, y_col]):
        return None

    out = pd.DataFrame(
        {
            "cell_id": meta[cell_col].astype(str),
            "expert_label": meta[label_col].astype(str),
            "x": pd.to_numeric(meta[x_col], errors="coerce"),
            "y": pd.to_numeric(meta[y_col], errors="coerce"),
        }
    )
    if "fov_group" in meta.columns:
        out["fov_group"] = meta["fov_group"].astype(str)
    elif "fov" in meta.columns:
        out["fov_group"] = meta["fov"].astype(str)
    elif "library_id" in meta.columns:
        out["fov_group"] = meta["library_id"].astype(str)
    else:
        out["fov_group"] = "all"
    out = out.dropna(subset=["x", "y"]).drop_duplicates("cell_id")
    return out if len(out) else None


def add_local_neighborhood_support(examples: pd.DataFrame, k: int = 12) -> pd.DataFrame:
    annotated = []
    metadata_cache: dict[str, pd.DataFrame | None] = {}
    for dataset_id, df in examples.groupby("dataset_id", sort=False):
        path = metadata_path(dataset_id)
        if path is None:
            metadata_cache[dataset_id] = None
        elif dataset_id not in metadata_cache:
            metadata_cache[dataset_id] = normalize_metadata(pd.read_csv(path, sep="\t", dtype=str))
        meta = metadata_cache[dataset_id]
        if meta is None:
            tmp = df.copy()
            tmp["neighbor_majority_label"] = ""
            tmp["neighbor_majority_fraction"] = np.nan
            tmp["truth_neighbor_fraction"] = np.nan
            tmp["predicted_neighbor_fraction"] = np.nan
            tmp["local_context_interpretation"] = "metadata unavailable"
            annotated.append(tmp)
            continue

        meta_by_id = meta.set_index("cell_id", drop=False)
        rows = []
        for row in df.itertuples(index=False):
            out = row._asdict()
            cell_id = str(row.cell_id)
            if cell_id not in meta_by_id.index:
                out.update(
                    neighbor_majority_label="",
                    neighbor_majority_fraction=np.nan,
                    truth_neighbor_fraction=np.nan,
                    predicted_neighbor_fraction=np.nan,
                    local_context_interpretation="cell absent from metadata",
                )
                rows.append(out)
                continue
            center = meta_by_id.loc[cell_id]
            local = meta[meta["fov_group"].eq(center["fov_group"])]
            if len(local) <= 1:
                local = meta
            dx = local["x"].to_numpy(float) - float(center["x"])
            dy = local["y"].to_numpy(float) - float(center["y"])
            dist = dx * dx + dy * dy
            order = np.argsort(dist)
            neighbor_idx = [idx for idx in order if local.iloc[idx]["cell_id"] != cell_id][:k]
            neighbors = local.iloc[neighbor_idx]
            counts = Counter(neighbors["expert_label"].astype(str))
            if counts:
                majority_label, majority_n = counts.most_common(1)[0]
                majority_fraction = majority_n / len(neighbors)
            else:
                majority_label, majority_fraction = "", np.nan
            truth = str(row.truth)
            predicted = str(row.label)
            truth_fraction = float((neighbors["expert_label"].astype(str) == truth).mean()) if len(neighbors) else np.nan
            predicted_fraction = float((neighbors["expert_label"].astype(str) == predicted).mean()) if len(neighbors) else np.nan
            if majority_label == truth:
                interp = "local majority supports expert label"
            elif predicted_fraction == 0 and len(neighbors):
                interp = "predicted label absent from local neighbors"
            elif truth_fraction > predicted_fraction:
                interp = "local neighbors favor expert label over prediction"
            else:
                interp = "local context flags conflict but does not resolve label"
            out.update(
                neighbor_majority_label=majority_label,
                neighbor_majority_fraction=majority_fraction,
                truth_neighbor_fraction=truth_fraction,
                predicted_neighbor_fraction=predicted_fraction,
                local_context_interpretation=interp,
            )
            rows.append(out)
        annotated.append(pd.DataFrame(rows))
    return pd.concat(annotated, ignore_index=True, sort=False)


def summarize(calls: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (dataset_id, model), df in calls.groupby(["dataset_id", "model"], sort=False):
        n = len(df)
        flagged = int(df["audit_flag"].sum())
        wrong = int((~df["correct_bool"]).sum())
        flagged_wrong = int(df["expert_confirmed_flagged_error"].sum())
        conflict_flagged = int(df["explicit_conflict_flag"].sum())
        conflict_wrong = int((df["explicit_conflict_flag"] & ~df["correct_bool"]).sum())
        rows.append(
            {
                "dataset_id": dataset_id,
                "model": model,
                "n_calls": n,
                "wrong_calls": wrong,
                "audit_flagged": flagged,
                "expert_confirmed_flagged_errors": flagged_wrong,
                "audit_flag_precision": flagged_wrong / flagged if flagged else np.nan,
                "wrong_call_rate": wrong / n if n else np.nan,
                "explicit_conflict_flagged": conflict_flagged,
                "explicit_conflict_precision": conflict_wrong / conflict_flagged if conflict_flagged else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["audit_flag_precision", "expert_confirmed_flagged_errors"],
        ascending=[False, False],
    )


def select_examples(calls: pd.DataFrame, n: int = 300) -> pd.DataFrame:
    cases = calls[calls["expert_confirmed_flagged_error"]].copy()
    cases["strong_flag_rank"] = np.where(cases["explicit_conflict_flag"], 0, 1)
    cases["confidence_rank"] = cases["confidence"].fillna(-1)
    cases["margin_rank"] = cases["margin"].fillna(-1)
    cases = cases.sort_values(
        ["strong_flag_rank", "model_rank", "confidence_rank", "margin_rank"],
        ascending=[True, True, False, False],
    )
    cols = [
        "dataset_id",
        "fold",
        "cell_id",
        "model",
        "truth",
        "label",
        "confidence",
        "margin",
        "conflict_reason",
        "explicit_conflict_flag",
        "low_margin_flag",
    ]
    return cases[cols].head(n).reset_index(drop=True)


def write_report(summary: pd.DataFrame, examples: pd.DataFrame, confirmed: pd.DataFrame) -> None:
    total_flagged = int(summary["audit_flagged"].sum())
    total_flagged_errors = int(summary["expert_confirmed_flagged_errors"].sum())
    unique_confirmed = confirmed.drop_duplicates(["dataset_id", "cell_id"]).shape[0]
    precision = total_flagged_errors / total_flagged if total_flagged else float("nan")
    local_available = examples["local_context_interpretation"].ne("metadata unavailable").sum()
    local_supportive = examples["local_context_interpretation"].isin(
        [
            "local majority supports expert label",
            "predicted label absent from local neighbors",
            "local neighbors favor expert label over prediction",
        ]
    ).sum()
    lines = [
        "# Biological Audit Casebook",
        "",
        "This casebook converts benchmark errors into reviewable biological audit events.",
        "A case is included when NicheTypeR or an external annotation output is flagged",
        "by the audit layer and the held-out author/expert label confirms that the",
        "predicted label is wrong.",
        "",
        f"Across all call tables, {total_flagged:,} predictions were audit-flagged and",
        f"{total_flagged_errors:,} of them were expert-confirmed model-call errors",
        f"(precision {precision:.3f}).",
        f"These correspond to {unique_confirmed:,} unique dataset-cell or dataset-spot",
        "events after removing duplicate model calls.",
        f"The released example table contains {len(examples):,} high-priority cases;",
        f"{local_available:,} have local metadata and {local_supportive:,} show local",
        "neighborhood evidence that either favors the expert label or makes the",
        "predicted label spatially implausible.",
        "",
        "## Highest-Precision Dataset/Model Strata",
        "",
        "| dataset | model | calls | audit flagged | confirmed flagged errors | precision | wrong-call rate |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary.head(20).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.model} | {row.n_calls} | {row.audit_flagged} | "
            f"{row.expert_confirmed_flagged_errors} | {row.audit_flag_precision:.3f} | "
            f"{row.wrong_call_rate:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Representative Expert-Confirmed Flagged Errors",
            "",
            "| dataset | model | expert label | predicted label | reason | local interpretation |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in examples.head(30).itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.model} | {row.truth} | {row.label} | "
            f"{row.conflict_reason} | {row.local_context_interpretation} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is not a prospective pathology re-annotation experiment. The independent",
            "evidence is the held-out author/expert label, with local-neighborhood summaries",
            "added when metadata are available. The result supports a narrower but testable",
            "claim: NicheTypeR can prioritize concrete, biologically inspectable annotation",
            "problems rather than only reporting aggregate F1 changes.",
            "",
        ]
    )
    (OUT_PREFIX.with_suffix(".md")).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    calls = load_calls()
    summary = summarize(calls)
    examples = add_local_neighborhood_support(select_examples(calls, n=300))

    confirmed = calls[calls["expert_confirmed_flagged_error"]].copy()
    confirmed_cols = [
        "dataset_id",
        "fold",
        "cell_id",
        "model",
        "truth",
        "label",
        "confidence",
        "margin",
        "conflict_reason",
        "explicit_conflict_flag",
        "low_margin_flag",
    ]
    summary.to_csv(OUT_PREFIX.with_name("BIOLOGICAL_AUDIT_CASEBOOK_summary.csv"), index=False)
    examples.to_csv(OUT_PREFIX.with_name("BIOLOGICAL_AUDIT_CASEBOOK_examples.csv"), index=False)
    confirmed[confirmed_cols].to_csv(
        OUT_PREFIX.with_name("BIOLOGICAL_AUDIT_CASEBOOK_confirmed_cases.csv"),
        index=False,
    )
    write_report(summary, examples, confirmed)
    print(summary.head(12).to_string(index=False))
    print(f"\nWrote {len(examples)} prioritized examples and {len(confirmed)} confirmed flagged errors.")


if __name__ == "__main__":
    main()
