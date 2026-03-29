# Capstone Project: Build a Personal Research Agent

## Project Brief

Build a fully functional AI agent that takes a research topic, autonomously investigates it using multiple tools, and produces a structured research report — all without human intervention after the initial prompt.

This capstone synthesizes everything from Module 1: the agent loop, tool-use, memory, multi-step reasoning, and evaluation.

## Requirements

### Minimum Viable Agent (Pass)
- [ ] Accepts a research topic from the user
- [ ] Generates at least 3 research questions about the topic
- [ ] Uses at least 2 tools to gather information (e.g., web search, file read, API call)
- [ ] Produces a structured report with sections: Summary, Key Findings, Sources
- [ ] Saves the report to a file

### Enhanced Agent (Distinction)
- [ ] All minimum requirements plus:
- [ ] Agent evaluates its own confidence level per finding (high/medium/low)
- [ ] Agent identifies gaps in its research and suggests follow-up questions
- [ ] Agent uses 3+ different tools
- [ ] Agent handles tool failures gracefully (retries or alternative approach)
- [ ] Report includes a methodology section explaining the agent's approach

### Outstanding Agent (Honors)
- [ ] All enhanced requirements plus:
- [ ] Agent maintains persistent memory across sessions
- [ ] Agent can compare new research with previous research on the same topic
- [ ] Agent produces output in multiple formats (markdown report + JSON data)
- [ ] Agent includes a self-evaluation section rating its own performance

## Suggested Tools to Implement

```python
# Tool 1: Web Search (simulated or real)
def search_web(query: str) -> str:
    """Search the web for information about a topic."""

# Tool 2: Read Document
def read_document(url_or_path: str) -> str:
    """Read and extract text from a document or webpage."""

# Tool 3: Save Report
def save_report(filename: str, content: str) -> str:
    """Save the research report to a file."""

# Tool 4: Get Current Date/Time
def get_current_datetime() -> str:
    """Get the current date and time for timestamping reports."""

# Tool 5 (Bonus): Query a Database
def query_knowledge_base(query: str) -> str:
    """Search a local knowledge base for previously saved research."""
```

## Evaluation Rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Agent Loop Implementation** | 20 | Agent correctly implements perceive → reason → act → observe loop |
| **Tool-Use** | 20 | Agent autonomously selects and uses appropriate tools |
| **Output Quality** | 20 | Report is well-structured, accurate, and useful |
| **Error Handling** | 15 | Agent handles failures, edge cases, and unexpected input |
| **Code Quality** | 15 | Clean, readable, well-commented code |
| **Creativity** | 10 | Novel approaches, additional features, thoughtful design |
| **Total** | **100** | |

**Grading Scale:**
- 90-100: Honors — exceptional work, production-quality agent
- 80-89: Distinction — strong implementation with enhanced features
- 70-79: Pass — meets all minimum requirements
- Below 70: Incomplete — revise and resubmit

## Starter Template

A starter notebook is provided in `labs/capstone_starter.ipynb` with:
- API setup boilerplate
- Tool definition templates
- Agent loop skeleton
- Report formatting helpers

## Submission

Submit the following:
1. Your completed Jupyter notebook (`.ipynb`)
2. Any generated reports from test runs
3. A brief reflection (3-5 sentences): What worked? What was hardest? What would you improve?

## Time Estimate
- **Setup & planning:** 20 minutes
- **Building the agent:** 60 minutes
- **Testing & refining:** 30 minutes
- **Documentation & reflection:** 10 minutes
- **Total:** ~2 hours

---

# Alternative Capstone: Intelligent Meeting Notes Agent

Choose this capstone if you want a different challenge. It covers the same Module 1 skills.

## Project Brief

Build an agent that takes meeting input (text transcript, pasted notes, or audio file), processes it autonomously, and produces structured meeting notes with action items, decisions, key discussion points, and follow-ups — all without human intervention after the initial input.

## What Makes This Agentic

A simple summarizer just shortens text. This agent:
- **Decides** what's an action item vs. a discussion point vs. a decision
- **Extracts** structured data (owners, deadlines, topics) from unstructured conversation
- **Uses tools** to transcribe audio, analyze text, and save outputs
- **Evaluates** its own output (did it catch everything?)

## Requirements

### Minimum Viable Agent (Pass)
- [ ] Accepts meeting transcript as text input
- [ ] Extracts action items with assigned owners (if mentioned)
- [ ] Identifies decisions made during the meeting
- [ ] Produces a structured summary with sections: Attendees, Key Discussion Points, Decisions, Action Items
- [ ] Saves the meeting notes to a file

### Enhanced Agent (Distinction)
- [ ] All minimum requirements plus:
- [ ] Transcribes audio files (MP3/WAV) to text using a transcription tool (Whisper API, AssemblyAI, or simulated)
- [ ] Detects deadlines and due dates mentioned in conversation
- [ ] Tags topics by category (engineering, design, business, etc.)
- [ ] Assigns priority (high/medium/low) to each action item
- [ ] Handles multiple meetings — saves to memory, can compare across sessions

### Outstanding Agent (Honors)
- [ ] All enhanced requirements plus:
- [ ] Generates follow-up email draft based on the action items
- [ ] Tracks action item completion across meetings (persistent memory)
- [ ] Produces output in multiple formats (Markdown notes + JSON data)
- [ ] Includes a "missed items" self-check — agent re-reads the transcript to verify it didn't miss anything
- [ ] Supports both audio file input AND pasted text input seamlessly

## Suggested Tools

```python
# Tool 1: Transcribe Audio (simulated or real)
def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file to text.

    For the capstone, you can simulate this by reading a .txt file
    that represents a transcript. For Honors level, integrate a
    real transcription API (OpenAI Whisper, AssemblyAI, or Deepgram).
    """

# Tool 2: Extract Action Items
def extract_action_items(transcript: str) -> str:
    """Analyze transcript and extract action items with owners and deadlines."""

# Tool 3: Save Meeting Notes
def save_notes(filename: str, content: str) -> str:
    """Save structured meeting notes to a file."""

# Tool 4: Get Current Date/Time
def get_current_datetime() -> str:
    """Get the current date and time for timestamping notes."""

# Tool 5: Save/Recall Memory
def save_memory(key: str, value: str) -> str:
    """Save meeting data to persistent memory for cross-session tracking."""

def recall_memory(key: str) -> str:
    """Recall previous meeting data."""

# Tool 6 (Bonus): Generate Follow-Up Email
def draft_email(recipients: str, action_items: str) -> str:
    """Draft a follow-up email summarizing action items and next steps."""
```

## Audio Transcription Options

For the audio transcription feature, choose one approach:

| Approach | Difficulty | Notes |
|----------|-----------|-------|
| **Simulated** (read .txt file) | Easy | Good for Pass level — just reads a pre-made transcript file |
| **OpenAI Whisper API** | Medium | `pip install openai` — reliable, supports MP3/WAV/M4A |
| **Local Whisper** | Advanced | `pip install openai-whisper` — runs locally, no API key needed, slower |
| **AssemblyAI** | Medium | `pip install assemblyai` — good accuracy, free tier available |

**Simulated approach (recommended for most students):**
```python
def transcribe_audio(file_path: str) -> str:
    """Simulate transcription by reading a text file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Audio file '{file_path}' not found."
```

## Sample Meeting Transcript (for testing)

Use this sample or paste your own:

```
Meeting: Sprint Planning — March 15, 2025
Attendees: Sarah (PM), James (Dev Lead), Priya (Designer), Marco (QA)

Sarah: Let's go through the backlog. The client wants the dashboard
redesign shipped by end of month. James, where are we on the API changes?

James: Backend is 80% done. I need two more days for the pagination
endpoint. I'll have it ready by Wednesday.

Sarah: Good. Priya, how's the new design system coming?

Priya: Components are done. I need to finalize the color tokens with
the client. I'll schedule a review call for Thursday.

Marco: I want to flag that we don't have test coverage for the new
filtering logic. I think we should add integration tests before we ship.

Sarah: Agreed. Marco, can you write up the test plan by Friday? James,
make sure the API responses match the new schema Priya designed.

James: Will do. One concern — the current deployment pipeline takes
45 minutes. Can we look at optimizing that?

Sarah: Let's make that a separate ticket. Not blocking for this sprint
but important. I'll create the ticket.

Decision: Ship dashboard redesign by March 31. Deployment optimization
is next sprint.

Sarah: Anything else? No? Let's wrap up. Next standup is Monday 10am.
```

## Evaluation Rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Transcript Processing** | 15 | Correctly ingests and parses meeting transcripts |
| **Information Extraction** | 25 | Accurately identifies action items, decisions, owners, deadlines |
| **Audio Support** | 10 | Handles audio input (simulated or real transcription) |
| **Agent Loop** | 15 | Multi-step processing with autonomous tool selection |
| **Output Quality** | 15 | Well-structured, actionable meeting notes |
| **Memory & Persistence** | 10 | Saves notes to file, optional cross-session tracking |
| **Code Quality** | 10 | Clean, documented, maintainable code |
| **Total** | **100** | |

## Submission

Same as the Research Agent capstone:
1. Your completed Jupyter notebook (`.ipynb`)
2. Generated meeting notes from at least 2 test runs
3. Reflection (3-5 sentences)
