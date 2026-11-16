"""Data layer for the readers-writers exercise (exercise 7).

No measured number is typed in a report module.  ``prepare()`` reads
``exercise-7/output/experiments.json`` -- produced by a program run -- and
returns ready-made tables.  ``numbers()`` collects every numeric token a report
may legitimately print, so the provenance test can be strict.
"""
from __future__ import annotations

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
JSON_PATH = os.path.join(REPO, "exercise-7", "output", "experiments.json")


def read() -> dict:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare() -> dict:
    raw = read()
    return {
        "raw": raw,
        "meta": raw["meta"],
        "counts": raw["counts"],
        "protocols": raw["protocols"],
        "verifications": raw["verifications"],
        "measurements": raw["measurements"],
        "sweeps": raw["sweeps"],
        "findings": raw["findings"],
        "figures": raw["figures"],
        "charts": raw["charts"],
        "random": raw["random"],
        "hand": raw["hand"],
        "divergence": raw["divergence"],
        "provenance": raw["provenance"],
        "sources": raw["sources"],
        "references": raw["references"],
    }


NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def numbers() -> set:
    """Every numeric string an exercise-7 report is allowed to print."""
    D = prepare()
    out = set()

    def walk(o):
        if isinstance(o, bool) or o is None:
            return
        if isinstance(o, (int, float)):
            out.add(str(o))
            if isinstance(o, float):
                out.add(f"{o:g}")
                out.add(f"{o:.2f}")
                out.add(f"{o:.3f}")
                out.add(f"{o:.4f}")
            return
        if isinstance(o, str):
            out.update(NUM_RE.findall(o))
            return
        if isinstance(o, dict):
            for k, v in o.items():
                out.update(NUM_RE.findall(str(k)))
                walk(v)
            return
        if isinstance(o, (list, tuple)):
            for v in o:
                walk(v)

    walk(D["raw"])
    # Structural tokens: page-rule bounds, TOC page numbers, exercise ids in
    # paths, small ordinals used in prose, and checksum prefixes.  They are
    # listed so the test can be strict about every *result-looking* number.
    out.update({str(i) for i in range(0, 41)})
    out.update({"100", "1000", "13197",
                "-1", "-2", "-3", "-4", "-5", "-6", "-7"})
    # Persian and Arabic-Indic digits are structural (state labels, exercise
    # numbers in the cover), not measurements.  Python's \d matches them too.
    out.update(list("۰۱۲۳۴۵۶۷۸۹") + list("٠١٢٣٤٥٦٧٨٩"))
    for s in D["sources"]:
        out.update(NUM_RE.findall(str(s.get("sha256", ""))[:12]))
    return out
