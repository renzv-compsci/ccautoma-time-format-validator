"""Side-by-side simulation of the epsilon-NFA, DFA, and minimized DFA.

All three machines are driven directly from data/*.json, the same specs the
Automata tab renders, so the simulation always matches the published artifacts.
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

# Branch membership of the epsilon-NFA states (see diagrams/nfa.dot callouts).
NFA_24H_STATES = {f"q{i}" for i in range(1, 8)}
NFA_12H_STATES = {f"q{i}" for i in range(8, 19)}


def load_spec(name: str) -> dict:
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


NFA_SPEC = load_spec("nfa.json")
DFA_SPEC = load_spec("dfa.json")
MIN_DFA_SPEC = load_spec("minimized_dfa.json")


def to_symbol(char: str) -> str:
    """Maps an input character to its alphabet key in the JSON specs."""
    return "SPACE" if char == " " else char


def state_sort_key(state: str):
    """Natural order so q2 sorts before q10."""
    match = re.search(r"\d+", state)
    return (re.sub(r"\d+", "", state), int(match.group()) if match else -1)


def sorted_states(states) -> list:
    return sorted(states, key=state_sort_key)


def epsilon_closure(spec: dict, states) -> tuple[set, list]:
    """Returns the epsilon-closure of `states` and the epsilon edges followed."""
    eps = spec.get("epsilon_transitions", {})
    closure = set(states)
    stack = list(states)
    edges = []
    while stack:
        u = stack.pop()
        for v in eps.get(u, []):
            edges.append((u, v))
            if v not in closure:
                closure.add(v)
                stack.append(v)
    return closure, edges


def run_nfa(text: str, spec: dict = NFA_SPEC) -> dict:
    """Tracks the full set of active NFA states symbol by symbol.

    Stops early once the active set is empty (every branch has died).
    """
    current, eps_edges = epsilon_closure(spec, {spec["start"]})
    initial = {"states": sorted_states(current), "eps_edges": eps_edges}
    steps = []

    for index, char in enumerate(text):
        symbol = to_symbol(char)
        moved = set()
        edges = []
        died = []
        for u in sorted_states(current):
            targets = spec["transitions"].get(u, {}).get(symbol, [])
            # States with only epsilon moves (q0) were split points, not branches.
            is_split_point = u in spec.get("epsilon_transitions", {}) and not spec["transitions"].get(u)
            if not targets and not is_split_point:
                died.append(u)
            for v in targets:
                edges.append((u, v))
                moved.add(v)
        after, step_eps = epsilon_closure(spec, moved)
        steps.append({
            "step": index + 1,
            "char": char,
            "before": sorted_states(current),
            "after": sorted_states(after),
            "edges": edges,
            "eps_edges": step_eps,
            "died": died,
        })
        current = after
        if not current:
            break

    consumed_all = len(steps) == len(text)
    return {
        "initial": initial,
        "steps": steps,
        "final": sorted_states(current),
        "accepted": consumed_all and bool(current & set(spec["accepting"])),
        "halted_at": None if consumed_all else len(steps),
    }


def run_dfa(text: str, spec: dict) -> dict:
    """Runs a DFA spec; missing transitions go to the spec's dead state.

    Mirrors core.automaton.simulate: reading stops on entering the dead state.
    """
    dead = spec["dead_state"]
    state = spec["start"]
    steps = []

    for index, char in enumerate(text):
        targets = spec["transitions"].get(state, {}).get(to_symbol(char))
        nxt = targets[0] if targets else dead
        steps.append({
            "step": index + 1,
            "char": char,
            "from_state": state,
            "to_state": nxt,
        })
        state = nxt
        if state == dead:
            break

    consumed_all = len(steps) == len(text)
    return {
        "start": spec["start"],
        "steps": steps,
        "final": state,
        "accepted": consumed_all and state in spec["accepting"],
        "halted_at": None if consumed_all else len(steps),
    }


def run_all(text: str) -> dict:
    """Runs all three models on the same input."""
    return {
        "text": text,
        "nfa": run_nfa(text),
        "dfa": run_dfa(text, DFA_SPEC),
        "min_dfa": run_dfa(text, MIN_DFA_SPEC),
    }


def nfa_states_at(run: dict, k: int) -> list:
    """Active NFA states after reading k symbols (frozen once halted)."""
    if k == 0 or not run["steps"]:
        return run["initial"]["states"]
    return run["steps"][min(k, len(run["steps"])) - 1]["after"]


def dfa_state_at(run: dict, k: int) -> str:
    """DFA state after reading k symbols (frozen once halted)."""
    if k == 0 or not run["steps"]:
        return run["start"]
    return run["steps"][min(k, len(run["steps"])) - 1]["to_state"]


def step_at(run: dict, k: int):
    """The step record that consumed symbol k (1-based), or None."""
    if 1 <= k <= len(run["steps"]):
        return run["steps"][k - 1]
    return None


def is_halted(run: dict, k: int) -> bool:
    """True when the model stopped reading before symbol k."""
    return run["halted_at"] is not None and k > run["halted_at"]


def branch_status(states) -> dict:
    """Which epsilon-NFA branches still have at least one active state."""
    active = set(states)
    return {
        "24-hour": bool(active & NFA_24H_STATES),
        "12-hour": bool(active & NFA_12H_STATES),
    }
