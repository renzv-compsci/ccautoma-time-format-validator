"""Unit tests for the side-by-side NFA / DFA / minimized DFA simulation."""

import random

from core import automaton, simulation
from core.samples import SAMPLES
from tests.util import check, check_true, finish

# Subset construction table from docs/DFA_SPECIFICATION.md section 3.
DFA_SUBSETS = {
    "S0": ["q0", "q1", "q8"], "S1": ["q2", "q9"], "S2": ["q2", "q10"],
    "S3": ["q3"], "S4": ["q4"], "S5": ["q4", "q11"], "S6": ["q5"],
    "S7": ["q5", "q12"], "S8": ["q6"], "S9": ["q6", "q13"], "S10": ["q7"],
    "S11": ["q7", "q14"], "S12": ["q15"], "S13": ["q16"], "S14": ["q17"],
    "S15": ["q18"], "dead": [],
}
SIGMA = "0123456789: AMP"


def _all_valid_times():
    times = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(60)]
    times += [f"{h:02d}:{m:02d} {s}" for h in range(1, 13) for m in range(60) for s in ("AM", "PM")]
    return times


def _verdicts(text):
    run = simulation.run_all(text)
    return (run["nfa"]["accepted"], run["dfa"]["accepted"],
            run["min_dfa"]["accepted"], automaton.simulate(text)["accepted"])


def main():
    valid = _all_valid_times()
    check("valid time count", len(valid), 2880)
    check_true("all 2,880 valid times accepted by every model",
               all(_verdicts(t) == (True,) * 4 for t in valid))

    for sample in SAMPLES:
        text = sample["input"]
        check(f"sample {text!r} agrees with Behavior Matrix",
              _verdicts(text), (sample["formal"],) * 4)

    rng = random.Random(2026)
    fuzz = ["".join(rng.choice(SIGMA) for _ in range(rng.randint(0, 9))) for _ in range(5000)]
    fuzz += [t[:i] + c + t[i + 1:] for t in rng.sample(valid, 300) for i in range(len(t)) for c in "09: AP"]
    check_true("NFA, DFA, minimized DFA, and engine agree on fuzz inputs",
               all(len(set(_verdicts(t))) == 1 for t in fuzz))

    mismatches = set()
    for text in valid + fuzz:
        run = simulation.run_all(text)
        for k in range(len(text) + 1):
            if simulation.is_halted(run["dfa"], k):
                break
            dfa_state = simulation.dfa_state_at(run["dfa"], k)
            nfa_states = simulation.nfa_states_at(run["nfa"], k)
            if DFA_SUBSETS[dfa_state] != nfa_states:
                mismatches.add((dfa_state, tuple(nfa_states)))
            min_state = simulation.dfa_state_at(run["min_dfa"], k)
            merged = simulation.MIN_DFA_SPEC["state_mapping_from_17_state_dfa"][min_state]
            if dfa_state not in merged:
                mismatches.add((dfa_state, min_state))
    check("DFA states match the documented NFA subsets and minimized merges", mismatches, set())

    nfa = simulation.run_nfa("12:00 PM")
    check("initial epsilon-closure", nfa["initial"]["states"], ["q0", "q1", "q8"])
    check("epsilon edges from q0", sorted(nfa["initial"]["eps_edges"]), [("q0", "q1"), ("q0", "q8")])
    check("q0 is a split point, not a dead branch", nfa["steps"][0]["died"], [])
    check("both branches alive after '12:00'",
          simulation.branch_status(simulation.nfa_states_at(nfa, 5)), {"24-hour": True, "12-hour": True})
    check("24-hour branch dies on the space", nfa["steps"][5]["died"], ["q7"])
    check("only 12-hour branch after '12:00 '",
          simulation.branch_status(simulation.nfa_states_at(nfa, 6)), {"24-hour": False, "12-hour": True})

    nfa = simulation.run_nfa("2")
    check("12-hour branch dies on leading 2", nfa["steps"][0]["died"], ["q8"])

    run = simulation.run_all("24:00")
    check("NFA halts when every branch dies", run["nfa"]["halted_at"], 2)
    check("NFA final set empty", run["nfa"]["final"], [])
    check("DFA halts in dead state", (run["dfa"]["halted_at"], run["dfa"]["final"]), (2, "dead"))
    check("minimized DFA halts in M14", (run["min_dfa"]["halted_at"], run["min_dfa"]["final"]), (2, "M14"))
    check_true("halted after step 2", simulation.is_halted(run["dfa"], 3)
               and not simulation.is_halted(run["dfa"], 2))
    check("state frozen after halt", simulation.dfa_state_at(run["min_dfa"], 5), "M14")

    run = simulation.run_all("09:3")
    check_true("incomplete input not accepted and not halted",
               not run["nfa"]["accepted"] and run["dfa"]["halted_at"] is None
               and run["min_dfa"]["final"] == "M9")

    run = simulation.run_all("")
    check("empty input stays at start", (run["dfa"]["final"], run["min_dfa"]["final"]), ("S0", "M0"))

    run = simulation.run_all("09-30")
    check("symbol outside sigma kills every branch", run["nfa"]["halted_at"], 3)

    finish("test_simulation")


if __name__ == "__main__":
    main()
