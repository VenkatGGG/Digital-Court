"""
ui/phases.py - Trial phase execution logic
"""

import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import get_settings
from config.prompts import Prompts
from orchestrator import TrialPhase
from ui.components import (
    render_counsel_box,
    render_jury_box,
    render_jury_box_from_scores,
    render_message,
    escape_html,
    format_content,
    JUROR_EMOJI_MAP,
)
from data.mock import JUROR_PERSONAS

settings = get_settings()

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
