"""Unit tests for Layer 2: Lexical Normalizer (rules N1 and N2 only)."""

from core.normalizer import normalize
from tests.util import check, finish


def main():
    check("N1 lowercase am", normalize("09:30 am"), "09:30 AM")
    check("N1 lowercase pm", normalize("09:30 pm"), "09:30 PM")
    check("N1 mixed case Am", normalize("09:30 Am"), "09:30 AM")
    check("N1 mixed case pM", normalize("12:00 pM"), "12:00 PM")

    check("N2 pads 9:30", normalize("9:30"), "09:30")
    check("N2 pads 1:05 PM", normalize("1:05 PM"), "01:05 PM")
    check("N1+N2 combined", normalize("9:30 am"), "09:30 AM")

    for raw in ["09:30AM", "09:30  AM", "24:00", "12:60", "10:15", "12:49 AM", "00:00"]:
        check(f"unchanged {raw!r}", normalize(raw), raw)

    finish("test_normalizer")


if __name__ == "__main__":
    main()