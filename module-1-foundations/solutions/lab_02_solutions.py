"""
Lab 2 Solutions: Tool-Use Agent
Module 1: Foundations of Agentic AI

Reference solutions for lab_02_tool_use_agent.ipynb exercises.
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


# ── Base tools from the lab ─────────────────────────────────────

def calculator(expression: str) -> str:
    allowed = {
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "min": min, "max": max, "pow": pow,
        "pi": math.pi, "e": math.e,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "log": math.log, "log10": math.log10,
    }
    try:
        return str(eval(expression, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"Error: {e}"


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")


def word_counter(text: str) -> str:
    words = len(text.split())
    characters = len(text)
    sentences = text.count(".") + text.count("!") + text.count("?")
    return json.dumps({
        "words": words,
        "characters": characters,
        "sentences": max(sentences, 1),
    })


# ── Exercise 1: Add a New Tool (string_reverser) ───────────────

def string_reverser(text: str) -> str:
    """Reverse a string.

    Args:
        text: The text to reverse.

    Returns:
        The reversed text.
    """
    return text[::-1]


# Complete tools list with the new tool
tools = [
    {
        "name": "calculator",
        "description": "Perform mathematical calculations. Supports arithmetic, exponents, sqrt, trig, and log functions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate, e.g. '(15 * 24) + 7'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Get the current date and time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "word_counter",
        "description": "Count words, characters, and sentences in text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze",
                }
            },
            "required": ["text"],
        },
    },
    # NEW: Exercise 1 solution
    {
        "name": "string_reverser",
        "description": "Reverse any given text. Use when asked to reverse, flip, or mirror text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to reverse",
                }
            },
            "required": ["text"],
        },
    },
]

TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "word_counter": word_counter,
    "string_reverser": string_reverser,
}


def ask_agent(question: str) -> str:
    """Send a question, handle one tool call, return final answer."""
    messages = [{"role": "user", "content": question}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "end_turn":
        return response.content[0].text

    # Handle tool use
    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input
            tool_use_id = block.id

            print(f"  [Tool: {tool_name}] Input: {tool_input}")

            func = TOOL_FUNCTIONS.get(tool_name)
            if func:
                try:
                    result = func(**tool_input)
                except Exception as e:
                    result = f"Error: {e}"
            else:
                result = f"Error: Unknown tool '{tool_name}'"

            print(f"  [Result: {result}]")

            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": result}],
            })

            final = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                tools=tools,
                messages=messages,
            )
            return final.content[0].text

    return "No response generated."


# Test Exercise 1
print("=== Exercise 1: String Reverser ===")
print(ask_agent("Reverse the text: 'Hello World'"))


# ── Exercise 2: Tool Description Experiment ─────────────────────

print("\n=== Exercise 2: Description Experiment ===")

# Vague description — still usually works for obvious math
vague_tools = tools.copy()
vague_tools[0] = {
    "name": "calculator",
    "description": "A math tool",  # Vague!
    "input_schema": tools[0]["input_schema"],
}

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=vague_tools,
    messages=[{"role": "user", "content": "What is 15 * 24?"}],
)
print(f"Vague description - Stop reason: {response.stop_reason}")
# Claude will likely still use the calculator for obvious math.

# Misleading description — may cause wrong tool selection
misleading_tools = tools.copy()
misleading_tools[0] = {
    "name": "calculator",
    "description": "Count the number of letters in a word",  # Misleading!
    "input_schema": tools[0]["input_schema"],
}

response2 = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=misleading_tools,
    messages=[{"role": "user", "content": "What is 15 * 24?"}],
)
print(f"Misleading description - Stop reason: {response2.stop_reason}")
# Claude may try to calculate without the tool, or use the tool incorrectly.
# This proves: tool descriptions drive tool selection.


# ── Exercise 3: Multi-Tool Task ─────────────────────────────────

print("\n=== Exercise 3: Multi-Tool Limitation ===")
result = ask_agent("What's today's date, and how many days are left until December 31st?")
print(f"Result: {result}")
# With our single-tool-call implementation, Claude can only call ONE tool per request.
# It will likely call get_current_time first but won't be able to then call calculator.
# The fix: the agent LOOP from Lab 3, which continues processing until end_turn.
