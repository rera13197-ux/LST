"""Root-level checks for the seven-exercise LST tree.

These tests run from the multi-exercise tree root (``python3 -m pytest tests``).
Per-exercise tests live in ``exercise-N/tests/`` and are written so they also
pass on a flattened branch that contains no sibling folders.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "content"))
sys.path.insert(0, os.path.join(ROOT, "core"))

import lab_kit  # noqa: E402
import lst_data  # noqa: E402
import rw7_data  # noqa: E402

EXERCISES = list(range(1, 8))
LST_EXERCISES = list(range(1, 7))
STEMS = ("REPORT_EN", "REPORT_FA")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def read(n):
    return rw7_data.read() if n == 7 else lst_data.read(n)


def test_build_manifest_all_clean():
    path = os.path.join(ROOT, "output", "build_manifest.json")
    assert os.path.exists(path), "run tools/verify_builds.py first"
    m = json.load(open(path, encoding="utf-8"))
    assert m["report_count"] == len(EXERCISES) * len(STEMS)
    assert m["all_clean"] is True
    for d in m["reports"]:
        assert d["clean"] is True
        assert d["overflow"] == []
        assert d["missing_figures"] == []
        assert d["missing_glyphs"] == []
        assert d["pages"] == d["pdf_pages"]
        assert 20 <= d["pdf_pages"] <= 40


@pytest.mark.parametrize("n", EXERCISES)
@pytest.mark.parametrize("stem", STEMS)
def test_no_handwritten_number_in_report(n, stem):
    """Every numeric token in a report must come from the data file.

    Structural tokens (page rule, exercise ids in paths, repository name,
    checksum prefixes) are explicitly listed in ``lst_data.numbers``; anything
    that looks like a measured result and is not in the JSON fails here.
    """
    md = os.path.join(ROOT, f"exercise-{n}", f"{stem}.md")
    text = open(md, encoding="utf-8").read()
    allowed = rw7_data.numbers() if n == 7 else lst_data.numbers(n)
    unexplained = sorted({tok for tok in NUM_RE.findall(text)
                          if tok not in allowed})
    assert not unexplained, f"exercise-{n}/{stem}: {unexplained}"


@pytest.mark.parametrize("n", EXERCISES)
def test_artefacts_exist(n):
    base = os.path.join(ROOT, f"exercise-{n}")
    for rel in ("output/experiments.json",
                "code/run_experiments.py", "code/make_diagrams.py",
                "code/lst_core.py", "code/lab_kit.py",
                "REPORT_EN.md", "REPORT_FA.md",
                "docs/REPORT_EN.docx", "docs/REPORT_EN.pdf",
                "docs/REPORT_FA.docx", "docs/REPORT_FA.pdf"):
        assert os.path.exists(os.path.join(base, rel)), f"exercise-{n}: {rel}"


@pytest.mark.parametrize("n", EXERCISES)
def test_every_figure_exists(n):
    base = os.path.join(ROOT, f"exercise-{n}")
    for fig in read(n)["figures"]:
        assert os.path.exists(os.path.join(base, "diagrams", fig["file"])), fig["file"]


@pytest.mark.parametrize("n", LST_EXERCISES)
def test_checker_runs_are_not_truncated(n):
    for s in read(n)["task_sets"]:
        assert s["checker"]["truncated"] is False, (n, s["id"])


@pytest.mark.parametrize("n", LST_EXERCISES)
def test_every_feasible_verdict_has_a_valid_independent_witness(n):
    for s in read(n)["task_sets"]:
        if s["checker"]["feasible"]:
            assert s["witness"]["valid"] is True, (n, s["id"])


@pytest.mark.parametrize("n", LST_EXERCISES)
def test_alignment_never_makes_things_worse(n):
    sets = read(n)["task_sets"]
    naive = sum(1 for s in sets if s["alignment"]["naive_agrees"])
    aligned = sum(1 for s in sets if s["alignment"]["aligned_agrees"])
    assert aligned >= naive


def test_vendor_checks_pass():
    for script in ("vendor_core.py", "vendor_lab.py"):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", script),
                            "--check"], cwd=ROOT, capture_output=True, text=True)
        assert p.returncode == 0, (script, p.stdout, p.stderr)


def test_exercise_three_hand_trace_agrees():
    d = read(3)
    m = d["manual"]
    assert m["agree"] is True
    assert m["compared_steps"] > 0
    assert all(t["agree"] for t in d["extra"]["traces"])
    assert m["divergence"]["witness"], "a printed divergence witness is required"


def test_exercise_four_random_study_relationships():
    r = read(4)["random"]
    assert r["truncated"] == 0
    assert r["feasible"] + r["infeasible"] == r["sets_generated"]
    assert r["witnesses_valid"] == r["feasible"]
    assert r["implicit_feasible"] <= r["implicit_sets"]
    assert r["tie_break_verdict_changes"] == 0
    assert r["lst_misses_on_feasible"] == 0
    assert r["edf_misses_on_feasible"] == 0
    assert r["rm_misses_on_feasible"] >= 0


def test_rw_every_counterexample_is_independently_verified():
    D = rw7_data.prepare()
    C = D["counts"]
    assert C["witnesses"] == C["witnesses_valid"] > 0
    for v in D["verifications"]:
        assert v["valid"] is True and v["violations"] == []
        assert v["steps"] > 0


def test_rw_no_exclusivity_or_deadlock_violation():
    C = rw7_data.prepare()["counts"]
    assert C["mutual_exclusion_violations"] == 0
    assert C["deadlock_states"] == 0
    assert C["truncated_checks"] == 0


def test_rw_starvation_witnesses_are_fair_cycles():
    for p in rw7_data.prepare()["protocols"]:
        if p["witness"] is None:
            continue
        w = p["witness"]
        assert w["grant_enabled_in_cycle"] == 0
        assert w["other_grants_in_cycle"] > 0
        assert w["cycle_length"] > 0


def test_rw_mechanisms_have_distinct_verdicts():
    ps = {(p["mechanism"], p["config"]): p
          for p in rw7_data.prepare()["protocols"]}
    assert ps[("readers_preference", "2r1w")]["starvation_free"] is False
    assert ps[("writers_preference", "1r2w")]["starvation_free"] is False
    assert ps[("mesa_signal", "2r1w")]["starvation_free"] is False
    assert ps[("hoare_signal", "2r1w")]["starvation_free"] is True
    assert ps[("fair_fifo", "2r1w")]["starvation_free"] is True
    assert ps[("dekker2", "1r1w")]["starvation_free"] is True
    assert ps[("peterson2", "1r1w")]["starvation_free"] is True


def test_rw_hand_trace_and_divergence():
    h = rw7_data.prepare()["hand"]
    assert h["agree"] is True
    assert h["compared_steps"] > 0
    assert h["divergence"]["divergent_count"] > 0
    assert h["divergence"]["witness"]


def test_rw_random_study_is_a_control():
    r = rw7_data.prepare()["random"]
    assert r["truncated"] == 0
    assert r["total_artefacts"] < r["total_starved"]
    assert r["measurements"] == r["workloads"] * len(r["per_mechanism"])


def test_rw_numbers_have_provenance():
    allowed = rw7_data.numbers()
    for stem in STEMS:
        md = os.path.join(ROOT, "exercise-7", f"{stem}.md")
        text = open(md, encoding="utf-8").read()
        unexplained = sorted({t for t in NUM_RE.findall(text)
                              if t not in allowed})
        assert not unexplained, f"exercise-7/{stem}: {unexplained}"


def test_rw_figures_and_charts_match():
    D = rw7_data.prepare()
    assert set(D["charts"]) == {f["file"] for f in D["figures"]}
    for f in D["figures"]:
        assert os.path.exists(os.path.join(ROOT, "exercise-7",
                                           "diagrams", f["file"])), f["file"]


def test_rw_references_have_explicit_status():
    for r in rw7_data.prepare()["references"]:
        assert r.get("title") and r.get("status")
        assert "DOI" not in r["title"]


def test_inherited_numbers_match_their_sources():
    """Exercises 5 and 6 re-read the sources; this test re-reads them again."""
    for n, needed in ((5, (1, 2, 3, 4)), (6, (1, 2, 3, 4, 5))):
        d = read(n)
        prov = d["provenance"]
        assert prov["mismatches"] == 0
        sources = {int(re.search(r"exercise-(\d)", s["path"]).group(1)): s
                   for s in d["sources"]}
        assert set(sources) == set(needed)
        for i, s in sources.items():
            live = lab_kit.read_exercise(i, ROOT)
            assert live["sha256"] == s["sha256"], (n, i)
        assert len(prov["inherited"]) > 0


def test_references_have_explicit_status():
    for r in read(6)["references"]:
        assert r.get("title") and r.get("status")
        assert "DOI" not in r["title"]


def test_decks_have_speaker_notes_on_every_slide():
    pptx = pytest.importorskip("pptx")
    for n in (5, 6):
        d = read(n)
        decks = d["decks"]
        assert decks["notes_on_every_slide"] is True
        files = [f for f in decks["files"] if f.lower().endswith(".pptx")]
        assert len(files) == 2
        for name in files:
            path = os.path.join(ROOT, f"exercise-{n}", "docs", name)
            assert os.path.exists(path), (n, name)
            prs = pptx.Presentation(path)
            assert len(prs.slides) == decks["slide_count"]
            for slide in prs.slides:
                notes = slide.notes_slide.notes_text_frame.text
                assert notes and notes.strip(), (n, name)
        for name in decks["files"]:
            if name.lower().endswith(".md"):
                assert os.path.exists(os.path.join(ROOT, f"exercise-{n}", "docs", name))
