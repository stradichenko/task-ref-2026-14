"""
Generate a draw.io (.drawio) architecture diagram from architecture_config.json.

Usage:
    python architecture_drawio.py [-c CONFIG] [-o OUTPUT]
"""

import argparse
import json
import math
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "architecture_config.json")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "architecture_map.drawio")

parser = argparse.ArgumentParser(description="DM1 Architecture → draw.io")
parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT)
args = parser.parse_args()

with open(args.config) as fh:
    config = json.load(fh)

# ── Helpers ───────────────────────────────────────────────────────
_cell_id = 1


def next_id():
    global _cell_id
    _cell_id += 1
    return str(_cell_id)


def add_cell(parent, **attrs):
    """Add an <mxCell> under *parent*, return the element."""
    cell = ET.SubElement(parent, "mxCell", **{k: str(v) for k, v in attrs.items()})
    return cell


def add_cell_geo(parent, x, y, w, h, style, value="", vertex="1", parent_id="1", extra=None):
    """Add an mxCell with mxGeometry child.  Returns (cell, cell_id)."""
    cid = next_id()
    attrs = {"id": cid, "value": value, "style": style,
             "vertex": vertex, "parent": parent_id}
    if extra:
        attrs.update(extra)
    cell = ET.SubElement(parent, "mxCell", **{k: str(v) for k, v in attrs.items()})
    ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                  width=str(w), height=str(h), **{"as": "geometry"})
    return cell, cid


def add_edge(parent, source, target, label="", style="", parent_id="1"):
    """Add a connection edge.  Returns (cell, cell_id)."""
    cid = next_id()
    attrs = {"id": cid, "value": label, "style": style,
             "edge": "1", "source": source, "target": target, "parent": parent_id}
    cell = ET.SubElement(parent, "mxCell", **{k: str(v) for k, v in attrs.items()})
    geo = ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
    return cell, cid


def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── Layout constants ──────────────────────────────────────────────
SIDEBAR_W = 140
GAP = 30
CARD_W = 260
CARD_H = 170
COMP_GAP = 30
ZONE_PAD = 30
ZONE_HEADER = 40
ARROW_GAP = 50

ZONE_ORDER = config.get("zone_order", [])
zones_by_id = {z["id"]: z for z in config["zones"]}

# Compute zone content widths
max_comps = max(len(zones_by_id[zid]["components"]) for zid in ZONE_ORDER)
ZONE_W = max_comps * CARD_W + (max_comps - 1) * COMP_GAP + 2 * ZONE_PAD

TOTAL_W = GAP + SIDEBAR_W + GAP + ZONE_W + GAP + SIDEBAR_W + GAP
ZONE_LEFT = GAP + SIDEBAR_W + GAP

# ── Build XML ─────────────────────────────────────────────────────
mxfile = ET.Element("mxfile", host="app.diagrams.net", type="device")
diagram = ET.SubElement(mxfile, "diagram", id="arch", name="Architecture Map")
model = ET.SubElement(diagram, "mxGraphModel",
                      dx="0", dy="0", grid="1", gridSize="10",
                      guides="1", tooltips="1", connect="1",
                      arrows="1", fold="1", page="1",
                      pageScale="1", pageWidth=str(TOTAL_W + 40),
                      pageHeight="4000", math="0", shadow="0")
root = ET.SubElement(model, "root")

# Required root cells
ET.SubElement(root, "mxCell", id="0")
ET.SubElement(root, "mxCell", id="1", parent="0")

# ── Title ─────────────────────────────────────────────────────────
title_y = 20
title_text = (f'<b style="font-size:22px">{html_escape(config["title"])}</b>'
              f'<br/><i style="font-size:13px;color:#546E7A">{html_escape(config.get("subtitle",""))}</i>')
add_cell_geo(root, 20, title_y, TOTAL_W, 60,
             "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fillColor=none;strokeColor=none;",
             value=title_text)

cursor_y = title_y + 80

# ── Store component positions for edges ───────────────────────────
comp_ids = {}   # comp_config_id → drawio cell id
comp_pos = {}   # comp_config_id → (cx, cy)  centre point

# ── Draw zones and component cards ────────────────────────────────
zone_y_centres = {}

for zid in ZONE_ORDER:
    zone = zones_by_id[zid]
    comps = zone["components"]
    n = len(comps)
    zone_h = ZONE_HEADER + CARD_H + 2 * ZONE_PAD
    colour = zone["colour"]
    border = zone["border"]

    # Zone band
    zone_style = (f"rounded=1;whiteSpace=wrap;html=1;"
                  f"fillColor={colour};strokeColor={border};strokeWidth=2;"
                  f"verticalAlign=top;align=left;spacingLeft=10;spacingTop=8;"
                  f"fontSize=15;fontStyle=1;fontColor={border};arcSize=6;")
    add_cell_geo(root, ZONE_LEFT, cursor_y, ZONE_W, zone_h, zone_style,
                 value=html_escape(zone["label"]))

    # Component cards
    total_cards_w = n * CARD_W + (n - 1) * COMP_GAP
    start_x = ZONE_LEFT + (ZONE_W - total_cards_w) / 2
    card_y = cursor_y + ZONE_HEADER + ZONE_PAD

    for ci, comp in enumerate(comps):
        cx = start_x + ci * (CARD_W + COMP_GAP)
        icon = comp.get("icon", "")
        detail_lines = comp.get("detail", "").replace("\n", "<br/>")

        card_html = (
            f'<b style="font-size:11px;color:{border};background:{border};'
            f'color:white;padding:2px 6px;border-radius:10px;">{html_escape(icon)}</b><br/>'
            f'<b style="font-size:12px">{html_escape(comp["label"])}</b><br/>'
            f'<i style="font-size:10px;color:#546E7A">{html_escape(comp.get("sublabel",""))}</i><br/>'
            f'<span style="font-size:9px;color:#78909C">{detail_lines}</span>'
        )

        card_style = (f"rounded=1;whiteSpace=wrap;html=1;"
                      f"fillColor=#FFFFFF;strokeColor={border};strokeWidth=2;"
                      f"verticalAlign=top;align=center;spacingTop=10;"
                      f"arcSize=10;shadow=1;")
        _, cid = add_cell_geo(root, cx, card_y, CARD_W, CARD_H, card_style,
                              value=card_html)
        comp_ids[comp["id"]] = cid
        comp_pos[comp["id"]] = (cx + CARD_W / 2, card_y + CARD_H / 2)

    zone_y_centres[zid] = cursor_y + zone_h / 2
    cursor_y += zone_h + ARROW_GAP

# ── Sidebars ──────────────────────────────────────────────────────
sidebars = config.get("sidebars", {})
sidebar_top = title_y + 80
sidebar_h = cursor_y - ARROW_GAP - sidebar_top

for side, sb in sidebars.items():
    sx = GAP if side == "left" else ZONE_LEFT + ZONE_W + GAP
    colour = sb["colour"]
    border = sb["border"]
    label_text = sb["label"].replace("\n", "<br/>")
    sub_text = sb.get("sublabel", "").replace("\n", "<br/>")

    sb_html = (
        f'<b style="font-size:13px;color:{border}">{label_text}</b><br/><br/>'
        f'<span style="font-size:10px;color:#546E7A">{sub_text}</span>'
    )
    sb_style = (f"rounded=1;whiteSpace=wrap;html=1;"
                f"fillColor={colour};strokeColor={border};strokeWidth=2;"
                f"verticalAlign=middle;align=center;"
                f"arcSize=4;opacity=70;")
    add_cell_geo(root, sx, sidebar_top, SIDEBAR_W, sidebar_h, sb_style,
                 value=sb_html)

    # Dashed ticks into each zone
    for zid in ZONE_ORDER:
        zy = zone_y_centres[zid]
        if side == "left":
            tick_x1 = sx + SIDEBAR_W
            tick_x2 = ZONE_LEFT
        else:
            tick_x1 = ZONE_LEFT + ZONE_W
            tick_x2 = sx
        _, tid_from = add_cell_geo(root, tick_x1, zy, 0, 0,
                                   "point;size=0;", value="")
        _, tid_to = add_cell_geo(root, tick_x2, zy, 0, 0,
                                 "point;size=0;", value="")
        add_edge(root, tid_from, tid_to, "",
                 f"dashed=1;endArrow=none;strokeColor={border};strokeWidth=1;opacity=40;")

# ── Connections ───────────────────────────────────────────────────
for conn in config["connections"]:
    fid = conn["from"]
    tid = conn["to"]
    if fid not in comp_ids or tid not in comp_ids:
        continue
    num = conn["number"]
    lbl = conn.get("label", "")

    from_zone = None
    for z in config["zones"]:
        for c in z["components"]:
            if c["id"] == fid:
                from_zone = z
                break

    border = from_zone["border"] if from_zone else "#2D3436"

    edge_label = f"{num}. {lbl}"

    # Common style base: curved routing
    _base = (f"edgeStyle=entityRelationEdgeStyle;rounded=1;html=1;"
             f"strokeColor={border};strokeWidth=2;"
             f"endArrow=blockThin;endFill=1;"
             f"curved=1;fontSize=10;fontColor=#37474F;")

    # Determine arrow direction heuristics
    fcx, fcy = comp_pos[fid]
    tcx, tcy = comp_pos[tid]
    dx = abs(tcx - fcx)
    dy = abs(tcy - fcy)

    if dy < 20:
        # Same row → horizontal
        if tcx > fcx:
            edge_style = _base + ("exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
                                  "entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
        else:
            edge_style = _base + ("exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
                                  "entryX=1;entryY=0.5;entryDx=0;entryDy=0;")
    elif tcy > fcy:
        # Downward
        edge_style = _base + ("exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                              "entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    else:
        # Upward
        edge_style = _base + ("exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                              "entryX=0.5;entryY=1;entryDx=0;entryDy=0;")

    add_edge(root, comp_ids[fid], comp_ids[tid], edge_label, edge_style)

# ── Icon Key legend ───────────────────────────────────────────────
icon_legend = config.get("icon_legend", [])
LEG_PAD = 20                             # padding each side
LEG_AVAIL = TOTAL_W - 2 * LEG_PAD       # full-width usable band

if icon_legend:
    leg_y = cursor_y + 10
    leg_cols = 4
    leg_cell_w = LEG_AVAIL / leg_cols    # spread across full width
    leg_cell_h = 30
    leg_row_h = 36
    leg_left = LEG_PAD

    # Section title
    add_cell_geo(root, LEG_PAD, leg_y, LEG_AVAIL, 30,
                 "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;"
                 "rounded=0;fillColor=none;strokeColor=none;fontSize=14;fontStyle=1;",
                 value="<b>Icon Key</b>")
    leg_y += 40

    for ii, entry in enumerate(icon_legend):
        row = ii // leg_cols
        col = ii % leg_cols
        ix = leg_left + col * leg_cell_w
        iy = leg_y + row * leg_row_h
        icon_html = (
            f'<b style="color:white;background:#546E7A;padding:2px 6px;'
            f'border-radius:10px;font-size:10px;">{html_escape(entry["icon"])}</b>'
            f' <span style="font-size:10px">{html_escape(entry["meaning"])}</span>'
        )
        add_cell_geo(root, ix, iy, leg_cell_w, leg_cell_h,
                     "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
                     "rounded=0;fillColor=none;strokeColor=none;",
                     value=icon_html)

    leg_y += math.ceil(len(icon_legend) / leg_cols) * leg_row_h + 20

# ── Zone-colour legend ────────────────────────────────────────────
legend_items = config.get("legend_groups", [])
if legend_items:
    zleg_cols = 4
    zleg_cell_w = LEG_AVAIL / zleg_cols  # spread across full width
    zleg_sw = 20
    zleg_row_h = 32
    zleg_left = LEG_PAD

    add_cell_geo(root, LEG_PAD, leg_y, LEG_AVAIL, 30,
                 "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;"
                 "rounded=0;fillColor=none;strokeColor=none;fontSize=14;fontStyle=1;",
                 value="<b>Zone Colours</b>")
    leg_y += 40

    for li, item in enumerate(legend_items):
        row = li // zleg_cols
        col = li % zleg_cols
        lx = zleg_left + col * zleg_cell_w
        ly = leg_y + row * zleg_row_h
        # Colour swatch
        add_cell_geo(root, lx, ly + 3, zleg_sw, zleg_sw,
                     f"rounded=1;whiteSpace=wrap;html=1;"
                     f"fillColor={item['colour']};strokeColor={item['border']};"
                     f"strokeWidth=2;arcSize=20;",
                     value="")
        # Label
        add_cell_geo(root, lx + zleg_sw + 6, ly, zleg_cell_w - zleg_sw - 10, zleg_row_h,
                     "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
                     "rounded=0;fillColor=none;strokeColor=none;fontSize=11;",
                     value=html_escape(item["label"]))

# ── Serialise ─────────────────────────────────────────────────────
rough = ET.tostring(mxfile, encoding="unicode")
pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding=None)
# Remove extra XML declaration
lines = pretty.split("\n")
if lines[0].startswith("<?xml"):
    lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'

with open(args.output, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"draw.io file saved to {args.output}")
