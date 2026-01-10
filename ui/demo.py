"""
ui/demo.py - Demo mode rendering
"""

import streamlit as st
import random
from ui.components import (
    render_header,
    render_status_bar,
    render_counsel_box,
    render_jury_box_from_scores,
    escape_html
)
from data.mock import (
    MOCK_PLAINTIFF_MESSAGES,
    MOCK_DEFENSE_MESSAGES,
    MOCK_CASE_FACTS,
    JUROR_PERSONAS
)

def render_demo_mode():
    """Render UI with mock data."""
    demo_jurors = st.session_state.demo_jurors

    render_header()
    render_status_bar("Arguments", "JEM-2024-00847", "Demo")

    # Judge's Bench
    st.markdown('''
    <div class="bench">
        <div class="bench-label">The Court</div>
        <div class="bench-content">
            <strong>Court is in Session</strong><br><br>
            <em>The jury is reminded to evaluate evidence based solely on what is presented in this courtroom.
            Outside research or personal knowledge of the parties is strictly prohibited.</em><br><br>
            Counsel may proceed with arguments.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    col_plaintiff, col_evidence, col_defense = st.columns([1, 1, 1])

    with col_plaintiff:
        st.markdown(render_counsel_box("plaintiff", MOCK_PLAINTIFF_MESSAGES), unsafe_allow_html=True)

    with col_evidence:
        st.markdown(f'''
        <div class="evidence-box">
            <div class="evidence-header">Evidence</div>
            <div class="evidence-content">
                <div class="case-title-display">Jones v. Smith</div>
                <div class="case-excerpt">{escape_html(MOCK_CASE_FACTS[:400])}...</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with col_defense:
        st.markdown(render_counsel_box("defense", MOCK_DEFENSE_MESSAGES), unsafe_allow_html=True)

    # Jury Box
    jury_scores = {j["name"]: j["score"] for j in demo_jurors}
    juror_personas = {}
    for j in demo_jurors:
        persona = JUROR_PERSONAS.get(j["name"], {"occupation": "Juror"})
        juror_personas[j["name"]] = {
            "occupation": persona["occupation"],
            "thought": j["thought"]
        }
    render_jury_box_from_scores(jury_scores, juror_personas)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Demo Mode</div>', unsafe_allow_html=True)

        st.info("Preview mode with mock data")

        if st.button("Exit Demo", use_container_width=True):
            st.session_state.demo_mode = False
            st.rerun()

        st.divider()
        st.markdown("### Jury Controls")

        if st.button("Randomize Scores", use_container_width=True):
            thoughts = [
                "This changes everything...",
                "I'm not convinced yet.",
                "Compelling argument.",
                "Need more evidence.",
                "The timeline is suspicious.",
                "Both sides have merit.",
            ]
            for j in st.session_state.demo_jurors:
                j["score"] = random.randint(20, 80)
                j["thought"] = random.choice(thoughts)
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("+ Plaintiff", use_container_width=True):
                for j in st.session_state.demo_jurors:
                    j["score"] = min(100, j["score"] + random.randint(5, 15))
                st.rerun()
        with col2:
            if st.button("+ Defense", use_container_width=True):
                for j in st.session_state.demo_jurors:
                    j["score"] = max(0, j["score"] - random.randint(5, 15))
                st.rerun()
