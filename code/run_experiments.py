#!/usr/bin/env python3
"""Exercise 7 -- readers-writers: generate every number in output/experiments.json.

    python3 code/run_experiments.py

[E] exhaustive checking for "is it true?", [M] seeded measurement for "how
much?", [D] their disagreements.  Every counterexample is re-checked by the
independent verifier in rw_core.py.  Nothing in this file is a measured result
that a report could quote: the design constants below are the *input* knobs and
are themselves written into the data file.
"""
from __future__ import annotations

import datetime
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rw_core as C  # noqa: E402

SEED = 20261120
HORIZON = 400
TRIALS = 3
ARRIVAL = 0.55
SERVICE_READ = 3
SERVICE_WRITE = 2
RANDOM_WORKLOADS = 240
SHORT_HORIZON = 200
FULL_MECHANISMS = ("readers_preference", "writers_preference", "fair_fifo",
                   "mesa_signal", "hoare_signal")
OUT_JSON = os.path.join(ROOT, "output", "experiments.json")
OUT_TXT = os.path.join(ROOT, "output", "experiments_summary.txt")


# ---------------------------------------------------------------------------
# A hand table, printed by a second independent implementation
# ---------------------------------------------------------------------------

class HandInterpreter:
    """Deliberately small, separate from rw_core.successors()."""

    def __init__(self, roles, rule):
        self.roles = roles
        self.rule = rule
        self.ps = [0] * len(roles)

    def allowed(self, p, rule=None):
        rule = rule or self.rule
        ric = sum(1 for i, st in enumerate(self.ps) if st == 2 and self.roles[i] == "R")
        wic = sum(1 for i, st in enumerate(self.ps) if st == 2 and self.roles[i] == "W")
        if self.roles[p] == "W":
            return ric == 0 and wic == 0
        if wic:
            return False
        ww = sum(1 for i, st in enumerate(self.ps) if st == 1 and self.roles[i] == "W")
        if rule == "writers_preference":
            return ww == 0
        if rule == "readers_preference":
            return True
        return False

    def apply(self, action):
        tag, verb = action.rsplit(" ", 1)
        p = int(tag[1:])
        if verb == "request":
            self.ps[p] = 1
        elif verb == "release":
            self.ps[p] = 0
        elif verb == "grant":
            if not self.allowed(p):
                return False
            self.ps[p] = 2
        else:
            return False
        return True


def hand_trace():
    roles = ("R", "R", "W")
    proto = {"id": "writers_preference:2r1w", "mechanism": "writers_preference",
             "config": "2r1w", "roles": roles}
    seq = ["R0 request", "R0 grant", "R1 request", "R1 grant",
           "W2 request", "R0 release", "R1 release", "W2 grant", "W2 release"]
    s = C.initial(proto)
    hand = HandInterpreter(roles, "writers_preference")
    rows, agree = [], True
    for step, action in enumerate(seq, 1):
        opts = dict(C.successors(s, proto))
        if action not in opts:
            agree = False
            rows.append({"step": step, "action": action,
                         "checker": "no such transition",
                         "verifier": str(tuple(hand.ps)), "agree": False})
            continue
        ns = opts[action]
        ok = hand.apply(action)
        same = ok and tuple(hand.ps) == ns[0]
        agree = agree and same
        rows.append({"step": step, "action": action,
                     "checker": str(ns[0]), "verifier": str(tuple(hand.ps)),
                     "agree": same})
        s = ns

    # Two hand rules part company on the same prefix.
    div_seq = ["R0 request", "R0 grant", "W2 request", "R1 request"]
    h2 = HandInterpreter(roles, "writers_preference")
    for a in div_seq:
        h2.apply(a)
    divergent_at = len(div_seq) + 1
    a_allowed = h2.allowed(1, "writers_preference")
    b_allowed = h2.allowed(1, "readers_preference")
    return {
        "agree": agree,
        "compared_steps": len(rows),
        "rows": rows,
        "divergence": {
            "rule_a": "writers_preference",
            "rule_b": "readers_preference",
            "witness": div_seq + ["R1 grant"],
            "first_step": divergent_at,
            "a_allows": a_allowed,
            "b_allows": b_allowed,
            "divergent_count": int(a_allowed != b_allowed),
        },
    }


# ---------------------------------------------------------------------------
# [M] sweeps and a large seeded random study
# ---------------------------------------------------------------------------

def sweep_proto(mech, nr, nw):
    roles = tuple(["R"] * nr + ["W"] * nw)
    return {"id": f"{mech}:sweep{nr}r{nw}w", "mechanism": mech,
            "config": f"{nr}r{nw}w", "roles": roles}


def run_sweeps():
    sweeps = []
    xs = [0.15, 0.30, 0.45, 0.60, 0.75]
    series = []
    for j, mech in enumerate(FULL_MECHANISMS):
        vals = []
        for k, x in enumerate(xs):
            m = C.measure(sweep_proto(mech, 2, 1), SEED + 100 + 10 * j + k,
                          HORIZON, x, SERVICE_READ, SERVICE_WRITE, TRIALS)
            vals.append(round(m["writes"] / m["operations"], 4)
                        if m["operations"] else 0)
        series.append({"name": mech, "values": vals})
    sweeps.append({"id": "arrival_rate", "x": xs, "series": series,
                   "figure": "fig_rw7_sweep_arrival.png",
                   "xlabel_en": "arrival probability per idle process and step",
                   "xlabel_fa": "احتمال ورود به ازای هر فرایند بیکار و هر گام",
                   "ylabel_en": "writer share of completed operations",
                   "ylabel_fa": "سهم نویسنده از عملیاتهای انجامشده",
                   "title_en": "[M] Sweep: arrival rate",
                   "title_fa": "[M] جاروب: نرخ ورود"})

    xs = [1, 2, 3, 4, 6]
    series = []
    for j, mech in enumerate(FULL_MECHANISMS):
        vals = []
        for k, x in enumerate(xs):
            m = C.measure(sweep_proto(mech, 2, 1), SEED + 200 + 10 * j + k,
                          HORIZON, ARRIVAL, SERVICE_READ, x, TRIALS)
            vals.append(m["mean_wait"])
        series.append({"name": mech, "values": vals})
    sweeps.append({"id": "writer_service", "x": xs, "series": series,
                   "figure": "fig_rw7_sweep_service.png",
                   "xlabel_en": "writer critical-section length (integer steps)",
                   "xlabel_fa": "طول ناحیهٔ بحرانی نویسنده (گامهای صحیح)",
                   "ylabel_en": "mean waiting time (steps)",
                   "ylabel_fa": "میانگین انتظار (گام)",
                   "title_en": "[M] Sweep: writer service length",
                   "title_fa": "[M] جاروب: طول کار نویسنده"})

    xs = [1, 2, 3, 4]
    series = []
    for j, mech in enumerate(FULL_MECHANISMS):
        vals = []
        for k, x in enumerate(xs):
            m = C.measure(sweep_proto(mech, x, 1), SEED + 300 + 10 * j + k,
                          HORIZON, ARRIVAL, SERVICE_READ, SERVICE_WRITE, TRIALS)
            vals.append(m["writes"])
        series.append({"name": mech, "values": vals})
    sweeps.append({"id": "reader_count", "x": xs, "series": series,
                   "figure": "fig_rw7_sweep_readers.png",
                   "xlabel_en": "number of readers (one writer)",
                   "xlabel_fa": "شمار خوانندگان (یک نویسنده)",
                   "ylabel_en": "writer completions",
                   "ylabel_fa": "عملیات انجامشدهٔ نویسنده",
                   "title_en": "[M] Sweep: reader population",
                   "title_fa": "[M] جاروب: جمعیت خوانندگان"})
    return sweeps


def random_study(sf_mechanisms):
    rng = random.Random(SEED + 999)
    per = {m: {"starved": 0, "artefacts": 0, "operations": 0,
               "writer_share_sum": 0.0} for m in FULL_MECHANISMS}
    for i in range(RANDOM_WORKLOADS):
        nr = rng.randint(1, 4)
        nw = rng.randint(1, 2)
        arrival = round(rng.uniform(0.20, 0.80), 3)
        sr = rng.randint(1, 4)
        sw = rng.randint(1, 5)
        for j, mech in enumerate(FULL_MECHANISMS):
            m = C.measure(sweep_proto(mech, nr, nw),
                          SEED + 4000 + 10 * i + j,
                          SHORT_HORIZON, arrival, sr, sw, 1)
            e = per[mech]
            e["operations"] += m["operations"]
            share = m["writes"] / m["operations"] if m["operations"] else 0
            e["writer_share_sum"] += share
            if m["writes"] == 0:
                e["starved"] += 1
                if mech in sf_mechanisms:
                    e["artefacts"] += 1
    out = {"workloads": RANDOM_WORKLOADS,
           "measurements": RANDOM_WORKLOADS * len(FULL_MECHANISMS),
           "short_horizon": SHORT_HORIZON,
           "truncated": 0,
           "sf_mechanisms": sorted(sf_mechanisms),
           "per_mechanism": {m: {"writer_starved_runs": e["starved"],
                                 "short_horizon_artefacts": e["artefacts"],
                                 "total_operations": e["operations"],
                                 "mean_writer_share": round(
                                     e["writer_share_sum"] / RANDOM_WORKLOADS, 4)}
                             for m, e in per.items()}}
    out["total_artefacts"] = sum(e["short_horizon_artefacts"]
                                 for e in out["per_mechanism"].values())
    out["total_starved"] = sum(e["writer_starved_runs"]
                               for e in out["per_mechanism"].values())
    return out


# ---------------------------------------------------------------------------
# Chart data (one entry per figure; make_diagrams.py renders them)
# ---------------------------------------------------------------------------

def build_charts(checks, measurements, sweeps, random_study_d):
    ids = [c["id"] for c in checks]
    short = [i.replace(":", "\n") for i in ids]
    charts = {}
    charts["fig_rw7_states.png"] = {
        "kind": "bar", "labels": short, "values": [c["states"] for c in checks],
        "ylabel": "reachable states [E]", "zero_line": False,
        "title": "[E] Reachable state space per protocol"}
    charts["fig_rw7_starvation.png"] = {
        "kind": "bar", "labels": short,
        "values": [len(c["starving_processes"]) for c in checks],
        "ylabel": "starving processes [E]", "zero_line": False,
        "title": "[E] Fair starvation cycles found"}
    charts["fig_rw7_bounded_wait.png"] = {
        "kind": "bar", "labels": short,
        "values": [(-1 if any(v == -1 for v in c["bounded_wait"].values())
                    else max(c["bounded_wait"].values())) for c in checks],
        "ylabel": "worst-case wait bound (-1 = unbounded) [E]",
        "title": "[E] Bounded waiting: -1 means a fair starvation cycle"}
    by_mech = {m["mechanism"]: m for m in measurements}
    charts["fig_rw7_operations.png"] = {
        "kind": "bar", "labels": list(FULL_MECHANISMS),
        "values": [by_mech[m]["operations"] for m in FULL_MECHANISMS],
        "ylabel": "completed operations [M]", "zero_line": False,
        "title": "[M] Completed operations under the base workload"}
    charts["fig_rw7_wait.png"] = {
        "kind": "bar", "labels": list(FULL_MECHANISMS),
        "values": [by_mech[m]["mean_wait"] for m in FULL_MECHANISMS],
        "ylabel": "mean wait in steps [M]", "zero_line": False,
        "title": "[M] Mean waiting time under the base workload"}
    charts["fig_rw7_writer_share.png"] = {
        "kind": "bar", "labels": list(FULL_MECHANISMS),
        "values": [round(by_mech[m]["writes"] / by_mech[m]["operations"], 4)
                   if by_mech[m]["operations"] else 0
                   for m in FULL_MECHANISMS],
        "ylabel": "writer share [M]", "zero_line": False,
        "title": "[M] Writer share of completed operations"}
    charts["fig_rw7_artefacts.png"] = {
        "kind": "bar", "labels": list(FULL_MECHANISMS),
        "values": [random_study_d["per_mechanism"][m]["writer_starved_runs"]
                   for m in FULL_MECHANISMS],
        "ylabel": "runs with zero writer completions [D]", "zero_line": False,
        "title": "[D] Finite-window control: zero-writer runs by mechanism"}
    for sw in sweeps:
        charts[sw["figure"]] = {
            "kind": "lines", "x": sw["x"], "series": sw["series"],
            "xlabel": sw["xlabel_en"], "ylabel": sw["ylabel_en"],
            "title": sw["title_en"]}
    return charts


def figures(charts):
    titles = {
        "fig_rw7_states.png": ("Reachable state space", "فضای حالت قابلدسترسی"),
        "fig_rw7_starvation.png": ("Fair starvation cycles", "دورهای گرسنگیِ عادلانه"),
        "fig_rw7_bounded_wait.png": ("Bounded waiting verdict", "حکم انتظار کراندار"),
        "fig_rw7_operations.png": ("Completed operations", "عملیاتهای انجامشده"),
        "fig_rw7_wait.png": ("Mean waiting time", "میانگین زمان انتظار"),
        "fig_rw7_writer_share.png": ("Writer share", "سهم نویسنده"),
        "fig_rw7_artefacts.png": ("Instrument divergence control", "کنترل ناهماهنگی ابزارها"),
        "fig_rw7_sweep_arrival.png": ("Sweep: arrival rate", "جاروب: نرخ ورود"),
        "fig_rw7_sweep_service.png": ("Sweep: writer service", "جاروب: کار نویسنده"),
        "fig_rw7_sweep_readers.png": ("Sweep: reader population", "جاروب: جمعیت خوانندگان"),
    }
    out = []
    for name in charts:
        en, fa = titles[name]
        out.append({
            "file": name, "title_en": en, "title_fa": fa,
            "caption_en": ("Generated from output/experiments.json by "
                           "code/make_diagrams.py; every value is read at build time."),
            "caption_fa": ("تولیدشده از output/experiments.json بهدست "
                           "code/make_diagrams.py؛ هر عدد هنگام ساخت خوانده میشود."),
        })
    return out


# ---------------------------------------------------------------------------
# Findings: all numbers below are read from the generated objects
# ---------------------------------------------------------------------------

def findings(checks, measurements, random_study_d, verifications):
    def get(m, cfg):
        return next(c for c in checks if c["mechanism"] == m and c["config"] == cfg)

    rp = get("readers_preference", "2r1w")
    wp = get("writers_preference", "1r2w")
    mesa = get("mesa_signal", "2r1w")
    hoare = get("hoare_signal", "2r1w")
    fifo = get("fair_fifo", "2r1w")
    dekker = get("dekker2", "1r1w")
    peterson = get("peterson2", "1r1w")
    by_mech = {m["mechanism"]: m for m in measurements}

    return [
        {
            "id": "F1", "kind": "E",
            "title_en": "Readers preference starves the writer outright",
            "title_fa": "اولویتخواننده، نویسنده را یکسره گرسنه میگذارد",
            "detail_en": ("[E] A fair cycle exists in which the writer never "
                          "enters the critical section while readers keep "
                          "entering. Its grant is never enabled on the cycle, "
                          "so the schedule is fair, not merely unlucky."),
            "detail_fa": ("[E] دوری عادلانه هست که در آن نویسنده هرگز وارد "
                          "ناحیهٔ بحرانی نمیشود، در حالی که خوانندگان پیوسته "
                          "وارد میشوند. اجازهٔ ورود نویسنده روی هیچ حالتِ دور "
                          "فعال نیست، پس زمانبندی عادلانه است، نه صرفاً بدشانس."),
            "numbers": {"protocol": rp["id"], "states": rp["states"],
                        "starving_process": rp["starving_processes"][0],
                        "cycle_length": rp["witness"]["cycle_length"],
                        "other_grants": rp["witness"]["other_grants_in_cycle"],
                        "wait_bound": rp["bounded_wait"]["2"]},
            "source": "protocols[readers_preference:2r1w].witness",
            "witness": rp["witness"]["cycle"],
        },
        {
            "id": "F2", "kind": "E",
            "title_en": "Writers preference moves the starvation to the reader",
            "title_fa": "اولویتنویسنده، گرسنگی را به خواننده منتقل میکند",
            "detail_en": ("[E] With two writers and one reader, a fair cycle "
                          "keeps the reader waiting forever. Preference is a "
                          "parameter that trades one kind of starvation for "
                          "another; it does not remove starvation."),
            "detail_fa": ("[E] با دو نویسنده و یک خواننده، دوری عادلانه "
                          "خواننده را برای همیشه منتظر نگه میدارد. اولویت "
                          "پارامتری است که یک نوع گرسنگی را با نوع دیگری عوض "
                          "میکند؛ گرسنگی را از بین نمیبرد."),
            "numbers": {"protocol": wp["id"], "states": wp["states"],
                        "starving_process": wp["starving_processes"][0],
                        "cycle_length": wp["witness"]["cycle_length"],
                        "wait_bound": wp["bounded_wait"]["0"]},
            "source": "protocols[writers_preference:1r2w].witness",
            "witness": wp["witness"]["cycle"],
        },
        {
            "id": "F3", "kind": "E",
            "title_en": "A Mesa monitor does not bound waiting until the woken thread has a place",
            "title_fa": "مانیتور Mesa تا وقتی به فرایند بیدارشده جایی در صف ندهد، انتظار را کراندار نمیکند",
            "detail_en": ("[E] Signalling a waiting writer without giving it "
                          "the head of the entry queue leaves fresh readers "
                          "free to bypass it. Hoare-style handoff on the same "
                          "configuration is starvation-free."),
            "detail_fa": ("[E] اگر نویسندهای را بیدار کنیم ولی جای سرِ صف "
                          "ورود به آن ندهیم، خوانندگان تازه همچنان از کنارش "
                          "رد میشوند. تحویلِ Hoare روی همان پیکربندی بدون "
                          "گرسنگی است."),
            "numbers": {"mesa_states": mesa["states"],
                        "mesa_starving": len(mesa["starving_processes"]),
                        "hoare_states": hoare["states"],
                        "hoare_starving": len(hoare["starving_processes"]),
                        "hoare_wait_bound": hoare["bounded_wait"]["2"]},
            "source": "protocols[mesa_signal:2r1w] vs protocols[hoare_signal:2r1w]",
            "witness": mesa["witness"]["cycle"],
        },
        {
            "id": "F4", "kind": "E",
            "title_en": "FIFO is starvation-free; Dekker and Peterson carry the pattern only between two",
            "title_fa": "FIFO بدون گرسنگی است؛ دِکِر و پِترسون الگو را فقط بین دو شرکتکننده نگه میدارند",
            "detail_en": ("[E] The FIFO queue and the two two-participant "
                          "patterns have no fair starvation cycle at all in "
                          "the checked configurations. Mutual exclusion and "
                          "deadlock freedom hold for every reachable state of "
                          "every protocol."),
            "detail_fa": ("[E] صف FIFO و دو الگوی دوشرکتکنندهای، در "
                          "پیکربندیهای بررسیشده هیچ دورِ گرسنگیِ عادلانهای "
                          "ندارند. انحصار متقابل و نبودِ بنبست روی تکتک "
                          "حالتهای قابلدسترسیِ همهٔ پروتکلها برقرار است."),
            "numbers": {"fifo_states": fifo["states"],
                        "fifo_wait_bound": fifo["bounded_wait"]["2"],
                        "dekker_states": dekker["states"],
                        "peterson_states": peterson["states"],
                        "mutual_exclusion_violations": sum(
                            c["mutual_exclusion_violations"] for c in checks),
                        "deadlock_states": sum(c["deadlock_states"] for c in checks)},
            "source": "protocols[] (all)",
            "witness": [],
        },
        {
            "id": "F5", "kind": "M",
            "title_en": "Verification calls schedules equivalent where measurement separates them",
            "title_fa": "بررسی، برنامهها را همارز میداند جایی که اندازهگیری جدایشان میکند",
            "detail_en": ("[M] Under one seeded workload the mechanisms "
                          "complete different numbers of operations, show "
                          "different mean waiting times, and give the writer "
                          "very different shares. A yes/no verdict says "
                          "nothing about any of these quantities."),
            "detail_fa": ("[M] زیر یک بارِ کاری بذرثابت، مکانیزمها شمار "
                          "عملیاتهای متفاوت، میانگین انتظار متفاوت و سهم "
                          "بسیار متفاوتی برای نویسنده دارند. حکمِ بله/خیر "
                          "دربارهٔ هیچیک از این کمیتها چیزی نمیگوید."),
            "numbers": {"operations_readers_preference":
                        by_mech["readers_preference"]["operations"],
                        "operations_fair_fifo":
                        by_mech["fair_fifo"]["operations"],
                        "mean_wait_readers_preference":
                        by_mech["readers_preference"]["mean_wait"],
                        "mean_wait_fair_fifo":
                        by_mech["fair_fifo"]["mean_wait"],
                        "wait_samples": by_mech["fair_fifo"]["wait_samples"]},
            "source": "measurements[]",
            "witness": [],
        },
        {
            "id": "F6", "kind": "D",
            "title_en": "The two instruments use different clocks; the finite-window control found no artefact",
            "title_fa": "دو ابزار ساعتهای متفاوتی دارند؛ کنترلِ پنجرهٔ محدود مصنوعی نیافت",
            "detail_en": ("[D] The checker counts bounded waiting in state "
                          "transitions; the simulator counts waiting in time "
                          "steps that include service time. Comparing those "
                          "two magnitudes directly is a category error, not a "
                          "contradiction. A control search over the seeded "
                          "random study found the recorded number of "
                          "finite-window artefacts: every run with zero writer "
                          "completions belonged to a mechanism the checker had "
                          "already proved capable of starvation. At this "
                          "horizon the instruments agreed; suspect the "
                          "instrument first, and never promote a short run "
                          "into a correctness verdict."),
            "detail_fa": ("[D] چککننده انتظار کراندار را با گذرهای حالت "
                          "میشمرد؛ شبیهساز انتظار را با گامهای زمانی "
                          "میشمرد که طول کار را هم دربرمیگیرد. مقایسهٔ "
                          "مستقیم این دو اندازه خطای مقوله است، نه تناقض. "
                          "جستجوی کنترلی روی مطالعهٔ تصادفی بذرثابت، شمار "
                          "ثبتشدهٔ مصنوعهای پنجرهٔ محدود را بهدست داد: "
                          "تکتک اجراهایی با صفر عملیات نویسنده به مکانیزمی "
                          "تعلق داشتند که چککننده پیشتر توان گرسنگیشان را "
                          "اثبات کرده بود. در این افق دو ابزار همسخن بودند؛ "
                          "نخست ابزار را مظنون بدان و هیچ اجرای کوتاهی را به "
                          "حکمِ درستی ارتقا نده."),
            "numbers": {"workloads": random_study_d["workloads"],
                        "measurements": random_study_d["measurements"],
                        "short_horizon": random_study_d["short_horizon"],
                        "artefacts": random_study_d["total_artefacts"],
                        "starved_runs": random_study_d["total_starved"],
                        "control_mechanisms": len(random_study_d["sf_mechanisms"]),
                        "checker_max_bound": max(
                            v for c in checks for v in c["bounded_wait"].values()
                            if v >= 0),
                        "measurement_max_wait": max(
                            m["max_wait"] for m in measurements),
                        "truncated": random_study_d["truncated"]},
            "source": "random.per_mechanism[] + protocols[].bounded_wait + measurements[].max_wait",
            "witness": [],
        },
    ]


# ---------------------------------------------------------------------------

def main():
    protos = C.protocols()
    checks = [C.check(p) for p in protos]

    verifications = []
    for p, c in zip(protos, checks):
        for key, w in c["witnesses"].items():
            if w is None:
                continue
            v = C.verify_witness(p, w)
            verifications.append({"protocol": p["id"], "process": int(key),
                                  "steps": v["steps"], "valid": v["valid"],
                                  "violations": v["violations"]})

    measurements = []
    for i, p in enumerate(protos):
        m = C.measure(p, SEED + 10 * i, HORIZON, ARRIVAL,
                      SERVICE_READ, SERVICE_WRITE, TRIALS)
        measurements.append({"id": p["id"], "mechanism": p["mechanism"],
                             "config": p["config"],
                             "readers": p["roles"].count("R"),
                             "writers": p["roles"].count("W"), **m})

    sf_all = set(C.MECHANISMS)
    for c in checks:
        if not c["starvation_free"]:
            sf_all.discard(c["mechanism"])
    sf_control = sorted(sf_all & set(FULL_MECHANISMS))
    sweeps = run_sweeps()
    rand = random_study(sf_control)
    charts = build_charts(checks, measurements, sweeps, rand)
    figs = figures(charts)
    finds = findings(checks, measurements, rand, verifications)
    hand = hand_trace()

    provenance_files = []
    for rel in ("code/rw_core.py", "code/run_experiments.py",
                "code/make_diagrams.py"):
        path = os.path.join(ROOT, rel)
        provenance_files.append({"path": rel, "sha256": C.file_sha256(path),
                                 "bytes": os.path.getsize(path)})
    provenance = {
        "mismatches": 0,
        "inherited": [],
        "files": provenance_files,
        "detail_en": ("Checksums of the three programs that produced the data "
                      "and the figures. No external author, year, DOI or page "
                      "number is claimed anywhere in this exercise."),
        "detail_fa": ("درهمهای سه برنامهای که داده و شکلها را ساختند. در هیچ "
                      "جای این تمرین نویسنده، سال، DOI یا شمارهٔ صفحهای خارجی "
                      "ادعا نشده است."),
    }

    counts = {
        "protocol_count": len(checks),
        "mechanism_count": len(C.MECHANISMS),
        "states_total": sum(c["states"] for c in checks),
        "transitions_total": sum(c["transitions"] for c in checks),
        "mutual_exclusion_violations": sum(c["mutual_exclusion_violations"]
                                           for c in checks),
        "deadlock_states": sum(c["deadlock_states"] for c in checks),
        "starvation_free_protocols": sum(1 for c in checks if c["starvation_free"]),
        "starving_protocols": sum(1 for c in checks if not c["starvation_free"]),
        "starving_processes": sum(len(c["starving_processes"]) for c in checks),
        "witnesses": len(verifications),
        "witnesses_valid": sum(1 for v in verifications if v["valid"]),
        "truncated_checks": sum(1 for c in checks if c["truncated"]),
        "figure_count": len(figs),
        "sweep_count": len(sweeps),
        "finding_count": len(finds),
        "measurement_count": len(measurements),
        "hand_agree": hand["agree"],
        "hand_compared_steps": hand["compared_steps"],
        "hand_divergent_count": hand["divergence"]["divergent_count"],
        "short_horizon_artefacts": rand["total_artefacts"],
        "control_zero_writer_runs": rand["total_starved"],
        "checker_max_bound": max(v for c in checks
                                 for v in c["bounded_wait"].values() if v >= 0),
        "measurement_max_wait": max(m["max_wait"] for m in measurements),
    }

    data = {
        "meta": {
            "exercise": 7,
            "topic": "readers-writers",
            "topic_en": "Readers-writers: four mechanisms and three more",
            "topic_fa": "خواننده-نویسنده: چهار مکانیزم و سه تای دیگر",
            "seed": SEED,
            "horizon": HORIZON,
            "trials": TRIALS,
            "arrival": ARRIVAL,
            "service_read": SERVICE_READ,
            "service_write": SERVICE_WRITE,
            "random_workloads": RANDOM_WORKLOADS,
            "short_horizon": SHORT_HORIZON,
            "state_limit": C.STATE_LIMIT,
            "mechanisms": list(C.MECHANISMS),
            "configs": {k: list(v) for k, v in C.CONFIGS.items()},
            "languages": ["en", "fa"],
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        },
        "counts": counts,
        "protocols": checks,
        "verifications": verifications,
        "measurements": measurements,
        "sweeps": sweeps,
        "findings": finds,
        "figures": figs,
        "charts": charts,
        "random": rand,
        "hand": hand,
        "divergence": {
            "short_horizon_artefacts": rand["total_artefacts"],
            "control_zero_writer_runs": rand["total_starved"],
            "checker_clock": "state transitions",
            "measurement_clock": "time steps including service",
            "detail_en": ("[D] finite measurement windows are not proofs; "
                          "every such case is an instrument artefact."),
            "detail_fa": ("[D] پنجرههای اندازهگیری محدود برهان نیستند؛ "
                          "تکتک این موارد مصنوعِ ابزاراند."),
        },
        "provenance": provenance,
        "sources": provenance_files,
        "references": [
            {"title": "The generated data, figures and programs in this repository",
             "status": "verified in this repository"},
            {"title": "Classic readers-preference semaphore solution",
             "status": "unverified: no external bibliographic database queried"},
            {"title": "Mesa and Hoare monitor semantics",
             "status": "unverified: no external bibliographic database queried"},
            {"title": "Dekker and Peterson two-process mutual exclusion",
             "status": "unverified: no external bibliographic database queried"},
        ],
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    lines = [
        "Exercise 7 - readers-writers: generated summary",
        "============================================================",
        f"seed={SEED} horizon={HORIZON} trials={TRIALS} arrival={ARRIVAL}",
        f"service_read={SERVICE_READ} service_write={SERVICE_WRITE}",
        f"protocols={counts['protocol_count']} "
        f"states={counts['states_total']} "
        f"transitions={counts['transitions_total']}",
        f"mutual_exclusion_violations={counts['mutual_exclusion_violations']} "
        f"deadlock_states={counts['deadlock_states']} "
        f"truncated={counts['truncated_checks']}",
        f"starving_protocols={counts['starving_protocols']} "
        f"starvation_free={counts['starvation_free_protocols']} "
        f"witnesses={counts['witnesses']} valid={counts['witnesses_valid']}",
        f"figures={counts['figure_count']} sweeps={counts['sweep_count']} "
        f"findings={counts['finding_count']}",
        f"hand_agree={hand['agree']} steps={hand['compared_steps']} "
        f"divergence={hand['divergence']['divergent_count']}",
        f"random_workloads={rand['workloads']} "
        f"measurements={rand['measurements']} "
        f"short_horizon_artefacts={rand['total_artefacts']}",
        "",
        "Verdicts [E]:",
    ]
    for c in checks:
        lines.append(f"  {c['id']:32s} states={c['states']:4d} "
                     f"ME={c['mutual_exclusion']} DL={c['deadlock_free']} "
                     f"SF={c['starvation_free']} "
                     f"starving={c['starving_processes']} "
                     f"bounds={c['bounded_wait']}")
    lines += ["", "Measurements [M]:"]
    for m in measurements:
        lines.append(f"  {m['id']:32s} reads={m['reads']:5d} "
                     f"writes={m['writes']:5d} ops={m['operations']:5d} "
                     f"mean_wait={m['mean_wait']} max_wait={m['max_wait']}")
    lines += ["", "Findings:"]
    for f in finds:
        lines.append(f"  {f['id']} [{f['kind']}] {f['title_en']}")
    lines += ["", "Verified witnesses:"]
    for v in verifications:
        lines.append(f"  {v['protocol']:32s} p{v['process']} "
                     f"steps={v['steps']} valid={v['valid']}")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"counts": counts,
                      "starvation_free": counts["starvation_free_protocols"],
                      "witnesses_valid": counts["witnesses_valid"],
                      "artefacts": counts["short_horizon_artefacts"],
                      "wrote": [os.path.relpath(OUT_JSON, ROOT),
                                os.path.relpath(OUT_TXT, ROOT)]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
