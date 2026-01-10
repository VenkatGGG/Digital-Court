"""
JUSTICIA EX MACHINA: Autonomous Judicial Simulation
════════════════════════════════════════════════════

A strikingly minimal interface for AI-powered courtroom proceedings.
The weight of algorithmic justice meets refined design.
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
    JUROR_DATA,
    render_counsel_box,
    escape_html,
    format_content,
)
from ui.handlers import stream_response, extract_pdf_text


# ═══════════════════════════════════════════════════════════════════════════════
# JUROR PERSONA MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

JUROR_PERSONAS = {
    "Marcus": {"occupation": "Construction Foreman"},
    "Elena": {"occupation": "High School Teacher"},
    "Raymond": {"occupation": "Retired Accountant"},
    "Destiny": {"occupation": "Emergency Room Nurse"},
    "Chen": {"occupation": "Software Engineer"},
    "Patricia": {"occupation": "Former Judge"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK DATA FOR DEMO MODE
# ═══════════════════════════════════════════════════════════════════════════════

MOCK_PLAINTIFF_MESSAGES = [
    {"agent_type": "plaintiff", "agent_name": "Plaintiff Counsel", "timestamp": "09:15:32",
     "content": "Your Honor, members of the jury, the evidence will show a clear pattern of negligence that resulted in catastrophic damages to my client."},
    {"agent_type": "plaintiff", "agent_name": "Plaintiff Counsel", "timestamp": "09:18:45",
     "content": "Exhibit A demonstrates that the defendant was explicitly warned about these risks three times before the incident occurred."},
]

MOCK_DEFENSE_MESSAGES = [
    {"agent_type": "defense", "agent_name": "Defense Counsel", "timestamp": "09:16:08",
     "content": "Your Honor, the plaintiff's case rests on circumstantial evidence and emotional appeals rather than established facts."},
    {"agent_type": "defense", "agent_name": "Defense Counsel", "timestamp": "09:19:55",
     "content": "My client followed every protocol mandated by industry standards. The so-called warnings were routine compliance notices."},
]

MOCK_CASE_FACTS = """SUPREME COURT OF THE STATE OF NEW YORK
COUNTY OF NASSAU

JOHN JONES,
    Plaintiff,
        v.
GEORGE SMITH,
    Defendant.

Index No. 2024-0130

COMPLAINT

Plaintiff John Jones, by and through his attorneys, alleges as follows:

1. Plaintiff is a resident of Nassau County, New York.
2. Defendant is a corporation organized under the laws of the State of New York.
3. At all times relevant hereto, Defendant owed a duty of care to Plaintiff..."""

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

# Sidebar state management
_base_state = "collapsed" if (hasattr(st, 'session_state') and st.session_state.get('trial_started', False)) else "expanded"
_sidebar_state = st.session_state.get("sidebar_visible", _base_state) if hasattr(st, "session_state") else _base_state

if hasattr(st, 'session_state') and 'sidebar_visible' in st.session_state:
    _sidebar_state = "expanded" if st.session_state.sidebar_visible else "collapsed"

st.set_page_config(
    page_title="Justicia Ex Machina",
    page_icon="",
    layout="wide",
    initial_sidebar_state=_sidebar_state
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


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_phase_display_name(phase: TrialPhase) -> str:
    """Get display name for trial phase."""
    phase_names = {
        TrialPhase.AWAITING_COMPLAINT: "Awaiting Case",
        TrialPhase.COURT_ASSEMBLED: "Court Assembled",
        TrialPhase.OPENING_STATEMENTS: "Opening Statements",
        TrialPhase.ARGUMENTS: "Arguments",
        TrialPhase.JURY_DELIBERATION: "Deliberation",
        TrialPhase.VERDICT: "Verdict",
        TrialPhase.ADJOURNED: "Adjourned",
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
        persona_info = JUROR_PERSONAS.get(name, {"occupation": "Juror"})
        personas[name] = {
            "occupation": persona_info["occupation"],
            "thought": st.session_state.juror_thoughts.get(name, "Awaiting deliberation...")
        }

    return personas


# ═══════════════════════════════════════════════════════════════════════════════
# STREAMING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def stream_to_placeholder(placeholder, agent, prompt, agent_type, agent_name):
    """Stream response to a placeholder with typing effect."""
    response = ""

    try:
        for chunk in agent.generate_stream(prompt):
            response += chunk
            display = escape_html(response).replace('\n', '<br>')
            placeholder.markdown(f'''
            <div class="argument-entry animate-in">
                <div class="argument-round">{agent_name}</div>
                <div class="argument-text">{display}<span class="typing-cursor"></span></div>
            </div>
            ''', unsafe_allow_html=True)
    except Exception as e:
        response = agent.generate(prompt)

    # Final render without cursor
    display = escape_html(response).replace('\n', '<br>')
    placeholder.markdown(f'''
    <div class="argument-entry">
        <div class="argument-round">{agent_name}</div>
        <div class="argument-text">{display}</div>
    </div>
    ''', unsafe_allow_html=True)

    return response


# ═══════════════════════════════════════════════════════════════════════════════
# TRIAL PHASE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def run_opening_statements(orch, plaintiff_placeholder, defense_placeholder, judge_placeholder):
    """Execute opening statements with streaming."""

    # Judge opens
    judge_content = orch.judge.open_court(orch.case_title)
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Plaintiff streams
    prompt = Prompts.PLAINTIFF_OPENING.format(case_facts=orch.case_facts)
    response = stream_to_placeholder(
        plaintiff_placeholder,
        orch.plaintiff_lawyer,
        prompt,
        "plaintiff",
        "Plaintiff Counsel"
    )
    orch._add_to_transcript("plaintiff", "Plaintiff Counsel", response)

    # Judge transition
    judge_content = Prompts.JUDGE_TRANSITION_TO_DEFENSE
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Defense streams
    prompt = Prompts.DEFENSE_OPENING.format(case_facts=orch.case_facts)
    response = stream_to_placeholder(
        defense_placeholder,
        orch.defense_lawyer,
        prompt,
        "defense",
        "Defense Counsel"
    )
    orch._add_to_transcript("defense", "Defense Counsel", response)

    # Conclude
    judge_content = Prompts.JUDGE_OPENINGS_COMPLETE
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    orch.start_arguments()


def run_argument_round(orch, plaintiff_placeholder, defense_placeholder, judge_placeholder):
    """Execute one round of arguments."""

    round_num = orch.current_round

    # Judge announces round
    judge_content = Prompts.JUDGE_ARGUMENT_ROUND.format(round_num=round_num)
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Get previous arguments
    plaintiff_msgs = [m for m in orch.transcript if m.agent_type == "plaintiff"]
    defense_msgs = [m for m in orch.transcript if m.agent_type == "defense"]

    # Plaintiff argument
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
        "Plaintiff Counsel"
    )
    orch._add_to_transcript("plaintiff", "Plaintiff Counsel", plaintiff_response)

    # Judge transition
    judge_content = Prompts.JUDGE_DEFENSE_RESPOND
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Defense rebuttal
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
        "Defense Counsel"
    )
    orch._add_to_transcript("defense", "Defense Counsel", defense_response)

    orch.advance_round()


def run_jury_deliberation(orch, judge_placeholder):
    """Execute parallel jury deliberation."""

    # Judge instructs jury
    judge_content = Prompts.JUDGE_JURY_DELIBERATE
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    context = orch.get_recent_arguments(4)

    # Progress indicator
    progress_placeholder = st.empty()
    progress_placeholder.markdown('''
    <div class="streaming-indicator" style="padding: 1rem;">
        <span class="streaming-dot"></span>
        <span>Jury deliberating</span>
    </div>
    ''', unsafe_allow_html=True)

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
            progress_placeholder.markdown(f'''
            <div class="streaming-indicator" style="padding: 1rem;">
                <span class="streaming-dot"></span>
                <span>Deliberating ({completed}/{orch.jury.size})</span>
            </div>
            ''', unsafe_allow_html=True)
            results.append(future.result())

    progress_placeholder.empty()

    # Store thoughts
    for result in results:
        juror = result["juror"]
        thought = result["response"][:80] + "..." if len(result["response"]) > 80 else result["response"]
        st.session_state.juror_thoughts[juror.name] = thought
        orch._add_to_transcript("juror", f"Juror {juror.name}", result["response"], result["score"])

    orch.start_jury_deliberation()


def run_verdict(orch, judge_placeholder):
    """Render final verdict."""

    # Judge pre-verdict
    judge_content = Prompts.JUDGE_PRE_VERDICT
    orch._add_to_transcript("judge", "The Court", judge_content)
    update_judge_bench(judge_placeholder, judge_content)

    # Summary
    context = orch.get_recent_arguments(4)
    prompt = Prompts.JUDGE_SUMMARY_PROMPT.format(context=context)
    summary = orch.judge.generate(prompt)
    orch._add_to_transcript("judge", "The Court", summary)

    # Verdict
    verdict_info = orch.jury.get_verdict()
    avg = verdict_info["average_score"]

    if verdict_info["verdict"] == "PLAINTIFF":
        verdict_text = f"Plaintiff Prevails — Damages: ${verdict_info['damages']:,}"
    elif verdict_info["verdict"] == "DEFENSE":
        verdict_text = "Defense Prevails — Case Dismissed"
    else:
        verdict_text = "Hung Jury — Mistrial Declared"

    scores = [f"{n}: {s}" for n, s in verdict_info["individual_scores"].items()]
    final_content = f"{summary}\n\n**{verdict_text}**\n\nAverage Score: {avg:.1f}"

    update_judge_bench(judge_placeholder, final_content)
    orch._add_to_transcript("judge", "The Court", verdict_text)

    orch.adjourn()


def run_autonomous_trial(orch, plaintiff_placeholder, defense_placeholder, judge_placeholder):
    """Run complete autonomous trial."""

    progress_container = st.empty()
    status_container = st.empty()

    for update in orch.run_autonomous_debate():
        event_type = update.get("type")

        if event_type == "judge":
            update_judge_bench(judge_placeholder, update.get("content", ""))

        elif event_type == "round_start":
            round_num = update.get("round", 1)
            progress_container.markdown(f'''
            <div class="streaming-indicator" style="padding: 1rem;">
                <span class="streaming-dot"></span>
                <span>Round {round_num}</span>
            </div>
            ''', unsafe_allow_html=True)

        elif event_type == "plaintiff_speaking":
            status_container.markdown("Plaintiff speaking...")
            plaintiff_msgs = [m for m in orch.get_transcript() if m.get('agent_type') == 'plaintiff']
            plaintiff_placeholder.markdown(render_counsel_box("plaintiff", plaintiff_msgs, "..."), unsafe_allow_html=True)

        elif event_type == "plaintiff_done":
            plaintiff_placeholder.markdown(render_counsel_box("plaintiff", [m for m in orch.get_transcript() if m.get('agent_type') == 'plaintiff']), unsafe_allow_html=True)

        elif event_type == "defense_speaking":
            status_container.markdown("Defense responding...")
            defense_msgs = [m for m in orch.get_transcript() if m.get('agent_type') == 'defense']
            defense_placeholder.markdown(render_counsel_box("defense", defense_msgs, "..."), unsafe_allow_html=True)

        elif event_type == "defense_done":
            defense_placeholder.markdown(render_counsel_box("defense", [m for m in orch.get_transcript() if m.get('agent_type') == 'defense']), unsafe_allow_html=True)

        elif event_type == "round_complete":
            round_num = update.get("round", 1)
            reason = update.get("reason", "")
            should_continue = update.get("should_continue", True)

            if should_continue:
                status_container.markdown(f"Round {round_num} complete. {reason}")
            else:
                status_container.markdown(f"Debate concluded: {reason}")

        elif event_type == "debate_complete":
            total_rounds = update.get("total_rounds", 1)
            progress_container.markdown(f"Debate complete after {total_rounds} rounds.")

    status_container.empty()

    run_jury_deliberation(orch, judge_placeholder)
    run_verdict(orch, judge_placeholder)


def update_judge_bench(placeholder, content: str):
    """Update the judge's bench."""
    formatted = format_content(content)

    placeholder.markdown(f'''
    <div class="bench">
        <div class="bench-label">The Court</div>
        <div class="bench-content">
            {formatted}
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO MODE
# ═══════════════════════════════════════════════════════════════════════════════

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
                st.session_state.upload_processed = True
                st.rerun()

        st.divider()
        st.markdown("### Controls")

        phase = orch.phase

        if phase == TrialPhase.AWAITING_COMPLAINT:
            if orch.case_facts:
                if st.button("Initialize Court", disabled=is_processing, use_container_width=True):
                    st.session_state.is_processing = True
                    with st.spinner("Assembling court..."):
                        orch.initialize_court()
                    st.session_state.is_processing = False
                    st.rerun()
            else:
                st.caption("Upload a complaint to begin")

        elif phase == TrialPhase.COURT_ASSEMBLED:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Begin Trial", disabled=is_processing, use_container_width=True):
                    st.session_state.is_processing = True
                    st.session_state.pending_action = "opening"
                    st.rerun()
            with col2:
                if st.button("Auto Trial", disabled=is_processing, use_container_width=True, help="Autonomous debate"):
                    st.session_state.is_processing = True
                    st.session_state.pending_action = "autonomous"
                    st.session_state.trial_started = True
                    st.rerun()

        elif phase == TrialPhase.ARGUMENTS:
            st.caption(f"Round {orch.current_round}")
            if st.button("Next Round", disabled=is_processing, use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "argument"
                st.rerun()

            if orch.current_round > 1:
                if st.button("Begin Deliberation", disabled=is_processing, use_container_width=True):
                    st.session_state.is_processing = True
                    st.session_state.pending_action = "jury"
                    st.rerun()

        elif phase == TrialPhase.JURY_DELIBERATION:
            if st.button("Render Verdict", disabled=is_processing, use_container_width=True):
                st.session_state.is_processing = True
                st.session_state.pending_action = "verdict"
                st.rerun()

        elif phase == TrialPhase.ADJOURNED:
            st.success("Trial Complete")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("New Case", use_container_width=True):
                    st.session_state.orchestrator = TrialOrchestrator()
                    st.session_state.upload_processed = False
                    st.session_state.is_processing = False
                    st.session_state.juror_thoughts = {}
                    st.session_state.trial_started = False
                    st.session_state.case_id = f"JEM-{time.strftime('%Y')}-{hash(time.time()) % 100000:05d}"
                    if "pending_action" in st.session_state:
                        del st.session_state.pending_action
                    st.rerun()
            with col2:
                if st.button("Export", use_container_width=True):
                    filepath = orch.export_transcript()
                    st.success("Saved")

        if is_processing:
            st.markdown('''
            <div class="streaming-indicator" style="margin-top: 1rem;">
                <span class="streaming-dot"></span>
                <span>Processing</span>
            </div>
            ''', unsafe_allow_html=True)

        st.divider()
        st.markdown("### Status")

        status_color = "#8B7355" if phase != TrialPhase.ADJOURNED else "#4A4845"
        st.markdown(f'''
        <div class="session-status">
            <strong>Phase:</strong> <span>{phase_display}</span><br>
            <strong>Case:</strong> <span>{st.session_state.case_id}</span><br>
            <strong>Round:</strong> <span>{orch.current_round if hasattr(orch, 'current_round') else 0}</span>
        </div>
        ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
