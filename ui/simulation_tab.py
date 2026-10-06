"""Simulation tab: steps the epsilon-NFA, DFA, and minimized DFA side by side.

The diagrams are the published diagrams/*.dot files with the live state of each
machine overlaid, so the animation runs on exactly the artifacts in the repo.
"""

import html
import pathlib
import re
import time

import pandas as pd
import streamlit as st

from core import simulation
from core.normalizer import normalize

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT / "diagrams"

MODE_NORMALIZED = "Normalized (Layer 2)"
MODE_RAW = "Raw (Layer 1, strict)"

# Highlight palette (dark text stays readable on every fill).
CURRENT_FILL = "#FFD54F"   # amber: active state(s) right now
VISITED_FILL = "#BBDEFB"   # light blue: visited earlier
ACCEPT_FILL = "#81C784"    # green: accepted at end of input
REJECT_FILL = "#E57373"    # red: rejected / dead
DIED_FILL = "#F8BBD0"      # pink: NFA branch that just died
CURRENT_EDGE = "#E53935"   # red: transition taken on this step
PATH_EDGE = "#1E88E5"      # blue: transitions taken on earlier steps

EDGE_RE = re.compile(r"^(\s*)(\w+)\s*->\s*(\w+)\s*(?:\[(.*)\])?\s*;\s*$")


def _load_dot(name):
    with open(DIAGRAM_DIR / name, "r", encoding="utf-8") as f:
        return f.read()


def _show(char):
    return "␣" if char == " " else char


def _set(states):
    return "{" + ", ".join(states) + "}" if states else "∅"


def _highlight_dot(source, node_fills, current_edges, path_edges, extra_edges=()):
    """Overlays colors on an existing .dot diagram.

    Edges are matched by (from, to); every state pair appears once per diagram.
    Node attributes are re-declared at the end, which Graphviz merges.
    """
    out = []
    for line in source.rstrip().rstrip("}").splitlines():
        match = EDGE_RE.match(line)
        if match:
            indent, u, v, attrs = match.groups()
            extra = None
            if (u, v) in current_edges:
                extra = f'color="{CURRENT_EDGE}", fontcolor="{CURRENT_EDGE}", penwidth=3.5'
            elif (u, v) in path_edges:
                extra = f'color="{PATH_EDGE}", fontcolor="{PATH_EDGE}", penwidth=2.5'
            if extra:
                attrs = f"{attrs}, {extra}" if attrs else extra
                line = f"{indent}{u} -> {v} [{attrs}];"
        out.append(line)

    # Transitions into the dead state are not drawn in the static diagrams.
    for u, v, label in extra_edges:
        out.append(
            f'    {u} -> {v} [label="{label}", style=dashed, '
            f'color="{CURRENT_EDGE}", fontcolor="{CURRENT_EDGE}", penwidth=3];'
        )
    for state, fill in node_fills.items():
        out.append(f'    {state} [style=filled, fillcolor="{fill}", penwidth=2];')
    out.append("}")
    return "\n".join(out)


def _dead_label(char):
    return "space" if char == " " else char.replace("\\", "\\\\").replace('"', '\\"')


def _nfa_dot(run, k, finished):
    states = simulation.nfa_states_at(run, k)
    fills = {}
    path, current = set(), set()

    if k == 0:
        current.update(run["initial"]["eps_edges"])
    else:
        path.update(run["initial"]["eps_edges"])
    for step in run["steps"][: min(k, len(run["steps"]))]:
        for state in step["before"]:
            fills[state] = VISITED_FILL
        target = current if step["step"] == k else path
        target.update(step["edges"])
        target.update(step["eps_edges"])
    path -= current

    # After a halt, keep showing the branches that died on the last symbol read.
    step = simulation.step_at(run, min(k, len(run["steps"])))
    if step and (step["step"] == k or simulation.is_halted(run, k)):
        for state in step["died"]:
            fills[state] = DIED_FILL
    for state in states:
        if finished:
            fills[state] = ACCEPT_FILL if state in simulation.NFA_SPEC["accepting"] else REJECT_FILL
        else:
            fills[state] = CURRENT_FILL
    return _highlight_dot(_load_dot("nfa.dot"), fills, current, path)


def _dfa_dot(run, spec, dot_name, k, finished):
    state = simulation.dfa_state_at(run, k)
    dead = spec["dead_state"]
    fills, path, current, extra = {}, set(), set(), []

    for step in run["steps"][: min(k, len(run["steps"]))]:
        fills[step["from_state"]] = VISITED_FILL
        edge = (step["from_state"], step["to_state"])
        if step["to_state"] == dead:
            extra.append((*edge, _dead_label(step["char"])))
        elif step["step"] == k:
            current.add(edge)
        else:
            path.add(edge)

    if state == dead:
        fills[state] = REJECT_FILL
    elif finished:
        fills[state] = ACCEPT_FILL if state in spec["accepting"] else REJECT_FILL
    else:
        fills[state] = CURRENT_FILL
    return _highlight_dot(_load_dot(dot_name), fills, current, path - current, extra)


def _tape_html(text, k, halted_at=None):
    cells = []
    halted = halted_at is not None and k > halted_at
    for i, char in enumerate(text):
        if halted and i >= halted_at:
            bg, border = "#FFFFFF", "#E0E0E0"  # never read: machines already halted
        elif halted and i == halted_at - 1:
            bg, border = REJECT_FILL, CURRENT_EDGE  # the symbol that killed the run
        elif i < k - 1:
            bg, border = "#E0E0E0", "#9E9E9E"
        elif i == k - 1:
            bg, border = CURRENT_FILL, CURRENT_EDGE
        else:
            bg, border = "#FFFFFF", "#9E9E9E"
        cells.append(
            f'<div style="display:inline-flex;flex-direction:column;align-items:center;margin:2px;">'
            f'<div style="width:2.4rem;height:2.4rem;display:flex;align-items:center;justify-content:center;'
            f"font:600 1.2rem monospace;color:#212121;background:{bg};border:2px solid {border};"
            f'border-radius:6px;">{html.escape(_show(char))}</div>'
            f'<div style="font-size:0.7rem;opacity:0.7;">{i + 1}</div></div>'
        )
    if k == 0:
        head = "▲ before first symbol"
    elif halted:
        head = (
            f"▲ halted at symbol {halted_at}: '{html.escape(_show(text[halted_at - 1]))}'; "
            "the remaining symbols are never read"
        )
    else:
        head = f"▲ just read symbol {k} of {len(text)}: '{html.escape(_show(text[k - 1]))}'"
    return (
        f'<div style="display:flex;flex-wrap:wrap;align-items:flex-start;">{"".join(cells)}</div>'
        f'<div style="font-size:0.85rem;opacity:0.8;margin-bottom:0.5rem;">{head}</div>'
    )


def _dfa_subset(state, nfa_states):
    """DFA state label plus the NFA subset it stands for at this point."""
    if state == simulation.DFA_SPEC["dead_state"]:
        return "∅ (dead)"
    return f"{state} ≡ {_set(nfa_states)}"


def _min_merge(state):
    merged = simulation.MIN_DFA_SPEC["state_mapping_from_17_state_dfa"].get(state, [])
    if state == simulation.MIN_DFA_SPEC["dead_state"]:
        return f"{state} (dead)"
    if len(merged) > 1:
        return f"{state} (merged {' + '.join(merged)})"
    return state


def _nfa_explanation(run, k):
    if k == 0:
        return (
            "Before reading anything, q0 takes both ε-moves for free, so the NFA "
            "starts in **{q0, q1, q8}**: the 24-hour branch (q1) and the 12-hour "
            "branch (q8) are both alive."
        )
    if simulation.is_halted(run, k):
        return f"Every branch died at symbol {run['halted_at']}; the NFA stopped reading (∅)."
    step = simulation.step_at(run, k)
    moves = ", ".join(f"{u}→{v}" for u, v in step["edges"]) or "none"
    text = f"Moves on '{_show(step['char'])}': {moves}."
    if step["died"]:
        text += f" Branch dead end at {', '.join(step['died'])} (no transition on '{_show(step['char'])}')."
    alive = simulation.branch_status(step["after"])
    live = [name for name, ok in alive.items() if ok]
    text += f" Still alive: **{', '.join(live) if live else 'nothing'}**."
    return text


def _dfa_explanation(run, spec, k, label):
    if k == 0:
        return f"Starts in the single state **{run['start']}**."
    if simulation.is_halted(run, k):
        return f"Entered the dead state at symbol {run['halted_at']} and stopped reading."
    step = simulation.step_at(run, k)
    to_state = step["to_state"]
    if to_state == spec["dead_state"]:
        return (
            f"δ({step['from_state']}, '{_show(step['char'])}') is undefined → "
            f"**{to_state}** ({label} trap state)."
        )
    return f"δ({step['from_state']}, '{_show(step['char'])}') = **{to_state}**: exactly one move."


def _comparison_table(run, k):
    nfa, dfa, mdfa = run["nfa"], run["dfa"], run["min_dfa"]
    rows = [{
        "Step": 0,
        "Read": "(start)",
        "ε-NFA active set": _set(nfa["initial"]["states"]),
        "DFA state (≡ NFA subset)": _dfa_subset(dfa["start"], nfa["initial"]["states"]),
        "Minimized DFA": _min_merge(mdfa["start"]),
    }]
    for i, char in enumerate(run["text"][:k], start=1):
        nfa_states = simulation.nfa_states_at(nfa, i)
        rows.append({
            "Step": i,
            "Read": _show(char),
            "ε-NFA active set": "(halted)" if simulation.is_halted(nfa, i) else _set(nfa_states),
            "DFA state (≡ NFA subset)": "(halted)" if simulation.is_halted(dfa, i)
            else _dfa_subset(simulation.dfa_state_at(dfa, i), nfa_states),
            "Minimized DFA": "(halted)" if simulation.is_halted(mdfa, i)
            else _min_merge(simulation.dfa_state_at(mdfa, i)),
        })
    df = pd.DataFrame(rows)

    def _row_style(row):
        style = f"background-color: {CURRENT_FILL}; color: #212121" if row["Step"] == k else ""
        return [style] * len(row)

    return df.style.apply(_row_style, axis=1)


def _verdict(run, finished):
    if not finished:
        return
    nfa, dfa, mdfa = run["nfa"], run["dfa"], run["min_dfa"]
    verdicts = {nfa["accepted"], dfa["accepted"], mdfa["accepted"]}
    if verdicts == {True}:
        st.success(
            f"ACCEPT: all three models agree. ε-NFA ends in {_set(nfa['final'])} "
            f"(contains an accepting state), DFA ends in {dfa['final']}, "
            f"Minimized DFA ends in {mdfa['final']}."
        )
    elif verdicts == {False}:
        st.error(
            f"REJECT: all three models agree. ε-NFA ends in {_set(nfa['final'])}, "
            f"DFA ends in {dfa['final']}, Minimized DFA ends in {mdfa['final']}; "
            "none of them is accepting."
        )
    else:
        st.warning("The models disagree. This should never happen for equivalent automata.")


def _draw_frame(run, k):
    text = run["text"]
    n = len(text)
    # Done once every symbol is read, or once all three models have halted.
    finished = k == n or all(
        run[m]["halted_at"] is not None and k >= run[m]["halted_at"]
        for m in ("nfa", "dfa", "min_dfa")
    )
    nfa, dfa, mdfa = run["nfa"], run["dfa"], run["min_dfa"]

    st.markdown(_tape_html(text, k, dfa["halted_at"]), unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    nfa_states = simulation.nfa_states_at(nfa, k)
    c1.metric("ε-NFA: set of states", _set(nfa_states))
    c2.metric("DFA: one state", simulation.dfa_state_at(dfa, k))
    c3.metric("Minimized DFA: one state", simulation.dfa_state_at(mdfa, k))

    _verdict(run, finished)

    st.markdown(f"##### ε-NFA (19 states): {_set(nfa_states)}")
    st.caption(_nfa_explanation(nfa, k))
    st.graphviz_chart(_nfa_dot(nfa, k, finished), use_container_width=True)

    dfa_state = simulation.dfa_state_at(dfa, k)
    st.markdown(f"##### DFA (17 states): {_dfa_subset(dfa_state, nfa_states)}")
    st.caption(
        _dfa_explanation(dfa, simulation.DFA_SPEC, k, "∅")
        + " Each DFA state is the *set* of NFA states shown above (subset construction)."
    )
    st.graphviz_chart(
        _dfa_dot(dfa, simulation.DFA_SPEC, "dfa.dot", k, finished), use_container_width=True
    )

    mdfa_state = simulation.dfa_state_at(mdfa, k)
    st.markdown(f"##### Minimized DFA (15 states): {_min_merge(mdfa_state)}")
    st.caption(
        _dfa_explanation(mdfa, simulation.MIN_DFA_SPEC, k, "M14")
        + " Same path as the DFA, but S10/S15 and S13/S14 are merged."
    )
    st.graphviz_chart(
        _dfa_dot(mdfa, simulation.MIN_DFA_SPEC, "minimized_dfa.dot", k, finished),
        use_container_width=True,
    )

    st.markdown("##### Step-by-step comparison (symbols read so far)")
    st.dataframe(_comparison_table(run, k), hide_index=True, use_container_width=True)


# "sim_pos" is the source of truth; "sim_slider" is only the widget mirroring it,
# because a widget's own key cannot be written once it is on the page.
def _set_step(value):
    st.session_state["sim_pos"] = value


def _slider_moved():
    st.session_state["sim_pos"] = st.session_state["sim_slider"]


def _start_play(n):
    if st.session_state.get("sim_pos", 0) >= n:
        st.session_state["sim_pos"] = 0
    st.session_state["sim_play"] = True


def render():
    st.subheader("Automata Simulation: ε-NFA vs DFA vs Minimized DFA")
    st.caption(
        "Type a time in the input box above (or click a sample), then step through it. "
        "The NFA tracks a set of states and runs both branches in parallel; the DFA and "
        "Minimized DFA always sit in exactly one state."
    )

    raw = st.session_state.get("raw_input", "")
    mode = st.radio(
        "Input fed to the automata", [MODE_NORMALIZED, MODE_RAW],
        key="sim_mode", horizontal=True,
    )
    text = normalize(raw) if mode == MODE_NORMALIZED else raw
    if not text:
        st.info("Enter a time string above to start the simulation.")
        return
    if mode == MODE_NORMALIZED and text != raw:
        st.caption(f"Layer 2 normalized `{raw}` → `{text}`")

    invalid = [c for c in text if c not in {" "} | set(simulation.NFA_SPEC["alphabet"])]
    if invalid:
        st.warning(
            f"'{invalid[0]}' is not in Σ. The automata have no transition on it, so every "
            "NFA branch dies and both DFAs fall into the dead state."
        )

    run = simulation.run_all(text)
    n = len(text)

    # Reset the step when the input changes; apply progress saved by Play.
    if st.session_state.get("sim_text") != text:
        st.session_state["sim_text"] = text
        st.session_state["sim_pos"] = 0
        st.session_state["sim_play"] = False
    k = min(st.session_state.get("sim_pos", 0), n)
    st.session_state["sim_pos"] = k
    st.session_state["sim_slider"] = k

    b1, b2, b3, b4, b5, speed_col = st.columns([1, 1, 1, 1, 1, 3])
    b1.button("⏮ Reset", key="sim_reset", on_click=_set_step, args=(0,), use_container_width=True)
    b2.button("◀ Back", key="sim_back", on_click=_set_step, args=(max(k - 1, 0),),
              disabled=k == 0, use_container_width=True)
    b3.button("Step ▶", key="sim_next", on_click=_set_step, args=(min(k + 1, n),),
              disabled=k == n, use_container_width=True)
    b4.button("End ⏭", key="sim_end", on_click=_set_step, args=(n,), use_container_width=True)
    b5.button("▶ Play", key="sim_play_btn", type="primary", on_click=_start_play, args=(n,),
              use_container_width=True)
    delay = speed_col.select_slider(
        "Play speed (seconds per symbol)", options=[0.4, 0.7, 1.0, 1.5, 2.0], value=1.0,
        key="sim_speed",
    )
    st.slider("Symbols read", 0, n, key="sim_slider", on_change=_slider_moved)

    frame = st.empty()
    if st.session_state.get("sim_play"):
        st.session_state["sim_play"] = False
        for i in range(k, n + 1):
            st.session_state["sim_pos"] = i
            with frame.container():
                _draw_frame(run, i)
            if i < n:
                time.sleep(delay)
        st.rerun()
    else:
        with frame.container():
            _draw_frame(run, k)
