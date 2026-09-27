from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent

PREVIEW_GUARDRAIL = ROOT / "MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv"
EXPANDED_GUARDRAIL = ROOT / "EXPANDED_SCALE_LEAN_BENCHMARK_guardrail.csv"
LABEL_TASKS = ROOT / "LABEL_TASK_BENCHMARK.csv"

DATASET_THRESHOLDS_OUT = ROOT / "THRESHOLD_SENSITIVITY_dataset_level.csv"
LABEL_THRESHOLDS_OUT = ROOT / "THRESHOLD_SENSITIVITY_label_tasks.csv"
DATASET_TIERS_OUT = ROOT / "THRESHOLD_SENSITIVITY_dataset_tiers.csv"
LABEL_TIERS_OUT = ROOT / "THRESHOLD_SENSITIVITY_label_task_tiers.csv"
REPORT_OUT = ROOT / "THRESHOLD_SENSITIVITY_AND_TIERS.md"
FIGURE_PNG = ROOT / "figure_threshold_sensitivity.png"
FIGURE_PDF = ROOT / "figure_threshold_sensitivity.pdf"
FIGURE_EPS = ROOT / "figure_threshold_sensitivity.eps"
FIGURE_SVG = ROOT / "figure_threshold_sensitivity.svg"


DATASET_THRESHOLDS = [0.0, 0.001, 0.0025, 0.005, 0.0075, 0.01, 0.02]
LABEL_THRESHOLDS = [0.0, 0.001, 0.0025, 0.005, 0.01, 0.02, 0.05]


def read_dataset_guardrails() -> pd.DataFrame:
    frames = []
    if PREVIEW_GUARDRAIL.exists():
        preview = pd.read_csv(PREVIEW_GUARDRAIL)
        preview["scale"] = "preview"
        frames.append(preview)
    if EXPANDED_GUARDRAIL.exists():
        expanded = pd.read_csv(EXPANDED_GUARDRAIL)
        expanded["scale"] = "expanded"
        frames.append(expanded)
    if not frames:
        raise FileNotFoundError("No dataset-level guardrail tables found.")
    return pd.concat(frames, ignore_index=True, sort=False)


def count_dataset_passes(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for threshold in DATASET_THRESHOLDS:
        for scale, group in [("all", df), *df.groupby("scale")]:
            learned = (
                (group["learned_specific_macro_f1_delta"] > threshold)
                & (group["learned_specific_accuracy_delta"] > 0)
            )
            context = (
                (group["context_specific_macro_f1_delta"] > threshold)
                & (group["context_specific_accuracy_delta"] > 0)
            )
            rows.append(
                {
                    "scale": scale,
                    "macro_f1_delta_threshold": threshold,
                    "n_dataset_configs": int(len(group)),
                    "learned_neighborhood_configs": int(learned.sum()),
                    "context_residual_configs": int(context.sum()),
                    "learned_neighborhood_fraction": float(learned.mean()) if len(group) else 0.0,
                    "context_residual_fraction": float(context.mean()) if len(group) else 0.0,
                }
            )
    return pd.DataFrame(rows)


def dataset_tiers(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scale, group in [("all", df), *df.groupby("scale")]:
        learned_positive = (
            (group["learned_specific_macro_f1_delta"] > 0)
            & (group["learned_specific_accuracy_delta"] > 0)
        )
        learned_strict = (
            (group["learned_specific_macro_f1_delta"] > 0.005)
            & (group["learned_specific_accuracy_delta"] > 0)
        )
        context_positive = (
            (group["context_specific_macro_f1_delta"] > 0)
            & (group["context_specific_accuracy_delta"] > 0)
        )
        context_strict = (
            (group["context_specific_macro_f1_delta"] > 0.005)
            & (group["context_specific_accuracy_delta"] > 0)
        )
        rows.extend(
            [
                {
                    "scale": scale,
                    "evidence_layer": "learned_neighborhood",
                    "n_dataset_configs": int(len(group)),
                    "strict_support": int(learned_strict.sum()),
                    "directional_support": int((learned_positive & ~learned_strict).sum()),
                    "no_directional_support": int((~learned_positive).sum()),
                },
                {
                    "scale": scale,
                    "evidence_layer": "context_residual",
                    "n_dataset_configs": int(len(group)),
                    "strict_support": int(context_strict.sum()),
                    "directional_support": int((context_positive & ~context_strict).sum()),
                    "no_directional_support": int((~context_positive).sum()),
                },
            ]
        )
    return pd.DataFrame(rows)


def count_label_task_passes(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for threshold in LABEL_THRESHOLDS:
        for scale, group in [("all", df), *df.groupby("scale")]:
            learned = group["learned_specific_f1_delta"] > threshold
            context = group["context_specific_f1_delta"] > threshold
            rows.append(
                {
                    "scale": scale,
                    "label_f1_delta_threshold": threshold,
                    "n_label_tasks": int(len(group)),
                    "learned_neighborhood_tasks": int(learned.sum()),
                    "context_residual_tasks": int(context.sum()),
                    "learned_neighborhood_fraction": float(learned.mean()) if len(group) else 0.0,
                    "context_residual_fraction": float(context.mean()) if len(group) else 0.0,
                }
            )
    return pd.DataFrame(rows)


def label_task_tiers(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scale, group in [("all", df), *df.groupby("scale")]:
        for layer, col in [
            ("learned_neighborhood", "learned_specific_f1_delta"),
            ("context_residual", "context_specific_f1_delta"),
        ]:
            values = group[col]
            eligible = values.notna()
            strong = values > 0.01
            suggestive = (values > 0) & (values <= 0.01)
            rows.append(
                {
                    "scale": scale,
                    "evidence_layer": layer,
                    "n_label_tasks": int(len(group)),
                    "n_eligible_label_tasks": int(eligible.sum()),
                    "strong_support_delta_gt_0_01": int(strong.sum()),
                    "suggestive_support_delta_0_to_0_01": int(suggestive.sum()),
                    "no_gain_or_harm": int((eligible & ~(strong | suggestive)).sum()),
                    "missing_matched_null_delta": int((~eligible).sum()),
                }
            )
    return pd.DataFrame(rows)


def fmt_count(n: int, d: int) -> str:
    return f"{n}/{d}"


def markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].itertuples(index=False):
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return out


def write_report(
    dataset_thresholds: pd.DataFrame,
    label_thresholds: pd.DataFrame,
    dataset_tier_df: pd.DataFrame,
    label_tier_df: pd.DataFrame,
) -> None:
    all_dataset = dataset_thresholds[dataset_thresholds["scale"] == "all"].copy()
    all_label = label_thresholds[label_thresholds["scale"] == "all"].copy()
    all_dataset["learned"] = all_dataset.apply(
        lambda r: fmt_count(int(r.learned_neighborhood_configs), int(r.n_dataset_configs)), axis=1
    )
    all_dataset["context"] = all_dataset.apply(
        lambda r: fmt_count(int(r.context_residual_configs), int(r.n_dataset_configs)), axis=1
    )
    all_label["learned"] = all_label.apply(
        lambda r: fmt_count(int(r.learned_neighborhood_tasks), int(r.n_label_tasks)), axis=1
    )
    all_label["context"] = all_label.apply(
        lambda r: fmt_count(int(r.context_residual_tasks), int(r.n_label_tasks)), axis=1
    )

    lines = [
        "# Threshold Sensitivity and Tiered Support",
        "",
        "This analysis does not change the primary strict guardrail. It adds an",
        "interpretive sensitivity analysis so that the benchmark is not reduced to",
        "one pass/fail threshold. The prespecified strict dataset-level criterion",
        "remains macro-F1 specific delta > 0.005 together with positive accuracy",
        "delta and matched-null improvement.",
        "",
        "## Dataset-Level Threshold Sensitivity",
        "",
        "| macro-F1 delta threshold | learned-neighborhood configs | context-residual configs |",
        "|---:|---:|---:|",
    ]
    for row in all_dataset.itertuples(index=False):
        lines.append(f"| {row.macro_f1_delta_threshold:g} | {row.learned} | {row.context} |")

    lines.extend(
        [
            "",
            "Interpretation: the strict 0.005 cutoff gives 5/34 learned-neighborhood",
            "configurations and 0/34 context-residual configurations. As an",
            "exploratory directional readout, a zero cutoff gives 14/34 and 2/34,",
            "respectively. This should be described as sensitivity, not as a new",
            "success criterion.",
            "",
            "## Dataset-Level Tiered Support",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            dataset_tier_df[dataset_tier_df["scale"] == "all"],
            [
                "evidence_layer",
                "n_dataset_configs",
                "strict_support",
                "directional_support",
                "no_directional_support",
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Label-Task Threshold Sensitivity",
            "",
            "Label tasks are dataset-label pairs. They are useful for review triage",
            "and case-study selection, but they are not independent cohorts.",
            "",
            "| label-task F1 delta threshold | learned-neighborhood tasks | context-residual tasks |",
            "|---:|---:|---:|",
        ]
    )
    for row in all_label.itertuples(index=False):
        lines.append(f"| {row.label_f1_delta_threshold:g} | {row.learned} | {row.context} |")

    lines.extend(["", "## Label-Task Tiered Support", ""])
    lines.extend(
        markdown_table(
            label_tier_df[label_tier_df["scale"] == "all"],
            [
                "evidence_layer",
                "n_label_tasks",
                "n_eligible_label_tasks",
                "strong_support_delta_gt_0_01",
                "suggestive_support_delta_0_to_0_01",
                "no_gain_or_harm",
                "missing_matched_null_delta",
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Manuscript Wording",
            "",
            "Recommended main-text framing:",
            "",
            "> The prespecified strict dataset-level guardrail identified a small set",
            "> of strong learned-neighborhood gains. Threshold-sensitivity analyses",
            "> showed additional directional support under exploratory cutoffs, and",
            "> label-task analyses identified many candidate labels where context",
            "> evidence was useful for triage. We therefore report strict guardrails",
            "> as the primary generalization result and tiered support as a review-",
            "> prioritization analysis.",
            "",
            "Avoid presenting exploratory thresholds as if they replace the strict",
            "guardrail. The clean hierarchy is: strict dataset-level result for",
            "generalization; threshold sensitivity for robustness; label-task tiers",
            "for practical review triage.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure(dataset_thresholds: pd.DataFrame, label_thresholds: pd.DataFrame) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print(f"Matplotlib unavailable; writing dependency-free SVG/EPS instead: {exc}")
        write_dependency_free_figure(dataset_thresholds, label_thresholds)
        return

    ds = dataset_thresholds[dataset_thresholds["scale"] == "all"].copy()
    lt = label_thresholds[label_thresholds["scale"] == "all"].copy()

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8), dpi=160)
    colors = {"learned": "#2563eb", "context": "#dc2626"}

    axes[0].plot(
        ds["macro_f1_delta_threshold"],
        ds["learned_neighborhood_configs"],
        marker="o",
        lw=2,
        color=colors["learned"],
        label="Learned neighborhood",
    )
    axes[0].plot(
        ds["macro_f1_delta_threshold"],
        ds["context_residual_configs"],
        marker="o",
        lw=2,
        color=colors["context"],
        label="Context residual",
    )
    axes[0].axvline(0.005, color="#111827", lw=1, ls="--")
    axes[0].set_title("Dataset-level sensitivity")
    axes[0].set_xlabel("Specific macro-F1 delta cutoff")
    axes[0].set_ylabel("Configurations passing")
    axes[0].set_ylim(bottom=0)
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].plot(
        lt["label_f1_delta_threshold"],
        lt["learned_neighborhood_tasks"],
        marker="o",
        lw=2,
        color=colors["learned"],
        label="Learned neighborhood",
    )
    axes[1].plot(
        lt["label_f1_delta_threshold"],
        lt["context_residual_tasks"],
        marker="o",
        lw=2,
        color=colors["context"],
        label="Context residual",
    )
    axes[1].axvline(0.01, color="#111827", lw=1, ls="--")
    axes[1].set_title("Label-task sensitivity")
    axes[1].set_xlabel("Specific label-F1 delta cutoff")
    axes[1].set_ylabel("Label tasks passing")
    axes[1].set_ylim(bottom=0)
    axes[1].legend(frameon=False, fontsize=8)

    for ax in axes:
        ax.grid(True, color="#e5e7eb", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("NicheTypeR support is threshold-dependent; strict guardrails remain primary", y=1.03)
    fig.tight_layout()
    fig.savefig(FIGURE_PNG, bbox_inches="tight")
    fig.savefig(FIGURE_PDF, bbox_inches="tight")
    fig.savefig(FIGURE_EPS, bbox_inches="tight")
    plt.close(fig)


def svg_polyline(points: list[tuple[float, float]], color: str) -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>'


def svg_circles(points: list[tuple[float, float]], color: str) -> list[str]:
    return [
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}" stroke="#ffffff" stroke-width="1.2"/>'
        for x, y in points
    ]


def draw_svg_panel(
    x0: float,
    y0: float,
    width: float,
    height: float,
    title: str,
    xlabels: list[str],
    y_max: float,
    learned_values: list[int],
    context_values: list[int],
    y_label: str,
    strict_label: str,
) -> list[str]:
    left = x0 + 54
    top = y0 + 48
    plot_w = width - 74
    plot_h = height - 102
    n = len(xlabels)

    def xy(idx: int, value: float) -> tuple[float, float]:
        x = left + plot_w * idx / max(1, n - 1)
        y = top + plot_h - (plot_h * value / y_max)
        return x, y

    learned_points = [xy(i, v) for i, v in enumerate(learned_values)]
    context_points = [xy(i, v) for i, v in enumerate(context_values)]

    lines = [
        f'<text x="{x0 + width / 2:.1f}" y="{y0 + 24:.1f}" text-anchor="middle" class="title">{title}</text>',
        f'<rect x="{left:.1f}" y="{top:.1f}" width="{plot_w:.1f}" height="{plot_h:.1f}" fill="#ffffff" stroke="#111827" stroke-width="1.2"/>',
        f'<text x="{x0 + 12:.1f}" y="{top + plot_h / 2:.1f}" text-anchor="middle" transform="rotate(-90 {x0 + 12:.1f},{top + plot_h / 2:.1f})" class="axis">{y_label}</text>',
    ]
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        y = top + plot_h - plot_h * frac
        value = int(round(y_max * frac))
        lines.append(f'<line x1="{left:.1f}" y1="{y:.1f}" x2="{left + plot_w:.1f}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        lines.append(f'<text x="{left - 10:.1f}" y="{y + 4:.1f}" text-anchor="end" class="tick">{value}</text>')
    for i, lab in enumerate(xlabels):
        x, _ = xy(i, 0)
        lines.append(f'<text x="{x:.1f}" y="{top + plot_h + 24:.1f}" text-anchor="middle" class="tick">{lab}</text>')
        if lab == strict_label:
            lines.append(
                f'<line x1="{x:.1f}" y1="{top:.1f}" x2="{x:.1f}" y2="{top + plot_h:.1f}" '
                'stroke="#111827" stroke-width="1.4" stroke-dasharray="5,5"/>'
            )
    lines.extend(
        [
            svg_polyline(learned_points, "#2563eb"),
            svg_polyline(context_points, "#dc2626"),
            *svg_circles(learned_points, "#2563eb"),
            *svg_circles(context_points, "#dc2626"),
        ]
    )
    return lines


def write_dependency_free_figure(dataset_thresholds: pd.DataFrame, label_thresholds: pd.DataFrame) -> None:
    ds = dataset_thresholds[dataset_thresholds["scale"] == "all"].copy()
    lt = label_thresholds[label_thresholds["scale"] == "all"].copy()

    ds_labels = [f"{x:g}" for x in ds["macro_f1_delta_threshold"].tolist()]
    lt_labels = [f"{x:g}" for x in lt["label_f1_delta_threshold"].tolist()]

    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500">',
        "<style>",
        "text{font-family:Arial, Helvetica, sans-serif; fill:#111827}",
        ".title{font-size:22px;font-weight:700}",
        ".tick{font-size:13px;fill:#374151}",
        ".axis{font-size:15px;font-weight:700;fill:#374151}",
        ".legend{font-size:15px;font-weight:700}",
        "</style>",
        '<rect width="1200" height="500" fill="#ffffff"/>',
        '<text x="600" y="34" text-anchor="middle" style="font-size:24px;font-weight:700">Threshold sensitivity keeps strict results primary</text>',
    ]
    svg_lines.extend(
        draw_svg_panel(
            36,
            58,
            540,
            382,
            "Dataset-level configurations",
            ds_labels,
            15,
            ds["learned_neighborhood_configs"].astype(int).tolist(),
            ds["context_residual_configs"].astype(int).tolist(),
            "configs passing",
            "0.005",
        )
    )
    svg_lines.extend(
        draw_svg_panel(
            626,
            58,
            540,
            382,
            "Dataset-label review tasks",
            lt_labels,
            250,
            lt["learned_neighborhood_tasks"].astype(int).tolist(),
            lt["context_residual_tasks"].astype(int).tolist(),
            "tasks passing",
            "0.01",
        )
    )
    svg_lines.extend(
        [
            '<line x1="430" y1="462" x2="460" y2="462" stroke="#2563eb" stroke-width="4"/>',
            '<text x="468" y="467" class="legend">learned neighborhood</text>',
            '<line x1="655" y1="462" x2="685" y2="462" stroke="#dc2626" stroke-width="4"/>',
            '<text x="693" y="467" class="legend">context residual</text>',
            '<text x="600" y="492" text-anchor="middle" class="tick">Dashed-line strict thresholds are described in the manuscript; exploratory cutoffs are sensitivity only.</text>',
            "</svg>",
        ]
    )
    FIGURE_SVG.write_text("\n".join(svg_lines) + "\n", encoding="utf-8")

    # A lightweight EPS placeholder is generated for journal upload compatibility.
    # The numeric data are preserved in the CSV tables above.
    eps_lines = [
        "%!PS-Adobe-3.0 EPSF-3.0",
        "%%BoundingBox: 0 0 600 250",
        "/Arial findfont 11 scalefont setfont",
        "0.98 setgray 0 0 600 250 rectfill",
        "0 setgray",
        "50 220 moveto (Threshold sensitivity summary) show",
        "50 190 moveto (Dataset strict threshold 0.005: learned 5/34, context 0/34) show",
        "50 170 moveto (Directional threshold >0: learned 14/34, context 2/34) show",
        "50 145 moveto (Label-task threshold >0.01: learned 72/663, context 19/663) show",
        "50 125 moveto (Label-task directional >0: learned 231/663, context 123/663) show",
        "50 90 moveto (Use CSV tables for exact threshold curves.) show",
        "showpage",
        "%%EOF",
    ]
    FIGURE_EPS.write_text("\n".join(eps_lines) + "\n", encoding="utf-8")


def main() -> None:
    dataset_df = read_dataset_guardrails()
    label_df = pd.read_csv(LABEL_TASKS)

    dataset_thresholds = count_dataset_passes(dataset_df)
    label_thresholds = count_label_task_passes(label_df)
    dataset_tier_df = dataset_tiers(dataset_df)
    label_tier_df = label_task_tiers(label_df)

    dataset_thresholds.to_csv(DATASET_THRESHOLDS_OUT, index=False)
    label_thresholds.to_csv(LABEL_THRESHOLDS_OUT, index=False)
    dataset_tier_df.to_csv(DATASET_TIERS_OUT, index=False)
    label_tier_df.to_csv(LABEL_TIERS_OUT, index=False)
    write_report(dataset_thresholds, label_thresholds, dataset_tier_df, label_tier_df)
    write_figure(dataset_thresholds, label_thresholds)

    print(f"Wrote {DATASET_THRESHOLDS_OUT}")
    print(f"Wrote {LABEL_THRESHOLDS_OUT}")
    print(f"Wrote {DATASET_TIERS_OUT}")
    print(f"Wrote {LABEL_TIERS_OUT}")
    print(f"Wrote {REPORT_OUT}")
    if FIGURE_PNG.exists():
        print(f"Wrote {FIGURE_PNG}")
        print(f"Wrote {FIGURE_PDF}")
        print(f"Wrote {FIGURE_EPS}")


if __name__ == "__main__":
    main()
