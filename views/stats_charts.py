from __future__ import annotations
import matplotlib

# Use non-interactive backend (important for embedding)
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from typing import Dict, Tuple


def make_bar_pie_figures(stats: Dict[str, object]) -> Tuple[plt.Figure, plt.Figure]:
    """Create Matplotlib figures for bar chart and pie chart.

    stats expected keys:
      - registered_total (int)
      - today_marked (int)
      - today_unmarked (int)
      - marked_pct (float)
      - unmarked_pct (float)
    """

    registered_total = int(stats.get("registered_total", 0) or 0)
    today_marked = int(stats.get("today_marked", 0) or 0)
    today_unmarked = int(stats.get("today_unmarked", 0) or 0)

    marked_pct = float(stats.get("marked_pct", 0.0) or 0.0)
    unmarked_pct = float(stats.get("unmarked_pct", 0.0) or 0.0)

    # ---------------- Bar chart ----------------
    fig_bar = plt.Figure(figsize=(5.2, 3.6), dpi=100)
    ax = fig_bar.add_subplot(111)

    labels = ["Đã chấm công", "Chưa chấm công"]
    values = [today_marked, today_unmarked]
    colors = ["#22c55e", "#ef4444"]  # green / red

    ax.bar(labels, values, color=colors, width=0.55)
    ax.set_ylabel("Số lượng")
    ax.set_title("Chấm công hôm nay")

    # annotate values
    for i, v in enumerate(values):
        ax.text(i, v + (0.02 * max(values) if max(values) > 0 else 0.2), str(v),
                ha="center", va="bottom", fontsize=10, color="#111827")

    ax.grid(axis="y", linestyle="--", alpha=0.35)

    fig_bar.tight_layout()

    # ---------------- Pie chart ----------------
    fig_pie = plt.Figure(figsize=(5.2, 3.6), dpi=100)
    ax2 = fig_pie.add_subplot(111)

    if registered_total <= 0:
        # placeholder empty-ish pie
        ax2.set_title("Tỷ lệ chấm công hôm nay")
        ax2.text(0.5, 0.5, "Chưa có dữ liệu",
                 ha="center", va="center", fontsize=12, color="#6b7280",
                 transform=ax2.transAxes)
        ax2.axis("off")
        fig_pie.tight_layout()
        return fig_bar, fig_pie

    sizes = [today_marked, today_unmarked]
    pie_labels = [
        f"Đã chấm: {marked_pct:.2f}%",
        f"Chưa chấm: {unmarked_pct:.2f}%",
    ]
    pie_colors = ["#22c55e", "#ef4444"]

    wedges, texts = ax2.pie(
        sizes,
        colors=pie_colors,
        startangle=90,
        autopct=None,
        wedgeprops={"edgecolor": "#111827", "linewidth": 0.6},
    )

    ax2.legend(wedges, pie_labels, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    ax2.set_title("Tỷ lệ chấm công hôm nay")

    # Add center total
    ax2.text(0.0, 0.0, str(registered_total), ha="center", va="center", fontsize=12, color="#111827")

    fig_pie.tight_layout()

    return fig_bar, fig_pie

