# A Hand-Worked LST Schedule and an Independent Trace

**the hand table, the machine table, and a witness of divergence**

- **Exercise:** Exercise 3
- **Course:** Real-Time Scheduling
- **Topic:** Least Slack Time (LST) scheduling
- **Deliverables:** bilingual EN/FA report, DOCX + PDF; diagrams; code; tests
- **Repository:** github.com/rera13197-ux/LST
- **Branch:** Exercise-3-LST-Manual-Scheduling
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
- The hand table, printed by the program (p. 10)
- Where the hand rules part company (p. 11)
- Task set M1 (p. 12)
- Task set M2 (p. 13)
- Task set M3 (p. 14)
- Task set M4 (p. 15)
- Task set M5 (p. 16)
- Task set M6 (p. 17)
- Sweeps: deadline-misses (p. 18)
- Sweeps: deadline-preemptions (p. 19)
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

Can a hand-worked LST schedule and an independent program trace be made to agree unit for unit, and where do they part company?

This report states what was asked and how it was answered before giving any result, so that a reader can try to refute the claim.

| Instrument | [E] + [M] |
|---|---|
| Scope | a hand-worked LST table, an independent program trace, and a printed divergence witness against an earliest-deadline hand rule |
| Random seed | 20261116 |
| Task sets | 6 |
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

> **The split used here.** In this exercise 4 of 6 sets use a constrained deadline. The split into 5 feasible and 1 infeasible sets is the [E] verdict, not a guess.


<!-- page 8 -->


## Experimental design

[M] The table below lists every task set used in this exercise. All rows come from the same generator and the same seed; no set was removed because its result was inconvenient. The verdict column is [E]: it is the exhaustive checker's decision over one hyperperiod, with a witness re-checked independently. Periods, execution times, deadlines and phases are integers.

```text
M1: T1(T=6,C=2,D=6,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=12,C=3,D=12,ph=0)
M2: T1(T=4,C=2,D=4,ph=0), T2(T=4,C=2,D=4,ph=0)
M3: T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=0), T3(T=12,C=3,D=7,ph=0)
M4: T1(T=5,C=2,D=3,ph=0), T2(T=6,C=2,D=3,ph=0)
M5: T1(T=6,C=2,D=4,ph=0), T2(T=8,C=2,D=5,ph=2), T3(T=12,C=3,D=7,ph=1)
M6: T1(T=4,C=1,D=3,ph=0), T2(T=8,C=2,D=6,ph=0), T3(T=16,C=4,D=12,ph=0)
```
*Full task specifications, read from the data file*

| Set | U | hyperperiod | D < T | verdict |
|---|---|---|---|---|
| M1 | 0.833333 | 24 | no | feasible |
| M2 | 1.0 | 4 | no | feasible |
| M3 | 0.833333 | 24 | yes | feasible |
| M4 | 0.733333 | 30 | yes | infeasible |
| M5 | 0.833333 | 24 | yes | feasible |
| M6 | 0.75 | 16 | yes | feasible |

*Task sets used, read from experiments.json*

| Random seed | 20261116 |
|---|---|
| Policies measured | 9 |
| Feasible sets [E] | 5 |
| Infeasible sets [E] | 1 |
| Checker states visited [E] | 91 |
| Truncated checker runs | 0 |

*Generated data at a glance*


<!-- page 9 -->


## A worked schedule

The schedule below is reproduced from the generated data, not typed by hand. Each row is a maximal run of one job on the processor. It is the object that a hand computation must match unit for unit; the agreement between an independent hand trace and the simulator's timeline is itself a test in this repository.

```text
T1#0  [0, 2)
T2#0  [2, 4)
T3#0  [4, 6)
T1#1  [6, 7)
T3#0  [7, 8)
T1#1  [8, 9)
T2#1  [9, 11)
T1#2  [12, 14)
T3#1  [14, 16)
T2#2  [16, 17)
T3#1  [17, 18)
T1#3  [18, 19)
T2#2  [19, 20)
T1#3  [20, 21)
```
*Runs read from the generated data*

| Values read from | output/experiments.json |
|---|---|
| Hand trace agrees [M] | True |
| Steps compared [M] | 24 |

*Trace provenance*

> **Why two programs.** The hand trace and the simulator are two independent programs. Their agreement is checked by a test, and their disagreement would be reported as an instrument defect.


<!-- page 10 -->


## The hand table, printed by the program

[M] This table is produced by a second, independent implementation of the discrete-time decision rule, not by the simulator. For every integer instant it lists the ready jobs, their slack values and the job chosen. A test compares this timeline with the simulator's own timeline step by step; the compared step count is in the data file.

| t | ready jobs | slack of ready jobs | chosen |
|---|---|---|---|
| 0 | T1#0, T2#0, T3#0 | 4, 6, 9 | T1#0 |
| 1 | T1#0, T2#0, T3#0 | 4, 5, 8 | T1#0 |
| 2 | T2#0, T3#0 | 4, 7 | T2#0 |
| 3 | T2#0, T3#0 | 4, 6 | T2#0 |
| 4 | T3#0 | 5 | T3#0 |
| 5 | T3#0 | 5 | T3#0 |
| 6 | T3#0, T1#1 | 5, 4 | T1#1 |
| 7 | T3#0, T1#1 | 4, 4 | T3#0 |
| 8 | T1#1, T2#1 | 3, 6 | T1#1 |
| 9 | T2#1 | 5 | T2#1 |
| 10 | T2#1 | 5 | T2#1 |
| 11 | - | - | - |
| 12 | T1#2, T3#1 | 4, 9 | T1#2 |

*Independent hand trace, read from the data file*

| Hand trace agrees [M] | yes |
|---|---|
| Steps compared [M] | 24 |
| Values read from | output/experiments.json |

*Agreement with the simulator [M]*


<!-- page 11 -->


## Where the hand rules part company

[M] A second hand rule, earliest deadline first, is run on the same task set. The first instant at which the two hand rules choose different jobs is a witness: it shows that the two policies are not the same algorithm even when both happen to meet every deadline. The witness sequence below is printed from the generated data.

| First divergence at t | 6 |
|---|---|
| Differing instants | 6 |
| Steps compared | 24 |

*Witness summary [M]*

```text
t=6  LST=T1#1  EDF=T3#0
t=7  LST=T3#0  EDF=T1#1
t=16  LST=T2#2  EDF=T3#1
t=17  LST=T3#1  EDF=T2#2
t=18  LST=T1#3  EDF=T2#2
t=19  LST=T2#2  EDF=T1#3
```
*Divergence witness, printed from the data*

> **Witness over assertion.** A verbal claim that two policies differ is weaker than a printed witness. Here the witness is data, and it can be re-read from the generated file.


<!-- page 12 -->


## Task set M1

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


## Task set M2

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


<!-- page 14 -->


## Task set M3

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


<!-- page 15 -->


## Task set M4

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


## Task set M5

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


## Task set M6

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


<!-- page 18 -->


## Sweeps: deadline-misses

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[0] |
|---|---|
| Swept parameter | deadline of T1 (time units) |

*Provenance*

![Figure 1: Sweep deadline-misses: deadline of T1 (time units) — values from sweeps[0]](fig_ex3_deadline_misses.png)

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


## Sweeps: deadline-preemptions

[M] A sweep changes one parameter and holds everything else fixed. The plot and the table are drawn from the same array in the generated data; the caption names the JSON path so a reader can re-read the values. Where the curves overlap, we write that the measurement does not separate the policies instead of inventing a ranking.

| Values read from | sweeps[1] |
|---|---|
| Swept parameter | deadline of T1 (time units) |

*Provenance*

![Figure 2: Sweep deadline-preemptions: deadline of T1 (time units) — values from sweeps[1]](fig_ex3_deadline_pre.png)

*Figure 2. Sweep deadline-preemptions: deadline of T1 (time units) — values from sweeps[1]*

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

![Figure 3: Sweep alignment: task set — values from sweeps[2]](fig_ex3_alignment.png)

*Figure 3. Sweep alignment: task set — values from sweeps[2]*

| task set | naive_lst_missed | aligned_lst_missed | checker_feasible |
|---|---|---|---|
| M1 | 0 | 0 | 1 |
| M2 | 0 | 0 | 1 |
| M3 | 0 | 0 | 1 |
| M4 | 2 | 1 | 0 |
| M5 | 0 | 0 | 1 |
| M6 | 0 | 0 | 1 |

*Values behind the plot*

> **Reading the sweep.** 6 points and 3 series are plotted. Where ranges overlap the measurement does not separate the policies.


<!-- page 21 -->


## Finding: F1


### Minimising slack is not minimising overhead

[M] measurement

[M] On M1, LST records 10 preemptions and 28 context switches; EDF records 0 and 18. Both miss 0 deadlines. [E] The checker verdict is feasible after 22 states. Correctness does not order these two policies; overhead does.

| Key | Value |
|---|---|
| checker states | 22 |
| edf preemptions | 0 |
| edf switches | 18 |
| lst preemptions | 10 |
| lst switches | 28 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 22 -->


## Finding: F2


### Implicit deadlines take the test away

[E] + [M]

[E] Of 2 sets with implicit deadlines, 2 are feasible. Of 4 constrained sets, 3 are feasible and 1 are infeasible. Feasibility has discriminating power only in the constrained regime; that is why every sweep here moves a deadline rather than a definition.

| Key | Value |
|---|---|
| constrained feasible | 3 |
| constrained infeasible | 1 |
| constrained sets | 4 |
| implicit feasible | 2 |
| implicit sets | 2 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 23 -->


## Finding: F3


### Naive versus aligned comparison

[D] disagreement

[D] No naive-versus-aligned mismatch survives on these 6 sets: 6 naive and 6 aligned comparisons agree with the checker. The largest gap in missed deadlines between the two settings is 1 on M4. Reporting a disagreement that the data does not contain would be the mistake.

| Key | Value |
|---|---|
| aligned agree | 6 |
| aligned missed target | 1 |
| naive agree | 6 |
| naive missed target | 2 |
| set count | 6 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 24 -->


## Finding: F4


### A state cap fabricates an infeasibility verdict

[D] disagreement

[D] With a reduced state cap, M1 is reported infeasible 3 times, each run flagged truncated; with the cap restored the verdict is feasible after 22 states. The smallest truncating cap was 4. A truncated run is an artefact of the instrument and is never used as a finding.

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


### The hand table and the simulator agree step by step

[M] measurement

[M] For 6 of 6 task sets the independent hand trace and the simulator timeline agree at every one of the compared instants; the primary worked example compares 24 instants. This is not a proof: it is two separate programs agreeing on the same integer timeline, and the agreement is checked by a test in this repository.

| Key | Value |
|---|---|
| agreeing traces | 6 |
| primary agree | 1 |
| primary steps | 24 |
| task sets | 6 |

*Numbers read from the data file*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 26 -->


## Finding: F6


### A witness that the two hand rules are different algorithms

[M] measurement

[M] An independent earliest-deadline hand rule is run on the same worked task set. The two hand rules choose different jobs at 6 of 24 instants, first at t=6. The witness lines below are printed from the generated data; a verbal claim that the policies differ would be weaker than this sequence.

| Key | Value |
|---|---|
| compared instants | 24 |
| divergent instants | 6 |
| first divergence | 6 |

*Numbers read from the data file*

```text
t=6 LST=T1#1 EDF=T3#0
t=7 LST=T3#0 EDF=T1#1
t=16 LST=T2#2 EDF=T3#1
t=17 LST=T3#1 EDF=T2#2
t=18 LST=T1#3 EDF=T2#2
t=19 LST=T2#2 EDF=T1#3
```
*Witness / counterexample*

> **Why this is a finding.** A disagreement is treated as an instrument defect until the two job sets are aligned; the gold is in the resolution, not in the headline.


<!-- page 27 -->


## Figures — group 1

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 4: Preemptions by policy on M1 — values from task_sets[0].policies.*.preemptions](fig_ex3_preemptions.png)

*Figure 4. Preemptions by policy on M1 — values from task_sets[0].policies.*.preemptions*

![Figure 5: Missed deadlines per set and policy — values from task_sets[*].policies.*.missed](fig_ex3_misses.png)

*Figure 5. Missed deadlines per set and policy — values from task_sets[*].policies.*.missed*


<!-- page 28 -->


## Figures — group 2

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 6: Tie events per set and policy — values from task_sets[*].policies.*.tie_events](fig_ex3_ties.png)

*Figure 6. Tie events per set and policy — values from task_sets[*].policies.*.tie_events*

![Figure 7: lst schedule on M1 — values from task_sets[0].gantt.lst](fig_ex3_gantt.png)

*Figure 7. lst schedule on M1 — values from task_sets[0].gantt.lst*


<!-- page 29 -->


## Figures — group 3

All figures are generated from the same data file. Plot labels are deliberately plain ASCII identifiers so that the images are reproducible without a shaping stack; the bilingual explanation lives in the captions and in the surrounding text. Each caption names the JSON path the values were read from.

![Figure 8: Hand-trace schedule on M1 — values from manual.gantt](fig_ex3_hand_gantt.png)

*Figure 8. Hand-trace schedule on M1 — values from manual.gantt*


<!-- page 30 -->


## When the two instruments disagree

The naive comparison puts a checker over one hyperperiod next to a simulator running two hyperperiods. Those two are not looking at the same job set, so a mismatch is expected and is an artefact of the instrument, not a discovery about scheduling. The aligned comparison gives both instruments the jobs released in one hyperperiod and enough time to finish them. The counts below show how much of the apparent disagreement disappears once the instruments are aligned. This is the same lesson learned earlier in this project, when the checker called a feasible set infeasible because it treated a forced idle instant as a dead end: the bug was in the checker.

| Set | checker | naive agrees | aligned agrees | aligned horizon |
|---|---|---|---|---|
| M1 | feasible | yes | yes | 36 |
| M2 | feasible | yes | yes | 8 |
| M3 | feasible | yes | yes | 31 |
| M4 | infeasible | yes | yes | 33 |
| M5 | feasible | yes | yes | 31 |
| M6 | feasible | yes | yes | 28 |

*Naive versus aligned comparison*

| Naive comparisons agreeing | 6 |
|---|---|
| Aligned comparisons agreeing | 6 |
| Task sets | 6 |
| Truncated checker runs | 0 |
| [E] RM counterexamples | 2 |
| [M] witness cheaper than LST | 4 |
| [D] cap artefacts | 5 |

*Agreement counts [D]*

> **Instrument alignment.** Naive comparisons that agree: 6. Aligned comparisons that agree: 6. The difference is measured, not argued.


<!-- page 31 -->


## A defect produced by a state cap

The checker has a state cap. With the cap set low, the very same task set that the full checker proves feasible is reported infeasible and the run is flagged truncated. [D] This is a disagreement between the instrument and the data, and the instrument is the suspect. [E] With the cap restored the verdict returns to feasible. A truncated run is never used as a finding anywhere in this project; it is reported as an artefact, with the limit and the state count that produced it.

| Cap on states | verdict | states visited | truncated |
|---|---|---|---|
| 4 | infeasible | 11 | yes |
| 8 | infeasible | 16 | yes |
| 16 | infeasible | 27 | yes |
| 4000000 | feasible | 22 | no |

*Checker verdict as a function of the cap [D]*

| Task specification | T1(T=6,C=2,D=6,ph=0), T2(T=8,C=2,D=8,ph=0), T3(T=12,C=3,D=12,ph=0) |
|---|---|
| [D] false infeasible verdicts | 3 |
| [E] full verdict | feasible |

*The same set under different caps*

> **Artefacts, not findings.** Across the 6 sets of this exercise, 5 produce a false infeasible verdict under a reduced cap. None of those verdicts is used as a result.


<!-- page 32 -->


## Verification is coarse, measurement is not

[E] The checker answers one question: does a feasible schedule exist. The witness it returns is one such schedule. [M] The simulator counts what that witness costs and what LST costs on the same task set. When the two numbers differ, the schedules are equivalent for verification and very different for the machine. This is not a contradiction; it is the limit of what a feasibility verdict can promise, made visible by measurement. A claim that all optimal schedules cost the same is refuted by the witness rows below.

| Set | witness preemptions | LST preemptions | EDF preemptions | witness valid |
|---|---|---|---|---|
| M1 | 0 | 10 | 0 | yes |
| M2 | 0 | 4 | 0 | yes |
| M3 | 0 | 0 | 0 | yes |
| M4 | 0 | 4 | 0 | no |
| M5 | 0 | 6 | 0 | yes |
| M6 | 1 | 2 | 2 | yes |

*Witness cost versus policy cost [M]*

| [M] sets where the witness is cheaper | 4 |
|---|---|
| [E] independently valid witnesses | 5 |
| [E] RM counterexamples | 2 |

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
| Figures | 8 |
| Findings | 6 |
| Sweeps | 3 |

*Data file summary*

> **Definition of a clean build.** A clean build is defined as empty overflow, missing figures and missing glyphs lists, with the generator's page count equal to the PDF page count.


<!-- page 35 -->


## Deliverables and checks

The table lists the artefacts of this exercise. Word and PDF are rendered from one content model, so their page counts agree with the generator's explicit page list; the exact PDF count is read back from the file by the checker. The Markdown file is a by-product of the same model. Speaker decks, where required, carry notes on every slide.

| Artefact | kind | how it is produced |
|---|---|---|
| REPORT_EN.docx / REPORT_EN.pdf | English report | tools/build_report.py lst3_en |
| REPORT_FA.docx / REPORT_FA.pdf | Persian report | tools/build_report.py lst3_fa |
| output/experiments.json | all numbers | code/run_experiments.py |
| diagrams/ | generated figures | code/make_diagrams.py |
| tests/ | green tests | python3 -m pytest |

*Artefact table*

| Figures | 8 |
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
  extra
  figures
  findings
  manual
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
