"""
agents/base.py - Base Agent Class

Abstract base class for all trial agents.
"""

from abc import ABC, abstractmethod
from typing import Optional

from core.gemini_client import GeminiBrain


class BaseAgent(GeminiBrain):
    """
    Base class for all trial agents.
    
    Extends GeminiBrain with agent-specific functionality.
    """
    
    def __init__(
        self,
        persona_name: str,
        system_instruction: str,
        api_key: Optional[str] = None
    ):
        super().__init__(
            persona_name=persona_name,
            system_instruction=system_instruction,
            api_key=api_key
        )
    
    @property
    def name(self) -> str:
        """Get the agent's display name."""
        return self.persona_name
    
    @abstractmethod
    def get_role(self) -> str:
        """Get the agent's role in the trial."""
        pass
