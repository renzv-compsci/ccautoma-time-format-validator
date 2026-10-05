"""Formal Language tab: LaTeX-rendered formal specification.

Mirrors Sections 3-7 of the revised Formal Language Analysis, plus the
user-input layer language (L_USER) with its own alphabet and component
sets defined over the normalized input, member strings shown as ordered
symbol sequences, and the mathematical regular expressions (R_TIME for
the formal layer and R_USER as the system-layer raw-input view), so the
GUI notation matches the team papers exactly.
"""

import pandas as pd
import streamlit as st


def render():
    st.subheader("Formal Language Specification")

    # ---------------------------------------------------------
    # 1. Master alphabet
    # ---------------------------------------------------------
    st.markdown("### 1. Master Alphabet")
    st.markdown(
        "The validator reads every input over one master alphabet of 15 symbols. "
        "The quoted space element denotes exactly one literal space character "
        "(written as the visible-space symbol in the team papers)."
    )
    st.latex(r"\Sigma_{\text{TIME}} = \{\,0,1,2,3,4,5,6,7,8,9,\;\; :\;\; \text{' '},\;\; A,\;\; M,\; P\,\}")
    st.latex(r"|\Sigma_{\text{TIME}}| = 15")

    # ---------------------------------------------------------
    # 2. Component sets (full formal specification)
    # ---------------------------------------------------------
    st.markdown("### 2. Component Sets")
    st.latex(r"D = \{0,1,2,3,4,5,6,7,8,9\}")
    st.latex(r"\text{MIN} = \{00, 01, 02, \dots, 58, 59\}")
    st.latex(r"H_{24} = \{00, 01, 02, \dots, 22, 23\}")
    st.latex(r"H_{12} = \{01, 02, 03, \dots, 11, 12\}")
    st.latex(r"\text{MER} = \{\text{AM}, \text{PM}\}")

    # ---------------------------------------------------------
    # 3. Language of the user's time input
    # ---------------------------------------------------------
    st.markdown("### 3. Language of the User's Time Input")
    st.latex(r"L_{24} = \{\, h\,:\,m \;\mid\; h \in H_{24},\; m \in \text{MIN} \,\}")
    st.latex(r"L_{12} = \{\, h\,:\,m\;\text{' '}\;x \;\mid\; h \in H_{12},\; m \in \text{MIN},\; x \in \text{MER} \,\}")
    st.latex(r"L_{\text{TIME}} = L_{24} \cup L_{12}")
    st.markdown(
        "The system applies **no mode selection**: an input is accepted when it "
        "belongs to either branch of the union."
    )

    # ---------------------------------------------------------
    # 4. Scope and conventions
    # ---------------------------------------------------------
    st.markdown("### 4. Scope and Conventions")
    st.markdown(
        """
        - Leading zeroes are required: `09:05` is valid, `9:05` is invalid.
        - The colon `:` between hour and minute is required.
        - The 24-hour format contains no AM or PM suffix.
        - The 12-hour format requires exactly one space before AM or PM.
        - Meridiem indicators must be uppercase: AM or PM.
        - Extra spaces or characters before or after the time are not allowed.
        - Seconds, dates, and time-zone indicators are outside the language.
        """
    )

    # ---------------------------------------------------------
    # 5. Rejection layers
    # ---------------------------------------------------------
    st.markdown("### 5. Rejection Layers")
    st.markdown(
        """
        1. **Alphabet Check** - any symbol outside $\Sigma_{\text{TIME}}$ is rejected before the automaton runs.
        2. **Automaton (Dead State)** - all symbols are legal, but the structure violates $L_{\text{TIME}}$.
        """
    )

    # ---------------------------------------------------------
    # 6. Boundary cases
    # ---------------------------------------------------------
    st.markdown("### 6. Boundary Cases")
    boundary = pd.DataFrame(
        [
            ["00:00", "Yes", "No", "ACCEPTED", "Earliest 24-hour time; 12-hour hours start at 01"],
            ["12:00", "Yes", "No", "ACCEPTED", "24-hour noon; 12-hour format requires a suffix"],
            ["12:00 AM", "No", "Yes", "ACCEPTED", "Midnight in 12-hour format"],
            ["12:00 PM", "No", "Yes", "ACCEPTED", "Noon in 12-hour format"],
            ["13:00", "Yes", "No", "ACCEPTED", "24-hour only; 12-hour hours stop at 12"],
            ["23:59", "Yes", "No", "ACCEPTED", "Latest 24-hour time"],
            ["00:00 AM", "No", "No", "REJECTED", "Hour 00 does not exist in 12-hour time"],
            ["13:00 PM", "No", "No", "REJECTED", "Hour 13 exceeds the 12-hour maximum"],
        ],
        columns=["Input", "In L24", "In L12", "System Result", "Explanation"],
    )
    st.dataframe(boundary, hide_index=True, use_container_width=True)

    # ---------------------------------------------------------
    # 7. Programming regex and examples
    # ---------------------------------------------------------
    st.markdown("### 7. Programming Regex (implementation reference)")
    st.code(r"^((([01][0-9]|2[0-3]):[0-5][0-9])|((0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)))$")

    st.markdown(
        "**Accepted examples:** `00:00`, `12:49`, `23:59`, `01:05 AM`, `12:00 PM`  \n"
        "**Rejected examples:** `24:00`, `12:60`, `13:00 PM`, `00:30 AM`, `09:30AM`, `ab:cd`"
    )

    # ---------------------------------------------------------
    # 8. User-input layer language (L_USER)
    # ---------------------------------------------------------
    st.markdown("### 8. User-Input Layer Language (L_USER)")
    st.markdown(
        "The two-layer architecture keeps the formal layer mathematically pure: "
        "casual typing habits are resolved by the system layer before the "
        "automaton runs, so the formal layer only ever reads canonical strings "
        "such as `09:30 AM`. To make the user layer a self-contained formal "
        "object, this section gives it its own alphabet and component sets, "
        "defined over the normalized user input."
    )
    st.latex(r"\Sigma_{\text{USER}} = \{0,1,2,3,4,5,6,7,8,9,\;\; :\;\; \text{' '},\;\; A,\;\; M,\; P\,\}")
    st.latex(r"|\Sigma_{\text{USER}}| = 15")
    st.latex(r"D_{U} = \{0,1,2,3,4,5,6,7,8,9\}")
    st.latex(r"\text{MIN}_{U} = \{00, 01, 02, \dots, 58, 59\}")
    st.latex(r"H_{24}^{U} = \{00, 01, 02, \dots, 22, 23\}")
    st.latex(r"H_{12}^{U} = \{01, 02, 03, \dots, 11, 12\}")
    st.latex(r"\text{MER}_{U} = \{\text{AM}, \text{PM}\}")
    st.latex(r"L_{\text{USER},24} = \{\, h\,:\,m \;\mid\; h \in H_{24}^{U},\; m \in \text{MIN}_{U} \,\}")
    st.latex(r"L_{\text{USER},12} = \{\, h\,:\,m\;\text{' '}\;x \;\mid\; h \in H_{12}^{U},\; m \in \text{MIN}_{U},\; x \in \text{MER}_{U} \,\}")
    st.latex(r"L_{\text{USER}} = L_{\text{USER},24} \cup L_{\text{USER},12}")
    st.latex(r"L_{\text{USER}} \equiv L_{\text{TIME}}")
    st.caption(
        "Because the system layer supplies only canonical strings, every user-layer "
        "component coincides with its general counterpart (Sigma_USER = Sigma_TIME, "
        "H24^U = H24, H12^U = H12, MIN_U = MIN, MER_U = MER). The parallel "
        "specification makes explicit what the normalized user input is as a formal "
        "object, and yields L_USER equivalent to L_TIME."
    )

    st.markdown(
        "A member of L_USER is an ordered sequence of symbols taken from "
        "Sigma_USER, not a set of symbols. For the normalized input 09:30 AM:"
    )
    st.latex(r"09:30\;\text{AM} \;=\; 0 \cdot 9 \cdot : \cdot 3 \cdot 0 \cdot \text{' '} \cdot A \cdot M \;\in\; L_{\text{USER},12}")
    st.latex(r"23:59 \;=\; 2 \cdot 3 \cdot : \cdot 5 \cdot 9 \;\in\; L_{\text{USER},24}")
    st.caption(
        "The collection {0, 9, :, 3, 0, ' ', A, M} is the symbol set of the single "
        "member 09:30 AM. The alphabet of the layer is the union of the symbols of "
        "all members, which is why Sigma_USER contains all ten digits, the colon, "
        "the space, and the letters A, M, and P."
    )

    user_examples = pd.DataFrame(
        [
            ["9:30 am", "09:30 AM", "L_USER,12", "ACCEPTED"],
            ["1:05 PM", "01:05 PM", "L_USER,12", "ACCEPTED"],
            ["0:30", "00:30", "L_USER,24", "ACCEPTED"],
            ["12:49 AM", "12:49 AM", "L_USER,12", "ACCEPTED"],
            ["0:30 am", "00:30 AM", "neither", "REJECTED"],
            ["24:00", "24:00", "neither", "REJECTED"],
        ],
        columns=["User input (system layer)", "Canonical form (formal layer)", "Branch", "Result"],
    )
    st.dataframe(user_examples, hide_index=True, use_container_width=True)
    st.caption(
        "The formal layer never sees the casual text; it evaluates only the canonical "
        "column. For example, 0:30 am is rejected because its canonical form 00:30 AM "
        "belongs to neither branch."
    )

    # ---------------------------------------------------------
    # 9. Mathematical regular expressions
    # ---------------------------------------------------------
    st.markdown("### 9. Mathematical Regular Expressions")
    st.markdown(
        "The programming regex of Section 7 is a direct encoding of the following "
        "theoretical expressions, written with concatenation and the union "
        "operation +. R_TIME is the expression of the formal layer and is "
        "evaluated on the canonical form of the user's input."
    )
    st.latex(r"D = (0+1+2+3+4+5+6+7+8+9)")
    st.latex(r"R_{24} = ((0+1)D + 2(0+1+2+3))\,:\,(0+1+2+3+4+5)D")
    st.latex(r"R_{12} = (0(1+2+\dots+9) + 1(0+1+2))\,:\,(0+1+2+3+4+5)D\;\text{' '}\;(AM+PM)")
    st.latex(r"R_{\text{TIME}} = R_{24} + R_{12}")
    st.markdown(
        "The system layer additionally accepts the raw inputs described by R_USER; "
        "it converts them to canonical form before the formal layer runs, so these "
        "raw-input expressions are a system-layer view, not part of the formal language."
    )
    st.latex(r"R_{\text{USER},24} = (D + (0+1)D + 2(0+1+2+3))\,:\,(0+1+2+3+4+5)D")
    st.latex(
        r"R_{\text{USER},12} = ((1+2+\dots+9) + 0(1+2+\dots+9) + 1(0+1+2))"
        r"\,:\,(0+1+2+3+4+5)D\;\text{' '}\;((a+A)(m+M) + (p+P)(m+M))"
    )
    st.latex(r"R_{\text{USER}} = R_{\text{USER},24} + R_{\text{USER},12}")

    legend = pd.DataFrame(
        [
            ["D", "any single digit", "[0-9]"],
            ["(0+1)D", "hours 00-19", "[01][0-9]"],
            ["2(0+1+2+3)", "hours 20-23", "2[0-3]"],
            ["(0+1+2+3+4+5)D", "minutes 00-59", "[0-5][0-9]"],
            ["0(1+2+...+9)", "hours 01-09", "0[1-9]"],
            ["1(0+1+2)", "hours 10-12", "1[0-2]"],
            [":", "literal colon", ":"],
            ["' ' (one space)", "literal space", " "],
            ["(AM+PM)", "uppercase meridiem", "(AM|PM)"],
            ["((a+A)(m+M) + (p+P)(m+M))", "any-case meridiem (system layer)", "handled before the formal layer"],
            ["leading D / (1+...+9)", "one-digit hour (system layer)", "handled before the formal layer"],
        ],
        columns=["Mathematical component", "Meaning", "Programming counterpart"],
    )
    st.table(legend)
    st.caption(
        "A raw string described by R_USER is accepted by the system because its "
        "canonical form matches R_TIME. The programming regex remains the "
        "implementation reference for R_TIME and is retained unchanged for the code."
    )

    st.caption("Full details: docs/FORMAL_SPECIFICATION.md")