from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
OUT = ROOT / "bioinformatics_submission"
LATEX_OUT = OUT / "latex_submission"


def main():
    guardrail = pd.read_csv(DATASETS / "MULTIDATASET_BLOCKED_BENCHMARK_guardrail.csv")
    validation = pd.read_csv(DATASETS / "DATASET_PREVIEW_VALIDATION.csv")
    merged = guardrail.merge(
        validation[["dataset_id", "preview_cells", "n_labels"]],
        on="dataset_id",
        how="left",
    )
    merged = merged.sort_values("learned_specific_macro_f1_delta", ascending=True)
    merged.to_csv(OUT / "figure1_guardrail_benchmark_data.csv", index=False)

    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import matplotlib as mpl
        from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
    except ImportError as exc:
        raise SystemExit("matplotlib is required to generate the figures.") from exc

    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Nimbus Roman", "Times", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.unicode_minus": False,
        }
    )

    def add_box(
        ax,
        xy,
        width,
        height,
        title,
        body,
        facecolor,
        edgecolor="#333333",
        body_y_delta=-0.03,
    ):
        x, y0 = xy
        patch = FancyBboxPatch(
            (x, y0),
            width,
            height,
            boxstyle="round,pad=0.02,rounding_size=0.035",
            linewidth=1.0,
            edgecolor=edgecolor,
            facecolor=facecolor,
        )
        ax.add_patch(patch)
        ax.text(
            x + width / 2,
            y0 + height - 0.08,
            title,
            ha="center",
            va="top",
            fontsize=9.5,
            fontweight="bold",
            color="#1f1f1f",
        )
        ax.text(
            x + width / 2,
            y0 + height / 2 + body_y_delta,
            body,
            ha="center",
            va="center",
            fontsize=8.1,
            color="#222222",
            linespacing=1.25,
        )

    def add_arrow(ax, start, end):
        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.2,
            color="#444444",
            shrinkA=6,
            shrinkB=6,
        )
        ax.add_patch(arrow)

    fig_w = plt.figure(figsize=(12.4, 6.25), facecolor="white")
    overlay = fig_w.add_axes([0, 0, 1, 1])
    overlay.set_axis_off()

    ink = "#202833"
    muted = "#697386"
    grid = "#D7DDE6"
    blue = "#2F6DF6"
    teal = "#268C7E"
    gold = "#B77A12"
    red = "#C73E3A"

    def style_panel(ax, letter, title, subtitle):
        ax.set_facecolor("#FFFFFF")
        for spine in ax.spines.values():
            spine.set_color(grid)
            spine.set_linewidth(0.9)
        ax.tick_params(length=0, labelsize=7.5, colors=muted)
        ax.text(
            -0.02,
            1.12,
            letter,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=14,
            fontweight="bold",
            color=ink,
        )
        ax.text(
            0.08,
            1.13,
            title,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=10.8,
            fontweight="bold",
            color=ink,
        )
        ax.text(
            0.08,
            1.035,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=7.8,
            color=muted,
        )

    def fig_arrow(start, end, color="#3D4652", lw=1.2, rad=0.0):
        arrow = FancyArrowPatch(
            start,
            end,
            transform=fig_w.transFigure,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=lw,
            color=color,
            shrinkA=4,
            shrinkB=4,
        )
        fig_w.add_artist(arrow)

    fig_w.text(
        0.5,
        0.965,
        "NicheTypeR CSAE: auditing whether annotation support exceeds matched context nulls",
        ha="center",
        va="center",
        fontsize=13.6,
        fontweight="bold",
        color=ink,
    )
    fig_w.text(
        0.5,
        0.033,
        "CSAE = Context-Specific Annotation Evidence. Candidate labels are treated as hypotheses, then tested against matched null context.",
        ha="center",
        va="center",
        fontsize=8.5,
        color=muted,
    )

    # A. Candidate labels as a compact score matrix.
    ax_a = fig_w.add_axes([0.055, 0.565, 0.245, 0.285])
    style_panel(ax_a, "A", "Candidate annotation", "External or marker labels enter as hypotheses.")
    candidate_scores = np.array(
        [
            [0.92, 0.22, 0.16, 0.08],
            [0.31, 0.81, 0.20, 0.11],
            [0.20, 0.27, 0.77, 0.18],
            [0.43, 0.35, 0.30, 0.52],
        ]
    )
    im_a = ax_a.imshow(candidate_scores, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax_a.set_xticks(range(4))
    ax_a.set_xticklabels(["T", "B", "M", "E"])
    ax_a.set_yticks(range(4))
    ax_a.set_yticklabels(["cell i", "cell j", "cell k", "spot s"])
    ax_a.set_xlabel("candidate label", fontsize=7.7, color=muted, labelpad=2)
    ax_a.set_ylabel("query unit", fontsize=7.7, color=muted, labelpad=2)
    for r in range(candidate_scores.shape[0]):
        for c in range(candidate_scores.shape[1]):
            ax_a.text(
                c,
                r,
                f"{candidate_scores[r, c]:.2f}",
                ha="center",
                va="center",
                fontsize=6.3,
                color="white" if candidate_scores[r, c] > 0.56 else "#26313D",
            )
    cax_a = fig_w.add_axes([0.305, 0.59, 0.006, 0.22])
    cb_a = fig_w.colorbar(im_a, cax=cax_a)
    cb_a.ax.tick_params(labelsize=6, length=2)
    cb_a.outline.set_linewidth(0.5)

    # B. Observed context is shown as tissue graph plus evidence-by-label matrix.
    ax_b = fig_w.add_axes([0.36, 0.565, 0.28, 0.285])
    style_panel(ax_b, "B", "Observed biological context", "Neighborhood, function and interaction evidence are label-specific.")
    ax_b.set_xlim(0, 1)
    ax_b.set_ylim(0, 1)
    ax_b.set_xticks([])
    ax_b.set_yticks([])
    coords = {
        "i": (0.30, 0.68, blue, "i"),
        "n1": (0.16, 0.80, teal, "T"),
        "n2": (0.50, 0.82, "#A54491", "M"),
        "n3": (0.18, 0.46, "#E4942D", "E"),
        "n4": (0.50, 0.48, teal, "T"),
        "n5": (0.70, 0.65, blue, "B"),
    }
    edges = [("i", "n1"), ("i", "n2"), ("i", "n3"), ("i", "n4"), ("n2", "n5"), ("n4", "n5")]
    for a, b in edges:
        xa, ya, _, _ = coords[a]
        xb, yb, _, _ = coords[b]
        ax_b.plot([xa, xb], [ya, yb], color="#9AA5B1", linewidth=1.0, zorder=1)
    for _, (x0, y0, color, label) in coords.items():
        ax_b.add_patch(Circle((x0, y0), 0.045, facecolor=color, edgecolor="white", linewidth=1.2, zorder=3))
        ax_b.text(x0, y0, label, ha="center", va="center", fontsize=7.5, color="white", fontweight="bold", zorder=4)
    ev = np.array(
        [
            [0.87, 0.28, 0.18, 0.22],
            [0.62, 0.36, 0.41, 0.19],
            [0.75, 0.31, 0.24, 0.28],
            [0.58, 0.22, 0.32, 0.40],
            [0.81, 0.35, 0.21, 0.26],
        ]
    )
    extent = [0.02, 0.98, 0.02, 0.35]
    ax_b.imshow(ev, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto", extent=extent, zorder=0)
    labels_y = ["marker", "ref", "program", "LR", "niche"]
    for idx, label in enumerate(labels_y):
        y_lab = 0.32 - idx * 0.065
        ax_b.text(-0.035, y_lab, label, ha="right", va="center", fontsize=6.8, color=muted)
    for idx, label in enumerate(["T", "B", "M", "E"]):
        x_lab = 0.14 + idx * 0.24
        ax_b.text(x_lab, -0.025, label, ha="center", va="top", fontsize=7.0, color=muted)
    ax_b.text(
        0.61,
        0.43,
        r"$O_{i\ell}=f(M,R,P,B,N;G,A)$",
        ha="center",
        va="center",
        fontsize=9.3,
        color=ink,
    )

    # C. Matched nulls and the observed-vs-null test.
    ax_c = fig_w.add_axes([0.715, 0.565, 0.235, 0.285])
    style_panel(ax_c, "C", "Matched null context", "Nulls preserve nuisance structure while breaking specificity.")
    x = np.linspace(-3.1, 3.1, 300)
    y_pdf = np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)
    ax_c.fill_between(x, y_pdf, color="#EEF1F5", edgecolor="#798494", linewidth=0.9)
    ax_c.plot(x, y_pdf, color="#586574", linewidth=1.0)
    obs = 1.55
    y_obs = np.exp(-0.5 * obs**2) / np.sqrt(2 * np.pi)
    ax_c.axvline(obs, color=red, linewidth=1.4)
    ax_c.scatter([obs], [y_obs], s=32, color=red, zorder=3)
    ax_c.text(obs + 0.12, y_obs + 0.025, r"observed $O_{i\ell}$", fontsize=7.3, color=red, ha="left")
    ax_c.text(-2.9, 0.37, r"null scores $O^0_{i\ell,b}$", fontsize=7.6, color=muted)
    ax_c.set_xticks([-2, 0, 2])
    ax_c.set_yticks([])
    ax_c.set_xlabel("context support", fontsize=7.6, color=muted, labelpad=1)
    ax_c.set_xlim(-3.1, 3.1)
    ax_c.set_ylim(0, 0.46)
    null_labels = [(r"$G^0$", "random graph"), (r"$A^\pi$", "permuted prior"), (r"$\Pi(O)$", "shuffled context")]
    for idx, (sym, label) in enumerate(null_labels):
        y0 = 0.08 + idx * 0.06
        ax_c.text(-2.85, y0, sym, fontsize=8.2, color=gold, fontweight="bold", ha="left", va="center")
        ax_c.plot([-2.18, -1.35], [y0, y0], color=gold, linewidth=1.1, linestyle=(0, (4, 3)))
        ax_c.text(-1.22, y0, label, fontsize=7.1, color="#6D4C12", ha="left", va="center")

    # D. CSAE decision rule, kept as a clean lower strip.
    fig_w.text(
        0.5,
        0.492,
        r"per-cell comparison: observed context support $O_{i\ell}$ vs matched null scores $O^0_{i\ell,b}$",
        ha="center",
        va="center",
        fontsize=8.6,
        color=muted,
    )

    ax_d = fig_w.add_axes([0.08, 0.135, 0.84, 0.30])
    ax_d.set_facecolor("#FFFFFF")
    for spine in ax_d.spines.values():
        spine.set_color(grid)
        spine.set_linewidth(0.9)
    ax_d.set_xlim(0, 1)
    ax_d.set_ylim(0, 1)
    ax_d.set_xticks([])
    ax_d.set_yticks([])
    ax_d.text(0.025, 0.91, "D", ha="left", va="center", fontsize=14, fontweight="bold", color=ink)
    ax_d.text(
        0.075,
        0.91,
        "Null-corrected audit decision",
        ha="left",
        va="center",
        fontsize=10.8,
        fontweight="bold",
        color=ink,
    )
    ax_d.text(
        0.075,
        0.81,
        "Observed label support is converted into reviewable evidence states.",
        ha="left",
        va="center",
        fontsize=7.8,
        color=muted,
    )
    ax_d.text(
        0.04,
        0.58,
        r"$\Delta_{i\ell}=O_{i\ell}-\mu^0_{i\ell}$",
        ha="left",
        va="center",
        fontsize=11.5,
        color=ink,
    )
    ax_d.text(
        0.04,
        0.39,
        r"$Z_{i\ell}=(O_{i\ell}-\mu^0_{i\ell})/(\sigma^0_{i\ell}+\epsilon)$",
        ha="left",
        va="center",
        fontsize=11.0,
        color=ink,
    )
    ax_d.text(
        0.04,
        0.21,
        r"empirical $p$-value + residual margin",
        ha="left",
        va="center",
        fontsize=9.5,
        color=muted,
    )
    ax_d.plot([0.38, 0.38], [0.15, 0.76], color=grid, linewidth=1.0)
    ax_d.text(0.42, 0.68, r"If $\tilde{y}_i$ is top context-specific label:", fontsize=8.6, color=muted)
    ax_d.text(0.42, 0.55, r"supported", fontsize=10.0, color=teal, fontweight="bold")
    ax_d.text(0.42, 0.39, r"if another label has stronger context support:", fontsize=8.6, color=muted)
    ax_d.text(0.42, 0.26, r"conflict", fontsize=10.0, color=red, fontweight="bold")
    ax_d.text(0.66, 0.68, r"If support is null-like:", fontsize=8.6, color=muted)
    ax_d.text(0.66, 0.55, r"not specific", fontsize=10.0, color="#59636F", fontweight="bold")
    ax_d.text(0.66, 0.39, r"If margins are small:", fontsize=8.6, color=muted)
    ax_d.text(0.66, 0.26, r"ambiguous", fontsize=10.0, color=gold, fontweight="bold")
    states = [
        (0.42, 0.08, 0.10, "#DBF2E1", teal, "supported"),
        (0.535, 0.08, 0.09, "#F9DEDD", red, "conflict"),
        (0.64, 0.08, 0.105, "#E9EDF2", "#59636F", "not specific"),
        (0.76, 0.08, 0.10, "#FFF0C8", gold, "ambiguous"),
    ]
    for x0, y0, width, fill, edge, label in states:
        ax_d.add_patch(Rectangle((x0, y0), width, 0.085, facecolor=fill, edgecolor=edge, linewidth=1.0))
        ax_d.text(x0 + width / 2, y0 + 0.043, label, ha="center", va="center", fontsize=7.5, color=edge, fontweight="bold")
    ax_d.text(
        0.88,
        0.15,
        "output table:\nlabel, confidence, margin,\nCSAE residual, z-score,\np-value, conflict reason,\nrescue/harm",
        fontsize=7.2,
        color=muted,
        ha="left",
        va="bottom",
        linespacing=1.18,
    )

    fig_arrow((0.315, 0.705), (0.35, 0.705))
    fig_arrow((0.65, 0.705), (0.705, 0.705))

    fig_w.savefig(OUT / "figure_method_workflow.png", dpi=300)
    fig_w.savefig(OUT / "figure_method_workflow.png", dpi=300)
    fig_w.savefig(OUT / "figure_method_workflow.pdf")
    fig_w.savefig(OUT / "figure_method_workflow.eps", format="eps")
    fig_w.savefig(LATEX_OUT / "figure_method_workflow.png", dpi=300)
    fig_w.savefig(LATEX_OUT / "figure_method_workflow.pdf")
    fig_w.savefig(LATEX_OUT / "figure_method_workflow.eps", format="eps")
    plt.close(fig_w)

    y = np.arange(len(merged))
    height = 0.24

    fig, ax = plt.subplots(figsize=(8.8, 7.2))
    ax.axvline(0, color="#303030", linewidth=0.8)
    ax.axvline(0.005, color="#606060", linewidth=0.8, linestyle="--")

    colors = {
        "learned": "#246BFE",
        "smoothing": "#2E8B57",
        "context": "#B0478C",
    }

    ax.barh(
        y + height,
        merged["learned_specific_macro_f1_delta"],
        height=height,
        color=colors["learned"],
        label="Learned neighborhood",
    )
    ax.barh(
        y,
        merged["smoothing_specific_macro_f1_delta"],
        height=height,
        color=colors["smoothing"],
        label="Spatial smoothing",
    )
    ax.barh(
        y - height,
        merged["context_specific_macro_f1_delta"],
        height=height,
        color=colors["context"],
        label="Context-specific residual",
    )

    for row_i, row in merged.reset_index(drop=True).iterrows():
        if bool(row["learned_passes_guardrail"]):
            ax.scatter(
                row["learned_specific_macro_f1_delta"],
                row_i + height,
                s=52,
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                zorder=3,
            )
        if bool(row["smoothing_passes_guardrail"]):
            ax.scatter(
                row["smoothing_specific_macro_f1_delta"],
                row_i,
                s=52,
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                zorder=3,
            )
        if bool(row["context_specific_passes_guardrail"]):
            ax.scatter(
                row["context_specific_macro_f1_delta"],
                row_i - height,
                s=52,
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                zorder=3,
            )

    short_names = {
        "GSE202623_LESION": "GSE202623 lesion",
        "GEO_GSE240015_VISIUM_THYMUS_DOMAIN": "GSE240015 thymus Visium",
        "GEO_GSE284005_MERSCOPE_MS": "GSE284005 MS MERSCOPE",
        "GEO_GSE327581_COSMX_AD_BRAIN": "GSE327581 AD brain CosMx",
        "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR": "GSE333737 pancreas MERSCOPE",
    }
    labels = [
        f"{short_names.get(row.dataset_id, row.dataset_id.replace('_', ' '))}\n"
        f"{int(row.preview_cells):,} cells/spots, {int(row.n_labels)} labels"
        for row in merged.itertuples()
    ]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("Macro-F1 change relative to marker-only / matched null controls")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3)
    ax.grid(axis="x", color="#d8d8d8", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    fig.savefig(OUT / "figure1_guardrail_benchmark.png", dpi=300)
    fig.savefig(OUT / "figure1_guardrail_benchmark.pdf")
    fig.savefig(OUT / "figure1_guardrail_benchmark.eps", format="eps")
    fig.savefig(LATEX_OUT / "figure1_guardrail_benchmark.png", dpi=300)
    fig.savefig(LATEX_OUT / "figure1_guardrail_benchmark.pdf")
    fig.savefig(LATEX_OUT / "figure1_guardrail_benchmark.eps", format="eps")


if __name__ == "__main__":
    main()
