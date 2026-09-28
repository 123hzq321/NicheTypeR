from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
CALLS = ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_calls.csv"
REFERENCE_CALLS = ROOT / "REFERENCE_PROFILE_BASELINE_calls.csv"
GUARDRAIL = ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv"
SUMMARY_OUT = ROOT / "ANNOTATION_AUDIT_CASE_STUDY_summary.csv"
EXAMPLES_OUT = ROOT / "ANNOTATION_AUDIT_CASE_STUDY_examples.csv"
REPORT_OUT = ROOT / "ANNOTATION_AUDIT_CASE_STUDY.md"


COMPARATORS = [
    "reference_profile",
    "marker_reference_profile",
    "marker_spatial_smoothing",
    "marker_learned_neighborhood",
    "reference_profile_learned_neighborhood",
    "marker_context_specific_neighborhood",
]


def paired_rows(calls: pd.DataFrame, comparator: str) -> pd.DataFrame:
    marker = calls[calls["model"] == "marker_only"].copy()
    other = calls[calls["model"] == comparator].copy()
    marker = marker.set_index(["dataset_id", "fold", "cell_id"]).sort_index()
    other = other.set_index(["dataset_id", "fold", "cell_id"]).sort_index()
    common = marker.index.intersection(other.index)
    marker = marker.loc[common]
    other = other.loc[common]
    out = pd.DataFrame({
        "dataset_id": marker.index.get_level_values("dataset_id"),
        "fold": marker.index.get_level_values("fold"),
        "cell_id": marker.index.get_level_values("cell_id"),
        "truth": marker["truth"].astype(str).to_numpy(),
        "marker_label": marker["label"].astype(str).to_numpy(),
        "comparator_label": other["label"].astype(str).to_numpy(),
        "marker_correct": marker["correct"].astype(bool).to_numpy(),
        "comparator_correct": other["correct"].astype(bool).to_numpy(),
        "marker_confidence": marker["confidence"].astype(float).to_numpy(),
        "comparator_confidence": other["confidence"].astype(float).to_numpy(),
        "marker_margin": marker["margin"].astype(float).to_numpy(),
        "comparator_margin": other["margin"].astype(float).to_numpy(),
        "marker_conflict_reason": marker["conflict_reason"].astype(str).to_numpy(),
        "comparator_conflict_reason": other["conflict_reason"].astype(str).to_numpy(),
    })
    out["comparator_model"] = comparator
    out["change_type"] = "unchanged"
    out.loc[~out["marker_correct"] & out["comparator_correct"], "change_type"] = "context_rescue"
    out.loc[out["marker_correct"] & ~out["comparator_correct"], "change_type"] = "context_harm"
    out.loc[~out["marker_correct"] & ~out["comparator_correct"] & (out["marker_label"] != out["comparator_label"]), "change_type"] = "changed_but_still_wrong"
    out.loc[out["marker_correct"] & out["comparator_correct"] & (out["marker_label"] != out["comparator_label"]), "change_type"] = "changed_between_correct_synonyms"
    out["confidence_gain"] = out["comparator_confidence"] - out["marker_confidence"]
    out["margin_gain"] = out["comparator_margin"] - out["marker_margin"]
    return out


def summarize(paired: pd.DataFrame, guardrail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    guardrail = guardrail.set_index("dataset_id") if not guardrail.empty else pd.DataFrame()
    for (dataset_id, comparator), df in paired.groupby(["dataset_id", "comparator_model"], sort=False):
        counts = df["change_type"].value_counts()
        n = len(df)
        row = {
            "dataset_id": dataset_id,
            "comparator_model": comparator,
            "n": n,
            "context_rescue": int(counts.get("context_rescue", 0)),
            "context_harm": int(counts.get("context_harm", 0)),
            "changed_but_still_wrong": int(counts.get("changed_but_still_wrong", 0)),
            "unchanged": int(counts.get("unchanged", 0)),
            "rescue_rate": float(counts.get("context_rescue", 0) / n) if n else 0.0,
            "harm_rate": float(counts.get("context_harm", 0) / n) if n else 0.0,
            "net_rescue_minus_harm": int(counts.get("context_rescue", 0) - counts.get("context_harm", 0)),
        }
        if dataset_id in guardrail.index:
            row["learned_passes_guardrail"] = bool(guardrail.loc[dataset_id, "learned_passes_guardrail"])
            row["smoothing_passes_guardrail"] = bool(guardrail.loc[dataset_id, "smoothing_passes_guardrail"])
            row["context_specific_passes_guardrail"] = bool(guardrail.loc[dataset_id, "context_specific_passes_guardrail"])
            row["guardrail_interpretation"] = str(guardrail.loc[dataset_id, "interpretation"])
        rows.append(row)
    return pd.DataFrame(rows)


def select_examples(paired: pd.DataFrame, n_per_group: int = 8) -> pd.DataFrame:
    examples = []
    for (dataset_id, comparator, change_type), df in paired.groupby(
        ["dataset_id", "comparator_model", "change_type"],
        sort=False,
    ):
        if change_type not in {"context_rescue", "context_harm", "changed_but_still_wrong"}:
            continue
        ranked = df.sort_values(
            ["comparator_margin", "comparator_confidence", "confidence_gain"],
            ascending=False,
        ).head(n_per_group)
        examples.append(ranked)
    if not examples:
        return pd.DataFrame()
    keep_cols = [
        "dataset_id", "fold", "cell_id", "comparator_model", "change_type",
        "truth", "marker_label", "comparator_label", "marker_confidence",
        "comparator_confidence", "marker_margin", "comparator_margin",
        "confidence_gain", "margin_gain", "marker_conflict_reason",
        "comparator_conflict_reason",
    ]
    return pd.concat(examples, ignore_index=True)[keep_cols]


def write_report(summary: pd.DataFrame, examples: pd.DataFrame) -> None:
    lines = [
        "# Annotation Audit Case Study",
        "",
        "This report translates per-cell benchmark calls into audit-style cases.",
        "A `context_rescue` is a held-out cell or spot where marker-only annotation",
        "is wrong but a comparator that adds reference or context evidence is",
        "correct. A `context_harm` is the opposite: marker-only is correct but the",
        "comparator changes the call to an incorrect label.",
        "",
        "The point is not to claim universal accuracy gains. The point is to show",
        "where NicheTypeR can surface actionable annotation conflicts and where",
        "context evidence should be treated cautiously.",
        "",
        "## Net Rescue Summary",
        "",
        "| dataset | comparator | rescue | harm | net | rescue rate | harm rate |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    ordered = summary.sort_values(
        ["comparator_model", "net_rescue_minus_harm", "rescue_rate"],
        ascending=[True, False, False],
    )
    for row in ordered.itertuples(index=False):
        lines.append(
            f"| {row.dataset_id} | {row.comparator_model} | {row.context_rescue} | "
            f"{row.context_harm} | {row.net_rescue_minus_harm:+d} | "
            f"{row.rescue_rate:.4f} | {row.harm_rate:.4f} |"
        )

    best = summary.sort_values("net_rescue_minus_harm", ascending=False).head(12)
    lines.extend([
        "",
        "## Highest Net Rescue Settings",
        "",
        "| dataset | comparator | net rescue minus harm | guardrail interpretation |",
        "|---|---|---:|---|",
    ])
    for row in best.itertuples(index=False):
        interpretation = getattr(row, "guardrail_interpretation", "")
        lines.append(f"| {row.dataset_id} | {row.comparator_model} | {row.net_rescue_minus_harm:+d} | {interpretation} |")

    if not examples.empty:
        lines.extend([
            "",
            "## Example Audit Events",
            "",
            "| dataset | comparator | change | truth | marker label | comparator label | marker conf. | comparator conf. |",
            "|---|---|---|---|---|---|---:|---:|",
        ])
        for row in examples.head(40).itertuples(index=False):
            lines.append(
                f"| {row.dataset_id} | {row.comparator_model} | {row.change_type} | "
                f"{row.truth} | {row.marker_label} | {row.comparator_label} | "
                f"{row.marker_confidence:.3f} | {row.comparator_confidence:.3f} |"
            )

    lines.extend([
        "",
        "## Manuscript Use",
        "",
        "This report supports a focused claim: NicheTypeR is an annotation-audit",
        "layer. It can quantify where reference/context evidence rescues a marker",
        "call, where it harms a correct marker call, and where a conflict should be",
        "sent back to expert review rather than silently accepted.",
        "",
    ])
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    calls = pd.read_csv(CALLS)
    if REFERENCE_CALLS.exists():
        reference_calls = pd.read_csv(REFERENCE_CALLS)
        calls = pd.concat([calls, reference_calls], ignore_index=True, sort=False)
    guardrail = pd.read_csv(GUARDRAIL) if GUARDRAIL.exists() else pd.DataFrame()
    pieces = []
    for comparator in COMPARATORS:
        if comparator in set(calls["model"]):
            pieces.append(paired_rows(calls, comparator))
    if not pieces:
        raise RuntimeError("No requested comparator models were found in the calls table.")
    paired = pd.concat(pieces, ignore_index=True)
    summary = summarize(paired, guardrail)
    examples = select_examples(paired)
    summary.to_csv(SUMMARY_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)
    write_report(summary, examples)
    print(summary.sort_values("net_rescue_minus_harm", ascending=False).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
