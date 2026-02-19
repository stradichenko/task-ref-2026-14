#!/usr/bin/env python3
"""
Generate a colour-coded RACI matrix from a JSON configuration file.

Usage:
    python raci_matrix.py                          # defaults: raci_config.json -> raci_matrix.png
    python raci_matrix.py -c config.json -o out.png
"""

import argparse
import json
import os
import textwrap

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
    rgba = to_rgba(hex_color)
    return (rgba[0], rgba[1], rgba[2], alpha)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def draw_raci(config: dict, output_path: str):
    legend_defs = config["legend"]   # R, A, C, I definitions
    roles = config["roles"]
    phases = config["phases"]

    n_cols = len(roles)

    # Flatten rows: phase headers + activity rows
    row_labels = []
    row_types = []     # "phase" | "activity"
    cell_data = []

    for phase in phases:
        row_labels.append(phase["name"])
        row_types.append("phase")
        cell_data.append([""] * n_cols)

        for act in phase["activities"]:
            row_labels.append(act["name"])
            row_types.append("activity")
            cell_data.append(act["raci"])

    n_rows = len(row_labels)

    # --- Colours for each RACI letter ---
    letter_colors = {}
    for key, spec in legend_defs.items():
        letter_colors[key] = hex_to_rgba(spec["color"])

    # --- Layout ---
    label_col_width = 5.2
    role_col_width  = 1.55
    row_height      = 0.44
    header_height   = 0.70
    title_height    = 0.80
    legend_height   = 0.85
    pad             = 0.35

    fig_width  = label_col_width + n_cols * role_col_width + pad
    fig_height = title_height + header_height + n_rows * row_height + legend_height + pad

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, fig_width)
    ax.set_ylim(0, fig_height)
    ax.axis("off")

    top = fig_height - title_height
    x_label = 0.15
    x_cells_start = label_col_width

    # --- Palette ---
    phase_bg   = (0.18, 0.24, 0.35, 1.0)
    phase_fg   = (1.0, 1.0, 1.0, 1.0)
    header_bg  = (0.12, 0.17, 0.27, 1.0)
    header_fg  = (1.0, 1.0, 1.0, 1.0)
    row_bg_even = (1.0, 1.0, 1.0, 1.0)
    row_bg_odd  = (0.96, 0.97, 0.98, 1.0)

    # --- Title ---
    ax.text(
        fig_width / 2, fig_height - title_height * 0.30,
        config["title"],
        ha="center", va="center",
        fontsize=16, fontweight="bold", color=(0.15, 0.15, 0.15),
    )
    if config.get("subtitle"):
        ax.text(
            fig_width / 2, fig_height - title_height * 0.72,
            config["subtitle"],
            ha="center", va="center",
            fontsize=12, color=(0.40, 0.40, 0.40),
        )

    # --- Column headers ---
    y_header_top = top
    y_header_bot = y_header_top - header_height

    ax.add_patch(plt.Rectangle(
        (0, y_header_bot), fig_width - pad, header_height,
        facecolor=header_bg, edgecolor="none",
    ))
    ax.text(
        x_label + 0.05, (y_header_top + y_header_bot) / 2,
        "Activity",
        ha="left", va="center",
        fontsize=13, fontweight="bold", color=header_fg,
    )
    for ci, role in enumerate(roles):
        cx = x_cells_start + ci * role_col_width + role_col_width / 2
        cy = (y_header_top + y_header_bot) / 2
        ax.text(
            cx, cy, role,
            ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=header_fg,
        )

    # --- Rows ---
    y_cursor = y_header_bot
    act_index = 0

    for ri in range(n_rows):
        y_top = y_cursor
        y_bot = y_top - row_height
        rtype = row_types[ri]

        if rtype == "phase":
            act_index = 0
            ax.add_patch(plt.Rectangle(
                (0, y_bot), fig_width - pad, row_height,
                facecolor=phase_bg, edgecolor="none",
            ))
            ax.text(
                x_label + 0.05, (y_top + y_bot) / 2,
                row_labels[ri],
                ha="left", va="center",
                fontsize=12, fontweight="bold", color=phase_fg,
            )
        else:
            bg = row_bg_even if act_index % 2 == 0 else row_bg_odd
            # Label column background
            ax.add_patch(plt.Rectangle(
                (0, y_bot), x_cells_start, row_height,
                facecolor=bg, edgecolor="none",
            ))
            ax.text(
                x_label + 0.15, (y_top + y_bot) / 2,
                row_labels[ri],
                ha="left", va="center",
                fontsize=12, color=(0.2, 0.2, 0.2),
            )

            # Data cells
            for ci in range(n_cols):
                cell_x = x_cells_start + ci * role_col_width
                cell_val = cell_data[ri][ci].strip()

                # Cell background with alternating tint
                ax.add_patch(plt.Rectangle(
                    (cell_x, y_bot), role_col_width, row_height,
                    facecolor=bg, edgecolor="white", linewidth=0.5,
                ))

                if not cell_val:
                    # Empty cell: draw a subtle dash
                    ax.text(
                        cell_x + role_col_width / 2, (y_top + y_bot) / 2,
                        "-",
                        ha="center", va="center",
                        fontsize=12, color=(0.80, 0.80, 0.80),
                    )
                else:
                    # May contain multiple letters, e.g. "R,A"
                    letters = [l.strip() for l in cell_val.split(",")]
                    n_letters = len(letters)
                    total_width = n_letters * 0.36 + (n_letters - 1) * 0.08
                    start_x = cell_x + role_col_width / 2 - total_width / 2 + 0.18
                    cy = (y_top + y_bot) / 2

                    for li, letter in enumerate(letters):
                        lx = start_x + li * 0.44
                        color = letter_colors.get(letter, (0.5, 0.5, 0.5, 1.0))

                        # Draw small rounded-ish badge
                        badge_w = 0.34
                        badge_h = 0.28
                        ax.add_patch(mpatches.FancyBboxPatch(
                            (lx - badge_w / 2, cy - badge_h / 2),
                            badge_w, badge_h,
                            boxstyle="round,pad=0.04",
                            facecolor=(*color[:3], 0.18),
                            edgecolor=(*color[:3], 0.60),
                            linewidth=1.0,
                        ))
                        ax.text(
                            lx, cy,
                            letter,
                            ha="center", va="center",
                            fontsize=13, fontweight="bold",
                            color=color,
                        )

            act_index += 1

        # Row separator
        ax.plot(
            [0, fig_width - pad], [y_bot, y_bot],
            color=(0.82, 0.82, 0.82), linewidth=0.3,
        )
        y_cursor = y_bot

    # Vertical separators
    for ci in range(n_cols + 1):
        x = x_cells_start + ci * role_col_width
        ax.plot(
            [x, x], [y_header_bot, y_cursor],
            color=(0.82, 0.82, 0.82), linewidth=0.3,
        )

    # --- Legend ---
    legend_y = y_cursor - legend_height * 0.50
    items = list(legend_defs.items())
    total_legend_w = sum(len(spec["label"]) * 0.09 + 1.1 for _, spec in items)
    lx = (fig_width - total_legend_w) / 2

    for key, spec in items:
        color = letter_colors[key]
        badge_w = 0.32
        badge_h = 0.26
        ax.add_patch(mpatches.FancyBboxPatch(
            (lx, legend_y - badge_h / 2),
            badge_w, badge_h,
            boxstyle="round,pad=0.04",
            facecolor=(*color[:3], 0.22),
            edgecolor=(*color[:3], 0.70),
            linewidth=1.0,
        ))
        ax.text(
            lx + badge_w / 2, legend_y,
            key,
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=color,
        )
        ax.text(
            lx + badge_w + 0.10, legend_y,
            f"= {spec['label']}",
            ha="left", va="center",
            fontsize=11, color=(0.25, 0.25, 0.25),
        )
        lx += len(spec["label"]) * 0.09 + 1.1

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
    print(f"RACI matrix saved to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a colour-coded RACI matrix."
    )
    parser.add_argument(
        "-c", "--config",
        default=os.path.join(os.path.dirname(__file__), "raci_config.json"),
        help="Path to the JSON configuration file (default: raci_config.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(os.path.dirname(__file__), "raci_matrix.png"),
        help="Output file path (default: raci_matrix.png)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    draw_raci(config, args.output)


if __name__ == "__main__":
    main()
