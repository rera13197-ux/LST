#!/usr/bin/env python3
"""Record the published *content* commit hashes of main + seven branches.

Run after ``push_lst.sh`` has published the content commits, before
``push_status.sh``.  The resulting file is staged into every branch by the
status commit, so a branch can show the hash of its own content commit (its
parent) without the circularity of putting a commit's hash inside itself.

    python3 tools/record_hashes.py
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from update_docs import BRANCH  # noqa: E402

REMOTE = os.environ.get("LST_REMOTE", "https://github.com/rera13197-ux/LST.git")
WANTED = ["main"] + [BRANCH[n] for n in range(1, 8)]
OUT = os.path.join(REPO, "output", "push_hashes.json")


def main() -> int:
    raw = subprocess.check_output(
        ["git", "ls-remote", "--heads", REMOTE], cwd=REPO, text=True)
    found = {}
    for line in raw.splitlines():
        if "\t" not in line:
            continue
        sha, ref = line.split("\t", 1)
        name = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
        if name in WANTED:
            found[name] = sha
    missing = [b for b in WANTED if b not in found]
    if missing:
        print("missing branches on remote: " + ", ".join(missing), file=sys.stderr)
        return 1
    data = {
        "generated": datetime.date.today().isoformat(),
        "remote": REMOTE,
        "kind": ("content commit; the small status commit that carries this "
                 "file is its child"),
        "branches": {b: found[b] for b in WANTED},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for b in WANTED:
        print(f"{b} {found[b]}")
    print("wrote", os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
