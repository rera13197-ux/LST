#!/usr/bin/env python3
"""Draw every exercise-7 figure from output/experiments.json.

No number is typed in this file: labels, values and series all come from the
data file produced by run_experiments.py.  Run from the exercise root (or from
the flattened branch root):

    python3 code/make_diagrams.py
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "output", "experiments.json")
OUT = os.path.join(ROOT, "diagrams")

INK = "#1B2A41"
ACC = "#37618E"
MUTED = "#8A94A3"
SERIES_COLORS = ["#37618E", "#C0653A", "#4E8B6B", "#8B5C9E", "#B99132",
                 "#3E8A94", "#A0575B"]


def _save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.relpath(path, ROOT))


def bar(spec, name, caption):
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    labels = spec["labels"]
    vals = spec["values"]
    colors = [ACC if v >= 0 else "#B3524A" for v in vals]
    ax.bar(range(len(vals)), vals, color=colors, width=0.62)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel(spec.get("ylabel", "value"), fontsize=9, color=INK)
    ax.set_title(spec.get("title", name), fontsize=10, color=INK)
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.tick_params(axis="y", labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    if spec.get("zero_line", True):
        ax.axhline(0, color=MUTED, linewidth=0.7)
    fig.text(0.01, -0.02, caption, fontsize=7, color=MUTED)
    _save(fig, name)


def lines(spec, name, caption):
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    for i, s in enumerate(spec["series"]):
        ax.plot(spec["x"], s["values"], marker="o", markersize=3.5,
                linewidth=1.6, color=SERIES_COLORS[i % len(SERIES_COLORS)],
                label=s["name"])
    ax.set_xlabel(spec.get("xlabel", "x"), fontsize=9, color=INK)
    ax.set_ylabel(spec.get("ylabel", "value"), fontsize=9, color=INK)
    ax.set_title(spec.get("title", name), fontsize=10, color=INK)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, frameon=False, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, -0.02, caption, fontsize=7, color=MUTED)
    _save(fig, name)


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        d = json.load(f)
    charts = d["charts"]
    figs = {f["file"]: f for f in d["figures"]}
    for name, spec in charts.items():
        cap = figs.get(name, {}).get("caption_en", "")
        if spec["kind"] == "bar":
            bar(spec, name, cap)
        elif spec["kind"] == "lines":
            lines(spec, name, cap)
        else:
            raise ValueError(f"unknown chart kind {spec['kind']}")
    missing = [f["file"] for f in d["figures"]
               if not os.path.exists(os.path.join(OUT, f["file"]))]
    if missing:
        print("missing figures:", missing, file=sys.stderr)
        return 1
    print(f"all {len(charts)} figures generated from {os.path.relpath(DATA, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
