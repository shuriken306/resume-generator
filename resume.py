#!/usr/bin/env python3
"""
Resume Generator
================
Reads data from a JSON file and produces a styled A4 PDF.

    uv run --with reportlab python3 resume.py
    uv run --with reportlab python3 resume.py my_data.json
    uv run --with reportlab python3 resume.py my_data.json --output my_cv.pdf
"""

import json
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas


# ╔══════════════════════════════════════════════════════╗
# ║  DESIGN CONSTANTS                                   ║
# ╚══════════════════════════════════════════════════════╝

COLORS = {
    "dark_bg":    HexColor("#0f172a"),
    "card_bg":    HexColor("#1e293b"),
    "white":      HexColor("#f8fafc"),
    "light":      HexColor("#cbd5e1"),
    "mid":        HexColor("#94a3b8"),
    "dim":        HexColor("#64748b"),
    "text_dark":  HexColor("#1e293b"),
    "text_mid":   HexColor("#475569"),
    "text_light": HexColor("#94a3b8"),
    "border":     HexColor("#e2e8f0"),
    "sky":        HexColor("#38bdf8"),
    "indigo":     HexColor("#818cf8"),
    "green":      HexColor("#4ade80"),
    "orange":     HexColor("#fb923c"),
    "red_dot":    HexColor("#ef4444"),
    "yellow_dot": HexColor("#eab308"),
    "green_dot":  HexColor("#22c55e"),
}

DOT_GRID_COLOR = Color(0.3, 0.4, 0.55, alpha=0.12)
BRACKET_COLOR  = Color(0.22, 0.74, 0.97, alpha=0.10)

W, H     = A4
HEADER_H = 78 * mm


# ╔══════════════════════════════════════════════════════╗
# ║  HELPERS                                            ║
# ╚══════════════════════════════════════════════════════╝

def c(name: str) -> Color:
    return COLORS.get(name, COLORS["sky"])


def wrap_text(pdf, text, x, y, font, size, color, max_w, leading=None):
    if leading is None:
        leading = size + 3
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w) if cur else w
        if pdf.stringWidth(test, font, size) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_section(pdf, title, x, y, width, icon=">"):
    pdf.setFillColor(c("sky"))
    pdf.setFont("Courier-Bold", 10)
    pdf.drawString(x, y, icon)
    pdf.setFillColor(c("text_dark"))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(x + 6 * mm, y, title)
    pdf.setStrokeColor(c("border"))
    pdf.setLineWidth(0.5)
    pdf.line(x, y - 4, x + width, y - 4)
    return y - 18


# ╔══════════════════════════════════════════════════════╗
# ║  HEADER                                             ║
# ╚══════════════════════════════════════════════════════╝

def draw_header(pdf, p, terminal_text):
    pdf.setFillColor(c("dark_bg"))
    pdf.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)

    # Dot grid background
    pdf.setFillColor(DOT_GRID_COLOR)
    for gx in range(0, int(W), 14):
        for gy in range(int(H - HEADER_H), int(H), 14):
            pdf.circle(gx, gy, 0.6, fill=1, stroke=0)

    # Code brackets
    pdf.setFillColor(BRACKET_COLOR)
    pdf.setFont("Courier-Bold", 120)
    pdf.drawString(-8, H - HEADER_H + 8, "{")
    pdf.drawString(W - 55, H - HEADER_H + 8, "}")

    # Terminal bar
    bar_y = H - 14 * mm
    pdf.setFillColor(c("card_bg"))
    pdf.roundRect(15 * mm, bar_y - 3, W - 30 * mm, 10 * mm, 4, fill=1, stroke=0)
    for i, dot in enumerate(["red_dot", "yellow_dot", "green_dot"]):
        pdf.setFillColor(c(dot))
        pdf.circle(22 * mm + i * 5 * mm, bar_y + 2, 1.8, fill=1, stroke=0)
    pdf.setFillColor(c("mid"))
    pdf.setFont("Courier", 7)
    pdf.drawString(40 * mm, bar_y, terminal_text)

    # Name + title
    ny = H - 34 * mm
    pdf.setFillColor(c("white"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawString(18 * mm, ny, p["name"])
    pdf.setFillColor(c("sky"))
    pdf.setFont("Helvetica", 12)
    pdf.drawString(18 * mm, ny - 16, p["title"])
    pdf.setFillColor(c("mid"))
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(18 * mm, ny - 30, p["stack_line"])

    # Contact line
    cy = H - HEADER_H + 12 * mm
    cx = 18 * mm
    for val in [p["email"], p["phone"], p["address"], p["github"]]:
        pdf.setFillColor(c("sky"))
        pdf.setFont("Courier-Bold", 7.5)
        pdf.drawString(cx, cy, "//")
        cx += 7 * mm
        pdf.setFillColor(c("light"))
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(cx, cy, val)
        cx += pdf.stringWidth(val, "Helvetica", 7.5) + 6 * mm

    pdf.setFillColor(c("dim"))
    pdf.setFont("Helvetica", 7)
    pdf.drawString(18 * mm, cy - 11, f"{p['born']}  \u00b7  {p['status']}")


# ╔══════════════════════════════════════════════════════╗
# ║  LEFT COLUMN                                        ║
# ╚══════════════════════════════════════════════════════╝

def draw_left_column(pdf, data, col1_x, col1_w, y):
    # Backward compatible: "job" (single) or "jobs" (list)
    jobs = data.get("jobs", [data["job"]] if "job" in data else [])

    y = draw_section(pdf, "BERUFSERFAHRUNG", col1_x, y, col1_w)

    timeline_top = y + 2
    jx = col1_x + 8 * mm

    for ji, job in enumerate(jobs):
        # Timeline dot per station
        pdf.setFillColor(c("sky"))
        pdf.circle(col1_x + 1.5, y + 2, 2.5, fill=1, stroke=0)

        pdf.setFillColor(c("text_dark"))
        pdf.setFont("Helvetica-Bold", 9.5)
        pdf.drawString(jx, y, job["title"])

        parts = job["company"].split(",", 1)
        pdf.setFillColor(c("sky"))
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(jx, y - 12, parts[0])
        if len(parts) > 1:
            cw = pdf.stringWidth(parts[0], "Helvetica-Bold", 7.5)
            pdf.setFillColor(c("text_light"))
            pdf.setFont("Helvetica", 7.5)
            pdf.drawString(jx + cw + 1, y - 12, "," + parts[1])

        pdf.setFillColor(c("text_mid"))
        pdf.setFont("Helvetica", 7)
        pdf.drawString(jx, y - 22, job["period"])
        y -= 36

        for task in job["tasks"]:
            pdf.setFillColor(c("sky"))
            pdf.setFont("Courier", 7)
            pdf.drawString(jx, y + 1, "->")
            y = wrap_text(pdf, task, jx + 5 * mm, y,
                          "Helvetica", 7.5, c("text_mid"),
                          col1_w - 16 * mm, leading=10)
            y -= 4

        y -= 4

    # Timeline line spanning all stations
    pdf.setStrokeColor(c("border"))
    pdf.setLineWidth(0.6)
    pdf.line(col1_x + 1.5, timeline_top - 1, col1_x + 1.5, y + 8)

    y -= 4

    # ── Education ──
    y = draw_section(pdf, "AUSBILDUNG", col1_x, y, col1_w)

    for edu in data["education"]:
        pdf.setFillColor(c("text_dark"))
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawString(col1_x, y, edu["title"])

        tag = edu.get("tag", "")
        if tag:
            tag_col = c(edu.get("tag_style", "sky"))
            tx = col1_x + pdf.stringWidth(edu["title"], "Helvetica-Bold", 8.5) + 3 * mm
            tw = pdf.stringWidth(tag, "Helvetica-Bold", 5.5) + 4 * mm
            pdf.setFillColor(Color(tag_col.red, tag_col.green, tag_col.blue, alpha=0.15))
            pdf.roundRect(tx, y - 1.5, tw, 9, 3, fill=1, stroke=0)
            pdf.setFillColor(tag_col)
            pdf.setFont("Helvetica-Bold", 5.5)
            pdf.drawString(tx + 2 * mm, y, tag)

        pdf.setFillColor(c("text_light"))
        pdf.setFont("Helvetica", 7.5)
        pdf.drawRightString(col1_x + col1_w, y, edu["when"])
        y -= 11

        pdf.setFillColor(c("text_mid"))
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(col1_x, y, edu["where"])
        y -= 10

        note = edu.get("note", "")
        if note:
            y = wrap_text(pdf, note, col1_x, y,
                          "Helvetica", 7, c("text_light"),
                          col1_w, leading=9.5)
            y -= 2
        y -= 6

    return y


# ╔══════════════════════════════════════════════════════╗
# ║  RIGHT COLUMN                                       ║
# ╚══════════════════════════════════════════════════════╝

def draw_right_column(pdf, data, col2_x, col2_w, y):
    # ── Tech Stack ──
    y = draw_section(pdf, "TECH STACK", col2_x, y, col2_w)

    for sk in data["skills"]:
        sk_col = c(sk["color"])
        hint = sk.get("hint", "")

        # Skill name
        pdf.setFillColor(c("text_dark"))
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(col2_x, y, sk["name"])

        # Progress bar below name
        by = y - 8
        bw = col2_w - 1 * mm
        pdf.setFillColor(c("border"))
        pdf.roundRect(col2_x, by, bw, 3, 1.5, fill=1, stroke=0)
        pdf.setFillColor(sk_col)
        pdf.roundRect(col2_x, by, bw * sk["level"], 3, 1.5, fill=1, stroke=0)

        # Hint below bar (if present)
        if hint:
            pdf.setFillColor(c("text_light"))
            pdf.setFont("Helvetica", 5.5)
            pdf.drawString(col2_x, by - 5, hint)

        # Uniform spacing for all skills (with or without hint)
        y = by - 14
    y -= 3

    # ── Further education ──
    y = draw_section(pdf, "WEITERBILDUNG", col2_x, y, col2_w)

    for fe in data["further_education"]:
        pdf.setFillColor(c("sky"))
        pdf.setFont("Courier", 7)
        pdf.drawString(col2_x, y + 1, "->")
        y = wrap_text(pdf, fe["desc"], col2_x + 5 * mm, y,
                      "Helvetica", 7.5, c("text_mid"),
                      col2_w - 5 * mm, leading=9.5)
        y -= 4
    y -= 5

    # ── Languages ──
    y = draw_section(pdf, "SPRACHEN", col2_x, y, col2_w)

    for lang in data["languages"]:
        pdf.setFillColor(c("text_dark"))
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(col2_x, y, lang["name"])
        pdf.setFillColor(c("text_light"))
        pdf.setFont("Helvetica", 7)
        pdf.drawString(col2_x + 18 * mm, y, lang["level"])
        y -= 13
    y -= 5

    # ── Profile ──
    y = draw_section(pdf, "PROFIL", col2_x, y, col2_w)
    wrap_text(pdf, data["profile"], col2_x, y,
              "Helvetica", 7.5, c("text_mid"),
              col2_w, leading=10.5)

    return y


# ╔══════════════════════════════════════════════════════╗
# ║  FOOTER                                             ║
# ╚══════════════════════════════════════════════════════╝

def draw_footer(pdf, p):
    pdf.setFillColor(c("dark_bg"))
    pdf.rect(0, 0, W, 10 * mm, fill=1, stroke=0)
    pdf.setFillColor(c("dim"))
    pdf.setFont("Courier", 6.5)
    pdf.drawString(14 * mm, 3.5 * mm, f"// {p['location']}, {p['date']}")


# ╔══════════════════════════════════════════════════════╗
# ║  MAIN                                               ║
# ╚══════════════════════════════════════════════════════╝

def build_pdf(json_path: str, output_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    p = data["personal"]
    pdf = canvas.Canvas(output_path, pagesize=A4)

    col1_x = 14 * mm
    col1_w = 108 * mm
    col2_x = col1_x + col1_w + 8 * mm
    col2_w = W - col2_x - 14 * mm
    content_top = H - HEADER_H - 10 * mm

    draw_header(pdf, p, data.get("terminal_text", ""))
    draw_left_column(pdf, data, col1_x, col1_w, content_top)
    draw_right_column(pdf, data, col2_x, col2_w, content_top)
    draw_footer(pdf, p)

    pdf.save()
    print(f"Resume created: {os.path.abspath(output_path)}")


def next_versioned_name(base: str) -> str:
    """resume.pdf -> resume_v1.pdf, resume_v2.pdf, ..."""
    name, ext = os.path.splitext(base)
    version = 1
    while os.path.exists(f"{name}_v{version}{ext}"):
        version += 1
    return f"{name}_v{version}{ext}"


if __name__ == "__main__":
    args = sys.argv[1:]
    json_file = None
    out_file  = None

    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            out_file = args[i + 1]; i += 2
        elif args[i].endswith(".json"):
            json_file = args[i]; i += 1
        else:
            i += 1

    if json_file is None:
        json_file = "resume_data_default.json"

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found.")
        print(f"Expected in: {os.getcwd()}")
        sys.exit(1)

    if out_file is None:
        out_file = next_versioned_name("resume.pdf")

    build_pdf(json_file, out_file)
