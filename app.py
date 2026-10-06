"""Smart Time Format Validator - main Streamlit entry point."""

import streamlit as st

from core.diagnostics import build_report
from core.samples import SAMPLE_BUTTONS
from ui import (
    automata_tab,
    formal_language_tab,
    layout,
    simulation_tab,
    summary_tab,
    test_cases_tab,
    trace_tab,
)

st.set_page_config(page_title="Smart Time Format Validator", layout="wide")

layout.render_header()

st.text_input("Enter a time string", key="raw_input", placeholder="e.g. 12:49 AM")


def _load_sample(sample: str):
    """Button callback. Runs before the next rerun, so widget keys may be set here."""
    st.session_state["raw_input"] = sample
    st.session_state["report"] = build_report(sample)


btn_cols = st.columns(len(SAMPLE_BUTTONS) + 1)
for col, sample in zip(btn_cols, SAMPLE_BUTTONS):
    col.button(sample, key=f"sample_{sample}", on_click=_load_sample, args=(sample,))

if btn_cols[-1].button("Validate", type="primary", key="validate_btn"):
    st.session_state["report"] = build_report(st.session_state.get("raw_input", ""))

report = st.session_state.get("report")

tab_summary, tab_lang, tab_automata, tab_sim, tab_trace, tab_tests = st.tabs(
    ["Summary", "Formal Language", "Automata", "Simulation", "Trace", "Test Cases"]
)

with tab_summary:
    if report:
        summary_tab.render(report)
    else:
        st.info("Enter a time string and press Validate.")

with tab_lang:
    formal_language_tab.render()

with tab_automata:
    automata_tab.render()

with tab_trace:
    if report:
        trace_tab.render(report)
    else:
        st.info("Run a validation to see the trace.")

with tab_tests:
    test_cases_tab.render()

# Rendered last: its Play animation sleeps between frames, which would
# otherwise delay every tab drawn after it.
with tab_sim:
    simulation_tab.render()
