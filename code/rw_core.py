#!/usr/bin/env python3
"""Readers-writers model for exercise 7.  Self-contained; no LST imports.

Two instruments, deliberately separate in what they answer:

* ``explore`` / ``check`` -- [E] exhaustive finite-state checking.  It answers
  yes/no questions: is mutual exclusion ever violated, is there a deadlock, is
  there a *fair* starvation cycle, is waiting bounded?  Every counterexample is
  a witness trace that ``verify_witness`` re-checks with an independent
  interpreter that shares no transition code with the checker.
* ``measure`` -- [M] a seeded discrete-event simulator.  It answers "how much":
  completed operations, waiting times, throughput, and how often a finite
  horizon makes a starvation-free mechanism *look* starving.

State is a hashable tuple ``(proc_states, queue, woken, turn)`` where
``proc_states[i]`` is 0 = thinking, 1 = waiting, 2 = in the critical section.
There is no unbounded counter, so the reachable graph is finite and a lasso is
a genuine infinite execution.  A starvation cycle is accepted only when the
starving process's grant is NEVER enabled on the cycle (fairness) AND some other
process enters the critical section on the cycle (progress).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from collections import deque

sys.setrecursionlimit(20000)

MECHANISMS = ("readers_preference", "writers_preference", "fair_fifo",
              "mesa_signal", "hoare_signal", "dekker2", "peterson2")
CONFIGS = {
    "2r1w": ("R", "R", "W"),
    "1r2w": ("R", "W", "W"),
    "1r1w": ("R", "W"),
}
STATE_LIMIT = 120_000


def protocols():
    out = []
    for mech in MECHANISMS:
        names = ("1r1w",) if mech in ("dekker2", "peterson2") else ("2r1w", "1r2w")
        for cfg in names:
            out.append({"id": f"{mech}:{cfg}", "mechanism": mech,
                        "config": cfg, "roles": CONFIGS[cfg]})
    return out


def _readers_in_cs(s, roles):
    return sum(1 for i, st in enumerate(s[0]) if st == 2 and roles[i] == "R")


def _writers_in_cs(s, roles):
    return sum(1 for i, st in enumerate(s[0]) if st == 2 and roles[i] == "W")


def _tag(p, roles):
    return f"{roles[p]}{p}"


def signal(ps, queue, woken, mech, roles):
    """Mesa/Hoare signalling when the critical section empties."""
    if mech not in ("mesa_signal", "hoare_signal"):
        return queue, woken
    if any(st == 2 for st in ps):
        return queue, woken
    waiting_w = [q for q in queue if ps[q] == 1 and roles[q] == "W"]
    if not waiting_w:
        return queue, -1
    if mech == "hoare_signal" and woken != -1 and woken in waiting_w:
        # Hoare handoff: the signalled thread keeps its place at the head.
        return (woken,) + tuple(x for x in queue if x != woken), woken
    w = waiting_w[0]
    if mech == "hoare_signal":
        queue = (w,) + tuple(x for x in queue if x != w)
    return queue, w


def can_grant(p, s, proto):
    """The mechanism's admission rule.  Shared by [E] and [M] on purpose: the
    policy is the object under study, not the instrument."""
    ps, queue, woken, turn = s
    roles, mech = proto["roles"], proto["mechanism"]
    ric, wic = _readers_in_cs(s, roles), _writers_in_cs(s, roles)
    if roles[p] == "W":
        if ric != 0 or wic != 0:
            return False
    else:
        if wic != 0:
            return False
    waiting_w = sum(1 for i, st in enumerate(ps)
                    if st == 1 and roles[i] == "W")
    if mech == "readers_preference":
        return True
    if mech == "writers_preference":
        return roles[p] == "W" or waiting_w == 0
    if mech == "fair_fifo":
        if p not in queue:
            return False
        idx = queue.index(p)
        if idx == 0:
            return True
        return (roles[p] == "R"
                and all(roles[q] == "R" for q in queue[:idx]))
    if mech == "mesa_signal":
        # Mesa: a woken writer is not put in the entry queue, so fresh readers
        # still bypass it.  Waiting is unbounded until it is given a place.
        return woken == p if roles[p] == "W" else True
    if mech == "hoare_signal":
        # Hoare: the signaller yields to the woken thread; no fresh entrant may
        # bypass a waiting writer.
        if roles[p] == "W":
            return woken == p
        return woken == -1 and waiting_w == 0
    if mech in ("dekker2", "peterson2"):
        if ric + wic > 0:
            return False
        other = 1 - p
        if ps[other] != 1:
            return True
        return turn == p
    return False


def successors(s, proto):
    ps, queue, woken, turn = s
    roles, mech = proto["roles"], proto["mechanism"]
    out = []
    for p, st in enumerate(ps):
        if st == 0:
            q = queue if p in queue else queue + (p,)
            w = woken
            if mech == "hoare_signal" and roles[p] == "W" and w == -1:
                w = p
                q = (p,) + tuple(x for x in q if x != p)
            turn2 = (1 - p) if mech == "peterson2" else turn
            ps2 = list(ps); ps2[p] = 1
            out.append((f"{_tag(p, roles)} request",
                        (tuple(ps2), q, w, turn2)))
        elif st == 1:
            if can_grant(p, s, proto):
                ps2 = list(ps); ps2[p] = 2
                q = tuple(x for x in queue if x != p)
                w = -1 if woken == p else woken
                out.append((f"{_tag(p, roles)} grant",
                            (tuple(ps2), q, w, turn)))
        else:
            ps2 = list(ps); ps2[p] = 0
            turn2 = (1 - p) if mech == "dekker2" else turn
            q, w = signal(tuple(ps2), queue, woken, mech, roles)
            out.append((f"{_tag(p, roles)} release",
                        (tuple(ps2), q, w, turn2)))
    return out


def initial(proto):
    return (tuple(0 for _ in proto["roles"]), (), -1, 0)


def explore(proto):
    """BFS over every reachable state.  Returns (init, seen, edges, parent)."""
    init = initial(proto)
    seen = {init}
    edges = {}
    parent = {init: None}
    dq = deque([init])
    truncated = False
    while dq:
        if len(seen) > STATE_LIMIT:
            truncated = True
            break
        s = dq.popleft()
        e = successors(s, proto)
        edges[s] = e
        for a, ns in e:
            if ns not in seen:
                seen.add(ns)
                parent[ns] = (s, a)
                dq.append(ns)
    return init, seen, edges, parent, truncated


def _prefix_actions(parent, s):
    out = []
    while parent.get(s) is not None:
        prev, a = parent[s]
        out.append(a)
        s = prev
    out.reverse()
    return out


def starvation_witness(proto, p, seen, edges, parent):
    """A fair lasso in which process p waits forever.  None if there is none."""
    roles = proto["roles"]
    color, stack, acts = {}, [], []
    found = []

    def dfs(s):
        color[s] = 1
        stack.append(s)
        for a, ns in edges.get(s, []):
            if ns not in seen or ns[0][p] != 1:
                continue
            c = color.get(ns, 0)
            if c == 0:
                acts.append(a)
                if dfs(ns):
                    return True
                acts.pop()
            elif c == 1 and ns in stack:
                i = stack.index(ns)
                cyc_states = stack[i:]
                cyc_acts = acts[i:] + [a]
                others = [x for x in cyc_acts
                          if x.endswith(" grant") and not x.startswith(f"{roles[p]}{p} ")]
                never_enabled = all(not can_grant(p, st, proto)
                                    for st in cyc_states)
                if others and never_enabled:
                    found.append({
                        "type": "starvation",
                        "process": p,
                        "role": roles[p],
                        "prefix": _prefix_actions(parent, stack[i]),
                        "cycle": cyc_acts,
                        "cycle_length": len(cyc_acts),
                        "grant_enabled_in_cycle": 0,
                        "other_grants_in_cycle": len(others),
                    })
                    return True
        stack.pop()
        color[s] = 2
        return False

    for s in sorted(seen, key=repr):
        if s[0][p] == 1 and color.get(s, 0) == 0:
            if dfs(s):
                break
    return found[0] if found else None


def bounded_wait(proto, p, seen, edges):
    """Max shortest distance from a waiting state to a state where p is in CS."""
    rev = {s: [] for s in seen}
    for s, e in edges.items():
        for a, ns in e:
            if ns in rev:
                rev[ns].append(s)
    dist, dq = {}, deque()
    for s in seen:
        if s[0][p] == 2:
            dist[s] = 0
            dq.append(s)
    while dq:
        x = dq.popleft()
        for y in rev[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    waiting = [s for s in seen if s[0][p] == 1]
    if not waiting:
        return 0
    if any(s not in dist for s in waiting):
        return -1
    return max(dist[s] for s in waiting)


def check(proto):
    """[E] exhaustive verdicts for one protocol instance."""
    init, seen, edges, parent, truncated = explore(proto)
    roles = proto["roles"]
    me_violations = 0
    for s in seen:
        if _writers_in_cs(s, roles) > 1 or (
                _readers_in_cs(s, roles) > 0 and _writers_in_cs(s, roles) > 0):
            me_violations += 1
    deadlocks = 0
    for s in seen:
        if any(st == 1 for st in s[0]) and not edges.get(s):
            deadlocks += 1
    starvation = {}
    for p in range(len(roles)):
        w = starvation_witness(proto, p, seen, edges, parent)
        starvation[str(p)] = w
    bounds = {}
    for p in range(len(roles)):
        # A fair starvation cycle means worst-case waiting is infinite, even
        # though a shortest path into the critical section may still exist.
        bounds[str(p)] = (-1 if starvation[str(p)] is not None
                          else bounded_wait(proto, p, seen, edges))
    witnesses = [w for w in starvation.values() if w]
    return {
        "id": proto["id"],
        "mechanism": proto["mechanism"],
        "config": proto["config"],
        "roles": list(roles),
        "states": len(seen),
        "transitions": sum(len(e) for e in edges.values()),
        "truncated": truncated,
        "mutual_exclusion": me_violations == 0,
        "mutual_exclusion_violations": me_violations,
        "deadlock_free": deadlocks == 0,
        "deadlock_states": deadlocks,
        "starvation_free": len(witnesses) == 0,
        "starving_processes": [int(k) for k, v in starvation.items() if v],
        "bounded_wait": bounds,
        "witness": witnesses[0] if witnesses else None,
        "witnesses": starvation,
    }


# ---------------------------------------------------------------------------
# Independent verifier: its own interpreter, no shared transition function.
# ---------------------------------------------------------------------------

def verify_witness(proto, witness):
    """Re-simulate a counterexample with a separate implementation."""
    roles, mech = proto["roles"], proto["mechanism"]
    ps = [0] * len(roles)
    queue, woken, turn = [], -1, 0
    steps, violations = 0, []

    def apply(action):
        """Return (ok, legal).  Independent of successors()/can_grant()."""
        nonlocal queue, woken, turn
        tag, verb = action.rsplit(" ", 1)
        role, idx = tag[0], int(tag[1:])
        if idx >= len(roles) or roles[idx] != role:
            return False
        ric = sum(1 for i, st in enumerate(ps) if st == 2 and roles[i] == "R")
        wic = sum(1 for i, st in enumerate(ps) if st == 2 and roles[i] == "W")
        if verb == "request":
            if ps[idx] != 0:
                return False
            ps[idx] = 1
            if idx not in queue:
                queue.append(idx)
            if mech == "peterson2":
                turn = 1 - idx
            if mech == "hoare_signal" and role == "W" and woken == -1:
                woken = idx
                queue.remove(idx)
                queue.insert(0, idx)
            return True
        if verb == "release":
            if ps[idx] != 2:
                return False
            ps[idx] = 0
            if mech == "dekker2":
                turn = 1 - idx
            if mech in ("mesa_signal", "hoare_signal") and not any(st == 2 for st in ps):
                cand = [q for q in queue if ps[q] == 1 and roles[q] == "W"]
                if not cand:
                    woken = -1
                else:
                    woken = cand[0]
                    if mech == "hoare_signal":
                        queue.remove(woken)
                        queue.insert(0, woken)
            return True
        if verb != "grant" or ps[idx] != 1:
            return False
        # Recompute the admission rule from scratch.
        if role == "W":
            if ric or wic:
                return False
        elif wic:
            return False
        ww = sum(1 for i, st in enumerate(ps) if st == 1 and roles[i] == "W")
        allowed = False
        if mech == "readers_preference":
            allowed = True
        elif mech == "writers_preference":
            allowed = role == "W" or ww == 0
        elif mech == "fair_fifo":
            if idx in queue:
                j = queue.index(idx)
                allowed = (j == 0 or (role == "R" and all(
                    roles[q] == "R" for q in queue[:j])))
        elif mech == "mesa_signal":
            allowed = (woken == idx) if role == "W" else True
        elif mech == "hoare_signal":
            allowed = ((woken == idx) if role == "W"
                       else (woken == -1 and ww == 0))
        elif mech in ("dekker2", "peterson2"):
            other = 1 - idx
            allowed = (ric + wic == 0
                       and (ps[other] != 1 or turn == idx))
        if not allowed:
            return False
        ps[idx] = 2
        if idx in queue:
            queue.remove(idx)
        if woken == idx:
            woken = -1
        return True

    p = witness["process"]
    for phase, actions in (("prefix", witness["prefix"]),
                           ("cycle", witness["cycle"]),
                           ("cycle_repeat", witness["cycle"])):
        for a in actions:
            steps += 1
            if not apply(a):
                violations.append(f"{phase}: illegal action {a}")
                break
            ric_now = sum(1 for i, st in enumerate(ps)
                          if st == 2 and roles[i] == "R")
            wic_now = sum(1 for i, st in enumerate(ps)
                          if st == 2 and roles[i] == "W")
            if ric_now and wic_now:
                violations.append(f"{phase}: mutual exclusion broken at {a}")
            if phase.startswith("cycle") and ps[p] != 1:
                violations.append(f"{phase}: starving process left WAIT at {a}")
    return {"valid": not violations and steps > 0,
            "steps": steps, "violations": violations,
            "process": p, "role": witness["role"]}


# ---------------------------------------------------------------------------
# [M] seeded discrete-event measurement
# ---------------------------------------------------------------------------

def measure(proto, seed, horizon, arrival, service_read, service_write,
            trials=3):
    """Completed operations and waiting times under a finite random workload."""
    roles, mech = proto["roles"], proto["mechanism"]
    n = len(roles)
    rng = random.Random(seed)
    agg = {"reads": 0, "writes": 0, "waits": [], "max_wait": 0,
           "writer_starved_trials": 0, "trials": trials}
    for _ in range(trials):
        state = [0] * n
        remaining = [0] * n
        requested = [0] * n
        queue, woken, turn = [], -1, 0
        reads = writes = 0
        waits = []
        for t in range(horizon):
            # 1. finish service
            for i in range(n):
                if state[i] == 2:
                    remaining[i] -= 1
                    if remaining[i] <= 0:
                        state[i] = 0
                        if roles[i] == "R":
                            reads += 1
                        else:
                            writes += 1
                        if mech == "dekker2":
                            turn = 1 - i
                        if mech in ("mesa_signal", "hoare_signal") and not any(
                                st == 2 for st in state):
                            cand = [q for q in queue if state[q] == 1 and roles[q] == "W"]
                            if not cand:
                                woken = -1
                            else:
                                if mech == "hoare_signal" and woken in cand:
                                    woken = woken
                                else:
                                    woken = cand[0]
                                if mech == "hoare_signal":
                                    queue.remove(woken)
                                    queue.insert(0, woken)
            # 2. arrivals
            for i in range(n):
                if state[i] == 0 and rng.random() < arrival:
                    state[i] = 1
                    requested[i] = t
                    if i not in queue:
                        queue.append(i)
                    if mech == "peterson2" and n == 2:
                        turn = 1 - i
                    if mech == "hoare_signal" and roles[i] == "W" and woken == -1:
                        woken = i
                        queue.remove(i)
                        queue.insert(0, i)
            # 3. grants (bounded by n so this always terminates)
            for _ in range(n):
                s = (tuple(state), tuple(queue), woken, turn)
                cand = [i for i in range(n)
                        if state[i] == 1 and can_grant(i, s, proto)]
                if not cand:
                    break
                i = cand[0]
                state[i] = 2
                remaining[i] = service_read if roles[i] == "R" else service_write
                waits.append(t - requested[i])
                if i in queue:
                    queue.remove(i)
                if woken == i:
                    woken = -1
        agg["reads"] += reads
        agg["writes"] += writes
        agg["waits"].extend(waits)
        if writes == 0 and any(r == "W" for r in roles):
            agg["writer_starved_trials"] += 1
    agg["operations"] = agg["reads"] + agg["writes"]
    agg["throughput"] = round(agg["operations"] / (trials * horizon), 4)
    agg["mean_wait"] = (round(sum(agg["waits"]) / len(agg["waits"]), 3)
                        if agg["waits"] else 0)
    agg["max_wait"] = max(agg["waits"]) if agg["waits"] else 0
    agg["wait_samples"] = len(agg["waits"])
    del agg["waits"]
    return agg


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def json_sha256(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()
