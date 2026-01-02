"""
Lex Umbra - Agents Package

AI agents for the trial simulation: Judge, Lawyers, and Jurors.
"""

from agents.judge import JudgeAgent
from agents.lawyer import LawyerAgent
from agents.juror import JurorBrain, JurorSwarm

__all__ = ["JudgeAgent", "LawyerAgent", "JurorBrain", "JurorSwarm"]
