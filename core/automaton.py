TRANSITIONS = {
    "M0": {"0": "M1", "1": "M2", "2": "M3"},
    "M1": {"0": "M4", "1": "M5", "2": "M5", "3": "M5", "4": "M5", "5": "M5", "6": "M5", "7": "M5", "8": "M5", "9": "M5"},
    "M2": {"0": "M5", "1": "M5", "2": "M5", "3": "M4", "4": "M4", "5": "M4", "6": "M4", "7": "M4", "8": "M4", "9": "M4"},
    "M3": {"0": "M4", "1": "M4", "2": "M4", "3": "M4"},
    "M4": {":": "M6"},
    "M5": {":": "M7"},
    "M6": {"0": "M8", "1": "M8", "2": "M8", "3": "M8", "4": "M8", "5": "M8"},
    "M7": {"0": "M9", "1": "M9", "2": "M9", "3": "M9", "4": "M9", "5": "M9"},
    "M8": {"0": "M10", "1": "M10", "2": "M10", "3": "M10", "4": "M10", "5": "M10", "6": "M10", "7": "M10", "8": "M10", "9": "M10"},
    "M9": {"0": "M11", "1": "M11", "2": "M11", "3": "M11", "4": "M11", "5": "M11", "6": "M11", "7": "M11", "8": "M11", "9": "M11"},
    "M10": {},
    "M11": {" ": "M12"},
    "M12": {"A": "M13", "P": "M13"},
    "M13": {"M": "M10"},
    "M14": {}
}

ACCEPTING_STATES = {"M10", "M11"}
DEAD_STATE = "M14"
START_STATE = "M0"

def simulate(input_string: str) -> dict:
    current_state = START_STATE
    trace = []

    for index, char in enumerate(input_string):
        next_state = TRANSITIONS.get(current_state, {}).get(char, DEAD_STATE)

        trace.append({
            "step": index,
            "char": char if char != " " else "' '",
            "from_state": current_state,
            "to_state": next_state
        })

        current_state = next_state

        # Dead-state optimization: stop reading on hard reject.
        if current_state == DEAD_STATE:
            break

    return {
        "accepted": current_state in ACCEPTING_STATES,
        "final_state": current_state,
        "trace": trace
    }