"""
ui/styles.py - JUSTICIA EX MACHINA: The Weight of Algorithmic Justice

A strikingly minimal design system that embodies the tension between
ancient judicial tradition and cold computational precision.

Design Philosophy: "Judicial Minimalism"
  - The gravitas of black robes and marble halls
  - The exactitude of legal documents
  - The coldness of algorithmic decision-making
  - Extreme negative space, purposeful typography

Color System:
  - Canvas: Near-black (#0B0B0B) - Judicial robes
  - Surface: Off-black (#141414) - Depth and layering
  - Text: Warm cream (#EDE8E0) - Aged parchment
  - Accent: Muted brass (#8B7355) - Scales of justice
  - Plaintiff: Deep wine (#4A1C1C) - Subdued aggression
  - Defense: Deep slate (#1C2A4A) - Calm stability
"""


def get_css() -> str:
    """Get the complete CSS for Justicia Ex Machina."""
    return """
<style>
    /* ══════════════════════════════════════════════════════════════════════════
       TYPOGRAPHY - Classical Meets Computational
       ══════════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&family=IBM+Plex+Mono:wght@300;400;500&family=Spectral:ital,wght@0,300;0,400;0,500;1,300;1,400&display=swap');

    :root {
        /* The Ink & Parchment Palette */
        --canvas: #0B0B0B;
        --surface: #141414;
        --surface-elevated: #1A1A1A;
        --surface-hover: #1F1F1F;

        --text-primary: #EDE8E0;
        --text-secondary: #A8A29E;
        --text-tertiary: #6B6560;
        --text-muted: #4A4845;

        --accent: #8B7355;
        --accent-dim: #6B5A48;
        --accent-glow: rgba(139, 115, 85, 0.08);

        --plaintiff: #4A1C1C;
        --plaintiff-text: #D4A5A5;
        --plaintiff-border: #6B2A2A;

        --defense: #1C2A4A;
        --defense-text: #A5B8D4;
        --defense-border: #2A3A6B;

        --verdict: #2A4A2A;
        --verdict-text: #A5D4A5;

        --border: rgba(139, 115, 85, 0.12);
        --border-subtle: rgba(255, 255, 255, 0.04);
        --border-strong: rgba(139, 115, 85, 0.25);

        /* Typography Scale */
        --font-display: 'Cormorant Garamond', Georgia, serif;
        --font-body: 'Spectral', Georgia, serif;
        --font-mono: 'IBM Plex Mono', 'Consolas', monospace;

        /* Spacing Scale */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2.5rem;
        --space-2xl: 4rem;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       GLOBAL FOUNDATION
       ══════════════════════════════════════════════════════════════════════════ */
    .stApp {
        background: var(--canvas) !important;
    }

    .main .block-container {
        padding: 1.5rem 2rem 3rem 2rem !important;
        max-width: 100% !important;
    }

    /* Hide Streamlit chrome */
    /* Hide Streamlit chrome but keep sidebar toggle accessible */
    #MainMenu, footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       TYPOGRAPHY SYSTEM
       ══════════════════════════════════════════════════════════════════════════ */

    /* Display headings - Classical serif */
    h1, h2, h3, .display-text {
        font-family: var(--font-display) !important;
        font-weight: 400 !important;
        letter-spacing: 0.02em !important;
        color: var(--text-primary) !important;
    }

    /* Body text - Refined serif */
    p, span, div, li, .stMarkdown {
        font-family: var(--font-body) !important;
        font-weight: 400;
        letter-spacing: 0.01em;
        line-height: 1.7;
        color: var(--text-secondary);
    }

    /* Monospace - Technical precision */
    code, pre, .mono-text {
        font-family: var(--font-mono) !important;
        font-size: 0.85rem;
        letter-spacing: -0.01em;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       THE HEADER - Restrained Authority
       ══════════════════════════════════════════════════════════════════════════ */
    .court-header {
        text-align: center;
        padding: var(--space-xl) 0 var(--space-lg) 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: var(--space-xl);
    }

    .court-title {
        font-family: var(--font-display) !important;
        font-size: 2.5rem !important;
        font-weight: 300 !important;
        letter-spacing: 0.25em !important;
        text-transform: uppercase;
        color: var(--text-primary) !important;
        margin: 0 0 var(--space-sm) 0 !important;
    }

    .court-subtitle {
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        font-weight: 400;
        letter-spacing: 0.3em !important;
        text-transform: uppercase;
        color: var(--text-tertiary) !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       STATUS INDICATOR - Minimal Data Display
       ══════════════════════════════════════════════════════════════════════════ */
    .trial-status {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: var(--space-xl);
        padding: var(--space-md) var(--space-xl);
        background: var(--surface);
        border: 1px solid var(--border);
        margin: 0 auto var(--space-xl) auto;
        max-width: 700px;
    }

    .status-segment {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-xs);
    }

    .status-label {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--text-muted);
    }

    .status-value {
        font-family: var(--font-display) !important;
        font-size: 1rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        color: var(--accent);
    }

    .status-divider {
        width: 1px;
        height: 2rem;
        background: var(--border);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       THE BENCH - Judicial Authority
       ══════════════════════════════════════════════════════════════════════════ */
    .bench {
        background: var(--surface);
        border: 1px solid var(--border);
        border-top: 2px solid var(--accent);
        padding: var(--space-xl);
        margin: 0 auto var(--space-xl) auto;
        max-width: 900px;
        position: relative;
    }

    .bench::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 2px;
        background: var(--accent);
    }

    .bench-label {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-muted);
        text-align: center;
        margin-bottom: var(--space-lg);
    }

    .bench-content {
        font-family: var(--font-body) !important;
        font-size: 1.05rem;
        line-height: 1.9;
        color: var(--text-primary);
        text-align: center;
    }

    .bench-content strong {
        font-weight: 600;
        color: var(--accent);
    }

    .bench-content em {
        font-style: italic;
        color: var(--text-secondary);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       COUNSEL BOXES - Adversarial Symmetry
       ══════════════════════════════════════════════════════════════════════════ */
    .counsel-box {
        background: var(--surface);
        border: 1px solid var(--border-subtle);
        min-height: 420px;
        display: flex;
        flex-direction: column;
    }

    .counsel-box-plaintiff {
        border-left: 2px solid var(--plaintiff-border);
    }

    .counsel-box-defense {
        border-right: 2px solid var(--defense-border);
    }

    .counsel-header {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: var(--space-md) var(--space-lg);
        border-bottom: 1px solid var(--border-subtle);
    }

    .counsel-header-plaintiff {
        color: var(--plaintiff-text);
        background: rgba(74, 28, 28, 0.15);
    }

    .counsel-header-defense {
        color: var(--defense-text);
        background: rgba(28, 42, 74, 0.15);
        text-align: right;
    }

    .counsel-content {
        flex: 1;
        padding: var(--space-md);
        overflow-y: auto;
        max-height: 350px;
    }

    .counsel-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        font-family: var(--font-body) !important;
        font-style: italic;
        font-size: 0.85rem;
        color: var(--text-muted);
    }

    /* Argument entries */
    .argument-entry {
        margin-bottom: var(--space-md);
        padding-bottom: var(--space-md);
        border-bottom: 1px solid var(--border-subtle);
    }

    .argument-entry:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }

    .argument-round {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: var(--space-xs);
    }

    .argument-text {
        font-family: var(--font-body) !important;
        font-size: 0.9rem;
        line-height: 1.7;
        color: var(--text-primary);
    }

    .argument-plaintiff .argument-text {
        border-left: 2px solid var(--plaintiff-border);
        padding-left: var(--space-md);
    }

    .argument-defense .argument-text {
        border-right: 2px solid var(--defense-border);
        padding-right: var(--space-md);
        text-align: right;
    }

    /* Collapsible arguments */
    .argument-collapse {
        background: transparent;
        border: 1px solid var(--border-subtle);
        margin-bottom: var(--space-sm);
        overflow: hidden;
    }

    .argument-collapse summary {
        padding: var(--space-sm) var(--space-md);
        cursor: pointer;
        font-family: var(--font-mono) !important;
        font-size: 0.75rem;
        color: var(--text-secondary);
        list-style: none;
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        transition: background 0.15s ease;
    }

    .argument-collapse summary::-webkit-details-marker {
        display: none;
    }

    .argument-collapse summary::before {
        content: '+';
        font-family: var(--font-mono);
        font-size: 0.8rem;
        color: var(--text-muted);
        transition: transform 0.15s ease;
    }

    .argument-collapse[open] summary::before {
        content: '-';
    }

    .argument-collapse summary:hover {
        background: var(--surface-hover);
    }

    .argument-collapse-content {
        padding: var(--space-md);
        background: rgba(0, 0, 0, 0.2);
        border-top: 1px solid var(--border-subtle);
        font-family: var(--font-body) !important;
        font-size: 0.85rem;
        line-height: 1.7;
        color: var(--text-primary);
        max-height: 200px;
        overflow-y: auto;
    }

    .argument-collapse-plaintiff {
        border-left: 2px solid var(--plaintiff-border);
    }

    .argument-collapse-defense {
        border-left: 2px solid var(--defense-border);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       EVIDENCE STAND - Documentary Display
       ══════════════════════════════════════════════════════════════════════════ */
    .evidence-box {
        background: var(--surface);
        border: 1px solid var(--border-subtle);
        min-height: 420px;
    }

    .evidence-header {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: var(--space-md) var(--space-lg);
        border-bottom: 1px solid var(--border-subtle);
        text-align: center;
    }

    .evidence-content {
        padding: var(--space-lg);
    }

    .case-title-display {
        font-family: var(--font-display) !important;
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-primary);
        text-align: center;
        padding: var(--space-md);
        border: 1px solid var(--border);
        margin-bottom: var(--space-lg);
        background: var(--surface-elevated);
    }

    .case-excerpt {
        font-family: var(--font-body) !important;
        font-size: 0.85rem;
        line-height: 1.8;
        color: var(--text-secondary);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       THE JURY - Collective Judgment
       ══════════════════════════════════════════════════════════════════════════ */
    .jury-section {
        background: var(--surface);
        border: 1px solid var(--border-subtle);
        border-top: 2px solid var(--text-muted);
        padding: var(--space-lg);
        margin-top: var(--space-xl);
    }

    .jury-label {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-muted);
        text-align: center;
        margin-bottom: var(--space-lg);
    }

    .jury-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: var(--space-md);
    }

    @media (max-width: 1200px) {
        .jury-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 768px) {
        .jury-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .juror {
        background: var(--surface-elevated);
        border: 1px solid var(--border-subtle);
        padding: var(--space-md);
        text-align: center;
        transition: border-color 0.2s ease;
    }

    .juror:hover {
        border-color: var(--border);
    }

    .juror-plaintiff {
        border-top: 2px solid var(--plaintiff-border);
    }

    .juror-defense {
        border-top: 2px solid var(--defense-border);
    }

    .juror-neutral {
        border-top: 2px solid var(--text-muted);
    }

    .juror-id {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        margin-bottom: var(--space-xs);
    }

    .juror-name {
        font-family: var(--font-display) !important;
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: var(--space-xs);
    }

    .juror-role {
        font-family: var(--font-body) !important;
        font-size: 0.7rem;
        color: var(--text-tertiary);
        font-style: italic;
        margin-bottom: var(--space-sm);
    }

    /* Sentiment bar - minimal visualization */
    .sentiment-track {
        height: 4px;
        background: var(--surface);
        margin: var(--space-sm) 0;
        position: relative;
        overflow: hidden;
    }

    .sentiment-track::before {
        content: '';
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 1px;
        background: var(--text-muted);
    }

    .sentiment-fill {
        height: 100%;
        transition: width 0.4s ease;
    }

    .sentiment-fill-plaintiff {
        background: linear-gradient(90deg, var(--surface), var(--plaintiff-border));
        margin-left: auto;
    }

    .sentiment-fill-defense {
        background: linear-gradient(90deg, var(--defense-border), var(--surface));
    }

    .juror-leaning {
        font-family: var(--font-mono) !important;
        font-size: 0.55rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-top: var(--space-xs);
    }

    .leaning-plaintiff {
        color: var(--plaintiff-text);
    }

    .leaning-defense {
        color: var(--defense-text);
    }

    .leaning-neutral {
        color: var(--text-muted);
    }

    .juror-thought {
        font-family: var(--font-body) !important;
        font-size: 0.75rem;
        font-style: italic;
        color: var(--text-tertiary);
        margin-top: var(--space-sm);
        line-height: 1.5;
        min-height: 2.5rem;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       VERDICT DISPLAY
       ══════════════════════════════════════════════════════════════════════════ */
    .verdict-display {
        background: var(--surface);
        border: 2px solid var(--accent);
        padding: var(--space-2xl);
        margin: var(--space-xl) auto;
        max-width: 600px;
        text-align: center;
    }

    .verdict-label {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: var(--space-md);
    }

    .verdict-text {
        font-family: var(--font-display) !important;
        font-size: 1.8rem;
        font-weight: 400;
        letter-spacing: 0.1em;
        color: var(--accent);
    }

    .verdict-details {
        font-family: var(--font-body) !important;
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-top: var(--space-lg);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       STREAMLIT COMPONENT OVERRIDES
       ══════════════════════════════════════════════════════════════════════════ */

    /* File uploader */
    .stFileUploader {
        background: var(--surface) !important;
        border: 1px dashed var(--border) !important;
        padding: var(--space-lg) !important;
    }

    .stFileUploader label {
        font-family: var(--font-mono) !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-tertiary) !important;
    }

    /* Buttons */
    .stButton > button {
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        background: var(--surface-elevated) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-secondary) !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: var(--surface-hover) !important;
        border-color: var(--accent-dim) !important;
        color: var(--accent) !important;
    }

    .stButton > button:disabled {
        background: var(--surface) !important;
        border-color: var(--border-subtle) !important;
        color: var(--text-muted) !important;
    }

    /* Expander */
    .stExpander {
        background: var(--surface) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    .stExpander details summary p {
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-secondary) !important;
    }

    /* Remove default arrow/chevron but add custom indicator */
    .stExpander details summary svg {
        display: none !important;
    }
    .stExpander details summary::marker {
        display: none !important;
        content: "";
    }
    .stExpander details summary::-webkit-details-marker {
        display: none !important;
    }
    .stExpander details summary span:first-child {
        display: none !important;
    }

    /* Custom Chevron Indicator */
    .stExpander details summary {
        position: relative !important;
        padding-left: 1.5rem !important;
        list-style: none !important;
    }

    .stExpander details summary::after {
        content: '';
        position: absolute;
        left: 0.2rem;
        top: 0.5rem;
        width: 0.4rem;
        height: 0.4rem;
        border-right: 2px solid var(--text-muted);
        border-bottom: 2px solid var(--text-muted);
        transform: rotate(-45deg);
        transition: all 0.2s ease;
        transform-origin: center;
    }

    .stExpander details:hover summary::after {
        border-color: var(--accent);
    }

    .stExpander details[open] summary::after {
        transform: rotate(45deg);
        top: 0.4rem;
        border-color: var(--accent);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: var(--font-display) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        letter-spacing: 0.05em !important;
    }

    .sidebar-title {
        font-family: var(--font-display) !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: var(--accent) !important;
        letter-spacing: 0.1em !important;
        margin-bottom: var(--space-lg) !important;
    }

    /* Sidebar buttons */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-header"],
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="collapsedControl"] button {
        color: var(--text-secondary) !important;
    }

    button[data-testid="stSidebarCollapseButton"] svg,
    button[data-testid="baseButton-header"] svg,
    [data-testid="stSidebar"] button[kind="header"] svg,
    [data-testid="collapsedControl"] button svg {
        fill: var(--text-secondary) !important;
        stroke: var(--text-secondary) !important;
    }

    [data-testid="collapsedControl"] {
        background: var(--surface) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    [data-testid="collapsedControl"]:hover {
        background: var(--surface-hover) !important;
        border-color: var(--border) !important;
    }

    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background: var(--border) !important;
        margin: var(--space-lg) 0 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        gap: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-mono) !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.05em !important;
        color: var(--text-tertiary) !important;
        background: transparent !important;
        border: none !important;
        padding: var(--space-sm) var(--space-md) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
        background: transparent !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        font-size: 1.5rem !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: var(--font-mono) !important;
        font-size: 0.6rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }

    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--defense-border), var(--text-muted), var(--plaintiff-border)) !important;
    }

    /* Info/warning/success/error */
    .stAlert {
        font-family: var(--font-body) !important;
        border-radius: 0 !important;
    }

    /* Scrollbars - Minimal */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }

    ::-webkit-scrollbar-track {
        background: var(--surface);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-tertiary);
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ANIMATIONS - Purposeful & Subtle
       ══════════════════════════════════════════════════════════════════════════ */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: slideUp 0.3s ease forwards;
    }

    .fade-in {
        animation: fadeIn 0.2s ease forwards;
    }

    /* Typing cursor */
    .typing-cursor {
        display: inline-block;
        width: 2px;
        height: 1em;
        background: var(--accent);
        margin-left: 2px;
        animation: blink 0.8s step-end infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }

    /* ══════════════════════════════════════════════════════════════════════════
       STREAMING STATES
       ══════════════════════════════════════════════════════════════════════════ */
    .streaming-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        font-family: var(--font-mono) !important;
        font-size: 0.65rem;
        color: var(--text-muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .streaming-dot {
        width: 4px;
        height: 4px;
        background: var(--accent);
        border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }

    /* ══════════════════════════════════════════════════════════════════════════
       SPECIAL ELEMENTS
       ══════════════════════════════════════════════════════════════════════════ */

    /* Session status card in sidebar */
    .session-status {
        background: var(--surface-elevated);
        border: 1px solid var(--border-subtle);
        border-left: 2px solid var(--accent);
        padding: var(--space-md);
        font-family: var(--font-mono) !important;
        font-size: 0.75rem;
        line-height: 1.8;
    }

    .session-status strong {
        color: var(--text-secondary);
    }

    .session-status span {
        color: var(--text-tertiary);
    }

    /* Main toggle button */
    button[title="Toggle Sidebar Visibility"] {
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 999999 !important;
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-secondary) !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-size: 0.9rem !important;
    }

    button[title="Toggle Sidebar Visibility"]:hover {
        background: var(--surface-hover) !important;
        border-color: var(--accent-dim) !important;
        color: var(--accent) !important;
    }

</style>
"""


# Color mappings for programmatic use
AGENT_COLORS = {
    "plaintiff": {"bg": "#4A1C1C", "border": "#6B2A2A", "text": "#D4A5A5"},
    "defense": {"bg": "#1C2A4A", "border": "#2A3A6B", "text": "#A5B8D4"},
    "judge": {"bg": "#141414", "border": "#8B7355", "text": "#EDE8E0"},
    "juror": {"bg": "#1A1A1A", "border": "#4A4845", "text": "#A8A29E"},
    "system": {"bg": "#141414", "border": "#4A4845", "text": "#6B6560"}
}


def get_score_color(score: int) -> str:
    """Get color for a bias score (0-100 scale, 50 = neutral)."""
    if score < 40:
        return "#A5B8D4"  # Defense blue
    elif score > 60:
        return "#D4A5A5"  # Plaintiff wine
    return "#A8A29E"  # Neutral


def get_sentiment_class(score: int) -> str:
    """Get CSS class based on sentiment score."""
    if score > 55:
        return "juror-plaintiff"
    elif score < 45:
        return "juror-defense"
    return "juror-neutral"
