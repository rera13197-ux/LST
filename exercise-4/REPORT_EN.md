# Optimality, Exhaustive Verification and Overload

**fixed seed, constrained deadlines, independent witness verification**

- **Exercise:** Exercise 4
- **Course:** Real-Time Scheduling
- **Topic:** Least Slack Time (LST) scheduling
- **Deliverables:** bilingual EN/FA report, DOCX + PDF; diagrams; code; tests
- **Repository:** github.com/rera13197-ux/LST
- **Branch:** Exercise-4-LST-Optimality-And-Overload
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
- Task set R1 (p. 10)
- Task set R2 (p. 11)
- Task set R3 (p. 12)
- Task set R4 (p. 13)
- Task set R5 (p. 14)
- Task set R6 (p. 15)
- Task set R7 (p. 16)
- Task set R8 (p. 17)
- Sweeps: deadline-misses (p. 18)
- Sweeps: deadline-first-miss (p. 19)
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
- The large random study (p. 33)
- Limitations we state ourselves (p. 34)
- Reproducibility (p. 35)
- Deliverables and checks (p. 36)
- Appendix: the data contract (p. 37)


<!-- page 1 -->


<!-- page 2 -->


<!-- page 3 -->


## The question

Does the optimality claim survive an exhaustive search over thousands of constrained-deadline task sets, and what happens under overload?

This report states what was asked and how it was answered before giving any result, so that a reader can try to refute the claim.

| Instrument | [E] + [M] |
|---|---|
| Scope | fixed-seed exhaustive verification on constrained deadlines, independent witness checks, an implicit-deadline control and overload |
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

> **The split used here.** In this exercise 7 of 8 sets use a constrained deadline. The split into 4 feasible and 4 infeasible sets is the [E] verdict, not a guess.


<!-- page 8 -->


## Experimental design

[M] The table below lists every task set used in this exercise. All rows come from the same generator and the same seed; no set was removed because its result was inconvenient. The verdict column is [E]: it is the exhaustive checker's decision over one hyperperiod, with a witness re-checked independently. Periods, execution times, deadlines and phases are integers.

```text
R1: T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=0), T3(T=12,C=3,D=7,ph=0)
R2: T1(T=5,C=2,D=3,ph=0), T2(T=6,C=2,D=3,ph=0)
R3: T1(T=6,C=2,D=6,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=12,C=3,D=12,ph=0)
R4: T1(T=4,C=3,D=4,ph=0), T2(T=6,C=3,D=5,ph=0)
R5: T1(T=5,C=2,D=3,ph=0), T2(T=10,C=3,D=6,ph=0), T3(T=10,C=2,D=7,ph=0)
R6: T1(T=4,C=2,D=3,ph=0), T2(T=4,C=3,D=4,ph=3)
R7: T1(T=4,C=1,D=3,ph=0), T2(T=8,C=2,D=6,ph=0), T3(T=16,C=4,D=12,ph=0)
R8: T1(T=5,C=2,D=3,ph=0), T2(T=5,C=2,D=3,ph=0), T3(T=10,C=3,D=6,ph=0)
```
*Full task specifications, read from the data file*

| Set | U | hyperperiod | D < T | verdict |
|---|---|---|---|---|
| R1 | 0.833333 | 24 | yes | feasible |
| R2 | 0.733333 | 30 | yes | infeasible |
| R3 | 0.833333 | 24 | no | feasible |
| R4 | 1.25 | 12 | yes | infeasible |
| R5 | 0.9 | 10 | yes | infeasible |
| R6 | 1.25 | 4 | yes | feasible |
| R7 | 0.75 | 16 | yes | feasible |
| R8 | 1.1 | 10 | yes | infeasible |

*Task sets used, read from experiments.json*

| Random seed | 20261116 |
|---|---|
| Policies measured | 9 |
| Feasible sets [E] | 4 |
| Infeasible sets [E] | 4 |
| Checker states visited [E] | 105 |
| Truncated checker runs | 0 |

*Generated data at a glance*


<!-- page 9 -->


## A worked schedule

The schedule below is reproduced from the generated data, not typed by hand. Each row is a maximal run of one job on the processor. It is the object that a hand computation must match unit for unit; the agreement between an independent hand trace and the simulator's timeline is itself a test in this repository.

```text
T1#0  [0, 2)
T2#0  [2, 4)
T3#0  [4, 7)
T1#1  [7, 9)
T2#1  [9, 11)
T1#2  [12, 14)
T3#1  [14, 17)
T2#2  [17, 19)
T1#3  [19, 21)
T1#4  [24, 26)
T2#3  [26, 28)
T3#2  [28, 31)
T1#5  [31, 33)
T2#4  [33, 35)
```
*Runs read from the generated data*

| Values read from | output/experiments.json |
|---|---|

*Trace provenance*

> **Why two programs.** The hand trace and the simulator are two independent programs. Their agreement is checked by a test, and their disagreement would be reported as an instrument defect.


<!-- page 10 -->


## Task set R1

| Task specification | T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=0), T3(T=12,C=3,D=7,ph=0) |
|---|---|
| Utilisation (descriptive) | 0.833333 |
| Hyperperiod | 24 |
| Constrained deadline | yes |
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
| lst | 0 | 0 | 18 | 0 | 0 | 6 |
| lst:edf | 0 | 0 | 18 | 0 | 0 | 6 |
| lst:rm | 0 | 4 | 22 | 0 | 0 | 6 |
| lst:stay | 0 | 0 | 18 | 0 | 0 | 6 |
| lst:lzs | 0 | 0 | 18 | 0 | 0 | 6 |
| edf | 0 | 0 | 18 | 0 | 0 | 6 |
| rm | 4 | 4 | 22 | 0 | -4 | 4 |
| dm | 4 | 4 | 22 | 0 | -4 | 4 |
| fifo | 0 | 0 | 18 | 0 | 0 | 6 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict feasible, 22 states, 0 pruned, independent witness valid. [M] LST recorded 0 preemptions and 0 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 6.


<!-- page 11 -->


## Task set R2

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


<!-- page 12 -->


## Task set R3

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


<!-- page 13 -->


## Task set R4

| Task specification | T1(T=4,C=3,D=4,ph=0), T2(T=6,C=3,D=5,ph=0) |
|---|---|
| Utilisation (descriptive) | 1.25 |
| Hyperperiod | 12 |
| Constrained deadline | yes |
| Checker verdict [E] | infeasible |
| States visited [E] | 8 |
| Branches pruned [E] | 5 |
| Jobs in checker horizon | 5 |
| Checker truncated | no |
| Idle enumeration agrees [E] | yes |
| Independent witness | not applicable |
| Aligned comparison agrees | yes |
| Naive comparison agrees | yes |

*Set parameters and [E] verdict*

| Policy | missed | preemptions | switches | zero-sw | min laxity | ties |
|---|---|---|---|---|---|---|
| lst | 8 | 6 | 14 | 1 | -4 | 6 |
| lst:edf | 8 | 6 | 14 | 1 | -4 | 6 |
| lst:rm | 8 | 8 | 16 | 1 | -4 | 6 |
| lst:stay | 9 | 6 | 14 | 0 | -4 | 6 |
| lst:lzs | 8 | 6 | 14 | 1 | -4 | 6 |
| edf | 8 | 0 | 8 | 0 | -4 | 3 |
| rm | 4 | 4 | 12 | 0 | -13 | 1 |
| dm | 4 | 4 | 12 | 0 | -13 | 1 |
| fifo | 8 | 0 | 8 | 0 | -4 | 3 |

*All policies on this set [M]*

> **What this set shows.** [E] verdict infeasible, 8 states, 5 pruned, independent witness not applicable. [M] LST recorded 6 preemptions and 8 missed deadlines; EDF recorded 0 preemptions on the same set. Tie events observed: 6.


<!-- page 14 -->


## Task set R5

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


<!-- page 15 -->


## Task set R6

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


<!-- page 16 -->


## Task set R7

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


<!-- page 17 -->


## Task set R8

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


<!-- page 18 -->


## Sweeps: deadline-misses

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[0] |
|---|---|
| Swept parameter | deadline of T1 (time units) |

*Provenance*

![Figure 1: Sweep deadline-misses: deadline of T1 (time units) — values from sweeps[0]](fig_ex4_deadline_misses.png)

*Figure 1. Sweep deadline-misses: deadline of T1 (time units) — values from sweeps[0]*

| deadline of T1 (time units) | lst_missed | edf_missed | rm_missed | checker_feasible |
|---|---|---|---|---|
| 2 | 0 | 0 | 0 | 1 |
| 3 | 0 | 0 | 0 | 1 |
| 4 | 0 | 0 | 0 | 1 |
| 5 | 0 | 0 | 0 | 1 |
| 6 | 0 | 0 | 0 | 1 |

*Values behind the plot*

> **Reading the sweep.** 5 points and 4 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 19 -->


## Sweeps: deadline-first-miss

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[1] |
|---|---|
| Swept parameter | deadline of T1 (time units) |

*Provenance*

![Figure 2: Sweep deadline-first-miss: deadline of T1 (time units) — values from sweeps[1]](fig_ex4_deadline_pre.png)

*Figure 2. Sweep deadline-first-miss: deadline of T1 (time units) — values from sweeps[1]*

| deadline of T1 (time units) | lst_preemptions | edf_preemptions | rm_preemptions |
|---|---|---|---|
| 2 | 6 | 4 | 4 |
| 3 | 6 | 4 | 4 |
| 4 | 6 | 4 | 4 |
| 5 | 6 | 4 | 4 |
| 6 | 10 | 0 | 4 |

*Values behind the plot*

> **Reading the sweep.** 5 points and 3 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 20 -->


## Sweeps: alignment

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[2] |
|---|---|
| Swept parameter | task set |

*Provenance*

![Figure 3: Sweep alignment: task set — values from sweeps[2]](fig_ex4_alignment.png)

*Figure 3. Sweep alignment: task set — values from sweeps[2]*

| task set | naive_lst_missed | aligned_lst_missed | checker_feasible |
|---|---|---|---|
| R1 | 0 | 0 | 1 |
| R2 | 2 | 1 | 0 |
| R3 | 0 | 0 | 1 |
| R4 | 8 | 4 | 0 |
| R5 | 2 | 1 | 0 |
| R6 | 1 | 0 | 1 |
| R7 | 0 | 0 | 1 |
| R8 | 9 | 4 | 0 |

*Values behind the plot*

> **Reading the sweep.** 8 points and 3 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 21 -->


## Finding: F1


### Minimising slack is not minimising overhead

[M] measurement

[M] On R1, LST records 0 preemptions and 18 context switches; EDF records 0 and 18. Both miss 0 deadlines. [E] The checker verdict is feasible after 22 states. Correctness does not order these two policies; overhead does.

| Key | Value |
|---|---|
| checker states | 22 |
| edf preemptions | 0 |
| edf switches | 18 |
| lst preemptions | 0 |
| lst switches | 18 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 22 -->


## Finding: F2


### Implicit deadlines take the test away

[E] + [M]

[E] Of 1 sets with implicit deadlines, 1 are feasible. Of 7 constrained sets, 3 are feasible and 4 are infeasible. Feasibility has discriminating power only in the constrained regime; that is why every sweep here moves a deadline rather than a definition.

| Key | Value |
|---|---|
| constrained feasible | 3 |
| constrained infeasible | 4 |
| constrained sets | 7 |
| implicit feasible | 1 |
| implicit sets | 1 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 23 -->


## Finding: F3


### Naive versus aligned comparison

[D] disagreement

[D] On R6 the checker says feasible, yet the naive two-hyperperiod LST run misses 1 deadlines while the aligned run misses 0. The two instruments were looking at different job sets. Aligning the release window removes the disagreement; the instrument, not the theorem, was at fault.

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

[D] With a reduced state cap, R1 is reported infeasible 3 times, each run flagged truncated; with the cap restored the verdict is feasible after 22 states. The smallest truncating cap was 4. A truncated run is an artefact of the instrument and is never used as a finding.

| Key | Value |
|---|---|
| false infeasible runs | 3 |
| full feasible | 1 |
| full states | 22 |
| smallest truncating limit | 4 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 25 -->


## Finding: F5


### Optimality survives an exhaustive search on constrained deadlines

[E] exhaustive verification

[E] The fixed-seed study generated 240 constrained-deadline sets: 140 feasible, 100 infeasible, 0 truncated, 140 independently valid witnesses. [M] On the feasible sets LST and EDF miss 0 and 0 deadlines in the aligned run, while RM misses 23. Changing the LST tie-break changed the verdict on 0 sets. The control batch of 120 implicit-deadline sets produced 120 feasible verdicts, which is why that regime cannot refute the claim.

| Key | Value |
|---|---|
| edf misses | 0 |
| feasible | 140 |
| generated | 240 |
| implicit feasible | 120 |
| implicit sets | 120 |
| infeasible | 100 |
| lst misses | 0 |
| rm misses | 23 |
| tie verdict changes | 0 |
| truncated | 0 |
| valid witnesses | 140 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 26 -->


## Finding: F6


### Under overload the interesting number is the first miss

[M] measurement

[M] On the overloaded set R4 LST misses 8 deadlines with first miss at t=5, minimum observed laxity -4 and 1 switches at zero laxity; EDF misses 8 with first miss at t=5. [E] The checker says infeasible and returns no witness. Missed jobs are kept running rather than dropped, so these counts describe a degraded system, not a failed instrument.

| Key | Value |
|---|---|
| edf first miss | 5 |
| edf missed | 8 |
| lst first miss | 5 |
| lst min laxity | -4 |
| lst missed | 8 |
| lst zero switches | 1 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 27 -->


## Figures — group 1

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 4: Preemptions by policy on R1 — values from task_sets[0].policies.*.preemptions](fig_ex4_preemptions.png)

*Figure 4. Preemptions by policy on R1 — values from task_sets[0].policies.*.preemptions*

![Figure 5: Missed deadlines per set and policy — values from task_sets[*].policies.*.missed](fig_ex4_misses.png)

*Figure 5. Missed deadlines per set and policy — values from task_sets[*].policies.*.missed*


<!-- page 28 -->


## Figures — group 2

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 6: Tie events per set and policy — values from task_sets[*].policies.*.tie_events](fig_ex4_ties.png)

*Figure 6. Tie events per set and policy — values from task_sets[*].policies.*.tie_events*

![Figure 7: lst schedule on R1 — values from task_sets[0].gantt.lst](fig_ex4_gantt.png)

*Figure 7. lst schedule on R1 — values from task_sets[0].gantt.lst*


<!-- page 29 -->


## Figures — group 3

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 8: Fixed-seed random study counts — values from random.table](fig_ex4_study.png)

*Figure 8. Fixed-seed random study counts — values from random.table*

![Figure 9: Task sets per utilisation band — values from random.utilisation_counts](fig_ex4_bins.png)

*Figure 9. Task sets per utilisation band — values from random.utilisation_counts*


<!-- page 30 -->


## When the two instruments disagree

The naive comparison puts a checker over one hyperperiod next to a simulator running two hyperperiods. Those two are not looking at the same job set, so a mismatch is expected and is an artefact of the instrument, not a discovery about scheduling. The aligned comparison gives both instruments the jobs released in one hyperperiod and enough time to finish them. The counts below show how much of the apparent disagreement disappears once the instruments are aligned. This is the same lesson learned earlier in this project, when the checker called a feasible set infeasible because it treated a forced idle instant as a dead end: the bug was in the checker.

| Set | checker | naive agrees | aligned agrees | aligned horizon |
|---|---|---|---|---|
| R1 | feasible | yes | yes | 31 |
| R2 | infeasible | yes | yes | 33 |
| R3 | feasible | yes | yes | 36 |
| R4 | infeasible | yes | yes | 17 |
| R5 | infeasible | yes | yes | 17 |
| R6 | feasible | no | yes | 8 |
| R7 | feasible | yes | yes | 28 |
| R8 | infeasible | yes | yes | 16 |

*Naive versus aligned comparison*

| Naive comparisons agreeing | 7 |
|---|---|
| Aligned comparisons agreeing | 8 |
| Task sets | 8 |
| Truncated checker runs | 0 |
| [E] RM counterexamples | 2 |
| [M] witness cheaper than LST | 3 |
| [D] cap artefacts | 4 |

*Agreement counts [D]*

> **Instrument alignment.** Naive comparisons that agree: 7. Aligned comparisons that agree: 8. The difference is measured, not argued.


<!-- page 31 -->


## A defect produced by a state cap

The checker has a state cap. With the cap set low, the very same task set that the full checker proves feasible is reported infeasible and the run is flagged truncated. [D] This is a disagreement between the instrument and the data, and the instrument is the suspect. [E] With the cap restored the verdict returns to feasible. A truncated run is never used as a finding anywhere in this project; it is reported as an artefact, with the limit and the state count that produced it.

| Cap on states | verdict | states visited | truncated |
|---|---|---|---|
| 4 | infeasible | 11 | yes |
| 8 | infeasible | 15 | yes |
| 16 | infeasible | 26 | yes |
| 4000000 | feasible | 22 | no |

*Checker verdict as a function of the cap [D]*

| Task specification | T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=0), T3(T=12,C=3,D=7,ph=0) |
|---|---|
| [D] false infeasible verdicts | 3 |
| [E] full verdict | feasible |

*The same set under different caps*

> **Artefacts, not findings.** Across the 8 sets of this exercise, 4 produce a false infeasible verdict under a reduced cap. None of those verdicts is used as a result.


<!-- page 32 -->


## Verification is coarse, measurement is not

[E] The checker answers one question: does a feasible schedule exist. The witness it returns is one such schedule. [M] The simulator counts what that witness costs and what LST costs on the same task set. When the two numbers differ, the schedules are equivalent for verification and very different for the machine. This is not a contradiction; it is the limit of what a feasibility verdict can promise, made visible by measurement. A claim that all optimal schedules cost the same is refuted by the witness rows below.

| Set | witness preemptions | LST preemptions | EDF preemptions | witness valid |
|---|---|---|---|---|
| R1 | 0 | 0 | 0 | yes |
| R2 | 0 | 4 | 0 | no |
| R3 | 0 | 10 | 0 | yes |
| R4 | 0 | 6 | 0 | no |
| R5 | 0 | 0 | 0 | no |
| R6 | 0 | 2 | 0 | yes |
| R7 | 1 | 2 | 2 | yes |
| R8 | 0 | 7 | 0 | no |

*Witness cost versus policy cost [M]*

| [M] sets where the witness is cheaper | 3 |
|---|---|
| [E] independently valid witnesses | 4 |
| [E] RM counterexamples | 2 |

*What the two instruments can say*

> **Complement, not contradiction.** A feasibility verdict is a coarse equivalence: it groups schedules that measurement can separate. Reporting the grouping as if it were a cost claim would be the mistake.


<!-- page 33 -->


## The large random study

[E] A fixed-seed generator produces constrained-deadline task sets with utilisation at most one and a bounded hyperperiod. Each set is decided by the exhaustive checker, every witness is re-checked by the independent verifier, and the aligned simulator run is compared with the verdict. [M] Counts below are sums over that run. A separate control batch with implicit deadlines shows what happens when the yardstick loses its power. Truncated runs are counted and excluded from every conclusion.

| Quantity | count | instrument |
|---|---|---|
| generated sets | 240 | [M] |
| feasible | 140 | [E] |
| infeasible | 100 | [E] |
| truncated runs | 0 | [E] |
| valid witnesses | 140 | [E] |
| LST misses on feasible sets | 0 | [M] |
| EDF misses on feasible sets | 0 | [M] |
| RM misses on feasible sets | 23 | [M] |
| tie-break verdict changes | 0 | [M] |
| cap artefacts | 100 | [D] |
| implicit control sets | 120 | [E] |
| implicit control feasible | 120 | [E] |

*Aggregates over the fixed-seed study*

| Random seed | 20261120 |
|---|---|
| Sets generated | 240 |
| Truncated runs | 0 |
| Tie-break verdict changes | 0 |

*Study parameters*

> **What the sweep decided.** Of 240 generated sets, 140 are feasible [E] and 100 infeasible. LST misses 0 deadlines on feasible sets, EDF 0 and RM 23. The implicit control produced 120 feasible verdicts out of 120.


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
| Figures | 9 |
| Findings | 6 |
| Sweeps | 3 |

*Data file summary*

> **Definition of a clean build.** A clean build is defined as empty overflow, missing figures and missing glyphs lists, with the generator's page count equal to the PDF page count.


<!-- page 36 -->


## Deliverables and checks

The table lists the artefacts of this exercise. Word and PDF are rendered from one content model, so their page counts agree with the generator's explicit page list; the exact PDF count is read back from the file by the checker. The Markdown file is a by-product of the same model. Speaker decks, where required, carry notes on every slide.

| Artefact | kind | how it is produced |
|---|---|---|
| REPORT_EN.docx / REPORT_EN.pdf | English report | tools/build_report.py lst4_en |
| REPORT_FA.docx / REPORT_FA.pdf | Persian report | tools/build_report.py lst4_fa |
| output/experiments.json | all numbers | code/run_experiments.py |
| diagrams/ | generated figures | code/make_diagrams.py |
| tests/ | green tests | python3 -m pytest |

*Artefact table*

| Figures | 9 |
|---|---|
| Findings | 6 |
| Independently valid witnesses | 4 |
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
  random
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
