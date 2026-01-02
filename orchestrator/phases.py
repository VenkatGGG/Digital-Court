"""
orchestrator/phases.py - Trial Phases

Enum and utilities for trial phase management.
"""

from enum import Enum


class TrialPhase(Enum):
    """Enumeration of trial phases."""
    
    AWAITING_COMPLAINT = "awaiting_complaint"
    COURT_ASSEMBLED = "court_assembled"
    OPENING_STATEMENTS = "opening_statements"
    ARGUMENTS = "arguments"
    JURY_DELIBERATION = "jury_deliberation"
    VERDICT = "verdict"
    ADJOURNED = "adjourned"
    
    @property
    def display_name(self) -> str:
        """Get human-readable phase name."""
        names = {
            self.AWAITING_COMPLAINT: "📄 Awaiting Complaint",
            self.COURT_ASSEMBLED: "⚖️ Court Assembled",
            self.OPENING_STATEMENTS: "🎬 Opening Statements",
            self.ARGUMENTS: "⚔️ Arguments",
            self.JURY_DELIBERATION: "👥 Jury Deliberation",
            self.VERDICT: "📜 Verdict",
            self.ADJOURNED: "🏛️ Adjourned"
        }
        return names.get(self, self.value)
    
    @property
    def is_active(self) -> bool:
        """Check if this is an active trial phase."""
        return self not in [self.AWAITING_COMPLAINT, self.ADJOURNED]
    
    @property
    def allows_next_round(self) -> bool:
        """Check if another argument round is allowed."""
        return self == self.ARGUMENTS
