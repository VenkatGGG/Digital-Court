"""
api/voice_server.py - FastAPI WebSocket Voice Debate Server

Orchestrates real-time voice debate between Defense and Prosecutor AI agents,
streaming audio to connected clients.
"""

import os
import json
import asyncio
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Environment configuration
DEFENSE_API_URL = os.getenv("DEFENSE_API_URL", "http://localhost:8001/generate")
PROSECUTOR_API_URL = os.getenv("PROSECUTOR_API_URL", "http://localhost:8002/generate")
VOICE_SERVER_PORT = int(os.getenv("VOICE_SERVER_PORT", "8765"))

# Global transcript storage for Jury access
debate_transcript: list[dict] = []


@dataclass
class DebateSession:
    """Tracks state for a single debate session."""
    case_text: str
    transcript: list[dict] = field(default_factory=list)
    current_turn: int = 0
    is_active: bool = True
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())


app = FastAPI(
    title="Voice Courtroom Server",
    description="WebSocket server for live AI voice debates"
)

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def call_gpu_node(
    client: httpx.AsyncClient,
    url: str,
    agent: str,
    conversation_history: list[dict],
    case_text: str
) -> dict:
    """
    Call external GPU node to generate speech.

    Args:
        client: Async HTTP client
        url: GPU node endpoint URL
        agent: 'defense' or 'prosecutor'
        conversation_history: Previous turns in the debate
        case_text: The case facts

    Returns:
        dict with 'audio_base64' and 'text' keys
    """
    payload = {
        "agent": agent,
        "case_text": case_text,
        "conversation_history": conversation_history,
        "temperature": 0.8,
        "max_tokens": 500
    }

    try:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"GPU node returned error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"Failed to connect to GPU node: {str(e)}")


def get_agent_config(agent: str) -> tuple[str, str]:
    """Get URL and display name for an agent."""
    if agent == "defense":
        return DEFENSE_API_URL, "Defense Attorney"
    else:
        return PROSECUTOR_API_URL, "Prosecutor"


@app.websocket("/ws/voice-debate")
async def voice_debate_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for live voice debate.

    Protocol:
    1. Client sends: { "case_text": "..." }
    2. Server runs 4 turns (Defense -> Prosecutor -> Defense -> Prosecutor)
    3. For each turn, server sends:
       - { "status": "speaking", "agent": "defense|prosecutor" }
       - { "type": "audio", "agent": "...", "payload": "base64...", "text": "..." }
    4. After all turns: { "status": "complete", "transcript": [...] }
    5. On error: { "status": "error", "message": "..." }
    """
    await websocket.accept()

    session: Optional[DebateSession] = None

    try:
        # Wait for initial message with case text
        init_data = await websocket.receive_text()
        init_json = json.loads(init_data)

        case_text = init_json.get("case_text", "")
        if not case_text:
            await websocket.send_json({
                "status": "error",
                "message": "case_text is required"
            })
            await websocket.close()
            return

        session = DebateSession(case_text=case_text)

        # Send session started
        await websocket.send_json({
            "status": "started",
            "message": "Voice debate session initialized"
        })

        # Define turn order: Defense speaks first, then alternating
        turn_order = ["defense", "prosecutor", "defense", "prosecutor"]

        async with httpx.AsyncClient() as client:
            for turn_idx, agent in enumerate(turn_order):
                if not session.is_active:
                    break

                session.current_turn = turn_idx + 1
                url, display_name = get_agent_config(agent)

                # Notify client that agent is about to speak
                await websocket.send_json({
                    "status": "speaking",
                    "agent": agent,
                    "turn": session.current_turn,
                    "display_name": display_name
                })

                try:
                    # Call GPU node
                    result = await call_gpu_node(
                        client=client,
                        url=url,
                        agent=agent,
                        conversation_history=session.transcript,
                        case_text=case_text
                    )

                    audio_base64 = result.get("audio_base64", "")
                    text = result.get("text", "")

                    # Append to transcript
                    turn_record = {
                        "turn": session.current_turn,
                        "agent": agent,
                        "display_name": display_name,
                        "text": text,
                        "timestamp": datetime.now().isoformat()
                    }
                    session.transcript.append(turn_record)

                    # Send audio to client
                    await websocket.send_json({
                        "type": "audio",
                        "agent": agent,
                        "turn": session.current_turn,
                        "display_name": display_name,
                        "payload": audio_base64,
                        "text": text
                    })

                except Exception as e:
                    # GPU node failure - notify client and close
                    await websocket.send_json({
                        "status": "error",
                        "message": f"GPU node error for {display_name}: {str(e)}",
                        "agent": agent,
                        "turn": session.current_turn
                    })
                    session.is_active = False
                    break

                # Brief pause between turns for natural flow
                await asyncio.sleep(0.5)

        # Debate complete - save transcript globally
        if session.is_active:
            global debate_transcript
            debate_transcript = session.transcript.copy()

            await websocket.send_json({
                "status": "complete",
                "message": "Voice debate concluded",
                "transcript": session.transcript,
                "total_turns": len(session.transcript)
            })

    except WebSocketDisconnect:
        # Client disconnected
        if session:
            session.is_active = False

    except json.JSONDecodeError:
        await websocket.send_json({
            "status": "error",
            "message": "Invalid JSON format"
        })

    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        })

    finally:
        try:
            await websocket.close()
        except:
            pass


@app.get("/transcript")
async def get_transcript():
    """Get the current debate transcript for Jury access."""
    return {
        "transcript": debate_transcript,
        "count": len(debate_transcript)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "voice-courtroom"}


def run_server():
    """Run the voice server (for standalone execution)."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=VOICE_SERVER_PORT)


if __name__ == "__main__":
    run_server()
