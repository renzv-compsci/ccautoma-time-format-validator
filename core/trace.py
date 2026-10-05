from core.automaton import DEAD_STATE


def format_trace_table(trace_data: list) -> list:
    """Converts the raw trace list into a clean table format for Streamlit."""
    return [
        {
            "Step": step["step"],
            "Read Symbol": step["char"],
            "Current State": step["from_state"],
            "Next State": step["to_state"],
        }
        for step in trace_data
    ]


def get_trace_summary(final_state: str, is_accepted: bool) -> str:
    """Generates a short text summary of the trace result."""
    if is_accepted:
        return (
            f"The automaton successfully reached accepting state {final_state}. "
            "The string is in L_TIME."
        )
    if final_state == DEAD_STATE:
        return (
            "The automaton transitioned to the dead state M14. "
            "The string violates the structural rules of L_TIME."
        )
    return (
        f"The automaton halted in non-accepting state {final_state}. "
        "The input was incomplete."
    )