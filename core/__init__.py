"""
Lex Umbra - Core Package

Core AI engine components including Gemini client and RAG tools.
"""

from core.gemini_client import GeminiBrain, GeminiBrainError
from core.rag import query_legal_db, get_legal_db

__all__ = ["GeminiBrain", "GeminiBrainError", "query_legal_db", "get_legal_db"]
