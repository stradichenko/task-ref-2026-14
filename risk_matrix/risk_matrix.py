#!/usr/bin/env python3
"""
Generate a risk matrix (likelihood vs. impact heat-map) from a JSON config.

Usage:
    python risk_matrix.py                          # defaults: risk_config.json -> risk_matrix.png
    python risk_matrix.py -c config.json -o out.png
    python risk_matrix.py -o risk_matrix.pdf
"""

import argparse
import json
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def severity_color(likelihood: int, impact: int):
    """
    Return a colour based on the product of likelihood (0-4) and impact (0-4).
    Score range 0-16, mapped to green -> yellow -> orange -> red.
    """
    score = likelihood * impact
    if score <= 3:
        return "#4CAF50"   # green  – low
    elif score <= 6:
        return "#8BC34A"   # light green
    elif score <= 9:
        return "#FFC107"   # amber
    elif score <= 12:
        return "#FF9800"   # orange
    else:
        return "#F44336"   # red – critical


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def draw_risk_matrix(config: dict, output_path: str):
    likelihood_labels = config["likelihood_levels"]   # index 0 = lowest
    impact_labels = config["impact_levels"]            # index 0 = lowest
    risks = config["risks"]

    n_rows = len(likelihood_labels)
    n_cols = len(impact_labels)

    # --- Pre-compute the register panel height so the grid can match it ---
    # Each risk: title line + wrapped mitigation lines + spacing
    line_height = 0.40
    register_heading = 0.55   # "Risk Register" heading + separator + gap
    register_item_height = 0.0
    for risk in risks:
        register_item_height += line_height  # title line
        mit_text = "Mitigation: " + risk["mitigation"]
        n_lines = len(textwrap.fill(mit_text, width=58).split("\n"))
        register_item_height += n_lines * line_height * 0.82  # mitigation lines
        register_item_height += 0.25  # gap after each risk
    register_content_height = register_heading + register_item_height + 0.15

    # --- Layout dimensions (inches) ---
    register_width = 5.8         # left panel for risk register
    gap = 0.55                   # gap between register and grid
    grid_label_margin = 1.45     # space for Y-axis labels between gap and grid
    axis_label_bottom = 0.95     # space below grid for X-axis labels
    title_height = 0.90
    pad = 0.4

    # Scale cell_size so the grid height matches the register panel height
    cell_size = max(register_content_height / n_rows, 1.20)

    grid_left = register_width + gap + grid_label_margin
    grid_width = n_cols * cell_size
    grid_height = n_rows * cell_size

    fig_width = grid_left + grid_width + pad
    fig_height = axis_label_bottom + grid_height + title_height + pad

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, fig_width)
    ax.set_ylim(0, fig_height)
    ax.axis("off")
    # Equal aspect so circles render as circles
    ax.set_aspect("equal", adjustable="box")

    grid_bottom = axis_label_bottom
    grid_top = grid_bottom + grid_height

    # --- Title (centred over the whole figure) ---
    ax.text(
        fig_width / 2, grid_top + title_height * 0.45,
        config["title"],
        ha="center", va="center",
        fontsize=15, fontweight="bold", color=(0.15, 0.15, 0.15),
    )
    if config.get("subtitle"):
        ax.text(
            fig_width / 2, grid_top + title_height * 0.12,
            config["subtitle"],
            ha="center", va="center",
            fontsize=11, color=(0.35, 0.35, 0.35),
        )

    # --- Draw grid cells with heat-map colours ---
    for row in range(n_rows):
        for col in range(n_cols):
            x = grid_left + col * cell_size
            y = grid_bottom + row * cell_size
            bg = severity_color(row, col)
            ax.add_patch(plt.Rectangle(
                (x, y), cell_size, cell_size,
                facecolor=bg, edgecolor="white", linewidth=2, alpha=0.38,
            ))

    # --- Grid axis labels ---
    # Y-axis: Likelihood (bottom to top)
    for row in range(n_rows):
        cy = grid_bottom + row * cell_size + cell_size / 2
        ax.text(
            grid_left - 0.15, cy,
            likelihood_labels[row],
            ha="right", va="center",
            fontsize=11, color=(0.2, 0.2, 0.2),
        )
    ax.text(
        grid_left - grid_label_margin + 0.20,
        grid_bottom + grid_height / 2,
        "LIKELIHOOD",
        ha="center", va="center",
        fontsize=11, fontweight="bold", color=(0.25, 0.25, 0.25),
        rotation=90,
    )

    # X-axis: Impact (left to right)
    for col in range(n_cols):
        cx = grid_left + col * cell_size + cell_size / 2
        ax.text(
            cx, grid_bottom - 0.15,
            impact_labels[col],
            ha="center", va="top",
            fontsize=11, color=(0.2, 0.2, 0.2),
        )
    ax.text(
        grid_left + grid_width / 2, grid_bottom - 0.60,
        "IMPACT",
        ha="center", va="center",
        fontsize=11, fontweight="bold", color=(0.25, 0.25, 0.25),
    )

    # --- Place risk badges on the grid ---
    badge_radius = 0.30
    cell_occupants: dict[tuple[int, int], list] = {}
    for risk in risks:
        key = (risk["likelihood"], risk["impact"])
        cell_occupants.setdefault(key, []).append(risk)

    for (lik, imp), group in cell_occupants.items():
        cx = grid_left + imp * cell_size + cell_size / 2
        cy = grid_bottom + lik * cell_size + cell_size / 2
        n = len(group)

        for i, risk in enumerate(group):
            offset_y = (n - 1) / 2 * 0.35 - i * 0.35 if n > 1 else 0
            bg = severity_color(lik, imp)

            badge = plt.Circle(
                (cx, cy + offset_y), badge_radius,
                facecolor=bg, edgecolor="white", linewidth=2.5,
                alpha=0.92, zorder=5,
            )
            ax.add_patch(badge)
            ax.text(
                cx, cy + offset_y,
                risk["id"],
                ha="center", va="center",
                fontsize=13, fontweight="bold", color="white", zorder=6,
            )

    # --- Grid outer border ---
    ax.add_patch(plt.Rectangle(
        (grid_left, grid_bottom),
        grid_width, grid_height,
        facecolor="none", edgecolor=(0.6, 0.6, 0.6), linewidth=1.2,
    ))

    # --- Severity colour legend (below grid) ---
    severity_items = [
        ("Low",      "#4CAF50"),
        ("Moderate", "#8BC34A"),
        ("Medium",   "#FFC107"),
        ("High",     "#FF9800"),
        ("Critical", "#F44336"),
    ]
    sx = grid_left
    sy = grid_bottom - 0.80
    ax.text(
        sx, sy,
        "Severity:",
        ha="left", va="center",
        fontsize=10, fontweight="bold", color=(0.25, 0.25, 0.25),
    )
    sx_cursor = sx + 0.90
    for label, color in severity_items:
        sq = 0.22
        ax.add_patch(plt.Rectangle(
            (sx_cursor, sy - sq / 2), sq, sq,
            facecolor=color, edgecolor="white", linewidth=1, alpha=0.70,
        ))
        ax.text(
            sx_cursor + sq + 0.06, sy,
            label,
            ha="left", va="center",
            fontsize=9.5, color=(0.30, 0.30, 0.30),
        )
        sx_cursor += len(label) * 0.08 + 0.55

    # ===================================================================
    # LEFT PANEL: Risk Register
    # ===================================================================
    reg_left = 0.30
    reg_top = grid_top - 0.05
    line_height = 0.40
    legend_badge_r = 0.20

    ax.text(
        reg_left, reg_top,
        "Risk Register",
        ha="left", va="top",
        fontsize=13, fontweight="bold", color=(0.15, 0.15, 0.15),
    )

    # Thin separator line under the heading
    ax.plot(
        [reg_left, reg_left + register_width - 0.6],
        [reg_top - 0.30, reg_top - 0.30],
        color=(0.75, 0.75, 0.75), linewidth=0.8,
    )

    cursor_y = reg_top - 0.55

    for risk in risks:
        bg = severity_color(risk["likelihood"], risk["impact"])

        # Badge circle
        badge = plt.Circle(
            (reg_left + legend_badge_r, cursor_y),
            legend_badge_r,
            facecolor=bg, edgecolor="white", linewidth=1.8,
            alpha=0.92, zorder=5,
        )
        ax.add_patch(badge)
        ax.text(
            reg_left + legend_badge_r, cursor_y,
            risk["id"],
            ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=6,
        )

        # Risk label
        label_text = risk["label"].replace("\n", " ")
        ax.text(
            reg_left + legend_badge_r * 2 + 0.20, cursor_y,
            label_text,
            ha="left", va="center",
            fontsize=11, fontweight="bold", color=(0.2, 0.2, 0.2),
        )
        cursor_y -= line_height

        # Mitigation text (wrapped)
        mitigation_wrapped = textwrap.fill(
            "Mitigation: " + risk["mitigation"], width=58
        )
        for line in mitigation_wrapped.split("\n"):
            ax.text(
                reg_left + legend_badge_r * 2 + 0.20, cursor_y,
                line,
                ha="left", va="center",
                fontsize=9.5, color=(0.35, 0.35, 0.35), style="italic",
            )
            cursor_y -= line_height * 0.82
        cursor_y -= 0.25

    # Vertical separator between register and grid area
    sep_x = register_width + gap / 2
    ax.plot(
        [sep_x, sep_x], [grid_bottom, grid_top],
        color=(0.82, 0.82, 0.82), linewidth=0.8, linestyle="--",
    )

    # --- Save ---
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.20,
        facecolor="white",
    )
    plt.close(fig)
    print(f"Risk matrix saved to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a risk matrix (likelihood vs. impact heat-map)."
    )
    parser.add_argument(
        "-c", "--config",
        default=os.path.join(os.path.dirname(__file__), "risk_config.json"),
        help="Path to the JSON configuration file (default: risk_config.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(os.path.dirname(__file__), "risk_matrix.png"),
        help="Output file path (default: risk_matrix.png)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    draw_risk_matrix(config, args.output)


if __name__ == "__main__":
    main()
