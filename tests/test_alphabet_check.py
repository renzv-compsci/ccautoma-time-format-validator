"""Unit tests for Layer 1: Alphabet Check."""

from core.alphabet_check import SIGMA_TIME, check_alphabet
from tests.util import check, check_true, finish


def main():
    check("alphabet size is 15", len(SIGMA_TIME), 15)
    for sym in sorted(SIGMA_TIME):
        check_true(f"symbol {sym!r} accepted alone", check_alphabet(sym)[0])

    for raw in ["00:00", "23:59", "12:49 AM", "09:30AM", "09:30  AM"]:
        ok, invalid = check_alphabet(raw)
        check(f"raw {raw!r} passes", (ok, invalid), (True, []))

    check("lowercase am flagged", check_alphabet("09:30 am"), (False, [(6, "a"), (7, "m")]))
    check("letters flagged", check_alphabet("ab:cd"), (False, [(0, "a"), (1, "b"), (3, "c"), (4, "d")]))
    check("dash flagged", check_alphabet("09-30"), (False, [(2, "-")]))
    check("X flagged", check_alphabet("09:30 XM"), (False, [(6, "X")]))

    check("empty input passes alphabet check", check_alphabet(""), (True, []))

    finish("test_alphabet_check")


if __name__ == "__main__":
    main()