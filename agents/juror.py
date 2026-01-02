"""
agents/juror.py - Juror Agents

Individual jurors and the JurorSwarm collective.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional, Callable

from core.gemini_client import GeminiBrain, GeminiBrainError
from config.prompts import Prompts
from config.settings import get_settings


@dataclass
class JurorVote:
    """A juror's vote and reasoning."""
    juror_name: str
    score: int
    reasoning: str


class JurorBrain(GeminiBrain):
    """
    Specialized GeminiBrain for juror personas.
    
    Automatically constructs system instruction from profile
    and tracks bias scoring.
    """
    
    def __init__(self, profile: dict, api_key: Optional[str] = None):
        """
        Initialize from a juror profile dictionary.
        
        Args:
            profile: Juror data from jurors.json
            api_key: Optional API key override
        """
        self.profile = profile
        self.current_bias_score = profile.get("initial_bias_score", 50)
        self.deliberation_history = []
        
        system_instruction = Prompts.build_juror_system_prompt(profile)
        
        super().__init__(
            persona_name=f"Juror_{profile.get('id', 'unknown')}",
            system_instruction=system_instruction,
            api_key=api_key
        )
    
    @property
    def name(self) -> str:
        return self.profile.get("name", "Unknown Juror")
    
    @property
    def occupation(self) -> str:
        return self.profile.get("occupation", "Unknown")
    
    def think(self, context: str) -> dict:
        """
        Generate internal monologue and update bias score.
        
        Args:
            context: Current trial situation
        
        Returns:
            Dict with 'monologue' and 'bias_score'
        """
        prompt = Prompts.JUROR_THINK.format(
            context=context,
            juror_name=self.name
        )
        
        response = self.generate(prompt)
        result = self._parse_response(response)
        
        self.deliberation_history.append({
            "context": context[:200] + "..." if len(context) > 200 else context,
            "response": result
        })
        
        return result
    
    def deliberate(self, context: str) -> dict:
        """
        Deliberate on arguments (used in parallel jury).
        
        Args:
            context: Arguments to consider
        
        Returns:
            Dict with 'monologue' and 'bias_score'
        """
        prompt = Prompts.JUROR_DELIBERATION.format(
            context=context,
            juror_name=self.name
        )
        
        response = self.generate(prompt)
        return self._parse_response(response)
    
    def _parse_response(self, response: str) -> dict:
        """Parse juror response for thoughts and score."""
        result = {"monologue": response, "bias_score": self.current_bias_score}
        
        for line in response.split("\n"):
            if line.upper().startswith("THOUGHTS:"):
                result["monologue"] = line.split(":", 1)[-1].strip()
            elif line.upper().startswith("SCORE:"):
                try:
                    score_text = line.split(":")[-1].strip()
                    score = int(''.join(filter(str.isdigit, score_text[:3])))
                    result["bias_score"] = max(0, min(100, score))
                    self.current_bias_score = result["bias_score"]
                except (ValueError, IndexError):
                    pass
        
        return result


class JurorSwarm:
    """
    Manages a panel of AI jurors.
    
    Supports:
    - Parallel deliberation
    - Vote tracking
    - Verdict calculation
    """
    
    def __init__(self, jurors_file: Optional[str] = None):
        """
        Initialize the juror swarm.
        
        Args:
            jurors_file: Path to jurors.json (uses settings default if None)
        """
        settings = get_settings()
        filepath = jurors_file or settings.jurors_file
        
        self.jurors: list[JurorBrain] = []
        self.vote_history: list[list[JurorVote]] = []
        
        self._load_jurors(filepath)
    
    def _load_jurors(self, filepath: str):
        """Load juror profiles from JSON."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            for profile in data.get("jurors", []):
                try:
                    juror = JurorBrain(profile)
                    self.jurors.append(juror)
                except GeminiBrainError as e:
                    print(f"⚠️ Failed to load {profile.get('name')}: {e}")
        except FileNotFoundError:
            raise GeminiBrainError(f"Jurors file not found: {filepath}")
    
    @property
    def size(self) -> int:
        return len(self.jurors)
    
    @property
    def juror_names(self) -> list[str]:
        return [j.name for j in self.jurors]
    
    def get_scores(self) -> dict[str, int]:
        """Get current scores for all jurors."""
        return {j.name: j.current_bias_score for j in self.jurors}
    
    def get_average_score(self) -> float:
        """Calculate average bias score."""
        if not self.jurors:
            return 50.0
        scores = [j.current_bias_score for j in self.jurors]
        return sum(scores) / len(scores)
    
    def deliberate_parallel(
        self,
        context: str,
        on_complete: Optional[Callable[[str, dict], None]] = None
    ) -> list[JurorVote]:
        """
        Have all jurors deliberate in parallel.
        
        Args:
            context: Arguments to consider (same for all)
            on_complete: Callback(name, result) after each completes
        
        Returns:
            List of JurorVote objects
        """
        settings = get_settings()
        
        def get_response(juror: JurorBrain) -> dict:
            result = juror.deliberate(context)
            return {
                "juror": juror,
                "result": result
            }
        
        votes = []
        
        with ThreadPoolExecutor(max_workers=settings.parallel_jury_workers) as executor:
            futures = {executor.submit(get_response, j): j for j in self.jurors}
            
            for future in as_completed(futures):
                data = future.result()
                juror = data["juror"]
                result = data["result"]
                
                vote = JurorVote(
                    juror_name=juror.name,
                    score=result["bias_score"],
                    reasoning=result["monologue"]
                )
                votes.append(vote)
                
                if on_complete:
                    on_complete(juror.name, result)
        
        self.vote_history.append(votes)
        return votes
    
    def get_verdict(self) -> dict:
        """
        Calculate the final verdict based on average jury score.
        
        Thresholds:
        - > 50: Plaintiff wins
        - <= 50: Defense wins (benefit of doubt to defendant)
        No hung jury option.
        """
        avg = self.get_average_score()
        scores = self.get_scores()
        
        if avg > 50:
            verdict = "PLAINTIFF"
            damages = int((avg - 50) * 20000)
        else:
            verdict = "DEFENSE"
            damages = 0
        
        return {
            "verdict": verdict,
            "average_score": round(avg, 1),
            "individual_scores": scores,
            "damages": damages
        }
