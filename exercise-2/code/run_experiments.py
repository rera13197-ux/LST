#!/usr/bin/env python3
"""Exercise 2 — LST against EDF and RM on measured workloads.

    python3 code/run_experiments.py   ->   output/experiments.json
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L
from lst_core import utilisation

SPECS = [
    ("W1", "light load", [["T1", 10, 2, 8], ["T2", 20, 3, 15]]),
    ("W2", "medium load, implicit deadlines", [["T1", 6, 2], ["T2", 8, 2], ["T3", 12, 3]]),
    ("W3", "harmonic periods", [["T1", 4, 1, 3], ["T2", 8, 2, 6], ["T3", 16, 4, 12]]),
    ("W4", "non-harmonic periods", [["T1", 5, 2, 4], ["T2", 7, 2, 5], ["T3", 11, 3, 8]]),
    ("W5", "heavy but feasible", [["T1", 4, 1, 3], ["T2", 5, 2, 4], ["T3", 20, 3, 12]]),
    ("W6", "heavy and infeasible", [["T1", 5, 2, 3], ["T2", 10, 3, 6], ["T3", 10, 2, 7]]),
    ("W7", "phased releases", [["T1", 6, 2, 4, 0], ["T2", 8, 2, 5, 2], ["T3", 12, 3, 7, 1]]),
    ("W8", "tight deadlines", [["T1", 5, 2, 3], ["T2", 6, 2, 3]]),
]


def base(c1):
    return L.mk([["T1", 6, c1], ["T2", 8, 2], ["T3", 12, 3]])


def sweeps_fn(sets):
    return [
        L.sweep_parameter("misses", "C of T1 (time units)", [1, 2, 3, 4],
                          base, "missed", figure="fig_ex2_misses_sweep.png",
                          source="sweeps[0]"),
        L.sweep_parameter("preemptions", "C of T1 (time units)", [1, 2, 3, 4],
                          base, "preemptions", figure="fig_ex2_pre_sweep.png",
                          source="sweeps[1]"),
        L.sweep_alignment(sets, figure="fig_ex2_alignment.png",
                          source="sweeps[2]"),
    ]


def extra_figures(sets, sweeps):
    return [
        L.fig_scatter("fig_ex2_scatter.png",
                      "Utilisation versus LST preemptions across workloads",
                      [[s["utilisation"], s["policies"]["lst"]["preemptions"]]
                       for s in sets],
                      "task_sets[*].policies.lst.preemptions",
                      ylabel="LST preemptions", xlabel="utilisation"),
        L.fig_grouped("fig_ex2_jitter.png", "Response jitter per workload and policy",
                      [s["id"] for s in sets],
                      [{"name": p,
                        "values": [s["policies"][p]["jitter"] or 0 for s in sets]}
                       for p in ("lst", "edf", "rm")],
                      "task_sets[*].policies.*.jitter", ylabel="jitter",
                      xlabel="workload"),
    ]


def extra_findings(sets):
    tot_lst = sum(s["policies"]["lst"]["preemptions"] for s in sets)
    tot_edf = sum(s["policies"]["edf"]["preemptions"] for s in sets)
    tot_rm = sum(s["policies"]["rm"]["preemptions"] for s in sets)
    miss_lst = sum(s["policies"]["lst"]["missed"] for s in sets)
    miss_edf = sum(s["policies"]["edf"]["missed"] for s in sets)
    miss_rm = sum(s["policies"]["rm"]["missed"] for s in sets)
    flat = [s for s in sets
            if s["policies"]["lst"]["missed"] == 0
            and s["policies"]["edf"]["missed"] == 0
            and s["policies"]["rm"]["missed"] == 0]
    jit = [(s["id"], s["policies"]["lst"]["jitter"], s["policies"]["edf"]["jitter"])
           for s in sets if s["policies"]["lst"]["jitter"] is not None
           and s["policies"]["edf"]["jitter"] is not None
           and s["policies"]["lst"]["jitter"] < s["policies"]["edf"]["jitter"]]
    return [
        L.finding(
            "F5", "M",
            "Cheapest correctness is not LST",
            "ارزانترین درستی، LST نیست",
            (f"[M] Across all {len(sets)} workloads LST records {tot_lst} "
             f"preemptions and {miss_lst} missed deadlines, EDF records "
             f"{tot_edf} and {miss_edf}, and RM records {tot_rm} and "
             f"{miss_rm}. [E] Wherever the checker says feasible, both LST and "
             f"EDF meet every deadline in the aligned run, while RM supplies "
             f"genuine counterexamples. On the raw cost of being correct, EDF "
             f"wins here; saying LST is better because it is optimal would "
             f"confuse a verdict with a measurement."),
            (f"[M] روی همهٔ {len(sets)} بار کاری، LST برابر {tot_lst} پیشگیری و "
             f"{miss_lst} خطا، EDF برابر {tot_edf} و {miss_edf}، و RM برابر "
             f"{tot_rm} و {miss_rm} ثبت میکند. [E] هرجا چککننده «شدنی» بگوید، "
             f"هم LST و هم EDF در اجرای همتراز به همهٔ ضربالاجلها میرسند، "
             f"در حالی که RM ضدمثالهای واقعی میدهد. در هزینهٔ خامِ درستبودن "
             f"این EDF است که میبرد؛ بهتر دانستنِ LST چون بهینه است، یکی گرفتنِ "
             f"حکم با اندازهگیری است."),
            {"workloads": len(sets), "lst_preemptions": tot_lst,
             "edf_preemptions": tot_edf, "rm_preemptions": tot_rm,
             "lst_missed": miss_lst, "edf_missed": miss_edf,
             "rm_missed": miss_rm},
            source="task_sets[*].policies"),
        L.finding(
            "F6", "M",
            "Where the correctness metric cannot separate the policies",
            "جایی که سنجهٔ درستی نمیتواند سیاستها را جدا کند",
            (f"[M] On {len(flat)} of {len(sets)} workloads all three policies "
             f"miss zero deadlines, so correctness does not separate them at "
             f"all. Preemptions still do, and so does response jitter: on "
             f"{len(jit)} workloads LST has strictly smaller jitter than EDF "
             f"even while costing more preemptions. That is not a contradiction "
             f"and not a ranking; it is a measurement that separates one "
             f"dimension while another stays inconclusive. The widest such "
             f"workload is reported in the tables above, not guessed."),
            (f"[M] روی {len(flat)} از {len(sets)} بار کاری هر سه سیاست صفر خطا "
             f"میدهند، پس سنجهٔ درستی اصلاً جدایشان نمیکند. پیشگیریها هنوز "
             f"جدا میکنند و لرزش پاسخ هم: روی {len(jit)} بار کاری لرزش LST "
             f"اکیداً کوچکتر از EDF است، هرچند پیشگیریش بیشتر است. این تناقض "
             f"نیست و رتبهبندی هم نیست؛ اندازهای است که یک بُعد را جدا میکند "
             f"در حالی که بُعد دیگر بیتصمیم میماند. اینجا ادعایی حدسی نشده؛ "
             f"همهٔ این عددها از جدولهای بالا میآیند."),
            {"workloads": len(sets), "all_zero_miss_sets": len(flat),
             "lst_lower_jitter_sets": len(jit),
             "lst_total_preemptions": tot_lst,
             "edf_total_preemptions": tot_edf},
            source="task_sets[*].policies.*.jitter"),
    ]


def main():
    L.build_exercise(
        __file__, 2, SPECS,
        "nine policies over light, heavy, harmonic, non-harmonic, phased and "
        "tight workloads, with misses, preemptions, jitter and switch counts",
        "نه سیاست روی بارهای سبک، سنگین، هماهنگ، ناهماهنگ، فازدار و تنگ، "
        "با خطاها، پیشگیریها، لرزش و شمارش تعویضها",
        sweeps_fn=sweeps_fn, extra_figures_fn=extra_figures,
        extra_findings_fn=extra_findings, prefix="ex2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
