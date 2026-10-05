# Minimized DFA Specification

## 1. Overview

This document defines the minimized DFA for L_TIME, obtained by applying
Moore's partitioning algorithm to the 17-state DFA in DFA_SPECIFICATION.md,
exactly as finalized in the revised DFA Minimization Report.

Result: 17 states reduced to 15 states by merging the indistinguishable
pairs (S10, S15) and (S13, S14). The minimized automaton recognizes the
same language with reduced memory and simpler lookup logic.

## 2. Formal Definition

Mmin = (Qmin, Σ, δmin, M0, Fmin):

- Qmin = {M0, M1, ..., M14} (15 states)
- Σ = {0,1,2,3,4,5,6,7,8,9, :, SPACE, A, M, P}
- δmin : Qmin × Σ → Qmin (total; missing entries go to M14)
- M0 = start state
- Fmin = {M10, M11}

## 3. State Mapping and Semantics

| Minimized | Original (17-state) | Meaning |
|---|---|---|
| M0 | S0 | Start; nothing read |
| M1 | S1 | Hour starts with 0 |
| M2 | S2 | Hour starts with 1 |
| M3 | S3 | Hour starts with 2 (24-hour only) |
| M4 | S4 | Hour valid only as 24-hour |
| M5 | S5 | Hour valid in both formats |
| M6 | S6 | 24-hour-only hour, colon read |
| M7 | S7 | Shared hour, colon read |
| M8 | S8 | Minute tens, 24-hour-only path |
| M9 | S9 | Minute tens, shared path |
| M10 | S10 + S15 | ACCEPTING: complete 24-hour or complete 12-hour time |
| M11 | S11 | ACCEPTING: complete 24-hour time that may extend to 12-hour |
| M12 | S12 | Space read after minutes |
| M13 | S13 + S14 | A or P read; waiting for M |
| M14 | ∅ | Dead (trap) state |

## 4. Minimization Process (Moore's Algorithm)

Unreachable states: none (subset construction only creates reachable states).

Partition rounds (full derivation in the revised DFA Minimization Report):

- P0 (2 classes): accepting {S10, S11, S15} vs non-accepting rest.
- P1 (4): {S8, S9} split (reach accepting on any digit); {S13, S14} split (reach accepting on M).
- P2 (6): {S6, S7} split (go to {S8,S9} on 0-5); {S12} split (goes to {S13,S14} on A/P).
- P3 (8): {S10, S15} separated from S11 (S11 goes to S12 on SPACE); {S4, S5} split.
- P4 (11): {S1, S2} stay together; {S3}, {S8}, {S9} separate.
- P5 (13): {S0} and {∅} separate; {S6}, {S7} separate.
- P6 (14): {S4}, {S5} separate.
- P7 (15): {S1}, {S2} separate.
- P8: identical to P7; refinement stops.

Final equivalence classes: all singletons except {S10, S15} and {S13, S14}.

Indistinguishability confirmation:

- S10 ≡ S15: both accepting; every symbol leads to ∅ from both.
- S13 ≡ S14: both non-accepting; M leads to S15 from both; all other symbols lead to ∅.

## 5. Transition Table

Legend: → start; * accepting; M14 dead. Grouped columns apply per digit.

| State | 0 | 1 | 2 | 3 | 4–5 | 6–9 | : | ␣ | A | P | M |
|---|---|---|---|---|---|---|---|---|---|---|---|
| → M0 | M1 | M2 | M3 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |
| M1 | M4 | M5 | M5 | M5 | M5 | M5 | ∅ | ∅ | ∅ | ∅ | ∅ |
| M2 | M5 | M5 | M5 | M4 | M4 | M4 | ∅ | ∅ | ∅ | ∅ | ∅ |
| M3 | M4 | M4 | M4 | M4 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |
| M4 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | M6 | ∅ | ∅ | ∅ | ∅ |
| M5 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | M7 | ∅ | ∅ | ∅ | ∅ |
| M6 | M8 | M8 | M8 | M8 | M8 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |
| M7 | M9 | M9 | M9 | M9 | M9 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |
| M8 | M10 | M10 | M10 | M10 | M10 | M10 | ∅ | ∅ | ∅ | ∅ | ∅ |
| M9 | M11 | M11 | M11 | M11 | M11 | M11 | ∅ | ∅ | ∅ | ∅ | ∅ |
| *M10 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |
| *M11 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | M12 | ∅ | ∅ | ∅ |
| M12 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | M13 | M13 | ∅ |
| M13 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | M10 |
| M14 | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |

## 6. Example Traces

- 23:45: M0 -2-> M3 -3-> M4 -:-> M6 -4-> M8 -5-> M10 (accept)
- 09:30 AM: M0 -0-> M1 -9-> M5 -:-> M7 -3-> M9 -0-> M11 -␣-> M12 -A-> M13 -M-> M10 (accept)
- 12:00: M0 -1-> M2 -2-> M5 -:-> M7 -0-> M9 -0-> M11 (accept)
- 13:00 PM: ... -0-> M10 -␣-> M14 (dead; 24-hour time cannot take a meridiem)
- 12:60: M7 -6-> M14 (minute tens must be 0-5)
- 09:30AM: M11 -A-> M14 (missing required single space)

## 7. Comparison and Improvement

- Original DFA: 17 states (16 + ∅). Minimized DFA: 15 states.
- Improvement: two fewer states, simpler lookup logic, and a single unified
  accepting state M10 for "complete time", which simplifies the simulator's
  acceptance test to {M10, M11}.

## 8. Implementation Notes (Implemented in core/automaton.py)

1. Alphabet validation runs before DFA execution (Layer 1).
2. ' ' is mapped to SPACE before table lookup.
3. Missing transitions go to M14.
4. Dead-state optimization: the read loop breaks immediately upon entering M14.
5. Accept only if the final state is M10 or M11.

## 9. Machine-Readable and Diagram Files

- data/minimized_dfa.json: M-named table consumed by core/automaton.py.
- diagrams/minimized_dfa.dot: horizontal diagram with merged-state labels.