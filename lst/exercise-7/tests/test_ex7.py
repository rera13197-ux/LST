"""Standalone tests for exercise 7 -- readers-writers.

They pass from ``exercise-7/`` in the multi-exercise tree AND from the root of
the flattened branch, where code/, output/, diagrams/ and docs/ sit next to
tests/.  No sibling exercise folder is needed.
"""
from __future__ import annotations

import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "code"))

import rw_core  # noqa: E402

DATA = os.path.join(ROOT, "output", "experiments.json")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
PERSIAN_DIGITS = set("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩")


@pytest.fixture(scope="module")
def data():
    with open(DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def test_every_protocol_has_a_full_verdict(data):
    assert len(data["protocols"]) == data["counts"]["protocol_count"] > 0
    for p in data["protocols"]:
        for key in ("states", "transitions", "mutual_exclusion",
                    "deadlock_free", "starvation_free", "bounded_wait",
                    "truncated", "starving_processes"):
            assert key in p, (p["id"], key)
        assert p["states"] > 0 and p["transitions"] > 0
        assert p["truncated"] is False


def test_no_exclusivity_or_deadlock_violation(data):
    for p in data["protocols"]:
        assert p["mutual_exclusion"] is True
        assert p["mutual_exclusion_violations"] == 0
        assert p["deadlock_free"] is True
        assert p["deadlock_states"] == 0
    assert data["counts"]["truncated_checks"] == 0


def test_every_witness_is_independently_verified(data):
    C = data["counts"]
    assert C["witnesses"] == C["witnesses_valid"] > 0
    for v in data["verifications"]:
        assert v["valid"] is True
        assert v["violations"] == []
        assert v["steps"] > 0


def test_starvation_witnesses_are_fair_cycles(data):
    seen = 0
    for p in data["protocols"]:
        for w in p["witnesses"].values():
            if w is None:
                continue
            seen += 1
            assert w["grant_enabled_in_cycle"] == 0
            assert w["other_grants_in_cycle"] > 0
            assert w["cycle_length"] > 0
            assert w["prefix"] is not None
    assert seen == data["counts"]["witnesses"]


def test_checker_agrees_with_an_independent_recheck():
    """Re-run the exhaustive check live, not just from the stored JSON."""
    for proto in rw_core.protocols():
        verdict = rw_core.check(proto)
        assert verdict["mutual_exclusion"] is True
        assert verdict["deadlock_free"] is True
        if verdict["witness"] is not None:
            assert rw_core.verify_witness(proto, verdict["witness"])["valid"]


def test_mechanisms_have_distinct_starvation_verdicts(data):
    ps = {(p["mechanism"], p["config"]): p for p in data["protocols"]}
    assert ps[("readers_preference", "2r1w")]["starvation_free"] is False
    assert ps[("writers_preference", "1r2w")]["starvation_free"] is False
    assert ps[("mesa_signal", "2r1w")]["starvation_free"] is False
    assert ps[("hoare_signal", "2r1w")]["starvation_free"] is True
    assert ps[("fair_fifo", "2r1w")]["starvation_free"] is True
    assert ps[("dekker2", "1r1w")]["starvation_free"] is True
    assert ps[("peterson2", "1r1w")]["starvation_free"] is True


def test_unbounded_wait_is_marked_minus_one(data):
    for p in data["protocols"]:
        if p["starvation_free"]:
            assert all(v >= 0 for v in p["bounded_wait"].values())
        else:
            assert any(v == -1 for v in p["bounded_wait"].values())


def test_hand_trace_agrees_and_rules_diverge(data):
    h = data["hand"]
    assert h["agree"] is True
    assert h["compared_steps"] > 0
    assert all(row["agree"] for row in h["rows"])
    d = h["divergence"]
    assert d["divergent_count"] > 0
    assert d["a_allows"] is False and d["b_allows"] is True
    assert len(d["witness"]) == d["first_step"]


def test_random_study_is_a_control(data):
    r = data["random"]
    assert r["truncated"] == 0
    assert r["workloads"] > 0
    assert r["measurements"] == r["workloads"] * len(r["per_mechanism"])
    assert r["total_artefacts"] < r["total_starved"]
    for v in r["per_mechanism"].values():
        assert v["writer_starved_runs"] >= 0
        assert v["mean_writer_share"] >= 0


def test_measurement_is_reproducible():
    proto = rw_core.protocols()[0]
    a = rw_core.measure(proto, 20261120, 200, 0.55, 3, 2, 2)
    b = rw_core.measure(proto, 20261120, 200, 0.55, 3, 2, 2)
    assert a == b


def test_every_figure_exists_and_has_a_chart(data):
    assert set(data["charts"]) == {f["file"] for f in data["figures"]}
    for f in data["figures"]:
        assert os.path.exists(os.path.join(ROOT, "diagrams", f["file"])), f["file"]
        assert f["title_en"] and f["title_fa"]


def test_every_sweep_has_a_figure_and_matching_series(data):
    for sw in data["sweeps"]:
        assert sw["figure"] in data["charts"]
        for s in sw["series"]:
            assert len(s["values"]) == len(sw["x"])


def test_report_numbers_have_provenance(data):
    allowed = set()

    def walk(o):
        if isinstance(o, bool) or o is None:
            return
        if isinstance(o, (int, float)):
            allowed.add(str(o))
            if isinstance(o, float):
                allowed.update({f"{o:g}", f"{o:.2f}", f"{o:.3f}", f"{o:.4f}"})
            return
        if isinstance(o, str):
            allowed.update(NUM_RE.findall(o))
            return
        if isinstance(o, dict):
            for k, v in o.items():
                allowed.update(NUM_RE.findall(str(k)))
                walk(v)
            return
        if isinstance(o, (list, tuple)):
            for v in o:
                walk(v)

    walk(data)
    allowed.update({str(i) for i in range(0, 41)})
    allowed.update({"100", "1000", "13197",
                    "-1", "-2", "-3", "-4", "-5", "-6", "-7"})
    allowed.update(PERSIAN_DIGITS)
    for s in data["sources"]:
        allowed.update(NUM_RE.findall(str(s.get("sha256", ""))[:12]))
    for stem in ("REPORT_EN", "REPORT_FA"):
        text = open(os.path.join(ROOT, f"{stem}.md"), encoding="utf-8").read()
        unexplained = sorted({t for t in NUM_RE.findall(text)
                              if t not in allowed})
        assert not unexplained, (stem, unexplained)


def test_reports_and_deliverables_exist(data):
    for rel in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
                "docs/REPORT_EN.docx", "docs/REPORT_EN.pdf",
                "docs/REPORT_FA.docx", "docs/REPORT_FA.pdf",
                "output/experiments_summary.txt",
                "code/rw_core.py", "code/run_experiments.py",
                "code/make_diagrams.py"):
        assert os.path.exists(os.path.join(ROOT, rel)), rel


def test_references_and_provenance_are_honest(data):
    assert data["provenance"]["mismatches"] == 0
    assert len(data["sources"]) == len(data["provenance"]["files"])
    for r in data["references"]:
        assert r.get("title") and r.get("status")
        assert "DOI" not in r["title"]
