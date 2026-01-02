"""
agents/lawyer.py - Lawyer Agents

Attorney Sarah Chen (Plaintiff) and Attorney Marcus Webb (Defense).
"""

from typing import Optional

from agents.base import BaseAgent
from config.prompts import Prompts


class LawyerAgent(BaseAgent):
    """
    A Lawyer Agent - represents either Plaintiff or Defense.
    
    Goals:
    - Plaintiff: Maximize damages
    - Defense: Dismiss case or minimize damages
    """
    
    SIDES = {
        "plaintiff": {
            "name": "Attorney_Chen",
            "display_name": "ATTORNEY CHEN (Plaintiff)",
            "system": Prompts.PLAINTIFF_SYSTEM
        },
        "defense": {
            "name": "Attorney_Webb",
            "display_name": "ATTORNEY WEBB (Defense)",
            "system": Prompts.DEFENSE_SYSTEM
        }
    }
    
    def __init__(self, side: str, api_key: Optional[str] = None):
        """
        Initialize a Lawyer Agent.
        
        Args:
            side: Either "plaintiff" or "defense"
            api_key: Optional API key override
        """
        self.side = side.lower()
        
        if self.side not in self.SIDES:
            raise ValueError(f"Invalid side: {side}. Must be 'plaintiff' or 'defense'")
        
        config = self.SIDES[self.side]
        
        super().__init__(
            persona_name=config["name"],
            system_instruction=config["system"],
            api_key=api_key
        )
        
        self._display_name = config["display_name"]
    
    def get_role(self) -> str:
        return self.side
    
    @property
    def display_name(self) -> str:
        """Get the lawyer's display name for UI."""
        return self._display_name
    
    def make_opening_statement(self, case_facts: str) -> str:
        """
        Generate an opening statement.
        
        Args:
            case_facts: Summary of the case from the complaint
        
        Returns:
            Opening statement
        """
        if self.side == "plaintiff":
            prompt = Prompts.PLAINTIFF_OPENING.format(case_facts=case_facts)
        else:
            prompt = Prompts.DEFENSE_OPENING.format(case_facts=case_facts)
        
        return self.generate(prompt)
    
    def make_argument(self, case_facts: str) -> str:
        """
        Generate a main argument.
        
        Args:
            case_facts: Summary of the case
        
        Returns:
            Main argument
        """
        if self.side == "plaintiff":
            prompt = Prompts.PLAINTIFF_MAIN_ARGUMENT.format(case_facts=case_facts)
        else:
            # Defense responds to allegations
            prompt = Prompts.DEFENSE_OPENING.format(case_facts=case_facts)
        
        return self.generate(prompt)
    
    def respond_to_argument(self, opponent_argument: str, context: str = "") -> str:
        """
        Generate a rebuttal to opposing counsel.
        
        Args:
            opponent_argument: The opposing argument
            context: Additional case context
        
        Returns:
            Rebuttal argument
        """
        if self.side == "plaintiff":
            prompt = Prompts.PLAINTIFF_REBUTTAL.format(
                defense_argument=opponent_argument[:500]
            )
        else:
            prompt = Prompts.DEFENSE_REBUTTAL.format(
                plaintiff_argument=opponent_argument[:500]
            )
        
        return self.generate(prompt)
