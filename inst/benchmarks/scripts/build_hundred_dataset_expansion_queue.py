from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "PUBLIC_SPATIAL_DATASET_CATALOG_FULL.csv"
PREVIEW = ROOT / "DATASET_PREVIEW_VALIDATION.csv"
EXPANDED = ROOT / "EXPANDED_SCALE_DATASETS.csv"
LOCAL_AUDIT = ROOT / "LOCAL_GEO_INGESTION_AUDIT_summary.csv"
DOWNLOAD_REPORT = ROOT / "HUNDRED_DATASET_DOWNLOAD_REPORT.csv"
DEFAULT_GEO100_ROOT = Path(r"D:\NicheTypeR_GEO_100_QUEUE")
CONTINUOUS_STATE = DEFAULT_GEO100_ROOT / "CONTINUOUS_EXPANSION_STATE.json"

QUEUE_OUT = ROOT / "HUNDRED_DATASET_EXPANSION_QUEUE.csv"
SUMMARY_OUT = ROOT / "HUNDRED_DATASET_EXPANSION_QUEUE_summary.csv"
REPORT_OUT = ROOT / "HUNDRED_DATASET_EXPANSION_QUEUE_report.json"
MD_OUT = ROOT / "HUNDRED_DATASET_EXPANSION_QUEUE.md"

TARGET_SOURCE_DATASETS = 100

TIER_RANK = {
    "benchmark_ready_processed": 0,
    "expanded_scale_validation": 1,
    "downloaded_candidate": 2,
    "partial_download_candidate": 3,
    "manifest_only_candidate": 4,
    "tier1_likely_benchmark_ready_h5ad": 5,
    "tier2_likely_benchmark_ready_files": 6,
    "tier3_high_priority_manual_review": 7,
    "tier4_candidate_manual_review": 8,
    "screened_low_priority": 9,
}


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def source_from_dataset_id(dataset_id: str) -> str:
    if dataset_id.startswith("SQUIDPY_"):
        return dataset_id
    for part in dataset_id.split("_"):
        if part.startswith("GSE"):
            return part
    if dataset_id.startswith("GSE"):
        return dataset_id.split("_", 1)[0]
    return dataset_id


def completed_sources() -> tuple[pd.DataFrame, dict[str, int]]:
    rows = []
    config_counts: dict[str, int] = {}

    if PREVIEW.exists():
        preview = pd.read_csv(PREVIEW)
        for row in preview.itertuples(index=False):
            dataset_id = str(getattr(row, "dataset_id", ""))
            source = source_from_dataset_id(dataset_id)
            config_counts[source] = config_counts.get(source, 0) + 1
            rows.append(
                {
                    "source_id": source,
                    "accession": source if source.startswith("GSE") else "",
                    "dataset_id": dataset_id,
                    "source_type": "current_preview_benchmark",
                    "completed_configurations": 1,
                    "completed_cells_or_spots": int(getattr(row, "preview_cells", 0) or 0),
                    "completed_labels": int(getattr(row, "n_labels", 0) or 0),
                }
            )

    if EXPANDED.exists():
        expanded = pd.read_csv(EXPANDED)
        for row in expanded.itertuples(index=False):
            source = str(getattr(row, "source_dataset_id", ""))
            dataset_id = str(getattr(row, "dataset_id", ""))
            config_counts[source] = config_counts.get(source, 0) + 1
            rows.append(
                {
                    "source_id": source,
                    "accession": source if source.startswith("GSE") else "",
                    "dataset_id": dataset_id,
                    "source_type": "current_expanded_benchmark",
                    "completed_configurations": 1,
                    "completed_cells_or_spots": int(getattr(row, "expanded_cells", 0) or 0),
                    "completed_labels": int(getattr(row, "n_labels", 0) or 0),
                }
            )

    return pd.DataFrame(rows), config_counts


def local_audit_status() -> dict[str, str]:
    if not LOCAL_AUDIT.exists():
        return {}
    audit = pd.read_csv(LOCAL_AUDIT)
    out = {}
    for row in audit.itertuples(index=False):
        acc = str(getattr(row, "accession", ""))
        ready_reason = []
        for col in ["has_expression", "has_coordinates", "has_label_or_domain"]:
            if col in audit.columns:
                ready_reason.append(f"{col}={getattr(row, col)}")
        out[acc] = "; ".join(ready_reason)
    return out


def screened_not_ready_accessions() -> dict[str, str]:
    screened: dict[str, str] = {}
    if DOWNLOAD_REPORT.exists() and DOWNLOAD_REPORT.stat().st_size > 2:
        try:
            report = pd.read_csv(DOWNLOAD_REPORT)
            for row in report.itertuples(index=False):
                acc = str(getattr(row, "accession", ""))
                status = str(getattr(row, "status", ""))
                note = str(getattr(row, "note", ""))
                if acc.startswith("GSE") and status in {"not_benchmark_ready_filelist", "filelist_error"}:
                    screened[acc] = f"download preflight: {status}; {note}"
        except Exception:
            pass
    if CONTINUOUS_STATE.exists():
        try:
            state = json.loads(CONTINUOUS_STATE.read_text(encoding="utf-8"))
            for acc, item in state.get("accessions", {}).items():
                acc = str(acc)
                if not acc.startswith("GSE"):
                    continue
                status = str(item.get("status", ""))
                reason = str(item.get("reason", item.get("prepare_result", {}).get("reason", "")))
                if status == "not_preparable" and reason and "missing raw dir" not in reason.lower():
                    screened.setdefault(acc, f"prepare preflight: {reason}")
        except Exception:
            pass
    return screened


def queue_status(row: pd.Series, completed: set[str]) -> tuple[str, str]:
    acc = str(row["accession"])
    tier = str(row["readiness_tier"])
    size_gb = float(row.get("total_supp_size_gb", 0) or 0)
    file_count = int(row.get("file_count", 0) or 0)
    has_h5ad = as_bool(row.get("has_h5ad", False))
    has_label = as_bool(row.get("has_label_evidence", False))
    has_expr = as_bool(row.get("has_expression_evidence", False))
    has_coord = as_bool(row.get("has_coordinate_evidence", False))

    if acc in completed:
        return "completed_current_benchmark", "already represented in preview and/or expanded validation"
    if tier == "downloaded_candidate":
        return "local_downloaded_needs_label_or_parser", "local files exist; previous audit did not confirm a supervised label/domain field"
    if tier == "partial_download_candidate":
        return "resume_download_and_parse", "partial local download exists; resume and inspect labels"
    if tier == "manifest_only_candidate":
        return "manifest_review_before_download", "manifest exists but no usable local data yet"
    if tier == "tier1_likely_benchmark_ready_h5ad":
        if size_gb <= 5 or file_count == 0:
            return "download_now_h5ad_priority", "h5ad evidence and full evidence set; manageable or unknown size"
        return "defer_large_h5ad", "h5ad evidence but accession is large; download sample-level files only"
    if tier == "tier2_likely_benchmark_ready_files":
        if size_gb <= 2 or file_count == 0:
            return "download_now_structured_files", "expression, coordinate and label evidence; manageable or unknown size"
        if size_gb <= 5:
            return "download_after_h5ad_queue", "structured files but larger than preferred first pass"
        return "defer_large_structured_files", "large structured-file accession; require sample-level filtering"
    if tier == "tier3_high_priority_manual_review":
        if has_h5ad and (size_gb <= 2 or file_count == 0):
            return "manual_review_h5ad_possible", "h5ad found but automated label evidence is weak"
        if has_expr and has_coord and has_label:
            return "manual_review_possible", "all evidence fields present but lower automated score"
        return "manual_review_low_label_confidence", "insufficient automated evidence for immediate benchmark use"
    return "low_priority", "not selected before higher-readiness candidates"


def build_queue() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    if not CATALOG.exists():
        raise FileNotFoundError(f"Missing catalog: {CATALOG}")

    catalog = pd.read_csv(CATALOG)
    completed_df, config_counts = completed_sources()
    completed = set(config_counts)
    audit = local_audit_status()
    screened_not_ready = screened_not_ready_accessions()

    rows = []
    for _, row in catalog.iterrows():
        acc = str(row["accession"])
        status, action_note = queue_status(row, completed)
        source_id = acc
        rows.append(
            {
                "source_id": source_id,
                "accession": acc,
                "catalog_rank": int(row["catalog_rank"]),
                "target_rank": None,
                "benchmark_status": status,
                "readiness_tier": row["readiness_tier"],
                "completed_configurations": config_counts.get(source_id, 0),
                "score": int(row["score"]),
                "title": row["title"],
                "taxon": row.get("taxon", ""),
                "publication_date": row.get("publication_date", ""),
                "n_samples": int(row.get("n_samples", 0) or 0),
                "file_count": int(row.get("file_count", 0) or 0),
                "total_supp_size_gb": float(row.get("total_supp_size_gb", 0) or 0),
                "has_h5ad": as_bool(row.get("has_h5ad", False)),
                "has_expression_evidence": as_bool(row.get("has_expression_evidence", False)),
                "has_coordinate_evidence": as_bool(row.get("has_coordinate_evidence", False)),
                "has_label_evidence": as_bool(row.get("has_label_evidence", False)),
                "filelist_url": row.get("filelist_url", ""),
                "geo_url": row.get("geo_url", ""),
                "h5ad_examples": row.get("h5ad_examples", ""),
                "expression_examples": row.get("expression_examples", ""),
                "coordinate_examples": row.get("coordinate_examples", ""),
                "label_examples": row.get("label_examples", ""),
                "local_audit_note": audit.get(acc, ""),
                "action_note": action_note,
            }
        )

    queue = pd.DataFrame(rows)
    if screened_not_ready:
        mask = queue["accession"].astype(str).isin(screened_not_ready) & (queue["benchmark_status"] != "completed_current_benchmark")
        queue.loc[mask, "benchmark_status"] = "screened_not_benchmark_ready"
        queue.loc[mask, "readiness_tier"] = "screened_low_priority"
        queue.loc[mask, "action_note"] = queue.loc[mask, "accession"].map(screened_not_ready)

    non_geo_completed = []
    if not completed_df.empty:
        for source, group in completed_df.groupby("source_id"):
            if str(source).startswith("GSE"):
                continue
            non_geo_completed.append(
                {
                    "source_id": source,
                    "accession": "",
                    "catalog_rank": 0,
                    "target_rank": None,
                    "benchmark_status": "completed_current_benchmark",
                    "readiness_tier": "non_geo_completed",
                    "completed_configurations": int(group.shape[0]),
                    "score": 0,
                    "title": f"{source} processed example dataset",
                    "taxon": "",
                    "publication_date": "",
                    "n_samples": "",
                    "file_count": "",
                    "total_supp_size_gb": 0.0,
                    "has_h5ad": True,
                    "has_expression_evidence": True,
                    "has_coordinate_evidence": True,
                    "has_label_evidence": True,
                    "filelist_url": "",
                    "geo_url": "",
                    "h5ad_examples": "",
                    "expression_examples": "",
                    "coordinate_examples": "",
                    "label_examples": "",
                    "local_audit_note": "",
                    "action_note": "already represented in current benchmark",
                }
            )
    if non_geo_completed:
        queue = pd.concat([pd.DataFrame(non_geo_completed), queue], ignore_index=True)

    status_rank = {
        "completed_current_benchmark": 0,
        "download_now_h5ad_priority": 1,
        "download_now_structured_files": 2,
        "resume_download_and_parse": 3,
        "local_downloaded_needs_label_or_parser": 4,
        "download_after_h5ad_queue": 5,
        "manual_review_h5ad_possible": 6,
        "manifest_review_before_download": 7,
        "manual_review_possible": 8,
        "defer_large_h5ad": 9,
        "defer_large_structured_files": 10,
        "manual_review_low_label_confidence": 11,
        "low_priority": 12,
        "screened_not_benchmark_ready": 13,
    }
    queue["_status_rank"] = queue["benchmark_status"].map(status_rank).fillna(99).astype(int)
    queue["_tier_rank"] = queue["readiness_tier"].map(TIER_RANK).fillna(99).astype(int)
    queue["_small_first"] = queue["total_supp_size_gb"].replace("", 0).astype(float)
    queue = queue.sort_values(
        [
            "_status_rank",
            "completed_configurations",
            "_tier_rank",
            "has_h5ad",
            "has_label_evidence",
            "_small_first",
            "score",
            "catalog_rank",
        ],
        ascending=[True, False, True, False, False, True, False, True],
    ).drop(columns=["_status_rank", "_tier_rank", "_small_first"])

    queue = queue.drop_duplicates("source_id", keep="first").reset_index(drop=True)
    queue = queue.head(max(TARGET_SOURCE_DATASETS, len(completed))).copy()
    queue["target_rank"] = range(1, len(queue) + 1)

    summary = (
        queue.groupby("benchmark_status", dropna=False)
        .agg(
            n_sources=("source_id", "count"),
            completed_configurations=("completed_configurations", "sum"),
            median_supp_gb=("total_supp_size_gb", "median"),
            total_supp_gb=("total_supp_size_gb", "sum"),
        )
        .reset_index()
        .sort_values("n_sources", ascending=False)
    )

    report = {
        "target_source_datasets": TARGET_SOURCE_DATASETS,
        "queued_source_datasets": int(queue.shape[0]),
        "completed_source_datasets": int((queue["benchmark_status"] == "completed_current_benchmark").sum()),
        "completed_benchmark_configurations": int(queue["completed_configurations"].sum()),
        "remaining_source_datasets_to_100": int(max(0, TARGET_SOURCE_DATASETS - (queue["benchmark_status"] == "completed_current_benchmark").sum())),
        "download_now_sources": int(queue["benchmark_status"].isin(["download_now_h5ad_priority", "download_now_structured_files"]).sum()),
        "resume_or_local_sources": int(queue["benchmark_status"].isin(["resume_download_and_parse", "local_downloaded_needs_label_or_parser"]).sum()),
        "large_or_manual_sources": int(queue["benchmark_status"].str.contains("defer|manual|manifest", regex=True).sum()),
    }
    return queue, summary, report


def write_markdown(queue: pd.DataFrame, summary: pd.DataFrame, report: dict) -> None:
    lines = [
        "# Hundred-Dataset Expansion Queue",
        "",
        "This file operationalizes the target of expanding NicheTypeR validation to",
        "approximately 100 public source datasets. It is a training and ingestion",
        "queue, not a claim that 100 datasets have already completed validation.",
        "",
        "## Current Count",
        "",
        f"- target public source datasets: {report['target_source_datasets']}",
        f"- queued source datasets: {report['queued_source_datasets']}",
        f"- completed source datasets already represented: {report['completed_source_datasets']}",
        f"- completed benchmark configurations already represented: {report['completed_benchmark_configurations']}",
        f"- source datasets still needed to reach 100 completed sources: {report['remaining_source_datasets_to_100']}",
        f"- immediate download candidates: {report['download_now_sources']}",
        f"- local/resume candidates: {report['resume_or_local_sources']}",
        "",
        "## Queue Status Summary",
        "",
        "| status | source datasets | completed configurations | median GB | total GB |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.benchmark_status} | {int(row.n_sources):,} | "
            f"{int(row.completed_configurations):,} | {float(row.median_supp_gb):.3f} | {float(row.total_supp_gb):.3f} |"
        )

    lines.extend(
        [
            "",
            "## First 40 Targets",
            "",
            "| rank | source | status | tier | GB | title |",
            "|---:|---|---|---|---:|---|",
        ]
    )
    for row in queue.head(40).itertuples(index=False):
        title = str(row.title).replace("|", "/")[:90]
        lines.append(
            f"| {int(row.target_rank)} | {row.source_id} | {row.benchmark_status} | "
            f"{row.readiness_tier} | {float(row.total_supp_size_gb or 0):.3f} | {title} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The honest manuscript language after this step is: NicheTypeR currently has",
            "completed validation on the existing preview and expanded benchmark",
            "configurations, and now includes a locked 100-source expansion queue.",
            "Only entries that complete expression/coordinate/label parsing and blocked",
            "validation should be counted as trained or benchmarked datasets.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    queue, summary, report = build_queue()
    queue.to_csv(QUEUE_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(queue, summary, report)
    print(json.dumps(report, indent=2))
    print(f"wrote {QUEUE_OUT}")


if __name__ == "__main__":
    main()
