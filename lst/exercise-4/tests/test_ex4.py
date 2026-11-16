"""Tests for exercise 4.  Green on a flattened branch, on its own.

Run from the exercise folder:  python3 -m pytest tests -q
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "output", "experiments.json")


def data():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def pdf_page_count(path):
    with open(path, "rb") as f:
        b = f.read()
    n = (b.count(b"/Type /Page\n") + b.count(b"/Type /Page/")
         + b.count(b"/Type /Page>>"))
    if n == 0:
        m = re.search(rb"/Count\s+(\d+)", b)
        n = int(m.group(1)) if m else 0
    return n


def md_page_count(path):
    with open(path, encoding="utf-8") as f:
        return len(re.findall(r"<!-- page \d+ -->", f.read()))


def test_data_file_complete():
    d = data()
    for key in ("meta", "task_sets", "sweeps", "figures", "findings"):
        assert key in d, key
    assert d["meta"]["exercise"] == 4
    assert d["meta"]["seed"] > 0
    assert len(d["task_sets"]) > 0
    assert len(d["findings"]) > 0


def test_no_truncated_checker_runs():
    for s in data()["task_sets"]:
        assert s["checker"]["truncated"] is False, s["id"]


def test_every_feasible_verdict_has_a_valid_independent_witness():
    for s in data()["task_sets"]:
        if s["checker"]["feasible"]:
            assert s["witness"]["valid"] is True, s["id"]


def test_alignment_never_makes_things_worse():
    sets = data()["task_sets"]
    naive = sum(1 for s in sets if s["alignment"]["naive_agrees"])
    aligned = sum(1 for s in sets if s["alignment"]["aligned_agrees"])
    assert aligned >= naive


def test_every_figure_exists():
    for fig in data()["figures"]:
        assert os.path.exists(os.path.join(ROOT, "diagrams", fig["file"])), fig["file"]


@pytest.mark.parametrize("stem", ("REPORT_EN", "REPORT_FA"))
def test_report_artefacts_and_page_counts(stem):
    md = os.path.join(ROOT, stem + ".md")
    docx = os.path.join(ROOT, "docs", stem + ".docx")
    pdf = os.path.join(ROOT, "docs", stem + ".pdf")
    for p in (md, docx, pdf):
        assert os.path.exists(p), p
    pages = md_page_count(md)
    assert 20 <= pages <= 40, pages
    assert pdf_page_count(pdf) == pages


def test_experiments_reproduce_byte_for_byte():
    before = open(DATA, "rb").read()
    script = os.path.join(ROOT, "code", "run_experiments.py")
    p = subprocess.run([sys.executable, script], cwd=ROOT,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    after = open(DATA, "rb").read()
    assert after == before, "deleting and regenerating must reproduce identical numbers"


def test_code_is_self_contained():
    for name in ("lst_core.py", "lab_kit.py", "run_experiments.py",
                 "make_diagrams.py"):
        assert os.path.exists(os.path.join(ROOT, "code", name)), name


def test_random_study_relationships():
    r = data()["random"]
    assert r["truncated"] == 0
    assert r["feasible"] + r["infeasible"] == r["sets_generated"]
    assert r["witnesses_valid"] == r["feasible"]
    assert r["implicit_feasible"] <= r["implicit_sets"]
    assert r["tie_break_verdict_changes"] == 0
