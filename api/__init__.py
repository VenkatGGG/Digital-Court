"""
api - Voice Debate WebSocket Server
"""

from .voice_server import app as voice_app, debate_transcript

__all__ = ["voice_app", "debate_transcript"]
