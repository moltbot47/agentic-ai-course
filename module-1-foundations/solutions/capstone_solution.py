"""
Capstone Solution: Personal Research Agent
Module 1: Foundations of Agentic AI

This is a complete, production-quality reference solution for the capstone.
It demonstrates Honors-level implementation with all features.
"""

import os
import json
import math
from getpass import getpass
from datetime import datetime

import anthropic

if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = getpass("Enter your Anthropic API key: ")

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-5-20241022"
MEMORY_FILE = "research_memory.json"


# ── Tool Definitions (6 tools — Honors level) ──────────────────

tools = [
    {
        "name": "search_knowledge",
        "description": (
            "Search for information about a specific query. Returns relevant "
            "facts, data points, and context. Use this to gather research data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Specific search query for best results",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_report",
        "description": "Save a research report to a markdown file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Output filename (e.g. 'report.md')"},
                "content": {"type": "string", "description": "Full report content"},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "save_json",
        "description": "Save structured data as JSON. Use for machine-readable research output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Output filename (e.g. 'data.json')"},
                "data": {"type": "string", "description": "JSON string to save"},
            },
            "required": ["filename", "data"],
        },
    },
    {
        "name": "get_current_datetime",
        "description": "Get the current date and time for timestamps.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "save_memory",
        "description": "Save a finding to persistent memory for future reference.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Topic label for this memory"},
                "value": {"type": "string", "description": "The information to remember"},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall_memory",
        "description": "Recall previously saved research by topic key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Topic label to recall"}
            },
            "required": ["key"],
        },
    },
]


# ── Tool Implementations ───────────────────────────────────────

def search_knowledge(query: str) -> str:
    """Simulated knowledge search using a separate Claude call."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a research database. Return factual, detailed information "
            "with specific data points, dates, and statistics where available. "
            "Format as a numbered list of key facts. If uncertain, say so."
        ),
        messages=[{"role": "user", "content": f"Search: {query}"}],
    )
    return response.content[0].text


def save_report(filename: str, content: str) -> str:
    """Save report to a markdown file."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Report saved to '{filename}' ({len(content)} chars)"
    except Exception as e:
        return f"Error saving report: {e}"


def save_json(filename: str, data: str) -> str:
    """Save structured JSON data to a file."""
    try:
        parsed = json.loads(data)
        with open(filename, "w") as f:
            json.dump(parsed, f, indent=2)
        return f"JSON saved to '{filename}'"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"
    except Exception as e:
        return f"Error: {e}"


def get_current_datetime() -> str:
    """Get current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")


def _load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_memory(key: str, value: str) -> str:
    """Save to persistent memory."""
    store = _load_memory()
    store[key] = {"value": value, "saved_at": datetime.now().isoformat()}
    with open(MEMORY_FILE, "w") as f:
        json.dump(store, f, indent=2)
    return f"Memory saved: '{key}'"


def recall_memory(key: str) -> str:
    """Recall from persistent memory."""
    store = _load_memory()
    if key in store:
        entry = store[key]
        return f"{entry['value']} (saved: {entry['saved_at']})"
    return f"No memory for '{key}'."


TOOL_FUNCTIONS = {
    "search_knowledge": search_knowledge,
    "save_report": save_report,
    "save_json": save_json,
    "get_current_datetime": get_current_datetime,
    "save_memory": save_memory,
    "recall_memory": recall_memory,
}


# ── The Research Agent ──────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert research agent. When given a topic, follow this methodology:

1. PLAN: Generate 3-5 specific research questions that, together, give a comprehensive understanding of the topic.

2. RESEARCH: For each question, use the search_knowledge tool to gather information. Use specific, targeted queries for best results.

3. ANALYZE: For each finding, assess your confidence level:
   - HIGH: Well-established fact with broad consensus
   - MEDIUM: Generally accepted but with some debate or uncertainty
   - LOW: Emerging area, limited data, or conflicting sources

4. SYNTHESIZE: Produce a structured research report with these sections:
   - Title and Date (use get_current_datetime)
   - Executive Summary (3-4 sentences)
   - Research Questions (numbered list)
   - Key Findings (with confidence levels)
   - Analysis and Connections
   - Knowledge Gaps and Follow-Up Questions
   - Methodology (brief description of your approach)
   - Self-Evaluation (rate your research: thoroughness, coverage, limitations)

5. SAVE:
   - Save the full report as markdown using save_report
   - Save structured findings as JSON using save_json
   - Save key findings to memory using save_memory

Be thorough but efficient. Use 3-5 searches, not more. Quality over quantity."""


def run_research_agent(
    topic: str,
    max_iterations: int = 20,
    verbose: bool = True,
) -> str:
    """Run the research agent on a given topic.

    Args:
        topic: The research topic to investigate.
        max_iterations: Maximum tool-use cycles.
        verbose: Print step-by-step reasoning.

    Returns:
        The agent's final response.
    """
    user_message = f"Research the following topic and produce a comprehensive report: {topic}"
    messages = [{"role": "user", "content": user_message}]
    iteration = 0
    tools_used: list[str] = []

    if verbose:
        print(f"\n{'='*60}")
        print(f"RESEARCH TOPIC: {topic}")
        print(f"{'='*60}")

    while iteration < max_iterations:
        iteration += 1

        if verbose:
            print(f"\n── Step {iteration} ──")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            final = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final += block.text
            if verbose:
                print(f"\n{'='*60}")
                print(f"✓ Research complete in {iteration} steps")
                print(f"Tools used: {tools_used}")
                print(f"Unique tools: {list(set(tools_used))}")
                print(f"{'='*60}")
            return final

        tool_results = []
        for block in response.content:
            if hasattr(block, "text") and block.text:
                if verbose:
                    print(f"  💭 {block.text[:200]}")

            if block.type == "tool_use":
                name = block.name
                inp = block.input
                tools_used.append(name)

                if verbose:
                    print(f"  🔧 {name}({json.dumps(inp)[:100]})")

                func = TOOL_FUNCTIONS.get(name)
                if func:
                    try:
                        result = func(**inp)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = f"Error: Unknown tool '{name}'"

                if verbose:
                    display = result[:150] + "..." if len(str(result)) > 150 else result
                    print(f"  📋 {display}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    return "Error: Hit max iterations."


# ── Run the solution ────────────────────────────────────────────

if __name__ == "__main__":
    result = run_research_agent(
        "The impact of AI agents on software development productivity in 2024-2025"
    )

    print("\n" + "=" * 60)
    print("AGENT FINAL RESPONSE:")
    print("=" * 60)
    print(result)

    # Check outputs
    print("\n=== Generated Files ===")
    for f in os.listdir("."):
        if f.endswith((".md", ".json")) and "research" in f.lower():
            print(f"  {f} ({os.path.getsize(f)} bytes)")

    # Cleanup (optional)
    # for f in ["research_memory.json"]:
    #     if os.path.exists(f):
    #         os.remove(f)
