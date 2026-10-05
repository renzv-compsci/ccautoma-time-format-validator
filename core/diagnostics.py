from core import alphabet_check, normalizer, automaton

STATE_EXPECTATION = {
    "M0": "Hour must start with 0, 1, or 2.",
    "M3": "Hour starting with 2 must end with 0-3 (20-23).",
    "M4": "Colon ':' expected after the hour.",
    "M5": "Colon ':' expected after the hour.",
    "M6": "First minute digit must be 0-5.",
    "M7": "First minute digit must be 0-5.",
    "M11": "End of input (24-hour) or exactly one space before AM/PM.",
    "M12": "Meridiem must start with 'A' or 'P'.",
    "M13": "Meridiem must end with 'M'.",
}

def _check_and_simulate(text: str) -> dict: 
    passed, invalid = alphabet_check.check_alphabet(text)
    if not passed: 
        return {"passed": False, "invalid": invalid, "sim": None}
    return {"passed": True, "invalid": [], "sim": automaton.simulate(text)}

def _detected_format(normalized: str, sim: dict): 
    if not sim or not sim["accepted"]: 
        return None 
    return "12-hour" if " " in normalized else "24-hour"

def _failure_info(sim: dict) -> dict: 
    for step in sim["trace"]: 
        if step["to_state"] == automaton.DEAD_STATE: 
            return{
                "index": step["step"], 
                "char": step["char"], 
                "from_state": step["from_state"], 
                "expected": sorted(
                    automaton.TRANSITIONS.get(step["from_state"], {}).keys()
                )
            }
    
    return {
        "index": len(sim["trace"]),
        "char": None, 
        "from_state": sim["final_state"], 
        "expected": sorted(
            automaton.TRANSITIONS.get(sim["final_state"], {}).keys()
        )
    }

def build_report(raw_input: str) -> dict: 
    normalized = normalizer.normalize(raw_input)

    layer1 = _check_and_simulate(raw_input)
    layer2 = _check_and_simulate(normalized)

    formal_accepted = bool(layer1["sim"] and layer1["sim"]["accepted"])
    system_accepted = bool(layer2["sim"] and layer2["sim"]["accepted"])

    report = {
        "raw": raw_input,
        "normalized": normalized,
        "layer1": layer1,
        "layer2": layer2,
        "formal_accepted": formal_accepted,
        "system_accepted": system_accepted,
        "detected_format": _detected_format(normalized, layer2["sim"]),
        "rejection_layer": None,
        "failure": None,
        "explanation": "",
    }

    if system_accepted:
        if not formal_accepted:
            report["explanation"] = (
                "Raw input is not in the formal language (Layer 1). "
                f"The lexical normalizer mapped it to '{normalized}', "
                "which the minimized DFA accepts (Layer 2)."
            )
        else:
            report["explanation"] = (
                f"Canonical input accepted as a {report['detected_format']} time."
            )
        return report

    if not layer2["passed"]:
        idx, char = layer2["invalid"][0]
        report["rejection_layer"] = "Alphabet Check"
        report["failure"] = {
            "index": idx,
            "char": char,
            "from_state": None,
            "expected": sorted(alphabet_check.SIGMA_TIME),
        }
        report["explanation"] = (
            f"Symbol '{char}' at index {idx} is not in the master alphabet. "
            "Rejected before automaton execution."
        )
    else:
        sim = layer2["sim"]
        fail = _failure_info(sim)
        report["failure"] = fail
        if sim["final_state"] == automaton.DEAD_STATE:
            report["rejection_layer"] = "Automaton (Dead State)"
        else:
            report["rejection_layer"] = "Incomplete Input"
        report["explanation"] = STATE_EXPECTATION.get(
            fail["from_state"], "Unexpected symbol at this position."
        )

    return report