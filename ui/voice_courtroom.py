"""
ui/voice_courtroom.py - Live Voice Courtroom Component

A Streamlit component that renders the voice courtroom interface with
WebSocket-powered real-time audio streaming between Defense and Prosecutor.
"""

import os
import streamlit as st
import streamlit.components.v1 as components

# Configuration
VOICE_SERVER_PORT = int(os.getenv("VOICE_SERVER_PORT", "8765"))
VOICE_SERVER_HOST = os.getenv("VOICE_SERVER_HOST", "localhost")


def get_voice_courtroom_css() -> str:
    """CSS for the voice courtroom - matches the judicial minimalism theme."""
    return """
    <style>
        .voice-courtroom {
            font-family: 'Spectral', Georgia, serif;
            background: var(--canvas, #0B0B0B);
            min-height: 500px;
            padding: 2rem;
            position: relative;
        }

        .voice-courtroom-title {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.5rem;
            font-weight: 300;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--text-primary, #EDE8E0);
            text-align: center;
            margin-bottom: 2rem;
        }

        .voice-arena {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 3rem;
            padding: 2rem 0;
        }

        .voice-avatar-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            transition: all 0.3s ease;
        }

        .voice-avatar {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        .voice-avatar-defense {
            background: var(--defense, #1C2A4A);
            border: 3px solid var(--defense-border, #2A3A6B);
            color: var(--defense-text, #A5B8D4);
        }

        .voice-avatar-prosecutor {
            background: var(--plaintiff, #4A1C1C);
            border: 3px solid var(--plaintiff-border, #6B2A2A);
            color: var(--plaintiff-text, #D4A5A5);
        }

        .voice-avatar.speaking {
            transform: scale(1.1);
            box-shadow: 0 0 40px rgba(139, 115, 85, 0.4);
        }

        .voice-avatar-defense.speaking {
            box-shadow: 0 0 40px rgba(42, 58, 107, 0.6);
            border-color: #4A6AAB;
        }

        .voice-avatar-prosecutor.speaking {
            box-shadow: 0 0 40px rgba(107, 42, 42, 0.6);
            border-color: #AB4A4A;
        }

        .voice-avatar-container.dimmed {
            opacity: 0.4;
        }

        .voice-avatar-container.dimmed .voice-avatar {
            transform: scale(0.95);
        }

        .voice-avatar-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-muted, #4A4845);
        }

        .voice-avatar-defense-label {
            color: var(--defense-text, #A5B8D4);
        }

        .voice-avatar-prosecutor-label {
            color: var(--plaintiff-text, #D4A5A5);
        }

        .voice-center {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.5rem;
        }

        .voice-status {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--accent, #8B7355);
            padding: 0.5rem 1rem;
            border: 1px solid var(--border, rgba(139, 115, 85, 0.12));
            background: var(--surface, #141414);
            min-width: 180px;
            text-align: center;
        }

        .voice-vs {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-tertiary, #6B6560);
            letter-spacing: 0.1em;
        }

        .voice-controls {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }

        .voice-btn {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 0.75rem 1.5rem;
            border: 1px solid var(--border, rgba(139, 115, 85, 0.12));
            background: var(--surface-elevated, #1A1A1A);
            color: var(--text-secondary, #A8A29E);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .voice-btn:hover:not(:disabled) {
            background: var(--surface-hover, #1F1F1F);
            border-color: var(--accent-dim, #6B5A48);
            color: var(--accent, #8B7355);
        }

        .voice-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .voice-btn-primary {
            background: var(--accent, #8B7355);
            color: var(--canvas, #0B0B0B);
            border-color: var(--accent, #8B7355);
        }

        .voice-btn-primary:hover:not(:disabled) {
            background: var(--accent-dim, #6B5A48);
            color: var(--text-primary, #EDE8E0);
        }

        .voice-btn-danger {
            border-color: var(--plaintiff-border, #6B2A2A);
            color: var(--plaintiff-text, #D4A5A5);
        }

        .voice-btn-danger:hover:not(:disabled) {
            background: var(--plaintiff, #4A1C1C);
        }

        .voice-transcript {
            margin-top: 2rem;
            padding: 1rem;
            background: var(--surface, #141414);
            border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.04));
            max-height: 200px;
            overflow-y: auto;
        }

        .voice-transcript-title {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.6rem;
            font-weight: 500;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--text-muted, #4A4845);
            margin-bottom: 0.75rem;
        }

        .voice-transcript-entry {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.04));
        }

        .voice-transcript-entry:last-child {
            border-bottom: none;
        }

        .voice-transcript-agent {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.65rem;
            font-weight: 500;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }

        .voice-transcript-defense {
            color: var(--defense-text, #A5B8D4);
        }

        .voice-transcript-prosecutor {
            color: var(--plaintiff-text, #D4A5A5);
        }

        .voice-transcript-text {
            font-family: 'Spectral', Georgia, serif;
            font-size: 0.85rem;
            line-height: 1.6;
            color: var(--text-secondary, #A8A29E);
        }

        .voice-error {
            background: var(--plaintiff, #4A1C1C);
            border: 1px solid var(--plaintiff-border, #6B2A2A);
            color: var(--plaintiff-text, #D4A5A5);
            padding: 1rem;
            margin-top: 1rem;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.8rem;
        }

        /* Pulse animation for speaking indicator */
        @keyframes voicePulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .speaking-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-left: 0.5rem;
        }

        .speaking-dot {
            width: 6px;
            height: 6px;
            background: var(--accent, #8B7355);
            border-radius: 50%;
            animation: voicePulse 1s ease-in-out infinite;
        }

        .speaking-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .speaking-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
    </style>
    """


def get_voice_courtroom_js(ws_url: str, case_text: str) -> str:
    """JavaScript for WebSocket handling and audio playback."""
    # Escape the case text for JavaScript
    escaped_case = case_text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

    return f"""
    <script>
        (function() {{
            const WS_URL = '{ws_url}';
            const CASE_TEXT = '{escaped_case}';

            let ws = null;
            let audioQueue = [];
            let isPlaying = false;
            let currentAudio = null;

            const elements = {{
                defenseAvatar: document.getElementById('avatar-defense'),
                prosecutorAvatar: document.getElementById('avatar-prosecutor'),
                defenseContainer: document.getElementById('container-defense'),
                prosecutorContainer: document.getElementById('container-prosecutor'),
                status: document.getElementById('voice-status'),
                startBtn: document.getElementById('btn-start'),
                stopBtn: document.getElementById('btn-stop'),
                transcript: document.getElementById('voice-transcript-content'),
                errorBox: document.getElementById('voice-error')
            }};

            function setStatus(text) {{
                if (elements.status) {{
                    elements.status.textContent = text;
                }}
            }}

            function showError(message) {{
                if (elements.errorBox) {{
                    elements.errorBox.textContent = message;
                    elements.errorBox.style.display = 'block';
                }}
            }}

            function hideError() {{
                if (elements.errorBox) {{
                    elements.errorBox.style.display = 'none';
                }}
            }}

            function setSpeaking(agent) {{
                // Reset both
                elements.defenseContainer?.classList.remove('dimmed');
                elements.prosecutorContainer?.classList.remove('dimmed');
                elements.defenseAvatar?.classList.remove('speaking');
                elements.prosecutorAvatar?.classList.remove('speaking');

                if (agent === 'defense') {{
                    elements.defenseAvatar?.classList.add('speaking');
                    elements.prosecutorContainer?.classList.add('dimmed');
                }} else if (agent === 'prosecutor') {{
                    elements.prosecutorAvatar?.classList.add('speaking');
                    elements.defenseContainer?.classList.add('dimmed');
                }}
            }}

            function resetAvatars() {{
                elements.defenseContainer?.classList.remove('dimmed');
                elements.prosecutorContainer?.classList.remove('dimmed');
                elements.defenseAvatar?.classList.remove('speaking');
                elements.prosecutorAvatar?.classList.remove('speaking');
            }}

            function addTranscriptEntry(agent, text) {{
                if (!elements.transcript) return;

                const entry = document.createElement('div');
                entry.className = 'voice-transcript-entry';

                const agentLabel = document.createElement('div');
                agentLabel.className = 'voice-transcript-agent voice-transcript-' + agent;
                agentLabel.textContent = agent === 'defense' ? 'Defense Attorney' : 'Prosecutor';

                const textContent = document.createElement('div');
                textContent.className = 'voice-transcript-text';
                textContent.textContent = text;

                entry.appendChild(agentLabel);
                entry.appendChild(textContent);
                elements.transcript.appendChild(entry);

                // Scroll to bottom
                elements.transcript.scrollTop = elements.transcript.scrollHeight;
            }}

            function playNextAudio() {{
                if (audioQueue.length === 0) {{
                    isPlaying = false;
                    resetAvatars();
                    return;
                }}

                isPlaying = true;
                const {{ agent, payload, text }} = audioQueue.shift();

                setSpeaking(agent);

                // Decode base64 audio and play
                try {{
                    const audioData = atob(payload);
                    const arrayBuffer = new ArrayBuffer(audioData.length);
                    const view = new Uint8Array(arrayBuffer);
                    for (let i = 0; i < audioData.length; i++) {{
                        view[i] = audioData.charCodeAt(i);
                    }}

                    const blob = new Blob([arrayBuffer], {{ type: 'audio/mp3' }});
                    const audioUrl = URL.createObjectURL(blob);

                    currentAudio = new Audio(audioUrl);
                    currentAudio.onended = function() {{
                        URL.revokeObjectURL(audioUrl);
                        addTranscriptEntry(agent, text);
                        playNextAudio();
                    }};
                    currentAudio.onerror = function() {{
                        console.error('Audio playback error');
                        addTranscriptEntry(agent, text);
                        playNextAudio();
                    }};
                    currentAudio.play().catch(function(err) {{
                        console.error('Audio play failed:', err);
                        addTranscriptEntry(agent, text);
                        playNextAudio();
                    }});
                }} catch (e) {{
                    console.error('Audio decode error:', e);
                    addTranscriptEntry(agent, text);
                    playNextAudio();
                }}
            }}

            function startDebate() {{
                hideError();
                elements.transcript.innerHTML = '';
                audioQueue = [];

                try {{
                    ws = new WebSocket(WS_URL);

                    ws.onopen = function() {{
                        setStatus('Connected');
                        elements.startBtn.disabled = true;
                        elements.stopBtn.disabled = false;

                        // Send case text to start debate
                        ws.send(JSON.stringify({{ case_text: CASE_TEXT }}));
                    }};

                    ws.onmessage = function(event) {{
                        const data = JSON.parse(event.data);

                        switch (data.status) {{
                            case 'started':
                                setStatus('Debate Started');
                                break;

                            case 'speaking':
                                setStatus(data.display_name + ' Speaking...');
                                setSpeaking(data.agent);
                                break;

                            case 'complete':
                                setStatus('Debate Complete');
                                elements.startBtn.disabled = false;
                                elements.stopBtn.disabled = true;
                                break;

                            case 'error':
                                showError(data.message);
                                setStatus('Error');
                                resetAvatars();
                                elements.startBtn.disabled = false;
                                elements.stopBtn.disabled = true;
                                break;
                        }}

                        if (data.type === 'audio') {{
                            audioQueue.push({{
                                agent: data.agent,
                                payload: data.payload,
                                text: data.text
                            }});

                            if (!isPlaying) {{
                                playNextAudio();
                            }}
                        }}
                    }};

                    ws.onerror = function(error) {{
                        showError('WebSocket connection error');
                        setStatus('Connection Failed');
                        resetAvatars();
                        elements.startBtn.disabled = false;
                        elements.stopBtn.disabled = true;
                    }};

                    ws.onclose = function() {{
                        setStatus('Disconnected');
                        elements.startBtn.disabled = false;
                        elements.stopBtn.disabled = true;
                    }};

                }} catch (e) {{
                    showError('Failed to connect: ' + e.message);
                    setStatus('Connection Failed');
                }}
            }}

            function stopDebate() {{
                if (ws) {{
                    ws.close();
                    ws = null;
                }}

                if (currentAudio) {{
                    currentAudio.pause();
                    currentAudio = null;
                }}

                audioQueue = [];
                isPlaying = false;
                resetAvatars();
                setStatus('Stopped');
                elements.startBtn.disabled = false;
                elements.stopBtn.disabled = true;
            }}

            // Attach event listeners
            elements.startBtn?.addEventListener('click', startDebate);
            elements.stopBtn?.addEventListener('click', stopDebate);
        }})();
    </script>
    """


def render_voice_courtroom(case_text: str, height: int = 700) -> None:
    """
    Render the voice courtroom component.

    Args:
        case_text: The case facts to debate
        height: Component height in pixels
    """
    ws_url = f"ws://{VOICE_SERVER_HOST}:{VOICE_SERVER_PORT}/ws/voice-debate"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&family=Spectral:wght@300;400;500&display=swap" rel="stylesheet">
        {get_voice_courtroom_css()}
    </head>
    <body style="margin: 0; background: #0B0B0B;">
        <div class="voice-courtroom">
            <div class="voice-courtroom-title">Live Voice Courtroom</div>

            <div class="voice-arena">
                <!-- Defense Avatar -->
                <div id="container-defense" class="voice-avatar-container">
                    <div id="avatar-defense" class="voice-avatar voice-avatar-defense">
                        <span>&#9878;</span>
                    </div>
                    <div class="voice-avatar-label voice-avatar-defense-label">Defense</div>
                </div>

                <!-- Center Status -->
                <div class="voice-center">
                    <div id="voice-status" class="voice-status">Ready</div>
                    <div class="voice-vs">VS</div>
                </div>

                <!-- Prosecutor Avatar -->
                <div id="container-prosecutor" class="voice-avatar-container">
                    <div id="avatar-prosecutor" class="voice-avatar voice-avatar-prosecutor">
                        <span>&#9879;</span>
                    </div>
                    <div class="voice-avatar-label voice-avatar-prosecutor-label">Prosecutor</div>
                </div>
            </div>

            <!-- Controls -->
            <div class="voice-controls">
                <button id="btn-start" class="voice-btn voice-btn-primary">Start Debate</button>
                <button id="btn-stop" class="voice-btn voice-btn-danger" disabled>Stop</button>
            </div>

            <!-- Error Display -->
            <div id="voice-error" class="voice-error" style="display: none;"></div>

            <!-- Live Transcript -->
            <div class="voice-transcript">
                <div class="voice-transcript-title">Live Transcript</div>
                <div id="voice-transcript-content"></div>
            </div>
        </div>

        {get_voice_courtroom_js(ws_url, case_text)}
    </body>
    </html>
    """

    components.html(html_content, height=height, scrolling=False)


def render_voice_courtroom_placeholder() -> None:
    """Render a placeholder when no case is loaded."""
    st.markdown("""
    <div style="
        background: #141414;
        border: 1px solid rgba(139, 115, 85, 0.12);
        padding: 3rem;
        text-align: center;
    ">
        <div style="
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.5rem;
            color: #EDE8E0;
            margin-bottom: 1rem;
        ">Live Voice Courtroom</div>
        <div style="
            font-family: 'Spectral', Georgia, serif;
            font-size: 0.9rem;
            color: #6B6560;
            font-style: italic;
        ">Upload a case to enable voice debate</div>
    </div>
    """, unsafe_allow_html=True)
