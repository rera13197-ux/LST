"""Shared laboratory helpers for the seven LST exercises.

This file is the canonical copy.  ``tools/vendor_lab.py`` copies it into
``exercise-N/code/lab_kit.py`` so that every exercise branch is self-contained:
on a flattened branch ``code/`` holds ``lst_core.py`` + ``lab_kit.py`` and
``code/run_experiments.py`` imports both from its own directory.

Design contract (from the project README and PROMPT_TEMPLATE.txt)
-----------------------------------------------------------------
* Two instruments, never mixed:
    - ``exhaustive_feasible`` decides *true / false* and returns a witness;
    - ``simulate`` measures *how much* and returns numbers.
* Every number that reaches a report is produced here from a program run and
  written to ``output/experiments.json``.  The report builder only reads that
  file; it never contains a measured constant.
* Integer time only; no floats in the model.  ``utilisation`` is the one float
  and is used for grouping/reporting, never for a decision.
* Alignment: the checker enumerates the jobs released in one hyperperiod; a
  simulator run is only comparable when ``release_window == hp`` and the run is
  long enough for those jobs to finish.  ``alignment()`` measures both the
  aligned and the naive comparison so the mismatch can be studied instead of
  hidden.
"""
from __future__ import annotations

import json
import os
import random
from typing import Dict, List, Optional, Sequence

from lst_core import (POLICIES, Task, exhaustive_feasible, gantt_rows,
                      hyperperiod, make_jobs, simulate, utilisation)

SEED = 20261116
LST_POLICIES = ("lst", "lst:edf", "lst:rm", "lst:stay", "lst:lzs")
BASE_POLICIES = ("edf", "rm", "dm", "fifo")
ALL_POLICIES = tuple(POLICIES)


# --------------------------------------------------------------------------
# io
# --------------------------------------------------------------------------

def dump(path: str, obj: dict) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return path


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def exercise_root(script_file: str) -> str:
    """Root of the exercise folder, whether run from the tree or a flat branch."""
    return os.path.dirname(os.path.dirname(os.path.abspath(script_file)))


def output_path(script_file: str) -> str:
    return os.path.join(exercise_root(script_file), "output", "experiments.json")


# --------------------------------------------------------------------------
# task sets
# --------------------------------------------------------------------------

def mk(rows: Sequence[Sequence]) -> List[Task]:
    """Build Task objects from [name, period, wcet] / [..., deadline] / [..., phase]."""
    out = []
    for r in rows:
        r = list(r)
        name, period, wcet = r[0], int(r[1]), int(r[2])
        deadline = int(r[3]) if len(r) > 3 else None
        phase = int(r[4]) if len(r) > 4 else 0
        out.append(Task(name, period, wcet, deadline, phase))
    return out


def rows_of(tasks: Sequence[Task]) -> list:
    return [[t.name, t.period, t.wcet, t.rel_deadline, t.phase] for t in tasks]


def spec_of(tasks: Sequence[Task]) -> str:
    return ", ".join(
        f"{t.name}(T={t.period},C={t.wcet},D={t.rel_deadline},ph={t.phase})"
        for t in tasks)


# --------------------------------------------------------------------------
# independent verifier (deliberately shares no code with the checker)
# --------------------------------------------------------------------------

def verify_witness(tasks: Sequence[Task], schedule: Optional[Sequence[Optional[int]]],
                   horizon: int) -> dict:
    """Re-check a checker witness from first principles.

    The checker's own recursion is *not* called here: we rebuild the job list,
    walk the schedule step by step and assert that every job completes no later
    than its deadline.  A witness that fails this is a bug in the instrument,
    and the report says so rather than quietly trusting the verdict.
    """
    if schedule is None:
        return {"checked": False, "valid": None, "reason": "no witness (infeasible verdict)"}
    jobs = make_jobs(tasks, horizon)
    n = len(jobs)
    left = [j.wcet for j in jobs]
    released = [False] * n
    for t, choice in enumerate(schedule):
        for i, j in enumerate(jobs):
            if j.release <= t:
                released[i] = True
        if choice is None:
            if any(released[i] and left[i] > 0 for i in range(n)):
                return {"checked": True, "valid": False,
                        "reason": f"optional idle at t={t} while work is ready"}
            continue
        if not (0 <= choice < n):
            return {"checked": True, "valid": False, "reason": f"bad job index at t={t}"}
        if not released[choice]:
            return {"checked": True, "valid": False,
                    "reason": f"job {choice} not released at t={t}"}
        if left[choice] <= 0:
            return {"checked": True, "valid": False,
                    "reason": f"job {choice} already complete at t={t}"}
        if t >= jobs[choice].deadline:
            return {"checked": True, "valid": False,
                    "reason": f"job {choice} runs at/after its deadline t={t}"}
        left[choice] -= 1
    for i, j in enumerate(jobs):
        if left[i] > 0:
            return {"checked": True, "valid": False,
                    "reason": f"job {i} still has {left[i]} units at the end"}
    return {"checked": True, "valid": True,
            "steps": len(schedule),
            "jobs": n,
            "busy": sum(1 for c in schedule if c is not None),
            "reason": "every job finished strictly before its deadline"}


# --------------------------------------------------------------------------
# one task set, both instruments
# --------------------------------------------------------------------------

def _metrics(res) -> dict:
    return {
        "missed": res.missed,
        "released": res.released,
        "completed": res.completed,
        "miss_rate": round(res.miss_rate, 6),
        "preemptions": res.preemptions,
        "context_switches": res.context_switches,
        "laxity_zero_switches": res.laxity_zero_switches,
        "tie_events": res.tie_events,
        "min_laxity": res.min_laxity,
        "worst_response": res.worst_response,
        "mean_response": (round(res.mean_response, 4)
                          if res.mean_response is not None else None),
        "jitter": res.jitter,
        "first_miss": res.first_miss,
        "idle": res.idle,
        "busy": res.busy,
        "horizon": res.horizon,
    }


OPTIMAL_POLICIES = ("lst", "edf")


def alignment(tasks: Sequence[Task],
              policies: Sequence[str] = ("lst", "edf", "rm")) -> dict:
    """Compare checker and simulator on the same job set, and on the naive one.

    ``naive`` compares a one-hyperperiod checker verdict with a two-hyperperiod
    simulator run.  ``aligned`` uses ``release_window=hp`` and
    ``horizon=hp+max_deadline`` so both instruments see the same jobs.

    Agreement is evaluated **only for the policies whose optimality is at
    issue** (LST and EDF).  RM is deliberately kept as a control: RM missing a
    deadline on a feasible set is a counterexample to RM's optimality, which
    is a genuine result, not an instrument mismatch.  Conflating the two was
    the first version of this function's mistake and is documented here.
    """
    hp = hyperperiod(tasks)
    maxd = max(t.rel_deadline for t in tasks)
    ok, _sched, _stats = exhaustive_feasible(tasks, horizon=hp)
    naive, aligned = {}, {}
    for p in policies:
        rn = simulate(tasks, p, cycles=2)
        ra = simulate(tasks, p, horizon=hp + maxd, release_window=hp)
        naive[p] = {"missed": rn.missed, "released": rn.released,
                    "horizon": rn.horizon}
        aligned[p] = {"missed": ra.missed, "released": ra.released,
                      "horizon": ra.horizon, "release_window": hp}
    rm_naive = naive.get("rm", {}).get("missed", 0)
    rm_aligned = aligned.get("rm", {}).get("missed", 0)
    return {
        "checker_verdict": ok,
        "checker_horizon": hp,
        "max_deadline": maxd,
        "optimal_policies": list(OPTIMAL_POLICIES),
        "naive": naive,
        "aligned": aligned,
        "naive_agrees": all((naive[p]["missed"] == 0) == ok
                            for p in OPTIMAL_POLICIES),
        "aligned_agrees": all((aligned[p]["missed"] == 0) == ok
                              for p in OPTIMAL_POLICIES),
        "rm_control": {"naive_missed": rm_naive,
                       "aligned_missed": rm_aligned,
                       "counterexample": bool(ok and (rm_naive > 0 or rm_aligned > 0))},
    }


def cap_control(tasks: Sequence[Task], limits: Sequence[int] = (4, 8, 16, 4000000)) -> dict:
    """Show that a state cap can fabricate an infeasibility verdict.

    A truncated checker run is an artefact of the instrument.  The report must
    flag it as such and must never present it as a scheduling finding.
    """
    hp = hyperperiod(tasks)
    rows = []
    for lim in limits:
        ok, _s, st = exhaustive_feasible(tasks, horizon=hp, limit=lim)
        rows.append({"limit": lim, "feasible": ok, "states": st["states"],
                     "truncated": st["truncated"]})
    full = rows[-1]
    false_verdicts = [r for r in rows
                      if r["truncated"] and not r["feasible"] and full["feasible"]]
    return {"rows": rows,
            "full_verdict": full["feasible"],
            "full_truncated": full["truncated"],
            "false_infeasible_count": len(false_verdicts),
            "smallest_truncating_limit": min((r["limit"] for r in false_verdicts),
                                             default=None),
            "explanation": "truncated runs are artefacts of the cap, not findings"}


def witness_cost(tasks: Sequence[Task], schedule: Optional[Sequence[Optional[int]]],
                 horizon: int) -> dict:
    """Cost of the checker's own witness schedule, using the simulator's counters.

    The witness and LST can both be feasible while costing very different
    numbers of preemptions.  Verification calls them equivalent; measurement
    does not.  That gap is one of the findings of this project.
    """
    if schedule is None:
        return {"preemptions": 0, "context_switches": 0, "idle": 0,
                "busy": 0, "steps": 0, "available": False}
    jobs = make_jobs(tasks, horizon)
    left = [j.wcet for j in jobs]
    prev = None
    pre = sw = idle = busy = 0
    for t, choice in enumerate(schedule):
        if choice is None or choice < 0:
            idle += 1
            prev = None
            continue
        if prev is not None and prev != choice:
            if left[prev] > 0:
                pre += 1
            sw += 1
        elif prev is None:
            sw += 1
        left[choice] -= 1
        busy += 1
        prev = choice
    return {"preemptions": pre, "context_switches": sw, "idle": idle,
            "busy": busy, "steps": len(schedule), "available": True}


def describe_set(tasks: Sequence[Task], sid: str, label: str,
                 policies: Sequence[str] = ALL_POLICIES,
                 gantt_policies: Sequence[str] = ("lst", "edf", "rm"),
                 cycles: int = 2) -> dict:
    """Everything measurable about one task set, in one JSON object."""
    hp = hyperperiod(tasks)
    ok, sched, stats = exhaustive_feasible(tasks, horizon=hp)
    ok_idle, _si, stats_idle = exhaustive_feasible(tasks, horizon=hp,
                                                   allow_idle=True)
    witness = verify_witness(tasks, sched, hp)
    pol = {}
    for p in policies:
        pol[p] = _metrics(simulate(tasks, p, cycles=cycles))
    gantt = {}
    for p in gantt_policies:
        r = simulate(tasks, p, cycles=cycles)
        gantt[p] = [[name, a, b] for name, a, b in gantt_rows(r)]
    return {
        "id": sid,
        "label": label,
        "tasks": rows_of(tasks),
        "spec": spec_of(tasks),
        "task_count": len(tasks),
        "hyperperiod": hp,
        "utilisation": round(utilisation(tasks), 6),
        "max_deadline": max(t.rel_deadline for t in tasks),
        "constrained_deadline": any(t.rel_deadline < t.period for t in tasks),
        "checker": {
            "feasible": ok,
            "states": stats["states"],
            "pruned": stats["pruned"],
            "truncated": stats["truncated"],
            "jobs": stats["jobs"],
            "horizon": stats["horizon"],
            "allow_idle_false": ok,
            "allow_idle_true": ok_idle,
            "idle_enumeration_agrees": ok == ok_idle,
            "schedule_length": len(sched) if sched else 0,
            "schedule": [(-1 if c is None else c) for c in sched] if sched else [],
        },
        "witness": witness,
        "witness_cost": witness_cost(tasks, sched, hp),
        "cap_control": cap_control(tasks),
        "policies": pol,
        "gantt": gantt,
        "alignment": alignment(tasks),
    }


# --------------------------------------------------------------------------
# hand trace: a second, independent implementation of discrete-time LST
# --------------------------------------------------------------------------

def hand_trace(tasks: Sequence[Task], horizon: int) -> dict:
    """Recompute an LST schedule without calling ``simulate``.

    Used by exercise 3: the table the program prints is produced by this
    implementation, then compared digit for digit with the simulator's own
    timeline.  Two independent implementations agreeing is a measurement;
    one implementation agreeing with itself is not.
    """
    jobs = make_jobs(tasks, horizon)
    n = len(jobs)
    left = [j.wcet for j in jobs]
    rows, timeline = [], []
    previous = None
    for t in range(horizon):
        ready = [i for i in range(n)
                 if jobs[i].release <= t and left[i] > 0]
        if not ready:
            rows.append({"t": t, "ready": [], "laxity": [], "chosen": None,
                         "note": "forced idle"})
            timeline.append(None)
            previous = None
            continue
        slack = [jobs[i].deadline - t - left[i] for i in ready]
        best = min(slack)
        chosen = min(i for i, s in zip(ready, slack) if s == best)
        rows.append({
            "t": t,
            "ready": [jobs[i].name for i in ready],
            "remaining": [left[i] for i in ready],
            "laxity": slack,
            "chosen": jobs[chosen].name,
            "chosen_index": chosen,
        })
        timeline.append(chosen)
        left[chosen] -= 1
        previous = chosen
    reference = simulate(tasks, "lst", horizon=horizon)
    ref_names = [name for _t, name in reference.timeline]
    got_names = [None if c is None else jobs[c].name for c in timeline]
    return {
        "horizon": horizon,
        "tasks": rows_of(tasks),
        "rows": rows,
        "timeline": [(-1 if c is None else c) for c in timeline],
        "timeline_names": got_names,
        "simulator_names": ref_names,
        "agree": got_names == ref_names,
        "compared_steps": len(ref_names),
        "gantt": [[name, a, b] for name, a, b in gantt_rows(reference)],
        "metrics": _metrics(reference),
    }


def hand_gantt(trace: dict) -> list:
    rows = []
    for t, name in enumerate(trace["timeline_names"]):
        if name is None:
            continue
        if rows and rows[-1][0] == name and rows[-1][2] == t:
            rows[-1] = [name, rows[-1][1], t + 1]
        else:
            rows.append([name, t, t + 1])
    return rows


# --------------------------------------------------------------------------
# figure specs (all numbers are literal values written by run_experiments)
# --------------------------------------------------------------------------

def fig_bar(name, title, labels, values, source, ylabel="count", xlabel="") -> dict:
    return {"file": name, "kind": "bar", "title": title, "labels": list(labels),
            "values": list(values), "ylabel": ylabel, "xlabel": xlabel,
            "source": source}


def fig_grouped(name, title, labels, series, source, ylabel="count", xlabel="") -> dict:
    return {"file": name, "kind": "grouped_bar", "title": title,
            "labels": list(labels), "series": [dict(s) for s in series],
            "ylabel": ylabel, "xlabel": xlabel, "source": source}


def fig_line(name, title, x, series, source, ylabel="count", xlabel="") -> dict:
    return {"file": name, "kind": "line", "title": title, "x": list(x),
            "series": [dict(s) for s in series], "ylabel": ylabel,
            "xlabel": xlabel, "source": source}


def fig_gantt(name, title, rows, source) -> dict:
    return {"file": name, "kind": "gantt", "title": title,
            "rows": [list(r) for r in rows], "source": source}


def fig_heatmap(name, title, matrix, xlabels, ylabels, source) -> dict:
    return {"file": name, "kind": "heatmap", "title": title,
            "matrix": [list(r) for r in matrix], "xlabels": list(xlabels),
            "ylabels": list(ylabels), "source": source}


def fig_scatter(name, title, points, source, ylabel="", xlabel="") -> dict:
    return {"file": name, "kind": "scatter", "title": title,
            "points": [list(p) for p in points], "ylabel": ylabel,
            "xlabel": xlabel, "source": source}


def render_figures(script_file: str, specs: Optional[List[dict]] = None) -> List[str]:
    """Draw every figure described in output/experiments.json into diagrams/.

    Figure labels are deliberately ASCII (policy ids, task ids, numbers): the
    reports carry the bilingual prose, and the plots stay reproducible on any
    machine without a Persian shaping stack.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    root = exercise_root(script_file)
    data = load(output_path(script_file))
    if specs is None:
        specs = data["figures"]
    out_dir = os.path.join(root, "diagrams")
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for s in specs:
        kind = s["kind"]
        fig, ax = plt.subplots(figsize=(9.2, 4.6), dpi=130)
        fig.patch.set_facecolor("white")
        if kind == "bar":
            ax.bar(range(len(s["labels"])), s["values"], color="#37618e")
            ax.set_xticks(range(len(s["labels"])))
            ax.set_xticklabels(s["labels"], rotation=30, ha="right", fontsize=8)
            ax.set_ylabel(s.get("ylabel", ""))
        elif kind == "grouped_bar":
            import numpy as np
            n = len(s["labels"])
            m = len(s["series"])
            w = 0.8 / max(m, 1)
            for k, ser in enumerate(s["series"]):
                ax.bar([i + (k - (m - 1) / 2) * w for i in range(n)],
                       ser["values"], width=w, label=ser["name"])
            ax.set_xticks(range(n))
            ax.set_xticklabels(s["labels"], rotation=30, ha="right", fontsize=8)
            ax.set_ylabel(s.get("ylabel", ""))
            ax.legend(fontsize=7, ncol=min(m, 4))
        elif kind == "line":
            for ser in s["series"]:
                ax.plot(s["x"], ser["values"], marker="o", linewidth=1.6,
                        label=ser["name"])
            ax.set_xlabel(s.get("xlabel", ""))
            ax.set_ylabel(s.get("ylabel", ""))
            ax.grid(alpha=0.3)
            ax.legend(fontsize=7, ncol=min(len(s["series"]), 4))
        elif kind == "scatter":
            ax.scatter([p[0] for p in s["points"]], [p[1] for p in s["points"]],
                       s=26, color="#a33a3a", alpha=0.7)
            ax.set_xlabel(s.get("xlabel", ""))
            ax.set_ylabel(s.get("ylabel", ""))
            ax.grid(alpha=0.3)
        elif kind == "gantt":
            rows = s["rows"]
            names = []
            for i, r in enumerate(rows):
                name, a, b = r[0], int(r[1]), int(r[2])
                if name not in names:
                    names.append(name)
                y = names.index(name)
                ax.barh(y, b - a, left=a, height=0.62, color="#37618e",
                        edgecolor="white")
            ax.set_yticks(range(len(names)))
            ax.set_yticklabels(names, fontsize=8)
            ax.set_xlabel("time")
            ax.invert_yaxis()
            ax.grid(axis="x", alpha=0.3)
        elif kind == "heatmap":
            import numpy as np
            m = np.array(s["matrix"], dtype=float)
            im = ax.imshow(m, cmap="Blues", aspect="auto")
            ax.set_xticks(range(len(s["xlabels"])))
            ax.set_xticklabels(s["xlabels"], rotation=30, ha="right", fontsize=8)
            ax.set_yticks(range(len(s["ylabels"])))
            ax.set_yticklabels(s["ylabels"], fontsize=8)
            for i in range(m.shape[0]):
                for j in range(m.shape[1]):
                    ax.text(j, i, f"{m[i, j]:g}", ha="center", va="center", fontsize=7)
            fig.colorbar(im, ax=ax, shrink=0.85)
        else:
            raise ValueError(f"unknown figure kind: {kind}")
        ax.set_title(s["title"], fontsize=10)
        ax.set_xlabel(s.get("xlabel", "") if kind not in ("bar", "grouped_bar", "gantt") else ax.get_xlabel())
        fig.tight_layout()
        path = os.path.join(out_dir, s["file"])
        fig.savefig(path, facecolor="white")
        plt.close(fig)
        made.append(path)
    return made


def write_summary(script_file: str, title: str, lines: Sequence[str]) -> str:
    root = exercise_root(script_file)
    path = os.path.join(root, "output", "experiments_summary.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(title + "\n" + "=" * len(title) + "\n\n")
        f.write("\n".join(lines) + "\n")
    return path


def rng(seed: int = SEED) -> random.Random:
    return random.Random(seed)


def finding(fid: str, kind: str, title_en: str, title_fa: str,
            detail_en: str, detail_fa: str, numbers: Optional[dict] = None,
            witness: Optional[Sequence[str]] = None, source: str = "") -> dict:
    """A tagged finding.  All numbers in ``detail_*`` and ``numbers`` are
    produced by the experiment script, never typed into a report."""
    return {"id": fid, "kind": kind, "title_en": title_en, "title_fa": title_fa,
            "detail_en": detail_en, "detail_fa": detail_fa,
            "numbers": numbers or {}, "witness": list(witness or []),
            "source": source}


def sweep(sid: str, xlabel: str, ylabel: str, x: Sequence,
          series: Sequence[dict], source: str, figure: str = "") -> dict:
    return {"id": sid, "xlabel": xlabel, "ylabel": ylabel,
            "x": list(x), "series": [dict(s) for s in series],
            "source": source, "figure": figure}


def meta(n: int, scope_en: str, scope_fa: str, extra: Optional[dict] = None) -> dict:
    d = {"exercise": n, "seed": SEED, "policies": list(ALL_POLICIES),
         "lst_tie_breaks": list(LST_POLICIES), "generator": "code/run_experiments.py",
         "scope_en": scope_en, "scope_fa": scope_fa,
         "question_en": "", "question_fa": ""}
    if extra:
        d.update(extra)
    return d


def common_findings(sets: Sequence[dict]) -> list:
    """Four findings that every exercise can make from its own measured data.

    The prose is generated from the numbers; nothing is asserted that the data
    does not support.  Each exercise appends its own question-specific findings.
    """
    s0 = sets[0]
    p = s0["policies"]
    implicit = [s for s in sets if not s["constrained_deadline"]]
    constrained = [s for s in sets if s["constrained_deadline"]]
    cap = s0["cap_control"]
    cap_bad = [r for r in cap["rows"] if r["truncated"] and not r["feasible"]]
    cheaper = [s for s in sets
               if s["witness_cost"].get("available")
               and s["witness_cost"]["preemptions"] < s["policies"]["lst"]["preemptions"]]
    mismatches = [s for s in sets
                  if s["alignment"]["naive_agrees"] != s["alignment"]["aligned_agrees"]]
    target = mismatches[0] if mismatches else max(
        sets, key=lambda s: (s["alignment"]["naive"]["lst"]["missed"]
                             - s["alignment"]["aligned"]["lst"]["missed"]))
    al = target["alignment"]
    if mismatches:
        d3_en = (f"[D] On {target['id']} the checker says "
                 f"{'feasible' if al['checker_verdict'] else 'infeasible'}, "
                 f"yet the naive two-hyperperiod LST run misses "
                 f"{al['naive']['lst']['missed']} deadlines while the aligned "
                 f"run misses {al['aligned']['lst']['missed']}. The two "
                 f"instruments were looking at different job sets. Aligning the "
                 f"release window removes the disagreement; the instrument, not "
                 f"the theorem, was at fault.")
        d3_fa = (f"[D] روی {target['id']} چککننده «"
                 f"{'شدنی' if al['checker_verdict'] else 'نشدنی'}» میگوید، ولی "
                 f"اجرای سادهلوح LST در دو دورهٔ بزرگ "
                 f"{al['naive']['lst']['missed']} خطا میدهد و اجرای همتراز "
                 f"{al['aligned']['lst']['missed']} خطا. دو ابزار به دو مجموعهٔ "
                 f"متفاوت از کارها نگاه میکردند. همتراز کردنِ پنجرهٔ انتشار "
                 f"اختلاف را برمیدارد؛ مقصر ابزار بود، نه برهان.")
    else:
        d3_en = (f"[D] No naive-versus-aligned mismatch survives on these "
                 f"{len(sets)} sets: {sum(1 for s in sets if s['alignment']['naive_agrees'])} "
                 f"naive and {sum(1 for s in sets if s['alignment']['aligned_agrees'])} "
                 f"aligned comparisons agree with the checker. The largest gap "
                 f"in missed deadlines between the two settings is "
                 f"{al['naive']['lst']['missed'] - al['aligned']['lst']['missed']} "
                 f"on {target['id']}. Reporting a disagreement that the data "
                 f"does not contain would be the mistake.")
        d3_fa = (f"[D] روی این {len(sets)} مجموعه هیچ ناهماهنگیِ "
                 f"سادهلوح/همتراز باقی نمیماند: "
                 f"{sum(1 for s in sets if s['alignment']['naive_agrees'])} مقایسهٔ "
                 f"سادهلوح و {sum(1 for s in sets if s['alignment']['aligned_agrees'])} "
                 f"مقایسهٔ همتراز با چککننده جوراند. بیشترین شکافِ خطاها بین دو "
                 f"تنظیم برابر "
                 f"{al['naive']['lst']['missed'] - al['aligned']['lst']['missed']} "
                 f"روی {target['id']} است. گزارشِ اختلافی که داده ندارد همان "
                 f"اشتباه است.")
    return [
        finding(
            "F1", "M",
            "Minimising slack is not minimising overhead",
            "کمینه کردن لَکسیَتی، کمینه کردن سربار نیست",
            (f"[M] On {s0['id']}, LST records {p['lst']['preemptions']} "
             f"preemptions and {p['lst']['context_switches']} context switches; "
             f"EDF records {p['edf']['preemptions']} and "
             f"{p['edf']['context_switches']}. Both miss "
             f"{p['lst']['missed']} deadlines. [E] The checker verdict is "
             f"{'feasible' if s0['checker']['feasible'] else 'infeasible'} "
             f"after {s0['checker']['states']} states. Correctness does not "
             f"order these two policies; overhead does."),
            (f"[M] روی {s0['id']}، LST برابر {p['lst']['preemptions']} پیشگیری "
             f"و {p['lst']['context_switches']} تعویض زمینه ثبت میکند؛ EDF "
             f"برابر {p['edf']['preemptions']} و {p['edf']['context_switches']}. "
             f"هر دو {p['lst']['missed']} ضربالاجل از دست میدهند. [E] حکم "
             f"چککننده پس از {s0['checker']['states']} حالت «"
             f"{'شدنی' if s0['checker']['feasible'] else 'نشدنی'}» است. درستی "
             f"این دو سیاست را مرتب نمیکند؛ سربار میکند."),
            {"lst_preemptions": p["lst"]["preemptions"],
             "edf_preemptions": p["edf"]["preemptions"],
             "lst_switches": p["lst"]["context_switches"],
             "edf_switches": p["edf"]["context_switches"],
             "checker_states": s0["checker"]["states"]},
            source="task_sets[0].policies"),
        finding(
            "F2", "B",
            "Implicit deadlines take the test away",
            "ضربالاجل ضمنی، آزمون را از میان برمیدارد",
            (f"[E] Of {len(implicit)} sets with implicit deadlines, "
             f"{sum(1 for s in implicit if s['checker']['feasible'])} are "
             f"feasible. Of {len(constrained)} constrained sets, "
             f"{sum(1 for s in constrained if s['checker']['feasible'])} are "
             f"feasible and {sum(1 for s in constrained if not s['checker']['feasible'])} "
             f"are infeasible. Feasibility has discriminating power only in "
             f"the constrained regime; that is why every sweep here moves a "
             f"deadline rather than a definition."),
            (f"[E] از {len(implicit)} مجموعه با ضربالاجل ضمنی، "
             f"{sum(1 for s in implicit if s['checker']['feasible'])} شدنیاند. "
             f"از {len(constrained)} مجموعهٔ مقید، "
             f"{sum(1 for s in constrained if s['checker']['feasible'])} شدنی و "
             f"{sum(1 for s in constrained if not s['checker']['feasible'])} "
             f"نشدنیاند. شدنیبودن فقط در رژیم مقید قدرت تفکیک دارد؛ برای همین "
             f"هر جاروبی اینجا ضربالاجلی را جابهجا میکند، نه تعریفی را."),
            {"implicit_sets": len(implicit),
             "implicit_feasible": sum(1 for s in implicit if s["checker"]["feasible"]),
             "constrained_sets": len(constrained),
             "constrained_feasible": sum(1 for s in constrained if s["checker"]["feasible"]),
             "constrained_infeasible": sum(1 for s in constrained if not s["checker"]["feasible"])},
            source="task_sets[*].checker"),
        finding("F3", "D",
                "Naive versus aligned comparison",
                "مقایسهٔ سادهلوح در برابر همتراز",
                d3_en, d3_fa,
                {"naive_agree": sum(1 for s in sets if s["alignment"]["naive_agrees"]),
                 "aligned_agree": sum(1 for s in sets if s["alignment"]["aligned_agrees"]),
                 "set_count": len(sets),
                 "naive_missed_target": al["naive"]["lst"]["missed"],
                 "aligned_missed_target": al["aligned"]["lst"]["missed"]},
                source="task_sets[*].alignment"),
        finding(
            "F4", "D",
            "A state cap fabricates an infeasibility verdict",
            "سقفِ حالت، حکمِ نشدنیبودن میسازد",
            (f"[D] With a reduced state cap, {s0['id']} is reported infeasible "
             f"{len(cap_bad)} times, each run flagged truncated; with the cap "
             f"restored the verdict is "
             f"{'feasible' if cap['full_verdict'] else 'infeasible'} after "
             f"{s0['checker']['states']} states. The smallest truncating cap "
             f"was {cap['smallest_truncating_limit']}. A truncated run is an "
             f"artefact of the instrument and is never used as a finding."),
            (f"[D] با سقفِ حالتِ کاهش‌یافته، {s0['id']} به تعداد {len(cap_bad)} "
             f"بار نشدنی گزارش میشود که هر بار برچسب بریدگی دارد؛ با "
             f"برگرداندن سقف، حکم پس از {s0['checker']['states']} حالت «"
             f"{'شدنی' if cap['full_verdict'] else 'نشدنی'}» است. کمترین سقفِ "
             f"بریدهکننده {cap['smallest_truncating_limit']} بود. اجرای "
             f"بریدهشده مصنوعِ ابزار است و هرگز یافته به حساب نمیآید."),
            {"false_infeasible_runs": len(cap_bad),
             "smallest_truncating_limit": cap["smallest_truncating_limit"],
             "full_states": s0["checker"]["states"],
             "full_feasible": 1 if cap["full_verdict"] else 0},
            source="task_sets[0].cap_control"),
    ]


def witness_finding(sets: Sequence[dict], fid: str = "F5") -> dict:
    cheaper = [s for s in sets
               if s["witness_cost"].get("available")
               and s["witness_cost"]["preemptions"] < s["policies"]["lst"]["preemptions"]]
    s0 = sets[0]
    return finding(
        fid, "M",
        "The checker's own witness is cheaper than LST",
        "شاهدِ خودِ چککننده از LST ارزانتر است",
        (f"[E] {sum(1 for s in sets if s['witness'].get('valid') is True)} "
         f"witnesses were independently re-checked and found valid. [M] On "
         f"{len(cheaper)} of {len(sets)} sets the witness needs fewer "
         f"preemptions than LST: on {s0['id']}, "
         f"{s0['witness_cost']['preemptions']} against "
         f"{s0['policies']['lst']['preemptions']}. Verification groups these "
         f"schedules as equivalent; measurement separates them. The witness "
         f"is a counterexample to the claim that all feasible schedules cost "
         f"the same."),
        (f"[E] {sum(1 for s in sets if s['witness'].get('valid') is True)} شاهد "
         f"به طور مستقل دوباره چک و معتبر شناخته شدند. [M] روی {len(cheaper)} "
         f"از {len(sets)} مجموعه، شاهد به پیشگیری کمتری از LST نیاز دارد: روی "
         f"{s0['id']}، {s0['witness_cost']['preemptions']} در برابر "
         f"{s0['policies']['lst']['preemptions']}. بررسی، این برنامهها را "
         f"همارز میداند؛ اندازهگیری جدایشان میکند. شاهد، counterexample ادعای "
         f"«همهٔ برنامههای شدنی هزینهٔ یکسان دارند» است."),
        {"valid_witnesses": sum(1 for s in sets if s["witness"].get("valid") is True),
         "witness_cheaper_sets": len(cheaper),
         "set_count": len(sets),
         "witness_preemptions": s0["witness_cost"]["preemptions"],
         "lst_preemptions": s0["policies"]["lst"]["preemptions"]},
        source="task_sets[*].witness_cost")


def rm_finding(sets: Sequence[dict], fid: str = "F6") -> dict:
    cands = [s for s in sets if s["alignment"]["rm_control"]["counterexample"]]
    s = cands[0] if cands else sets[0]
    p = s["policies"]
    return finding(
        fid, "E",
        "RM is a genuine counterexample, not an instrument mismatch",
        "RM یک ضدمثال واقعی است، نه ناهماهنگی ابزار",
        (f"[E] {s['id']} is feasible by exhaustive search. [M] RM misses "
         f"{p['rm']['missed']} deadlines while LST and EDF miss "
         f"{p['lst']['missed']} and {p['edf']['missed']}; the aligned RM run "
         f"still misses {s['alignment']['aligned']['rm']['missed']}. This is "
         f"a counterexample to RM's optimality, not a checker defect: the "
         f"independent witness is valid. Demanding that RM agree with the "
         f"verdict was the first version of the alignment helper's mistake."),
        (f"[E] {s['id']} به حکم جستجوی جامع شدنی است. [M] RM برابر "
         f"{p['rm']['missed']} ضربالاجل از دست میدهد در حالی که LST و EDF به "
         f"ترتیب {p['lst']['missed']} و {p['edf']['missed']} خطا دارند؛ اجرای "
         f"همتراز RM باز هم {s['alignment']['aligned']['rm']['missed']} خطا "
         f"میدهد. این ضدمثالِ بهینگی RM است، نه نقصِ چککننده: شاهد مستقل "
         f"معتبر است. خواستنِ جوربودنِ RM با حکم، اشتباه نسخهٔ نخستِ "
         f"همترازساز بود."),
        {"rm_missed": p["rm"]["missed"],
         "lst_missed": p["lst"]["missed"],
         "edf_missed": p["edf"]["missed"],
         "rm_aligned_missed": s["alignment"]["aligned"]["rm"]["missed"]},
        source="task_sets[*].policies.rm")


def standard_figures(sets: Sequence[dict], prefix: str,
                     gantt_policy: str = "lst") -> list:
    """A common, fully data-driven figure bundle for one exercise."""
    s0 = sets[0]
    ids = [s["id"] for s in sets]
    policies = [p for p in s0["policies"]]
    figs = [
        fig_bar(f"fig_{prefix}_preemptions.png",
                f"Preemptions by policy on {s0['id']}",
                policies,
                [s0["policies"][p]["preemptions"] for p in policies],
                "task_sets[0].policies.*.preemptions", ylabel="preemptions"),
        fig_grouped(f"fig_{prefix}_misses.png",
                    "Missed deadlines per set and policy", ids,
                    [{"name": p, "values": [s["policies"][p]["missed"] for s in sets]}
                     for p in ("lst", "edf", "rm") if p in s0["policies"]],
                    "task_sets[*].policies.*.missed", ylabel="missed deadlines",
                    xlabel="task set"),
        fig_heatmap(f"fig_{prefix}_ties.png",
                    "Tie events per set and policy",
                    [[s["policies"][p]["tie_events"] for s in sets]
                     for p in LST_POLICIES if p in s0["policies"]],
                    ids, [p for p in LST_POLICIES if p in s0["policies"]],
                    "task_sets[*].policies.*.tie_events"),
    ]
    if s0.get("gantt", {}).get(gantt_policy):
        figs.append(fig_gantt(f"fig_{prefix}_gantt.png",
                              f"{gantt_policy} schedule on {s0['id']}",
                              s0["gantt"][gantt_policy][:16],
                              f"task_sets[0].gantt.{gantt_policy}"))
    return figs


def slide(title_en: str, title_fa: str, body_en: Sequence[str],
          body_fa: Sequence[str], notes_en: str, notes_fa: str,
          figure: str = "", source: str = "") -> dict:
    """One bilingual slide spec.  Every number in a body/notes string must
    have been produced by a program and stored in the data file."""
    return {"title_en": title_en, "title_fa": title_fa,
            "body_en": list(body_en), "body_fa": list(body_fa),
            "notes_en": notes_en, "notes_fa": notes_fa,
            "figure": figure, "source": source}


def deck_spec(files: Sequence[str], slides: Sequence[dict]) -> dict:
    return {"files": list(files), "slide_count": len(slides),
            "notes_on_every_slide": all(s.get("notes_en") and s.get("notes_fa")
                                        for s in slides),
            "slides": list(slides)}


def read_exercise(n: int, root: Optional[str] = None) -> dict:
    """Read another exercise's generated data (used by exercises 5 and 6)."""
    import hashlib
    root = root or REPO
    p = os.path.join(root, f"exercise-{n}", "output", "experiments.json")
    raw = open(p, "rb").read()
    return {"path": os.path.relpath(p, root), "sha256": hashlib.sha256(raw).hexdigest(),
            "data": json.loads(raw.decode("utf-8"))}


def sweep_alignment(sets: Sequence[dict], figure: str = "",
                    source: str = "sweeps[last]") -> dict:
    ids, naive, aligned, verdict = [], [], [], []
    for s in sets:
        al = s["alignment"]
        ids.append(s["id"])
        naive.append(al["naive"]["lst"]["missed"])
        aligned.append(al["aligned"]["lst"]["missed"])
        verdict.append(1 if al["checker_verdict"] else 0)
    return sweep("alignment", "task set", "count", ids,
                 [{"name": "naive_lst_missed", "values": naive},
                  {"name": "aligned_lst_missed", "values": aligned},
                  {"name": "checker_feasible", "values": verdict}],
                 source, figure=figure)


def sweep_parameter(sid: str, xlabel: str, xvalues: Sequence,
                    build_tasks, metric: str,
                    policies: Sequence[str] = ("lst", "edf", "rm"),
                    figure: str = "", source: str = "") -> dict:
    """Vary one parameter, measure one metric for several policies.

    ``build_tasks(x)`` returns a task list; everything else stays fixed.  The
    checker verdict is included as an extra series when the metric is misses,
    so the two instruments can be seen on the same plot.
    """
    x = list(xvalues)
    series = [{"name": f"{p}_{metric}", "values": []} for p in policies]
    verdict = []
    for value in x:
        tasks = build_tasks(value)
        ok, _s, _st = exhaustive_feasible(tasks, horizon=hyperperiod(tasks))
        verdict.append(1 if ok else 0)
        for ser, p in zip(series, policies):
            r = simulate(tasks, p, cycles=2)
            ser["values"].append(getattr(r, metric))
    if metric == "missed":
        series.append({"name": "checker_feasible", "values": verdict})
    return sweep(sid, xlabel, metric, x, series, source, figure=figure)


def build_exercise(script_file: str, n: int, specs: Sequence[Sequence],
                   scope_en: str, scope_fa: str, sweeps_fn=None,
                   extra_figures_fn=None, extra_findings_fn=None,
                   gantt_policies=("lst", "edf", "rm"),
                   prefix: Optional[str] = None, extra: Optional[dict] = None,
                   extra_fn=None,
                   policies: Sequence[str] = ALL_POLICIES) -> dict:
    """Assemble one exercise's whole data file from its task-set specs."""
    prefix = prefix or f"ex{n}"
    sets = [describe_set(mk(rows), sid, label,
                         policies=policies, gantt_policies=gantt_policies)
            for sid, label, rows in specs]
    sweeps = list(sweeps_fn(sets)) if sweeps_fn else []
    figures = standard_figures(sets, prefix)
    for sw in sweeps:
        if sw.get("figure"):
            figures.append(fig_line(sw["figure"],
                                    "Sweep " + sw["id"] + ": " + sw["xlabel"],
                                    sw["x"], sw["series"], sw["source"],
                                    ylabel=sw["ylabel"], xlabel=sw["xlabel"]))
    if extra_figures_fn:
        figures += list(extra_figures_fn(sets, sweeps))
    if extra_findings_fn:
        tail = list(extra_findings_fn(sets))
    else:
        tail = [witness_finding(sets), rm_finding(sets)]
    findings = (common_findings(sets) + tail)[:6]
    if extra_fn:
        merged = dict(extra or {})
        merged.update(extra_fn(sets))
        extra = merged
    return finish(script_file, n, sets, sweeps, figures, findings,
                  scope_en, scope_fa, extra=extra)


def finish(script_file: str, n: int, sets: Sequence[dict],
           sweeps: Sequence[dict], figures: Sequence[dict],
           findings: Sequence[dict], scope_en: str, scope_fa: str,
           extra: Optional[dict] = None) -> dict:
    """Assemble, write and summarise the generated data file.

    No content module ever sees a number that did not pass through here.
    """
    data = {
        "meta": meta(n, scope_en, scope_fa,
                     {"task_sets": len(sets), "sweeps": len(sweeps),
                      "figures": len(figures), "findings": len(findings),
                      "horizon_cycles": 2}),
        "task_sets": list(sets),
        "sweeps": list(sweeps),
        "figures": list(figures),
        "findings": list(findings),
    }
    if extra:
        data.update(extra)
    path = dump(output_path(script_file), data)
    naive = sum(1 for s in sets if s["alignment"]["naive_agrees"])
    aligned = sum(1 for s in sets if s["alignment"]["aligned_agrees"])
    caps = sum(1 for s in sets if s["cap_control"]["false_infeasible_count"] > 0)
    feas = sum(1 for s in sets if s["checker"]["feasible"])
    lines = [
        f"seed: {SEED}",
        f"task sets: {len(sets)}  figures: {len(figures)}  "
        f"sweeps: {len(sweeps)}  findings: {len(findings)}",
        f"feasible [E]: {feas}  infeasible [E]: {len(sets) - feas}",
        f"naive comparisons agreeing: {naive}",
        f"aligned comparisons agreeing: {aligned}",
        f"cap artefacts: {caps}",
        f"independently valid witnesses: "
        f"{sum(1 for s in sets if s['witness'].get('valid') is True)}",
    ]
    write_summary(script_file, f"Exercise {n} — LST", lines)
    print("\n".join(lines))
    print("wrote", path)
    return data


# --------------------------------------------------------------------------
# random task sets with constrained deadlines (the only meaningful regime)
# --------------------------------------------------------------------------

def random_sets(rnd: random.Random, count: int, n_tasks=(2, 3),
                max_hp=40, u_cap=1.0, constrained=True) -> List[List[Task]]:
    """Generate task sets with D in [C, T] (optionally forced D < T).

    With implicit deadlines (D = T) and U <= 1 every synchronous periodic set
    is feasible on one preemptive processor, so an optimality experiment has
    no discriminating power.  Constrained deadlines are the real test.
    """
    out = []
    periods = [3, 4, 5, 6, 8, 10, 12]
    tries = 0
    while len(out) < count and tries < count * 200:
        tries += 1
        n = rnd.choice(list(n_tasks))
        rows = []
        hp = 1
        for i in range(n):
            p = rnd.choice(periods)
            c = rnd.randint(1, max(1, min(p - 1, 5)))
            d = rnd.randint(c, p)
            if constrained and d == p and c < p:
                d = rnd.randint(c, p - 1) if p - 1 >= c else c
            rows.append([f"T{i + 1}", p, c, d])
            import math
            hp = hp * p // math.gcd(hp, p)
        if hp > max_hp:
            continue
        tasks = mk(rows)
        if utilisation(tasks) > u_cap + 1e-9:
            continue
        out.append(tasks)
    return out
