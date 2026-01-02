"""
LEX UMBRA: Autonomous Judicial Simulation
═════════════════════════════════════════
The Digital Courtroom Interface - Cyber-Noir Edition

A high-tech judicial control center that spatially mimics a real courtroom.
"""

import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

# Package imports
from config.settings import get_settings
from config.prompts import Prompts
from orchestrator import TrialOrchestrator, TrialPhase
from ui.styles import get_css
from ui.components import (
    render_header,
    render_status_bar,
    render_judge_bench,
    render_message,
    render_jury_panel,
    render_jury_box_from_scores,
    render_verdict_card,
    render_case_title,
    JurorDisplay,
    render_jury_box,
    JUROR_EMOJI_MAP,
)
from ui.handlers import stream_response, extract_pdf_text


# ═══════════════════════════════════════════════════════════════════════════════
# JUROR PERSONA MAPPING (Used for both Demo and Main modes)
# ═══════════════════════════════════════════════════════════════════════════════

JUROR_PERSONAS = {
    "Marcus": {"emoji": "👷", "occupation": "Construction Foreman"},
    "Elena": {"emoji": "👩‍🏫", "occupation": "High School Teacher"},
    "Raymond": {"emoji": "👨‍💼", "occupation": "Retired Accountant"},
    "Destiny": {"emoji": "👩‍⚕️", "occupation": "ER Nurse"},
    "Chen": {"emoji": "👨‍🔬", "occupation": "Software Engineer"},
    "Patricia": {"emoji": "👵", "occupation": "Former Judge"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK DATA FOR DEMO MODE
# ═══════════════════════════════════════════════════════════════════════════════

MOCK_PLAINTIFF_MESSAGES = [
    {"agent_type": "plaintiff", "agent_name": "ATTORNEY CHEN", "timestamp": "09:15:32",
     "content": "Your Honor, members of the jury—the evidence will show a clear pattern of negligence that resulted in catastrophic damages to my client."},
    {"agent_type": "plaintiff", "agent_name": "ATTORNEY CHEN", "timestamp": "09:18:45",
     "content": "Exhibit A demonstrates that the defendant was explicitly warned about these risks THREE TIMES before the incident occurred."},
    {"agent_type": "plaintiff", "agent_name": "ATTORNEY CHEN", "timestamp": "09:22:11",
     "content": "We intend to prove, beyond any reasonable doubt, that this was not an accident—it was willful disregard for human safety."},
]

MOCK_DEFENSE_MESSAGES = [
    {"agent_type": "defense", "agent_name": "ATTORNEY WEBB", "timestamp": "09:16:08",
     "content": "Your Honor, the plaintiff's case rests on circumstantial evidence and emotional appeals rather than facts."},
    {"agent_type": "defense", "agent_name": "ATTORNEY WEBB", "timestamp": "09:19:55",
     "content": "My client followed every protocol mandated by industry standards. The so-called 'warnings' were routine compliance notices."},
    {"agent_type": "defense", "agent_name": "ATTORNEY WEBB", "timestamp": "09:23:40",
     "content": "We will demonstrate that the plaintiff's own actions contributed significantly to the outcome they now attribute to my client."},
]

MOCK_CASE_FACTS = """**CASE SUMMARY: Meridian Corp v. Sullivan**

**Plaintiff:** Meridian Corporation
**Defendant:** James Sullivan, Former CTO

**Core Allegation:** Breach of fiduciary duty and misappropriation of trade secrets following defendant's departure to competitor firm.

**Key Evidence:**
- Email correspondence dated March 2024
- Server access logs showing unusual download patterns
- Witness testimony from 3 former colleagues
- Financial records showing competitor's accelerated timeline

**Damages Sought:** $4.2 Million + Injunctive Relief"""

MOCK_JUROR_DATA = [
    {"name": "Marcus", "score": 45, "thought": "The defense seems unprepared..."},
    {"name": "Elena", "score": 62, "thought": "Those documents are damning."},
    {"name": "Raymond", "score": 38, "thought": "I need to see the numbers myself."},
    {"name": "Destiny", "score": 55, "thought": "Both sides make valid points."},
    {"name": "Chen", "score": 48, "thought": "The timeline doesn't add up."},
    {"name": "Patricia", "score": 52, "thought": "Counsel is grandstanding again."},
]


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

settings = get_settings()

st.set_page_config(
    page_title="LEX UMBRA | Autonomous Judicial Simulation",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS
st.markdown(get_css(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize all session state variables."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = TrialOrchestrator()
    if "upload_processed" not in st.session_state:
        st.session_state.upload_processed = False
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "case_id" not in st.session_state:
        st.session_state.case_id = f"LU-{time.strftime('%Y')}-{hash(time.time()) % 100000:05d}"
    if "juror_thoughts" not in st.session_state:
        st.session_state.juror_thoughts = {}
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False
    if "demo_jurors" not in st.session_state:
        st.session_state.demo_jurors = [j.copy() for j in MOCK_JUROR_DATA]
    if "expanded_message" not in st.session_state:
        st.session_state.expanded_message = None


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


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_phase_display_name(phase: TrialPhase) -> str:
    """Get display name for trial phase."""
    phase_names = {
        TrialPhase.AWAITING_COMPLAINT: "AWAITING CASE",
        TrialPhase.COURT_ASSEMBLED: "COURT ASSEMBLED",
        TrialPhase.OPENING_STATEMENTS: "OPENING STATEMENTS",
        TrialPhase.ARGUMENTS: "ARGUMENTS",
        TrialPhase.JURY_DELIBERATION: "DELIBERATION",
        TrialPhase.VERDICT: "VERDICT",
        TrialPhase.ADJOURNED: "ADJOURNED",
    }
    return phase_names.get(phase, phase.value)


def get_case_summary(case_facts: str, max_length: int = 500) -> str:
    """Extract a summary from case facts."""
    if not case_facts:
        return "No case loaded."
    summary = case_facts[:max_length]
    if len(case_facts) > max_length:
        summary += "..."
    return summary


def get_latest_judge_message(orch) -> str:
    """Get the most recent judge message from transcript."""
    transcript = orch.get_transcript()
    judge_msgs = [m for m in transcript if m.get('agent_type') == 'judge']
    if judge_msgs:
        return judge_msgs[-1].get('content', '')
    return None


def build_juror_personas(orch) -> dict:
    """Build juror persona dict from orchestrator."""
    if not orch.jury or not orch.jury.jurors:
        return {}

    personas = {}
    for juror in orch.jury.jurors:
        name = juror.name
        persona_info = JUROR_PERSONAS.get(name, {"emoji": "👤", "occupation": "Juror"})
        personas[name] = {
            "emoji": persona_info["emoji"],
            "occupation": persona_info["occupation"],
            "thought": st.session_state.juror_thoughts.get(name, "Awaiting deliberation...")
        }

    return personas


def render_message_card(msg: dict, side: str, show_full: bool = False):
    """Render a clickable message card in counsel table."""
    content = msg.get('content', '')
    msg_id = f"{side}_{msg.get('timestamp', '')}_{hash(content[:20]) if content else 0}"

    # Truncate if not expanded
    display_content = content
    is_truncated = False
    if not show_full and len(content) > 250:
        display_content = content[:250] + "..."
        is_truncated = True

    # Escape HTML
    display_content = display_content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')

    message_class = f"{side}-message"

    st.markdown(f'''
    <div class="counsel-message {message_class}" style="cursor: {'pointer' if is_truncated else 'default'};">
        <div class="message-sender">{msg.get('agent_name', '')}</div>
        {display_content}
        <div class="message-time">⏱ {msg.get('timestamp', '')}</div>
        {'<div style="color: #C5A059; font-size: 0.7rem; margin-top: 0.5rem;">Click to expand...</div>' if is_truncated else ''}
    </div>
    ''', unsafe_allow_html=True)

    return is_truncated, msg_id


# ═══════════════════════════════════════════════════════════════════════════════
# STREAMING FUNCTIONS (Stream into appropriate columns)
# ═══════════════════════════════════════════════════════════════════════════════

def stream_to_placeholder(placeholder, agent, prompt, agent_type, agent_name):
    """Stream response to a placeholder with typing effect."""
    response = ""
    message_class = f"{agent_type}-message"

    try:
        for chunk in agent.generate_stream(prompt):
            response += chunk
            display = response.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            placeholder.markdown(f'''
            <div class="counsel-message {message_class}">
                <div class="message-sender">{agent_name}</div>
                {display}<span style="animation: blink 1s infinite;">▌</span>
                <div class="message-time">⏱ {time.strftime("%H:%M:%S")}</div>
            </div>
            <style>@keyframes blink {{ 0%, 50% {{ opacity: 1; }} 51%, 100% {{ opacity: 0; }} }}</style>
            ''', unsafe_allow_html=True)
    except Exception as e:
        # Fallback to non-streaming
        response = agent.generate(prompt)

    # Final render without cursor
    display = response.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
    placeholder.markdown(f'''
    <div class="counsel-message {message_class}">
        <div class="message-sender">{agent_name}</div>
        {display}
        <div class="message-time">⏱ {time.strftime("%H:%M:%S")}</div>
    </div>
    ''', unsafe_allow_html=True)

    return response


# ═══════════════════════════════════════════════════════════════════════════════
# TRIAL PHASE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def run_opening_statements(orch, plaintiff_placeholder, defense_placeholder, judge_placeholder):
    """Execute opening statements with streaming to appropriate columns."""

    # Judge opens
    judge_content = orch.judge.open_court(orch.case_title)
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Plaintiff streams
    prompt = Prompts.PLAINTIFF_OPENING.format(case_facts=orch.case_facts)
    response = stream_to_placeholder(
        plaintiff_placeholder,
        orch.plaintiff_lawyer,
        prompt,
        "plaintiff",
        "ATTORNEY CHEN (Plaintiff)"
    )
    orch._add_to_transcript("plaintiff", "ATTORNEY CHEN (Plaintiff)", response)

    # Judge transition
    judge_content = Prompts.JUDGE_TRANSITION_TO_DEFENSE
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Defense streams
    prompt = Prompts.DEFENSE_OPENING.format(case_facts=orch.case_facts)
    response = stream_to_placeholder(
        defense_placeholder,
        orch.defense_lawyer,
        prompt,
        "defense",
        "ATTORNEY WEBB (Defense)"
    )
    orch._add_to_transcript("defense", "ATTORNEY WEBB (Defense)", response)

    # Conclude
    judge_content = Prompts.JUDGE_OPENINGS_COMPLETE
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    orch.start_arguments()


def run_argument_round(orch, plaintiff_placeholder, defense_placeholder, judge_placeholder):
    """Execute one round of arguments with bidirectional context."""

    round_num = orch.current_round

    # Judge announces round
    judge_content = Prompts.JUDGE_ARGUMENT_ROUND.format(round_num=round_num)
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Get previous arguments from both sides
    plaintiff_msgs = [m for m in orch.transcript if m.agent_type == "plaintiff"]
    defense_msgs = [m for m in orch.transcript if m.agent_type == "defense"]
    
    # Plaintiff argument - with context from both sides
    if round_num == 1:
        prompt = Prompts.PLAINTIFF_MAIN_ARGUMENT.format(case_facts=orch.case_facts)
    else:
        last_defense = defense_msgs[-1].content if defense_msgs else ""
        last_plaintiff = plaintiff_msgs[-1].content if plaintiff_msgs else ""
        prompt = Prompts.PLAINTIFF_ARGUMENT_WITH_CONTEXT.format(
            plaintiff_previous=last_plaintiff[:400],
            defense_argument=last_defense[:400]
        )

    plaintiff_response = stream_to_placeholder(
        plaintiff_placeholder,
        orch.plaintiff_lawyer,
        prompt,
        "plaintiff",
        "ATTORNEY CHEN (Plaintiff)"
    )
    orch._add_to_transcript("plaintiff", "ATTORNEY CHEN (Plaintiff)", plaintiff_response)

    # Judge transition
    judge_content = Prompts.JUDGE_DEFENSE_RESPOND
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Defense rebuttal - with context from both sides
    last_defense = defense_msgs[-1].content if defense_msgs else ""
    prompt = Prompts.DEFENSE_ARGUMENT_WITH_CONTEXT.format(
        plaintiff_argument=plaintiff_response[:400],
        defense_previous=last_defense[:400]
    )
    
    defense_response = stream_to_placeholder(
        defense_placeholder,
        orch.defense_lawyer,
        prompt,
        "defense",
        "ATTORNEY WEBB (Defense)"
    )
    orch._add_to_transcript("defense", "ATTORNEY WEBB (Defense)", defense_response)

    orch.advance_round()


def run_jury_deliberation(orch, judge_placeholder):
    """Execute parallel jury deliberation."""

    # Judge instructs jury
    judge_content = Prompts.JUDGE_JURY_DELIBERATE
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    context = orch.get_recent_arguments(4)

    # Progress indicator
    progress_placeholder = st.empty()
    progress_placeholder.info("⏳ All jurors are deliberating simultaneously...")

    def get_juror_response(juror):
        prompt = Prompts.JUROR_DELIBERATION.format(context=context, juror_name=juror.name)
        response = juror.generate(prompt)

        score = juror.current_bias_score
        for line in response.split('\n'):
            if 'SCORE:' in line.upper():
                try:
                    score = int(''.join(filter(str.isdigit, line.split(':')[-1].strip()[:3])))
                    score = max(0, min(100, score))
                    juror.current_bias_score = score
                except:
                    pass

        return {"juror": juror, "response": response, "score": score}

    results = []
    with ThreadPoolExecutor(max_workers=settings.parallel_jury_workers) as executor:
        futures = {executor.submit(get_juror_response, j): j for j in orch.jury.jurors}

        completed = 0
        for future in as_completed(futures):
            completed += 1
            progress_placeholder.info(f"⏳ Jurors deliberating... ({completed}/{orch.jury.size} complete)")
            results.append(future.result())

    progress_placeholder.empty()

    # Store thoughts for jury box display
    for result in results:
        juror = result["juror"]
        thought = result["response"][:80] + "..." if len(result["response"]) > 80 else result["response"]
        st.session_state.juror_thoughts[juror.name] = thought
        orch._add_to_transcript("juror", f"JUROR: {juror.name}", result["response"], result["score"])

    orch.start_jury_deliberation()


def run_verdict(orch, judge_placeholder):
    """Render final verdict."""

    # Judge pre-verdict
    judge_content = Prompts.JUDGE_PRE_VERDICT
    orch._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Summary
    context = orch.get_recent_arguments(4)
    prompt = Prompts.JUDGE_SUMMARY_PROMPT.format(context=context)
    summary = orch.judge.generate(prompt)
    orch._add_to_transcript("judge", "JUDGE MARSHALL", summary)

    # Verdict
    verdict_info = orch.jury.get_verdict()
    avg = verdict_info["average_score"]

    if verdict_info["verdict"] == "PLAINTIFF":
        verdict_text = f"VERDICT: PLAINTIFF PREVAILS\n\nDamages Awarded: ${verdict_info['damages']:,}"
    elif verdict_info["verdict"] == "DEFENSE":
        verdict_text = "VERDICT: DEFENSE PREVAILS\n\nCase Dismissed"
    else:
        verdict_text = "VERDICT: HUNG JURY\n\nMistrial Declared"

    scores = [f"{n}: {s}" for n, s in verdict_info["individual_scores"].items()]
    final_content = f"{summary}\n\n**{verdict_text}**\n\nJury Score: {avg:.1f}/100\nBreakdown: {', '.join(scores)}"

    update_judge_bench(judge_placeholder, final_content)
    orch._add_to_transcript("judge", "JUDGE MARSHALL", verdict_text)

    orch.adjourn()


def run_autonomous_trial(orch, plaintiff_placeholder, defense_placeholder, judge_placeholder):
    """Run the complete autonomous trial - agents debate until done, then jury deliberates."""
    
    # Progress display
    progress_container = st.empty()
    status_container = st.empty()
    
    # Run the autonomous debate
    for update in orch.run_autonomous_debate():
        event_type = update.get("type")
        
        if event_type == "judge":
            update_judge_bench(judge_placeholder, update.get("content", ""))
            
        elif event_type == "round_start":
            round_num = update.get("round", 1)
            progress_container.info(f"⚔️ Round {round_num} - Counsel are debating...")
            
        elif event_type == "plaintiff_speaking":
            status_container.markdown("🔴 **Plaintiff speaking...**")
            
        elif event_type == "plaintiff_done":
            content = update.get("content", "")
            display = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            plaintiff_placeholder.markdown(f'''
            <div class="counsel-message plaintiff-message">
                <div class="message-sender">ATTORNEY CHEN (Plaintiff)</div>
                {display}
                <div class="message-time">⏱ {time.strftime("%H:%M:%S")}</div>
            </div>
            ''', unsafe_allow_html=True)
            
        elif event_type == "defense_speaking":
            status_container.markdown("🔵 **Defense responding...**")
            
        elif event_type == "defense_done":
            content = update.get("content", "")
            display = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            defense_placeholder.markdown(f'''
            <div class="counsel-message defense-message">
                <div class="message-sender">ATTORNEY WEBB (Defense)</div>
                {display}
                <div class="message-time">⏱ {time.strftime("%H:%M:%S")}</div>
            </div>
            ''', unsafe_allow_html=True)
            
        elif event_type == "round_complete":
            round_num = update.get("round", 1)
            reason = update.get("reason", "")
            should_continue = update.get("should_continue", True)
            
            if should_continue:
                status_container.success(f"✓ Round {round_num} complete. {reason}")
            else:
                status_container.success(f"✓ Round {round_num} complete. Debate concluded: {reason}")
                
        elif event_type == "debate_complete":
            total_rounds = update.get("total_rounds", 1)
            progress_container.success(f"✅ Debate complete after {total_rounds} rounds. Proceeding to jury...")
    
    # Clear progress
    status_container.empty()
    
    # Now run jury deliberation
    run_jury_deliberation(orch, judge_placeholder)
    
    # And verdict
    run_verdict(orch, judge_placeholder)


def update_judge_bench(placeholder, content: str):
    """Update the judge's bench with new content."""
    formatted = content.replace('<', '&lt;').replace('>', '&gt;')
    formatted = formatted.replace('**', '<strong>').replace('*', '<em>')
    formatted = formatted.replace('\n', '<br>')

    placeholder.markdown(f'''
    <div class="judge-bench glow-effect">
        <div class="judge-header">The Honorable Court Presiding</div>
        <div class="judge-content">
            {formatted}
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO MODE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_demo_mode():
    """Render the UI with mock data for layout verification."""
    demo_jurors = st.session_state.demo_jurors

    render_header()
    render_status_bar("ARGUMENTS", "LU-2024-00847", "DEMO")

    # Judge's Bench
    st.markdown('''
    <div class="judge-bench glow-effect">
        <div class="judge-header">The Honorable Court Presiding</div>
        <div class="judge-content">
            <strong>COURT IS IN SESSION</strong><br><br>
            <em>The jury is reminded that they must evaluate evidence based solely on what is presented in this courtroom.
            Outside research or personal knowledge of the parties involved is strictly prohibited.</em><br><br>
            Counsel may proceed with arguments.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    col_plaintiff, col_evidence, col_defense = st.columns([1, 1, 1])

    with col_plaintiff:
        st.markdown('''
        <div class="counsel-table plaintiff-table">
            <div class="plaintiff-header">Plaintiff Counsel</div>
        ''', unsafe_allow_html=True)

        for msg in MOCK_PLAINTIFF_MESSAGES:
            st.markdown(f'''
            <div class="counsel-message plaintiff-message">
                <div class="message-sender">{msg["agent_name"]}</div>
                {msg["content"]}
                <div class="message-time">⏱ {msg["timestamp"]}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_evidence:
        st.markdown('''
        <div class="evidence-stand">
            <div class="evidence-header">📋 Evidence Stand</div>
        ''', unsafe_allow_html=True)

        render_case_title("Meridian Corp v. Sullivan")

        st.markdown(f'''
        <div class="evidence-content">
            {MOCK_CASE_FACTS.replace(chr(10), '<br>')}
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_defense:
        st.markdown('''
        <div class="counsel-table defense-table">
            <div class="defense-header">Defense Counsel</div>
        ''', unsafe_allow_html=True)

        for msg in MOCK_DEFENSE_MESSAGES:
            st.markdown(f'''
            <div class="counsel-message defense-message">
                <div class="message-sender">{msg["agent_name"]}</div>
                {msg["content"]}
                <div class="message-time">⏱ {msg["timestamp"]}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Jury Box with emojis
    jury_scores = {j["name"]: j["score"] for j in demo_jurors}
    juror_personas = {}
    for j in demo_jurors:
        persona = JUROR_PERSONAS.get(j["name"], {"emoji": "👤", "occupation": "Juror"})
        juror_personas[j["name"]] = {
            "emoji": persona["emoji"],
            "occupation": persona["occupation"],
            "thought": j["thought"]
        }
    render_jury_box_from_scores(jury_scores, juror_personas)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🎭 Demo Mode</div>', unsafe_allow_html=True)

        st.warning("UI Preview Mode - Mock Data")

        if st.button("Exit Demo Mode", use_container_width=True):
            st.session_state.demo_mode = False
            st.rerun()

        st.divider()
        st.markdown("### Jury Controls")

        if st.button("🎲 Randomize Sentiment", use_container_width=True):
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
            if st.button("🔴 Plaintiff", use_container_width=True):
                for j in st.session_state.demo_jurors:
                    j["score"] = min(100, j["score"] + random.randint(5, 15))
                st.rerun()
        with col2:
            if st.button("🔵 Defense", use_container_width=True):
                for j in st.session_state.demo_jurors:
                    j["score"] = max(0, j["score"] - random.randint(5, 15))
                st.rerun()


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
    # ZONE A: HEADER
    # ═══════════════════════════════════════════════════════════════════════════
    render_header()

    phase = orch.phase
    phase_display = get_phase_display_name(phase)
    session_status = "PROCESSING" if is_processing else "ACTIVE"

    render_status_bar(phase_display, st.session_state.case_id, session_status)

    # ═══════════════════════════════════════════════════════════════════════════
    # ZONE B: JUDGE'S BENCH (Shows actual judge statements)
    # ═══════════════════════════════════════════════════════════════════════════
    judge_placeholder = st.empty()

    # Get latest judge message or show phase-appropriate default
    latest_judge = get_latest_judge_message(orch)

    if latest_judge:
        judge_content = latest_judge
    elif phase == TrialPhase.AWAITING_COMPLAINT:
        judge_content = "**COURT AWAITING CASE FILING**\n\n*Submit a complaint document to initialize the judicial simulation.*"
    elif phase == TrialPhase.COURT_ASSEMBLED:
        judge_content = f"**COURT IS ASSEMBLED**\n\n*Case:* {orch.case_title}\n\n*All parties are present. Counsel may proceed when ready.*"
    elif phase == TrialPhase.ADJOURNED:
        judge_content = "**COURT IS ADJOURNED**\n\n*This matter has been concluded. The record is sealed.*"
    else:
        judge_content = "**COURT IS IN SESSION**\n\n*Proceedings are underway. The jury is reminded to evaluate evidence based solely on what is presented.*"

    update_judge_bench(judge_placeholder, judge_content)

    # ═══════════════════════════════════════════════════════════════════════════
    # ZONE C: THE WELL (Counsel Tables + Evidence Stand)
    # ═══════════════════════════════════════════════════════════════════════════
    col_plaintiff, col_evidence, col_defense = st.columns([1, 1, 1])

    # Plaintiff Table
    with col_plaintiff:
        plaintiff_msgs = [m for m in orch.get_transcript() if m.get('agent_type') == 'plaintiff']
        
        # Build history HTML (all messages as cards inside the box)
        history_html = ""
        if plaintiff_msgs:
            for idx, msg in enumerate(plaintiff_msgs):
                content = msg.get('content', '')
                preview = content[:80] + "..." if len(content) > 80 else content
                preview = preview.replace('<', '&lt;').replace('>', '&gt;').replace('\n', ' ')
                full_content = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                round_label = f"Round {idx + 1}"
                
                history_html += f'''
                <details class="argument-card plaintiff-card">
                    <summary>📜 {round_label}: {preview}</summary>
                    <div class="argument-full">{full_content}</div>
                </details>
                '''
        
        # Render complete box with history inside
        placeholder_msg = '<div style="color: #64748b; font-style: italic; padding: 1rem; text-align: center;">Awaiting opening statements...</div>' if not plaintiff_msgs else ""
        
        st.markdown(f'''
        <div class="counsel-table plaintiff-table">
            <div class="plaintiff-header">🔴 Plaintiff Counsel</div>
            <div class="message-card-list">
                {history_html if history_html else placeholder_msg}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Placeholder for streaming current argument (below the box)
        plaintiff_stream_placeholder = st.empty()

    # Evidence Stand
    with col_evidence:
        st.markdown('''
        <div class="evidence-stand">
            <div class="evidence-header">📋 Evidence Stand</div>
        ''', unsafe_allow_html=True)

        if orch.case_facts:
            if orch.case_title:
                render_case_title(orch.case_title)

            summary = get_case_summary(orch.case_facts, 400)
            st.markdown(f'''
            <div class="evidence-content">
                {summary}
            </div>
            ''', unsafe_allow_html=True)

            with st.expander("View Full Case Document"):
                st.markdown(orch.case_facts)
        else:
            st.markdown('''
            <div style="color: #64748b; font-style: italic; padding: 1rem; text-align: center;">
                No evidence submitted
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Defense Table
    with col_defense:
        defense_msgs = [m for m in orch.get_transcript() if m.get('agent_type') == 'defense']
        
        # Build history HTML (all messages as cards inside the box)
        history_html = ""
        if defense_msgs:
            for idx, msg in enumerate(defense_msgs):
                content = msg.get('content', '')
                preview = content[:80] + "..." if len(content) > 80 else content
                preview = preview.replace('<', '&lt;').replace('>', '&gt;').replace('\n', ' ')
                full_content = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                round_label = f"Round {idx + 1}"
                
                history_html += f'''
                <details class="argument-card defense-card">
                    <summary>📜 {round_label}: {preview}</summary>
                    <div class="argument-full">{full_content}</div>
                </details>
                '''
        
        # Render complete box with history inside
        placeholder_msg = '<div style="color: #64748b; font-style: italic; padding: 1rem; text-align: center;">Awaiting opening statements...</div>' if not defense_msgs else ""
        
        st.markdown(f'''
        <div class="counsel-table defense-table">
            <div class="defense-header">Defense Counsel 🔵</div>
            <div class="message-card-list">
                {history_html if history_html else placeholder_msg}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Placeholder for streaming current argument (below the box)
        defense_stream_placeholder = st.empty()

    # ═══════════════════════════════════════════════════════════════════════════
    # ZONE D: JURY BOX (with expandable juror tabs)
    # ═══════════════════════════════════════════════════════════════════════════
    if orch.jury and orch.jury.size > 0:
        jury_scores = orch.jury.get_scores()
        juror_personas = build_juror_personas(orch)
        
        # First render the visual jury box
        render_jury_box_from_scores(jury_scores, juror_personas)
        
        # Then add expandable tabs for each juror's full thoughts
        st.markdown("#### 👥 Juror Deliberations (Click to expand)")
        juror_tabs = st.tabs([f"{JUROR_EMOJI_MAP.get(name, '👤')} {name.split()[0]}" for name in jury_scores.keys()])
        
        for idx, (name, score) in enumerate(jury_scores.items()):
            with juror_tabs[idx]:
                persona = juror_personas.get(name, {})
                occupation = persona.get("occupation", "Juror")
                thought = persona.get("thought", "No thoughts recorded")
                emoji = JUROR_EMOJI_MAP.get(name, "👤")
                
                # Leaning indicator
                if score >= 55:
                    leaning = "🔴 Leaning Plaintiff"
                elif score <= 45:
                    leaning = "🔵 Leaning Defense"
                else:
                    leaning = "⚪ Undecided"
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{emoji} {name}**")
                    st.caption(occupation)
                with col2:
                    st.metric("Score", f"{score}/100", leaning)
                
                st.markdown("---")
                st.markdown("**Full Thought Process:**")
                st.markdown(f"*{thought}*")

    # ═══════════════════════════════════════════════════════════════════════════
    # COURT PROCEEDINGS (Full Transcript)
    # ═══════════════════════════════════════════════════════════════════════════
    with st.expander("📜 Court Proceedings Transcript", expanded=False):
        for msg in orch.get_transcript():
            render_message(msg)

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute pending action (streaming goes to appropriate placeholders)
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
            st.error(f"Error during proceedings: {e}")
            import traceback
            st.code(traceback.format_exc())

        st.session_state.is_processing = False
        st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # SIDEBAR: Case Management & Controls
    # ═══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown('<div class="sidebar-header">⚖️ Case Management</div>', unsafe_allow_html=True)

        if st.button("🎭 Preview UI (Demo Mode)", use_container_width=True):
            st.session_state.demo_mode = True
            st.rerun()

        st.divider()

        uploaded = st.file_uploader(
            "📄 Submit Complaint (PDF)",
            type=["pdf"],
            disabled=is_processing,
            help="Upload a legal complaint document to begin the trial"
        )

        if uploaded and not st.session_state.upload_processed:
            text = extract_pdf_text(uploaded)
            if text:
                orch.set_case(text, uploaded.name.replace(".pdf", ""))
                st.session_state.upload_processed = True
                st.rerun()

        st.divider()
        st.markdown("### 🎮 Trial Controls")

        phase = orch.phase

        if phase == TrialPhase.AWAITING_COMPLAINT:
            if orch.case_facts:
                if st.button("⚖️ Initialize Court", disabled=is_processing, use_container_width=True):
                    st.session_state.is_processing = True
                    with st.spinner("Assembling court..."):
                        orch.initialize_court()
                    st.session_state.is_processing = False
                    st.rerun()
            else:
                st.info("📄 Upload a complaint to begin")

        elif phase == TrialPhase.COURT_ASSEMBLED:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎬 Begin Trial", disabled=is_processing, use_container_width=True):
                    st.session_state.is_processing = True
                    st.session_state.pending_action = "opening"
                    st.rerun()
            with col2:
                if st.button("🤖 Auto Trial", disabled=is_processing, use_container_width=True, help="Agents debate automatically"):
                    st.session_state.is_processing = True
                    st.session_state.pending_action = "autonomous"
                    st.rerun()

        elif phase == TrialPhase.ARGUMENTS:
            st.caption(f"Round {orch.current_round}")
            if st.button("⚔️ Next Round", disabled=is_processing, use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "argument"
                st.rerun()

            if orch.current_round > 1:
                if st.button("👥 Begin Deliberation", disabled=is_processing, use_container_width=True):
                    st.session_state.is_processing = True
                    st.session_state.pending_action = "jury"
                    st.rerun()

        elif phase == TrialPhase.JURY_DELIBERATION:
            if st.button("📜 Render Verdict", disabled=is_processing, use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "verdict"
                st.rerun()

        elif phase == TrialPhase.ADJOURNED:
            st.success("✅ Trial Complete")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 New Case", use_container_width=True):
                    st.session_state.orchestrator = TrialOrchestrator()
                    st.session_state.upload_processed = False
                    st.session_state.is_processing = False
                    st.session_state.juror_thoughts = {}
                    st.session_state.case_id = f"LU-{time.strftime('%Y')}-{hash(time.time()) % 100000:05d}"
                    if "pending_action" in st.session_state:
                        del st.session_state.pending_action
                    st.rerun()
            with col2:
                if st.button("💾 Export", use_container_width=True):
                    filepath = orch.export_transcript()
                    st.success("Saved!")

        if is_processing:
            st.warning("⏳ Processing...")

        st.divider()
        st.markdown("### 📊 Session Status")

        status_color = "#C5A059" if phase != TrialPhase.ADJOURNED else "#4a5568"
        st.markdown(f'''
        <div style="
            padding: 0.75rem;
            background: rgba(0,0,0,0.3);
            border-left: 3px solid {status_color};
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
        ">
            <strong>Phase:</strong> {phase_display}<br>
            <strong>Case:</strong> {st.session_state.case_id}<br>
            <strong>Round:</strong> {orch.current_round if hasattr(orch, 'current_round') else 0}
        </div>
        ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
