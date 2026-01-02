"""
ui/handlers.py - Action Handlers

Handlers for streaming responses and trial actions.
"""

import time
import re
import streamlit as st

from ui.components import render_message_streaming, escape_html


def stream_response(agent, prompt: str, agent_type: str, agent_name: str, placeholder) -> str:
    """
    Stream an agent's response into a Streamlit placeholder.
    
    Args:
        agent: The agent (with generate_stream method)
        prompt: The prompt to send
        agent_type: Type for styling (plaintiff, defense, etc.)
        agent_name: Display name
        placeholder: Streamlit placeholder to update
    
    Returns:
        The complete response text
    """
    timestamp = time.strftime("%H:%M:%S")
    full_response = ""
    
    try:
        for chunk in agent.generate_stream(prompt):
            full_response += chunk
            render_message_streaming(
                agent_type=agent_type,
                agent_name=agent_name,
                content=full_response,
                timestamp=timestamp,
                is_streaming=True,
                placeholder=placeholder
            )
        
        # Final render without cursor
        render_message_streaming(
            agent_type=agent_type,
            agent_name=agent_name,
            content=full_response,
            timestamp=timestamp,
            is_streaming=False,
            placeholder=placeholder
        )
        
    except Exception as e:
        full_response = f"[Error: {e}]"
        placeholder.error(full_response)
    
    return full_response


def extract_pdf_text(uploaded_file) -> str:
    """
    Extract text from an uploaded PDF file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        Extracted text or None on error
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages]).strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
