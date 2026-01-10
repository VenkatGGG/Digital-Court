"""
JUSTICIA EX MACHINA: Autonomous Judicial Simulation
════════════════════════════════════════════════════

A strikingly minimal interface for AI-powered courtroom proceedings.
The weight of algorithmic justice meets refined design.
"""

import streamlit as st
import time

# Package imports
from config.settings import get_settings
from orchestrator import TrialOrchestrator, TrialPhase
from ui.styles import get_css
from ui.components import (
    render_header,
    render_status_bar,
    render_counsel_box,
    render_jury_box_from_scores,
    render_message,
    escape_html,
)
from ui.handlers import extract_pdf_text

# New modules
from data.mock import JUROR_PERSONAS
from core.session import init_session_state
from ui.demo import render_demo_mode
from ui.phases import (
    get_phase_display_name,
    get_case_summary,
    get_latest_judge_message,
    build_juror_personas,
    update_judge_bench,
    run_opening_statements,
    run_argument_round,
    run_jury_deliberation,
    run_verdict,
    run_autonomous_trial
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

settings = get_settings()

# Sidebar state management
_sidebar_state = "expanded"

if hasattr(st, 'session_state') and 'sidebar_visible' in st.session_state:
    _sidebar_state = "expanded" if st.session_state.sidebar_visible else "collapsed"

st.set_page_config(
    page_title="Justicia Ex Machina",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state=_sidebar_state

)

# Apply CSS
st.markdown(get_css(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    init_session_state()

    if st.session_state.demo_mode:
        render_demo_mode()
        return

    orch = st.session_state.orchestrator
    is_processing = st.session_state.is_processing

    # ═══════════════════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════════════════
    render_header()

    phase = orch.phase
    phase_display = get_phase_display_name(phase)
    session_status = "Processing" if is_processing else "Active"

    render_status_bar(phase_display, st.session_state.case_id, session_status)

    # ═══════════════════════════════════════════════════════════════════════════
    # JUDGE'S BENCH
    # ═══════════════════════════════════════════════════════════════════════════
    judge_placeholder = st.empty()

    latest_judge = get_latest_judge_message(orch)

    if latest_judge:
        judge_content = latest_judge
    elif phase == TrialPhase.AWAITING_COMPLAINT:
        judge_content = "**Awaiting Case Filing**\n\n*Submit a complaint document to initialize proceedings.*"
    elif phase == TrialPhase.COURT_ASSEMBLED:
        judge_content = f"**Court is Assembled**\n\n*Case:* {orch.case_title}\n\n*All parties present. Counsel may proceed.*"
    elif phase == TrialPhase.ADJOURNED:
        judge_content = "**Court is Adjourned**\n\n*This matter has been concluded.*"
    else:
        judge_content = "**Court is in Session**\n\n*Proceedings underway.*"

    update_judge_bench(judge_placeholder, judge_content)

    # ═══════════════════════════════════════════════════════════════════════════
    # THE WELL: Counsel Tables + Evidence
    # ═══════════════════════════════════════════════════════════════════════════
    col_plaintiff, col_evidence, col_defense = st.columns([1, 1, 1])

    # Plaintiff
    with col_plaintiff:
        plaintiff_msgs = [m for m in orch.get_transcript() if m.get('agent_type') == 'plaintiff']
        plaintiff_stream_placeholder = st.empty()
        plaintiff_stream_placeholder.markdown(render_counsel_box("plaintiff", plaintiff_msgs), unsafe_allow_html=True)

    # Evidence
    with col_evidence:
        evidence_html = '<div class="evidence-box"><div class="evidence-header">Evidence</div><div class="evidence-content">'

        if orch.case_facts:
            if orch.case_title:
                evidence_html += f'<div class="case-title-display">{escape_html(orch.case_title)}</div>'

            summary = get_case_summary(orch.case_facts, 400)
            evidence_html += f'<div class="case-excerpt">{escape_html(summary)}</div>'

            # Expandable full document
            full_doc = escape_html(orch.case_facts).replace('\n', '<br>')
            evidence_html += f'''
            <details class="argument-collapse" style="margin-top: 1rem;">
                <summary>View Full Document</summary>
                <div class="argument-collapse-content" style="max-height: 300px; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem;">
                    {full_doc}
                </div>
            </details>'''
        else:
            evidence_html += '<div style="color: #4A4845; font-style: italic; padding: 2rem; text-align: center;">No evidence submitted</div>'

        evidence_html += '</div></div>'
        st.markdown(evidence_html, unsafe_allow_html=True)

    # Defense
    with col_defense:
        defense_msgs = [m for m in orch.get_transcript() if m.get('agent_type') == 'defense']
        defense_stream_placeholder = st.empty()
        defense_stream_placeholder.markdown(render_counsel_box("defense", defense_msgs), unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # JURY BOX
    # ═══════════════════════════════════════════════════════════════════════════
    if orch.jury and orch.jury.size > 0:
        jury_scores = orch.jury.get_scores()
        juror_personas = build_juror_personas(orch)

        render_jury_box_from_scores(jury_scores, juror_personas)

        # Expandable juror details
        with st.expander("Juror Details", expanded=False):
            cols = st.columns(3)
            for idx, (name, score) in enumerate(jury_scores.items()):
                with cols[idx % 3]:
                    persona = juror_personas.get(name, {})
                    occupation = JUROR_PERSONAS.get(name, {}).get("occupation", "Juror")
                    thought = persona.get("thought", "Deliberating...")

                    if score > 55:
                        leaning = "Plaintiff"
                        leaning_color = "#6B2A2A"
                    elif score < 45:
                        leaning = "Defense"
                        leaning_color = "#2A3A6B"
                    else:
                        leaning = "Undecided"
                        leaning_color = "#4A4845"

                    st.markdown(f'''
                    <div style="background: #1A1A1A; border: 1px solid rgba(255,255,255,0.04); border-left: 2px solid {leaning_color}; padding: 1rem; margin-bottom: 0.75rem;">
                        <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #EDE8E0;">{name}</div>
                        <div style="font-family: 'Spectral', serif; font-size: 0.75rem; color: #6B6560; font-style: italic; margin-bottom: 0.5rem;">{occupation}</div>
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #A8A29E; margin-bottom: 0.5rem;">Score: {score} — {leaning}</div>
                        <div style="font-family: 'Spectral', serif; font-size: 0.8rem; color: #6B6560; font-style: italic; line-height: 1.5;">{thought}</div>
                    </div>
                    ''', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # TRANSCRIPT
    # ═══════════════════════════════════════════════════════════════════════════
    with st.expander("Full Transcript", expanded=False):
        for msg in orch.get_transcript():
            render_message(msg)

    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTE PENDING ACTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    if "pending_action" in st.session_state:
        action = st.session_state.pending_action
        del st.session_state.pending_action

        try:
            if action == "opening":
                run_opening_statements(orch, plaintiff_stream_placeholder, defense_stream_placeholder, judge_placeholder)
            elif action == "argument":
                run_argument_round(orch, plaintiff_stream_placeholder, defense_stream_placeholder, judge_placeholder)
            elif action == "jury":
                run_jury_deliberation(orch, judge_placeholder)
            elif action == "verdict":
                run_verdict(orch, judge_placeholder)
            elif action == "autonomous":
                run_autonomous_trial(orch, plaintiff_stream_placeholder, defense_stream_placeholder, judge_placeholder)
        except Exception as e:
            st.error(f"Error: {e}")
            import traceback
            st.code(traceback.format_exc())

        st.session_state.is_processing = False
        st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Case Management</div>', unsafe_allow_html=True)

        if st.button("Preview Demo", use_container_width=True):
            st.session_state.demo_mode = True
            st.rerun()

        st.divider()

        uploaded = st.file_uploader(
            "Submit Complaint (PDF)",
            type=["pdf"],
            disabled=is_processing,
            help="Upload a legal complaint to begin"
        )

        if uploaded and not st.session_state.upload_processed:
            text = extract_pdf_text(uploaded)
            if text:
                orch.set_case(text, uploaded.name.replace(".pdf", ""))
                orch.initialize_court()
                st.session_state.upload_processed = True
                st.rerun()

        st.divider()
        st.markdown("### Controls")

        action_container = st.container()

        if phase == TrialPhase.AWAITING_COMPLAINT:
            action_container.info("Upload a case to begin")

        elif phase == TrialPhase.COURT_ASSEMBLED:
            if action_container.button("Start Proceedings", disabled=is_processing, type="primary", use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "opening"
                st.rerun()

        elif phase == TrialPhase.OPENING_STATEMENTS:
            action_container.warning("Opening statements in progress...")

        elif phase == TrialPhase.ARGUMENTS:
            col1, col2 = action_container.columns(2)
            if col1.button("Next Round", disabled=is_processing, type="primary", use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "argument"
                st.rerun()

            if col2.button("Conclude Debate", disabled=is_processing, use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "jury"
                st.rerun()

            action_container.divider()
            if action_container.button("Run Fully Autonomous", disabled=is_processing, use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "autonomous"
                st.rerun()

        elif phase == TrialPhase.JURY_DELIBERATION:
            if action_container.button("Reach Verdict", disabled=is_processing, type="primary", use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "verdict"
                st.rerun()

        elif phase == TrialPhase.VERDICT:
            if action_container.button("Reset Court", disabled=is_processing, use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # Debug
        with st.expander("Debug Utils"):
            if st.button("Reset State"):
                st.session_state.clear()
                st.rerun()


if __name__ == "__main__":
    main()
