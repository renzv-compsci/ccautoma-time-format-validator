"""Trace tab: dynamic step-by-step simulation display and focused automaton view."""

import streamlit as st
import json
import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _load_json(name):
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_state_name(label):
    """Helper to clean state labels for exact matching (removes '-> ' and '* ')."""
    return label.replace("-> ", "").replace("* ", "").strip()


def _table(spec):
    """Helper to build the dataframe table."""
    has_eps = "epsilon_transitions" in spec
    rows = []
    for state in spec["states"]:
        label = state
        if state == spec.get("start"):
            label = "-> " + label
        if state in spec.get("accepting", []):
            label = "* " + label
        row = {"State": label}
        if has_eps:
            eps = spec["epsilon_transitions"].get(state)
            row["epsilon"] = ", ".join(eps) if eps else "empty"
        trans = spec["transitions"].get(state, {})
        for sym in spec["alphabet"]:
            disp = "SPACE" if sym == "SPACE" else sym
            targets = trans.get(sym)
            row[disp] = ", ".join(targets) if targets else "empty"
        rows.append(row)
    return pd.DataFrame(rows)


def _generate_linear_trace_dot(trace, is_accepted, final_state):
    """Generates the simple linear path diagram."""
    if not trace:
        return None

    lines = [
        "digraph ExecutionTrace {",
        "    rankdir=LR;",
        "    bgcolor=\"white\";",
        "    node [shape=circle, fontname=\"Helvetica\", style=filled, color=\"black\", fontcolor=\"black\"];",
        "    edge [fontname=\"Helvetica\", fontsize=12, penwidth=2.5, color=\"black\"];",
        "    start [shape=point, width=0.12, style=solid];"
    ]

    visited_states = set()
    lines.append(f'    start -> "{trace[0]["from_state"]}" [style=dashed, color="gray"];')
    visited_states.add(trace[0]["from_state"])

    for step in trace:
        u = step["from_state"]
        v = step["to_state"]
        char = step["char"]
        visited_states.add(u)
        visited_states.add(v)
        label = "space" if char == "' '" else char
        lines.append(f'    "{u}" -> "{v}" [label="{label}", color="red", penwidth="2.5"];')

    for state in visited_states:
        if state == final_state and is_accepted:
            lines.append(f'    "{state}" [shape=doublecircle, fillcolor="#90EE90"];') # Light Green
        elif state == final_state and not is_accepted:
            lines.append(f'    "{state}" [shape=circle, fillcolor="#FF6B6B"];') # Red
        else:
            lines.append(f'    "{state}" [shape=circle, fillcolor="#ADD8E6"];') # Light Blue

    lines.append("}")
    return "\n".join(lines)


def _generate_highlighted_minimized_dfa(trace, is_accepted, final_state):
    """
    Generates the FULL Minimized DFA diagram (M0-M14) with high-contrast colors.
    """
    spec = _load_json("minimized_dfa.json")
    lines = [
        "digraph MinimizedDFAExecution {",
        "    rankdir=LR;",
        "    bgcolor=\"white\";",
        "    node [shape=circle, fontname=\"Helvetica\", style=filled, color=\"black\", fontcolor=\"black\", penwidth=2];",
        "    edge [fontname=\"Helvetica\", fontsize=10, color=\"black\"];"
    ]

    visited_states = set()
    active_edges = set()

    for step in trace:
        visited_states.add(step["from_state"])
        visited_states.add(step["to_state"])
        
        trace_char = step["char"]
        json_symbol = "SPACE" if trace_char == "' '" else trace_char
        active_edges.add((step["from_state"], step["to_state"], json_symbol))

    # Add Nodes
    for state in spec["states"]:
        shape = "circle"
        fillcolor = "#E0E0E0" # Light gray (visible on white)
        style = "filled"
        
        if state in visited_states:
            fillcolor = "#ADD8E6" # Light Blue
            
        if state == final_state:
            if is_accepted:
                fillcolor = "#90EE90" # Light Green
                shape = "doublecircle"
            else:
                fillcolor = "#FF6B6B" # Red
                
        label = state
        if state == "M10": label = "M10 (S10+S15)"
        if state == "M13": label = "M13 (S13+S14)"
        if state == "M14": label = "M14 (Dead)"

        lines.append(f'    "{state}" [label="{label}", shape="{shape}", style="{style}", fillcolor="{fillcolor}"];')

    # Add Edges
    for u, transitions in spec["transitions"].items():
        for symbol, v_list in transitions.items():
            for v in v_list:
                is_active = (u, v, symbol) in active_edges
                
                # Active: Red, Thick
                # Inactive: Dark Gray (#555555), Thin, Dashed (Visible on white!)
                color = "#FF0000" if is_active else "#555555"
                penwidth = "3.0" if is_active else "1.0"
                style = "solid" if is_active else "dashed"
                
                label = "space" if symbol == "SPACE" else symbol
                lines.append(f'    "{u}" -> "{v}" [label="{label}", color="{color}", penwidth="{penwidth}", style="{style}"];')

    # Dead State Loop (M14)
    if "M14" in visited_states:
        lines.append(f'    "M14" -> "M14" [label="all", color="#FF0000", penwidth="3.0", style="solid"];')
    else:
        lines.append(f'    "M14" -> "M14" [label="all", color="#555555", style="dashed"];')

    lines.append("}")
    return "\n".join(lines)


def render(report):
    st.subheader("Execution Trace & Automaton View")

    layer2 = report["layer2"]
    
    if layer2["sim"] is None:
        st.warning("Layer 2 did not run: normalized input failed the Alphabet Check.")
        st.info("No automaton trace can be generated for invalid alphabet symbols.")
        return

    sim = layer2["sim"]
    trace = sim["trace"]
    is_accepted = sim["accepted"]
    final_state = sim["final_state"]

    st.markdown("#### 1. Step-by-Step Execution Path")
    st.caption("The exact linear path taken by the input string.")
    
    dot_source = _generate_linear_trace_dot(trace, is_accepted, final_state)
    if dot_source:
        st.graphviz_chart(dot_source)
    else:
        st.info("No trace to display.")

    st.markdown("#### 2. Transition Log")
    st.dataframe(
        pd.DataFrame([
            {"Step": step["step"], "Read Symbol": step["char"], "Current State": step["from_state"], "Next State": step["to_state"]}
            for step in trace
        ]),
        hide_index=True, use_container_width=True
    )
    
    if is_accepted:
        st.success(f"The automaton successfully reached accepting state {final_state}. The string is in L_TIME.")
    else:
        if final_state == "M14":
            st.error("The automaton transitioned to the dead state (M14). The string violates the structural rules of L_TIME.")
        else:
            st.warning(f"The automaton halted in non-accepting state {final_state}. The input was incomplete.")

    st.markdown("#### 3. Minimized DFA Execution View")
    st.caption("The full 15-state Minimized DFA (M0-M14). The red/thick path shows your input's journey; gray/dashed lines are unused transitions.")
    
    highlighted_dot = _generate_highlighted_minimized_dfa(trace, is_accepted, final_state)
    if highlighted_dot:
        st.graphviz_chart(highlighted_dot)
    else:
        st.info("No diagram to display.")

    st.markdown("#### 4. Focused Transition Table (Visited States Only)")
    st.caption("Transition rules only for the states visited during this execution.")
    
    visited_states = list(dict.fromkeys(step["from_state"] for step in trace))
    full_spec = _load_json("minimized_dfa.json")
    full_df = _table(full_spec)
    
    # Exact match filtering to prevent "M1" from matching "* M10"
    mask = full_df["State"].apply(lambda x: _extract_state_name(x) in visited_states)
    st.dataframe(full_df[mask], hide_index=True, use_container_width=True)