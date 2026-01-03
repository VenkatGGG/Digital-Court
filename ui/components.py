"""
ui/components.py - LEX UMBRA Courtroom Components

Reusable UI components for the cyber-noir judicial interface.
Implements the spatial courtroom metaphor with distinct zones.
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
    emoji: str
    occupation: str
    score: int  # 0-100 sentiment score
    thought: str  # Latest internal monologue


# Juror emoji mapping - matches names used in app.py JUROR_PERSONAS
JUROR_EMOJI_MAP = {
    "Marcus": "👷",           # Construction Foreman
    "Elena": "👩‍🏫",           # High School Teacher
    "Raymond": "👨‍💼",         # Retired Accountant
    "Destiny": "👩‍⚕️",         # ER Nurse
    "Chen": "👨‍🔬",            # Software Engineer
    "Patricia": "👵",         # Former Judge
}


# ═══════════════════════════════════════════════════════════════════════════════
# ZONE A: HEADER COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header(case_id: str = "LU-2024-00000"):
    """
    Render Zone A: The application header with title and status bar.

    Args:
        case_id: The current case identifier
    """
    st.markdown('<h1 class="main-title">LEX UMBRA</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="main-subtitle">Autonomous Judicial Simulation</p>',
        unsafe_allow_html=True
    )


def render_status_bar(phase: str, case_id: str, session_status: str = "ACTIVE"):
    """
    Render the prominent trial status banner at top center.

    Args:
        phase: Current trial phase name
        case_id: Case identifier
        session_status: Session status (ACTIVE, PAUSED, etc.)
    """
    # Determine status icon and color based on phase
    phase_icon = "⚖️"
    if "AWAITING" in phase:
        phase_icon = "📋"
    elif "OPENING" in phase:
        phase_icon = "🎬"
    elif "ARGUMENT" in phase:
        phase_icon = "⚔️"
    elif "DELIBERATION" in phase:
        phase_icon = "🤔"
    elif "VERDICT" in phase:
        phase_icon = "📜"
    elif "ADJOURNED" in phase:
        phase_icon = "🔒"

    session_icon = "🟢" if session_status == "ACTIVE" else "🟡" if session_status == "PROCESSING" else "⚪"

    st.markdown(f'''
    <div class="trial-status-banner">
        <div class="status-phase-main">
            <span class="phase-icon">{phase_icon}</span>
            <span class="phase-text">{phase}</span>
        </div>
        <div class="status-details">
            <div class="status-item">
                <span class="status-label">Case</span>
                <span class="status-value">{case_id}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Status</span>
                <span class="status-value">{session_icon} {session_status}</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ZONE B: JUDGE'S BENCH COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_judge_bench(instruction: str, glow: bool = True):
    """
    Render Zone B: The Judge's Bench - dominant authority display.

    Args:
        instruction: Current judge instruction/statement
        glow: Whether to apply the animated glow effect
    """
    glow_class = "glow-effect" if glow else ""

    # Convert markdown formatting
    formatted = format_content(instruction)

    st.markdown(f'''
    <div class="judge-bench {glow_class}">
        <div class="judge-header">The Honorable Court Presiding</div>
        <div class="judge-content">
            {formatted}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_judge_instruction_streaming(placeholder, content: str, is_streaming: bool = True):
    """
    Render judge instruction with streaming cursor effect.

    Args:
        placeholder: Streamlit placeholder to update
        content: Current content
        is_streaming: Whether still streaming
    """
    cursor = '<span class="typing-indicator">▌</span>' if is_streaming else ""
    formatted = format_content(content)

    placeholder.markdown(f'''
    <div class="judge-bench pulse-border">
        <div class="judge-header">The Honorable Court Presiding</div>
        <div class="judge-content">
            {formatted}{cursor}
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ZONE C: COUNSEL TABLE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_plaintiff_table_start():
    """Render the opening HTML for plaintiff counsel table."""
    st.markdown('''
    <div class="counsel-table plaintiff-table">
        <div class="plaintiff-header">Plaintiff Counsel</div>
        <div class="counsel-messages">
    ''', unsafe_allow_html=True)


def render_plaintiff_table_end():
    """Render the closing HTML for plaintiff counsel table."""
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_defense_table_start():
    """Render the opening HTML for defense counsel table."""
    st.markdown('''
    <div class="counsel-table defense-table">
        <div class="defense-header">Defense Counsel</div>
        <div class="counsel-messages">
    ''', unsafe_allow_html=True)


def render_defense_table_end():
    """Render the closing HTML for defense counsel table."""
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_counsel_message(content: str, side: str, timestamp: str = "", sender: str = ""):
    """
    Render a message in the counsel table.

    Args:
        content: Message content
        side: "plaintiff" or "defense"
        timestamp: Optional timestamp
        sender: Optional sender name
    """
    message_class = f"{side}-message"
    formatted = format_content(content)

    sender_html = f'<div class="message-sender">{sender}</div>' if sender else ""
    time_html = f'<div class="message-time">⏱ {timestamp}</div>' if timestamp else ""

    st.markdown(f'''
    <div class="counsel-message {message_class} animate-in">
        {sender_html}
        {formatted}
        {time_html}
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
    """
    Render a streaming message in counsel table.

    Args:
        placeholder: Streamlit placeholder
        content: Current content
        side: "plaintiff" or "defense"
        timestamp: Message timestamp
        sender: Sender name
        is_streaming: Whether still streaming
    """
    message_class = f"{side}-message"
    formatted = format_content(content)
    cursor = '<span class="typing-indicator">▌</span>' if is_streaming else ""

    sender_html = f'<div class="message-sender">{sender}</div>' if sender else ""
    time_html = f'<div class="message-time">⏱ {timestamp}</div>' if timestamp else ""

    placeholder.markdown(f'''
    <div class="counsel-message {message_class}">
        {sender_html}
        {formatted}{cursor}
        {time_html}
    </div>
    ''', unsafe_allow_html=True)


def render_evidence_stand_start():
    """Render the opening HTML for evidence stand."""
    st.markdown('''
    <div class="evidence-stand">
        <div class="evidence-header">Evidence Stand</div>
    ''', unsafe_allow_html=True)


def render_evidence_stand_end():
    """Render the closing HTML for evidence stand."""
    st.markdown('</div>', unsafe_allow_html=True)


def render_evidence_content(content: str):
    """
    Render evidence/case facts content.

    Args:
        content: The evidence or case facts text
    """
    formatted = format_content(content)
    st.markdown(f'''
    <div class="evidence-content">
        {formatted}
    </div>
    ''', unsafe_allow_html=True)


def render_case_title(title: str):
    """
    Render a case title banner.

    Args:
        title: The case title
    """
    st.markdown(f'''
    <div class="case-title">{escape_html(title)}</div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ZONE D: JURY BOX COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_jury_box(jurors: List[JurorDisplay]):
    """
    Render Zone D: The Jury Box with individual juror cards.

    Args:
        jurors: List of JurorDisplay objects
    """
    juror_cards_html = ""
    for juror in jurors:
        juror_cards_html += _render_juror_card_html(juror)

    st.markdown(f'''
    <div class="jury-box">
        <div class="jury-header">The Jury Box</div>
        <div class="juror-grid">
            {juror_cards_html}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def _render_juror_card_html(juror: JurorDisplay) -> str:
    """
    Generate HTML for a single juror card.

    Args:
        juror: JurorDisplay object

    Returns:
        HTML string for the juror card
    """
    # Determine leaning
    leaning_class = get_sentiment_class(juror.score)

    if juror.score > 55:
        sentiment_class = "plaintiff-leaning"
        bar_width = juror.score
    elif juror.score < 45:
        sentiment_class = "defense-leaning"
        bar_width = 100 - juror.score
    else:
        sentiment_class = ""
        bar_width = 50

    # Sentiment label
    if juror.score > 60:
        sentiment_label = "Favors Plaintiff"
    elif juror.score < 40:
        sentiment_label = "Favors Defense"
    else:
        sentiment_label = "Undecided"

    # Clean up the thought - remove internal monologue prefixes
    thought_clean = juror.thought
    for prefix in ["THOUGHTS:", "Internal Monologue:", "INTERNAL MONOLOGUE:", "*"]:
        thought_clean = thought_clean.replace(prefix, "").strip()
    
    # Truncate if too long
    if len(thought_clean) > 120:
        thought_clean = thought_clean[:120] + "..."
    
    thought_escaped = escape_html(thought_clean)

    return f'''
    <div class="juror-card {leaning_class}">
        <div class="juror-avatar">{juror.emoji}</div>
        <div class="juror-name">{escape_html(juror.name)}</div>
        <div class="juror-occupation">{escape_html(juror.occupation)}</div>
        <div class="sentiment-container">
            <div class="sentiment-bar-bg">
                <div class="sentiment-bar {sentiment_class}" style="width: {bar_width}%;"></div>
            </div>
            <div class="sentiment-label">{sentiment_label}</div>
        </div>
        <div class="thought-bubble">{thought_escaped}</div>
    </div>
    '''


def render_jury_panel(jury_scores: Dict[str, int], average: float, container=None):
    """
    Render the jury panel status display (simplified metrics view).

    Args:
        jury_scores: Dict of {juror_name: score}
        average: Average jury score
        container: Optional Streamlit container
    """
    target = container or st

    with target:
        st.markdown("### The Jury Box")

        # Create juror grid
        cols = st.columns(min(len(jury_scores), 6))
        for i, (name, score) in enumerate(jury_scores.items()):
            with cols[i % len(cols)]:
                # Determine icon based on score
                if score > 60:
                    icon = "🔴"
                elif score < 40:
                    icon = "🔵"
                else:
                    icon = "⚪"
                st.metric(f"{icon} {name}", f"{score}/100")

        # Progress bar showing average
        st.progress(average / 100)
        st.caption(f"Average Sentiment: {average:.1f}/100 • (0 = Defense, 100 = Plaintiff)")


def render_jury_box_from_scores(
    jury_scores: Dict[str, int],
    juror_personas: Optional[Dict[str, Any]] = None,
    juror_thoughts: Optional[Dict[str, str]] = None
):
    """
    Render jury box from score dictionary with dynamic emoji lookup.

    Args:
        jury_scores: Dict of {juror_name: score}
        juror_personas: Optional dict of {juror_name: {emoji, occupation, thought}}
        juror_thoughts: Optional dict of {juror_name: thought} (alternative format)
    """
    personas = juror_personas or {}
    thoughts = juror_thoughts or {}

    jurors = []
    for i, (name, score) in enumerate(jury_scores.items(), 1):
        # Check if personas is in old format (dict of dicts)
        persona = personas.get(name, {})
        
        if isinstance(persona, dict):
            # Old format: {name: {emoji, occupation, thought}}
            emoji = persona.get("emoji") or JUROR_EMOJI_MAP.get(name, "👤")
            occupation = persona.get("occupation", "Juror")
            thought = persona.get("thought", thoughts.get(name, "Deliberating..."))
        else:
            # New format or no persona provided
            emoji = JUROR_EMOJI_MAP.get(name, "👤")
            occupation = "Juror"
            thought = thoughts.get(name, "Deliberating...")
        
        jurors.append(JurorDisplay(
            id=i,
            name=name,
            emoji=emoji,
            occupation=occupation,
            score=score,
            thought=thought
        ))

    render_jury_box(jurors)


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY CHAT MESSAGE COMPONENTS (Backward Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

def render_message(msg: dict, container=None):
    """
    Render a chat message with appropriate styling.

    Args:
        msg: Message dict with agent_type, agent_name, content, timestamp, score
        container: Optional Streamlit container to render in
    """
    css_class = f"{msg.get('agent_type', 'system')}-msg"

    # Score badge
    score_html = ""
    if msg.get("score") is not None:
        score = msg["score"]
        color = get_score_color(score)
        score_html = f'<span class="score-badge" style="color: {color};">Score: {score}/100</span>'

    # Format content
    content = msg.get('content', '')
    content = format_content(content)

    html = f"""
    <div class="chat-message {css_class} animate-in">
        <div class="agent-name">{msg.get('agent_name', 'SYSTEM')} • {msg.get('timestamp', '')}{score_html}</div>
        <div>{content}</div>
    </div>
    """

    if container:
        with container:
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_message_streaming(
    agent_type: str,
    agent_name: str,
    content: str,
    timestamp: str,
    is_streaming: bool = True,
    placeholder=None
):
    """
    Render a message during streaming with optional cursor.

    Args:
        agent_type: Type of agent (plaintiff, defense, etc.)
        agent_name: Display name
        content: Current content
        timestamp: Message timestamp
        is_streaming: If True, shows blinking cursor
        placeholder: Streamlit placeholder to update
    """
    css_class = f"{agent_type}-msg"
    display = format_content(content)

    cursor = '<span class="typing-indicator">▌</span>' if is_streaming else ""

    html = f"""
    <div class="chat-message {css_class}">
        <div class="agent-name">{agent_name} • {timestamp}</div>
        <div>{display}{cursor}</div>
    </div>
    """

    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_verdict_card(verdict: str, details: str = ""):
    """
    Render the final verdict announcement card.

    Args:
        verdict: The verdict text (e.g., "PLAINTIFF PREVAILS")
        details: Additional verdict details
    """
    details_html = f'<div style="margin-top: 1rem; font-size: 0.9rem; color: #94a3b8;">{escape_html(details)}</div>' if details else ""

    st.markdown(f'''
    <div class="verdict-card">
        <div class="verdict-text">{escape_html(verdict)}</div>
        {details_html}
    </div>
    ''', unsafe_allow_html=True)


def render_control_panel_start(title: str = "Simulation Controls"):
    """Render control panel header."""
    st.markdown(f'''
    <div class="control-panel">
        <div class="control-header">{escape_html(title)}</div>
    ''', unsafe_allow_html=True)


def render_control_panel_end():
    """Render control panel footer."""
    st.markdown('</div>', unsafe_allow_html=True)


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
    Convert basic markdown to HTML for display.

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
    """Alias for format_content for backward compatibility."""
    return format_content(text)


# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGE CARDS & COLLAPSIBLE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_message_card(
    msg_id: str,
    timestamp: str,
    label: str,
    preview: str,
    side: str,
    is_active: bool = False
) -> str:
    """
    Generate HTML for a clickable message card.
    
    Args:
        msg_id: Unique message identifier
        timestamp: Message timestamp
        label: Card label (e.g., "Opening Statement")
        preview: Preview text (truncated)
        side: "plaintiff", "defense", or "juror"
        is_active: Whether this card is currently expanded
    
    Returns:
        HTML string for the card
    """
    card_class = f"{side}-card"
    active_class = "active" if is_active else ""
    preview_clean = escape_html(preview)[:80]
    if len(preview) > 80:
        preview_clean += "..."
    
    return f'''
    <div class="message-card {card_class} {active_class}" data-msg-id="{msg_id}">
        <div class="card-header">
            <span class="card-label">{escape_html(label)}</span>
            <span class="card-time">{timestamp}</span>
        </div>
        <div class="card-preview">{preview_clean}</div>
        <div class="card-expand-hint">Click to expand</div>
    </div>
    '''


def render_message_card_list(messages: List[Dict], side: str, expanded_id: Optional[str] = None):
    """
    Render a scrollable list of message cards.
    
    Args:
        messages: List of message dicts with id, timestamp, label, content
        side: "plaintiff", "defense", or "juror"
        expanded_id: Currently expanded message ID
    """
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
    <div class="message-card-list">
        {cards_html}
    </div>
    ''', unsafe_allow_html=True)


def render_streaming_area(content: str, side: str, is_active: bool = True):
    """
    Render the streaming area for active responses.
    
    Args:
        content: Current streamed content
        side: "plaintiff", "defense", or "judge"
        is_active: Whether streaming is active
    """
    active_class = "active" if is_active else ""
    stream_class = f"{side}-stream" if side in ["plaintiff", "defense"] else ""
    formatted = format_content(content)
    cursor = '<span class="typing-indicator">▌</span>' if is_active else ""
    
    label = {
        "plaintiff": "Plaintiff Speaking...",
        "defense": "Defense Speaking...",
        "judge": "Court Speaking..."
    }.get(side, "Speaking...")
    
    st.markdown(f'''
    <div class="streaming-area {active_class} {stream_class}">
        <div class="streaming-label">{label}</div>
        <div class="streaming-content">{formatted}{cursor}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_expanded_transcript(title: str, content: str, msg_id: str):
    """
    Render the expanded transcript view below a message card.
    
    Args:
        title: Title for the expanded view
        content: Full message content
        msg_id: Message ID (for close button)
    """
    formatted = format_content(content)
    
    st.markdown(f'''
    <div class="expanded-transcript">
        <div class="expanded-header">
            <span class="expanded-title">{escape_html(title)}</span>
            <span class="expanded-close" data-close-id="{msg_id}">Close</span>
        </div>
        <div class="expanded-content">{formatted}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_counsel_box_header(side: str, icon: str = ""):
    """
    Render counsel box header with icon.
    
    Args:
        side: "plaintiff" or "defense"
        icon: Optional emoji icon
    """
    if side == "plaintiff":
        icon = icon or "🔴"
        title = "Plaintiff Counsel"
        header_class = "plaintiff-header"
    else:
        icon = icon or "🔵"
        title = "Defense Counsel"
        header_class = "defense-header"
    
    st.markdown(f'''
    <div class="{header_class} counsel-header-with-icon">
        <span class="header-icon">{icon}</span>
        <span>{title}</span>
    </div>
    ''', unsafe_allow_html=True)


def render_evidence_box_header():
    """Render evidence stand header with icon."""
    st.markdown('''
    <div class="evidence-header counsel-header-with-icon">
        <span class="header-icon">📁</span>
        <span>Evidence Stand</span>
    </div>
    ''', unsafe_allow_html=True)


def render_judge_box_header():
    """Render judge bench header with icon."""
    st.markdown('''
    <div class="judge-header counsel-header-with-icon">
        <span class="header-icon">⚖️</span>
        <span>The Honorable Court Presiding</span>
    </div>
    ''', unsafe_allow_html=True)

def get_juror_emoji(name: str) -> str:
    """Get emoji for a juror by name."""
    return JUROR_EMOJI_MAP.get(name, "👤")


# ═══════════════════════════════════════════════════════════════════════════════
# FULL COUNSEL BOX RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def render_counsel_box(side: str, messages: list, streaming_content: str = None) -> str:
    """
    Render the complete counsel box HTML including header, history cards, and streaming area.
    This ensures all content stays visually contained within the bordered box.
    """
    if side == "plaintiff":
        header_html = '<div class="plaintiff-header">🔴 Plaintiff Counsel</div>'
        box_class = "counsel-table plaintiff-table"
        card_class = "argument-card plaintiff-card"
        agent_name = "ATTORNEY CHEN (Plaintiff)"
    else:
        header_html = '<div class="defense-header">Defense Counsel 🔵</div>'
        box_class = "counsel-table defense-table"
        card_class = "argument-card defense-card"
        agent_name = "ATTORNEY WEBB (Defense)"
        
    # 1. Build History HTML
    history_items = []
    if messages:
        for idx, msg in enumerate(messages):
            content = msg.get('content', '')
            
            # Escape HTML
            escaped_content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Create preview (first 80 chars)
            preview = escaped_content[:80].replace('\n', ' ') + "..." if len(escaped_content) > 80 else escaped_content.replace('\n', ' ')
            
            # Full content with BRs
            full_content = escaped_content.replace('\n', '<br>')
            round_label = f"Round {idx + 1}"
            
            # item_html: flush left
            item_html = f'''
<details class="{card_class}">
<summary>📜 {round_label}: {preview}</summary>
<div class="argument-full">{full_content}</div>
</details>'''
            history_items.append(item_html)
            
    history_html = "\n".join(history_items)
            
    # 2. Build Streaming/Latest HTML
    streaming_html = ""
    if streaming_content:
        # Active streaming
        import time
        escaped_stream = streaming_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        streaming_html = f'''
<div class="counsel-message {side}-message" style="margin-top: 1rem; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 1rem;">
<div class="message-sender">{agent_name} (Streaming...)</div>
<div class="streaming-text">{escaped_stream}</div>
</div>'''
    elif not messages:
        # Empty state
        streaming_html = '<div style="color: #64748b; font-style: italic; padding: 2rem; text-align: center;">Awaiting opening statements...</div>'
        
    return f'''
<div class="{box_class}" style="min-height: 400px; display: flex; flex-direction: column;">
{header_html}
<div class="message-card-list" style="flex: 1; overflow-y: auto; max-height: 300px;">
{history_html}
</div>
<div class="streaming-area">
{streaming_html}
</div>
</div>'''
