# Tie-Breaking, Laxity-Zero Thrashing and Their Cost

**the checker is silent about cost; the simulator is not**

- **Exercise:** Exercise 7
- **Course:** Real-Time Scheduling
- **Topic:** Least Slack Time (LST) scheduling
- **Deliverables:** bilingual EN/FA report, DOCX + PDF; diagrams; code; tests
- **Repository:** github.com/rera13197-ux/LST
- **Branch:** Exercise-7-LST-Tie-Breaking-And-Thrashing
- **Random seed:** 20261116
- **Status:** complete: every number regenerated from a program run
- **Page count:** measured from the produced PDF, see tools/check_outputs.py
- **Method:** two separate instruments: exhaustive verification and measurement

## Table of contents

- The question (p. 3)
- Two instruments, two kinds of claim (p. 4)
- Model and notation (p. 5)
- The scheduling rule (p. 6)
- Why deadlines must be constrained (p. 7)
- Experimental design (p. 8)
- A worked schedule (p. 9)
- Task set K1 (p. 10)
- Task set K2 (p. 11)
- Task set K3 (p. 12)
- Task set K4 (p. 13)
- Task set K5 (p. 14)
- Task set K6 (p. 15)
- Task set K7 (p. 16)
- Task set K8 (p. 17)
- Sweeps: task-count (p. 18)
- Sweeps: deadline-zero-switches (p. 19)
- Sweeps: alignment (p. 20)
- Finding: F1 (p. 21)
- Finding: F2 (p. 22)
- Finding: F3 (p. 23)
- Finding: F4 (p. 24)
- Finding: F5 (p. 25)
- Finding: F6 (p. 26)
- Figures — group 1 (p. 27)
- Figures — group 2 (p. 28)
- Figures — group 3 (p. 29)
- Figures — group 4 (p. 30)
- When the two instruments disagree (p. 31)
- A defect produced by a state cap (p. 32)
- Verification is coarse, measurement is not (p. 33)
- Limitations we state ourselves (p. 34)
- Reproducibility (p. 35)
- Deliverables and checks (p. 36)
- Appendix: the data contract (p. 37)


<!-- page 1 -->


<!-- page 2 -->


<!-- page 3 -->


## The question

What does tie-breaking actually change, and how expensive is laxity-zero thrashing when measurement and verification are kept apart?

This report states what was asked and how it was answered before giving any result, so that a reader can try to refute the claim.

| Instrument | [E] + [M] |
|---|---|
| Scope | the cost of LST tie-breaking and laxity-zero thrashing, with verification kept separate from measurement |
| Random seed | 20261116 |
| Task sets | 8 |
| Policies measured | 9 |

*Scope of this exercise*

> **Intent.** Nothing in this report is a definition restated louder. The subject is what the two instruments reveal when they are pointed at the same task sets.


<!-- page 4 -->


## Two instruments, two kinds of claim

Two tools are used in this project and they answer different questions. The exhaustive checker walks every reachable state and returns a verdict, true or false, together with a witness schedule when the verdict is true. The discrete-event simulator counts what happens in a particular run. The reports tag every claim with the tool that produced it: [E] for verification and [M] for measurement. A sentence of the form 'it never missed in our runs, therefore it is correct' is not written here.


### Which claim comes from where

- [E] exhaustive verification — feasibility, witnesses, idle-enumeration controls, optimality counterexamples.
- [M] measurement — preemptions, switches, laxity-zero switches, tie events, response time, jitter, first miss.
- [D] disagreement — a mismatch; the instrument is suspected first.

[M] Preemptions, context switches, laxity-zero switches, tie events, minimum observed laxity, response time and jitter are counted by the simulator over an integer timeline. [E] Feasibility is decided by the checker, and every witness schedule it returns is re-checked by a separate verifier that shares no code with the checker. When the two instruments disagree, the instrument is the first suspect, not the theorem and not the data.

> **Standing rule.** Every witness schedule returned by the checker is walked again by a verifier that does not call the checker. This is a standing rule, not a one-off check.


<!-- page 5 -->


## Model and notation

One processor, preemptive, independent jobs, integer time. Execution time is taken equal to the worst-case estimate, so a schedule worked out by hand and the program's timeline can be compared unit by unit without tolerance. A preemption is counted but not charged to the timeline; overhead is therefore a measurement, not a distortion of the model. A job's slack is how long it could still wait and still meet its deadline.

```text
laxity(job, t) = deadline(job) - t - remaining(job)
LST(t)        = argmin laxity(job, t) over ready jobs
```
*Definition, not a measurement*

| Symbol | Meaning |
|---|---|
| T | period |
| C | worst-case execution, equal to actual here |
| D | relative deadline |
| t | integer time instant |
| U | descriptive utilisation ratio |

*Notation*

The tie-break rule of LST is a parameter in the simulator, not a hidden implementation choice, because whether it changes correctness or cost is itself one of the questions of this project. The checker enumerates work-conserving schedules only; forced idle, when nothing has been released yet, is always allowed. Optional idle is a separate mode used as a control, never as the default.


<!-- page 6 -->


## The scheduling rule

The rule is short; the interesting part is what it does when two jobs reach the same slack. The tie-break is an explicit parameter of the simulator.

```text
at every integer instant t:
    release every job whose release time is t
    mark a job missed if t reaches its deadline
    ready = jobs released and not finished
    if ready is empty: idle for this unit (forced idle)
    else:
        slack(j) = deadline(j) - t - remaining(j)
        best     = min slack over ready
        run the ready job attaining best, chosen by tie_break
        count a preemption if the previous job still has work
        count a laxity-zero switch if both slacks are zero
```
*Discrete-time rule as implemented in the core*


### Tie-break policies

- lst / lst:edf / lst:rm / lst:stay / lst:lzs — index, earliest deadline, shortest period, keep the running job, or switch by earliest deadline at zero laxity.
- edf / rm / dm / fifo — baseline policies with no tie-break parameter.

> **Parameter, not detail.** The tie-break never silently changes: it is part of the policy name and of every generated data row.


<!-- page 7 -->


## Why deadlines must be constrained

With implicit deadlines equal to periods and utilisation at most one, every synchronous periodic task set is feasible on a preemptive uniprocessor. An optimality experiment then has nothing to decide: the checker always says feasible and every optimal policy records the same zero misses. All experiments therefore use constrained deadlines, deadline smaller than the period, where utilisation is necessary but not sufficient and the feasible / infeasible split is real. This choice is a design decision about the measuring instrument, not a claim about the algorithm.

| Regime | What the checker can say |
|---|---|
| implicit deadline, U no more than one | always feasible, so no optimality test |
| constrained deadline | feasible and infeasible sets both occur |

*Design of the measuring instrument*

> **The split used here.** In this exercise 4 of 8 sets use a constrained deadline. The split into 5 feasible and 3 infeasible sets is the [E] verdict, not a guess.


<!-- page 8 -->


## Experimental design

[M] The table below lists every task set used in this exercise. All rows come from the same generator and the same seed; no set was removed because its result was inconvenient. The verdict column is [E]: it is the exhaustive checker's decision over one hyperperiod, with a witness re-checked independently. Periods, execution times, deadlines and phases are integers.

```text
K1: T1(T=4,C=2,D=4,ph=0), T2(T=4,C=2,D=4,ph=0)
K2: T1(T=8,C=4,D=8,ph=0), T2(T=8,C=4,D=8,ph=0)
K3: T1(T=6,C=2,D=6,ph=0), T2(T=6,C=2,D=6,ph=0), T3(T=6,C=2,D=6,ph=0)
K4: T1(T=8,C=2,D=8,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=8,C=2,D=8,ph=0), T4(T=8,C=2,D=8,ph=0)
K5: T1(T=6,C=3,D=4,ph=0), T2(T=9,C=3,D=5,ph=0), T3(T=12,C=2,D=7,ph=0)
K6: T1(T=5,C=2,D=3,ph=0), T2(T=6,C=2,D=3,ph=0)
K7: T1(T=5,C=2,D=3,ph=0), T2(T=5,C=2,D=3,ph=0), T3(T=10,C=3,D=6,ph=0)
K8: T1(T=4,C=2,D=3,ph=0), T2(T=4,C=3,D=4,ph=3)
```
*Full task specifications, read from the data file*

| Set | U | hyperperiod | D < T | verdict |
|---|---|---|---|---|
| K1 | 1.0 | 4 | no | feasible |
| K2 | 1.0 | 8 | no | feasible |
| K3 | 1.0 | 6 | no | feasible |
| K4 | 1.0 | 8 | no | feasible |
| K5 | 1.0 | 36 | yes | infeasible |
| K6 | 0.733333 | 30 | yes | infeasible |
| K7 | 1.1 | 10 | yes | infeasible |
| K8 | 1.25 | 4 | yes | feasible |

*Task sets used, read from experiments.json*

| Random seed | 20261116 |
|---|---|
| Policies measured | 9 |
| Feasible sets [E] | 5 |
| Infeasible sets [E] | 3 |
| Checker states visited [E] | 59 |
| Truncated checker runs | 0 |

*Generated data at a glance*


<!-- page 9 -->


## A worked schedule

The schedule below is reproduced from the generated data, not typed by hand. Each row is a maximal run of one job on the processor. It is the object that a hand computation must match unit for unit; the agreement between an independent hand trace and the simulator's timeline is itself a test in this repository.

```text
T1#0  [0, 1)
T2#0  [1, 2)
T1#0  [2, 3)
T2#0  [3, 4)
T1#1  [4, 5)
T2#1  [5, 6)
T1#1  [6, 7)
T2#1  [7, 8)
```
*Runs read from the generated data*

| Values read from | output/experiments.json |
|---|---|

*Trace provenance*

> **Why two programs.** The hand trace and the simulator are two independent programs. Their agreement is checked by a test, and their disagreement would be reported as an instrument defect.


<!-- page 10 -->


## Task set K1

| Task specification | T1(T=4,C=2,D=4,ph=0), T2(T=4,C=2,D=4,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.0 |
| Hyperperiod | 4 |
| Constrained deadline | no |
| Checker verdict [E] | feasible |
| States visited [E] | 5 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 2 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 4 | 8 | 0 | 0 | 4 |
| lst:edf | 0 | 4 | 8 | 0 | 0 | 4 |
| lst:rm | 0 | 4 | 8 | 0 | 0 | 4 |
| lst:stay | 0 | 2 | 6 | 0 | 0 | 4 |
| lst:lzs | 0 | 4 | 8 | 0 | 0 | 4 |
| edf | 0 | 0 | 4 | 0 | 0 | 2 |
| rm | 0 | 0 | 4 | 0 | 0 | 2 |
| dm | 0 | 0 | 4 | 0 | 0 | 2 |
| fifo | 0 | 0 | 4 | 0 | 0 | 2 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 5 states, 0 pruned, independent witness valid. [M] LST recorded 4 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 4.


<!-- page 11 -->


## Task set K2

| Task specification | T1(T=8,C=4,D=8,ph=0), T2(T=8,C=4,D=8,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.0 |
| Hyperperiod | 8 |
| Constrained deadline | no |
| Checker verdict [E] | feasible |
| States visited [E] | 9 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 2 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 12 | 16 | 0 | 0 | 8 |
| lst:edf | 0 | 12 | 16 | 0 | 0 | 8 |
| lst:rm | 0 | 12 | 16 | 0 | 0 | 8 |
| lst:stay | 0 | 6 | 10 | 0 | 0 | 8 |
| lst:lzs | 0 | 12 | 16 | 0 | 0 | 8 |
| edf | 0 | 0 | 4 | 0 | 0 | 2 |
| rm | 0 | 0 | 4 | 0 | 0 | 2 |
| dm | 0 | 0 | 4 | 0 | 0 | 2 |
| fifo | 0 | 0 | 4 | 0 | 0 | 2 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 9 states, 0 pruned, independent witness valid. [M] LST recorded 12 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 8.


<!-- page 12 -->


## Task set K3

| Task specification | T1(T=6,C=2,D=6,ph=0), T2(T=6,C=2,D=6,ph=0), T3(T=6,C=2,D=6,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.0 |
| Hyperperiod | 6 |
| Constrained deadline | no |
| Checker verdict [E] | feasible |
| States visited [E] | 7 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 3 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 6 | 12 | 0 | 0 | 8 |
| lst:edf | 0 | 6 | 12 | 0 | 0 | 8 |
| lst:rm | 0 | 6 | 12 | 0 | 0 | 8 |
| lst:stay | 0 | 4 | 10 | 0 | 0 | 8 |
| lst:lzs | 0 | 6 | 12 | 0 | 0 | 8 |
| edf | 0 | 0 | 6 | 0 | 0 | 6 |
| rm | 0 | 0 | 6 | 0 | 0 | 6 |
| dm | 0 | 0 | 6 | 0 | 0 | 6 |
| fifo | 0 | 0 | 6 | 0 | 0 | 6 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 7 states, 0 pruned, independent witness valid. [M] LST recorded 6 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 8.


<!-- page 13 -->


## Task set K4

| Task specification | T1(T=8,C=2,D=8,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=8,C=2,D=8,ph=0), T4(T=8,C=2,D=8,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.0 |
| Hyperperiod | 8 |
| Constrained deadline | no |
| Checker verdict [E] | feasible |
| States visited [E] | 9 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 4 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 8 | 16 | 0 | 0 | 12 |
| lst:edf | 0 | 8 | 16 | 0 | 0 | 12 |
| lst:rm | 0 | 8 | 16 | 0 | 0 | 12 |
| lst:stay | 0 | 6 | 14 | 0 | 0 | 12 |
| lst:lzs | 0 | 8 | 16 | 0 | 0 | 12 |
| edf | 0 | 0 | 8 | 0 | 0 | 10 |
| rm | 0 | 0 | 8 | 0 | 0 | 10 |
| dm | 0 | 0 | 8 | 0 | 0 | 10 |
| fifo | 0 | 0 | 8 | 0 | 0 | 10 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 9 states, 0 pruned, independent witness valid. [M] LST recorded 8 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 12.


<!-- page 14 -->


## Task set K5

| Task specification | T1(T=6,C=3,D=4,ph=0), T2(T=9,C=3,D=5,ph=0), T3(T=12,C=2,D=7,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.0 |
| Hyperperiod | 36 |
| Constrained deadline | yes |
| Checker verdict [E] | infeasible |
| States visited [E] | 11 |
| Branches pruned [E] | 14 |
| Jobs in checker horizon | 13 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | not applicable |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 16 | 12 | 38 | 6 | -2 | 16 |
| lst:edf | 16 | 12 | 38 | 6 | -2 | 16 |
| lst:rm | 20 | 20 | 46 | 8 | -2 | 16 |
| lst:stay | 20 | 12 | 38 | 2 | -2 | 16 |
| lst:lzs | 16 | 12 | 38 | 6 | -2 | 16 |
| edf | 14 | 0 | 26 | 2 | -2 | 10 |
| rm | 10 | 2 | 28 | 0 | -15 | 2 |
| dm | 10 | 2 | 28 | 0 | -15 | 2 |
| fifo | 14 | 0 | 26 | 2 | -2 | 10 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict infeasible, 11 states, 14 pruned, independent witness not applicable. [M] LST recorded 12 preemptions and 16 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 16.


<!-- page 15 -->


## Task set K6

| Task specification | T1(T=5,C=2,D=3,ph=0), T2(T=6,C=2,D=3,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.733333 |
| Hyperperiod | 30 |
| Constrained deadline | yes |
| Checker verdict [E] | infeasible |
| States visited [E] | 5 |
| Branches pruned [E] | 4 |
| Jobs in checker horizon | 11 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | not applicable |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 2 | 4 | 26 | 2 | -1 | 8 |
| lst:edf | 2 | 4 | 26 | 2 | -1 | 8 |
| lst:rm | 2 | 8 | 30 | 4 | -1 | 8 |
| lst:stay | 2 | 2 | 24 | 0 | -1 | 8 |
| lst:lzs | 2 | 4 | 26 | 2 | -1 | 8 |
| edf | 2 | 0 | 22 | 0 | -1 | 6 |
| rm | 4 | 2 | 24 | 0 | -1 | 6 |
| dm | 4 | 2 | 24 | 0 | -1 | 6 |
| fifo | 2 | 0 | 22 | 0 | -1 | 6 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict infeasible, 5 states, 4 pruned, independent witness not applicable. [M] LST recorded 4 preemptions and 2 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 8.


<!-- page 16 -->


## Task set K7

| Task specification | T1(T=5,C=2,D=3,ph=0), T2(T=5,C=2,D=3,ph=0), T3(T=10,C=3,D=6,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.1 |
| Hyperperiod | 10 |
| Constrained deadline | yes |
| Checker verdict [E] | infeasible |
| States visited [E] | 6 |
| Branches pruned [E] | 10 |
| Jobs in checker horizon | 5 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | not applicable |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 9 | 7 | 16 | 1 | -3 | 7 |
| lst:edf | 9 | 7 | 16 | 1 | -3 | 7 |
| lst:rm | 9 | 7 | 16 | 1 | -3 | 7 |
| lst:stay | 9 | 4 | 13 | 0 | -3 | 7 |
| lst:lzs | 9 | 7 | 16 | 1 | -3 | 7 |
| edf | 8 | 0 | 9 | 0 | -3 | 4 |
| rm | 6 | 2 | 12 | 0 | -9 | 1 |
| dm | 6 | 2 | 12 | 0 | -9 | 1 |
| fifo | 8 | 0 | 9 | 0 | -3 | 4 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict infeasible, 6 states, 10 pruned, independent witness not applicable. [M] LST recorded 7 preemptions and 9 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 7.


<!-- page 17 -->


## Task set K8

| Task specification | T1(T=4,C=2,D=3,ph=0), T2(T=4,C=3,D=4,ph=3) |
|---|---|
| Utilisation (descriptive) | 1.25 |
| Hyperperiod | 4 |
| Constrained deadline | yes |
| Checker verdict [E] | feasible |
| States visited [E] | 7 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 2 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | no |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 1 | 2 | 5 | 1 | -1 | 2 |
| lst:edf | 1 | 2 | 5 | 1 | -1 | 2 |
| lst:rm | 1 | 2 | 5 | 1 | -1 | 2 |
| lst:stay | 1 | 1 | 4 | 0 | -1 | 2 |
| lst:lzs | 1 | 2 | 5 | 1 | -1 | 2 |
| edf | 1 | 0 | 3 | 0 | -1 | 1 |
| rm | 1 | 0 | 3 | 0 | -1 | 1 |
| dm | 1 | 1 | 4 | 0 | -1 | 1 |
| fifo | 1 | 0 | 3 | 0 | -1 | 1 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 7 states, 0 pruned, independent witness valid. [M] LST recorded 2 preemptions and 1 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 2.


<!-- page 18 -->


## Sweeps: task-count

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[0] |
|---|---|
| Swept parameter | number of equal tasks |

*Provenance*

![Figure 1: Sweep task-count: number of equal tasks — values from sweeps[0]](fig_ex7_taskcount.png)

*Figure 1. Sweep task-count: number of equal tasks — values from sweeps[0]*

| number of equal tasks | lst_preemptions | lst:edf_preemptions | lst:rm_preemptions | lst:stay_preemptions | lst:lzs_preemptions |
|---|---|---|---|---|---|
| 2 | 4 | 4 | 4 | 2 | 4 |
| 3 | 6 | 6 | 6 | 4 | 6 |
| 4 | 8 | 8 | 8 | 6 | 8 |
| 5 | 10 | 10 | 10 | 8 | 10 |

*Values behind the plot*

> **Reading the sweep.** 4 points and 5 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 19 -->


## Sweeps: deadline-zero-switches

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[1] |
|---|---|
| Swept parameter | shared deadline (time units) |

*Provenance*

![Figure 2: Sweep deadline-zero-switches: shared deadline (time units) — values from sweeps[1]](fig_ex7_deadline_lzs.png)

*Figure 2. Sweep deadline-zero-switches: shared deadline (time units) — values from sweeps[1]*

| shared deadline (time units) | lst_laxity_zero_switches | lst:edf_laxity_zero_switches | lst:rm_laxity_zero_switches | lst:stay_laxity_zero_switches | lst:lzs_laxity_zero_switches |
|---|---|---|---|---|---|
| 4 | 0 | 0 | 0 | 0 | 0 |
| 5 | 2 | 2 | 2 | 0 | 2 |
| 6 | 2 | 2 | 2 | 0 | 2 |
| 7 | 2 | 2 | 2 | 0 | 2 |
| 8 | 0 | 0 | 0 | 0 | 0 |

*Values behind the plot*

> **Reading the sweep.** 5 points and 5 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 20 -->


## Sweeps: alignment

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[2] |
|---|---|
| Swept parameter | task set |

*Provenance*

![Figure 3: Sweep alignment: task set — values from sweeps[2]](fig_ex7_alignment.png)

*Figure 3. Sweep alignment: task set — values from sweeps[2]*

| task set | naive_lst_missed | aligned_lst_missed | checker_feasible |
|---|---|---|---|
| K1 | 0 | 0 | 1 |
| K2 | 0 | 0 | 1 |
| K3 | 0 | 0 | 1 |
| K4 | 0 | 0 | 1 |
| K5 | 16 | 8 | 0 |
| K6 | 2 | 1 | 0 |
| K7 | 9 | 4 | 0 |
| K8 | 1 | 0 | 1 |

*Values behind the plot*

> **Reading the sweep.** 8 points and 3 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 21 -->


## Finding: F1


### Minimising slack is not minimising overhead

[M] measurement

[M] On K1, LST records 4 preemptions and 8 context switches; EDF records 0 and 4. Both miss 0 deadlines. [E] The checker verdict is feasible after 5 states. Correctness does not order these two policies; overhead does.

| Key | Value |
|---|---|
| checker states | 5 |
| edf preemptions | 0 |
| edf switches | 4 |
| lst preemptions | 4 |
| lst switches | 8 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 22 -->


## Finding: F2


### Implicit deadlines take the test away

[E] + [M]

[E] Of 4 sets with implicit deadlines, 4 are feasible. Of 4 constrained sets, 1 are feasible and 3 are infeasible. Feasibility has discriminating power only in the constrained regime; that is why every sweep here moves a deadline rather than a definition.

| Key | Value |
|---|---|
| constrained feasible | 1 |
| constrained infeasible | 3 |
| constrained sets | 4 |
| implicit feasible | 4 |
| implicit sets | 4 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 23 -->


## Finding: F3


### Naive versus aligned comparison

[D] disagreement

[D] On K8 the checker says feasible, yet the naive two-hyperperiod LST run misses 1 deadlines while the aligned run misses 0. The two instruments were looking at different job sets. Aligning the release window removes the disagreement; the instrument, not the theorem, was at fault.

| Key | Value |
|---|---|
| aligned agree | 8 |
| aligned missed target | 0 |
| naive agree | 7 |
| naive missed target | 1 |
| set count | 8 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 24 -->


## Finding: F4


### A state cap fabricates an infeasibility verdict

[D] disagreement

[D] With a reduced state cap, K1 is reported infeasible 1 times, each run flagged truncated; with the cap restored the verdict is feasible after 5 states. The smallest truncating cap was 4. A truncated run is an artefact of the instrument and is never used as a finding.

| Key | Value |
|---|---|
| false infeasible runs | 1 |
| full feasible | 1 |
| full states | 5 |
| smallest truncating limit | 4 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 25 -->


## Finding: F5


### Tie-breaking changes the cost, not the verdict

[M] measurement

[E] On all 5 feasible sets the checker's verdict is unchanged by the choice of tie-break, and 0 sets show a tie-break changing LST's zero-miss status at all. [M] On K2, lst records 12 preemptions while lst:stay records 6 and EDF 0. The widest spread between two tie-breaks is 8 preemptions on K5. Verification treats these as the same feasible outcome; the machine does not.

| Key | Value |
|---|---|
| edf preemptions K2 | 0 |
| feasible sets | 5 |
| lst preemptions K2 | 12 |
| stay preemptions K2 | 6 |
| verdict changing sets | 0 |
| widest spread | 8 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 26 -->


## Finding: F6


### Laxity-zero thrashing is measurable, and the cheap policy is not cheap on every metric

[M] measurement

[M] On K5, lst records 6 switches at zero laxity, lst:stay records 2 and EDF 2; the largest value over all sets is 6. Yet on 6 sets LST has strictly smaller response jitter than EDF even though it preempts more: on K2 the jitters are 1 and 4. A single metric would have hidden this. We report the trade-off rather than declaring a winner the data does not support.

| Key | Value |
|---|---|
| edf jitter K2 | 4 |
| edf zero switches K5 | 2 |
| lst jitter K2 | 1 |
| lst lower jitter sets | 6 |
| lst zero switches K5 | 6 |
| max zero switches | 6 |
| stay zero switches K5 | 2 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 27 -->


## Figures — group 1

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 4: Preemptions by policy on K1 — values from task_sets[0].policies.*.preemptions](fig_ex7_preemptions.png)

*Figure 4. Preemptions by policy on K1 — values from task_sets[0].policies.*.preemptions*

![Figure 5: Missed deadlines per set and policy — values from task_sets[*].policies.*.missed](fig_ex7_misses.png)

*Figure 5. Missed deadlines per set and policy — values from task_sets[*].policies.*.missed*


<!-- page 28 -->


## Figures — group 2

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 6: Tie events per set and policy — values from task_sets[*].policies.*.tie_events](fig_ex7_ties.png)

*Figure 6. Tie events per set and policy — values from task_sets[*].policies.*.tie_events*

![Figure 7: lst schedule on K1 — values from task_sets[0].gantt.lst](fig_ex7_gantt.png)

*Figure 7. lst schedule on K1 — values from task_sets[0].gantt.lst*


<!-- page 29 -->


## Figures — group 3

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 8: Preemptions by LST tie-break and task set — values from task_sets[*].policies.*.preemptions](fig_ex7_tiebreak.png)

*Figure 8. Preemptions by LST tie-break and task set — values from task_sets[*].policies.*.preemptions*

![Figure 9: Laxity-zero switches by tie-break and task set — values from task_sets[*].policies.*.laxity_zero_switches](fig_ex7_lzs.png)

*Figure 9. Laxity-zero switches by tie-break and task set — values from task_sets[*].policies.*.laxity_zero_switches*


<!-- page 30 -->


## Figures — group 4

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 10: Response jitter: LST, stay, EDF — values from task_sets[*].policies.*.jitter](fig_ex7_jitter.png)

*Figure 10. Response jitter: LST, stay, EDF — values from task_sets[*].policies.*.jitter*


<!-- page 31 -->


## When the two instruments disagree

The naive comparison puts a checker over one hyperperiod next to a simulator running two hyperperiods. Those two are not looking at the same job set, so a mismatch is expected and is an artefact of the instrument, not a discovery about scheduling. The aligned comparison gives both instruments the jobs released in one hyperperiod and enough time to finish them. The counts below show how much of the apparent disagreement disappears once the instruments are aligned. This is the same lesson learned earlier in this project, when the checker called a feasible set infeasible because it treated a forced idle instant as a dead end: the bug was in the checker.

| Set | checker | naive agrees | aligned agrees | aligned horizon |
|---|---|---|---|---|
| K1 | feasible | yes | yes | 8 |
| K2 | feasible | yes | yes | 16 |
| K3 | feasible | yes | yes | 12 |
| K4 | feasible | yes | yes | 16 |
| K5 | infeasible | yes | yes | 43 |
| K6 | infeasible | yes | yes | 33 |
| K7 | infeasible | yes | yes | 16 |
| K8 | feasible | no | yes | 8 |

*Naive versus aligned comparison*

| Naive comparisons agreeing | 7 |
|---|---|
| Aligned comparisons agreeing | 8 |
| Task sets | 8 |
| Truncated checker runs | 0 |
| [E] RM counterexamples | 1 |
| [M] witness cheaper than LST | 5 |
| [D] cap artefacts | 5 |

*Agreement counts [D]*

> **Instrument alignment.** Naive comparisons that agree: 7. Aligned comparisons that agree: 8. The difference is measured, not argued.


<!-- page 32 -->


## A defect produced by a state cap

The checker has a state cap. With the cap set low, the very same task set that the full checker proves feasible is reported infeasible and the run is flagged truncated. [D] This is a disagreement between the instrument and the data, and the instrument is the suspect. [E] With the cap restored the verdict returns to feasible. A truncated run is never used as a finding anywhere in this project; it is reported as an artefact, with the limit and the state count that produced it.

| Cap on states | verdict | states visited | truncated |
|---|---|---|---|
| 4 | infeasible | 7 | yes |
| 8 | feasible | 5 | no |
| 16 | feasible | 5 | no |
| 4000000 | feasible | 5 | no |

*Checker verdict as a function of the cap [D]*

| Task specification | T1(T=4,C=2,D=4,ph=0), T2(T=4,C=2,D=4,ph=0) |
|---|---|
| [D] false infeasible verdicts | 1 |
| [E] full verdict | feasible |

*The same set under different caps*

> **Artefacts, not findings.** Across the 8 sets of this exercise, 5 produce a false infeasible verdict under a reduced cap. None of those verdicts is used as a result.


<!-- page 33 -->


## Verification is coarse, measurement is not

[E] The checker answers one question: does a feasible schedule exist. The witness it returns is one such schedule. [M] The simulator counts what that witness costs and what LST costs on the same task set. When the two numbers differ, the schedules are equivalent for verification and very different for the machine. This is not a contradiction; it is the limit of what a feasibility verdict can promise, made visible by measurement. A claim that all optimal schedules cost the same is refuted by the witness rows below.

| Set | witness preemptions | LST preemptions | EDF preemptions | witness valid |
|---|---|---|---|---|
| K1 | 0 | 4 | 0 | yes |
| K2 | 0 | 12 | 0 | yes |
| K3 | 0 | 6 | 0 | yes |
| K4 | 0 | 8 | 0 | yes |
| K5 | 0 | 12 | 0 | no |
| K6 | 0 | 4 | 0 | no |
| K7 | 0 | 7 | 0 | no |
| K8 | 0 | 2 | 0 | yes |

*Witness cost versus policy cost [M]*

| [M] sets where the witness is cheaper | 5 |
|---|---|
| [E] independently valid witnesses | 5 |
| [E] RM counterexamples | 1 |

*What the two instruments can say*

> **Complement, not contradiction.** A feasibility verdict is a coarse equivalence: it groups schedules that measurement can separate. Reporting the grouping as if it were a cost claim would be the mistake.


<!-- page 34 -->


## Limitations we state ourselves

The model is a single preemptive processor with no release cost, no cache or migration effects and execution equal to the worst case. Therefore these measurements say nothing about multicore behaviour or about runtime variance. The checker's verdict is exact only for the enumerated job set and only when its run was not truncated; every truncation flag is reported and no conclusion is drawn from a truncated run. Utilisation is a descriptive ratio here, never a schedulability test. Finally, a measurement that does not separate two policies is reported as inconclusive rather than as a tie broken by preference.

- single processor; no multicore or migration claim
- execution equals worst case; no runtime variance
- checker state cap; every truncation is reported
- integer time; no floating tolerance needed
- overlapping ranges are called inconclusive

> **Stated in advance.** A result obtained from a truncated checker state space is an artefact of the cap. It is never reported as a finding.


<!-- page 35 -->


## Reproducibility

Every artefact is regenerated by the commands below, from the exercise folder or from the multi-exercise tree root. The seed, the policy list and the figure list are read from the generated data; deleting any output file and re-running must reproduce byte-identical numbers. The report itself is built from a content module that contains prose only.

```text
python3 code/run_experiments.py
python3 code/make_diagrams.py
python3 -m pytest tests -q
python3 tools/build_report.py lstN_en exercise-N REPORT_EN
python3 tools/build_report.py lstN_fa exercise-N REPORT_FA
python3 tools/check_outputs.py exercise-N
```
*Commands (from the exercise folder / tree root)*

| Random seed | 20261116 |
|---|---|
| Policies measured | lst, lst:edf, lst:rm, lst:stay, lst:lzs, edf, rm, dm, fifo |
| Figures | 10 |
| Findings | 6 |
| Sweeps | 3 |

*Data file summary*

> **Definition of a clean build.** A clean build is defined as empty overflow, missing figures and missing glyphs lists, with the generator's page count equal to the PDF page count.


<!-- page 36 -->


## Deliverables and checks

The table lists the artefacts of this exercise. Word and PDF are rendered from one content model, so their page counts agree with the generator's explicit page list; the exact PDF count is read back from the file by the checker. The Markdown file is a by-product of the same model. Speaker decks, where required, carry notes on every slide.

| Artefact | kind | how it is produced |
|---|---|---|
| REPORT_EN.docx / REPORT_EN.pdf | English report | tools/build_report.py lst7_en |
| REPORT_FA.docx / REPORT_FA.pdf | Persian report | tools/build_report.py lst7_fa |
| output/experiments.json | all numbers | code/run_experiments.py |
| diagrams/ | generated figures | code/make_diagrams.py |
| tests/ | green tests | python3 -m pytest |

*Artefact table*

| Figures | 10 |
|---|---|
| Findings | 6 |
| Independently valid witnesses | 5 |
| Truncated checker runs | 0 |

*Checks*

> **Two kinds of page count.** Word page counts are estimated by the checker against the real section geometry; PDF page counts are exact because they are read back from the file.


<!-- page 37 -->


## Appendix: the data contract

The generated data file is the single source of numbers. Its top-level keys are listed below together with what they contain. A test in this repository checks that every numeric token in the generated report also occurs in this file or in values derived from it; a typed-in measurement would fail that test.

```text
top-level keys of output/experiments.json:
  figures
  findings
  meta
  sweeps
  task_sets
```
*Data contract*

| Key | Contains |
|---|---|
| meta | seed, policies, scope |
| task_sets | per-set measurements and [E] verdicts |
| sweeps | parameter sweeps |
| findings | tagged findings |
| figures | plot specifications and JSON paths |

*Key meanings*

> **Enforced by a test.** If a number appears in this report that cannot be found in the data file, the provenance test fails and the report is rebuilt.
