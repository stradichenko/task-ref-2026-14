#!/usr/bin/env python3
"""
Entity-Relationship Diagram Generator
DM1 Multi-Modal Dataset

Generates a database schema diagram (ERD) showing tables grouped by
domain (clinical, genomic, proteomic, governance), with columns,
data types, primary/foreign key markers, and relationship lines.

Usage:
    python erd_diagram.py                       # defaults → erd_config.json → erd_diagram.png
    python erd_diagram.py -c config.json -o out.png
"""

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.colors import to_rgba
import numpy as np

# ── Defaults ────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "erd_config.json")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "erd_diagram.png")


# ── Config loader ───────────────────────────────────────────────────
def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── Colour helpers ──────────────────────────────────────────────────
def lighten(hex_color: str, amount: float = 0.85) -> tuple:
    """Return a lightened RGBA tuple for use as table body background."""
    r, g, b, _ = to_rgba(hex_color)
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount, 1.0)


def darken(hex_color: str, amount: float = 0.25) -> tuple:
    r, g, b, _ = to_rgba(hex_color)
    return (r * (1 - amount), g * (1 - amount), b * (1 - amount), 1.0)


# ── Layout constants ────────────────────────────────────────────────
HEADER_H   = 0.48       # height of table header row
ROW_H      = 0.34       # height of each column row
COL_PAD    = 0.18       # horizontal padding inside table box
TABLE_W    = 4.2        # width of every table box
GROUP_PAD  = 0.7        # vertical padding between domain groups
TABLE_PAD  = 0.45       # vertical padding between tables within a group
FONT_SIZE  = 8.5
HEADER_FS  = 10
TITLE_FS   = 18
SUBTITLE_FS = 12
PK_SYMBOL  = "PK"
FK_SYMBOL  = "FK"


# ── Positioning logic ──────────────────────────────────────────────
def compute_table_height(table: dict) -> float:
    return HEADER_H + len(table["columns"]) * ROW_H


def layout_tables(config: dict):
    """
    Assign (x, y) positions to every table, grouped by domain in columns.

    Returns:
        table_positions : dict   table_id → (x, y_top)
        fig_w, fig_h    : float  required figure size
    """
    tables = config["tables"]
    domains = config["domains"]

    # Bucket tables by domain, preserving config order
    domain_order = list(domains.keys())
    buckets = {d: [] for d in domain_order}
    for t in tables:
        buckets[t["domain"]].append(t)

    col_gap = TABLE_W + 1.8  # horizontal gap between domain columns
    margin_top = 2.2
    margin_bottom = 1.6
    margin_left = 1.0

    positions = {}
    max_col_bottom = 0

    for col_idx, domain_key in enumerate(domain_order):
        x = margin_left + col_idx * col_gap
        y_cursor = margin_top
        for t in buckets[domain_key]:
            h = compute_table_height(t)
            positions[t["id"]] = (x, y_cursor)
            y_cursor += h + TABLE_PAD
        col_bottom = y_cursor - TABLE_PAD + margin_bottom
        if col_bottom > max_col_bottom:
            max_col_bottom = col_bottom

    fig_w = margin_left + len(domain_order) * col_gap + 0.6
    fig_h = max_col_bottom

    return positions, fig_w, fig_h


# ── Drawing helpers ─────────────────────────────────────────────────
def draw_table(ax, table: dict, x: float, y_top: float, domain_color: str):
    """Draw a single table box with header and column rows."""
    n_cols = len(table["columns"])
    h = compute_table_height(table)
    body_bg = lighten(domain_color, 0.88)
    header_bg = to_rgba(domain_color)

    # Outer border
    outer = FancyBboxPatch(
        (x, y_top), TABLE_W, h,
        boxstyle="round,pad=0.06",
        facecolor=body_bg,
        edgecolor=darken(domain_color, 0.3),
        linewidth=1.3,
    )
    ax.add_patch(outer)

    # Header band
    header = FancyBboxPatch(
        (x, y_top), TABLE_W, HEADER_H,
        boxstyle="round,pad=0.06",
        facecolor=header_bg,
        edgecolor=darken(domain_color, 0.3),
        linewidth=1.3,
    )
    ax.add_patch(header)

    # Table name
    ax.text(
        x + TABLE_W / 2, y_top + HEADER_H / 2,
        table["label"],
        ha="center", va="center",
        fontsize=HEADER_FS, fontweight="bold", color="white",
        fontfamily="monospace",
    )

    # Column rows
    for i, col in enumerate(table["columns"]):
        row_y = y_top + HEADER_H + i * ROW_H
        # Alternating row shading
        if i % 2 == 1:
            alt = FancyBboxPatch(
                (x + 0.04, row_y + 0.02), TABLE_W - 0.08, ROW_H - 0.04,
                boxstyle="square,pad=0",
                facecolor=lighten(domain_color, 0.93),
                edgecolor="none",
            )
            ax.add_patch(alt)

        # Key badge
        badge = ""
        badge_color = None
        if col.get("pk"):
            badge = PK_SYMBOL
            badge_color = "#D4AC0D"
        elif col.get("fk"):
            badge = FK_SYMBOL
            badge_color = "#5DADE2"

        # Column name
        name_x = x + COL_PAD + (0.42 if badge else 0.0)
        ax.text(
            name_x, row_y + ROW_H / 2,
            col["name"],
            ha="left", va="center",
            fontsize=FONT_SIZE, color="#1A1A2E",
            fontfamily="monospace",
        )
        if badge:
            bx = x + COL_PAD
            by = row_y + ROW_H / 2
            badge_box = FancyBboxPatch(
                (bx - 0.02, by - 0.10), 0.36, 0.20,
                boxstyle="round,pad=0.03",
                facecolor=badge_color, edgecolor="none", alpha=0.85,
            )
            ax.add_patch(badge_box)
            ax.text(
                bx + 0.16, by,
                badge,
                ha="center", va="center",
                fontsize=6.5, fontweight="bold", color="white",
                fontfamily="sans-serif",
            )

        # Data type (right-aligned)
        ax.text(
            x + TABLE_W - COL_PAD, row_y + ROW_H / 2,
            col["type"],
            ha="right", va="center",
            fontsize=FONT_SIZE - 0.5, color="#636E72",
            fontfamily="monospace",
        )


def find_column_y(table: dict, col_name: str, y_top: float) -> float:
    """Return the vertical centre of a specific column row."""
    for i, col in enumerate(table["columns"]):
        if col["name"] == col_name:
            return y_top + HEADER_H + i * ROW_H + ROW_H / 2
    return y_top + HEADER_H + ROW_H / 2  # fallback


def draw_relationship(ax, rel: dict, config: dict, positions: dict):
    """Draw a relationship line between two columns in different tables."""
    from_table_id, from_col = rel["from"].split(".", 1)
    to_table_id, to_col = rel["to"].split(".", 1)

    tables_by_id = {t["id"]: t for t in config["tables"]}

    from_table = tables_by_id[from_table_id]
    to_table = tables_by_id[to_table_id]

    fx, fy_top = positions[from_table_id]
    tx, ty_top = positions[to_table_id]

    fy = find_column_y(from_table, from_col, fy_top)
    ty = find_column_y(to_table, to_col, ty_top)

    # Decide which side of each box to connect
    from_cx = fx + TABLE_W / 2
    to_cx = tx + TABLE_W / 2

    if from_cx < to_cx:
        x1 = fx + TABLE_W
        x2 = tx
    elif from_cx > to_cx:
        x1 = fx
        x2 = tx + TABLE_W
    else:
        # Same column — connect on the right
        x1 = fx + TABLE_W
        x2 = tx + TABLE_W

    # Curved connection
    mid_x = (x1 + x2) / 2
    # If tables are in the same column, route the line to the right
    if abs(from_cx - to_cx) < 0.5:
        offset = TABLE_W * 0.35
        verts_x = [x1, x1 + offset, x1 + offset, x2]
        verts_y = [fy, fy, ty, ty]
        ax.plot(verts_x, verts_y, color="#95A5A6", linewidth=0.9,
                linestyle="-", alpha=0.7, zorder=0)
    else:
        ax.annotate(
            "",
            xy=(x2, ty), xytext=(x1, fy),
            arrowprops=dict(
                arrowstyle="-",
                color="#95A5A6",
                linewidth=0.9,
                connectionstyle="arc3,rad=0.15",
            ),
            zorder=0,
        )

    # Cardinality labels
    card = rel.get("cardinality", "")
    if card:
        parts = card.split(":")
        if len(parts) == 2:
            ax.text(x1, fy + 0.12, parts[0], ha="center", va="bottom",
                    fontsize=6.5, color="#636E72", fontweight="bold")
            ax.text(x2, ty + 0.12, parts[1], ha="center", va="bottom",
                    fontsize=6.5, color="#636E72", fontweight="bold")


# ── Main drawing routine ────────────────────────────────────────────
def draw_erd(config: dict, output_path: str):
    positions, fig_w, fig_h = layout_tables(config)
    domains = config["domains"]
    tables_by_id = {t["id"]: t for t in config["tables"]}

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(fig_h, 0)  # y increases downward for natural reading order
    ax.axis("off")

    # Title
    ax.text(
        fig_w / 2, 0.5,
        config["title"],
        ha="center", va="center",
        fontsize=TITLE_FS, fontweight="bold", color="#1A1A2E",
        fontfamily="sans-serif",
    )
    if config.get("subtitle"):
        ax.text(
            fig_w / 2, 1.05,
            config["subtitle"],
            ha="center", va="center",
            fontsize=SUBTITLE_FS, color="#636E72",
            fontfamily="sans-serif",
        )

    # Domain column headers
    domain_order = list(domains.keys())
    col_gap = TABLE_W + 1.8
    margin_left = 1.0
    for col_idx, dk in enumerate(domain_order):
        cx = margin_left + col_idx * col_gap + TABLE_W / 2
        d = domains[dk]
        ax.text(
            cx, 1.65,
            d["label"],
            ha="center", va="center",
            fontsize=13, fontweight="bold",
            color=to_rgba(d["color"]),
            fontfamily="sans-serif",
        )

    # Draw relationships first (below tables)
    for rel in config.get("relationships", []):
        try:
            draw_relationship(ax, rel, config, positions)
        except KeyError:
            pass  # skip if table/column not found

    # Draw tables
    for t in config["tables"]:
        domain_color = domains[t["domain"]]["color"]
        x, y_top = positions[t["id"]]
        draw_table(ax, t, x, y_top, domain_color)

    # Legend
    legend_y = fig_h - 0.8
    lx = margin_left

    # PK / FK badge legends
    for badge_text, badge_color, label in [
        ("PK", "#D4AC0D", "Primary Key"),
        ("FK", "#5DADE2", "Foreign Key"),
    ]:
        badge_box = FancyBboxPatch(
            (lx, legend_y - 0.13), 0.36, 0.26,
            boxstyle="round,pad=0.03",
            facecolor=badge_color, edgecolor="none", alpha=0.85,
        )
        ax.add_patch(badge_box)
        ax.text(lx + 0.18, legend_y, badge_text,
                ha="center", va="center",
                fontsize=7, fontweight="bold", color="white",
                fontfamily="sans-serif")
        ax.text(lx + 0.50, legend_y, label,
                ha="left", va="center",
                fontsize=9, color="#2D3436", fontfamily="sans-serif")
        lx += 2.5

    # Domain colour swatches in legend
    for dk in domain_order:
        d = domains[dk]
        swatch = FancyBboxPatch(
            (lx, legend_y - 0.13), 0.35, 0.26,
            boxstyle="round,pad=0.03",
            facecolor=to_rgba(d["color"]),
            edgecolor="none",
        )
        ax.add_patch(swatch)
        ax.text(lx + 0.50, legend_y, d["label"],
                ha="left", va="center",
                fontsize=9, color="#2D3436", fontfamily="sans-serif")
        lx += 2.5

    # Save
    plt.tight_layout(pad=0.3)
    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"ERD saved to {output_path}")


# ── CLI ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Generate a database schema diagram (ERD) for the DM1 dataset."
    )
    parser.add_argument(
        "-c", "--config", default=DEFAULT_CONFIG,
        help="Path to the JSON config file (default: erd_config.json)",
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT,
        help="Output image path (default: erd_diagram.png)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    draw_erd(config, args.output)


if __name__ == "__main__":
    main()
