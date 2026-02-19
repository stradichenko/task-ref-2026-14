#!/usr/bin/env python3
"""
Generate a colour-coded RBAC permission matrix from a JSON configuration file.

Usage:
    python rbac_matrix.py                        # defaults: rbac_config.json -> rbac_matrix.png
    python rbac_matrix.py -c config.json -o out.png
    python rbac_matrix.py -o rbac_matrix.pdf     # PDF output if the extension is .pdf
"""

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def hex_to_rgba(hex_color: str, alpha: float = 1.0):
    """Convert a hex colour string to an RGBA tuple."""
    rgba = to_rgba(hex_color)
    return (rgba[0], rgba[1], rgba[2], alpha)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def build_matrix(config: dict):
    """
    Return three parallel lists:
      - row_labels : list[str]          permission names, with blank strings
                                        inserted to act as category headers.
      - row_types  : list[str]          "category" | "permission"
      - cell_data  : list[list[str]]    access level keys per role, empty for
                                        category rows.
    """
    roles = config["roles"]
    row_labels = []
    row_types = []
    cell_data = []

    for cat in config["categories"]:
        # Category header row (spans the full width visually)
        row_labels.append(cat["name"])
        row_types.append("category")
        cell_data.append([""] * len(roles))

        for perm in cat["permissions"]:
            row_labels.append(perm["name"])
            row_types.append("permission")
            cell_data.append([perm["access"].get(r, "denied") for r in roles])

    return row_labels, row_types, cell_data


def draw_matrix(config: dict, output_path: str):
    roles = config["roles"]
    access_defs = config["access_levels"]
    row_labels, row_types, cell_data = build_matrix(config)

    n_rows = len(row_labels)
    n_cols = len(roles)

    # --- Colours ---
    level_bg = {}
    level_fg = {}
    for key, spec in access_defs.items():
        level_bg[key] = hex_to_rgba(spec["color"], alpha=0.25)
        level_fg[key] = hex_to_rgba(spec["color"], alpha=1.0)
    # Explicit "denied" cell: very light grey background, grey symbol
    level_bg["denied"] = (0.92, 0.92, 0.92, 1.0)
    level_fg["denied"] = (0.70, 0.70, 0.70, 1.0)

    cat_bg = (0.18, 0.24, 0.35, 1.0)   # dark navy for category rows
    cat_fg = (1.0, 1.0, 1.0, 1.0)

    header_bg = (0.12, 0.17, 0.27, 1.0)
    header_fg = (1.0, 1.0, 1.0, 1.0)

    perm_label_bg_even = (1.0, 1.0, 1.0, 1.0)
    perm_label_bg_odd  = (0.96, 0.97, 0.98, 1.0)

    # --- Dimensions ---
    label_col_width = 5.0       # inches for the permission label column
    role_col_width  = 1.55      # inches per role column
    row_height      = 0.38      # inches per row
    header_height   = 0.55      # inches for the role header row
    legend_height   = 0.80      # inches for the legend area
    title_height    = 0.65      # inches for the title

    fig_width  = label_col_width + n_cols * role_col_width + 0.3
    fig_height = title_height + header_height + n_rows * row_height + legend_height + 0.3

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, fig_width)
    ax.set_ylim(0, fig_height)
    ax.axis("off")

    # Coordinate helpers  (origin bottom-left, we draw top-down)
    top = fig_height - title_height
    x_label = 0.15
    x_cells_start = label_col_width

    # --- Title ---
    ax.text(
        fig_width / 2, fig_height - title_height / 2,
        config["title"],
        ha="center", va="center",
        fontsize=16, fontweight="bold", color=(0.15, 0.15, 0.15),
    )

    # --- Column headers (role names) ---
    y_header_top = top
    y_header_bot = y_header_top - header_height

    # Full header background
    ax.add_patch(plt.Rectangle(
        (x_cells_start, y_header_bot), n_cols * role_col_width, header_height,
        facecolor=header_bg, edgecolor="none",
    ))
    # Label column header
    ax.add_patch(plt.Rectangle(
        (0, y_header_bot), x_cells_start, header_height,
        facecolor=header_bg, edgecolor="none",
    ))
    ax.text(
        x_label + label_col_width * 0.02, (y_header_top + y_header_bot) / 2,
        "Permission",
        ha="left", va="center",
        fontsize=12, fontweight="bold", color=header_fg,
    )
    for ci, role in enumerate(roles):
        cx = x_cells_start + ci * role_col_width + role_col_width / 2
        cy = (y_header_top + y_header_bot) / 2
        ax.text(
            cx, cy, role,
            ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=header_fg,
            rotation=0,
        )

    # --- Rows ---
    y_cursor = y_header_bot
    perm_index = 0  # tracks alternation within a category

    for ri in range(n_rows):
        y_top = y_cursor
        y_bot = y_top - row_height
        rtype = row_types[ri]

        if rtype == "category":
            perm_index = 0
            # Full-width category band
            ax.add_patch(plt.Rectangle(
                (0, y_bot), fig_width - 0.3, row_height,
                facecolor=cat_bg, edgecolor="none",
            ))
            ax.text(
                x_label + 0.05, (y_top + y_bot) / 2,
                row_labels[ri].upper(),
                ha="left", va="center",
                fontsize=10, fontweight="bold", color=cat_fg,
            )
        else:
            # Alternating background for the label column
            bg = perm_label_bg_even if perm_index % 2 == 0 else perm_label_bg_odd
            ax.add_patch(plt.Rectangle(
                (0, y_bot), x_cells_start, row_height,
                facecolor=bg, edgecolor="none",
            ))
            ax.text(
                x_label + 0.15, (y_top + y_bot) / 2,
                row_labels[ri],
                ha="left", va="center",
                fontsize=11, color=(0.2, 0.2, 0.2),
            )

            # Data cells
            for ci in range(n_cols):
                level = cell_data[ri][ci]
                cell_x = x_cells_start + ci * role_col_width
                cell_bg = level_bg.get(level, level_bg["denied"])
                cell_fc = level_fg.get(level, level_fg["denied"])
                symbol  = access_defs.get(level, {}).get("symbol", "-")

                # Cell background
                cell_alt = bg  # match label row tint
                blended = tuple(
                    cell_bg[i] * 0.55 + cell_alt[i] * 0.45 for i in range(4)
                )
                ax.add_patch(plt.Rectangle(
                    (cell_x, y_bot), role_col_width, row_height,
                    facecolor=blended, edgecolor="white", linewidth=0.5,
                ))

                # Symbol
                ax.text(
                    cell_x + role_col_width / 2, (y_top + y_bot) / 2,
                    symbol,
                    ha="center", va="center",
                    fontsize=12.5, fontweight="bold", color=cell_fc,
                )

            perm_index += 1

        # Thin horizontal separator
        ax.plot(
            [0, fig_width - 0.3], [y_bot, y_bot],
            color=(0.82, 0.82, 0.82), linewidth=0.3,
        )

        y_cursor = y_bot

    # Vertical separators between role columns
    for ci in range(n_cols + 1):
        x = x_cells_start + ci * role_col_width
        ax.plot(
            [x, x], [y_header_bot, y_cursor],
            color=(0.82, 0.82, 0.82), linewidth=0.3,
        )

    # --- Legend ---
    legend_y = y_cursor - legend_height * 0.55
    legend_items = [
        (access_defs["granted"]["symbol"],   access_defs["granted"]["label"],   level_fg["granted"]),
        (access_defs["scoped"]["symbol"],    access_defs["scoped"]["label"],    level_fg["scoped"]),
        (access_defs["read_only"]["symbol"], access_defs["read_only"]["label"], level_fg["read_only"]),
        (access_defs["denied"]["symbol"],    access_defs["denied"]["label"],    level_fg["denied"]),
    ]
    total_legend_width = sum(len(item[1]) * 0.085 + 0.7 for item in legend_items)
    lx = (fig_width - total_legend_width) / 2

    for symbol, label, color in legend_items:
        # Draw small coloured square
        sq_size = 0.22
        ax.add_patch(plt.Rectangle(
            (lx, legend_y - sq_size / 2), sq_size, sq_size,
            facecolor=(*color[:3], 0.30), edgecolor=color, linewidth=0.8,
        ))
        ax.text(
            lx + sq_size + 0.08, legend_y,
            f"{symbol} = {label}",
            ha="left", va="center",
            fontsize=10.5, color=(0.25, 0.25, 0.25),
        )
        lx += len(label) * 0.085 + 0.7

    # --- Save ---
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.15,
        facecolor="white",
    )
    plt.close(fig)
    print(f"Permission matrix saved to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a colour-coded RBAC permission matrix."
    )
    parser.add_argument(
        "-c", "--config",
        default=os.path.join(os.path.dirname(__file__), "rbac_config.json"),
        help="Path to the JSON configuration file (default: rbac_config.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(os.path.dirname(__file__), "rbac_matrix.png"),
        help="Output file path (default: rbac_matrix.png)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    draw_matrix(config, args.output)


if __name__ == "__main__":
    main()
