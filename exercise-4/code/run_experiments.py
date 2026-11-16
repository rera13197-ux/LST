#!/usr/bin/env python3
"""Exercise 4 — optimality against an exhaustive search, and overload.

Two things are measured separately and never mixed:

* [E] a fixed-seed large study of constrained-deadline task sets, each decided
  by ``exhaustive_feasible`` with an independently re-checked witness;
* [M] the aligned simulator runs of LST, EDF and RM on the same job sets.

A control batch with implicit deadlines shows why that regime cannot test an
optimality claim.  Truncated checker runs are counted and never used as a
finding.

    python3 code/run_experiments.py   ->   output/experiments.json
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L
from lst_core import (Task, exhaustive_feasible, hyperperiod, simulate,
                      utilisation)

SPECS = [
    ("R1", "feasible constrained", [["T1", 6, 2, 4], ["T2", 8, 2, 5], ["T3", 12, 3, 7]]),
    ("R2", "infeasible constrained", [["T1", 5, 2, 3], ["T2", 6, 2, 3]]),
    ("R3", "implicit control", [["T1", 6, 2], ["T2", 8, 2], ["T3", 12, 3]]),
    ("R4", "overload", [["T1", 4, 3, 4], ["T2", 6, 3, 5]]),
    ("R5", "heavy infeasible", [["T1", 5, 2, 3], ["T2", 10, 3, 6], ["T3", 10, 2, 7]]),
    ("R6", "phased", [["T1", 4, 2, 3, 0], ["T2", 4, 3, 4, 3]]),
    ("R7", "harmonic", [["T1", 4, 1, 3], ["T2", 8, 2, 6], ["T3", 16, 4, 12]]),
    ("R8", "tight three tasks", [["T1", 5, 2, 3], ["T2", 5, 2, 3], ["T3", 10, 3, 6]]),
]


def implicit_batch(rnd, count):
    """A control batch with D = T and U <= 1, built by code, not by hand."""
    out = []
    periods = [3, 4, 5, 6, 8, 10, 12]
    tries = 0
    while len(out) < count and tries < count * 200:
        tries += 1
        n = rnd.choice([2, 3])
        rows, hp = [], 1
        for i in range(n):
            p = rnd.choice(periods)
            c = rnd.randint(1, max(1, min(p - 1, 4)))
            rows.append([f"T{i + 1}", p, c, p])
            hp = hp * p // math.gcd(hp, p)
        if hp > 36:
            continue
        tasks = L.mk(rows)
        if utilisation(tasks) > 1.0 + 1e-9:
            continue
        out.append(tasks)
    return out


def random_study():
    seed = L.SEED + 4
    rnd = L.rng(seed)
    sets = L.random_sets(rnd, 240, n_tasks=(2, 3), max_hp=36,
                         u_cap=1.0, constrained=True)
    ctrl = implicit_batch(L.rng(seed + 1), 120)
    feasible = infeasible = truncated = 0
    lst_miss = edf_miss = rm_miss = 0
    tie_changes = 0
    cap_artifacts = 0
    witnesses_valid = 0
    bins = [0] * 5
    for tasks in sets:
        hp = hyperperiod(tasks)
        maxd = max(t.rel_deadline for t in tasks)
        ok, sched, stats = exhaustive_feasible(tasks, horizon=hp)
        if stats["truncated"]:
            truncated += 1
            continue
        v = L.verify_witness(tasks, sched, hp)
        if v.get("valid"):
            witnesses_valid += 1
        u = utilisation(tasks)
        bins[min(4, int(u * 5))] += 1
        if ok:
            feasible += 1
        else:
            infeasible += 1
        aligned = {}
        for p in ("lst", "edf", "rm"):
            r = simulate(tasks, p, horizon=hp + maxd, release_window=hp)
            aligned[p] = r.missed
        if ok:
            lst_miss += aligned["lst"]
            edf_miss += aligned["edf"]
            rm_miss += aligned["rm"]
        verdicts = set()
        for p in L.LST_POLICIES:
            r = simulate(tasks, p, horizon=hp + maxd, release_window=hp)
            verdicts.add(r.missed == 0)
        if len(verdicts) > 1:
            tie_changes += 1
        cap_ok, _s, cap_st = exhaustive_feasible(tasks, horizon=hp, limit=8)
        if cap_st["truncated"] and not cap_ok and ok:
            cap_artifacts += 1
    implicit_feasible = 0
    for tasks in ctrl:
        ok, _s, _st = exhaustive_feasible(tasks, horizon=hyperperiod(tasks))
        if ok:
            implicit_feasible += 1
    table = [
        ["generated sets", len(sets), "[M]"],
        ["feasible", feasible, "[E]"],
        ["infeasible", infeasible, "[E]"],
        ["truncated runs", truncated, "[E]"],
        ["valid witnesses", witnesses_valid, "[E]"],
        ["LST misses on feasible sets", lst_miss, "[M]"],
        ["EDF misses on feasible sets", edf_miss, "[M]"],
        ["RM misses on feasible sets", rm_miss, "[M]"],
        ["tie-break verdict changes", tie_changes, "[M]"],
        ["cap artefacts", cap_artifacts, "[D]"],
        ["implicit control sets", len(ctrl), "[E]"],
        ["implicit control feasible", implicit_feasible, "[E]"],
    ]
    return {
        "seed": seed,
        "sets_generated": len(sets),
        "feasible": feasible, "infeasible": infeasible,
        "truncated": truncated, "witnesses_valid": witnesses_valid,
        "lst_misses_on_feasible": lst_miss,
        "edf_misses_on_feasible": edf_miss,
        "rm_misses_on_feasible": rm_miss,
        "tie_break_verdict_changes": tie_changes,
        "cap_artifacts": cap_artifacts,
        "implicit_sets": len(ctrl), "implicit_feasible": implicit_feasible,
        "utilisation_bins": ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"],
        "utilisation_counts": bins,
        "table": table,
    }


def sweeps_fn(sets):
    base = lambda d: L.mk([["T1", 6, 2, d], ["T2", 8, 2], ["T3", 12, 3]])
    return [
        L.sweep_parameter("deadline-misses", "deadline of T1 (time units)",
                          list(range(2, 7)), base, "missed",
                          figure="fig_ex4_deadline_misses.png",
                          source="sweeps[0]"),
        L.sweep_parameter("deadline-first-miss", "deadline of T1 (time units)",
                          list(range(2, 7)), base, "preemptions",
                          figure="fig_ex4_deadline_pre.png",
                          source="sweeps[1]"),
        L.sweep_alignment(sets, figure="fig_ex4_alignment.png",
                          source="sweeps[2]"),
    ]


STUDY = None


def extra_figures(sets, sweeps):
    study = STUDY
    return [
        L.fig_bar("fig_ex4_study.png", "Fixed-seed random study counts",
                  [r[0] for r in study["table"]],
                  [r[1] for r in study["table"]],
                  "random.table", ylabel="count"),
        L.fig_bar("fig_ex4_bins.png", "Task sets per utilisation band",
                  study["utilisation_bins"], study["utilisation_counts"],
                  "random.utilisation_counts", ylabel="task sets",
                  xlabel="utilisation band"),
    ]


def extra_findings(sets):
    study = STUDY
    r4 = sets[3]["policies"]
    return [
        L.finding(
            "F5", "E",
            "Optimality survives an exhaustive search on constrained deadlines",
            "بهینگی در برابر جستجوی جامع روی ضربالاجلهای مقید دوام میآورد",
            (f"[E] The fixed-seed study generated {study['sets_generated']} "
             f"constrained-deadline sets: {study['feasible']} feasible, "
             f"{study['infeasible']} infeasible, {study['truncated']} truncated, "
             f"{study['witnesses_valid']} independently valid witnesses. "
             f"[M] On the feasible sets LST and EDF miss "
             f"{study['lst_misses_on_feasible']} and "
             f"{study['edf_misses_on_feasible']} deadlines in the aligned run, "
             f"while RM misses {study['rm_misses_on_feasible']}. Changing the "
             f"LST tie-break changed the verdict on "
             f"{study['tie_break_verdict_changes']} sets. The control batch of "
             f"{study['implicit_sets']} implicit-deadline sets produced "
             f"{study['implicit_feasible']} feasible verdicts, which is why "
             f"that regime cannot refute the claim."),
            (f"[E] مطالعهٔ بذرثابت {study['sets_generated']} مجموعهٔ "
             f"ضربالاجلمقید ساخت: {study['feasible']} شدنی، "
             f"{study['infeasible']} نشدنی، {study['truncated']} بریدهشده، "
             f"{study['witnesses_valid']} شاهد مستقل معتبر. [M] روی مجموعههای "
             f"شدنی، LST و EDF در اجرای همتراز به ترتیب "
             f"{study['lst_misses_on_feasible']} و "
             f"{study['edf_misses_on_feasible']} خطا میدهند، در حالی که RM "
             f"{study['rm_misses_on_feasible']} خطا دارد. عوض کردنِ تساویشکنی "
             f"LST حکم را روی {study['tie_break_verdict_changes']} مجموعه عوض "
             f"کرد. دستهٔ کنترلِ {study['implicit_sets']} مجموعه با ضربالاجل "
             f"ضمنی، {study['implicit_feasible']} حکم شدنی داد، و برای همین "
             f"آن رژیم نمیتواند ادعا را نقض کند."),
            {"generated": study["sets_generated"],
             "feasible": study["feasible"],
             "infeasible": study["infeasible"],
             "truncated": study["truncated"],
             "valid_witnesses": study["witnesses_valid"],
             "lst_misses": study["lst_misses_on_feasible"],
             "edf_misses": study["edf_misses_on_feasible"],
             "rm_misses": study["rm_misses_on_feasible"],
             "tie_verdict_changes": study["tie_break_verdict_changes"],
             "implicit_sets": study["implicit_sets"],
             "implicit_feasible": study["implicit_feasible"]},
            source="random"),
        L.finding(
            "F6", "M",
            "Under overload the interesting number is the first miss",
            "زیر بار اضافه عددِ جالب نخستین خطا است",
            (f"[M] On the overloaded set {sets[3]['id']} LST misses "
             f"{r4['lst']['missed']} deadlines with first miss at "
             f"t={r4['lst']['first_miss']}, minimum observed laxity "
             f"{r4['lst']['min_laxity']} and "
             f"{r4['lst']['laxity_zero_switches']} switches at zero laxity; "
             f"EDF misses {r4['edf']['missed']} with first miss at "
             f"t={r4['edf']['first_miss']}. [E] The checker says "
             f"{'feasible' if sets[3]['checker']['feasible'] else 'infeasible'} "
             f"and returns no witness. Missed jobs are kept running rather "
             f"than dropped, so these counts describe a degraded system, not "
             f"a failed instrument."),
            (f"[M] روی مجموعهٔ پُربار {sets[3]['id']}، LST برابر "
             f"{r4['lst']['missed']} ضربالاجل از دست میدهد با نخستین خطا در "
             f"t={r4['lst']['first_miss']}، کمینهٔ لَکسیَتی دیدهشده "
             f"{r4['lst']['min_laxity']} و "
             f"{r4['lst']['laxity_zero_switches']} تعویض در لَکسیَتی صفر؛ EDF "
             f"{r4['edf']['missed']} خطا با نخستین خطا در "
             f"t={r4['edf']['first_miss']}. [E] چککننده «"
             f"{'شدنی' if sets[3]['checker']['feasible'] else 'نشدنی'}» میگوید "
             f"و شاهدی برنمیگرداند. کارهای خطاکرده حذف نمیشوند بلکه همچنان "
             f"اجرا میشوند، پس این شمارشها سیستمی افتکرده را توصیف میکنند، "
             f"نه ابزاری خراب را."),
            {"lst_missed": r4["lst"]["missed"],
             "lst_first_miss": r4["lst"]["first_miss"],
             "lst_min_laxity": r4["lst"]["min_laxity"],
             "lst_zero_switches": r4["lst"]["laxity_zero_switches"],
             "edf_missed": r4["edf"]["missed"],
             "edf_first_miss": r4["edf"]["first_miss"]},
            source="task_sets[3].policies"),
    ]


def main():
    global STUDY
    STUDY = random_study()
    L.build_exercise(
        __file__, 4, SPECS,
        "fixed-seed exhaustive verification on constrained deadlines, "
        "independent witness checks, an implicit-deadline control and overload",
        "بررسی جامع بذرثابت روی ضربالاجلهای مقید، راستیآزمایی مستقل شاهدها، "
        "کنترلِ ضربالاجل ضمنی و بار اضافه",
        sweeps_fn=sweeps_fn, extra_figures_fn=extra_figures,
        extra_findings_fn=extra_findings, prefix="ex4",
        extra={"random": STUDY})
    return 0


if __name__ == "__main__":
    sys.exit(main())
