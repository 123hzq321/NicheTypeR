from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTDIR = Path(__file__).resolve().parent
PDF = OUTDIR / "figure_mechanism_overview.pdf"

W, H = landscape((11.0 * 72, 4.65 * 72))

COLORS = {
    "ink": colors.HexColor("#111111"),
    "muted": colors.HexColor("#4b4b4b"),
    "line": colors.HexColor("#9da2a6"),
    "bg": colors.HexColor("#ffffff"),
    "white": colors.white,
    "blue": colors.HexColor("#202428"),
    "blue_light": colors.HexColor("#f0f1f1"),
    "teal": colors.HexColor("#202428"),
    "teal_light": colors.HexColor("#f0f1f1"),
    "green": colors.HexColor("#33483a"),
    "green_light": colors.HexColor("#f4f5f4"),
    "purple": colors.HexColor("#202428"),
    "purple_light": colors.HexColor("#f0f1f1"),
    "amber": colors.HexColor("#594929"),
    "amber_light": colors.HexColor("#f5f4f1"),
    "red": colors.HexColor("#5e302d"),
    "red_light": colors.HexColor("#f6f3f2"),
    "slate": colors.HexColor("#30363b"),
    "slate_light": colors.HexColor("#f0f1f2"),
}


def wrap_text(text, max_width, font="Helvetica", size=8.5):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(c, text, x, y, max_width, size=8.5, color=None, leading=None, font="Helvetica"):
    color = color or COLORS["ink"]
    leading = leading or size + 2.0
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap_text(text, max_width, font, size):
        c.drawString(x, y, line)
        y -= leading
    return y


def panel(c, x, y, w, h, number, title, accent, chapter):
    c.setFillColor(COLORS["white"])
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(1.0)
    c.roundRect(x, y, w, h, 8, stroke=1, fill=1)

    c.setFillColor(accent)
    c.roundRect(x + 10, y + h - 31, 25, 19, 5, stroke=0, fill=1)
    c.setFillColor(COLORS["white"])
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + 22.5, y + h - 25, str(number))

    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 6.7)
    c.drawString(x + 42, y + h - 18, chapter.upper())
    title_size = 10.2
    while stringWidth(title, "Helvetica-Bold", title_size) > w - 52 and title_size > 8.6:
        title_size -= 0.2
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", title_size)
    c.drawString(x + 42, y + h - 30, title)


def arrow(c, x1, y1, x2, y2, color=None, width=1.7):
    color = color or COLORS["slate"]
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    c.line(x2, y2, x2 - 6, y2 + 4)
    c.line(x2, y2, x2 - 6, y2 - 4)


def down_arrow(c, x, y1, y2, color=None, width=1.2):
    color = color or COLORS["slate"]
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x, y1, x, y2)
    c.line(x, y2, x - 4, y2 + 6)
    c.line(x, y2, x + 4, y2 + 6)


def chip(c, x, y, w, text, fill, stroke, size=7.4, text_color=None, radius=6):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, 18, radius, stroke=1, fill=1)
    c.setFillColor(text_color or stroke)
    c.setFont("Helvetica-Bold", size)
    c.drawCentredString(x + w / 2, y + 5.6, text)


def draw_cell(c, x, y, r, fill, outline=None, label=None, pale=False):
    c.setFillColor(fill)
    c.setStrokeColor(outline or COLORS["white"])
    c.setLineWidth(1.2)
    c.circle(x, y, r, stroke=1, fill=1)
    nucleus = colors.Color(fill.red * 0.72, fill.green * 0.72, fill.blue * 0.72)
    c.setFillColor(nucleus)
    c.circle(x - r * 0.10, y + r * 0.03, r * 0.37, stroke=0, fill=1)
    if not pale:
        dots = [(-0.48, 0.42), (0.42, 0.36), (0.48, -0.30), (-0.38, -0.40)]
        for dx, dy in dots:
            c.setFillColor(COLORS["amber_light"])
            c.circle(x + r * dx, y + r * dy, max(1.1, r * 0.10), stroke=0, fill=1)
    if label:
        c.setFillColor(COLORS["white"])
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x, y - 2.3, label)


def gene_bar(c, x, y, name, fraction, color):
    c.setFillColor(COLORS["muted"])
    c.setFont("Helvetica", 6.7)
    c.drawString(x, y + 2.3, name)
    bx = x + 31
    bw = 64
    c.setFillColor(COLORS["slate_light"])
    c.roundRect(bx, y, bw, 7, 3.5, stroke=0, fill=1)
    c.setFillColor(color)
    c.roundRect(bx, y, bw * fraction, 7, 3.5, stroke=0, fill=1)


def issue_card(c, x, y, w, title, text, kind):
    warning = COLORS["red"] if kind != "thin" else COLORS["amber"]
    c.setFillColor(COLORS["white"])
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(0.7)
    c.roundRect(x, y, w, 43, 6, stroke=1, fill=1)
    c.setStrokeColor(warning)
    c.setLineWidth(2.2)
    c.line(x + 5, y + 8, x + 5, y + 35)

    icon_x = x + 18
    icon_y = y + 24
    if kind == "shared":
        draw_cell(c, icon_x - 5, icon_y, 7, COLORS["blue"], pale=True)
        draw_cell(c, icon_x + 6, icon_y, 7, COLORS["red"], pale=True)
        c.setFillColor(COLORS["amber"])
        c.circle(icon_x, icon_y + 7, 1.8, stroke=0, fill=1)
        c.circle(icon_x, icon_y - 5, 1.8, stroke=0, fill=1)
    elif kind == "thin":
        draw_cell(c, icon_x, icon_y, 10, COLORS["slate_light"], COLORS["slate"], pale=True)
        c.setFillColor(COLORS["amber"])
        c.circle(icon_x - 3, icon_y + 3, 1.5, stroke=0, fill=1)
        c.circle(icon_x + 4, icon_y - 2, 1.5, stroke=0, fill=1)
    else:
        c.setFillColor(COLORS["blue"])
        c.wedge(icon_x - 10, icon_y - 10, icon_x + 10, icon_y + 10, 90, 180, stroke=0, fill=1)
        c.setFillColor(COLORS["red"])
        c.wedge(icon_x - 10, icon_y - 10, icon_x + 10, icon_y + 10, 270, 180, stroke=0, fill=1)
        c.setStrokeColor(COLORS["white"])
        c.setLineWidth(1)
        c.line(icon_x, icon_y - 9, icon_x, icon_y + 9)

    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 7.3)
    c.drawString(x + 36, y + 28, title)
    draw_wrapped(c, text, x + 36, y + 16, w - 43, 6.5, COLORS["muted"], 7.4)


def evidence_row(c, x, y, w, label, accent, symbol):
    c.setFillColor(colors.HexColor("#fbfcfe"))
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(0.65)
    c.roundRect(x, y, w, 27, 5, stroke=1, fill=1)
    c.setFillColor(accent)
    c.circle(x + 15, y + 13.5, 8, stroke=0, fill=1)
    c.setFillColor(COLORS["white"])
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x + 15, y + 11.1, symbol)
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 7.6)
    c.drawString(x + 29, y + 16.4, label)


def method_card(c, x, y, w, h, function_name, detail, fill, stroke, function_size=7.0):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.75)
    c.roundRect(x, y, w, h, 5, stroke=1, fill=1)

    size = function_size
    while stringWidth(function_name, "Courier-Bold", size) > w - 10 and size > 5.0:
        size -= 0.2
    c.setFillColor(stroke)
    c.setFont("Courier-Bold", size)
    c.drawCentredString(x + w / 2, y + h - 12, function_name)
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica", 6.3)
    c.drawCentredString(x + w / 2, y + 6, detail)


def evidence_strip(c, x, y, w):
    c.setFillColor(colors.HexColor("#fbfcfe"))
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(0.7)
    c.roundRect(x, y, w, 28, 5, stroke=1, fill=1)
    c.setFillColor(COLORS["muted"])
    c.setFont("Helvetica-Bold", 5.8)
    c.drawString(x + 7, y + 18, "EVIDENCE MATRICES")

    items = [
        ("marker", COLORS["blue"]),
        ("reference", COLORS["blue"]),
        ("pathway", COLORS["blue"]),
        ("niche", COLORS["blue"]),
        ("LR", COLORS["blue"]),
    ]
    xx = x + 7
    for label, color in items:
        c.setFillColor(color)
        c.circle(xx + 2.5, y + 8, 2.5, stroke=0, fill=1)
        c.setFillColor(COLORS["ink"])
        c.setFont("Helvetica", 5.9)
        c.drawString(xx + 7, y + 5.7, label)
        xx += stringWidth(label, "Helvetica", 5.9) + 15


def output_card(c, x, y, w, title, detail, fill, stroke):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, 38, 6, stroke=1, fill=1)
    c.setFillColor(stroke)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 9, y + 23, title)
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica", 6.8)
    c.drawString(x + 9, y + 10, detail)


def draw_species_icon(c, x, y, color):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.1)

    # Human bust.
    c.circle(x - 9, y + 5.5, 3.2, stroke=0, fill=1)
    human = c.beginPath()
    human.moveTo(x - 16, y - 7)
    human.curveTo(x - 15, y - 1, x - 12, y + 0.5, x - 9, y + 0.5)
    human.curveTo(x - 6, y + 0.5, x - 3, y - 1, x - 2, y - 7)
    human.close()
    c.drawPath(human, stroke=0, fill=1)

    # Mouse silhouette with ears, eye and curved tail.
    c.ellipse(x + 0, y - 5.5, x + 14, y + 4.5, stroke=1, fill=0)
    c.circle(x + 14, y + 3.5, 3.6, stroke=1, fill=0)
    c.circle(x + 11.8, y + 7.0, 1.7, stroke=1, fill=0)
    c.circle(x + 15.3, y + 7.2, 1.5, stroke=1, fill=0)
    c.circle(x + 15.0, y + 4.2, 0.65, stroke=0, fill=1)
    c.line(x + 17.5, y + 2.8, x + 20.3, y + 2.0)
    tail = c.beginPath()
    tail.moveTo(x + 1.0, y - 1.5)
    tail.curveTo(x - 5.0, y - 2.0, x - 4.0, y - 8.0, x - 9.0, y - 8.0)
    c.drawPath(tail, stroke=1, fill=0)


def draw_tissue_icon(c, x, y, color):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.1)

    # Brain outline with a central fissure.
    brain = c.beginPath()
    brain.moveTo(x - 16, y)
    brain.curveTo(x - 17, y + 5.5, x - 12, y + 9, x - 8, y + 6.5)
    brain.curveTo(x - 5, y + 9, x, y + 6.5, x - 1, y + 2)
    brain.curveTo(x + 1, y - 2, x - 2, y - 7, x - 7, y - 6)
    brain.curveTo(x - 11, y - 8, x - 16, y - 5, x - 16, y)
    brain.close()
    c.drawPath(brain, stroke=1, fill=0)
    c.line(x - 8, y + 6, x - 8, y - 5.5)
    c.line(x - 14, y + 1.5, x - 10, y + 2.2)
    c.line(x - 6, y + 2.4, x - 2.5, y + 1.5)

    # Tumor cluster.
    for dx, dy, radius in [(4, 2, 3.0), (9, 4, 2.7), (10, -2, 3.1), (4, -4, 2.8)]:
        c.circle(x + dx, y + dy, radius, stroke=0, fill=1)

    # Immune cell with short membrane processes.
    immune_x = x + 19
    c.circle(immune_x, y, 3.8, stroke=1, fill=0)
    c.circle(immune_x - 1.1, y + 0.7, 1.2, stroke=0, fill=1)
    for dx, dy in [(0, 7), (0, -7), (7, 0), (-7, 0), (5, 5), (-5, 5), (5, -5), (-5, -5)]:
        length = (dx * dx + dy * dy) ** 0.5
        c.line(
            immune_x + dx * 4.5 / length,
            y + dy * 4.5 / length,
            immune_x + dx * 6.3 / length,
            y + dy * 6.3 / length,
        )


def source_tile(c, x, y, w, top, bottom, fill, stroke, icon):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.75)
    c.roundRect(x, y, w, 35, 6, stroke=1, fill=1)
    ix = x + 20
    iy = y + 17.5

    c.setStrokeColor(stroke)
    c.setFillColor(stroke)
    c.setLineWidth(1.2)
    if icon == "species":
        draw_species_icon(c, ix, iy, stroke)
    elif icon == "tissue":
        draw_tissue_icon(c, ix, iy, stroke)
    elif icon == "platform":
        for dx, dy in [(-6, 5), (1, 6), (7, 1), (-4, -4), (4, -5)]:
            c.circle(ix + dx, iy + dy, 1.9, stroke=0, fill=1)
        c.rect(ix - 9, iy - 8, 19, 16, stroke=1, fill=0)
    else:
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(ix, iy - 4, "100")

    tx = x + (52 if icon in ("species", "tissue", "platform") else 38)
    c.setFillColor(stroke)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawString(tx, y + 21.2, top)
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica", 6.7)
    c.drawString(tx, y + 9.2, bottom)


def build():
    c = canvas.Canvas(str(PDF), pagesize=(W, H))
    c.setTitle("NicheTypeR problem-to-solution mechanism")
    c.setFillColor(COLORS["bg"])
    c.rect(0, 0, W, H, stroke=0, fill=1)

    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 16.4)
    c.drawCentredString(
        W / 2,
        H - 23,
        "Why a plausible cell label can still be wrong - and how NicheTypeR audits it",
    )
    c.setFillColor(COLORS["muted"])
    c.setFont("Helvetica", 8.6)
    c.drawCentredString(
        W / 2,
        H - 38,
        "Single-cell annotation usually reads the cell alone. Spatial tissue supplies the missing biological context.",
    )

    panel_y = 70
    panel_h = 207
    gap = 9
    widths = [150, 172, 225, 170]
    xs = [24]
    for width in widths[:-1]:
        xs.append(xs[-1] + width + gap)

    panels = [
        (1, "A model names the cell", COLORS["blue"], "first answer"),
        (2, "Why labels go wrong", COLORS["blue"], "the problem"),
        (3, "NicheTypeR runs the audit", COLORS["blue"], "R package"),
        (4, "A result people can use", COLORS["blue"], "the decision"),
    ]
    for x, width, spec in zip(xs, widths, panels):
        panel(c, x, panel_y, width, panel_h, *spec)

    mid_y = panel_y + panel_h / 2
    for i in range(3):
        arrow(c, xs[i] + widths[i] + 2, mid_y, xs[i + 1] - 3, mid_y)

    # 1. The conventional first answer.
    x = xs[0]
    draw_wrapped(
        c,
        "Expression alone can give a confident-looking answer.",
        x + 11,
        panel_y + panel_h - 48,
        widths[0] - 22,
        7.6,
        COLORS["muted"],
        9.0,
    )
    draw_cell(c, x + 39, panel_y + 112, 25, COLORS["blue"], label="?")
    chip(c, x + 72, panel_y + 124, 65, "Macrophage", COLORS["blue_light"], COLORS["blue"], 7.2)
    c.setFillColor(COLORS["muted"])
    c.setFont("Helvetica", 6.8)
    c.drawString(x + 82, panel_y + 112, "score 0.82")
    gene_bar(c, x + 17, panel_y + 82, "LST1", 0.88, COLORS["blue"])
    gene_bar(c, x + 17, panel_y + 68, "TYROBP", 0.79, COLORS["blue"])
    gene_bar(c, x + 17, panel_y + 54, "IFITM3", 0.72, COLORS["blue"])
    chip(
        c,
        x + 13,
        panel_y + 16,
        widths[0] - 26,
        "looks certain",
        COLORS["slate_light"],
        COLORS["slate"],
        7.6,
    )

    # 2. The failure modes that motivate the audit.
    x = xs[1]
    draw_wrapped(
        c,
        "One signal can tell several biological stories.",
        x + 11,
        panel_y + panel_h - 48,
        widths[1] - 22,
        7.6,
        COLORS["muted"],
        9.0,
    )
    issue_card(c, x + 11, panel_y + 104, widths[1] - 22, "Shared signals", "Different states reuse genes", "shared")
    issue_card(c, x + 11, panel_y + 58, widths[1] - 22, "Thin measurements", "Missing RNA hides markers", "thin")
    issue_card(c, x + 11, panel_y + 12, widths[1] - 22, "Mixed boundaries", "Doublets blur cell identity", "mixed")
    # 3. Actual NicheTypeR R-package execution path.
    x = xs[2]
    left_w = 96
    right_w = widths[2] - 35 - left_w
    method_card(
        c,
        x + 11,
        panel_y + 133,
        left_w,
        34,
        "score_external_labels()",
        "SingleR / Seurat / CellTypist",
        COLORS["blue_light"],
        COLORS["blue"],
        6.2,
    )
    method_card(
        c,
        x + 24 + left_w,
        panel_y + 133,
        right_w,
        34,
        "run_nichetype_workflow()",
        "expression + coordinates",
        COLORS["blue_light"],
        COLORS["blue"],
        6.0,
    )

    c.setStrokeColor(COLORS["slate"])
    c.setLineWidth(1.0)
    c.line(x + 11 + left_w / 2, panel_y + 133, x + widths[2] / 2, panel_y + 126)
    c.line(x + 24 + left_w + right_w / 2, panel_y + 133, x + widths[2] / 2, panel_y + 126)
    down_arrow(c, x + widths[2] / 2, panel_y + 126, panel_y + 124, COLORS["slate"], 1.0)

    evidence_strip(c, x + 12, panel_y + 96, widths[2] - 24)

    down_arrow(c, x + widths[2] / 2, panel_y + 94, panel_y + 87, COLORS["slate"], 1.0)
    method_card(
        c,
        x + 12,
        panel_y + 54,
        widths[2] - 24,
        33,
        "audit_external_annotation()",
        "fused score + margin + conflict reason",
        COLORS["blue_light"],
        COLORS["blue"],
        7.0,
    )

    down_arrow(c, x + widths[2] / 2, panel_y + 52, panel_y + 49, COLORS["slate"], 1.0)
    method_card(
        c,
        x + 12,
        panel_y + 7,
        widths[2] - 24,
        42,
        "score_context_specific_annotation()",
        "CSAE = observed context - matched null mean",
        COLORS["blue_light"],
        COLORS["blue"],
        6.8,
    )

    # 4. Actionable, human-readable output.
    x = xs[3]
    draw_wrapped(
        c,
        "NicheTypeR does not force a new label. It shows what deserves review.",
        x + 11,
        panel_y + panel_h - 48,
        widths[3] - 22,
        7.6,
        COLORS["muted"],
        9.0,
    )
    output_card(c, x + 12, panel_y + 107, widths[3] - 24, "KEEP", "evidence agrees", COLORS["white"], COLORS["green"])
    output_card(c, x + 12, panel_y + 65, widths[3] - 24, "REVIEW FIRST", "biology conflicts", COLORS["white"], COLORS["red"])
    output_card(c, x + 12, panel_y + 23, widths[3] - 24, "UNCERTAIN", "evidence is weak", COLORS["white"], COLORS["amber"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 6.8)
    c.drawCentredString(x + widths[3] / 2, panel_y + 11, "ranked review list + plain-language reason")

    # Cross-species, cross-tissue and cross-platform evaluation ribbon.
    band_x = 24
    band_y = 14
    band_w = W - 48
    band_h = 47
    c.setFillColor(COLORS["white"])
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(0.9)
    c.roundRect(band_x, band_y, band_w, band_h, 8, stroke=1, fill=1)
    tile_y = band_y + 6
    source_tile(c, band_x + 11, tile_y, 132, "Multiple species", "human, mouse and models", COLORS["white"], COLORS["blue"], "species")
    source_tile(c, band_x + 150, tile_y, 190, "Diverse tissues", "brain, tumor, immune-rich", COLORS["white"], COLORS["blue"], "tissue")
    source_tile(c, band_x + 347, tile_y, 235, "Multiple assay families", "MERFISH, CosMx, Visium, IMC, Slide-seqV2", COLORS["white"], COLORS["blue"], "platform")
    source_tile(c, band_x + 589, tile_y, 144, "100 public sources", "61 labelled + 39 calibration", COLORS["white"], COLORS["blue"], "count")

    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
