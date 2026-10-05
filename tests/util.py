"""Shared helpers for the project test scripts."""

FAILURES = []


def check(name, actual, expected):
    ok = actual == expected
    if not ok:
        FAILURES.append(name)
    print(f"{'OK  ' if ok else 'FAIL'} {name} | actual={actual!r} expected={expected!r}")
    return ok


def check_true(name, condition, detail=""):
    ok = bool(condition)
    if not ok:
        FAILURES.append(name)
    suffix = f" | {detail}" if detail != "" else ""
    print(f"{'OK  ' if ok else 'FAIL'} {name}{suffix}")
    return ok


def finish(suite):
    print("-" * 70)
    if FAILURES:
        print(f"{suite}: {len(FAILURES)} FAILURE(S)")
    else:
        print(f"{suite}: ALL PASSED")