# ---------------------------------------------------------------------------
# USER-INPUT LAYER LANGUAGE (L_USER)
# ---------------------------------------------------------------------------
# L_TIME describes the strict strings the automaton reads.
# L_USER describes the raw strings the SYSTEM accepts: after the normalizer
# (N1 meridiem case-fold, N2 hour padding) repairs them, they land in L_TIME.

USER_ALPHABET = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ":", " ",
    "A", "a", "M", "m", "P", "p",
]


def _two_digit(values):
    return [f"{v:02d}" for v in values]


# Strict (formal layer) component sets. If this file already defines them
# under other names, reuse those and delete these aliases.
STRICT_H24 = _two_digit(range(0, 24))
STRICT_H12 = _two_digit(range(1, 13))
STRICT_MIN = _two_digit(range(0, 60))
STRICT_MER = ["AM", "PM"]

# User-layer component sets.
# One- or two-digit hours that become valid 24-hour values after N2.
H24_USER = [str(d) for d in range(0, 10)] + STRICT_H24
# One- or two-digit hours that become valid 12-hour values after N2.
# The lone "0" is excluded: padding it yields "00", not a 12-hour hour.
H12_USER = [str(d) for d in range(1, 10)] + STRICT_H12
# Meridiem indicators in any letter case (N1 folds them to AM / PM).
MER_USER = [a + m for a in ("A", "a") for m in ("M", "m")] + \
           [p + m for p in ("P", "p") for m in ("M", "m")]
MIN_USER = STRICT_MIN


def user_alphabet_check(s):
    """Alphabet check against the 18-symbol user-input alphabet."""
    invalid = [(i, ch) for i, ch in enumerate(s) if ch not in USER_ALPHABET]
    return (len(invalid) == 0, invalid)


def in_L_TIME_strict(s):
    """Membership in the strict formal language L_TIME = L_24 ∪ L_12."""
    parts = s.split(":")
    if len(parts) != 2:
        return False
    hour, rest = parts
    if hour in STRICT_H24 and rest in STRICT_MIN:
        return True
    if rest.count(" ") == 1:
        minute, mer = rest.split(" ")
        if hour in STRICT_H12 and minute in STRICT_MIN and mer in STRICT_MER:
            return True
    return False


def in_L_USER24(s):
    parts = s.split(":")
    if len(parts) != 2:
        return False
    hour, minute = parts
    return hour in H24_USER and minute in MIN_USER


def in_L_USER12(s):
    parts = s.split(":")
    if len(parts) != 2:
        return False
    hour, rest = parts
    if rest.count(" ") != 1:
        return False
    minute, mer = rest.split(" ")
    return hour in H12_USER and minute in MIN_USER and mer in MER_USER


def in_L_USER(s):
    """Membership in the user-input layer language L_USER."""
    return in_L_USER24(s) or in_L_USER12(s)


def layer_bridge(raw, normalize_fn):
    """Return (in_user, normalized, normalized_in_time).

    Demonstrates the two defining properties of the two-layer design:
      1. L_TIME ⊆ L_USER  (strict strings are already valid user inputs)
      2. w ∈ L_USER ⇒ N(w) ∈ L_TIME  (normalization maps onto the strict layer)
    """
    normalized = normalize_fn(raw)
    return in_L_USER(raw), normalized, in_L_TIME_strict(normalized)