# Time Format Validator

> **A formal-language-driven time string validator built on a minimized 15-state Deterministic Finite Automaton (DFA). Developed as the CCAUTOMA / COM241 course project by Group Chicken Wings.**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-151%20passed-brightgreen.svg)](./tests)
[![States](https://img.shields.io/badge/DFA%20States-15%20minimized-orange.svg)](./data/minimized_dfa.json)

---

## Overview

The **Time Format Validator** is a smart pattern-recognition system that determines whether an input string follows a valid time format in the combined language **L_TIME = L_24 ∪ L_12**, without requiring manual mode selection.

It recognizes two formats simultaneously:
- **24-hour format**: `HH:MM` (hours 00-23, minutes 00-59)
- **12-hour format**: `HH:MM AM` or `HH:MM PM` (hours 01-12, minutes 00-59, uppercase meridiem)

The entire system is built from the ground up using formal language theory: a mathematical regular expression was converted into an ε-NFA, which was then transformed via subset construction into a 17-state DFA, and finally reduced to an optimized **15-state minimized DFA** using Moore's Algorithm.

## Features

- **Dual-Format Recognition**: Accepts both 24-hour and 12-hour time formats in a single pass
- **Mathematically Verified**: Every state and transition is formally defined and tested
- **Two-Layer Architecture**:
  - **Layer 1 (Formal)**: Strict alphabet check + DFA evaluation on raw input
  - **Layer 2 (System)**: Normalization (case-folding, hour padding) + DFA evaluation
- **151 Test Cases**: Comprehensive unit, integration, and behavior matrix tests — all passing
- **Step-by-Step Trace**: Visualizes every state transition as the DFA processes input
- **Diagnostics Engine**: Explains exactly *why* an input was rejected (alphabet failure, dead state, or incomplete)
- **Data-Driven Design**: DFA transitions stored in JSON, separating math from code

## Architecture

The system implements a **two-layer policy** that bridges mathematical purity with practical usability:

```
┌─────────────────────────────────────────────────────────────┐
│                    Raw User Input                            │
│                    (e.g., "9:30 am")                         │
└──────────────────┬──────────────────────┬───────────────────┘
                   │                      │
         ┌─────────▼─────────┐  ┌────────▼────────┐
         │   LAYER 1 (Formal)│  │  LAYER 2 (System)│
         │   Alphabet Check  │  │   Normalizer     │
         │   + Raw DFA Run   │  │   + DFA Run      │
         └─────────┬─────────┘  └────────┬────────┘
                   │                      │
         ┌─────────▼─────────┐  ┌────────▼────────┐
         │  Formal Verdict   │  │  System Verdict  │
         │   (REJECTED)      │  │   (ACCEPTED)     │
         └─────────┬─────────┘  └────────┬────────┘
                   │                      │
                   └──────────┬───────────┘
                              ▼
                    ┌──────────────────┐
                    │    GUI Output    │
                    │   Dual Verdicts  │
                    └──────────────────┘
```

### Why Two Layers?

- The **formal layer** enforces strict membership in **L_TIME** as defined in the mathematical specification.
- The **system layer** handles real-world typing habits (lowercase `am`, missing leading zero) via two documented normalization rules:
  - **N1**: Meridiem case-folding (`am` → `AM`)
  - **N2**: Hour zero-padding (`9:30` → `09:30`)
- The space delimiter is **not** normalized because it is a structural boundary, not a cosmetic detail.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Web UI | Streamlit 1.64.0 |
| Data | JSON configuration files |
| Testing | Custom Python test harness |
| Diagrams | Graphviz |

## Project Structure

```
CCAUTOMA-Time-Format-Validator/
├── core/                    # Core processing engine
│   ├── alphabet_check.py    # Layer 1 symbol validation
│   ├── normalizer.py        # N1 and N2 normalization rules
│   ├── automaton.py         # DFA simulation engine
│   └── trace.py             # State transition tracer
├── artifacts/               # Mathematical definitions (Python)
│   ├── formal_language.py   # Σ, component sets, L_TIME
│   └── regex_artifacts.py   # Programming + mathematical regex
├── data/                    # Machine-readable formal specs
│   ├── nfa.json             # 19-state ε-NFA transitions
│   ├── dfa.json             # 17-state DFA transitions
│   └── minimized_dfa.json   # 15-state minimized DFA transitions
├── ui/                      # Streamlit interface
│   ├── layout.py            # Main app layout
│   ├── formal_language_tab.py
│   ├── automata_tab.py
│   └── trace_tab.py
├── tests/                   # 151 test cases
│   ├── test_alphabet_check.py
│   ├── test_normalizer.py
│   ├── test_automaton.py
│   ├── test_trace.py
│   ├── test_samples.py
│   ├── test_diagnostics.py
│   └── smoke_test/
├── diagrams/                # Graphviz .dot state diagrams
├── docs/                    # Documentation
│   └── FORMAL_SPECIFICATION.md
└── README.md
```

## Installation & Usage

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/renzv-compsci/ccautoma-time-format-validator.git
cd ccautoma-time-format-validator

# Create and activate virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run ui/layout.py
```

The app will open in your browser at `http://localhost:8501`.

### Running Tests

```bash
# Run all 151 tests
python -m tests.test_alphabet_check
python -m tests.test_normalizer
python -m tests.test_automaton
python -m tests.test_trace
python -m tests.test_samples
python -m tests.test_diagnostics

# Run integration smoke tests
python -m tests.smoke_test.test_layers
python -m tests.smoke_test.test_dfa
python -m tests.smoke_test.test_pipeline
```

## Testing Coverage

The system is verified by **151 test cases** across 9 test suites:

| Suite | Scope | Cases |
|-------|-------|-------|
| Alphabet Check | Layer 1 symbol gate | 26 |
| Lexical Normalizer | N1 + N2 rules | 14 |
| Minimized DFA Engine | Accept/dead/incomplete verdicts | 28 |
| Trace Builder | GUI rendering | 7 |
| Behavior Matrix | Two-layer verdicts | 33 |
| Diagnostics | Rejection explanations | 13 |
| Two-Layer Smoke | Integration wiring | 6 |
| Engine Trace Smoke | Key transitions | 6 |
| Full Pipeline | End-to-end | 18 |

**Boundary values tested**: `00`, `12`, `23`, `24`, `59`, `60`

## Formal Language Theory

This project demonstrates the equivalence of multiple representations of a regular language:

| Representation | Description |
|----------------|-------------|
| **Set-Builder Notation** | L_TIME = L_24 ∪ L_12 |
| **Regular Expression** | R_TIME = R_24 + R_12 |
| **ε-NFA** | 19 states (q0–q18) |
| **DFA (subset construction)** | 17 states (S0–S15 + ∅) |
| **Minimized DFA** | 15 states (M0–M14) |

The master alphabet Σ_TIME contains exactly 15 symbols:

```
Σ_TIME = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, :, ' ', A, M, P}
```

### Minimization Results

Moore's Algorithm identified two pairs of indistinguishable states:
- **{S10, S15}** → **M10**: Both accepting states with identical transitions (all to dead state)
- **{S13, S14}** → **M13**: Both transition to M10 on 'M', to dead state otherwise

## Team - Chicken Wings

| Role | Member |
|------|--------|
| Project Leader | Renz Viloria |
| Language Analyst | Markie Angelo |
| RE/NFA Designer | Mae Santos |
| DFA Designer | Antonio Garcia |
| Automata Optimizer | Nico Gallardo |
| Programmer | Renz Viloria |
| Tester/QA | Kit Dustin & Michelle Senopera |
| Documentation Lead | Charles Cabatian |

## Course Information

- **Course**: CCAUTOMA / COM241 — Automata Theory and Formal Languages
- **Academic Year**: 1st Semester, AY 2026
- **Project Type**: Pattern Recognition System
- **Defense Date**: October 6 & 9, 2026

## License

This project was developed for academic purposes as part of the CCAUTOMA / COM241 course project. All formal language definitions, automata constructions, and test cases are original work of Group Chicken Wings.

---

<p align="center">
  <b>Built with rigor. Verified by automata.</b><br>
  <i>A demonstration that mathematical theory and practical software engineering can coexist cleanly.</i>
</p>