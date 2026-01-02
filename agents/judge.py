"""
agents/judge.py - Judge Agent

The Honorable Judge Evelyn Marshall - presides over the trial
with access to legal rules for procedural rulings.
"""

from typing import Optional

from agents.base import BaseAgent
from config.prompts import Prompts
from core.rag import query_legal_db, format_rules_for_context


class JudgeAgent(BaseAgent):
    """
    The Judge Agent - presides over trials with legal database access.
    
    Capabilities:
    - Query the legal database to cite specific rules
    - Issue procedural rulings
    - Summarize arguments for the jury
    - Enforce the FRCP
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Judge Agent."""
        super().__init__(
            persona_name="Judge_Marshall",
            system_instruction=Prompts.JUDGE_SYSTEM,
            api_key=api_key
        )
        
        # Check database availability
        try:
            from core.rag import get_legal_db
            collection = get_legal_db()
            self._db_available = True
            self._db_count = collection.count()
        except Exception:
            self._db_available = False
            self._db_count = 0
    
    def get_role(self) -> str:
        return "judge"
    
    @property
    def db_status(self) -> str:
        """Get database connection status."""
        if self._db_available:
            return f"Connected ({self._db_count} rules)"
        return "Unavailable"
    
    def consult_rulebook(self, topic: str, n_rules: int = 3) -> str:
        """
        Query the legal database for relevant rules.
        
        Args:
            topic: The legal topic to research
            n_rules: Number of rules to retrieve
        
        Returns:
            Formatted string of relevant rules
        """
        if not self._db_available:
            return "[Database unavailable]"
        
        results = query_legal_db(topic, n_results=n_rules)
        return format_rules_for_context(results, max_rules=n_rules)
    
    def rule_on_matter(self, matter: str, context: str = "") -> str:
        """
        Make a ruling on a procedural matter, citing relevant rules.
        
        Args:
            matter: The procedural issue
            context: Additional case context
        
        Returns:
            The judge's ruling with citations
        """
        rules = self.consult_rulebook(matter)
        
        prompt = f"""A procedural matter has arisen.

MATTER: {matter}

CONTEXT: {context if context else "No additional context."}

{rules}

Issue your ruling, citing specific rules if applicable."""

        return self.generate(prompt)
    
    def summarize_for_jury(self, arguments: list[dict]) -> str:
        """
        Summarize arguments for the jury.
        
        Args:
            arguments: List of dicts with 'party' and 'argument' keys
        
        Returns:
            Neutral summary for the jury
        """
        formatted = "\n\n".join([
            f"{arg['party'].upper()}: {arg['argument']}"
            for arg in arguments
        ])
        
        prompt = Prompts.JUDGE_SUMMARY_PROMPT.format(context=formatted)
        return self.generate(prompt)
    
    def open_court(self, case_title: str) -> str:
        """Generate the court opening statement."""
        return Prompts.JUDGE_OPEN_COURT.format(case_title=case_title)
