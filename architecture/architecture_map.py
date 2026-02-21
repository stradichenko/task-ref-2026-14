"""
Architecture Map Generator  —  Top-Down Pipeline Layout (Dynamic Sizing)
DM1 Prospective Data Collection Platform

Zones are stacked vertically from top (Client) to bottom (External),
making the data-flow direction immediately obvious.  IAM and
Observability run as full-height sidebars on left and right.

Cards are dynamically sized to fit their text content so there is no
dead space.  Arrows and badges are coloured per source-zone for easy
visual distinction.

Usage:
    python architecture_map.py [-c CONFIG] [-o OUTPUT]
"""

import argparse
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "architecture_config.json")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "architecture_map.png")

parser = argparse.ArgumentParser(description="DM1 Architecture Map Generator")
parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT)
args = parser.parse_args()

with open(args.config) as fh:
    config = json.load(fh)

# ═══════════════════════════════════════════════════════════════════
#  FONTS  — very large for readability
# ═══════════════════════════════════════════════════════════════════
FF             = "sans-serif"
TITLE_SZ       = 84
SUBTITLE_SZ    = 50
ZONE_LABEL_SZ  = 58
COMP_LABEL_SZ  = 40
COMP_SUB_SZ    = 32
COMP_DETAIL_SZ = 26
ICON_SZ        = 32
BADGE_SZ       = 34
SIDEBAR_SZ     = 48
SIDEBAR_SUB_SZ = 32
LEGEND_SZ      = 32
FLOW_SZ        = 32
FLOW_HEAD_SZ   = 52
ARROW_LBL_SZ   = 32

BADGE_R = 0.80          # uniform numbered-badge radius

BG = "#FAFBFC"

# ═══════════════════════════════════════════════════════════════════
#  COLOUR — per-zone arrow & badge colours (no single ARROW_CLR)
# ═══════════════════════════════════════════════════════════════════
zones_by_id = {z["id"]: z for z in config["zones"]}

# component-id → zone-id
comp_to_zone = {}
for z in config["zones"]:
    for c in z["components"]:
        comp_to_zone[c["id"]] = z["id"]

# flow-step number (str) → source-zone border colour
step_colours = {}
for conn in config["connections"]:
    fid = conn["from"]
    zid = comp_to_zone[fid]
    step_colours[str(conn["number"])] = zones_by_id[zid]["border"]


def zone_clr(zone_id):
    """Return the border colour of a zone."""
    return zones_by_id[zone_id]["border"]


# ═══════════════════════════════════════════════════════════════════
#  TEXT MEASUREMENT  (data units ≈ inches)
# ═══════════════════════════════════════════════════════════════════
def est_w(text, fontsize):
    """Approximate text width in data units."""
    return len(text) * fontsize * 0.55 / 72


def est_h(fontsize, spacing=1.35):
    """Approximate single-line height in data units."""
    return fontsize * spacing / 72


# ═══════════════════════════════════════════════════════════════════
#  DYNAMIC CARD SIZING
# ═══════════════════════════════════════════════════════════════════
CARD_PAD_X   = 0.8       # horizontal padding each side inside card
CARD_ICON_H  = 1.7       # space consumed by the icon badge + gap
CARD_LINE_GAP = 0.15     # small gap between sublabel and detail block
CARD_PAD_BOT = 0.30      # bottom padding inside card

ZONE_ORDER = config.get("zone_order",
    ["client", "gateway_iam", "operational", "processing",
     "research", "external"])
N_ZONES = len(ZONE_ORDER)

zone_card_w = {}   # zone_id → card width  (uniform per zone)
zone_card_h = {}   # zone_id → card height (uniform per zone)

for zid in ZONE_ORDER:
    zone = zones_by_id[zid]
    max_w = 0.0
    max_h = 0.0
    for comp in zone["components"]:
        # Width — widest text line + padding
        widths = [
            est_w(comp["label"], COMP_LABEL_SZ),
            est_w(comp.get("sublabel", ""), COMP_SUB_SZ),
        ]
        detail_lines = comp.get("detail", "").split("\n")
        for dl in detail_lines:
            widths.append(est_w(dl, COMP_DETAIL_SZ))
        needed_w = max(widths) + 2 * CARD_PAD_X
        max_w = max(max_w, needed_w)

        # Height — stack elements
        needed_h = (CARD_ICON_H
                    + est_h(COMP_LABEL_SZ)
                    + est_h(COMP_SUB_SZ)
                    + CARD_LINE_GAP
                    + len(detail_lines) * est_h(COMP_DETAIL_SZ, 1.55)
                    + CARD_PAD_BOT)
        max_h = max(max_h, needed_h)

    zone_card_w[zid] = max_w
    zone_card_h[zid] = max_h

# ═══════════════════════════════════════════════════════════════════
#  LAYOUT CONSTANTS
# ═══════════════════════════════════════════════════════════════════
SIDEBAR_W    = 5.5
ZONE_PAD_X   = 1.2
GAP_X        = 1.0
COMP_GAP     = 1.0
ZONE_HEADER  = 2.0
ZONE_CARD_GAP = 0.55     # gap between zone header line and cards
ZONE_PAD_Y   = 0.6       # below cards inside zone
ARROW_ZONE   = 2.2       # vertical space for big flow arrow

# zone content width = widest zone row
needed_ws = []
for zid in ZONE_ORDER:
    n = len(zones_by_id[zid]["components"])
    cw = zone_card_w[zid]
    needed_ws.append(n * cw + (n - 1) * COMP_GAP + 2 * ZONE_PAD_X)

ZONE_CONTENT_W = max(needed_ws)

# per-zone band height
zone_band_h = {}
for zid in ZONE_ORDER:
    zone_band_h[zid] = ZONE_HEADER + ZONE_CARD_GAP + zone_card_h[zid] + ZONE_PAD_Y

# ── Figure size ───────────────────────────────────────────────────
TITLE_H  = 5.5
LEGEND_H = 7.0

FIG_W = GAP_X + SIDEBAR_W + GAP_X + ZONE_CONTENT_W + GAP_X + SIDEBAR_W + GAP_X
FIG_H = (TITLE_H
         + sum(zone_band_h[z] for z in ZONE_ORDER)
         + (N_ZONES - 1) * ARROW_ZONE
         + 1.2
         + LEGEND_H
         + 1.0)

ZONE_LEFT  = GAP_X + SIDEBAR_W + GAP_X
ZONE_RIGHT = ZONE_LEFT + ZONE_CONTENT_W

# ═══════════════════════════════════════════════════════════════════
#  PRE-COMPUTE positions
# ═══════════════════════════════════════════════════════════════════
zone_tops = {}       # zone_id → y of top edge of band
comp_centres = {}    # comp_id → (cx, cy)

cursor_y = FIG_H - TITLE_H

for zid in ZONE_ORDER:
    zone_tops[zid] = cursor_y
    zone = zones_by_id[zid]
    comps = zone["components"]
    n = len(comps)
    cw = zone_card_w[zid]
    ch = zone_card_h[zid]
    total_w = n * cw + (n - 1) * COMP_GAP
    start_x = ZONE_LEFT + (ZONE_CONTENT_W - total_w) / 2
    card_top = cursor_y - ZONE_HEADER - ZONE_CARD_GAP
    for ci, comp in enumerate(comps):
        cx = start_x + ci * (cw + COMP_GAP) + cw / 2
        cy = card_top - ch / 2
        comp_centres[comp["id"]] = (cx, cy)
    cursor_y -= zone_band_h[zid] + ARROW_ZONE

ZONES_BOTTOM = cursor_y + ARROW_ZONE

# ═══════════════════════════════════════════════════════════════════
#  DRAW
# ═══════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(BG)

# ── Title ─────────────────────────────────────────────────────────
ty = FIG_H - 1.4
ax.text(FIG_W / 2, ty, config["title"],
        ha="center", va="center", fontsize=TITLE_SZ, fontweight="bold",
        color="#1A1A2E", fontfamily=FF)
ax.text(FIG_W / 2, ty - 1.8, config.get("subtitle", ""),
        ha="center", va="center", fontsize=SUBTITLE_SZ, color="#546E7A",
        fontfamily=FF, style="italic")

# ── Sidebars ──────────────────────────────────────────────────────
sidebar_top = zone_tops[ZONE_ORDER[0]]
sidebar_bot = zone_tops[ZONE_ORDER[-1]] - zone_band_h[ZONE_ORDER[-1]]

sidebars = config.get("sidebars", {})
for side, sb in sidebars.items():
    sx = GAP_X if side == "left" else ZONE_RIGHT + GAP_X
    sh = sidebar_top - sidebar_bot
    ax.add_patch(FancyBboxPatch(
        (sx, sidebar_bot), SIDEBAR_W, sh,
        boxstyle="round,pad=0.28",
        facecolor=sb["colour"], edgecolor=sb["border"],
        linewidth=4.0, alpha=0.50))

    mid_y = (sidebar_top + sidebar_bot) / 2
    rot = 90 if side == "left" else 270
    ax.text(sx + SIDEBAR_W / 2, mid_y + sh * 0.18,
            sb["label"], ha="center", va="center",
            fontsize=SIDEBAR_SZ, fontweight="bold", color=sb["border"],
            fontfamily=FF, rotation=rot, linespacing=1.3)
    ax.text(sx + SIDEBAR_W / 2, mid_y - sh * 0.18,
            sb.get("sublabel", ""), ha="center", va="center",
            fontsize=SIDEBAR_SUB_SZ, color="#546E7A",
            fontfamily=FF, rotation=rot, linespacing=1.3)

    # Dashed ticks into each zone
    for zid2 in ZONE_ORDER:
        zy = zone_tops[zid2] - zone_band_h[zid2] / 2
        if side == "left":
            ax.plot([sx + SIDEBAR_W, sx + SIDEBAR_W + GAP_X * 0.7],
                    [zy, zy], color=sb["border"],
                    linestyle="dashed", linewidth=2.5, alpha=0.40)
        else:
            ax.plot([sx - GAP_X * 0.7, sx],
                    [zy, zy], color=sb["border"],
                    linestyle="dashed", linewidth=2.5, alpha=0.40)

# ── Zone bands and component cards ────────────────────────────────
for zid in ZONE_ORDER:
    zone = zones_by_id[zid]
    ztop = zone_tops[zid]
    zh = zone_band_h[zid]
    cw = zone_card_w[zid]
    ch = zone_card_h[zid]

    # Band
    ax.add_patch(FancyBboxPatch(
        (ZONE_LEFT, ztop - zh), ZONE_CONTENT_W, zh,
        boxstyle="round,pad=0.28",
        facecolor=zone["colour"], edgecolor=zone["border"],
        linewidth=4.0, alpha=0.50))

    # Zone label
    ax.text(ZONE_LEFT + 0.8, ztop - 1.0, zone["label"],
            ha="left", va="center",
            fontsize=ZONE_LABEL_SZ, fontweight="bold",
            color=zone["border"], fontfamily=FF)

    # Accent line
    ax.plot([ZONE_LEFT + 0.25, ZONE_RIGHT - 0.25],
            [ztop - ZONE_HEADER + 0.04, ztop - ZONE_HEADER + 0.04],
            color=zone["border"], linewidth=3.0, alpha=0.30)

    # Cards
    comps = zone["components"]
    n = len(comps)
    total_w = n * cw + (n - 1) * COMP_GAP
    start_x = ZONE_LEFT + (ZONE_CONTENT_W - total_w) / 2
    card_top = ztop - ZONE_HEADER - ZONE_CARD_GAP

    for ci, comp in enumerate(comps):
        cx = start_x + ci * (cw + COMP_GAP) + cw / 2
        cl = cx - cw / 2
        cb = card_top - ch

        # Shadow
        ax.add_patch(FancyBboxPatch(
            (cl + 0.08, cb - 0.08), cw, ch,
            boxstyle="round,pad=0.14",
            facecolor="#B0BEC5", edgecolor="none", alpha=0.18))

        # Card box
        ax.add_patch(FancyBboxPatch(
            (cl, cb), cw, ch,
            boxstyle="round,pad=0.16",
            facecolor="white", edgecolor=zone["border"],
            linewidth=3.0, alpha=0.95))

        # Icon badge
        iy = card_top - 0.80
        ax.add_patch(plt.Circle(
            (cx, iy), 0.65,
            facecolor=zone["border"], edgecolor="white",
            linewidth=3.2, alpha=0.85, zorder=5))
        ax.text(cx, iy, comp.get("icon", ""),
                ha="center", va="center",
                fontsize=ICON_SZ, fontweight="bold",
                color="white", zorder=6, fontfamily=FF)

        # Label
        label_y = card_top - CARD_ICON_H
        ax.text(cx, label_y, comp["label"],
                ha="center", va="center",
                fontsize=COMP_LABEL_SZ, fontweight="bold",
                color="#1A1A2E", fontfamily=FF)

        # Sublabel
        sub_y = label_y - est_h(COMP_LABEL_SZ)
        ax.text(cx, sub_y, comp.get("sublabel", ""),
                ha="center", va="center",
                fontsize=COMP_SUB_SZ, color="#546E7A", fontfamily=FF)

        # Detail lines
        detail_top = sub_y - est_h(COMP_SUB_SZ) - CARD_LINE_GAP
        detail_lh = est_h(COMP_DETAIL_SZ, 1.55)
        for di, dline in enumerate(comp.get("detail", "").split("\n")):
            ax.text(cx, detail_top - di * detail_lh, dline,
                    ha="center", va="center",
                    fontsize=COMP_DETAIL_SZ, color="#78909C", fontfamily=FF)

# ═══════════════════════════════════════════════════════════════════
#  BIG FLOW ARROWS between consecutive zones — zone-coloured
# ═══════════════════════════════════════════════════════════════════
flow_labels = {
    ("client", "gateway_iam"):     ("1",  "HTTPS + TLS 1.2+"),
    ("gateway_iam", "operational"): ("3",  "Validated & authorised"),
    ("operational", "processing"):  ("5",  "Operational data export"),
    ("processing", "research"):     ("7",  "OMOP CDM load"),
    ("research", "external"):       ("10", "Governed sharing"),
}

for i in range(N_ZONES - 1):
    z_from = ZONE_ORDER[i]
    z_to   = ZONE_ORDER[i + 1]
    y_start = zone_tops[z_from] - zone_band_h[z_from] - 0.10
    y_end   = zone_tops[z_to] + 0.10
    mid_x   = ZONE_LEFT + ZONE_CONTENT_W / 2

    arrow_clr = zone_clr(z_from)
    arc_rad   = 0.25 if i % 2 == 0 else -0.25

    ax.annotate("",
        xy=(mid_x, y_end), xytext=(mid_x, y_start),
        arrowprops=dict(
            arrowstyle="-|>", color=arrow_clr,
            linewidth=6.0, mutation_scale=44,
            connectionstyle=f"arc3,rad={arc_rad}",
            shrinkA=5, shrinkB=5),
        zorder=4)

    pair = (z_from, z_to)
    if pair in flow_labels:
        num, lbl = flow_labels[pair]
        my = (y_start + y_end) / 2
        badge_clr = step_colours.get(num, arrow_clr)
        ax.add_patch(plt.Circle(
            (mid_x - 2.8, my), BADGE_R,
            facecolor=badge_clr, edgecolor="white",
            linewidth=3.2, zorder=10))
        ax.text(mid_x - 2.8, my, num,
                ha="center", va="center",
                fontsize=BADGE_SZ, fontweight="bold",
                color="white", zorder=11)
        ax.text(mid_x + 1.8, my, lbl,
                ha="left", va="center",
                fontsize=ARROW_LBL_SZ, color="#37474F",
                fontfamily=FF, style="italic")

# ═══════════════════════════════════════════════════════════════════
#  LATERAL CONNECTIONS (intra-zone) — zone-coloured
# ═══════════════════════════════════════════════════════════════════
lateral_connections = [
    ("api_gateway", "keycloak",        "2", "Token validation",   0.45),
    ("api_gateway", "app_services",    "3", "Validated request",  -0.35),
    ("app_services", "identity_store", "4", "ID resolution",      0.55),
    ("omop_warehouse", "atlas",        "8", "WebAPI",             0.40),
    ("omop_warehouse", "analytics_env","8", "Read-only SQL",      -0.40),
    ("fhir_facade", "app_services",    "9", "FHIR R4 interop",   0.50),
]

drawn_badges = set()

for fid, tid, num, lbl, rad in lateral_connections:
    if fid not in comp_centres or tid not in comp_centres:
        continue
    fcx, fcy = comp_centres[fid]
    tcx, tcy = comp_centres[tid]

    from_zone = comp_to_zone[fid]
    to_zone   = comp_to_zone[tid]
    arrow_clr = zone_clr(from_zone)

    hw1 = zone_card_w[from_zone] / 2
    hh1 = zone_card_h[from_zone] / 2
    hw2 = zone_card_w[to_zone] / 2
    hh2 = zone_card_h[to_zone] / 2

    dx, dy = tcx - fcx, tcy - fcy
    if abs(dx) > abs(dy):
        x1 = fcx + hw1 + 0.10 if dx > 0 else fcx - hw1 - 0.10
        y1 = fcy
        x2 = tcx - hw2 - 0.10 if dx > 0 else tcx + hw2 + 0.10
        y2 = tcy
    else:
        x1 = fcx
        y1 = fcy + hh1 + 0.10 if dy > 0 else fcy - hh1 - 0.10
        x2 = tcx
        y2 = tcy - hh2 - 0.10 if dy > 0 else tcy + hh2 + 0.10

    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>", color=arrow_clr,
            linewidth=4.0, mutation_scale=32,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=5, shrinkB=5),
        zorder=3)

    if num not in drawn_badges:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        mx += nx * rad * 0.55
        my += ny * rad * 0.55
        badge_clr = step_colours.get(num, arrow_clr)
        ax.add_patch(plt.Circle(
            (mx, my), BADGE_R,
            facecolor=badge_clr, edgecolor="white",
            linewidth=3.2, zorder=10))
        ax.text(mx, my, num,
                ha="center", va="center",
                fontsize=BADGE_SZ, fontweight="bold",
                color="white", zorder=11)
        drawn_badges.add(num)

# ═══════════════════════════════════════════════════════════════════
#  VERTICAL THROUGH-ARROWS (cross-zone) — zone-coloured
# ═══════════════════════════════════════════════════════════════════
vertical_connections = [
    ("app_services", "clinical_db",      "4",  0.22),
    ("clinical_db",  "deidentification", "5", -0.28),
    ("etl_mapping",  "omop_warehouse",   "7",  0.22),
]

for fid, tid, num, rad in vertical_connections:
    if fid not in comp_centres or tid not in comp_centres:
        continue
    fcx, fcy = comp_centres[fid]
    tcx, tcy = comp_centres[tid]

    from_zone = comp_to_zone[fid]
    to_zone   = comp_to_zone[tid]
    arrow_clr = zone_clr(from_zone)

    hh1 = zone_card_h[from_zone] / 2
    hh2 = zone_card_h[to_zone] / 2

    x1, y1 = fcx, fcy - hh1 - 0.10
    x2, y2 = tcx, tcy + hh2 + 0.10

    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>", color=arrow_clr,
            linewidth=4.0, mutation_scale=32,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=5, shrinkB=5),
        zorder=3)

    if num not in drawn_badges:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ln = math.hypot(x2 - x1, y2 - y1) or 1.0
        nx, ny = -(y2 - y1) / ln, (x2 - x1) / ln
        mx += nx * rad * 0.55
        my += ny * rad * 0.55
        badge_clr = step_colours.get(num, arrow_clr)
        ax.add_patch(plt.Circle(
            (mx, my), BADGE_R,
            facecolor=badge_clr, edgecolor="white",
            linewidth=3.2, zorder=10))
        ax.text(mx, my, num,
                ha="center", va="center",
                fontsize=BADGE_SZ, fontweight="bold",
                color="white", zorder=11)
        drawn_badges.add(num)

# ═══════════════════════════════════════════════════════════════════
#  DATA-FLOW SEQUENCE LEGEND
# ═══════════════════════════════════════════════════════════════════
flow_steps = [
    (1,  "HTTPS request from clients"),
    (2,  "Token validation (Keycloak)"),
    (3,  "Validated & authorised request"),
    (4,  "Pseudonymised write / ID resolution"),
    (5,  "Operational data export"),
    (6,  "De-identified data"),
    (7,  "OMOP CDM load"),
    (8,  "Research query (Atlas / Analytics)"),
    (9,  "FHIR R4 interoperability"),
    (10, "Governed external sharing"),
]

legend_top = ZONES_BOTTOM - 1.5
ax.text(ZONE_LEFT + ZONE_CONTENT_W / 2, legend_top,
        "Data Flow Sequence",
        ha="center", va="center",
        fontsize=FLOW_HEAD_SZ, fontweight="bold",
        color="#1A1A2E", fontfamily=FF)

FLOW_COLS = 5
flow_item_w = ZONE_CONTENT_W / FLOW_COLS
flow_row_h = 1.50
ftop = legend_top - 1.4

for si, (sn, sl) in enumerate(flow_steps):
    row = si // FLOW_COLS
    col = si % FLOW_COLS
    sx = ZONE_LEFT + col * flow_item_w + 1.0
    sy = ftop - row * flow_row_h

    badge_clr = step_colours.get(str(sn), "#1565C0")
    ax.add_patch(plt.Circle(
        (sx, sy), BADGE_R,
        facecolor=badge_clr, edgecolor="white",
        linewidth=3.2, zorder=10))
    ax.text(sx, sy, str(sn),
            ha="center", va="center",
            fontsize=BADGE_SZ, fontweight="bold",
            color="white", zorder=11)
    ax.text(sx + 1.10, sy, sl,
            ha="left", va="center",
            fontsize=FLOW_SZ, color="#37474F", fontfamily=FF)

# ── Zone-colour legend row ────────────────────────────────────────
legend_items = config.get("legend_groups", [])
n_leg = len(legend_items)
_leg_y = ftop - 2 * flow_row_h - 1.2
leg_item_w = ZONE_CONTENT_W / n_leg

for li, item in enumerate(legend_items):
    lx = ZONE_LEFT + li * leg_item_w + 0.30
    ax.add_patch(FancyBboxPatch(
        (lx, _leg_y - 0.40), 1.10, 0.80,
        boxstyle="round,pad=0.08",
        facecolor=item["colour"], edgecolor=item["border"],
        linewidth=3.0, alpha=0.70))
    ax.text(lx + 1.40, _leg_y,
            item["label"], ha="left", va="center",
            fontsize=LEGEND_SZ, color="#37474F", fontfamily=FF)

# ═══════════════════════════════════════════════════════════════════
plt.tight_layout(pad=0.3)
fig.savefig(args.output, dpi=200, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Architecture map saved to {args.output}")
