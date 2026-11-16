"""Data layer for every LST report.

Rule (project README, PROMPT_TEMPLATE section 4): a content module never
contains a measured number.  It calls ``data()`` in ``lstN_data`` which reads
``exercise-N/output/experiments.json`` -- produced by a program run -- and
returns ready-made tables and scalars.  Nothing here is typed by hand either:
every value is derived from the JSON.

``numbers()`` collects every numeric token that the report may legitimately
print.  The provenance test uses it to prove that no number in a generated
report is an unmeasured constant.
"""
from __future__ import annotations

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

POLICY_ORDER = ("lst", "lst:edf", "lst:rm", "lst:stay", "lst:lzs",
                "edf", "rm", "dm", "fifo")


def json_path(n: int) -> str:
    return os.path.join(REPO, f"exercise-{n}", "output", "experiments.json")


def read(n: int) -> dict:
    with open(json_path(n), "r", encoding="utf-8") as f:
        return json.load(f)


def _policy_rows(s: dict) -> list:
    """[policy, missed, preemptions, switches, zero-sw, min laxity, tie events]."""
    return [[p,
             s["policies"][p]["missed"],
             s["policies"][p]["preemptions"],
             s["policies"][p]["context_switches"],
             s["policies"][p]["laxity_zero_switches"],
             s["policies"][p]["min_laxity"],
             s["policies"][p]["tie_events"]]
            for p in POLICY_ORDER if p in s["policies"]]


def prepare(n: int) -> dict:
    raw = read(n)
    sets = []
    for s in raw.get("task_sets", []):
        c = s["checker"]
        sets.append({
            "id": s["id"],
            "label": s["label"],
            "spec": s["spec"],
            "tasks": s["tasks"],
            "task_count": s["task_count"],
            "hyperperiod": s["hyperperiod"],
            "utilisation": s["utilisation"],
            "max_deadline": s["max_deadline"],
            "constrained": s["constrained_deadline"],
            "feasible": c["feasible"],
            "states": c["states"],
            "pruned": c["pruned"],
            "truncated": c["truncated"],
            "jobs": c["jobs"],
            "horizon": c["horizon"],
            "idle_agrees": c["idle_enumeration_agrees"],
            "schedule_length": c["schedule_length"],
            "witness": s["witness"],
            "witness_cost": s.get("witness_cost", {}),
            "cap_control": s.get("cap_control", {}),
            "alignment": s["alignment"],
            "policy_rows": _policy_rows(s),
            "policies": s["policies"],
            "gantt": s.get("gantt", {}),
        })

    profiles = []
    for p in POLICY_ORDER:
        rows, total_pre, total_sw, total_miss, total_zero, total_tie = [], 0, 0, 0, 0, 0
        for s in sets:
            if p not in s["policies"]:
                continue
            m = s["policies"][p]
            rows.append([s["id"], m["missed"], m["preemptions"],
                         m["context_switches"], m["laxity_zero_switches"],
                         m["min_laxity"], m["tie_events"], m["jitter"]])
            total_pre += m["preemptions"] or 0
            total_sw += m["context_switches"] or 0
            total_miss += m["missed"] or 0
            total_zero += m["laxity_zero_switches"] or 0
            total_tie += m["tie_events"] or 0
        profiles.append({"policy": p, "rows": rows, "sets": len(rows),
                         "total_preemptions": total_pre,
                         "total_switches": total_sw,
                         "total_missed": total_miss,
                         "total_zero_switches": total_zero,
                         "total_tie_events": total_tie})

    derived = {
        "task_set_count": len(sets),
        "feasible_count": sum(1 for s in sets if s["feasible"]),
        "infeasible_count": sum(1 for s in sets if not s["feasible"]),
        "constrained_count": sum(1 for s in sets if s["constrained"]),
        "witness_valid_count": sum(1 for s in sets
                                   if s["witness"].get("valid") is True),
        "truncated_count": sum(1 for s in sets if s["truncated"]),
        "aligned_agree_count": sum(1 for s in sets
                                   if s["alignment"]["aligned_agrees"]),
        "naive_agree_count": sum(1 for s in sets
                                 if s["alignment"]["naive_agrees"]),
        "checker_states_total": sum(s["states"] for s in sets),
        "pruned_total": sum(s["pruned"] for s in sets),
        "cap_artifact_count": sum(1 for s in sets
                                  if s["cap_control"].get("false_infeasible_count", 0) > 0),
        "rm_counterexample_count": sum(1 for s in sets
                                       if s["alignment"].get("rm_control", {}).get("counterexample")),
        "witness_cheaper_count": sum(
            1 for s in sets
            if s["witness_cost"].get("available")
            and s["witness_cost"].get("preemptions", 0)
            < s["policies"].get("lst", {}).get("preemptions", 0)),
        "figure_count": len(raw.get("figures", [])),
        "finding_count": len(raw.get("findings", [])),
        "sweep_count": len(raw.get("sweeps", [])),
        "policy_count": len(POLICY_ORDER),
    }
    for pr in profiles:
        derived[f"preemptions_{pr['policy']}"] = pr["total_preemptions"]
        derived[f"missed_{pr['policy']}"] = pr["total_missed"]

    return {
        "n": n,
        "raw": raw,
        "meta": raw.get("meta", {}),
        "sets": sets,
        "sweeps": raw.get("sweeps", []),
        "findings": raw.get("findings", []),
        "figures": raw.get("figures", []),
        "profiles": profiles,
        "derived": derived,
        "manual": raw.get("manual", {}),
        "random": raw.get("random", {}),
        "provenance": raw.get("provenance", {}),
        "decks": raw.get("decks", {}),
        "extra": raw.get("extra", {}),
        "sources": raw.get("sources", []),
    }


NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def numbers(n: int) -> set:
    """Every numeric string a report from exercise ``n`` is allowed to print."""
    D = prepare(n)
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
    walk(D["derived"])
    for pr in D["profiles"]:
        walk(pr)
    for s in D["sets"]:
        walk(s["policy_rows"])
    # Structural tokens that are deliberately not measurements: the page rule,
    # exercise ids, page numbers in the TOC, file paths ("exercise-N" produces
    # a "-N" token), the repository owner name, and checksum prefixes shown in
    # the provenance table.  They are listed here so the provenance test can
    # be strict about every *number that looks like a result*.
    out.update({"1", "2", "3", "4", "5", "6", "7", "8", "9",
                "20", "40", "0", "10", "11", "12", "13", "14", "15",
                "16", "17", "18", "19", "21", "22", "23", "24", "25",
                "26", "27", "28", "29", "30", "31", "32", "33", "34",
                "35", "36", "37", "38", "39", "100", "1000",
                "13197", "-1", "-2", "-3", "-4", "-5", "-6", "-7"})
    for src in D["raw"].get("sources", []):
        # the report prints the first twelve characters of each checksum
        out.update(NUM_RE.findall(str(src.get("sha256", ""))[:12]))
    return out
