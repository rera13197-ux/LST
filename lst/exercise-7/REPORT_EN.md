# Readers-Writers: Verification and Measurement

**Exercise 7 - bilingual report (EN/FA)**

- **Exercise:** Exercise 7
- **Course:** Real-Time Scheduling
- **Topic:** Readers-writers
- **Repository:** github.com/rera13197-ux/LST
- **Branch:** Exercise-7-LST-Tie-Breaking-And-Thrashing
- **Random seed:** 20261120
- **Protocols:** 12
- **Figures:** 10
- **Method:** two separate instruments: exhaustive checking and measurement
- **Status:** complete: every number regenerated from a program run

## Table of contents

- The question (p. 3)
- Two instruments, two kinds of claim (p. 4)
- Model and notation (p. 5)
- Mechanisms, part one (p. 6)
- Mechanisms, part two (p. 7)
- [E] Exhaustive checker (p. 8)
- Verdicts, part one (p. 9)
- Verdicts, part two (p. 10)
- Mutual exclusion and deadlock (p. 11)
- What counts as starvation (p. 12)
- Bounded waiting verdict (p. 13)
- Independent verifier (p. 14)
- A hand table, printed by two implementations (p. 15)
- Where two hand rules part company (p. 16)
- [M] Measurement design (p. 17)
- Measurement results, part one (p. 18)
- Measurement results, part two (p. 19)
- [M] Sweep: arrival rate (p. 20)
- [M] Sweep: writer service length (p. 21)
- [M] Sweep: reader population (p. 22)
- Finding F1 [E] (p. 23)
- Finding F2 [E] (p. 24)
- Finding F3 [E] (p. 25)
- Finding F4 [E] (p. 26)
- Finding F5 [M] (p. 27)
- Finding F6 [D] (p. 28)
- Figures, group 1 (p. 29)
- Figures, group 2 (p. 30)
- Figures, group 3 (p. 31)
- Figures, group 4 (p. 32)
- [D] When the instruments disagree (p. 33)
- The large seeded random study (p. 34)
- Provenance of every number (p. 35)
- Limitations (p. 36)
- How to reproduce (p. 37)
- Deliverables (p. 38)
- References and verification status (p. 39)


<!-- page 1 -->


<!-- page 2 -->


<!-- page 3 -->


## The question

Which readers-writers mechanisms actually guarantee mutual exclusion, deadlock freedom and freedom from starvation, and what does each guarantee cost in completed operations and waiting time?

This report states what was asked and how it was answered before giving any result, so a reader can try to refute the claim.


<!-- page 4 -->


## Two instruments, two kinds of claim

[E] The exhaustive checker enumerates every reachable global state of a small protocol instance. It answers yes/no questions and returns a witness schedule for every counterexample. [M] The seeded simulator runs a finite workload and counts operations and waiting times. The two instruments are never substituted for one another: a verdict is not a cost, and a cost is not a verdict.

- [E] asks whether a property holds in every reachable state.
- [M] asks how much work the mechanism completes.
- [D] is what happens when the two are compared carelessly.

> **Note.** When the tools disagree, suspect the tool first, not the data.


<!-- page 5 -->


## Model and notation

Each process is thinking, waiting, or inside the critical section. The global state is a tuple of per-process states, the entry queue, the signalled process and a turn variable. There is no unbounded counter, so the reachable graph is finite and a lasso is a genuine infinite execution. Readers may share the critical section; a writer must have it alone.

```text
state = (process states, entry queue, signalled, turn)
process state: 0 thinking, 1 waiting, 2 in critical section
readers may share; a writer requires an empty section
```
| Mechanisms | 7 |
|---|---|
| Configurations | 3 |
| Protocol instances | 12 |
| State limit | 120000 |


<!-- page 6 -->


## Mechanisms, part one

The mechanism is a parameter, not an implementation detail. These four are semaphore-style or monitor-style admission rules over the same shared state.

```text
readers_preference  : readers bypass waiting writers
writers_preference  : a waiting writer blocks new readers
fair_fifo           : entry queue, leading readers batched
mesa_signal         : signal without a place in the entry queue
```
*Admission rules, part one*

> **Note.** Preference trades one kind of starvation for another.


<!-- page 7 -->


## Mechanisms, part two

Hoare-style handoff gives the woken thread a place. Dekker and Peterson carry the mutual-exclusion pattern only between two participants; the checker only admits them in that configuration.

```text
hoare_signal        : signal with immediate handoff at the head
dekker2             : two participants, turn alternates on release
peterson2           : two participants, turn set on request
```
*Admission rules, part two*

> **Note.** Two-participant patterns cannot be assumed for a third.


<!-- page 8 -->


## [E] Exhaustive checker

[E] A breadth-first search from the all-thinking state records every reachable state and transition. Mutual exclusion and deadlock are checked on every state. Starvation is a reachable cycle on which the waiting process never gets its grant enabled while some other process does enter the critical section: a fair cycle, not merely an unlucky schedule. Bounded waiting is reported as minus one when such a cycle exists, because worst-case waiting is then infinite.

- Breadth-first exploration with memoisation.
- Fair-cycle search with a separate independent verifier.
- Truncated runs are counted and excluded from conclusions.

| Reachable states | 374 |
|---|---|
| Transitions | 785 |
| Truncated checks | 0 |


<!-- page 9 -->


## Verdicts, part one

[E] Every row is a separate protocol instance: one mechanism under one reader/writer configuration.

| protocol | states | ME | DL-free | SF | starving |
|---|---|---|---|---|---|
| readers_preference:2r1w | 33 | yes | yes | no | 1 |
| readers_preference:1r2w | 31 | yes | yes | yes | 0 |
| writers_preference:2r1w | 33 | yes | yes | yes | 0 |
| writers_preference:1r2w | 31 | yes | yes | no | 1 |
| fair_fifo:2r1w | 33 | yes | yes | yes | 0 |
| fair_fifo:1r2w | 31 | yes | yes | yes | 0 |

*Exhaustive verdicts [E]*


<!-- page 10 -->


## Verdicts, part two

[E] Every row is a separate protocol instance: one mechanism under one reader/writer configuration.

| protocol | states | ME | DL-free | SF | starving |
|---|---|---|---|---|---|
| mesa_signal:2r1w | 49 | yes | yes | no | 1 |
| mesa_signal:1r2w | 49 | yes | yes | no | 2 |
| hoare_signal:2r1w | 25 | yes | yes | yes | 0 |
| hoare_signal:1r2w | 31 | yes | yes | no | 1 |
| dekker2:1r1w | 18 | yes | yes | yes | 0 |
| peterson2:1r1w | 10 | yes | yes | yes | 0 |

*Exhaustive verdicts [E]*


<!-- page 11 -->


## Mutual exclusion and deadlock

[E] Both properties are checked on every reachable state, not on a sample of runs. The counts below are sums over all protocol instances.

| Mutual-exclusion violations | 0 |
|---|---|
| Deadlock states | 0 |
| Starving protocol instances | 5 |
| Starvation-free instances | 7 |

> **Note.** Zero violations here is a property of the model, not a claim about any particular runtime lock.


<!-- page 12 -->


## What counts as starvation

A process waiting a long time is not yet starved. Starvation requires an infinite fair execution in which it never enters. The checker therefore looks for a reachable cycle with two conditions.

- the waiting process's grant is never enabled on the cycle;
- some other process does enter the critical section on the cycle.

> **Note.** Without the second condition a stuttering schedule would fake starvation.


<!-- page 13 -->


## Bounded waiting verdict

[E] Minus one means a fair starvation cycle exists, so worst-case waiting is infinite. Other entries are the largest shortest path into the critical section, counted in state transitions.

| protocol | max bound |
|---|---|
| readers_preference:2r1w | -1 |
| readers_preference:1r2w | 2 |
| writers_preference:2r1w | 3 |
| writers_preference:1r2w | -1 |
| fair_fifo:2r1w | 5 |
| fair_fifo:1r2w | 5 |
| mesa_signal:2r1w | -1 |
| mesa_signal:1r2w | -1 |

*Bounded waiting [E]*

> **Note.** Transitions are not time steps; see the divergence page.


<!-- page 14 -->


## Independent verifier

[E] No counterexample is accepted on the checker's word. An independent interpreter, written separately and sharing no transition function with the checker, replays the prefix and then the cycle twice. It re-derives every admission decision, checks that the starving process stays waiting, and checks mutual exclusion after every action. The table records the result for every witness.

| protocol | process | steps | valid |
|---|---|---|---|
| readers_preference:2r1w | 2 | 10 | yes |
| writers_preference:1r2w | 0 | 10 | yes |
| mesa_signal:2r1w | 2 | 13 | yes |
| mesa_signal:1r2w | 1 | 11 | yes |
| mesa_signal:1r2w | 2 | 11 | yes |
| hoare_signal:1r2w | 0 | 14 | yes |

*Every witness re-checked [E]*

```text
R0 grant
R0 release
R0 request
```
*First starvation cycle (witness)*

| Witnesses | 6 |
|---|---|
| Verified valid | 6 |


<!-- page 15 -->


## A hand table, printed by two implementations

[M] A small independent interpreter replays a fixed action sequence for writers preference. Its process-state timeline is compared step by step with the checker's transition function.

| step | action | process states | agree |
|---|---|---|---|
| 1 | R0 request | (1, 0, 0) | yes |
| 2 | R0 grant | (2, 0, 0) | yes |
| 3 | R1 request | (2, 1, 0) | yes |
| 4 | R1 grant | (2, 2, 0) | yes |
| 5 | W2 request | (2, 2, 1) | yes |
| 6 | R0 release | (0, 2, 1) | yes |
| 7 | R1 release | (0, 0, 1) | yes |
| 8 | W2 grant | (0, 0, 2) | yes |
| 9 | W2 release | (0, 0, 0) | yes |

*Hand trace [M]*

| Compared steps | 9 |
|---|---|
| Agree | yes |


<!-- page 16 -->


## Where two hand rules part company

[M] On the same prefix, writers preference refuses a new reader while a writer waits, and readers preference admits it. The first differing step is a printed witness: the two rules are different algorithms.

```text
R0 request
R0 grant
W2 request
R1 request
R1 grant
```
*Divergence witness*

| First divergent step | 5 |
|---|---|
| Writers preference allows | no |
| Readers preference allows | yes |
| Divergent decisions | 1 |


<!-- page 17 -->


## [M] Measurement design

[M] A seeded discrete-event simulator advances in integer steps. At each step it finishes due service, admits new requests with a fixed arrival probability, and grants as many compatible processes as the mechanism allows. It records completed reads and writes, the mean and maximum waiting time, throughput and the number of finite runs with zero writer completions. The mechanism's admission rule is shared with the checker on purpose: the policy is the object under study, not the instrument.

| Random seed | 20261120 |
|---|---|
| Horizon | 400 |
| Trials | 3 |
| Arrival probability | 0.55 |
| Reader service | 3 |
| Writer service | 2 |


<!-- page 18 -->


## Measurement results, part one

[M] Sums over the seeded trials for each instance.

| protocol | reads | writes | ops | mean wait |
|---|---|---|---|---|
| readers_preference:2r1w | 622 | 47 | 669 | 1.455 |
| readers_preference:1r2w | 286 | 168 | 454 | 4.348 |
| writers_preference:2r1w | 318 | 345 | 663 | 2.078 |
| writers_preference:1r2w | 22 | 564 | 586 | 3.066 |
| fair_fifo:2r1w | 443 | 227 | 670 | 1.847 |
| fair_fifo:1r2w | 171 | 340 | 511 | 3.798 |

*Completed work [M]*


<!-- page 19 -->


## Measurement results, part two

[M] Sums over the seeded trials for each instance.

| protocol | reads | writes | ops | mean wait |
|---|---|---|---|---|
| mesa_signal:2r1w | 609 | 53 | 662 | 1.635 |
| mesa_signal:1r2w | 296 | 147 | 443 | 4.513 |
| hoare_signal:2r1w | 314 | 351 | 665 | 2.111 |
| hoare_signal:1r2w | 21 | 566 | 587 | 3.076 |
| dekker2:1r1w | 230 | 243 | 473 | 1.689 |
| peterson2:1r1w | 235 | 235 | 470 | 1.774 |

*Completed work [M]*


<!-- page 20 -->


## [M] Sweep: arrival rate

[M] One parameter is swept while the rest are held fixed. The curve and the table are drawn from an array in the generated data file.

![Figure 1: arrival probability per idle process and step / writer share of completed operations](fig_rw7_sweep_arrival.png)

*Figure 1. arrival probability per idle process and step / writer share of completed operations*

| x | readers_preference | writers_preference | fair_fifo | mesa_signal | hoare_signal |
|---|---|---|---|---|---|
| 0.15 | 0.3146 | 0.3951 | 0.3256 | 0.2204 | 0.38 |
| 0.3 | 0.2198 | 0.381 | 0.3315 | 0.1537 | 0.3894 |
| 0.45 | 0.1168 | 0.4664 | 0.3416 | 0.1194 | 0.4581 |
| 0.6 | 0.0607 | 0.5817 | 0.3338 | 0.0459 | 0.5392 |
| 0.75 | 0.0166 | 0.6503 | 0.3343 | 0.0222 | 0.6651 |

*Sweep values [M]*


<!-- page 21 -->


## [M] Sweep: writer service length

[M] One parameter is swept while the rest are held fixed. The curve and the table are drawn from an array in the generated data file.

![Figure 2: writer critical-section length (integer steps) / mean waiting time (steps)](fig_rw7_sweep_service.png)

*Figure 2. writer critical-section length (integer steps) / mean waiting time (steps)*

| x | readers_preference | writers_preference | fair_fifo | mesa_signal | hoare_signal |
|---|---|---|---|---|---|
| 1 | 1.624 | 1.206 | 1.373 | 1.546 | 1.193 |
| 2 | 1.332 | 2.079 | 1.826 | 1.636 | 2.041 |
| 3 | 1.699 | 3.132 | 2.301 | 1.594 | 3.061 |
| 4 | 1.681 | 3.967 | 2.881 | 1.775 | 3.779 |
| 6 | 1.934 | 5.974 | 4.042 | 2.09 | 5.868 |

*Sweep values [M]*


<!-- page 22 -->


## [M] Sweep: reader population

[M] One parameter is swept while the rest are held fixed. The curve and the table are drawn from an array in the generated data file.

![Figure 3: number of readers (one writer) / writer completions](fig_rw7_sweep_readers.png)

*Figure 3. number of readers (one writer) / writer completions*

| x | readers_preference | writers_preference | fair_fifo | mesa_signal | hoare_signal |
|---|---|---|---|---|---|
| 1 | 150 | 349 | 238 | 130 | 352 |
| 2 | 52 | 331 | 223 | 45 | 340 |
| 3 | 10 | 336 | 228 | 8 | 334 |
| 4 | 4 | 345 | 221 | 4 | 355 |

*Sweep values [M]*


<!-- page 23 -->


## Finding F1 [E]

Readers preference starves the writer outright

[E] A fair cycle exists in which the writer never enters the critical section while readers keep entering. Its grant is never enabled on the cycle, so the schedule is fair, not merely unlucky.

| cycle length | 3 |
|---|---|
| other grants | 1 |
| protocol | readers_preference:2r1w |
| starving process | 2 |
| states | 33 |
| wait bound | -1 |

*Numbers from the data file*

```text
R0 grant
R0 release
R0 request
```
*Witness schedule [E]*

> **Note.** Source: protocols[readers_preference:2r1w].witness


<!-- page 24 -->


## Finding F2 [E]

Writers preference moves the starvation to the reader

[E] With two writers and one reader, a fair cycle keeps the reader waiting forever. Preference is a parameter that trades one kind of starvation for another; it does not remove starvation.

| cycle length | 3 |
|---|---|
| protocol | writers_preference:1r2w |
| starving process | 0 |
| states | 31 |
| wait bound | -1 |

*Numbers from the data file*

```text
W1 release
W1 request
W1 grant
```
*Witness schedule [E]*

> **Note.** Source: protocols[writers_preference:1r2w].witness


<!-- page 25 -->


## Finding F3 [E]

A Mesa monitor does not bound waiting until the woken thread has a place

[E] Signalling a waiting writer without giving it the head of the entry queue leaves fresh readers free to bypass it. Hoare-style handoff on the same configuration is starvation-free.

| hoare starving | 0 |
|---|---|
| hoare states | 25 |
| hoare wait bound | 3 |
| mesa starving | 1 |
| mesa states | 49 |

*Numbers from the data file*

```text
R0 grant
R0 release
R0 request
```
*Witness schedule [E]*

> **Note.** Source: protocols[mesa_signal:2r1w] vs protocols[hoare_signal:2r1w]


<!-- page 26 -->


## Finding F4 [E]

FIFO is starvation-free; Dekker and Peterson carry the pattern only between two

[E] The FIFO queue and the two two-participant patterns have no fair starvation cycle at all in the checked configurations. Mutual exclusion and deadlock freedom hold for every reachable state of every protocol.

| deadlock states | 0 |
|---|---|
| dekker states | 18 |
| fifo states | 33 |
| fifo wait bound | 5 |
| mutual exclusion violations | 0 |
| peterson states | 10 |

*Numbers from the data file*

> **Note.** Source: protocols[] (all)


<!-- page 27 -->


## Finding F5 [M]

Verification calls schedules equivalent where measurement separates them

[M] Under one seeded workload the mechanisms complete different numbers of operations, show different mean waiting times, and give the writer very different shares. A yes/no verdict says nothing about any of these quantities.

| mean wait fair fifo | 3.798 |
|---|---|
| mean wait readers preference | 4.348 |
| operations fair fifo | 511 |
| operations readers preference | 454 |
| wait samples | 514 |

*Numbers from the data file*

> **Note.** Source: measurements[]


<!-- page 28 -->


## Finding F6 [D]

The two instruments use different clocks; the finite-window control found no artefact

[D] The checker counts bounded waiting in state transitions; the simulator counts waiting in time steps that include service time. Comparing those two magnitudes directly is a category error, not a contradiction. A control search over the seeded random study found the recorded number of finite-window artefacts: every run with zero writer completions belonged to a mechanism the checker had already proved capable of starvation. At this horizon the instruments agreed; suspect the instrument first, and never promote a short run into a correctness verdict.

| artefacts | 0 |
|---|---|
| checker max bound | 5 |
| control mechanisms | 1 |
| measurement max wait | 226 |
| measurements | 1200 |
| short horizon | 200 |
| starved runs | 64 |
| truncated | 0 |
| workloads | 240 |

*Numbers from the data file*

> **Note.** Source: random.per_mechanism[] + protocols[].bounded_wait + measurements[].max_wait


<!-- page 29 -->


## Figures, group 1

[M] Every chart is drawn from output/experiments.json by code/make_diagrams.py. Captions name the data source; no value is typed into a figure or into this report.

![Figure 4: Reachable state space. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_states.png)

*Figure 4. Reachable state space. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*

![Figure 5: Fair starvation cycles. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_starvation.png)

*Figure 5. Fair starvation cycles. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*


<!-- page 30 -->


## Figures, group 2

[M] Every chart is drawn from output/experiments.json by code/make_diagrams.py. Captions name the data source; no value is typed into a figure or into this report.

![Figure 6: Bounded waiting verdict. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_bounded_wait.png)

*Figure 6. Bounded waiting verdict. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*

![Figure 7: Completed operations. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_operations.png)

*Figure 7. Completed operations. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*


<!-- page 31 -->


## Figures, group 3

[M] Every chart is drawn from output/experiments.json by code/make_diagrams.py. Captions name the data source; no value is typed into a figure or into this report.

![Figure 8: Mean waiting time. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_wait.png)

*Figure 8. Mean waiting time. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*

![Figure 9: Writer share. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_writer_share.png)

*Figure 9. Writer share. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*


<!-- page 32 -->


## Figures, group 4

[M] Every chart is drawn from output/experiments.json by code/make_diagrams.py. Captions name the data source; no value is typed into a figure or into this report.

![Figure 10: Instrument divergence control. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.](fig_rw7_artefacts.png)

*Figure 10. Instrument divergence control. Generated from output/experiments.json by code/make_diagrams.py; every value is read at build time.*


<!-- page 33 -->


## [D] When the instruments disagree

[D] The checker counts bounded waiting in state transitions; the simulator counts waiting in time steps that include service time. Comparing those two magnitudes directly is a category error, not a contradiction. A control search over the seeded random study found the recorded number of finite-window artefacts: every run with zero writer completions belonged to a mechanism the checker had already proved capable of starvation. At this horizon the instruments agreed; suspect the instrument first, and never promote a short run into a correctness verdict.

| Checker clock | state transitions |
|---|---|
| Measurement clock | time steps including service |
| Largest checker bound | 5 |
| Largest measured wait | 226 |
| Finite-window artefacts | 0 |

*Different units [D]*

> **Note.** [D] finite measurement windows are not proofs; every such case is an instrument artefact.


<!-- page 34 -->


## The large seeded random study

[M] A fixed-seed generator varies the reader population, the writer population, the arrival probability and both service lengths. Each workload is run once per mechanism in a short window. [D] Zero-writer runs are counted but never promoted into correctness verdicts.

| mechanism | zero-writer runs | artefacts | mean writer share |
|---|---|---|---|
| fair_fifo | 0 | 0 | 0.3764 |
| hoare_signal | 0 | 0 | 0.6563 |
| mesa_signal | 32 | 0 | 0.1325 |
| readers_preference | 32 | 0 | 0.1423 |
| writers_preference | 0 | 0 | 0.6608 |

*Random study [M]/[D]*

| Workloads | 240 |
|---|---|
| Measurements | 1200 |
| Short horizon | 200 |
| Truncated | 0 |


<!-- page 35 -->


## Provenance of every number

A test collects every numeric token allowed by the data file and fails if the report prints a number that is not there. The three producer programs are checksummed below.

| file | bytes | sha256 prefix |
|---|---|---|
| code/rw_core.py | 19357 | f6a1b8d85938 |
| code/run_experiments.py | 35583 | c84a574f8110 |
| code/make_diagrams.py | 3422 | b4de2991575b |

*Producer checksums*

| Checksum mismatches | 0 |
|---|---|

> **Note.** Checksums of the three programs that produced the data and the figures. No external author, year, DOI or page number is claimed anywhere in this exercise.


<!-- page 36 -->


## Limitations

The exhaustive results hold for the checked small configurations, not for an unbounded number of processes. The simulator uses a seeded synthetic workload rather than a particular operating system's lock implementation, so absolute waiting times are not portable even though the ordering is reproducible. No external author, year, DOI or page number is claimed: the references table states the verification status of every entry.

- Small configurations only for exhaustive results.
- Synthetic seeded workload, not a specific OS lock.
- No external bibliographic metadata is claimed.


<!-- page 37 -->


## How to reproduce

Run from the multi-exercise tree root for the reports, and from the exercise folder for the data and figures. On a flattened branch the code and tests sit at the root.

```text
python3 code/run_experiments.py
python3 code/make_diagrams.py
python3 -m pytest tests -q
python3 tools/build_report.py rw7_en exercise-7 REPORT_EN
python3 tools/build_report.py rw7_fa exercise-7 REPORT_FA
python3 tools/verify_builds.py
```
*Commands*


<!-- page 38 -->


## Deliverables

The English and Persian reports are rendered from one content model, so their page counts agree with the produced PDFs.

| path | what |
|---|---|
| REPORT_EN.md / REPORT_FA.md | Markdown of the same model |
| docs/REPORT_EN.docx / .pdf | English Word and PDF |
| docs/REPORT_FA.docx / .pdf | Persian Word and PDF |
| output/experiments.json | the only source of numbers |
| diagrams/ | generated figures |
| code/ + tests/ | code and green tests |

*Artefact table*

| Figures | 10 |
|---|---|
| Findings | 6 |
| Sweeps | 3 |


<!-- page 39 -->


## References and verification status

Every entry states whether it was verified inside this repository or left explicitly unverified. No author, year, DOI or page number is invented.

| item | status |
|---|---|
| The generated data, figures and programs in this repository | verified in this repository |
| Classic readers-preference semaphore solution | unverified: no external bibliographic database queried |
| Mesa and Hoare monitor semantics | unverified: no external bibliographic database queried |
| Dekker and Peterson two-process mutual exclusion | unverified: no external bibliographic database queried |

*Verified and unverified*
