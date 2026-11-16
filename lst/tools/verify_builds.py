#!/usr/bin/env python3
"""Rebuild all fourteen reports and record whether each build is clean.

    python3 tools/verify_builds.py

Writes ``output/build_manifest.json``.  ``tests/test_reports.py`` reads that
file, so the page counts and the four clean-build conditions are checked
against a real program run rather than against a hand-written note.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def main():
    out = []
    for n in range(1, 8):
        for lang in ("en", "fa"):
            stem = f"REPORT_{lang.upper()}"
            module = (f"lst{n}_{lang}" if n <= 6
                      else f"rw{n}_{lang}")
            cmd = [sys.executable, os.path.join(HERE, "build_report.py"),
                   module, f"exercise-{n}", stem]
            p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
            text = p.stdout.strip()
            try:
                d = json.loads(text[text.index("{"):text.rindex("}") + 1])
            except Exception:
                print(f"FAILED to parse build output for {n}/{lang}:")
                print(text[-1500:])
                print(p.stderr[-1500:])
                return 1
            clean = (d["overflow"] == [] and d["missing_figures"] == []
                     and d["missing_glyphs"] == []
                     and d["pages"] == d["pdf_pages"]
                     and 20 <= d["pdf_pages"] <= 40)
            d["clean"] = clean
            d["exercise"] = n
            d["lang"] = lang
            out.append(d)
            print(f"exercise-{n}/{lang}: pages={d['pages']} "
                  f"pdf={d['pdf_pages']} clean={clean}")
    path = os.path.join(REPO, "output", "build_manifest.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"reports": out,
                   "all_clean": all(d["clean"] for d in out),
                   "report_count": len(out)},
                  f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print("wrote", path)
    return 0 if all(d["clean"] for d in out) else 1


if __name__ == "__main__":
    sys.exit(main())
