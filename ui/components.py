"""
ui/components.py - JUSTICIA EX MACHINA Component Library

Refined, minimal components for the judicial simulation interface.
Embodies the tension between ancient judicial tradition and computational precision.
"""

import re
import streamlit as st
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from ui.styles import get_score_color, get_sentiment_class


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class JurorDisplay:
    """Data class for juror display information."""
    id: int
    name: str
    occupation: str
    score: int  # 0-100 sentiment score
    thought: str  # Latest internal monologue


# Juror persona data - now without emojis, just names and roles
JUROR_DATA = {
    "Marcus": {"occupation": "Construction Foreman"},
    "Elena": {"occupation": "High School Teacher"},
    "Raymond": {"occupation": "Retired Accountant"},
    "Destiny": {"occupation": "Emergency Room Nurse"},
    "Chen": {"occupation": "Software Engineer"},
    "Patricia": {"occupation": "Former Judge"},
}

# Legacy mapping for backward compatibility
JUROR_EMOJI_MAP = {
    "Marcus": "I",
    "Elena": "II",
    "Raymond": "III",
    "Destiny": "IV",
    "Chen": "V",
    "Patricia": "VI",
}


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header(case_id: str = ""):
    """Render the court header with refined typography."""
    st.markdown('''
    <div class="court-header">
        <h1 class="court-title">Justicia Ex Machina</h1>
        <p class="court-subtitle">Autonomous Judicial Simulation</p>
    </div>
    ''', unsafe_allow_html=True)


def render_status_bar(phase: str, case_id: str, session_status: str = "ACTIVE"):
    """Render the minimal status indicator."""
    st.markdown(f'''
    <div class="trial-status">
        <div class="status-segment">
            <span class="status-label">Phase</span>
            <span class="status-value">{phase}</span>
        </div>
        <div class="status-divider"></div>
        <div class="status-segment">
            <span class="status-label">Case</span>
            <span class="status-value">{case_id}</span>
        </div>
        <div class="status-divider"></div>
        <div class="status-segment">
            <span class="status-label">Status</span>
            <span class="status-value">{session_status}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# JUDGE'S BENCH COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_judge_bench(instruction: str, glow: bool = False):
    """Render the Judge's Bench with refined styling."""
    formatted = format_content(instruction)

    st.markdown(f'''
    <div class="bench">
        <div class="bench-label">The Court</div>
        <div class="bench-content">
            {formatted}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_judge_instruction_streaming(placeholder, content: str, is_streaming: bool = True):
    """Render judge instruction with minimal streaming indicator."""
    cursor = '<span class="typing-cursor"></span>' if is_streaming else ""
    formatted = format_content(content)

    placeholder.markdown(f'''
    <div class="bench">
        <div class="bench-label">The Court</div>
        <div class="bench-content">
            {formatted}{cursor}
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# COUNSEL BOX COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_counsel_box(side: str, messages: list, streaming_content: str = None) -> str:
    """
    Render the complete counsel box with history and streaming area.
    Returns HTML string for the box.
    """
    if side == "plaintiff":
        header_class = "counsel-header counsel-header-plaintiff"
        box_class = "counsel-box counsel-box-plaintiff"
        collapse_class = "argument-collapse argument-collapse-plaintiff"
        header_text = "Plaintiff"
    else:
        header_class = "counsel-header counsel-header-defense"
        box_class = "counsel-box counsel-box-defense"
        collapse_class = "argument-collapse argument-collapse-defense"
        header_text = "Defense"

    # Build argument history
    history_html = ""
    if messages:
        for idx, msg in enumerate(messages):
            content = msg.get('content', '')
            escaped = escape_html(content)

            # Preview: first 100 chars
            preview = escaped[:100].replace('\n', ' ')
            if len(escaped) > 100:
                preview += "..."

            # Full content with line breaks
            full_content = escaped.replace('\n', '<br>')
            round_label = f"Round {idx + 1}"

            history_html += f'''
<details class="{collapse_class}">
<summary>{round_label} &mdash; {preview}</summary>
<div class="argument-collapse-content">{full_content}</div>
</details>'''

    # Streaming or empty state
    streaming_html = ""
    if streaming_content:
        escaped_stream = escape_html(streaming_content).replace('\n', '<br>')
        streaming_html = f'''
<div class="argument-entry animate-in" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.04);">
    <div class="argument-round">Speaking</div>
    <div class="argument-text">{escaped_stream}<span class="typing-cursor"></span></div>
</div>'''
    elif not messages:
        streaming_html = ''

    return f'''
<div class="{box_class}">
    <div class="{header_class}">{header_text}</div>
    <div class="counsel-content">
        {history_html}
        {streaming_html}
    </div>
</div>'''


def render_plaintiff_table_start():
    """Render opening HTML for plaintiff box."""
    st.markdown('''
    <div class="counsel-box counsel-box-plaintiff">
        <div class="counsel-header counsel-header-plaintiff">Plaintiff</div>
        <div class="counsel-content">
    ''', unsafe_allow_html=True)


def render_plaintiff_table_end():
    """Close plaintiff box."""
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_defense_table_start():
    """Render opening HTML for defense box."""
    st.markdown('''
    <div class="counsel-box counsel-box-defense">
        <div class="counsel-header counsel-header-defense">Defense</div>
        <div class="counsel-content">
    ''', unsafe_allow_html=True)


def render_defense_table_end():
    """Close defense box."""
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_counsel_message(content: str, side: str, timestamp: str = "", sender: str = ""):
    """Render a single counsel message."""
    formatted = format_content(content)

    entry_class = f"argument-entry argument-{side}"

    st.markdown(f'''
    <div class="{entry_class} animate-in">
        <div class="argument-text">{formatted}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_counsel_message_streaming(
    placeholder,
    content: str,
    side: str,
    timestamp: str = "",
    sender: str = "",
    is_streaming: bool = True
):
    """Render a streaming message."""
    formatted = format_content(content)
    cursor = '<span class="typing-cursor"></span>' if is_streaming else ""

    entry_class = f"argument-entry argument-{side}"

    placeholder.markdown(f'''
    <div class="{entry_class}">
        <div class="argument-text">{formatted}{cursor}</div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE STAND COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_evidence_stand_start():
    """Render opening HTML for evidence stand."""
    st.markdown('''
    <div class="evidence-box">
        <div class="evidence-header">Evidence</div>
        <div class="evidence-content">
    ''', unsafe_allow_html=True)


def render_evidence_stand_end():
    """Close evidence stand."""
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_evidence_content(content: str):
    """Render evidence content."""
    formatted = format_content(content)
    st.markdown(f'''
    <div class="case-excerpt">
        {formatted}
    </div>
    ''', unsafe_allow_html=True)


def render_case_title(title: str):
    """Render case title banner."""
    st.markdown(f'''
    <div class="case-title-display">{escape_html(title)}</div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# JURY BOX COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_jury_box(jurors: List[JurorDisplay]):
    """Render the jury section with individual juror cards."""
    juror_cards = ""

    for juror in jurors:
        # Determine sentiment
        sentiment_class = get_sentiment_class(juror.score)

        if juror.score > 55:
            fill_class = "sentiment-fill-plaintiff"
            bar_width = juror.score
            leaning_class = "leaning-plaintiff"
            leaning_text = "Plaintiff"
        elif juror.score < 45:
            fill_class = "sentiment-fill-defense"
            bar_width = 100 - juror.score
            leaning_class = "leaning-defense"
            leaning_text = "Defense"
        else:
            fill_class = ""
            bar_width = 0
            leaning_class = "leaning-neutral"
            leaning_text = "Undecided"

        # Clean thought text
        thought = juror.thought
        for prefix in ["THOUGHTS:", "Internal Monologue:", "INTERNAL MONOLOGUE:", "*"]:
            thought = thought.replace(prefix, "").strip()
        if len(thought) > 80:
            thought = thought[:80] + "..."
        thought = escape_html(thought)

        # Get juror number
        juror_num = JUROR_EMOJI_MAP.get(juror.name, str(juror.id))

        juror_cards += f'''
        <div class="juror {sentiment_class}">
            <div class="juror-id">Juror {juror_num}</div>
            <div class="juror-name">{escape_html(juror.name)}</div>
            <div class="juror-role">{escape_html(juror.occupation)}</div>
            <div class="sentiment-track">
                <div class="sentiment-fill {fill_class}" style="width: {bar_width}%;"></div>
            </div>
            <div class="juror-leaning {leaning_class}">{leaning_text}</div>
            <div class="juror-thought">{thought}</div>
        </div>
        '''

    st.markdown(f'''
    <div class="jury-section">
        <div class="jury-label">The Jury</div>
        <div class="jury-grid">
            {juror_cards}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_jury_box_from_scores(
    jury_scores: Dict[str, int],
    juror_personas: Optional[Dict[str, Any]] = None,
    juror_thoughts: Optional[Dict[str, str]] = None
):
    """Render jury box from score dictionary."""
    personas = juror_personas or {}
    thoughts = juror_thoughts or {}

    jurors = []
    for i, (name, score) in enumerate(jury_scores.items(), 1):
        persona = personas.get(name, {})

        if isinstance(persona, dict):
            occupation = persona.get("occupation", JUROR_DATA.get(name, {}).get("occupation", "Juror"))
            thought = persona.get("thought", thoughts.get(name, "Deliberating..."))
        else:
            occupation = JUROR_DATA.get(name, {}).get("occupation", "Juror")
            thought = thoughts.get(name, "Deliberating...")

        jurors.append(JurorDisplay(
            id=i,
            name=name,
            occupation=occupation,
            score=score,
            thought=thought
        ))

    render_jury_box(jurors)


def render_jury_panel(jury_scores: Dict[str, int], average: float, container=None):
    """Render simplified jury panel metrics."""
    target = container or st

    with target:
        st.markdown("### The Jury")

        cols = st.columns(min(len(jury_scores), 6))
        for i, (name, score) in enumerate(jury_scores.items()):
            with cols[i % len(cols)]:
                st.metric(name, f"{score}")

        st.progress(average / 100)
        st.caption(f"Average: {average:.1f} (0=Defense, 100=Plaintiff)")


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_verdict_card(verdict: str, details: str = ""):
    """Render the verdict announcement."""
    details_html = f'<div class="verdict-details">{escape_html(details)}</div>' if details else ""

    st.markdown(f'''
    <div class="verdict-display">
        <div class="verdict-label">Verdict</div>
        <div class="verdict-text">{escape_html(verdict)}</div>
        {details_html}
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY CHAT MESSAGE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_message(msg: dict, container=None):
    """Render a legacy chat message."""
    agent_type = msg.get('agent_type', 'system')
    agent_name = msg.get('agent_name', 'System')
    content = format_content(msg.get('content', ''))
    timestamp = msg.get('timestamp', '')

    # Score display
    score_html = ""
    if msg.get("score") is not None:
        score = msg["score"]
        color = get_score_color(score)
        score_html = f' &mdash; Score: {score}'

    st.markdown(f'''
    <div class="argument-entry animate-in" style="padding: 1rem; background: rgba(20,20,20,0.5); margin-bottom: 0.75rem;">
        <div class="argument-round">{agent_name} &middot; {timestamp}{score_html}</div>
        <div class="argument-text" style="text-align: left; padding-left: 0; border: none;">{content}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_message_streaming(
    agent_type: str,
    agent_name: str,
    content: str,
    timestamp: str,
    is_streaming: bool = True,
    placeholder=None
):
    """Render streaming message."""
    display = format_content(content)
    cursor = '<span class="typing-cursor"></span>' if is_streaming else ""

    html = f'''
    <div class="argument-entry">
        <div class="argument-round">{agent_name} &middot; {timestamp}</div>
        <div class="argument-text" style="text-align: left; padding-left: 0; border: none;">{display}{cursor}</div>
    </div>
    '''

    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    """Escape HTML characters for safe rendering."""
    if not text:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def format_content(text: str) -> str:
    """
    Convert basic markdown to HTML.

    Handles:
        - **bold** -> <strong>
        - *italic* -> <em>
        - newlines -> <br>
    """
    if not text:
        return ""

    # Escape HTML first
    text = escape_html(text)

    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # Newlines
    text = text.replace('\n', '<br>')

    return text


def format_markdown(text: str) -> str:
    """Alias for format_content."""
    return format_content(text)


# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL HELPER COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_streaming_area(content: str, side: str, is_active: bool = True):
    """Render streaming area for active responses."""
    formatted = format_content(content)
    cursor = '<span class="typing-cursor"></span>' if is_active else ""

    label = {
        "plaintiff": "Plaintiff speaking",
        "defense": "Defense speaking",
        "judge": "Court speaking"
    }.get(side, "Speaking")

    st.markdown(f'''
    <div class="argument-entry" style="padding: 1rem; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.04);">
        <div class="streaming-indicator">
            <span class="streaming-dot"></span>
            <span>{label}</span>
        </div>
        <div class="argument-text" style="margin-top: 0.75rem;">{formatted}{cursor}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_control_panel_start(title: str = "Controls"):
    """Render control panel header."""
    st.markdown(f'''
    <div style="background: #141414; border: 1px solid rgba(139,115,85,0.12); padding: 1rem; margin-top: 1rem;">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase; color: #4A4845; margin-bottom: 0.75rem;">{escape_html(title)}</div>
    ''', unsafe_allow_html=True)


def render_control_panel_end():
    """Render control panel footer."""
    st.markdown('</div>', unsafe_allow_html=True)


def render_message_card(
    msg_id: str,
    timestamp: str,
    label: str,
    preview: str,
    side: str,
    is_active: bool = False
) -> str:
    """Generate HTML for a clickable message card."""
    collapse_class = f"argument-collapse argument-collapse-{side}"
    preview_clean = escape_html(preview)[:80]
    if len(preview) > 80:
        preview_clean += "..."

    return f'''
    <details class="{collapse_class}">
        <summary>{escape_html(label)} &mdash; {preview_clean}</summary>
        <div class="argument-collapse-content">{escape_html(preview)}</div>
    </details>
    '''


def render_message_card_list(messages: List[Dict], side: str, expanded_id: Optional[str] = None):
    """Render a list of message cards."""
    cards_html = ""
    for msg in messages:
        cards_html += render_message_card(
            msg_id=msg.get("id", ""),
            timestamp=msg.get("timestamp", ""),
            label=msg.get("label", "Statement"),
            preview=msg.get("content", ""),
            side=side,
            is_active=(msg.get("id") == expanded_id)
        )

    st.markdown(f'''
    <div style="max-height: 300px; overflow-y: auto;">
        {cards_html}
    </div>
    ''', unsafe_allow_html=True)


def render_expanded_transcript(title: str, content: str, msg_id: str):
    """Render expanded transcript view."""
    formatted = format_content(content)

    st.markdown(f'''
    <div style="background: #1A1A1A; border: 1px solid rgba(139,115,85,0.12); padding: 1.5rem; margin-top: 1rem;">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; color: #6B6560; margin-bottom: 1rem;">{escape_html(title)}</div>
        <div style="font-family: 'Spectral', serif; font-size: 0.9rem; line-height: 1.8; color: #EDE8E0;">{formatted}</div>
    </div>
    ''', unsafe_allow_html=True)


def get_juror_emoji(name: str) -> str:
    """Get juror number designation by name."""
    return JUROR_EMOJI_MAP.get(name, "")


def render_counsel_box_header(side: str, icon: str = ""):
    """Render counsel box header."""
    if side == "plaintiff":
        title = "Plaintiff"
        header_class = "counsel-header counsel-header-plaintiff"
    else:
        title = "Defense"
        header_class = "counsel-header counsel-header-defense"

    st.markdown(f'''
    <div class="{header_class}">{title}</div>
    ''', unsafe_allow_html=True)


def render_evidence_box_header():
    """Render evidence header."""
    st.markdown('''
    <div class="evidence-header">Evidence</div>
    ''', unsafe_allow_html=True)


def render_judge_box_header():
    """Render judge bench header."""
    st.markdown('''
    <div class="bench-label">The Court</div>
    ''', unsafe_allow_html=True)
