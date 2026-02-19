"""
End-to-End Data Flow Diagram Generator
DM1 Prospective Data Collection Platform

Generates a visual pipeline diagram showing data flow from capture
through processing, de-identification, and research use, with
governance checkpoints and cross-cutting concerns.
"""

import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "data_flow_config.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data_flow_diagram.png")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# ── Colour palette ──────────────────────────────────────────────────
LAYER_COLOURS = {
    "client":         "#4A90D9",
    "network":        "#6C5CE7",
    "infrastructure": "#00B894",
    "application":    "#E17055",
    "data":           "#FDCB6E",
    "pipeline":       "#A29BFE",
    "research":       "#55EFC4",
    "external":       "#636E72",
}
STAGE_TEXT      = "#1A1A2E"
GOVERNANCE_BG   = "#F8F9FA"
GOVERNANCE_EDGE = "#BDC3C7"
ARROW_COLOUR    = "#2D3436"
CROSS_CUT_BG    = "#DFE6E9"
CROSS_CUT_EDGE  = "#636E72"

# ── Layout parameters ───────────────────────────────────────────────
stages = config["stages"]
N = len(stages)

# Pre-compute governance box widths based on longest line of text
gov_widths = []
for stage in stages:
    gov_text = stage.get("governance", "")
    gov_lines = gov_text.split("\n") if gov_text else [""]
    max_chars = max((len(l) for l in gov_lines), default=0)
    # Character-based width heuristic, clamped to sensible bounds
    box_w = max(4.0, min(7.0, max_chars * 0.14))
    gov_widths.append(box_w)

MAX_GOV_W = max(gov_widths) if gov_widths else 6.0

# Column positions (in figure coordinates)
STAGE_X      = 4.0       # centre of stage boxes
STAGE_W      = 6.2       # width of stage boxes
STAGE_H      = 1.1       # height of stage boxes
GOV_X        = 9.5       # left edge of governance annotations (close to stages)
ARROW_X_LEFT = STAGE_X + STAGE_W / 2 + 0.2
ARROW_X_RIGHT = GOV_X - 0.2

# Pre-compute content horizontal extent so figure width is tight
_iam_x  = -0.8
_iam_w  = 1.0
_obs_x  = GOV_X + MAX_GOV_W + 1.0
_obs_w  = 1.4
CONTENT_LEFT  = _iam_x - 0.4          # small left pad
CONTENT_RIGHT = _obs_x + _obs_w + 0.4 # small right pad

# Legend row-wrapping pre-computation
LEGEND_ITEM_W = 2.8   # width per legend item (swatch + label + gap)
_legend_items = 8
_legend_avail = CONTENT_RIGHT - CONTENT_LEFT - 1.0  # usable width
LEGEND_COLS   = max(1, int(_legend_avail // LEGEND_ITEM_W))
LEGEND_ROWS   = int(np.ceil(_legend_items / LEGEND_COLS))
LEGEND_ROW_H  = 0.5

ROW_HEIGHT = 1.8
TITLE_SPACE = 1.4      # space above first stage for title + headers
LEGEND_GAP  = 0.8      # gap between last stage and legend title

# ── Pre-compute all Y positions so figure height is exact ───────────
# Stages: first stage top is at a reference point; everything else relative.
_first_stage_top = 0.0  # temporary; we shift everything after computing extent
stage_tops = []
for i in range(N):
    stage_tops.append(_first_stage_top - i * ROW_HEIGHT)

# Side bars span from first stage top to last stage bottom
_side_bar_top = stage_tops[0] + STAGE_H / 2 - 0.15
_side_bar_bot = stage_tops[-1] - STAGE_H / 2 + 0.15

# Legend sits below the side bars
_legend_title_y = _side_bar_bot - LEGEND_GAP
_legend_bottom  = _legend_title_y - 0.55 - (LEGEND_ROWS - 1) * LEGEND_ROW_H - 0.15

# Title sits above the first stage
_title_y = stage_tops[0] + STAGE_H / 2 + TITLE_SPACE

# Determine y extent and add small padding
_y_max_content = _title_y + 0.3
_y_min_content = _legend_bottom - 0.3

# Shift everything so y_min = 0
_y_shift = -_y_min_content
FIG_HEIGHT = _y_max_content - _y_min_content
FIG_WIDTH  = CONTENT_RIGHT - CONTENT_LEFT

# ── Create figure ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
ax.set_xlim(CONTENT_LEFT, CONTENT_RIGHT)
ax.set_ylim(0, FIG_HEIGHT)
ax.axis("off")

# Helper: shift a raw y to figure coords
def fy(raw_y):
    return raw_y + _y_shift

# Pre-shifted key Y values
TITLE_Y  = fy(_title_y)
HEADER_Y = fy(stage_tops[0] + STAGE_H / 2 + 0.55)

# Column headers
ax.text(
    STAGE_X, HEADER_Y,
    "Processing Stage",
    ha="center", va="center",
    fontsize=20, fontweight="bold", color="#2D3436",
    fontfamily="sans-serif",
)
ax.text(
    GOV_X + MAX_GOV_W / 2, HEADER_Y,
    "Governance Controls",
    ha="center", va="center",
    fontsize=20, fontweight="bold", color="#2D3436",
    fontfamily="sans-serif",
)

# ── Draw stages ─────────────────────────────────────────────────────
stage_centres_y = []
for i, stage in enumerate(stages):
    y_centre = fy(stage_tops[i])
    stage_centres_y.append(y_centre)

    layer = stage["layer"]
    colour = LAYER_COLOURS.get(layer, "#BDC3C7")

    # Stage box
    box = FancyBboxPatch(
        (STAGE_X - STAGE_W / 2, y_centre - STAGE_H / 2),
        STAGE_W, STAGE_H,
        boxstyle="round,pad=0.12",
        facecolor=colour,
        edgecolor="#2D3436",
        linewidth=1.4,
        alpha=0.88,
    )
    ax.add_patch(box)

    # Stage number badge
    badge_x = STAGE_X - STAGE_W / 2 + 0.35
    badge_r = 0.22
    circle = plt.Circle(
        (badge_x, y_centre),
        badge_r,
        facecolor="#2D3436",
        edgecolor="white",
        linewidth=1.2,
        zorder=5,
    )
    ax.add_patch(circle)
    ax.text(
        badge_x, y_centre,
        str(i + 1),
        ha="center", va="center",
        fontsize=14, fontweight="bold", color="white",
        zorder=6,
    )

    # Stage label and sublabel
    # Determine text colour based on layer brightness
    text_col = "white" if layer in ("client", "network", "infrastructure",
                                     "application", "external") else "#1A1A2E"
    ax.text(
        STAGE_X + 0.15, y_centre + 0.18,
        stage["label"],
        ha="center", va="center",
        fontsize=18, fontweight="bold", color=text_col,
        fontfamily="sans-serif",
    )
    ax.text(
        STAGE_X + 0.15, y_centre - 0.22,
        stage["sublabel"],
        ha="center", va="center",
        fontsize=15, color=text_col, alpha=0.9,
        fontfamily="sans-serif",
    )

    # Governance annotation box
    gov_text = stage.get("governance", "")
    gov_lines = gov_text.split("\n")
    gov_box_h = max(0.85, len(gov_lines) * 0.27 + 0.35)
    gov_box_w = gov_widths[i]
    gov_y = y_centre

    gov_box = FancyBboxPatch(
        (GOV_X, gov_y - gov_box_h / 2),
        gov_box_w, gov_box_h,
        boxstyle="round,pad=0.1",
        facecolor=GOVERNANCE_BG,
        edgecolor=GOVERNANCE_EDGE,
        linewidth=1.0,
        alpha=0.9,
    )
    ax.add_patch(gov_box)

    for j, line in enumerate(gov_lines):
        line_y = gov_y + (len(gov_lines) - 1) * 0.125 - j * 0.25
        ax.text(
            GOV_X + 0.25, line_y,
            line,
            ha="left", va="center",
            fontsize=14, color="#2D3436",
            fontfamily="sans-serif",
        )

    # Dashed connector from stage to governance
    ax.annotate(
        "",
        xy=(GOV_X - 0.05, gov_y),
        xytext=(STAGE_X + STAGE_W / 2 + 0.05, y_centre),
        arrowprops=dict(
            arrowstyle="-",
            color="#95A5A6",
            linestyle="dashed",
            linewidth=1.0,
        ),
    )

# ── Flow arrows between stages ──────────────────────────────────────
for i in range(N - 1):
    y_start = stage_centres_y[i] - STAGE_H / 2 - 0.08
    y_end   = stage_centres_y[i + 1] + STAGE_H / 2 + 0.08

    ax.annotate(
        "",
        xy=(STAGE_X, y_end),
        xytext=(STAGE_X, y_start),
        arrowprops=dict(
            arrowstyle="-|>",
            color=ARROW_COLOUR,
            linewidth=2.0,
            mutation_scale=18,
        ),
    )

# ── Cross-cutting concern bars ──────────────────────────────────────
# IAM bar on the far left (kept clear of stage boxes)
iam = config["iam"]
iam_x = -0.8
iam_w = 1.0
# Shorten the bar slightly so it does not span the full stack height
iam_top = stage_centres_y[0] + STAGE_H / 2 - 0.15
iam_bot = stage_centres_y[-1] - STAGE_H / 2 + 0.15
iam_h = iam_top - iam_bot

iam_box = FancyBboxPatch(
    (iam_x, iam_bot),
    iam_w, iam_h,
    boxstyle="round,pad=0.12",
    facecolor="#DFE6E9",
    edgecolor="#636E72",
    linewidth=1.4,
    alpha=0.8,
)
ax.add_patch(iam_box)

# Vertical text inside the bar — label in upper half, sublabel in lower half
iam_mid_y = (iam_top + iam_bot) / 2
ax.text(
    iam_x + iam_w / 2, iam_mid_y + iam_h * 0.22,
    iam["label"],
    ha="center", va="center",
    fontsize=14, fontweight="bold", color="#2D3436",
    rotation=90,
    fontfamily="sans-serif",
)
ax.text(
    iam_x + iam_w / 2, iam_mid_y - iam_h * 0.22,
    iam["sublabel"],
    ha="center", va="center",
    fontsize=12, color="#636E72",
    rotation=90,
    fontfamily="sans-serif",
)

# Observability bar on the far right
obs = config["observability"]
obs_x = GOV_X + MAX_GOV_W + 1.0
obs_w = 1.4
obs_top = iam_top
obs_bot = iam_bot
obs_h = obs_top - obs_bot

obs_box = FancyBboxPatch(
    (obs_x, obs_bot),
    obs_w, obs_h,
    boxstyle="round,pad=0.12",
    facecolor="#DFE6E9",
    edgecolor="#636E72",
    linewidth=1.4,
    alpha=0.8,
)
ax.add_patch(obs_box)

obs_mid_y = (obs_top + obs_bot) / 2
ax.text(
    obs_x + obs_w / 2, obs_mid_y + obs_h * 0.22,
    obs["label"],
    ha="center", va="center",
    fontsize=14, fontweight="bold", color="#2D3436",
    rotation=270,
    fontfamily="sans-serif",
)
ax.text(
    obs_x + obs_w / 2, obs_mid_y - obs_h * 0.22,
    obs["sublabel"],
    ha="center", va="center",
    fontsize=12, color="#636E72",
    rotation=270,
    fontfamily="sans-serif",
)

# ── Compute graph extent for dynamic centring ───────────────────────
graph_left  = iam_x
graph_right = obs_x + obs_w
graph_centre_x = (graph_left + graph_right) / 2
graph_span = graph_right - graph_left

# ── Draw the title, centred on the actual graph ─────────────────────
ax.text(
    graph_centre_x, TITLE_Y,
    config["title"],
    ha="center", va="top",
    fontsize=24, fontweight="bold", color="#1A1A2E",
    fontfamily="sans-serif",
)

# ── Layer legend (row-wrapping, dynamically centred) ────────────────
layer_labels = {
    "client":         "Client Layer",
    "network":        "Network Layer",
    "infrastructure": "Infrastructure Layer",
    "application":    "Application Layer",
    "data":           "Data Layer",
    "pipeline":       "Pipeline Layer",
    "research":       "Research Layer",
    "external":       "External Layer",
}

legend_base_y = fy(_legend_title_y)  # anchored relative to graph bottom
items = list(layer_labels.items())
num_items = len(items)

# Title above all legend rows
ax.text(
    graph_centre_x, legend_base_y + 0.2,
    "Architecture Layers",
    ha="center", va="center",
    fontsize=15, fontweight="bold", color="#2D3436",
    fontfamily="sans-serif",
)

for idx, (layer_key, label) in enumerate(items):
    row = idx // LEGEND_COLS
    col = idx % LEGEND_COLS
    items_in_row = min(LEGEND_COLS, num_items - row * LEGEND_COLS)
    row_width = items_in_row * LEGEND_ITEM_W
    row_left = graph_centre_x - row_width / 2

    lx = row_left + col * LEGEND_ITEM_W
    ly = legend_base_y - 0.55 - row * LEGEND_ROW_H
    colour = LAYER_COLOURS[layer_key]

    legend_patch = FancyBboxPatch(
        (lx, ly - 0.15),
        0.4, 0.3,
        boxstyle="round,pad=0.04",
        facecolor=colour,
        edgecolor="#2D3436",
        linewidth=0.8,
        alpha=0.88,
    )
    ax.add_patch(legend_patch)
    ax.text(
        lx + 0.55, ly,
        label,
        ha="left", va="center",
        fontsize=13, color="#2D3436",
        fontfamily="sans-serif",
    )

# ── Save ────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.5)
fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Data flow diagram saved to {OUTPUT_PATH}")
