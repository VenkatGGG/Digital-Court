LEX UMBRA - AI Legal Trial Simulation System
=============================================

A Multi-Agent AI system that simulates legal trial proceedings using 
Google Gemini 2.5 Flash with Real-Time Retrieval-Augmented Generation (RAG).


OVERVIEW
--------
Lex Umbra creates an interactive courtroom simulation where AI agents 
representing a Judge, Plaintiff Attorney, Defense Attorney, and a jury 
of six distinct personas argue cases based on uploaded complaint documents.
The system uses a vector database of Federal legal rules to ground 
judicial decisions in actual law.


SYSTEM REQUIREMENTS
-------------------
- Python 3.9+
- Google Gemini API key
- ChromaDB for vector storage
- Streamlit for web interface


INSTALLATION
------------
1. Clone the repository

2. Create and activate virtual environment:
   python -m venv venv
   source venv/bin/activate  (Unix/Mac)
   venv\Scripts\activate     (Windows)

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment:
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY

5. Populate the legal database:
   python -m ingest.ingest_cfr
   python -m ingest.ingest_rules


USAGE
-----
Start the application:
   streamlit run app.py

Then:
1. Upload a complaint document (PDF format)
2. Click "Initialize Court" to assemble the AI agents
3. Click "Begin Trial" to start opening statements
4. Progress through argument rounds
5. Send to jury for deliberation
6. Receive final verdict


PROJECT STRUCTURE
-----------------

Justicia-Ex-Machina/
|
|-- app.py                    Main Streamlit entry point
|
|-- config/                   Configuration
|   |-- settings.py           Application settings and environment
|   |-- prompts.py            All AI prompts centralized
|
|-- core/                     Core AI Engine
|   |-- gemini_client.py      Gemini API wrapper with retry logic
|   |-- rag.py                ChromaDB RAG query functions
|
|-- agents/                   AI Agent Classes
|   |-- base.py               Abstract base agent
|   |-- judge.py              Judge with legal database access
|   |-- lawyer.py             Plaintiff and Defense attorneys
|   |-- juror.py              Individual jurors and jury swarm
|
|-- orchestrator/             Trial State Machine
|   |-- phases.py             Trial phase enumeration
|   |-- trial.py              Central orchestration controller
|
|-- ui/                       User Interface
|   |-- styles.py             CSS styling
|   |-- components.py         Reusable UI components
|   |-- handlers.py           Streaming and action handlers
|
|-- ingest/                   Knowledge Base Population
|   |-- ingest_cfr.py         US Code Title 28 ingestion
|   |-- ingest_rules.py       Federal Rules of Civil Procedure
|
|-- data/                     Data Files
|   |-- jurors.json           Juror persona definitions
|   |-- judge_db/             ChromaDB vector database
|
|-- tests/                    Test Suite


ARCHITECTURE
------------

                    +------------------+
                    |    Streamlit     |
                    |    Frontend      |
                    |    (app.py)      |
                    +--------+---------+
                             |
                             v
              +--------------+--------------+
              |      Trial Orchestrator     |
              |   (orchestrator/trial.py)   |
              +--------------+--------------+
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
   +------+------+    +------+------+    +------+------+
   |   Judge     |    |   Lawyers   |    |   Jury      |
   |   Agent     |    |   (2)       |    |   Swarm     |
   +------+------+    +------+------+    +------+------+
          |                  |                  |
          |                  |                  |
          v                  v                  v
   +------+------+    +------+------+    +------+------+
   |   ChromaDB  |    |   Gemini    |    |   Gemini    |
   |   (RAG)     |    |   2.5 Flash |    |   Parallel  |
   +-------------+    +-------------+    +-------------+


DATA FLOW
---------

1. User uploads complaint PDF
2. Text extracted and stored as case facts
3. Orchestrator initializes all AI agents
4. Judge opens court, attorneys make opening statements
5. Attorneys argue in rounds, responses stream in real-time
6. Jury deliberates in parallel (concurrent API calls)
7. Judge summarizes and announces verdict
8. Transcript exportable as JSON


AGENT DESCRIPTIONS
------------------

JUDGE (Judge Evelyn Marshall)
   - 62-year-old Federal judge with 25 years on the bench
   - Accesses ChromaDB to cite specific FRCP rules
   - Maintains courtroom order and summarizes for jury

PLAINTIFF ATTORNEY (Sarah Chen)
   - 15 years civil litigation experience
   - Goal: Maximize damages awarded to client
   - Uses emotional appeals and vivid storytelling

DEFENSE ATTORNEY (Marcus Webb)
   - 20 years at major corporate law firm
   - Goal: Case dismissal or damage minimization
   - Uses logical argumentation and rule citation

JURY (6 Members)
   - Margaret Chen: 58, Retired Teacher, education-focused
   - Marcus Thompson: 34, Software Engineer, analytical
   - Patricia O'Brien: 67, Retired Nurse, healthcare-aware
   - James Kowalski: 52, Truck Driver, blue-collar perspective
   - Aisha Washington: 41, Social Worker, socially conscious
   - Robert Kim: 45, Restaurant Owner, business-minded

   Each juror has hidden biases that subtly influence their scoring.


CONFIGURATION
-------------

Environment Variables (in .env):
   GEMINI_API_KEY      Required. Your Google Gemini API key.
   GEMINI_MODEL        Optional. Model name (default: gemini-2.5-flash)

Settings (in config/settings.py):
   max_retries         API retry attempts (default: 3)
   max_argument_rounds Maximum argument rounds allowed (default: 5)
   parallel_jury_workers  Concurrent jury API calls (default: 6)


PROMPT CUSTOMIZATION
--------------------

All prompts are centralized in config/prompts.py for easy modification:
   - JUDGE_SYSTEM       Judge persona and instructions
   - PLAINTIFF_SYSTEM   Plaintiff attorney persona
   - DEFENSE_SYSTEM     Defense attorney persona
   - JUROR_SYSTEM_TEMPLATE  Template for juror personas
   - Opening, argument, and verdict prompt templates


API USAGE
---------

The system uses the google-genai SDK (not google-generativeai).

Streaming is used for real-time response display.
Non-streaming is used for parallel jury deliberation.

Exponential backoff with jitter handles rate limiting.


KNOWN LIMITATIONS
-----------------

- PDF extraction may miss complex formatting
- Jury scores are heuristic, not legally binding
- Model responses may occasionally break character
- ChromaDB similarity scores are distance-based


LICENSE
-------

MIT License. See LICENSE file for details.


ACKNOWLEDGMENTS
---------------

- Google Gemini for LLM capabilities
- ChromaDB for vector storage
- Streamlit for rapid prototyping
- Legal rules from public domain sources
