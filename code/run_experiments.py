#!/usr/bin/env python3
"""Exercise 3 — a hand-worked LST schedule and an independent program trace.

The hand table is produced by a second implementation of the decision rule
(``hand_trace`` in lab_kit), not by the simulator.  A third hand rule (earliest
deadline first) supplies a divergence witness.  All three timelines are written
to ``output/experiments.json`` and are compared by the tests.

    python3 code/run_experiments.py   ->   output/experiments.json
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L
from lst_core import hyperperiod, make_jobs

SPECS = [
    ("M1", "worked example, implicit deadlines", [["T1", 6, 2], ["T2", 8, 2], ["T3", 12, 3]]),
    ("M2", "two equal tasks", [["T1", 4, 2, 4], ["T2", 4, 2, 4]]),
    ("M3", "constrained deadlines", [["T1", 6, 2, 4], ["T2", 8, 2, 5], ["T3", 12, 3, 7]]),
    ("M4", "tight and infeasible", [["T1", 5, 2, 3], ["T2", 6, 2, 3]]),
    ("M5", "phased releases", [["T1", 6, 2, 4, 0], ["T2", 8, 2, 5, 2], ["T3", 12, 3, 7, 1]]),
    ("M6", "harmonic periods", [["T1", 4, 1, 3], ["T2", 8, 2, 6], ["T3", 16, 4, 12]]),
]


def edf_hand(tasks, horizon):
    """A third, independent hand rule: earliest absolute deadline first."""
    jobs = make_jobs(tasks, horizon)
    left = [j.wcet for j in jobs]
    out = []
    for t in range(horizon):
        ready = [i for i, j in enumerate(jobs) if j.release <= t and left[i] > 0]
        if not ready:
            out.append(None)
            continue
        chosen = min(ready, key=lambda i: (jobs[i].deadline, i))
        out.append(jobs[chosen].name)
        left[chosen] -= 1
    return out


def traces_fn(sets):
    """Compute hand traces for every set; store one as the primary worked table."""
    all_traces = []
    for s in sets:
        tasks = L.mk(s["tasks"])
        hp = s["hyperperiod"]
        tr = L.hand_trace(tasks, hp)
        all_traces.append({"id": s["id"], "horizon": hp,
                           "agree": tr["agree"],
                           "compared_steps": tr["compared_steps"],
                           "gantt": tr["gantt"]})
    primary_tasks = L.mk(sets[0]["tasks"])
    hp = sets[0]["hyperperiod"]
    primary = L.hand_trace(primary_tasks, hp)
    edf = edf_hand(primary_tasks, hp)
    pairs = list(zip(primary["timeline_names"], edf))
    divergent = [[t, a, b] for t, (a, b) in enumerate(pairs) if a != b]
    primary["divergence"] = {
        "first_divergence": divergent[0][0] if divergent else -1,
        "divergent_count": len(divergent),
        "compared_steps": len(pairs),
        "witness": divergent[:10],
        "edf_timeline": edf,
    }
    primary["traces"] = all_traces
    primary["agreeing_traces"] = sum(1 for t in all_traces if t["agree"])
    return {"manual": primary,
            "extra": {"traces": all_traces,
                      "agreeing_traces": primary["agreeing_traces"]}}


def sweeps_fn(sets):
    base = lambda d: L.mk([["T1", 6, 2, d], ["T2", 8, 2], ["T3", 12, 3]])
    return [
        L.sweep_parameter("deadline-misses", "deadline of T1 (time units)",
                          list(range(2, 7)), base, "missed",
                          figure="fig_ex3_deadline_misses.png",
                          source="sweeps[0]"),
        L.sweep_parameter("deadline-preemptions", "deadline of T1 (time units)",
                          list(range(2, 7)), base, "preemptions",
                          figure="fig_ex3_deadline_pre.png",
                          source="sweeps[1]"),
        L.sweep_alignment(sets, figure="fig_ex3_alignment.png",
                          source="sweeps[2]"),
    ]


def extra_figures(sets, sweeps):
    return [
        L.fig_gantt("fig_ex3_hand_gantt.png", "Hand-trace schedule on M1",
                    L.hand_gantt(L.hand_trace(L.mk(sets[0]["tasks"]),
                                              sets[0]["hyperperiod"]))[:16],
                    "manual.gantt"),
    ]


def main():
    def findings_fn(sets):
        tasks0 = L.mk(sets[0]["tasks"])
        hp = sets[0]["hyperperiod"]
        hand = L.hand_trace(tasks0, hp)
        edf = edf_hand(tasks0, hp)
        div = [[t, a, b] for t, (a, b) in enumerate(zip(hand["timeline_names"], edf))
               if a != b]
        agreeing = []
        for s in sets:
            tr = L.hand_trace(L.mk(s["tasks"]), s["hyperperiod"])
            agreeing.append(tr["agree"])
        return [
            L.finding(
                "F5", "M",
                "The hand table and the simulator agree step by step",
                "جدول دستی و شبیهساز گامبهگام جوراند",
                (f"[M] For {sum(1 for a in agreeing if a)} of {len(sets)} task "
                 f"sets the independent hand trace and the simulator timeline "
                 f"agree at every one of the compared instants; the primary "
                 f"worked example compares {hand['compared_steps']} instants. "
                 f"This is not a proof: it is two separate programs agreeing "
                 f"on the same integer timeline, and the agreement is checked "
                 f"by a test in this repository."),
                (f"[M] برای {sum(1 for a in agreeing if a)} از {len(sets)} "
                 f"مجموعهکار، ردگیری دستی مستقل و خطِ زمان شبیهساز در تکتک "
                 f"لحظههای مقایسهشده جوراند؛ مثالِ دستی اصلی "
                 f"{hand['compared_steps']} لحظه را مقایسه میکند. این برهان "
                 f"نیست: دو برنامهٔ جدااند که روی یک خطِ زمان صحیح به یک نتیجه "
                 f"میرسند، و تطابقشان را تستی در این مخزن چک میکند."),
                {"task_sets": len(sets),
                 "agreeing_traces": sum(1 for a in agreeing if a),
                 "primary_steps": hand["compared_steps"],
                 "primary_agree": 1 if hand["agree"] else 0},
                source="manual + extra.traces"),
            L.finding(
                "F6", "M",
                "A witness that the two hand rules are different algorithms",
                "شاهدی که دو قاعدهٔ دستی دو الگوریتم متفاوتاند",
                (f"[M] An independent earliest-deadline hand rule is run on "
                 f"the same worked task set. The two hand rules choose "
                 f"different jobs at {len(div)} of {len(edf)} instants, first "
                 f"at t={div[0][0] if div else -1}. The witness lines below "
                 f"are printed from the generated data; a verbal claim that "
                 f"the policies differ would be weaker than this sequence."),
                (f"[M] قاعدهٔ دستی مستقلِ زودترین ضربالاجل نخست روی همان "
                 f"مجموعه اجرا میشود. دو قاعدهٔ دستی در {len(div)} لحظه از "
                 f"{len(edf)} لحظه کارهای متفاوتی برمیکزینند، نخستین بار در "
                 f"t={div[0][0] if div else -1}. خطوط شاهد زیر از دادهٔ "
                 f"تولیدشده چاپ میشوند؛ ادعای کلامی دربارهٔ تفاوت سیاستها "
                 f"ضعیفتر از این دنباله است."),
                {"divergent_instants": len(div),
                 "compared_instants": len(edf),
                 "first_divergence": div[0][0] if div else -1},
                witness=[f"t={w[0]} LST={w[1]} EDF={w[2]}" for w in div[:8]],
                source="manual.divergence"),
        ]

    L.build_exercise(
        __file__, 3, SPECS,
        "a hand-worked LST table, an independent program trace, and a printed "
        "divergence witness against an earliest-deadline hand rule",
        "جدول دستی LST، یک ردگیری مستقل از برنامه، و شاهد چاپشدهٔ واگرایی "
        "در برابر قاعدهٔ دستی زودترین ضربالاجل",
        sweeps_fn=sweeps_fn, extra_figures_fn=extra_figures,
        extra_findings_fn=findings_fn, extra_fn=traces_fn, prefix="ex3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
