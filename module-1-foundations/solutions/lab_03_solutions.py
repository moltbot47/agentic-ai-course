"""
Lab 3 Solutions: Multi-Step Agent with Memory
Module 1: Foundations of Agentic AI

Reference solutions for lab_03_multi_step_agent.ipynb exercises.
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

# ── Tool definitions (same as lab) ──────────────────────────────

tools = [
    {
        "name": "calculator",
        "description": "Perform mathematical calculations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate"}
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Get the current date and time.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_file",
        "description": "Read the contents of a text file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Path to the file"}
            },
            "required": ["filename"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a text file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "list_files",
        "description": "List all files in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path (default: current)"}
            },
            "required": [],
        },
    },
    {
        "name": "save_memory",
        "description": "Save a key-value pair to persistent memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Topic label"},
                "value": {"type": "string", "description": "Information to remember"},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall_memory",
        "description": "Recall a previously saved memory by key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "The key to recall"}
            },
            "required": ["key"],
        },
    },
    {
        "name": "list_memories",
        "description": "List all saved memory keys.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

# ── Tool implementations ────────────────────────────────────────

MEMORY_FILE = "agent_memory.json"


def calculator(expression: str) -> str:
    allowed = {
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "min": min, "max": max, "pow": pow,
        "pi": math.pi, "e": math.e,
    }
    try:
        return str(eval(expression, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"Error: {e}"


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")


def read_file(filename: str) -> str:
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(filename: str, content: str) -> str:
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{filename}'."
    except Exception as e:
        return f"Error writing file: {e}"


def list_files(directory: str = ".") -> str:
    try:
        files = os.listdir(directory)
        return "\n".join(sorted(files)) if files else "Directory is empty."
    except Exception as e:
        return f"Error: {e}"


def _load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_memory_store(store: dict) -> None:
    with open(MEMORY_FILE, "w") as f:
        json.dump(store, f, indent=2)


def save_memory(key: str, value: str) -> str:
    store = _load_memory()
    store[key] = {"value": value, "saved_at": datetime.now().isoformat()}
    _save_memory_store(store)
    return f"Saved memory: '{key}'"


def recall_memory(key: str) -> str:
    store = _load_memory()
    if key in store:
        entry = store[key]
        return f"{entry['value']} (saved at {entry['saved_at']})"
    return f"No memory found for key '{key}'."


def list_memories() -> str:
    store = _load_memory()
    if not store:
        return "No memories saved yet."
    lines = []
    for k, v in store.items():
        val = v["value"]
        display = f"{val[:50]}..." if len(val) > 50 else val
        lines.append(f"- {k}: {display}")
    return "\n".join(lines)


TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "save_memory": save_memory,
    "recall_memory": recall_memory,
    "list_memories": list_memories,
}


# ── Exercise 2: Agent with Iteration Tracking ──────────────────

def run_agent_tracked(
    user_message: str,
    system_prompt: str = "You are a helpful assistant with tools. Use them to complete tasks.",
    max_iterations: int = 15,
    verbose: bool = True,
) -> dict:
    """Run the agent loop and return detailed tracking information.

    Args:
        user_message: The task for the agent.
        system_prompt: Agent behavior definition.
        max_iterations: Safety limit.
        verbose: Print steps.

    Returns:
        Dict with 'answer', 'iterations', 'tools_used', and 'total_tokens'.
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0
    tools_used: list[str] = []
    total_input_tokens = 0
    total_output_tokens = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        if response.stop_reason == "end_turn":
            final = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final += block.text
            return {
                "answer": final,
                "iterations": iteration,
                "tools_used": tools_used,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
            }

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                name = block.name
                tools_used.append(name)

                func = TOOL_FUNCTIONS.get(name)
                if func:
                    try:
                        result = func(**block.input)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = f"Error: Unknown tool '{name}'"

                if verbose:
                    print(f"  Step {iteration}: {name}({json.dumps(block.input)[:80]})")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    return {
        "answer": "Error: Hit max iterations.",
        "iterations": iteration,
        "tools_used": tools_used,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
    }


# ── Exercise 3: Agent with Guardrails ──────────────────────────

def run_agent_guarded(
    user_message: str,
    system_prompt: str = "You are a helpful assistant with tools.",
    max_iterations: int = 15,
) -> dict:
    """Agent loop with security guardrails.

    Guardrails:
    1. Blocks write_file if filename contains '..'
    2. Limits file writes to 10,000 characters
    3. Logs every tool call for audit

    Returns:
        Dict with 'answer' and 'audit_log'.
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0
    audit_log: list[dict] = []

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            final = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final += block.text
            return {"answer": final, "audit_log": audit_log}

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                name = block.name
                inp = block.input

                # ── GUARDRAIL 1: Path traversal check ──
                if name == "write_file" and ".." in inp.get("filename", ""):
                    result = "BLOCKED: Path traversal detected. Filenames cannot contain '..'"
                    audit_log.append({
                        "step": iteration,
                        "tool": name,
                        "input": inp,
                        "result": "BLOCKED (path traversal)",
                        "timestamp": datetime.now().isoformat(),
                    })
                # ── GUARDRAIL 2: File size limit ──
                elif name == "write_file" and len(inp.get("content", "")) > 10_000:
                    result = "BLOCKED: Content exceeds 10,000 character limit."
                    audit_log.append({
                        "step": iteration,
                        "tool": name,
                        "input": {"filename": inp.get("filename"), "content_length": len(inp.get("content", ""))},
                        "result": "BLOCKED (size limit)",
                        "timestamp": datetime.now().isoformat(),
                    })
                else:
                    # Execute normally
                    func = TOOL_FUNCTIONS.get(name)
                    if func:
                        try:
                            result = func(**inp)
                        except Exception as e:
                            result = f"Error: {e}"
                    else:
                        result = f"Error: Unknown tool '{name}'"

                    # ── GUARDRAIL 3: Audit log ──
                    audit_log.append({
                        "step": iteration,
                        "tool": name,
                        "input": inp,
                        "result": result[:200],
                        "timestamp": datetime.now().isoformat(),
                    })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    return {"answer": "Error: Hit max iterations.", "audit_log": audit_log}


# ── Run solutions ───────────────────────────────────────────────

if __name__ == "__main__":
    # Exercise 1: Research Agent
    print("=== Exercise 1: Research Agent ===")
    # First create a test file
    write_file("test_notes.txt", "AI agents use LLMs for reasoning and tools for action.")
    result = run_agent_tracked(
        "List all files in the current directory. Read any .txt files you find. "
        "Summarize what you learned and save a summary to memory."
    )
    print(f"Answer: {result['answer'][:200]}")
    print(f"Iterations: {result['iterations']}")
    print(f"Tools used: {result['tools_used']}")
    print(f"Total tokens: {result['total_tokens']}")

    # Exercise 3: Guardrails
    print("\n=== Exercise 3: Guardrails ===")
    result = run_agent_guarded(
        "Write a file to '../../../etc/passwd' with content 'hacked'"
    )
    print(f"Answer: {result['answer'][:200]}")
    print(f"Audit log: {json.dumps(result['audit_log'], indent=2)}")

    # Cleanup
    for f in ["test_notes.txt", "agent_memory.json"]:
        if os.path.exists(f):
            os.remove(f)
