# LST against EDF and RM on Measured Workloads

**nine policies, several workload families, several metrics**

- **Exercise:** Exercise 2
- **Course:** Real-Time Scheduling
- **Topic:** Least Slack Time (LST) scheduling
- **Deliverables:** bilingual EN/FA report, DOCX + PDF; diagrams; code; tests
- **Repository:** github.com/rera13197-ux/LST
- **Branch:** Exercise-2-LST-EDF-RM-Comparison
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
- Task set W1 (p. 10)
- Task set W2 (p. 11)
- Task set W3 (p. 12)
- Task set W4 (p. 13)
- Task set W5 (p. 14)
- Task set W6 (p. 15)
- Task set W7 (p. 16)
- Task set W8 (p. 17)
- Sweeps: misses (p. 18)
- Sweeps: preemptions (p. 19)
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
- When the two instruments disagree (p. 30)
- A defect produced by a state cap (p. 31)
- Verification is coarse, measurement is not (p. 32)
- Limitations we state ourselves (p. 33)
- Reproducibility (p. 34)
- Deliverables and checks (p. 35)
- Appendix: the data contract (p. 36)


<!-- page 1 -->


<!-- page 2 -->


<!-- page 3 -->


## The question

How does LST compare with EDF and RM on light, heavy, harmonic and constrained-deadline workloads, on more than one metric?

This report states what was asked and how it was answered before giving any result, so that a reader can try to refute the claim.

| Instrument | [E] + [M] |
|---|---|
| Scope | nine policies over light, heavy, harmonic, non-harmonic, phased and tight workloads, with misses, preemptions, jitter and switch counts |
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

> **The split used here.** In this exercise 7 of 8 sets use a constrained deadline. The split into 5 feasible and 3 infeasible sets is the [E] verdict, not a guess.


<!-- page 8 -->


## Experimental design

[M] The table below lists every task set used in this exercise. All rows come from the same generator and the same seed; no set was removed because its result was inconvenient. The verdict column is [E]: it is the exhaustive checker's decision over one hyperperiod, with a witness re-checked independently. Periods, execution times, deadlines and phases are integers.

```text
W1: T1(T=10,C=2,D=8,ph=0), T2(T=20,C=3,D=15,ph=0)
W2: T1(T=6,C=2,D=6,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=12,C=3,D=12,ph=0)
W3: T1(T=4,C=1,D=3,ph=0), T2(T=8,C=2,D=6,ph=0), T3(T=16,C=4,D=12,ph=0)
W4: T1(T=5,C=2,D=4,ph=0), T2(T=7,C=2,D=5,ph=0), T3(T=11,C=3,D=8,ph=0)
W5: T1(T=4,C=1,D=3,ph=0), T2(T=5,C=2,D=4,ph=0), T3(T=20,C=3,D=12,ph=0)
W6: T1(T=5,C=2,D=3,ph=0), T2(T=10,C=3,D=6,ph=0), T3(T=10,C=2,D=7,ph=0)
W7: T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=2), T3(T=12,C=3,D=7,ph=1)
W8: T1(T=5,C=2,D=3,ph=0), T2(T=6,C=2,D=3,ph=0)
```
*Full task specifications, read from the data file*

| Set | U | hyperperiod | D < T | verdict |
|---|---|---|---|---|
| W1 | 0.35 | 20 | yes | feasible |
| W2 | 0.833333 | 24 | no | feasible |
| W3 | 0.75 | 16 | yes | feasible |
| W4 | 0.958442 | 385 | yes | infeasible |
| W5 | 0.8 | 20 | yes | feasible |
| W6 | 0.9 | 10 | yes | infeasible |
| W7 | 0.833333 | 24 | yes | feasible |
| W8 | 0.733333 | 30 | yes | infeasible |

*Task sets used, read from experiments.json*

| Random seed | 20261116 |
|---|---|
| Policies measured | 9 |
| Feasible sets [E] | 5 |
| Infeasible sets [E] | 3 |
| Checker states visited [E] | 197 |
| Truncated checker runs | 0 |

*Generated data at a glance*


<!-- page 9 -->


## A worked schedule

The schedule below is reproduced from the generated data, not typed by hand. Each row is a maximal run of one job on the processor. It is the object that a hand computation must match unit for unit; the agreement between an independent hand trace and the simulator's timeline is itself a test in this repository.

```text
T1#0  [0, 2)
T2#0  [2, 5)
T1#1  [10, 12)
T1#2  [20, 22)
T2#1  [22, 25)
T1#3  [30, 32)
```
*Runs read from the generated data*

| Values read from | output/experiments.json |
|---|---|

*Trace provenance*

> **Why two programs.** The hand trace and the simulator are two independent programs. Their agreement is checked by a test, and their disagreement would be reported as an instrument defect.


<!-- page 10 -->


## Task set W1

| Task specification | T1(T=10,C=2,D=8,ph=0), T2(T=20,C=3,D=15,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.35 |
| Hyperperiod | 20 |
| Constrained deadline | yes |
| Checker verdict [E] | feasible |
| States visited [E] | 13 |
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
| lst | 0 | 0 | 6 | 0 | 6 | 0 |
| lst:edf | 0 | 0 | 6 | 0 | 6 | 0 |
| lst:rm | 0 | 0 | 6 | 0 | 6 | 0 |
| lst:stay | 0 | 0 | 6 | 0 | 6 | 0 |
| lst:lzs | 0 | 0 | 6 | 0 | 6 | 0 |
| edf | 0 | 0 | 6 | 0 | 6 | 0 |
| rm | 0 | 0 | 6 | 0 | 6 | 0 |
| dm | 0 | 0 | 6 | 0 | 6 | 0 |
| fifo | 0 | 0 | 6 | 0 | 6 | 0 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 13 states, 0 pruned, independent witness valid. [M] LST recorded 0 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 0.


<!-- page 11 -->


## Task set W2

| Task specification | T1(T=6,C=2,D=6,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=12,C=3,D=12,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.833333 |
| Hyperperiod | 24 |
| Constrained deadline | no |
| Checker verdict [E] | feasible |
| States visited [E] | 22 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 9 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 10 | 28 | 0 | 3 | 6 |
| lst:edf | 0 | 10 | 28 | 0 | 3 | 6 |
| lst:rm | 0 | 4 | 22 | 0 | 3 | 6 |
| lst:stay | 0 | 4 | 22 | 0 | 3 | 6 |
| lst:lzs | 0 | 10 | 28 | 0 | 3 | 6 |
| edf | 0 | 0 | 18 | 0 | 3 | 0 |
| rm | 0 | 4 | 22 | 0 | 1 | 6 |
| dm | 0 | 4 | 22 | 0 | 1 | 6 |
| fifo | 0 | 0 | 18 | 0 | 3 | 0 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 22 states, 0 pruned, independent witness valid. [M] LST recorded 10 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 6.


<!-- page 12 -->


## Task set W3

| Task specification | T1(T=4,C=1,D=3,ph=0), T2(T=8,C=2,D=6,ph=0), T3(T=16,C=4,D=12,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.75 |
| Hyperperiod | 16 |
| Constrained deadline | yes |
| Checker verdict [E] | feasible |
| States visited [E] | 14 |
| Branches pruned [E] | 1 |
| Jobs in checker horizon | 7 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 2 | 16 | 0 | 2 | 0 |
| lst:edf | 0 | 2 | 16 | 0 | 2 | 0 |
| lst:rm | 0 | 2 | 16 | 0 | 2 | 0 |
| lst:stay | 0 | 2 | 16 | 0 | 2 | 0 |
| lst:lzs | 0 | 2 | 16 | 0 | 2 | 0 |
| edf | 0 | 2 | 16 | 0 | 2 | 0 |
| rm | 0 | 2 | 16 | 0 | 2 | 0 |
| dm | 0 | 2 | 16 | 0 | 2 | 0 |
| fifo | 2 | 0 | 14 | 0 | -1 | 0 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 14 states, 1 pruned, independent witness valid. [M] LST recorded 2 preemptions and 0 missed deadlines; EDF recorded 2 preemptions on the same set. Tie events observed: 0.


<!-- page 13 -->


## Task set W4

| Task specification | T1(T=5,C=2,D=4,ph=0), T2(T=7,C=2,D=5,ph=0), T3(T=11,C=3,D=8,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.958442 |
| Hyperperiod | 385 |
| Constrained deadline | yes |
| Checker verdict [E] | infeasible |
| States visited [E] | 80 |
| Branches pruned [E] | 34 |
| Jobs in checker horizon | 167 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | not applicable |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 2 | 162 | 496 | 2 | -1 | 136 |
| lst:edf | 2 | 124 | 458 | 0 | -1 | 136 |
| lst:rm | 2 | 158 | 492 | 10 | -1 | 136 |
| lst:stay | 2 | 82 | 416 | 2 | -1 | 136 |
| lst:lzs | 2 | 162 | 496 | 2 | -1 | 136 |
| edf | 2 | 38 | 372 | 0 | -1 | 92 |
| rm | 40 | 110 | 444 | 0 | -5 | 96 |
| dm | 40 | 110 | 444 | 0 | -5 | 96 |
| fifo | 16 | 0 | 334 | 6 | -2 | 68 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict infeasible, 80 states, 34 pruned, independent witness not applicable. [M] LST recorded 162 preemptions and 2 missed deadlines; EDF recorded 38 preemptions on the same set. Tie events observed: 136.


<!-- page 14 -->


## Task set W5

| Task specification | T1(T=4,C=1,D=3,ph=0), T2(T=5,C=2,D=4,ph=0), T3(T=20,C=3,D=12,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.8 |
| Hyperperiod | 20 |
| Constrained deadline | yes |
| Checker verdict [E] | feasible |
| States visited [E] | 19 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 10 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 4 | 24 | 0 | 1 | 4 |
| lst:edf | 0 | 4 | 24 | 0 | 1 | 4 |
| lst:rm | 0 | 6 | 26 | 0 | 1 | 4 |
| lst:stay | 0 | 4 | 24 | 0 | 1 | 4 |
| lst:lzs | 0 | 4 | 24 | 0 | 1 | 4 |
| edf | 0 | 4 | 24 | 0 | 1 | 4 |
| rm | 0 | 6 | 26 | 0 | 1 | 4 |
| dm | 0 | 6 | 26 | 0 | 1 | 4 |
| fifo | 0 | 0 | 20 | 2 | 0 | 4 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 19 states, 0 pruned, independent witness valid. [M] LST recorded 4 preemptions and 0 missed deadlines; EDF recorded 4 preemptions on the same set. Tie events observed: 4.


<!-- page 15 -->


## Task set W6

| Task specification | T1(T=5,C=2,D=3,ph=0), T2(T=10,C=3,D=6,ph=0), T3(T=10,C=2,D=7,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.9 |
| Hyperperiod | 10 |
| Constrained deadline | yes |
| Checker verdict [E] | infeasible |
| States visited [E] | 21 |
| Branches pruned [E] | 15 |
| Jobs in checker horizon | 4 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | not applicable |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 2 | 0 | 8 | 0 | -1 | 4 |
| lst:edf | 2 | 0 | 8 | 0 | -1 | 4 |
| lst:rm | 4 | 4 | 12 | 2 | -1 | 4 |
| lst:stay | 2 | 0 | 8 | 0 | -1 | 4 |
| lst:lzs | 2 | 0 | 8 | 0 | -1 | 4 |
| edf | 2 | 0 | 8 | 0 | -1 | 4 |
| rm | 2 | 0 | 8 | 0 | -2 | 2 |
| dm | 2 | 0 | 8 | 0 | -2 | 2 |
| fifo | 2 | 0 | 8 | 0 | -1 | 4 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict infeasible, 21 states, 15 pruned, independent witness not applicable. [M] LST recorded 0 preemptions and 2 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 4.


<!-- page 16 -->


## Task set W7

| Task specification | T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=2), T3(T=12,C=3,D=7,ph=1) |
|---|---|
| Utilisation (descriptive) | 0.833333 |
| Hyperperiod | 24 |
| Constrained deadline | yes |
| Checker verdict [E] | feasible |
| States visited [E] | 23 |
| Branches pruned [E] | 0 |
| Jobs in checker horizon | 9 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | valid |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 0 | 6 | 24 | 0 | 1 | 6 |
| lst:edf | 0 | 4 | 22 | 0 | 1 | 6 |
| lst:rm | 0 | 4 | 22 | 0 | 1 | 6 |
| lst:stay | 0 | 2 | 20 | 0 | 1 | 6 |
| lst:lzs | 0 | 6 | 24 | 0 | 1 | 6 |
| edf | 0 | 0 | 18 | 0 | 1 | 4 |
| rm | 2 | 2 | 20 | 0 | -1 | 4 |
| dm | 2 | 2 | 20 | 0 | -1 | 4 |
| fifo | 0 | 0 | 18 | 0 | 0 | 4 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 23 states, 0 pruned, independent witness valid. [M] LST recorded 6 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 6.


<!-- page 17 -->


## Task set W8

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


<!-- page 18 -->


## Sweeps: misses

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[0] |
|---|---|
| Swept parameter | C of T1 (time units) |

*Provenance*

![Figure 1: Sweep misses: C of T1 (time units) — values from sweeps[0]](fig_ex2_misses_sweep.png)

*Figure 1. Sweep misses: C of T1 (time units) — values from sweeps[0]*

| C of T1 (time units) | lst_missed | edf_missed | rm_missed | checker_feasible |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 1 |
| 2 | 0 | 0 | 0 | 1 |
| 3 | 0 | 0 | 2 | 1 |
| 4 | 11 | 9 | 3 | 0 |

*Values behind the plot*

> **Reading the sweep.** 4 points and 4 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 19 -->


## Sweeps: preemptions

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[1] |
|---|---|
| Swept parameter | C of T1 (time units) |

*Provenance*

![Figure 2: Sweep preemptions: C of T1 (time units) — values from sweeps[1]](fig_ex2_pre_sweep.png)

*Figure 2. Sweep preemptions: C of T1 (time units) — values from sweeps[1]*

| C of T1 (time units) | lst_preemptions | edf_preemptions | rm_preemptions |
|---|---|---|---|
| 1 | 0 | 0 | 0 |
| 2 | 10 | 0 | 4 |
| 3 | 16 | 0 | 4 |
| 4 | 20 | 0 | 1 |

*Values behind the plot*

> **Reading the sweep.** 4 points and 3 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 20 -->


## Sweeps: alignment

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[2] |
|---|---|
| Swept parameter | task set |

*Provenance*

![Figure 3: Sweep alignment: task set — values from sweeps[2]](fig_ex2_alignment.png)

*Figure 3. Sweep alignment: task set — values from sweeps[2]*

| task set | naive_lst_missed | aligned_lst_missed | checker_feasible |
|---|---|---|---|
| W1 | 0 | 0 | 1 |
| W2 | 0 | 0 | 1 |
| W3 | 0 | 0 | 1 |
| W4 | 2 | 1 | 0 |
| W5 | 0 | 0 | 1 |
| W6 | 2 | 1 | 0 |
| W7 | 0 | 0 | 1 |
| W8 | 2 | 1 | 0 |

*Values behind the plot*

> **Reading the sweep.** 8 points and 3 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 21 -->


## Finding: F1


### Minimising slack is not minimising overhead

[M] measurement

[M] On W1, LST records 0 preemptions and 6 context switches; EDF records 0 and 6. Both miss 0 deadlines. [E] The checker verdict is feasible after 13 states. Correctness does not order these two policies; overhead does.

| Key | Value |
|---|---|
| checker states | 13 |
| edf preemptions | 0 |
| edf switches | 6 |
| lst preemptions | 0 |
| lst switches | 6 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 22 -->


## Finding: F2


### Implicit deadlines take the test away

[E] + [M]

[E] Of 1 sets with implicit deadlines, 1 are feasible. Of 7 constrained sets, 4 are feasible and 3 are infeasible. Feasibility has discriminating power only in the constrained regime; that is why every sweep here moves a deadline rather than a definition.

| Key | Value |
|---|---|
| constrained feasible | 4 |
| constrained infeasible | 3 |
| constrained sets | 7 |
| implicit feasible | 1 |
| implicit sets | 1 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 23 -->


## Finding: F3


### Naive versus aligned comparison

[D] disagreement

[D] No naive-versus-aligned mismatch survives on these 8 sets: 8 naive and 8 aligned comparisons agree with the checker. The largest gap in missed deadlines between the two settings is 1 on W4. Reporting a disagreement that the data does not contain would be the mistake.

| Key | Value |
|---|---|
| aligned agree | 8 |
| aligned missed target | 1 |
| naive agree | 8 |
| naive missed target | 2 |
| set count | 8 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 24 -->


## Finding: F4


### A state cap fabricates an infeasibility verdict

[D] disagreement

[D] With a reduced state cap, W1 is reported infeasible 2 times, each run flagged truncated; with the cap restored the verdict is feasible after 13 states. The smallest truncating cap was 4. A truncated run is an artefact of the instrument and is never used as a finding.

| Key | Value |
|---|---|
| false infeasible runs | 2 |
| full feasible | 1 |
| full states | 13 |
| smallest truncating limit | 4 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 25 -->


## Finding: F5


### Cheapest correctness is not LST

[M] measurement

[M] Across all 8 workloads LST records 188 preemptions and 6 missed deadlines, EDF records 44 and 6, and RM records 126 and 48. [E] Wherever the checker says feasible, both LST and EDF meet every deadline in the aligned run, while RM supplies genuine counterexamples. On the raw cost of being correct, EDF wins here; saying LST is better because it is optimal would confuse a verdict with a measurement.

| Key | Value |
|---|---|
| edf missed | 6 |
| edf preemptions | 44 |
| lst missed | 6 |
| lst preemptions | 188 |
| rm missed | 48 |
| rm preemptions | 126 |
| workloads | 8 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 26 -->


## Finding: F6


### Where the correctness metric cannot separate the policies

[M] measurement

[M] On 4 of 8 workloads all three policies miss zero deadlines, so correctness does not separate them at all. Preemptions still do, and so does response jitter: on 0 workloads LST has strictly smaller jitter than EDF even while costing more preemptions. That is not a contradiction and not a ranking; it is a measurement that separates one dimension while another stays inconclusive. The widest such workload is reported in the tables above, not guessed.

| Key | Value |
|---|---|
| all zero miss sets | 4 |
| edf total preemptions | 44 |
| lst lower jitter sets | 0 |
| lst total preemptions | 188 |
| workloads | 8 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 27 -->


## Figures — group 1

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 4: Preemptions by policy on W1 — values from task_sets[0].policies.*.preemptions](fig_ex2_preemptions.png)

*Figure 4. Preemptions by policy on W1 — values from task_sets[0].policies.*.preemptions*

![Figure 5: Missed deadlines per set and policy — values from task_sets[*].policies.*.missed](fig_ex2_misses.png)

*Figure 5. Missed deadlines per set and policy — values from task_sets[*].policies.*.missed*


<!-- page 28 -->


## Figures — group 2

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 6: Tie events per set and policy — values from task_sets[*].policies.*.tie_events](fig_ex2_ties.png)

*Figure 6. Tie events per set and policy — values from task_sets[*].policies.*.tie_events*

![Figure 7: lst schedule on W1 — values from task_sets[0].gantt.lst](fig_ex2_gantt.png)

*Figure 7. lst schedule on W1 — values from task_sets[0].gantt.lst*


<!-- page 29 -->


## Figures — group 3

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 8: Utilisation versus LST preemptions across workloads — values from task_sets[*].policies.lst.preemptions](fig_ex2_scatter.png)

*Figure 8. Utilisation versus LST preemptions across workloads — values from task_sets[*].policies.lst.preemptions*

![Figure 9: Response jitter per workload and policy — values from task_sets[*].policies.*.jitter](fig_ex2_jitter.png)

*Figure 9. Response jitter per workload and policy — values from task_sets[*].policies.*.jitter*


<!-- page 30 -->


## When the two instruments disagree

The naive comparison puts a checker over one hyperperiod next to a simulator running two hyperperiods. Those two are not looking at the same job set, so a mismatch is expected and is an artefact of the instrument, not a discovery about scheduling. The aligned comparison gives both instruments the jobs released in one hyperperiod and enough time to finish them. The counts below show how much of the apparent disagreement disappears once the instruments are aligned. This is the same lesson learned earlier in this project, when the checker called a feasible set infeasible because it treated a forced idle instant as a dead end: the bug was in the checker.

| Set | checker | naive agrees | aligned agrees | aligned horizon |
|---|---|---|---|---|
| W1 | feasible | yes | yes | 35 |
| W2 | feasible | yes | yes | 36 |
| W3 | feasible | yes | yes | 28 |
| W4 | infeasible | yes | yes | 393 |
| W5 | feasible | yes | yes | 32 |
| W6 | infeasible | yes | yes | 17 |
| W7 | feasible | yes | yes | 31 |
| W8 | infeasible | yes | yes | 33 |

*Naive versus aligned comparison*

| Naive comparisons agreeing | 8 |
|---|---|
| Aligned comparisons agreeing | 8 |
| Task sets | 8 |
| Truncated checker runs | 0 |
| [E] RM counterexamples | 1 |
| [M] witness cheaper than LST | 4 |
| [D] cap artefacts | 5 |

*Agreement counts [D]*

> **Instrument alignment.** Naive comparisons that agree: 8. Aligned comparisons that agree: 8. The difference is measured, not argued.


<!-- page 31 -->


## A defect produced by a state cap

The checker has a state cap. With the cap set low, the very same task set that the full checker proves feasible is reported infeasible and the run is flagged truncated. [D] This is a disagreement between the instrument and the data, and the instrument is the suspect. [E] With the cap restored the verdict returns to feasible. A truncated run is never used as a finding anywhere in this project; it is reported as an artefact, with the limit and the state count that produced it.

| Cap on states | verdict | states visited | truncated |
|---|---|---|---|
| 4 | infeasible | 7 | yes |
| 8 | infeasible | 11 | yes |
| 16 | feasible | 13 | no |
| 4000000 | feasible | 13 | no |

*Checker verdict as a function of the cap [D]*

| Task specification | T1(T=10,C=2,D=8,ph=0), T2(T=20,C=3,D=15,ph=0) |
|---|---|
| [D] false infeasible verdicts | 2 |
| [E] full verdict | feasible |

*The same set under different caps*

> **Artefacts, not findings.** Across the 8 sets of this exercise, 5 produce a false infeasible verdict under a reduced cap. None of those verdicts is used as a result.


<!-- page 32 -->


## Verification is coarse, measurement is not

[E] The checker answers one question: does a feasible schedule exist. The witness it returns is one such schedule. [M] The simulator counts what that witness costs and what LST costs on the same task set. When the two numbers differ, the schedules are equivalent for verification and very different for the machine. This is not a contradiction; it is the limit of what a feasibility verdict can promise, made visible by measurement. A claim that all optimal schedules cost the same is refuted by the witness rows below.

| Set | witness preemptions | LST preemptions | EDF preemptions | witness valid |
|---|---|---|---|---|
| W1 | 0 | 0 | 0 | yes |
| W2 | 0 | 10 | 0 | yes |
| W3 | 1 | 2 | 2 | yes |
| W4 | 0 | 162 | 38 | no |
| W5 | 0 | 4 | 4 | yes |
| W6 | 0 | 0 | 0 | no |
| W7 | 0 | 6 | 0 | yes |
| W8 | 0 | 4 | 0 | no |

*Witness cost versus policy cost [M]*

| [M] sets where the witness is cheaper | 4 |
|---|---|
| [E] independently valid witnesses | 5 |
| [E] RM counterexamples | 1 |

*What the two instruments can say*

> **Complement, not contradiction.** A feasibility verdict is a coarse equivalence: it groups schedules that measurement can separate. Reporting the grouping as if it were a cost claim would be the mistake.


<!-- page 33 -->


## Limitations we state ourselves

The model is a single preemptive processor with no release cost, no cache or migration effects and execution equal to the worst case. Therefore these measurements say nothing about multicore behaviour or about runtime variance. The checker's verdict is exact only for the enumerated job set and only when its run was not truncated; every truncation flag is reported and no conclusion is drawn from a truncated run. Utilisation is a descriptive ratio here, never a schedulability test. Finally, a measurement that does not separate two policies is reported as inconclusive rather than as a tie broken by preference.

- single processor; no multicore or migration claim
- execution equals worst case; no runtime variance
- checker state cap; every truncation is reported
- integer time; no floating tolerance needed
- overlapping ranges are called inconclusive

> **Stated in advance.** A result obtained from a truncated checker state space is an artefact of the cap. It is never reported as a finding.


<!-- page 34 -->


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
| Figures | 9 |
| Findings | 6 |
| Sweeps | 3 |

*Data file summary*

> **Definition of a clean build.** A clean build is defined as empty overflow, missing figures and missing glyphs lists, with the generator's page count equal to the PDF page count.


<!-- page 35 -->


## Deliverables and checks

The table lists the artefacts of this exercise. Word and PDF are rendered from one content model, so their page counts agree with the generator's explicit page list; the exact PDF count is read back from the file by the checker. The Markdown file is a by-product of the same model. Speaker decks, where required, carry notes on every slide.

| Artefact | kind | how it is produced |
|---|---|---|
| REPORT_EN.docx / REPORT_EN.pdf | English report | tools/build_report.py lst2_en |
| REPORT_FA.docx / REPORT_FA.pdf | Persian report | tools/build_report.py lst2_fa |
| output/experiments.json | all numbers | code/run_experiments.py |
| diagrams/ | generated figures | code/make_diagrams.py |
| tests/ | green tests | python3 -m pytest |

*Artefact table*

| Figures | 9 |
|---|---|
| Findings | 6 |
| Independently valid witnesses | 5 |
| Truncated checker runs | 0 |

*Checks*

> **Two kinds of page count.** Word page counts are estimated by the checker against the real section geometry; PDF page counts are exact because they are read back from the file.


<!-- page 36 -->


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
