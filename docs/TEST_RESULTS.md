# Test Cases and Results

Project: Time Format Validator
Group: Chicken Wings
Course: CCAUTOMA / COM241
Supports: Section 18 (Test Cases and Results) of the final report

## 1. Testing Methodology

Testing was performed at three levels:

1. Unit tests per module: Alphabet Check (Layer 1), Lexical Normalizer (Layer 2), minimized DFA engine, trace builder, and diagnostics.
2. Behavior-matrix tests over the curated sample set defined in core/samples.py.
3. Integration smoke tests over the full two-layer pipeline.

The system under test implements the two-layer policy:

- Layer 1 (Formal): Alphabet Check against the 15-symbol master alphabet, then simulation of the raw input on the minimized DFA.
- Layer 2 (System): Lexical normalization (N1 meridiem case-fold, N2 hour padding), then simulation of the normalized input on the minimized DFA.

Rejections are classified into three layers: Alphabet Check, Automaton (Dead State M14), and Incomplete Input.

Boundary values emphasized per the Language Analyst handoff: 00, 12, 23, 24, 59, 60.

All suites were executed from the project root via `python -m <suite>`. The tables below summarize the verbatim console output. Each suite section begins with a Purpose line (what the suite proves) and a per-test explanation of what each check does.

## 2. Test Environment

| Item | Value |
| --- | --- |
| Python | 3.12.8 (pyenv-win) |
| Operating system | Windows, CMD |
| Streamlit | 1.64.0 |
| Dependencies | per requirements.txt |
| Automaton under test | Minimized DFA M0-M14; start M0; F = {M10, M11}; M14 dead |

## 3. Suite Summary

| # | Suite | Scope | What it verifies | Checks | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | tests.test_alphabet_check | Unit, Layer 1 | The symbol gate: accepts every symbol of the 15-symbol master alphabet and flags illegal symbols with exact indices | 26 | ALL PASSED |
| 2 | tests.test_normalizer | Unit, Layer 2 | The N1 case-fold and N2 hour-padding rules, plus the no-over-correction guarantee | 14 | ALL PASSED |
| 3 | tests.test_automaton | Unit, DFA engine | Accepting, dead-state, and incomplete verdicts of M0-M14, plus trace invariants and the dead-state early break | 28 | ALL PASSED |
| 4 | tests.test_trace | Unit, trace builder | The GUI trace table structure and the verdict summary texts | 7 | ALL PASSED |
| 5 | tests.test_samples | Behavior matrix | Expected-vs-actual two-layer verdicts and detected formats over 18 curated samples | 33 | ALL PASSED |
| 6 | tests.test_diagnostics | Unit, rejection layers | Rejection-layer classification, failure index/symbol, and expected-symbol hints | 13 | ALL PASSED |
| 7 | tests.smoke_test.test_layers | Integration, two layers | Raw-vs-normalized wiring: casual inputs flip FAIL to PASS; invalid inputs fail both layers | 6 cases | ALL CORRECT |
| 8 | tests.smoke_test.test_dfa | Integration, engine traces | The key transitions taken on representative accepting and dead-state paths | 6 cases | ALL CORRECT |
| 9 | tests.smoke_test.test_pipeline | Integration, full pipeline | End-to-end equality with the behavior matrix (no integration drift) | 18 cases | ALL PASSED |

Total: 121 unit and behavior checks plus 30 integration cases = 151 executed, all passing.

## 4. Detailed Results

### 4.1 Suite 1 - Alphabet Check (Layer 1)

Purpose: Verify the first gate of the pipeline. The alphabet check must accept every symbol of the master alphabet, reject any symbol outside it, and report the exact index and character of each violation so the GUI can point at the offending symbol.

What each check does:
- TC-A01 verifies the alphabet definition itself: the constant must contain exactly 15 symbols.
- TC-A02 feeds each of the 15 symbols alone and requires acceptance, proving no legal symbol is ever falsely flagged.
- TC-A03 feeds legal-but-structurally-edge strings and requires zero invalid-symbol reports, proving the checker flags characters only, never structure.
- TC-A04 to TC-A07 feed illegal characters (lowercase am/pm, arbitrary letters, '-', 'X') and require the exact (index, symbol) pairs that the diagnostics panel displays.
- TC-A08 confirms the empty string passes this layer, leaving structural rejection of empty input to the DFA (separation of concerns).
- Check count reconciliation: 1 + 15 (TC-A02) + 5 (TC-A03) + 1 + 1 + 1 + 1 + 1 = 26.

| ID | Check | Observed | Result |
| --- | --- | --- | --- |
| TC-A01 | Master alphabet size | 15 | PASS |
| TC-A02 | Each of the 15 symbols of Σ_TIME accepted alone | 15/15 OK | PASS |
| TC-A03 | '00:00', '23:59', '12:49 AM', '09:30AM', '09:30  AM' pass with no invalid symbols | (True, []) each | PASS |
| TC-A04 | '09:30 am' flags lowercase letters | [(6, 'a'), (7, 'm')] | PASS |
| TC-A05 | 'ab:cd' flags all letters | [(0, 'a'), (1, 'b'), (3, 'c'), (4, 'd')] | PASS |
| TC-A06 | '09-30' flags '-' | [(2, '-')] | PASS |
| TC-A07 | '09:30 XM' flags 'X' | [(6, 'X')] | PASS |
| TC-A08 | Empty input contains no invalid symbols (structure handled by the DFA) | (True, []) | PASS |

### 4.2 Suite 2 - Lexical Normalizer (Layer 2)

Purpose: Verify the two normalization rules in isolation (N1 folds the meridiem to uppercase; N2 pads a one-digit hour), and, critically, verify that the normalizer never over-corrects strings it must leave untouched.

What each check does:
- TC-N01 to TC-N04 verify N1 on lowercase and mixed-case meridiems.
- TC-N05 to TC-N06 verify N2 on one-digit hours, with and without a meridiem suffix.
- TC-N07 verifies that N1 and N2 compose correctly on a single input.
- TC-N08 verifies no over-correction: already-canonical strings and structurally invalid strings (missing space, double space, out-of-range values) must come out byte-identical, so the normalizer can never mask a genuine error.
- Check count reconciliation: 7 + 7 (TC-N08 strings) = 14.

| ID | Check | Observed | Result |
| --- | --- | --- | --- |
| TC-N01 | N1: '09:30 am' case-folded | '09:30 AM' | PASS |
| TC-N02 | N1: '09:30 pm' case-folded | '09:30 PM' | PASS |
| TC-N03 | N1: '09:30 Am' mixed case | '09:30 AM' | PASS |
| TC-N04 | N1: '12:00 pM' mixed case | '12:00 PM' | PASS |
| TC-N05 | N2: '9:30' hour padded | '09:30' | PASS |
| TC-N06 | N2: '1:05 PM' hour padded | '01:05 PM' | PASS |
| TC-N07 | N1+N2 combined: '9:30 am' | '09:30 AM' | PASS |
| TC-N08 | No over-correction: '09:30AM', '09:30  AM', '24:00', '12:60', '10:15', '12:49 AM', '00:00' unchanged | identical output, 7/7 | PASS |

### 4.3 Suite 3 - Minimized DFA Engine

Purpose: Verify the core automaton (M0-M14) against the language definition: valid strings must end in an accepting state, structurally invalid strings must sink to the dead state M14, truncated strings must halt in a non-accepting non-dead state, and the trace machinery must be internally consistent, including the dead-state early-break optimization.

What each check does:
- Accepted-inputs table (10 rows): feeds boundary and representative valid strings and checks the final state is in F = {M10, M11}.
- Dead-state table (9 rows): feeds invalid strings (bad hour, bad minute, missing colon, missing space, double space, wrong suffix) and checks every one sinks to M14.
- Incomplete table (3 rows): feeds truncated prefixes and checks the machine halts in the specific non-accepting, non-dead state that produces the "incomplete" verdict.
- TC-M01 to TC-M05 verify trace invariants: the trace starts at M0, consecutive steps chain, it ends at the reported final state, its length equals the input length, and the dead-state transition is recorded exactly once (early break).

Accepted inputs (final state in F):

| Input | Final state | Result |
| --- | --- | --- |
| '00:00' | M10 | PASS |
| '12:00' | M11 | PASS |
| '12:49' | M11 | PASS |
| '13:00' | M10 | PASS |
| '18:30' | M10 | PASS |
| '23:59' | M10 | PASS |
| '01:05 AM' | M10 | PASS |
| '09:30 AM' | M10 | PASS |
| '12:00 PM' | M10 | PASS |
| '11:59 PM' | M10 | PASS |

Dead-state rejections (final state M14):

| Input | Final state | Result |
| --- | --- | --- |
| '24:00' | M14 | PASS |
| '25:30' | M14 | PASS |
| '23:60' | M14 | PASS |
| '12:75' | M14 | PASS |
| '0930' | M14 | PASS |
| '09:30AM' | M14 | PASS |
| '09:30  AM' | M14 | PASS |
| '18:30 PM' | M14 | PASS |
| '00:30 AM' | M14 | PASS |

Incomplete inputs (halt in non-accepting, non-dead state):

| Input | Halt state | Result |
| --- | --- | --- |
| '09:3' | M9 | PASS |
| '09:30 A' | M13 | PASS |
| '12:' | M7 | PASS |

Trace structure and dead-state optimization:

| ID | Check | Observed | Result |
| --- | --- | --- | --- |
| TC-M01 | Trace starts at start state | M0 | PASS |
| TC-M02 | Consecutive trace steps chain (to_state equals next from_state) | chained | PASS |
| TC-M03 | Trace ends at reported final state ('12:49 AM') | M10 | PASS |
| TC-M04 | Accepted trace length equals input length ('12:49 AM') | 8 | PASS |
| TC-M05 | Early break: '24:00' trace stops at the step entering M14 | length 2, last to_state M14 | PASS |

### 4.4 Suite 4 - Trace Builder and Formatter

Purpose: Verify the human-readable trace rendering used by the GUI Trace tab: correct columns, one row per step, correct display of the space symbol, and correct verdict wording for all three outcome classes.

What each check does:
- TC-T01 to TC-T03 verify table structure: the four column headers, one row per trace step, and the space symbol rendered as a visible character at the correct step.
- TC-T04 to TC-T06 verify the summary text for the accepted, dead-state, and incomplete verdicts.
- TC-T07 verifies the early-break transition appears exactly once in the rendered trace.

| ID | Check | Observed | Result |
| --- | --- | --- | --- |
| TC-T01 | Table columns | Step, Read Symbol, Current State, Next State | PASS |
| TC-T02 | Table row count equals trace steps ('12:00 PM') | 8 | PASS |
| TC-T03 | Space symbol displayed at step index 5 of '12:00 PM' | "' '" | PASS |
| TC-T04 | Accepted summary text | "accepting state" present | PASS |
| TC-T05 | Dead summary text ('24:00') | "dead state" present | PASS |
| TC-T06 | Incomplete summary text ('09:3') | "incomplete" present | PASS |
| TC-T07 | Dead transition recorded exactly once (early break) | 1 | PASS |

### 4.5 Suite 5 - Behavior Matrix (18 curated samples)

Purpose: The primary evidence that the two-layer policy behaves as specified. For each curated raw input, the observed Layer 1 verdict, Layer 2 verdict, and detected format must equal the Language Analyst's expected values, including the F/T rows where the raw input formally fails but the system accepts after normalization.

What each check does:
- Rows 1-6 (T/T): strict valid strings must pass both layers with the correct detected format.
- Rows 7-9 (F/T): casual valid strings (lowercase meridiem, one-digit hour) must fail Layer 1 but pass Layer 2, proving the normalization bridge works.
- Rows 10-18 (F/F): invalid strings must fail both layers, proving normalization never rescues a genuinely bad input.
- The GUI sample-button check verifies that all six buttons wired to the interface produce valid reports.

| Input | Expected (L1/L2) | Actual (L1/L2) | Detected format | Result |
| --- | --- | --- | --- | --- |
| '00:00' | T/T | T/T | 24-hour | PASS |
| '12:00' | T/T | T/T | 24-hour | PASS |
| '12:49' | T/T | T/T | 24-hour | PASS |
| '23:59' | T/T | T/T | 24-hour | PASS |
| '12:49 AM' | T/T | T/T | 12-hour | PASS |
| '12:00 PM' | T/T | T/T | 12-hour | PASS |
| '9:30 am' | F/T | F/T | 12-hour | PASS |
| '09:30 pm' | F/T | F/T | 12-hour | PASS |
| '1:05 PM' | F/T | F/T | 12-hour | PASS |
| '24:00' | F/F | F/F | - | PASS |
| '12:60' | F/F | F/F | - | PASS |
| '13:00 PM' | F/F | F/F | - | PASS |
| '00:30 AM' | F/F | F/F | - | PASS |
| '09:30AM' | F/F | F/F | - | PASS |
| '09:30  AM' | F/F | F/F | - | PASS |
| '09-30' | F/F | F/F | - | PASS |
| '09:30 XM' | F/F | F/F | - | PASS |
| 'ab:cd' | F/F | F/F | - | PASS |

All six GUI sample buttons ('12:49 AM', '23:59', '9:30 am', '09:30AM', '24:00', '13:00 PM') produced valid reports: PASS.

### 4.6 Suite 6 - Diagnostics and Rejection Layers

Purpose: Verify the diagnostics engine that explains rejections to the user: correct rejection-layer classification, correct failure index and symbol, correct expected-symbol hints at the failing state, and correct detected format for accepted inputs.

What each check does:
- TC-D01 to TC-D02 verify an Alphabet-Check rejection and its exact index/symbol.
- TC-D03 verifies the two-layer divergence case: raw '09:30 am' fails but the system accepts.
- TC-D04 to TC-D07 verify dead-state rejections with index/symbol and the expected-symbol hint (for example {0,1,2,3} after a leading 2, and a single space at M11).
- TC-D08 to TC-D09 verify the Incomplete-Input classification and its expected digits.
- TC-D10 to TC-D11 verify format detection (24-hour vs 12-hour) on accepted inputs.

| ID | Check | Observed | Result |
| --- | --- | --- | --- |
| TC-D01 | '09-30' rejection layer | Alphabet Check | PASS |
| TC-D02 | '09-30' failure index / symbol | 2 / '-' | PASS |
| TC-D03 | '09:30 am' raw fails but system accepts | (False, True) | PASS |
| TC-D04 | '24:00' rejection layer | Automaton (Dead State) | PASS |
| TC-D05 | '24:00' failure index / symbol | 1 / '4' | PASS |
| TC-D06 | '24:00' expected symbols at hour-2x state | {0, 1, 2, 3} | PASS |
| TC-D07 | '09:30AM' expected symbol at M11 | {' '} (single space) | PASS |
| TC-D08 | '09:3' rejection layer | Incomplete Input | PASS |
| TC-D09 | '09:3' expected symbols | {0-9} | PASS |
| TC-D10 | '23:59' detected format | 24-hour | PASS |
| TC-D11 | '09:30 AM' detected format | 12-hour | PASS |

### 4.7 Suite 7 - Two-Layer Smoke Test

Purpose: Integration check that Layer 1 and Layer 2 are wired together correctly: for each raw input it shows the raw verdict, the normalized string, and the normalized verdict, proving casual inputs flip from FAIL to PASS while genuinely invalid inputs fail both layers.

What each check does: each row runs one raw input through both layers and asserts the observed pair of verdicts and the normalized string, covering a clean 24-hour string, two casual 12-hour strings, a clean 12-hour-pending string, a structural rejection, and a total garbage string.

| Raw input | Layer 1 (raw) | Normalized | Layer 1 (normalized) | Result |
| --- | --- | --- | --- | --- |
| '23:45' | PASS | '23:45' | PASS | PASS |
| '9:30 am' | FAIL [(5,'a'),(6,'m')] | '09:30 AM' | PASS | PASS |
| '09:30 pm' | FAIL [(6,'p'),(7,'m')] | '09:30 PM' | PASS | PASS |
| '12:00' | PASS | '12:00' | PASS | PASS |
| '09:30AM' | PASS | '09:30AM' | PASS | PASS |
| 'ab:cd' | FAIL [(0,'a'),(1,'b'),(3,'c'),(4,'d')] | 'ab:cd' | FAIL | PASS |

### 4.8 Suite 8 - Engine Trace Smoke Test

Purpose: Integration check of the engine's trace output on representative paths: it asserts the key transitions taken on accepted 24-hour and 12-hour paths and on the three classic dead-state traps (missing space, hour 2x out of range, minute tens out of range), so the exact killing transition of each invalid input is verified.

What each check does: each row runs one input and asserts the acceptance flag, the final state, and the specific transition that decides the verdict.

| Input | Accepted | Final state | Key transition | Result |
| --- | --- | --- | --- | --- |
| '23:45' | True | M10 | M6 -4-> M8 -5-> M10 | PASS |
| '09:30 AM' | True | M10 | M11 -space-> M12 -A-> M13 -M-> M10 | PASS |
| '12:00' | True | M11 | M7 -0-> M9 -0-> M11 | PASS |
| '09:30AM' | False | M14 | M11 -A-> M14 (missing space) | PASS |
| '25:00' | False | M14 | M3 -5-> M14 (hour 2x limited to 20-23) | PASS |
| '12:60' | False | M14 | M7 -6-> M14 (minute tens limited to 0-5) | PASS |

### 4.9 Suite 9 - Full Pipeline Smoke Test

Purpose: Prove there is no integration drift: all 18 behavior-matrix rows are re-executed end-to-end through the complete diagnostics pipeline (alphabet check, normalization, DFA simulation, diagnostics, report), and every verdict must equal the values obtained from the individually tested modules in Suite 5.

All 18 behavior-matrix rows re-executed end-to-end through the diagnostics pipeline: ALL PASSED (values identical to Suite 5).

## 5. Boundary Value Coverage

| Boundary | Test(s) | Observed | Result |
| --- | --- | --- | --- |
| 00 | '00:00' accepted (M10); '00:30 AM' dead | accepted / M14 | PASS |
| 12 | '12:00' accepted (M11); '12:00 AM/PM' accepted (M10); '12:60', '12:75' dead | as expected | PASS |
| 23 | '23:59' accepted (M10); '23:60' dead | as expected | PASS |
| 24 | '24:00', '24:00'-class inputs dead at second hour digit | M14 | PASS |
| 59 | '23:59', '11:59 PM' accepted | M10 | PASS |
| 60 | '12:60', '23:60' dead at minute tens | M14 | PASS |

## 6. Defect Log

| ID | Item | Finding | Resolution |
| --- | --- | --- | --- |
| DEF-01 | Test oracle error in first revision of tests.test_alphabet_check | The original expected value for '09:30 am' listed invalid indices (5, 6), omitting the space at index 5. Manual index counting confirmed the system output (6, 7) was correct. | Test corrected to [(6, 'a'), (7, 'm')]; suite re-run to ALL PASSED. No system defect. |

No system defects were found. All 151 executed checks and cases pass.

## 7. Conclusion

The test campaign confirms that the implemented simulator behaves exactly as specified by the Formal Language Analysis, the Regular Expression and NFA design, the NFA-to-DFA conversion, and the revised DFA Minimization report. The two-layer policy (strict formal layer plus lexical normalization) works as designed, rejection layers are correctly classified, boundary values behave per the language definition, and the minimized DFA (M0-M14) with dead-state early break operates correctly. The system is verified and ready for demonstration and defense.