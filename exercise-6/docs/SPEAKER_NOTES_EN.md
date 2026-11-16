# Speaker notes — English

## Slide 1. Least Slack Time: a measured account

- Combining five exercises into one argument
- Verification for truth, measurement for cost
- Every number inherited and checksum-recorded

**Speaker text:** State the paper's claim: what the definition cannot tell us, measurement can.

## Slide 2. The question

- What does LST minimise?
- Is the optimality claim checkable?
- What does correctness cost?

**Speaker text:** Three questions, three different instruments.

## Slide 3. Method: two separate instruments

- [E] exhaustive search decides feasibility and returns a witness
- [M] discrete-event simulation counts what a run costs
- [D] disagreements suspect the instrument first

**Speaker text:** Never mix the two. This is the methodological spine of every exercise.

## Slide 4. Model

- One preemptive processor, integer time
- Execution equals worst case
- Constrained deadlines only

**Speaker text:** Explain why integer time lets a hand table and a program agree unit by unit.

## Slide 5. Why the implicit regime was abandoned

- Control: 120 of 120 implicit sets feasible [E]
- Constrained study: 140 feasible, 100 infeasible [E]
- A yardstick that cannot vary cannot test

**Speaker text:** This design decision is stated before any result, as the method requires.

## Slide 6. The large study

- 240 fixed-seed constrained sets [E]
- 0 truncated runs, 140 valid witnesses
- Tie-break changed the verdict on 0 sets [M]

**Speaker text:** No truncated run is used as a finding; say that explicitly.

## Slide 7. Optimality, checked

- LST and EDF: zero misses on 140 feasible sets [M]
- RM: 23 misses on those sets [M]
- Across exercise 2, RM misses 48 [M]

**Speaker text:** RM failing is a counterexample, not an instrument defect.

## Slide 8. Cost, measured

- First set of exercise 1: LST 10, EDF 0 preemptions [M]
- Summed over exercise 2: LST 188, EDF 44 [M]
- Correctness does not order them; cost does

**Speaker text:** This is the paper's unexpected result, not a restated definition.

## Slide 9. The hand table

- Exercise 3 compared 24 instants [M]
- 6 independent traces agreed
- Two hand rules diverged at 6 instants

**Speaker text:** Two independent programs agreeing is checked by a test, not asserted.

## Slide 10. The disagreement that was an instrument

- Exercise 1: 7 naive comparisons agree
- 8 aligned comparisons agree
- Aligning the job sets removes the mismatch

**Speaker text:** Tell the forced-idle bug story: the checker was the culprit, not the exchange lemma.

## Slide 11. Artefacts we refuse to report as findings

- 100 cap artefacts counted [D]
- A truncated checker reports a feasible set as infeasible
- Raising the cap restores the verdict

**Speaker text:** Suspect the instrument first. This is the standing rule.

## Slide 12. What verification cannot say

- A verdict groups all feasible schedules as equivalent
- Measurement separates them by cost
- The checker's witness is a printed counterexample

**Speaker text:** Complement, not contradiction: the verdict answers a coarser question.

## Slide 13. Inherited provenance

- 20 values inherited by exercise 5
- 12 slides in its bilingual deck
- This paper re-reads all five source data files

**Speaker text:** Mention the consistency pass and that its mismatch count must be zero.

## Slide 14. Which policy, and when

- Correctness only: LST and EDF tie on feasible sets
- Preemption cost: the data favours EDF
- Jitter: measure it, do not assume a ranking

**Speaker text:** A recommendation grounded in data. State where the measurement does not separate.

## Slide 15. Limitations

- Single processor, no migration or cache effects
- Execution equals worst case
- Checker cap and truncated runs

**Speaker text:** We write the limitations ourselves before anyone else does.

## Slide 16. References and verification status

- 4 reference entries, each with an explicit status
- No external author, year, DOI or page number is asserted
- Unverifiable items are labelled unverified

**Speaker text:** Explain why: no bibliographic network access in this environment.

## Slide 17. Conclusion

- Definitions say what LST is
- Verification says what is true
- Measurement says what it costs

**Speaker text:** Close on the gap between the two instruments, which is the contribution.
