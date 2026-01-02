"""
orchestrator/trial.py - Trial Orchestrator

Central controller for the trial simulation state machine.
"""

import json
import time
from dataclasses import dataclass
from typing import Optional

from orchestrator.phases import TrialPhase
from agents import JudgeAgent, LawyerAgent, JurorSwarm
from config.prompts import Prompts
from config.settings import get_settings


@dataclass
class TrialMessage:
    """A message in the trial proceedings."""
    agent_type: str
    agent_name: str
    content: str
    score: Optional[int] = None
    timestamp: str = ""


class TrialOrchestrator:
    """
    Central controller for the trial simulation.
    
    Manages state transitions and coordinates all agents.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.phase = TrialPhase.AWAITING_COMPLAINT
        self.case_facts: Optional[str] = None
        self.case_title: str = "Untitled Case"
        
        # Agents (initialized on demand)
        self.judge: Optional[JudgeAgent] = None
        self.plaintiff_lawyer: Optional[LawyerAgent] = None
        self.defense_lawyer: Optional[LawyerAgent] = None
        self.jury: Optional[JurorSwarm] = None
        
        # Trial state
        self.transcript: list[TrialMessage] = []
        self.current_round: int = 0
        
        settings = get_settings()
        self.max_argument_rounds = settings.max_argument_rounds
    
    def set_case(self, facts: str, title: str = "Civil Matter"):
        """Set the case facts from the complaint."""
        self.case_facts = facts
        self.case_title = title
        self._add_to_transcript(
            "system", "COURT CLERK",
            f"Case filed: {title} ({len(facts)} characters)"
        )
    
    def initialize_court(self) -> bool:
        """
        Initialize all AI agents.
        
        Returns:
            True if successful
        """
        try:
            self.judge = JudgeAgent()
            self._add_to_transcript(
                "system", "COURT",
                "The Honorable Judge Evelyn Marshall presiding."
            )
            
            self.plaintiff_lawyer = LawyerAgent("plaintiff")
            self.defense_lawyer = LawyerAgent("defense")
            self._add_to_transcript(
                "system", "COURT",
                "Counsel for both parties have entered the courtroom."
            )
            
            self.jury = JurorSwarm()
            self._add_to_transcript(
                "system", "COURT",
                f"The jury has been seated: {', '.join(self.jury.juror_names)}"
            )
            
            self.phase = TrialPhase.COURT_ASSEMBLED
            return True
            
        except Exception as e:
            self._add_to_transcript("system", "ERROR", f"Initialization failed: {e}")
            return False
    
    def _add_to_transcript(
        self,
        agent_type: str,
        agent_name: str,
        content: str,
        score: Optional[int] = None
    ) -> TrialMessage:
        """Add a message to the trial transcript."""
        msg = TrialMessage(
            agent_type=agent_type,
            agent_name=agent_name,
            content=content,
            score=score,
            timestamp=time.strftime("%H:%M:%S")
        )
        self.transcript.append(msg)
        return msg
    
    def get_transcript(self) -> list[dict]:
        """Get transcript as list of dicts."""
        return [
            {
                "agent_type": m.agent_type,
                "agent_name": m.agent_name,
                "content": m.content,
                "score": m.score,
                "timestamp": m.timestamp
            }
            for m in self.transcript
        ]
    
    def get_recent_arguments(self, count: int = 4) -> str:
        """Get recent lawyer arguments as context string."""
        lawyer_msgs = [
            m for m in self.transcript
            if m.agent_type in ["plaintiff", "defense"]
        ][-count:]
        
        return "\n".join([
            f"{m.agent_name}: {m.content[:200]}..."
            for m in lawyer_msgs
        ])
    
    def export_transcript(self, filepath: str = "trial_transcript.json") -> str:
        """Export trial transcript to JSON."""
        data = {
            "case_title": self.case_title,
            "phase": self.phase.value,
            "rounds_completed": self.current_round - 1,
            "verdict": self.jury.get_verdict() if self.jury else None,
            "transcript": self.get_transcript()
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    # =========================================================================
    # PHASE TRANSITION HELPERS
    # =========================================================================
    
    def start_arguments(self):
        """Transition to arguments phase."""
        self.phase = TrialPhase.ARGUMENTS
        self.current_round = 1
    
    def advance_round(self):
        """Advance to next argument round."""
        self.current_round += 1
    
    def start_jury_deliberation(self):
        """Transition to jury deliberation."""
        self.phase = TrialPhase.JURY_DELIBERATION
    
    def render_verdict(self):
        """Transition to verdict phase."""
        self.phase = TrialPhase.VERDICT
    
    def adjourn(self):
        """Transition to adjourned phase."""
        self.phase = TrialPhase.ADJOURNED
    
    # =========================================================================
    # AUTONOMOUS DEBATE METHODS
    # =========================================================================
    
    def get_full_argument_context(self) -> str:
        """Get all lawyer arguments as a formatted context string."""
        lawyer_msgs = [
            m for m in self.transcript
            if m.agent_type in ["plaintiff", "defense"]
        ]
        
        if not lawyer_msgs:
            return "No arguments yet."
        
        lines = []
        for m in lawyer_msgs:
            side = "PLAINTIFF" if m.agent_type == "plaintiff" else "DEFENSE"
            lines.append(f"[{side} - {m.timestamp}]\n{m.content}\n")
        
        return "\n".join(lines)
    
    def get_side_summary(self, side: str, max_chars: int = 800) -> str:
        """Get summary of arguments from one side."""
        msgs = [m for m in self.transcript if m.agent_type == side]
        
        if not msgs:
            return "No arguments yet."
        
        # Combine and truncate
        combined = "\n".join([m.content for m in msgs])
        if len(combined) > max_chars:
            combined = combined[:max_chars] + "..."
        
        return combined
    
    def should_conclude_debate(self, round_num: int) -> tuple[bool, str]:
        """
        Ask the judge if debate should conclude.
        
        Returns:
            Tuple of (should_conclude, reason)
        """
        settings = get_settings()
        
        # Always complete minimum rounds
        if round_num < settings.autonomous_min_rounds:
            return False, "Minimum rounds not reached"
        
        # Always stop at maximum rounds
        if round_num >= settings.autonomous_max_rounds:
            return True, "Maximum rounds reached"
        
        # Ask judge
        prompt = Prompts.JUDGE_SHOULD_CONCLUDE.format(
            plaintiff_summary=self.get_side_summary("plaintiff"),
            defense_summary=self.get_side_summary("defense"),
            round_num=round_num,
            max_rounds=settings.autonomous_max_rounds
        )
        
        response = self.judge.generate(prompt, temperature=0.3)
        should_conclude = "CONCLUDE" in response.upper()
        reason = "Both parties have made their essential points" if should_conclude else "Arguments continue"
        
        return should_conclude, reason
    
    def run_autonomous_debate(self):
        """
        Run autonomous debate between plaintiff and defense.
        
        Yields status updates as the debate progresses:
            {"type": "round_start", "round": int}
            {"type": "plaintiff_speaking", "round": int}
            {"type": "plaintiff_done", "round": int, "content": str}
            {"type": "defense_speaking", "round": int}
            {"type": "defense_done", "round": int, "content": str}
            {"type": "round_complete", "round": int, "should_continue": bool}
            {"type": "debate_complete", "total_rounds": int}
        """
        settings = get_settings()
        self.phase = TrialPhase.ARGUMENTS
        
        # Opening by judge
        judge_content = self.judge.open_court(self.case_title)
        self._add_to_transcript("judge", "JUDGE MARSHALL", judge_content)
        yield {"type": "judge", "content": judge_content}
        
        for round_num in range(1, settings.autonomous_max_rounds + 1):
            self.current_round = round_num
            yield {"type": "round_start", "round": round_num}
            
            # Get argument history
            argument_history = self.get_full_argument_context()
            
            # Plaintiff argues
            yield {"type": "plaintiff_speaking", "round": round_num}
            
            if round_num == 1:
                plaintiff_prompt = Prompts.PLAINTIFF_OPENING.format(case_facts=self.case_facts)
            else:
                plaintiff_prompt = Prompts.PLAINTIFF_AUTONOMOUS_ARGUMENT.format(
                    round_num=round_num,
                    case_facts=self.case_facts,
                    argument_history=argument_history
                )
            
            plaintiff_response = self.plaintiff_lawyer.generate(plaintiff_prompt)
            self._add_to_transcript("plaintiff", "ATTORNEY CHEN (Plaintiff)", plaintiff_response)
            yield {"type": "plaintiff_done", "round": round_num, "content": plaintiff_response}
            
            # Defense responds
            yield {"type": "defense_speaking", "round": round_num}
            
            # Refresh history with plaintiff's new argument
            argument_history = self.get_full_argument_context()
            
            if round_num == 1:
                defense_prompt = Prompts.DEFENSE_OPENING.format(case_facts=self.case_facts)
            else:
                defense_prompt = Prompts.DEFENSE_AUTONOMOUS_ARGUMENT.format(
                    round_num=round_num,
                    case_facts=self.case_facts,
                    argument_history=argument_history
                )
            
            defense_response = self.defense_lawyer.generate(defense_prompt)
            self._add_to_transcript("defense", "ATTORNEY WEBB (Defense)", defense_response)
            yield {"type": "defense_done", "round": round_num, "content": defense_response}
            
            # Check if debate should conclude
            should_conclude, reason = self.should_conclude_debate(round_num)
            
            # Judge announces round status
            judge_transition = Prompts.JUDGE_DEBATE_TRANSITION.format(
                round_num=round_num,
                reason=reason
            )
            self._add_to_transcript("judge", "JUDGE MARSHALL", judge_transition)
            
            yield {"type": "round_complete", "round": round_num, "should_continue": not should_conclude, "reason": reason}
            
            if should_conclude:
                break
        
        self.phase = TrialPhase.JURY_DELIBERATION
        yield {"type": "debate_complete", "total_rounds": self.current_round}
