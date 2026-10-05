"""Unit tests for the trace builder and formatter."""

from core.automaton import DEAD_STATE, simulate
from core.trace import format_trace_table, get_trace_summary
from tests.util import check, check_true, finish


def main():
    sim = simulate("12:00 PM")
    table = format_trace_table(sim["trace"])
    check("table columns", list(table[0].keys()),
          ["Step", "Read Symbol", "Current State", "Next State"])
    check("table rows equal trace steps", len(table), len(sim["trace"]))
    check("space symbol displayed", table[5]["Read Symbol"], "' '")

    check_true("summary accepted text",
               "accepting state" in get_trace_summary(sim["final_state"], True))
    dead_sim = simulate("24:00")
    check_true("summary dead text",
               "dead state" in get_trace_summary(dead_sim["final_state"], False))
    inc_sim = simulate("09:3")
    check_true("summary incomplete text",
               "incomplete" in get_trace_summary(inc_sim["final_state"], False))

    dead_steps = [s for s in dead_sim["trace"] if s["to_state"] == DEAD_STATE]
    check("single recorded dead entry", len(dead_steps), 1)

    finish("test_trace")


if __name__ == "__main__":
    main()