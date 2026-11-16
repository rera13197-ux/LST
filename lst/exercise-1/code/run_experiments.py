#!/usr/bin/env python3
"""Exercise 1 — what LST minimises, and what that choice costs.

Run from anywhere::

    python3 code/run_experiments.py

Writes ``output/experiments.json``.  Every number in the reports is read from
that file; no measured constant lives in the content modules.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L
from lst_core import (Task, exhaustive_feasible, hyperperiod, simulate,
                      utilisation)

SEED = L.SEED

# id, label, [name, period, wcet, (deadline), (phase)]
SPECS = [
    ("S1", "implicit deadlines, harmonic-ish", [["T1", 6, 2], ["T2", 8, 2], ["T3", 12, 3]]),
    ("S2", "constrained deadlines", [["T1", 6, 2, 4], ["T2", 8, 2, 5], ["T3", 12, 3, 7]]),
    ("S3", "phased releases", [["T1", 6, 2, 4, 0], ["T2", 8, 2, 5, 2], ["T3", 12, 3, 7, 1]]),
    ("S4", "phased, deadline past the hyperperiod", [["T1", 4, 2, 3, 0], ["T2", 4, 3, 4, 3]]),
    ("S5", "tight deadlines, infeasible", [["T1", 5, 2, 3], ["T2", 6, 2, 3]]),
    ("S6", "two equal tasks, full utilisation", [["T1", 4, 2, 4], ["T2", 4, 2, 4]]),
    ("S7", "harmonic periods", [["T1", 4, 1, 3], ["T2", 8, 2, 6], ["T3", 16, 4, 12]]),
    ("S8", "heavy but infeasible", [["T1", 5, 2, 3], ["T2", 10, 3, 6], ["T3", 10, 2, 7]]),
]


def build_sets():
    return [L.describe_set(L.mk(rows), sid, label)
            for sid, label, rows in SPECS]


def build_sweeps(sets):
    """Two parameter sweeps plus an alignment sweep.  One parameter changes,
    everything else is held fixed; every plotted value is measured here."""
    sweeps = []
    dv, lst_m, edf_m, rm_m, feas = [], [], [], [], []
    for d1 in range(2, 7):
        tasks = L.mk([["T1", 6, 2, d1], ["T2", 8, 2], ["T3", 12, 3]])
        ok, _s, _st = exhaustive_feasible(tasks, horizon=hyperperiod(tasks))
        r1 = simulate(tasks, "lst", cycles=2)
        r2 = simulate(tasks, "edf", cycles=2)
        r3 = simulate(tasks, "rm", cycles=2)
        dv.append(d1)
        lst_m.append(r1.missed)
        edf_m.append(r2.missed)
        rm_m.append(r3.missed)
        feas.append(1 if ok else 0)
    sweeps.append(L.sweep("deadline", "deadline of T1 (time units)", "count",
                          dv, [{"name": "lst_missed", "values": lst_m},
                               {"name": "edf_missed", "values": edf_m},
                               {"name": "rm_missed", "values": rm_m},
                               {"name": "checker_feasible", "values": feas}],
                          "sweeps[0]", figure="fig_ex1_deadline_sweep.png"))

    cv, lst_p, edf_p, rm_p, lst_mm = [], [], [], [], []
    for c1 in range(1, 5):
        tasks = L.mk([["T1", 6, c1], ["T2", 8, 2], ["T3", 12, 3]])
        a, b, c, d = (simulate(tasks, p, cycles=2)
                      for p in ("lst", "edf", "rm", "lst"))
        cv.append(round(utilisation(tasks), 4))
        lst_p.append(a.preemptions)
        edf_p.append(b.preemptions)
        rm_p.append(c.preemptions)
        lst_mm.append(d.missed)
    sweeps.append(L.sweep("utilisation", "utilisation (descriptive)", "count",
                          cv, [{"name": "lst_preemptions", "values": lst_p},
                               {"name": "edf_preemptions", "values": edf_p},
                               {"name": "rm_preemptions", "values": rm_p},
                               {"name": "lst_missed", "values": lst_mm}],
                          "sweeps[1]", figure="fig_ex1_util_sweep.png"))

    ids, naive, aligned, verdict = [], [], [], []
    for s in sets:
        al = s["alignment"]
        ids.append(s["id"])
        naive.append(al["naive"]["lst"]["missed"])
        aligned.append(al["aligned"]["lst"]["missed"])
        verdict.append(1 if al["checker_verdict"] else 0)
    sweeps.append(L.sweep("alignment", "task set", "count", ids,
                          [{"name": "naive_lst_missed", "values": naive},
                           {"name": "aligned_lst_missed", "values": aligned},
                           {"name": "checker_feasible", "values": verdict}],
                          "sweeps[2]", figure="fig_ex1_alignment.png"))
    return sweeps


def build_figures(sets, sweeps):
    figs = []
    s1 = sets[0]
    figs.append(L.fig_bar("fig_ex1_preemptions.png",
                          "Preemptions by policy on S1 (two hyperperiods)",
                          [p for p in s1["policies"]],
                          [s1["policies"][p]["preemptions"] for p in s1["policies"]],
                          "task_sets[0].policies.*.preemptions", ylabel="preemptions"))
    for sw in sweeps:
        figs.append(L.fig_line(sw["figure"],
                               "Sweep " + sw["id"] + ": " + sw["xlabel"],
                               sw["x"], sw["series"], sw["source"],
                               ylabel=sw["ylabel"], xlabel=sw["xlabel"]))
    figs.append(L.fig_gantt("fig_ex1_gantt_lst.png", "LST schedule on S1",
                            s1["gantt"]["lst"][:16],
                            "task_sets[0].gantt.lst"))
    figs.append(L.fig_gantt("fig_ex1_gantt_edf.png", "EDF schedule on S1",
                            s1["gantt"]["edf"][:16],
                            "task_sets[0].gantt.edf"))
    figs.append(L.fig_grouped(
        "fig_ex1_misses.png", "Missed deadlines per set and policy",
        [s["id"] for s in sets],
        [{"name": p,
          "values": [s["policies"][p]["missed"] for s in sets]}
         for p in ("lst", "edf", "rm")],
        "task_sets[*].policies.*.missed", ylabel="missed deadlines",
        xlabel="task set"))
    figs.append(L.fig_heatmap(
        "fig_ex1_tie_heatmap.png", "Tie events per set and policy",
        [[s["policies"][p]["tie_events"] for s in sets] for p in L.LST_POLICIES],
        [s["id"] for s in sets], list(L.LST_POLICIES),
        "task_sets[*].policies.*.tie_events"))
    return figs


def build_findings(sets):
    s1, s2, s4 = sets[0], sets[1], sets[3]
    p1 = s1["policies"]
    implicit = [s for s in sets if not s["constrained_deadline"]]
    constrained = [s for s in sets if s["constrained_deadline"]]
    cap = s1["cap_control"]
    cap_bad = [r for r in cap["rows"] if r["truncated"] and not r["feasible"]]
    cheaper = [s for s in sets
               if s["witness_cost"].get("available")
               and s["witness_cost"]["preemptions"] < s["policies"]["lst"]["preemptions"]]
    al4 = s4["alignment"]
    return [
        L.finding(
            "F1", "M",
            "Minimising slack is not minimising overhead",
            "کمینه کردن لَکسیَتی، کمینه کردن سربار نیست",
            (f"[M] On {s1['id']} the checker says "
             f"{'feasible' if s1['checker']['feasible'] else 'infeasible'} [E], "
             f"yet LST records {p1['lst']['preemptions']} preemptions while "
             f"EDF records {p1['edf']['preemptions']}; both miss "
             f"{p1['lst']['missed']} deadlines. LST's stricter local rule buys "
             f"no extra correctness here and costs measured context switches: "
             f"{p1['lst']['context_switches']} against "
             f"{p1['edf']['context_switches']}."),
            (f"[M] روی {s1['id']} چککننده حکم «"
             f"{'شدنی' if s1['checker']['feasible'] else 'نشدنی'}» میدهد [E]، "
             f"با این حال LST برابر {p1['lst']['preemptions']} پیشگیری ثبت میکند "
             f"در حالی که EDF برابر {p1['edf']['preemptions']} دارد؛ هر دو "
             f"{p1['lst']['missed']} ضربالاجل از دست میدهند. قاعدهٔ محلیِ "
             f"سختگیرانهٔ LST اینجا درستی اضافهای نمیخرد ولی تعویضهای زمینهٔ "
             f"اندازهگیریشدهای میپردازد: {p1['lst']['context_switches']} در "
             f"برابر {p1['edf']['context_switches']}."),
            {"lst_preemptions": p1["lst"]["preemptions"],
             "edf_preemptions": p1["edf"]["preemptions"],
             "lst_switches": p1["lst"]["context_switches"],
             "edf_switches": p1["edf"]["context_switches"],
             "lst_missed": p1["lst"]["missed"]},
            source="task_sets[0].policies"),
        L.finding(
            "F2", "B",
            "Implicit deadlines take the test away",
            "ضربالاجل ضمنی، آزمون را از میان برمیدارد",
            (f"[E] Of {len(implicit)} sets with implicit deadlines and "
             f"utilisation at most one, {sum(1 for s in implicit if s['checker']['feasible'])} "
             f"are feasible. Of {len(constrained)} constrained sets, "
             f"{sum(1 for s in constrained if s['checker']['feasible'])} are "
             f"feasible and {sum(1 for s in constrained if not s['checker']['feasible'])} "
             f"are infeasible. A study whose yardstick is feasibility therefore "
             f"cannot be calibrated in the implicit regime; the constrained "
             f"regime is where the checker can be wrong and the experiment has "
             f"power."),
            (f"[E] از {len(implicit)} مجموعه با ضربالاجل ضمنی و بهرهوری حداکثر "
             f"یک، {sum(1 for s in implicit if s['checker']['feasible'])} مجموعه "
             f"شدنیاند. از {len(constrained)} مجموعهٔ مقید، "
             f"{sum(1 for s in constrained if s['checker']['feasible'])} شدنی و "
             f"{sum(1 for s in constrained if not s['checker']['feasible'])} "
             f"نشدنیاند. پس پژوهشی که سنجهاش شدنیبودن باشد در رژیم ضمنی "
             f"واسنجی نمیشود؛ رژیم مقید جایی است که چککننده میتواند اشتباه کند "
             f"و آزمایش قدرت دارد."),
            {"implicit_sets": len(implicit),
             "implicit_feasible": sum(1 for s in implicit if s["checker"]["feasible"]),
             "constrained_sets": len(constrained),
             "constrained_feasible": sum(1 for s in constrained if s["checker"]["feasible"]),
             "constrained_infeasible": sum(1 for s in constrained if not s["checker"]["feasible"])},
            source="task_sets[*].checker"),
        L.finding(
            "F3", "D",
            "A phased set where the instruments disagree",
            "مجموعهای فازدار که دو ابزار در آن اختلاف دارند",
            (f"[D] On {s4['id']} the checker verdict is "
             f"{'feasible' if al4['checker_verdict'] else 'infeasible'} over "
             f"one hyperperiod, but the naive two-hyperperiod LST run misses "
             f"{al4['naive']['lst']['missed']} deadlines while the aligned run "
             f"misses {al4['aligned']['lst']['missed']}. The two instruments "
             f"were looking at different job sets: a phased release has a "
             f"deadline beyond the hyperperiod, so the longer run adds a job "
             f"that the checker never saw. Aligning the release window removes "
             f"the disagreement. The instrument was the suspect, and it was "
             f"the culprit."),
            (f"[D] روی {s4['id']} حکم چککننده روی یک دورهٔ بزرگ «"
             f"{'شدنی' if al4['checker_verdict'] else 'نشدنی'}» است، ولی اجرای "
             f"سادهلوحِ LST در دو دورهٔ بزرگ {al4['naive']['lst']['missed']} "
             f"خطا میدهد، در حالی که اجرای همتراز {al4['aligned']['lst']['missed']} "
             f"خطا دارد. دو ابزار به دو مجموعهٔ متفاوت از کارها نگاه میکردند: "
             f"انتشارِ فازدار ضربالاجلی فراتر از دورهٔ بزرگ دارد، پس اجرای "
             f"بلندتر کاری میافزاید که چککننده هرگز ندیده است. همتراز کردنِ "
             f"پنجرهٔ انتشار اختلاف را برمیدارد. ابزار مظنون بود و مقصر هم بود."),
            {"checker_feasible": 1 if al4["checker_verdict"] else 0,
             "naive_lst_missed": al4["naive"]["lst"]["missed"],
             "aligned_lst_missed": al4["aligned"]["lst"]["missed"],
             "checker_jobs": s4["checker"]["jobs"]},
            source="task_sets[3].alignment"),
        L.finding(
            "F4", "D",
            "A state cap fabricates an infeasibility verdict",
            "سقفِ حالت، حکمِ نشدنیبودن میسازد",
            (f"[D] With the checker's state cap reduced, {s1['id']} is reported "
             f"infeasible {len(cap_bad)} times and every one of those runs is "
             f"flagged truncated; with the cap restored the verdict is "
             f"{'feasible' if cap['full_verdict'] else 'infeasible'}. The "
             f"smallest truncating cap was {cap['smallest_truncating_limit']}. "
             f"A truncated result is an artefact of the instrument. It is "
             f"reported here and never used as a scheduling finding."),
            (f"[D] وقتی سقفِ حالت چککننده کم شود، {s1['id']} به تعداد "
             f"{len(cap_bad)} بار نشدنی گزارش میشود و تکتک آن اجراها برچسب "
             f"بریدگی دارند؛ با برگرداندن سقف، حکم «"
             f"{'شدنی' if cap['full_verdict'] else 'نشدنی'}» است. کمترین سقفِ "
             f"بریدهکننده {cap['smallest_truncating_limit']} بود. نتیجهٔ "
             f"بریدهشده مصنوعِ ابزار است. اینجا گزارش میشود و هرگز به عنوان "
             f"یافتهٔ زمانبندی به کار نمیرود."),
            {"false_infeasible_runs": len(cap_bad),
             "smallest_truncating_limit": cap["smallest_truncating_limit"],
             "full_states": s1["checker"]["states"],
             "full_feasible": 1 if cap["full_verdict"] else 0},
            source="task_sets[0].cap_control"),
        L.finding(
            "F5", "M",
            "The checker's own witness is cheaper than LST",
            "شاهدِ خودِ چککننده از LST ارزانتر است",
            (f"[E] Every witness returned for a feasible set is re-checked by "
             f"an independent verifier; {sum(1 for s in sets if s['witness'].get('valid') is True)} "
             f"witnesses were valid. [M] On {len(cheaper)} sets the witness "
             f"schedule needs fewer preemptions than LST on the same task set: "
             f"for {s1['id']}, {s1['witness_cost']['preemptions']} against "
             f"{s1['policies']['lst']['preemptions']}. Verification calls the "
             f"two schedules equivalent; measurement separates them. The "
             f"witness is a counterexample to the claim that all feasible "
             f"schedules cost the same."),
            (f"[E] هر شاهدی که برای مجموعهای شدنی برگردانده شود توسط "
             f"راستیآزمای مستقل دوباره چک میشود؛ "
             f"{sum(1 for s in sets if s['witness'].get('valid') is True)} شاهد "
             f"معتبر بودند. [M] روی {len(cheaper)} مجموعه، برنامهٔ شاهد به "
             f"پیشگیریهای کمتری از LST روی همان مجموعه نیاز دارد: برای "
             f"{s1['id']}، {s1['witness_cost']['preemptions']} در برابر "
             f"{s1['policies']['lst']['preemptions']}. بررسی، دو برنامه را "
             f"همارز میداند؛ اندازهگیری جدا میکند. شاهد، counterexample ادعای "
             f"«همهٔ برنامههای شدنی هزینهٔ یکسان دارند» است."),
            {"valid_witnesses": sum(1 for s in sets if s["witness"].get("valid") is True),
             "witness_cheaper_sets": len(cheaper),
             "witness_preemptions_S1": s1["witness_cost"]["preemptions"],
             "lst_preemptions_S1": s1["policies"]["lst"]["preemptions"]},
            source="task_sets[*].witness_cost"),
        L.finding(
            "F6", "E",
            "RM is a genuine counterexample, not an instrument mismatch",
            "RM یک ضدمثال واقعی است، نه ناهماهنگی ابزار",
            (f"[E] {s2['id']} is feasible by the exhaustive checker. [M] RM "
             f"misses {s2['policies']['rm']['missed']} deadlines on it while "
             f"LST and EDF miss {s2['policies']['lst']['missed']} and "
             f"{s2['policies']['edf']['missed']}. This is a counterexample to "
             f"RM's optimality, not a defect in the checker: the checker's "
             f"witness is valid, and the aligned RM run still misses "
             f"{s2['alignment']['aligned']['rm']['missed']}. The first version "
             f"of the alignment helper mixed this up by demanding that RM "
             f"agree with the verdict."),
            (f"[E] {s2['id']} به حکم چککنندهٔ جامع شدنی است. [M] RM روی آن "
             f"{s2['policies']['rm']['missed']} ضربالاجل از دست میدهد در حالی "
             f"که LST و EDF به ترتیب {s2['policies']['lst']['missed']} و "
             f"{s2['policies']['edf']['missed']} خطا دارند. این ضدمثالِ "
             f"بهینگی RM است، نه نقصِ چککننده: شاهدش معتبر است و اجرای همترازِ "
             f"RM باز هم {s2['alignment']['aligned']['rm']['missed']} خطا "
             f"میدهد. نسخهٔ نخستِ کمکتابعِ همترازسازی همین را قاطی کرده بود، "
             f"چون از RM میخواست با حکم جور باشد."),
            {"rm_missed": s2["policies"]["rm"]["missed"],
             "lst_missed": s2["policies"]["lst"]["missed"],
             "edf_missed": s2["policies"]["edf"]["missed"],
             "rm_aligned_missed": s2["alignment"]["aligned"]["rm"]["missed"]},
            source="task_sets[1].policies.rm"),
    ]


def main():
    sets = build_sets()
    sweeps = build_sweeps(sets)
    figures = build_figures(sets, sweeps)
    findings = build_findings(sets)
    L.finish(__file__, 1, sets, sweeps, figures, findings,
             "laxity, the LST decision rule, first measurements and "
             "the two-instrument method",
             "لَکسیَتی، قاعدهٔ تصمیم LST، نخستین اندازهگیریها و روشِ دو ابزاری")
    return 0


if __name__ == "__main__":
    sys.exit(main())
