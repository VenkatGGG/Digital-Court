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
    if "theme_dark" not in st.session_state:
        st.session_state.theme_dark = True
    if "sidebar_visible" not in st.session_state:
        st.session_state.sidebar_visible = True

    # Voice argument mode state
    if "voice_mode" not in st.session_state:
        st.session_state.voice_mode = False
    if "voice_recording_side" not in st.session_state:
        st.session_state.voice_recording_side = None  # "plaintiff" or "defense"
    if "voice_audio_data" not in st.session_state:
        st.session_state.voice_audio_data = {}  # {side: bytes}
    if "voice_transcripts" not in st.session_state:
        st.session_state.voice_transcripts = {}  # {side: str}
    if "voice_status" not in st.session_state:
        st.session_state.voice_status = "idle"  # idle, recording, processing, playing, error

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
