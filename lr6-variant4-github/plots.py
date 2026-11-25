"""Графики времени серии и одной вставки по results/timings.csv."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LINES = {"linked": ("Двусвязный список", "#275885", "o"),
         "deque": ("Кольцевой дек", "#128575", "s"),
         "list": ("Встроенный list", "#a2542b", "^")}


def draw(root):
    with (root / "results" / "timings.csv").open(encoding="utf-8") as f:
        data = list(csv.DictReader(f))
    folder = root / "figures"
    folder.mkdir(exist_ok=True)
    charts = [("batch_ms", "Время серии, мс", "batch_time.png"),
              ("ns_per_op", "Среднее время вставки, нс", "operation_time.png")]
    for field, units, filename in charts:
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.0))
        modes = [("front", "В начало"), ("back", "В конец"), ("alternating", "Поочерёдно")]
        for ax, (mode, title) in zip(axes, modes):
            for name, (label, color, marker) in LINES.items():
                rows = [r for r in data if r["structure"] == name and r["operation"] == mode]
                ax.plot([int(r["n"]) for r in rows], [float(r[field]) for r in rows],
                        marker=marker, color=color, label=label, linewidth=2, markersize=5)
            ax.set(title=title, xlabel="Количество вставок n", xticks=[2000, 4000, 8000])
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", color="#dce3e8", linewidth=.7)
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(labelsize=9)
        axes[0].set_ylabel(units)
        fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center",
                   ncol=3, frameon=False, fontsize=9)
        fig.tight_layout(rect=(0, .09, 1, 1))
        fig.savefig(folder / filename, dpi=175)
        plt.close(fig)


if __name__ == "__main__":
    draw(Path(__file__).resolve().parent)
