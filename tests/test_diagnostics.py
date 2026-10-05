"""Unit tests for rejection-layer classification and failure diagnostics."""

from core.diagnostics import build_report
from tests.util import check, finish


def main():
    r = build_report("09-30")
    check("layer for 09-30", r["rejection_layer"], "Alphabet Check")
    check("failure index for 09-30", r["failure"]["index"], 2)
    check("failure char for 09-30", r["failure"]["char"], "-")

    r = build_report("09:30 am")
    check("raw fail but system accept", (r["formal_accepted"], r["system_accepted"]), (False, True))

    r = build_report("24:00")
    check("layer for 24:00", r["rejection_layer"], "Automaton (Dead State)")
    check("failure index for 24:00", r["failure"]["index"], 1)
    check("failure char for 24:00", r["failure"]["char"], "4")
    check("expected symbols at hour-2x", set(r["failure"]["expected"]), {"0", "1", "2", "3"})

    r = build_report("09:30AM")
    check("missing space expected symbol", set(r["failure"]["expected"]), {" "})

    r = build_report("09:3")
    check("layer for 09:3", r["rejection_layer"], "Incomplete Input")
    check("incomplete expected symbols", set(r["failure"]["expected"]), set("0123456789"))

    check("format 23:59", build_report("23:59")["detected_format"], "24-hour")
    check("format 09:30 AM", build_report("09:30 AM")["detected_format"], "12-hour")

    finish("test_diagnostics")


if __name__ == "__main__":
    main()