# ---------------------------------------------------------------------------
# MATHEMATICAL REGULAR EXPRESSIONS (theoretical view, union written as +)
# The programming regex already in this file remains the implementation
# reference for R_TIME. R_USER is the mathematical view of the user layer.
# ---------------------------------------------------------------------------

MATHEMATICAL_REGEX = {
    "R24": "((0+1)D + 2(0+1+2+3)) : (0+1+2+3+4+5)D",
    "R12": "(0(1+2+3+4+5+6+7+8+9) + 1(0+1+2)) : (0+1+2+3+4+5)D ␣ (AM+PM)",
    "R_TIME": "R24 + R12",
    "R_USER24": "(D + (0+1)D + 2(0+1+2+3)) : (0+1+2+3+4+5)D",
    "R_USER12": "((1+2+3+4+5+6+7+8+9) + 0(1+2+3+4+5+6+7+8+9) + 1(0+1+2))"
                " : (0+1+2+3+4+5)D ␣ ((a+A)(m+M) + (p+P)(m+M))",
    "R_USER": "R_USER24 + R_USER12",
}

# Component-by-component translation between the mathematical view and the
# programming view. "N1/N2" marks components the normalizer repairs instead.
MATH_PROGRAMMING_LEGEND = [
    ("D", "any single digit", "[0-9]"),
    ("(0+1)D", "hours 00-19", "[01][0-9]"),
    ("2(0+1+2+3)", "hours 20-23", "2[0-3]"),
    ("(0+1+2+3+4+5)D", "minutes 00-59", "[0-5][0-9]"),
    ("0(1+2+...+9)", "hours 01-09", "0[1-9]"),
    ("1(0+1+2)", "hours 10-12", "1[0-2]"),
    (":", "literal colon", ":"),
    ("␣", "one literal space", " "),
    ("(AM+PM)", "uppercase meridiem", "(AM|PM)"),
    ("((a+A)(m+M) + (p+P)(m+M))", "any-case meridiem (user layer)", "handled by N1"),
    ("leading D / (1+...+9)", "one-digit hour (user layer)", "handled by N2"),
]


def mathematical_view():
    """Return the mathematical expressions in display order."""
    return ["R24", "R12", "R_TIME", "R_USER24", "R_USER12", "R_USER"]