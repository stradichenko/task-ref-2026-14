#!/usr/bin/env python3
"""
Generate a Gantt-style chart from gantt_config.json.

Usage:
    python gantt_chart.py                        # renders to screen
    python gantt_chart.py -o gantt.png           # saves to file
    python gantt_chart.py -o gantt.pdf           # saves as PDF
    python gantt_chart.py --config other.json    # use a different config
"""

import argparse
import json
import pathlib
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # headless backend; avoids Tk dependency
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def build_chart(cfg: dict, output: str | None = None) -> None:
    workstreams = cfg["workstreams"]
    milestones = cfg.get("milestones", [])
    title = cfg.get("title", "Gantt Chart")

    # Collect all tasks (bottom-to-top so first workstream appears at the top)
    rows: list[dict] = []
    for ws in reversed(workstreams):
        for task in reversed(ws["tasks"]):
            rows.append({
                "label": task["label"],
                "start": parse_date(task["start"]),
                "end": parse_date(task["end"]),
                "color": ws["color"],
                "workstream": ws["name"],
            })

    n = len(rows)
    fig_height = max(6, n * 0.35 + 2)
    fig, ax = plt.subplots(figsize=(22, fig_height))

    y_positions = range(n)
    bar_height = 0.7

    for i, row in enumerate(rows):
        duration = (row["end"] - row["start"]).days
        ax.barh(
            i,
            duration,
            left=row["start"],
            height=bar_height,
            color=row["color"],
            edgecolor="white",
            linewidth=0.5,
            alpha=0.85,
        )

        # Decide whether to place the label inside the bar or to the right.
        # Render a temporary text to measure its width in data coordinates.
        mid = row["start"] + timedelta(days=duration / 2)
        tmp = ax.text(mid, i, row["label"], fontsize=9, visible=False)
        fig.canvas.draw()  # force renderer so get_window_extent works
        bbox = tmp.get_window_extent(renderer=fig.canvas.get_renderer())
        inv = ax.transData.inverted()
        text_width_days = (inv.transform((bbox.x1, 0))[0]
                           - inv.transform((bbox.x0, 0))[0]).item()
        tmp.remove()

        # Wrap to two lines if the label is too long for the bar
        label = row["label"]
        if text_width_days > duration * 0.95:
            words = label.split()
            half = len(words) // 2
            label = " ".join(words[:half]) + "\n" + " ".join(words[half:])

        # Re-measure after wrapping
        tmp2 = ax.text(mid, i, label, fontsize=9, visible=False)
        fig.canvas.draw()
        bbox2 = tmp2.get_window_extent(renderer=fig.canvas.get_renderer())
        text_width_days2 = (inv.transform((bbox2.x1, 0))[0]
                            - inv.transform((bbox2.x0, 0))[0]).item()
        tmp2.remove()

        fits_inside = text_width_days2 <= duration * 0.95

        if fits_inside:
            ax.text(
                mid, i, label,
                ha="center", va="center",
                fontsize=9, color="white", fontweight="medium",
                clip_on=True,
            )
        else:
            # Place to the right of the bar
            ax.text(
                row["end"] + timedelta(days=0.5), i, row["label"],
                ha="left", va="center",
                fontsize=9, color=row["color"], fontweight="medium",
                clip_on=False,
            )

    # Y-axis labels
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels([r["label"] for r in rows], fontsize=10)

    # X-axis formatting
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_minor_locator(mdates.DayLocator())
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)

    # Limits
    global_start = parse_date(cfg.get("start_date", "2026-03-01")) - timedelta(days=3)
    global_end = max(r["end"] for r in rows) + timedelta(days=5)
    ax.set_xlim(global_start, global_end)
    ax.set_ylim(-0.5, n + 2.5)

    # Gridlines -- draw manually so they stop at the top bar and don't
    # cross into the milestone area.
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)  # disable built-in grid
    grid_top = n - 1 + bar_height / 2 + 0.1  # just above the highest bar

    # Force a draw so the locator can compute tick positions from the axis limits
    fig.canvas.draw()
    for tick_pos in ax.xaxis.get_majorticklocs():
        ax.plot(
            [tick_pos, tick_pos], [-0.5, grid_top],
            color="grey", linewidth=0.3, alpha=0.5, zorder=0,
            transform=ax.transData,
        )

    # Milestones as diamond markers (drawn above grid area)
    ms_marker_y = n + 0.4
    ms_label_y = n + 1.0
    ms_rects = []  # collect bounding info for legend placement
    for idx, ms in enumerate(milestones):
        ms_date = parse_date(ms["date"])
        ax.axvline(
            ms_date, ymin=0, ymax=(grid_top + 0.5) / (n + 2.5),
            color="#555555", linewidth=0.8, linestyle="--", alpha=0.5,
        )
        ax.plot(
            ms_date, ms_marker_y,
            marker="D", color="#e63946", markersize=8,
            zorder=5, clip_on=False,
        )
        txt = ax.text(
            ms_date, ms_label_y, ms["label"],
            ha="center", va="bottom",
            fontsize=9, color="#e63946", fontweight="bold",
            rotation=30, clip_on=False,
        )
        ms_rects.append((ms_date, txt))

    # Legend (one entry per workstream) -- find empty space dynamically
    seen = {}
    legend_handles = []
    for ws in workstreams:
        if ws["name"] not in seen:
            seen[ws["name"]] = True
            legend_handles.append(
                mpatches.Patch(color=ws["color"], label=ws["name"], alpha=0.85)
            )

    # Scan a grid of candidate positions and pick the one with least bar overlap
    from matplotlib.transforms import Bbox

    renderer = fig.canvas.get_renderer()
    best_loc = "lower right"
    best_overlap = float("inf")

    candidates = [
        "upper right", "upper left", "lower left", "lower right",
        "center right", "center left", "lower center",
    ]

    for loc_name in candidates:
        test_legend = ax.legend(
            handles=legend_handles, loc=loc_name,
            fontsize=10, framealpha=0.9,
        )
        fig.canvas.draw()
        leg_bbox = test_legend.get_window_extent(renderer)
        leg_data = ax.transData.inverted().transform(leg_bbox)
        lx0 = leg_data[0][0]  # in matplotlib date-float space
        lx1 = leg_data[1][0]
        ly0 = leg_data[0][1]
        ly1 = leg_data[1][1]

        overlap = 0.0
        # Heavy penalty if legend extends above the bar grid into milestone area
        if ly1 > grid_top:
            overlap += (ly1 - grid_top) * (lx1 - lx0) * 10
        # Check overlap with bars
        for j, row in enumerate(rows):
            bar_y0 = j - bar_height / 2
            bar_y1 = j + bar_height / 2
            bx0 = mdates.date2num(row["start"])
            bx1 = mdates.date2num(row["end"])
            if lx0 < bx1 and lx1 > bx0 and ly0 < bar_y1 and ly1 > bar_y0:
                ox = max(0, min(lx1, bx1) - max(lx0, bx0))
                oy = max(0, min(ly1, bar_y1) - max(ly0, bar_y0))
                overlap += ox * oy
        # Check overlap with milestone markers and labels
        for ms_date, ms_txt in ms_rects:
            ms_num = mdates.date2num(ms_date)
            # Diamond marker approximate footprint
            mk_half_x = 1.0  # ~1 day in data space
            mk_half_y = 0.4
            mk_x0 = ms_num - mk_half_x
            mk_x1 = ms_num + mk_half_x
            mk_y0 = ms_marker_y - mk_half_y
            mk_y1 = ms_marker_y + mk_half_y
            if lx0 < mk_x1 and lx1 > mk_x0 and ly0 < mk_y1 and ly1 > mk_y0:
                ox = max(0, min(lx1, mk_x1) - max(lx0, mk_x0))
                oy = max(0, min(ly1, mk_y1) - max(ly0, mk_y0))
                overlap += ox * oy * 2  # weight milestones heavier
            # Label bounding box
            try:
                tb = ms_txt.get_window_extent(renderer)
                td = ax.transData.inverted().transform(tb)
                tx0, ty0 = td[0]
                tx1, ty1 = td[1]
                if lx0 < tx1 and lx1 > tx0 and ly0 < ty1 and ly1 > ty0:
                    ox = max(0, min(lx1, tx1) - max(lx0, tx0))
                    oy = max(0, min(ly1, ty1) - max(ly0, ty0))
                    overlap += ox * oy * 2
            except Exception:
                pass

        if overlap < best_overlap:
            best_overlap = overlap
            best_loc = loc_name

        test_legend.remove()

    ax.legend(
        handles=legend_handles,
        loc=best_loc,
        fontsize=10,
        framealpha=0.9,
    )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=60)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Clip the left spine so it only spans the bar region, not the milestone area
    ax.spines["left"].set_bounds(-0.5, grid_top)

    plt.tight_layout()

    if output:
        fig.savefig(output, dpi=200, bbox_inches="tight")
        print(f"Chart saved to {output}")
    else:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Gantt chart from JSON config.")
    parser.add_argument(
        "--config",
        default=str(pathlib.Path(__file__).parent / "gantt_config.json"),
        help="Path to the JSON config file (default: gantt_config.json next to this script)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (e.g. gantt.png, gantt.pdf). If omitted, shows on screen.",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    build_chart(cfg, output=args.output)


if __name__ == "__main__":
    main()
