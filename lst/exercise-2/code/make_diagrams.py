#!/usr/bin/env python3
"""Exercise 2: render every figure described in output/experiments.json.

All plotted values are read from the data file; no number is typed here.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L


def main():
    made = L.render_figures(__file__)
    print(f"exercise 2: wrote {len(made)} figures to diagrams/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
