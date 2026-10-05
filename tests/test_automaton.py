"""Unit tests for the minimized DFA engine."""

from core.automaton import ACCEPTING_STATES, DEAD_STATE, START_STATE, simulate
from tests.util import check, check_true, finish

ACCEPTED = ["00:00", "12:00", "12:49", "13:00", "18:30", "23:59",
            "01:05 AM", "09:30 AM", "12:00 PM", "11:59 PM"]
DEAD_INPUTS = ["24:00", "25:30", "23:60", "12:75", "0930",
               "09:30AM", "09:30  AM", "18:30 PM", "00:30 AM"]
INCOMPLETE = ["09:3", "09:30 A", "12:"]


def main():
    for text in ACCEPTED:
        r = simulate(text)
        check_true(f"accept {text!r}", r["accepted"] and r["final_state"] in ACCEPTING_STATES,
                   f"final={r['final_state']}")

    for text in DEAD_INPUTS:
        r = simulate(text)
        check_true(f"dead-reject {text!r}", (not r["accepted"]) and r["final_state"] == DEAD_STATE,
                   f"final={r['final_state']}")

    for text in INCOMPLETE:
        r = simulate(text)
        check_true(f"incomplete {text!r}", (not r["accepted"]) and r["final_state"] != DEAD_STATE,
                   f"final={r['final_state']}")

    r = simulate("12:49 AM")
    t = r["trace"]
    check_true("trace starts at start state", t[0]["from_state"] == START_STATE)
    check_true("trace steps chain",
               all(t[i]["to_state"] == t[i + 1]["from_state"] for i in range(len(t) - 1)))
    check("trace ends at final state", t[-1]["to_state"], r["final_state"])
    check("accepted trace length equals input length", len(t), len("12:49 AM"))

    r = simulate("24:00")
    check("early break length", len(r["trace"]), 2)
    check("early break enters dead", r["trace"][-1]["to_state"], DEAD_STATE)

    finish("test_automaton")


if __name__ == "__main__":
    main()