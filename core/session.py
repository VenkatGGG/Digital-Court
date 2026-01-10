"""
core/session.py - Session state management
"""

import streamlit as st
import time
from orchestrator import TrialOrchestrator
from data.mock import MOCK_JUROR_DATA

def init_session_state():
    """Initialize all session state variables."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = TrialOrchestrator()
    if "upload_processed" not in st.session_state:
        st.session_state.upload_processed = False
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "case_id" not in st.session_state:
        st.session_state.case_id = f"JEM-{time.strftime('%Y')}-{hash(time.time()) % 100000:05d}"
    if "juror_thoughts" not in st.session_state:
        st.session_state.juror_thoughts = {}
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False
    if "demo_jurors" not in st.session_state:
        st.session_state.demo_jurors = [j.copy() for j in MOCK_JUROR_DATA]
    if "expanded_message" not in st.session_state:
        st.session_state.expanded_message = None
    if "trial_started" not in st.session_state:
        st.session_state.trial_started = False

def add_message(orch, agent_type: str, agent_name: str, content: str, score=None) -> dict:
    """Add message to transcript and return formatted dict."""
    msg = orch._add_to_transcript(agent_type, agent_name, content, score)
    return {
        "agent_type": msg.agent_type,
        "agent_name": msg.agent_name,
        "content": msg.content,
        "timestamp": msg.timestamp,
        "score": msg.score
    }
