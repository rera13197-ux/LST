#!/usr/bin/env python3
"""Exercise 7 — tie-breaking and laxity-zero thrashing.

The checker answers one question (is there a feasible schedule) and is silent
about cost.  The simulator counts what each LST tie-break costs.  This exercise
keeps the two instruments apart deliberately and reports where they look like
they disagree but do not: a verdict invariant under tie-breaking, and a cost
that is not.

    python3 code/run_experiments.py   ->   output/experiments.json
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L

SPECS = [
    ("K1", "two equal short tasks", [["T1", 4, 2, 4], ["T2", 4, 2, 4]]),
    ("K2", "two equal long tasks", [["T1", 8, 4, 8], ["T2", 8, 4, 8]]),
    ("K3", "three equal tasks", [["T1", 6, 2, 6], ["T2", 6, 2, 6], ["T3", 6, 2, 6]]),
    ("K4", "four equal tasks", [["T1", 8, 2, 8], ["T2", 8, 2, 8],
                                ["T3", 8, 2, 8], ["T4", 8, 2, 8]]),
    ("K5", "mixed periods, heavy thrashing", [["T1", 6, 3, 4], ["T2", 9, 3, 5],
                                               ["T3", 12, 2, 7]]),
    ("K6", "tight pair, infeasible", [["T1", 5, 2, 3], ["T2", 6, 2, 3]]),
    ("K7", "tight triple, overload", [["T1", 5, 2, 3], ["T2", 5, 2, 3],
                                       ["T3", 10, 3, 6]]),
    ("K8", "phased, deadline past hyperperiod", [["T1", 4, 2, 3, 0], ["T2", 4, 3, 4, 3]]),
]


def equal_tasks(n):
    return L.mk([[f"T{i + 1}", 10, 2, 10] for i in range(n)])


def symmetric_deadline(d):
    return L.mk([["T1", 8, 4, d], ["T2", 8, 4, d]])


def sweeps_fn(sets):
    return [
        L.sweep_parameter("task-count", "number of equal tasks", [2, 3, 4, 5],
                          equal_tasks, "preemptions",
                          policies=L.LST_POLICIES,
                          figure="fig_ex7_taskcount.png", source="sweeps[0]"),
        L.sweep_parameter("deadline-zero-switches", "shared deadline (time units)",
                          [4, 5, 6, 7, 8], symmetric_deadline,
                          "laxity_zero_switches", policies=L.LST_POLICIES,
                          figure="fig_ex7_deadline_lzs.png", source="sweeps[1]"),
        L.sweep_alignment(sets, figure="fig_ex7_alignment.png",
                          source="sweeps[2]"),
    ]


def extra_figures(sets, sweeps):
    ids = [s["id"] for s in sets]
    return [
        L.fig_grouped("fig_ex7_tiebreak.png",
                      "Preemptions by LST tie-break and task set",
                      ids,
                      [{"name": p,
                        "values": [s["policies"][p]["preemptions"] for s in sets]}
                       for p in L.LST_POLICIES],
                      "task_sets[*].policies.*.preemptions",
                      ylabel="preemptions", xlabel="task set"),
        L.fig_heatmap("fig_ex7_lzs.png",
                      "Laxity-zero switches by tie-break and task set",
                      [[s["policies"][p]["laxity_zero_switches"] for s in sets]
                       for p in L.LST_POLICIES],
                      ids, list(L.LST_POLICIES),
                      "task_sets[*].policies.*.laxity_zero_switches"),
        L.fig_grouped("fig_ex7_jitter.png", "Response jitter: LST, stay, EDF",
                      ids,
                      [{"name": p,
                        "values": [s["policies"][p]["jitter"] or 0 for s in sets]}
                       for p in ("lst", "lst:stay", "edf")],
                      "task_sets[*].policies.*.jitter",
                      ylabel="jitter", xlabel="task set"),
    ]


def extra_findings(sets):
    k2, k5 = sets[1], sets[4]
    p2, p5 = k2["policies"], k5["policies"]
    # verdict invariance: does any tie-break change zero-miss status on a set?
    invariant = [s for s in sets
                 if len({s["policies"][p]["missed"] == 0
                         for p in L.LST_POLICIES}) > 1]
    feasible = [s for s in sets if s["checker"]["feasible"]]
    spread = [(s["id"],
               max(s["policies"][p]["preemptions"] for p in L.LST_POLICIES)
               - min(s["policies"][p]["preemptions"] for p in L.LST_POLICIES))
              for s in sets]
    widest = max(spread, key=lambda x: x[1])
    max_lzs = max(s["policies"]["lst"]["laxity_zero_switches"] for s in sets)
    cheaper_jitter = [s for s in sets
                      if s["policies"]["lst"]["jitter"] is not None
                      and s["policies"]["edf"]["jitter"] is not None
                      and s["policies"]["lst"]["jitter"]
                      < s["policies"]["edf"]["jitter"]]
    return [
        L.finding(
            "F5", "M",
            "Tie-breaking changes the cost, not the verdict",
            "تساویشکنی هزینه را عوض میکند، نه حکم را",
            (f"[E] On all {len(feasible)} feasible sets the checker's verdict "
             f"is unchanged by the choice of tie-break, and "
             f"{len(invariant)} sets show a tie-break changing LST's "
             f"zero-miss status at all. [M] On {k2['id']}, "
             f"lst records {p2['lst']['preemptions']} preemptions while "
             f"lst:stay records {p2['lst:stay']['preemptions']} and EDF "
             f"{p2['edf']['preemptions']}. The widest spread between two "
             f"tie-breaks is {widest[1]} preemptions on {widest[0]}. "
             f"Verification treats these as the same feasible outcome; the "
             f"machine does not."),
            (f"[E] روی همهٔ {len(feasible)} مجموعهٔ شدنی، حکم چککننده با عوض "
             f"شدنِ تساویشکنی تغییر نمیکند، و {len(invariant)} مجموعه نشان "
             f"میدهند تساویشکنی اصولاً وضعیتِ صفرخطای LST را عوض کند. "
             f"[M] روی {k2['id']}، lst برابر {p2['lst']['preemptions']} "
             f"پیشگیری، lst:stay برابر {p2['lst:stay']['preemptions']} و EDF "
             f"برابر {p2['edf']['preemptions']} ثبت میکند. بیشترین شکافِ دو "
             f"تساویشکنی برابر {widest[1]} پیشگیری روی {widest[0]} است. بررسی "
             f"اینها را یک نتیجهٔ شدنی یکسان میداند؛ ماشین نه."),
            {"feasible_sets": len(feasible),
             "verdict_changing_sets": len(invariant),
             "lst_preemptions_K2": p2["lst"]["preemptions"],
             "stay_preemptions_K2": p2["lst:stay"]["preemptions"],
             "edf_preemptions_K2": p2["edf"]["preemptions"],
             "widest_spread": widest[1]},
            source="task_sets[*].policies"),
        L.finding(
            "F6", "M",
            "Laxity-zero thrashing is measurable, and the cheap policy is not "
            "cheap on every metric",
            "لرزشِ لَکسیَتی صفر اندازهپذیر است، و سیاست ارزان در همهٔ سنجهها ارزان نیست",
            (f"[M] On {k5['id']}, lst records "
             f"{p5['lst']['laxity_zero_switches']} switches at zero laxity, "
             f"lst:stay records {p5['lst:stay']['laxity_zero_switches']} and "
             f"EDF {p5['edf']['laxity_zero_switches']}; the largest value over "
             f"all sets is {max_lzs}. Yet on {len(cheaper_jitter)} sets LST has "
             f"strictly smaller response jitter than EDF even though it "
             f"preempts more: on {k2['id']} the jitters are "
             f"{p2['lst']['jitter']} and {p2['edf']['jitter']}. A single "
             f"metric would have hidden this. We report the trade-off rather "
             f"than declaring a winner the data does not support."),
            (f"[M] روی {k5['id']}، lst برابر "
             f"{p5['lst']['laxity_zero_switches']} تعویض در لَکسیَتی صفر، "
             f"lst:stay برابر {p5['lst:stay']['laxity_zero_switches']} و EDF "
             f"برابر {p5['edf']['laxity_zero_switches']} ثبت میکند؛ بیشترین "
             f"مقدار روی همهٔ مجموعهها {max_lzs} است. با این حال روی "
             f"{len(cheaper_jitter)} مجموعه لرزش پاسخ LST اکیداً کوچکتر از EDF "
             f"است، هرچند پیشگیری بیشتری دارد: روی {k2['id']} لرزشها برابر "
             f"{p2['lst']['jitter']} و {p2['edf']['jitter']}اند. یک سنجهٔ تنها "
             f"این را پنهان میکرد. ما بدهبستان را گزارش میکنیم، نه برندهای را "
             f"که داده پشتیبانی نمیکند."),
            {"lst_zero_switches_K5": p5["lst"]["laxity_zero_switches"],
             "stay_zero_switches_K5": p5["lst:stay"]["laxity_zero_switches"],
             "edf_zero_switches_K5": p5["edf"]["laxity_zero_switches"],
             "max_zero_switches": max_lzs,
             "lst_lower_jitter_sets": len(cheaper_jitter),
             "lst_jitter_K2": p2["lst"]["jitter"],
             "edf_jitter_K2": p2["edf"]["jitter"]},
            source="task_sets[*].policies"),
    ]


def main():
    L.build_exercise(
        __file__, 7, SPECS,
        "the cost of LST tie-breaking and laxity-zero thrashing, with "
        "verification kept separate from measurement",
        "هزینهٔ تساویشکنی LST و لرزشِ لَکسیَتی صفر، با جدا نگه داشتنِ بررسی "
        "از اندازهگیری",
        sweeps_fn=sweeps_fn, extra_figures_fn=extra_figures,
        extra_findings_fn=extra_findings, prefix="ex7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
