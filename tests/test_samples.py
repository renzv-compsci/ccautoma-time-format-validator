"""Behavior-matrix tests over the curated sample set."""

from core.diagnostics import build_report
from core.samples import SAMPLES, SAMPLE_BUTTONS
from tests.util import check_true, finish


def main():
    for s in SAMPLES:
        r = build_report(s["input"])
        check_true(
            f"matrix {s['input']!r}",
            r["formal_accepted"] == s["formal"] and r["system_accepted"] == s["system"],
            f"formal={r['formal_accepted']} system={r['system_accepted']}",
        )
        if s["system"]:
            expected = "12-hour" if " " in r["normalized"] else "24-hour"
            check_true(f"format {s['input']!r}", r["detected_format"] == expected,
                       r["detected_format"])

    for b in SAMPLE_BUTTONS:
        check_true(f"button {b!r} runs", isinstance(build_report(b), dict))

    finish("test_samples")


if __name__ == "__main__":
    main()