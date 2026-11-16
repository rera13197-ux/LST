# Speaker notes — English

## Slide 1. Least Slack Time in a few minutes

- A dynamic-priority rule for one preemptive processor
- Run the job that can wait the least
- Two instruments: verification and measurement

**Speaker text:** Open by saying this presentation reports measurements, not definitions. Every number shown was produced by a program in an earlier exercise.

*Source: provenance.inherited*

## Slide 2. What slack means

- slack = deadline - now - remaining work
- It is how long a job may still wait
- The smallest slack is the most urgent job

**Speaker text:** This is the only definition in the deck. Say it once and move to data.

*Source: core/lst_core.py*

## Slide 3. What we actually measured

- Exercise 1: 8 task sets, 6 feasible and 2 infeasible [E]
- Exercise 2: 8 workloads
- Exercise 4: 240 fixed-seed random sets

**Speaker text:** Read the counts as verdicts [E], not as performance claims.

## Slide 4. Why deadlines must be constrained

- Implicit-deadline control: 120 of 120 sets feasible [E]
- A checker that always says feasible cannot be tested
- Constrained deadlines: 140 feasible, 100 infeasible [E]

**Speaker text:** This is the design decision that gives the experiment its power.

## Slide 5. Optimality, checked

- On 140 feasible sets LST misses zero deadlines [M]
- RM misses 23 on the same sets [M]
- Every feasible witness was independently re-checked [E]

**Speaker text:** Distinguish the verdict from the counterexample: RM failing is a result, not a bug.

## Slide 6. But correctness is not cost

- Exercise 1, first set: LST 10 preemptions, EDF 0 [M]
- Across exercise 2: LST 188, EDF 44 [M]
- Both meet every deadline on feasible sets

**Speaker text:** This slide is the point of the whole project: the definition cannot tell you this.

## Slide 7. A hand table that the program prints

- Exercise 3 compared 24 integer instants [M]
- 6 independent hand traces agreed
- Two hand rules parted company at 6 instants

**Speaker text:** Two independent programs agreeing is a measurement, not a proof.

## Slide 8. When the instruments disagree

- Exercise 1: 7 naive comparisons agree
- 8 aligned comparisons agree
- The instrument is the first suspect, not the theorem

**Speaker text:** Describe the forced-idle bug history: the checker was wrong, not the exchange argument.

## Slide 9. A defect made by a state cap

- Exercise 4 counted 100 cap artefacts [D]
- A truncated run reports a feasible set as infeasible
- Truncated results are artefacts, never findings

**Speaker text:** Emphasise the method rule: suspect the tool before the data or the proof.

## Slide 10. What the checker cannot say

- A feasibility verdict groups schedules as equivalent
- Measurement separates them by preemption count
- The witness schedule is a printed counterexample

**Speaker text:** Do not claim the checker is wrong here; it answers a coarser question.

## Slide 11. Which one should you use

- If correctness is the only yardstick, LST and EDF tie
- If preemption cost matters, the data favours EDF
- If response jitter matters, measure it too

**Speaker text:** A recommendation on data, not on preference. Say what the measurement does not separate.

## Slide 12. Takeaways

- Definitions state what LST is
- Verification states what is true
- Measurement states what it costs

**Speaker text:** Close by repeating that every number in this deck was inherited and checksum-recorded.
