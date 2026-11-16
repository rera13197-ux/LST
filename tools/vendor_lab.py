#!/usr/bin/env python3
"""Vendor ``tools/lab_kit.py`` into every ``exercise-N/code/`` folder.

The exercise branches are flat and must be self-contained: on a branch,
``code/`` holds ``lst_core.py`` (vendored by ``vendor_core.py``) and
``lab_kit.py`` (vendored here), and ``run_experiments.py`` imports both from
its own directory.  ``--check`` fails if any copy has drifted.

    python3 tools/vendor_lab.py
    python3 tools/vendor_lab.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(HERE, "lab_kit.py")
DECKS = os.path.join(HERE, "make_decks.py")
EXERCISES = [f"exercise-{n}" for n in range(1, 8)]
DECK_EXERCISES = [f"exercise-{n}" for n in (5, 6)]


def digest(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    want = digest(SRC)
    want_decks = digest(DECKS)
    targets = [os.path.join(REPO, e, "code", "lab_kit.py") for e in EXERCISES]
    deck_targets = [os.path.join(REPO, e, "code", "make_decks.py")
                    for e in DECK_EXERCISES]
    if args.check:
        bad = [t for t in targets
               if not os.path.exists(t) or digest(t) != want]
        bad += [t for t in deck_targets
                if not os.path.exists(t) or digest(t) != want_decks]
        for t in bad:
            print(f"  out of date: {os.path.relpath(t, REPO)}")
        if bad:
            print("run tools/vendor_lab.py")
            return 1
        print(f"all {len(targets)} lab_kit copies and {len(deck_targets)} "
              f"make_decks copies match the canonical files")
        return 0
    for t in targets:
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copyfile(SRC, t)
    for t in deck_targets:
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copyfile(DECKS, t)
    print(f"vendored lab_kit -> {len(targets)} folders; "
          f"make_decks -> {len(deck_targets)} folders")
    return 0


if __name__ == "__main__":
    sys.exit(main())
