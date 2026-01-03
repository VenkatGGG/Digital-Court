"""
ui/styles.py - LEX UMBRA: The Shadow Court Aesthetic

Cyber-noir judicial interface styling with dramatic visual hierarchy.
Color System:
  - Background: Dark Slate (#0e1117) - The "Shadow"
  - Judge: Muted Gold (#C5A059) - Authority
  - Plaintiff: Muted Crimson (#8B0000) - Aggression
  - Defense: Navy Blue (#000080) - Stability
  - Jury: Neutral Grey → Green (Convinced) / Red (Skeptical)
"""


def get_css() -> str:
    """Get the complete CSS for the Lex Umbra application."""
    return """
<style>
    /* ══════════════════════════════════════════════════════════════════════════
       IMPORTS & ROOT VARIABLES
       ══════════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

    :root {
        --shadow-black: #0a0c10;
        --slate-dark: #0e1117;
        --slate-mid: #1a1f2e;
        --slate-light: #262d40;

        --judge-gold: #C5A059;
        --judge-gold-dim: #8B7355;
        --judge-gold-glow: rgba(197, 160, 89, 0.3);

        --plaintiff-crimson: #8B0000;
        --plaintiff-crimson-light: #A52A2A;
        --plaintiff-glow: rgba(139, 0, 0, 0.25);

        --defense-navy: #000080;
        --defense-navy-light: #191970;
        --defense-glow: rgba(0, 0, 128, 0.25);

        --jury-neutral: #4a5568;
        --jury-agree: #2d5a3d;
        --jury-skeptic: #5a2d2d;

        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
        --text-dim: #64748b;

        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-glow: rgba(197, 160, 89, 0.15);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       GLOBAL RESETS & BASE STYLES
       ══════════════════════════════════════════════════════════════════════════ */
    .stApp {
        background: linear-gradient(180deg, var(--shadow-black) 0%, var(--slate-dark) 50%, var(--shadow-black) 100%) !important;
        background-attachment: fixed !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(ellipse at 50% 0%, rgba(197, 160, 89, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 0% 50%, rgba(139, 0, 0, 0.02) 0%, transparent 40%),
            radial-gradient(ellipse at 100% 50%, rgba(0, 0, 128, 0.02) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
    }

    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       TYPOGRAPHY
       ══════════════════════════════════════════════════════════════════════════ */
    h1, h2, h3, .header-text {
        font-family: 'Orbitron', monospace !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }

    p, span, div, .stMarkdown, li {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 400;
        letter-spacing: 0.02em;
    }

    code, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE A: THE HEADER
       ══════════════════════════════════════════════════════════════════════════ */
    .main-title {
        font-family: 'Orbitron', monospace !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        color: var(--judge-gold) !important;
        text-shadow:
            0 0 30px var(--judge-gold-glow),
            0 0 60px rgba(197, 160, 89, 0.15) !important;
        letter-spacing: 0.3em !important;
        margin-bottom: 0.25rem !important;
        padding-top: 0.5rem !important;
    }

    .main-subtitle {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        text-align: center !important;
        color: var(--text-dim) !important;
        letter-spacing: 0.5em !important;
        text-transform: uppercase !important;
        margin-bottom: 1.5rem !important;
    }

    /* Prominent Trial Status Banner */
    .trial-status-banner {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 2rem;
        background: linear-gradient(180deg, rgba(197, 160, 89, 0.15), rgba(197, 160, 89, 0.05));
        border: 2px solid var(--judge-gold-dim);
        border-radius: 8px;
        margin: 0 auto 1.5rem auto;
        max-width: 600px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 40px var(--judge-gold-glow);
        animation: status-glow 3s ease-in-out infinite;
    }

    @keyframes status-glow {
        0%, 100% { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 30px var(--judge-gold-glow); }
        50% { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 50px var(--judge-gold-glow); }
    }

    .status-phase-main {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .phase-icon {
        font-size: 1.5rem;
        animation: phase-pulse 2s ease-in-out infinite;
    }

    .phase-text {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--judge-gold);
        text-transform: uppercase;
        letter-spacing: 0.2em;
        text-shadow: 0 0 20px var(--judge-gold-glow);
    }

    .status-details {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }

    .status-bar {
        display: flex;
        justify-content: center;
        gap: 3rem;
        padding: 0.75rem 2rem;
        background: linear-gradient(90deg, transparent, var(--slate-mid), transparent);
        border-top: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 1.5rem;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .status-label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .status-value {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.2rem 0.5rem;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border-subtle);
        border-radius: 2px;
    }

    .phase-indicator {
        animation: phase-pulse 2s ease-in-out infinite;
    }

    @keyframes phase-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE B: THE JUDGE'S BENCH
       ══════════════════════════════════════════════════════════════════════════ */
    .judge-bench {
        background: linear-gradient(180deg, var(--slate-mid) 0%, var(--slate-dark) 100%);
        border: 2px solid var(--judge-gold-dim);
        border-top: 4px solid var(--judge-gold);
        border-radius: 4px;
        padding: 1.5rem 2rem;
        margin: 0 auto 1.5rem auto;
        max-width: 900px;
        position: relative;
        box-shadow:
            0 10px 40px rgba(0, 0, 0, 0.5),
            0 0 60px var(--judge-gold-glow),
            inset 0 1px 0 rgba(197, 160, 89, 0.1);
    }

    .judge-bench::before {
        content: '⚖';
        position: absolute;
        top: -1rem;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.5rem;
        background: var(--slate-dark);
        padding: 0 1rem;
        color: var(--judge-gold);
    }

    .judge-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.75rem;
        color: var(--judge-gold);
        text-transform: uppercase;
        letter-spacing: 0.3em;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-glow);
    }

    .judge-content {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem;
        color: var(--text-primary);
        line-height: 1.8;
        text-align: center;
    }

    .judge-content strong {
        color: var(--judge-gold);
        font-weight: 600;
    }

    .judge-content em {
        color: var(--text-secondary);
        font-style: italic;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE C: THE WELL - COUNSEL TABLES
       ══════════════════════════════════════════════════════════════════════════ */
    .counsel-table {
        background: linear-gradient(180deg, var(--slate-mid) 0%, rgba(14, 17, 23, 0.95) 100%);
        border-radius: 4px;
        padding: 1rem;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
        position: relative;
    }

    /* Plaintiff Styling */
    .plaintiff-table {
        border: 1px solid var(--plaintiff-crimson);
        border-left: 4px solid var(--plaintiff-crimson);
        box-shadow:
            -5px 0 30px var(--plaintiff-glow),
            inset 0 0 30px rgba(139, 0, 0, 0.05);
    }

    .plaintiff-table::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--plaintiff-crimson), transparent);
    }

    .plaintiff-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem;
        color: var(--plaintiff-crimson-light);
        text-transform: uppercase;
        letter-spacing: 0.25em;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(139, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .plaintiff-header::before {
        content: '🔴';
        font-size: 0.5rem;
    }

    /* Defense Styling */
    .defense-table {
        border: 1px solid var(--defense-navy);
        border-right: 4px solid var(--defense-navy);
        box-shadow:
            5px 0 30px var(--defense-glow),
            inset 0 0 30px rgba(0, 0, 128, 0.05);
    }

    .defense-table::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--defense-navy));
    }

    .defense-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem;
        color: var(--defense-navy-light);
        text-transform: uppercase;
        letter-spacing: 0.25em;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(0, 0, 128, 0.3);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.5rem;
    }

    .defense-header::after {
        content: '🔵';
        font-size: 0.5rem;
    }

    /* Message Bubbles */
    .counsel-message {
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        border-radius: 4px;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.95rem;
        line-height: 1.6;
        color: var(--text-primary);
        position: relative;
        animation: fadeInUp 0.4s ease forwards;
    }

    .plaintiff-message {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.15), rgba(139, 0, 0, 0.05));
        border-left: 2px solid var(--plaintiff-crimson);
    }

    .defense-message {
        background: linear-gradient(135deg, rgba(0, 0, 128, 0.05), rgba(0, 0, 128, 0.15));
        border-right: 2px solid var(--defense-navy);
        text-align: right;
    }

    .message-time {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem;
        color: var(--text-dim);
        margin-top: 0.5rem;
    }

    .message-sender {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.6rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }

    /* Evidence Stand */
    .evidence-stand {
        background: linear-gradient(180deg, var(--slate-mid) 0%, var(--slate-dark) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        padding: 1rem;
        min-height: 400px;
        position: relative;
    }

    .evidence-stand::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--text-dim), transparent);
    }

    .evidence-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.25em;
        text-align: center;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .evidence-content {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    .evidence-content strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE D: THE JURY BOX
       ══════════════════════════════════════════════════════════════════════════ */
    .jury-box {
        background: linear-gradient(180deg, var(--slate-dark) 0%, var(--shadow-black) 100%);
        border: 1px solid var(--border-subtle);
        border-top: 2px solid var(--jury-neutral);
        border-radius: 4px;
        padding: 1.25rem;
        margin-top: 1.5rem;
    }

    .jury-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.3em;
        text-align: center;
        margin-bottom: 1rem;
    }

    .juror-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.75rem;
    }

    @media (max-width: 1200px) {
        .juror-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 768px) {
        .juror-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .juror-card {
        background: linear-gradient(180deg, var(--slate-mid), var(--slate-dark));
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        padding: 0.75rem;
        text-align: center;
        position: relative;
        transition: all 0.3s ease;
        overflow: hidden;
    }

    .juror-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--jury-neutral);
        transition: background 0.3s ease;
    }

    .juror-card.leaning-plaintiff::before {
        background: linear-gradient(90deg, var(--plaintiff-crimson), var(--plaintiff-crimson-light));
    }

    .juror-card.leaning-defense::before {
        background: linear-gradient(90deg, var(--defense-navy-light), var(--defense-navy));
    }

    .juror-card:hover {
        transform: translateY(-2px);
        border-color: var(--text-dim);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
    }

    .juror-avatar {
        font-size: 1.75rem;
        margin-bottom: 0.25rem;
        filter: grayscale(20%);
    }

    .juror-name {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.6rem;
        color: var(--text-primary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.25rem;
    }

    .juror-occupation {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.55rem;
        color: var(--text-dim);
        margin-bottom: 0.5rem;
    }

    /* Sentiment Bar */
    .sentiment-container {
        margin: 0.5rem 0;
    }

    .sentiment-bar-bg {
        height: 6px;
        background: var(--slate-light);
        border-radius: 3px;
        overflow: hidden;
        position: relative;
    }

    .sentiment-bar-bg::before {
        content: '';
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 1px;
        background: var(--text-dim);
    }

    .sentiment-bar {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease, background 0.3s ease;
    }

    .sentiment-bar.plaintiff-leaning {
        background: linear-gradient(90deg, var(--slate-light), var(--plaintiff-crimson));
        margin-left: auto;
    }

    .sentiment-bar.defense-leaning {
        background: linear-gradient(90deg, var(--defense-navy), var(--slate-light));
    }

    .sentiment-label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.55rem;
        color: var(--text-dim);
        margin-top: 0.25rem;
    }

    /* Thought Bubble */
    .thought-bubble {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        padding: 0.5rem;
        margin-top: 0.5rem;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.7rem;
        font-style: italic;
        color: var(--text-secondary);
        line-height: 1.4;
        min-height: 2.5rem;
    }

    .thought-bubble::before {
        content: '💭 ';
        opacity: 0.5;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       CHAT MESSAGES (Legacy Support)
       ══════════════════════════════════════════════════════════════════════════ */
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
        font-family: 'Rajdhani', sans-serif !important;
        line-height: 1.7;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        animation: fadeInUp 0.4s ease forwards;
    }

    .plaintiff-msg {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.2) 0%, rgba(139, 0, 0, 0.1) 100%);
        border-left: 3px solid var(--plaintiff-crimson);
        color: #fca5a5;
    }

    .defense-msg {
        background: linear-gradient(135deg, rgba(0, 0, 128, 0.1) 0%, rgba(0, 0, 128, 0.2) 100%);
        border-left: 3px solid var(--defense-navy);
        color: #93c5fd;
    }

    .judge-msg {
        background: linear-gradient(135deg, rgba(197, 160, 89, 0.15) 0%, rgba(139, 115, 85, 0.1) 100%);
        border-left: 3px solid var(--judge-gold);
        color: #fef3c7;
    }

    .juror-msg {
        background: linear-gradient(135deg, rgba(74, 85, 104, 0.2) 0%, rgba(74, 85, 104, 0.1) 100%);
        border-left: 3px solid var(--jury-neutral);
        color: #cbd5e1;
    }

    .system-msg {
        background: linear-gradient(135deg, rgba(55, 65, 81, 0.3) 0%, rgba(55, 65, 81, 0.15) 100%);
        border-left: 3px solid #6b7280;
        color: #9ca3af;
        font-style: italic;
    }

    .agent-name {
        font-family: 'Orbitron', monospace !important;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }

    .score-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 2px;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem;
        font-weight: 500;
        margin-left: 0.75rem;
        background: rgba(0,0,0,0.3);
        border: 1px solid currentColor;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       STREAMLIT COMPONENT OVERRIDES
       ══════════════════════════════════════════════════════════════════════════ */
    .stFileUploader {
        background: var(--slate-mid) !important;
        border: 1px dashed var(--text-dim) !important;
        border-radius: 4px !important;
        padding: 1rem !important;
    }

    .stFileUploader label {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    .stButton > button {
        font-family: 'Orbitron', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        background: linear-gradient(180deg, var(--slate-light), var(--slate-mid)) !important;
        border: 1px solid var(--judge-gold-dim) !important;
        color: var(--judge-gold) !important;
        transition: all 0.3s ease !important;
        border-radius: 2px !important;
    }

    .stButton > button:hover {
        border-color: var(--judge-gold) !important;
        box-shadow: 0 0 20px var(--judge-gold-glow) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:disabled {
        background: var(--slate-dark) !important;
        border-color: var(--text-dim) !important;
        color: var(--text-dim) !important;
        cursor: not-allowed !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, var(--defense-navy), var(--judge-gold), var(--plaintiff-crimson)) !important;
    }

    .stSelectbox, .stTextInput, .stTextArea {
        font-family: 'Rajdhani', sans-serif !important;
    }

    .stExpander {
        background: var(--slate-mid) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 4px !important;
    }

    .stExpander > div > div > div > div {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--shadow-black), var(--slate-dark)) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Orbitron', monospace !important;
        color: var(--judge-gold) !important;
        font-size: 0.9rem !important;
    }

    .sidebar-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: var(--judge-gold) !important;
        margin-bottom: 1rem !important;
        letter-spacing: 0.15em !important;
    }

    /* Sidebar collapse button (three dots) - make it white */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-header"],
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="collapsedControl"] button {
        color: white !important;
    }

    button[data-testid="stSidebarCollapseButton"] svg,
    button[data-testid="baseButton-header"] svg,
    [data-testid="stSidebar"] button[kind="header"] svg,
    [data-testid="collapsedControl"] button svg {
        fill: white !important;
        stroke: white !important;
    }

    /* Collapsed sidebar expand button */
    [data-testid="collapsedControl"] {
        background: var(--slate-dark) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    [data-testid="collapsedControl"]:hover {
        background: var(--slate-mid) !important;
        border-color: var(--judge-gold-dim) !important;
    }

    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--judge-gold-dim), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.65rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: var(--slate-dark);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--slate-light);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-dim);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ANIMATIONS
       ══════════════════════════════════════════════════════════════════════════ */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: fadeInUp 0.4s ease forwards;
    }

    @keyframes typing {
        from { opacity: 0.3; }
        to { opacity: 1; }
    }

    .typing-indicator {
        animation: typing 0.5s ease-in-out infinite alternate;
    }

    @keyframes glow-pulse {
        0%, 100% {
            box-shadow: 0 0 20px var(--judge-gold-glow);
        }
        50% {
            box-shadow: 0 0 40px var(--judge-gold-glow), 0 0 60px rgba(197, 160, 89, 0.1);
        }
    }

    .glow-effect {
        animation: glow-pulse 3s ease-in-out infinite;
    }

    @keyframes borderGlow {
        0%, 100% {
            border-color: var(--judge-gold-dim);
        }
        50% {
            border-color: var(--judge-gold);
        }
    }

    .pulse-border {
        animation: borderGlow 2s ease-in-out infinite;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       CONTROL PANEL
       ══════════════════════════════════════════════════════════════════════════ */
    .control-panel {
        background: var(--slate-mid);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .control-header {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 0.75rem;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       SPECIAL EFFECTS
       ══════════════════════════════════════════════════════════════════════════ */
    .verdict-card {
        background: linear-gradient(180deg, rgba(197, 160, 89, 0.1), rgba(0, 0, 0, 0.3));
        border: 2px solid var(--judge-gold);
        border-radius: 4px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 0 40px var(--judge-gold-glow);
    }

    .verdict-text {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--judge-gold);
        text-transform: uppercase;
        letter-spacing: 0.2em;
    }

    .case-title {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.9rem;
        color: var(--text-primary);
        text-align: center;
        padding: 0.5rem 1rem;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border-subtle);
        border-radius: 2px;
        margin-bottom: 1rem;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       MESSAGE CARDS & COLLAPSIBLE LISTS
       ══════════════════════════════════════════════════════════════════════════ */
    
    .message-card-list {
        max-height: 300px;
        overflow-y: auto;
        padding: 0.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .message-card {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        padding: 0.6rem 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }

    .message-card:hover {
        border-color: var(--text-dim);
        transform: translateX(3px);
        background: rgba(0, 0, 0, 0.4);
    }

    .message-card.active {
        border-color: var(--judge-gold);
        box-shadow: 0 0 10px var(--judge-gold-glow);
    }

    .message-card.plaintiff-card {
        border-left: 3px solid var(--plaintiff-crimson);
    }

    .message-card.defense-card {
        border-left: 3px solid var(--defense-navy);
    }

    .message-card.juror-card-mini {
        border-left: 3px solid var(--jury-neutral);
    }

    /* Argument Card using HTML details/summary (no Material Icons needed) */
    .argument-card {
        background: rgba(10, 12, 16, 0.4);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        margin-bottom: 0.4rem;
        overflow: hidden;
        transition: border-color 0.2s ease;
    }

    .argument-card:hover {
        border-color: var(--border-glow);
    }

    .argument-card summary {
        padding: 0.7rem 0.8rem;
        cursor: pointer;
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-family: 'Rajdhani', sans-serif;
        font-weight: 500;
        list-style: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }

    .argument-card summary::-webkit-details-marker {
        display: none;
    }

    .argument-card summary::before {
        content: '▶';
        font-size: 0.7rem;
        transition: transform 0.2s ease;
    }

    .argument-card[open] summary::before {
        transform: rotate(90deg);
    }

    .argument-card summary:hover {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-primary);
    }

    .argument-card.plaintiff-card {
        border-left: 3px solid var(--plaintiff-crimson);
    }

    .argument-card.defense-card {
        border-left: 3px solid var(--defense-navy);
    }

    .argument-full {
        padding: 0.8rem;
        background: rgba(0, 0, 0, 0.2);
        border-top: 1px solid var(--border-subtle);
        font-size: 0.85rem;
        line-height: 1.5;
        color: var(--text-primary);
        max-height: 200px;
        overflow-y: auto;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }

    .card-time {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.6rem;
        color: var(--text-dim);
    }

    .card-label {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.55rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .card-preview {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.8rem;
        color: var(--text-primary);
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .card-expand-hint {
        font-size: 0.6rem;
        color: var(--text-dim);
        text-align: right;
        margin-top: 0.25rem;
    }

    /* Streaming Area */
    .streaming-area {
        background: linear-gradient(180deg, var(--slate-dark), rgba(0, 0, 0, 0.5));
        border: 1px dashed var(--border-subtle);
        border-radius: 4px;
        padding: 1rem;
        margin-top: 0.75rem;
        min-height: 80px;
        position: relative;
    }

    .streaming-area.active {
        border-color: var(--judge-gold);
        animation: streamPulse 1.5s ease-in-out infinite;
    }

    .streaming-area.plaintiff-stream {
        border-color: var(--plaintiff-crimson);
    }

    .streaming-area.defense-stream {
        border-color: var(--defense-navy);
    }

    @keyframes streamPulse {
        0%, 100% { border-color: var(--judge-gold-dim); }
        50% { border-color: var(--judge-gold); }
    }

    .streaming-label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.6rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .streaming-label::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--judge-gold);
        border-radius: 50%;
        animation: blink 1s ease-in-out infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .streaming-content {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.95rem;
        color: var(--text-primary);
        line-height: 1.6;
    }

    /* Expanded Transcript */
    .expanded-transcript {
        background: linear-gradient(180deg, var(--slate-mid), var(--slate-dark));
        border: 1px solid var(--judge-gold-dim);
        border-radius: 4px;
        padding: 1rem 1.25rem;
        margin-top: 1rem;
        position: relative;
        animation: fadeInUp 0.3s ease forwards;
    }

    .expanded-transcript::before {
        content: '';
        position: absolute;
        top: -8px;
        left: 2rem;
        width: 14px;
        height: 14px;
        background: var(--slate-mid);
        border-top: 1px solid var(--judge-gold-dim);
        border-left: 1px solid var(--judge-gold-dim);
        transform: rotate(45deg);
    }

    .expanded-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.75rem;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .expanded-title {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .expanded-close {
        font-size: 0.7rem;
        color: var(--text-dim);
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        border: 1px solid var(--border-subtle);
        border-radius: 2px;
        transition: all 0.2s ease;
    }

    .expanded-close:hover {
        border-color: var(--judge-gold);
        color: var(--judge-gold);
    }

    .expanded-content {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem;
        color: var(--text-primary);
        line-height: 1.8;
        max-height: 300px;
        overflow-y: auto;
    }

    /* Header Icons */
    .header-icon {
        font-size: 1rem;
        margin-right: 0.5rem;
    }

    .counsel-header-with-icon {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Juror Avatar Emojis */
    .juror-face {
        font-size: 2rem;
        margin-bottom: 0.25rem;
    }

</style>
"""


# Color mappings for programmatic use
AGENT_COLORS = {
    "plaintiff": {"bg": "#8B0000", "border": "#A52A2A", "text": "#fca5a5"},
    "defense": {"bg": "#000080", "border": "#191970", "text": "#93c5fd"},
    "judge": {"bg": "#8B7355", "border": "#C5A059", "text": "#fef3c7"},
    "juror": {"bg": "#4a5568", "border": "#64748b", "text": "#cbd5e1"},
    "system": {"bg": "#374151", "border": "#6b7280", "text": "#9ca3af"}
}


def get_score_color(score: int) -> str:
    """Get color for a bias score (0-100 scale, 50 = neutral)."""
    if score < 40:
        return "#000080"  # Navy (defense)
    elif score > 60:
        return "#8B0000"  # Crimson (plaintiff)
    return "#4a5568"  # Neutral grey


def get_sentiment_class(score: int) -> str:
    """Get CSS class based on sentiment score."""
    if score > 55:
        return "leaning-plaintiff"
    elif score < 45:
        return "leaning-defense"
    return ""
