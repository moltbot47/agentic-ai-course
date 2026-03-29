"""
Lab 1 Solutions: Hello Agent — Claude API Basics
Module 1: Foundations of Agentic AI

These are reference solutions for the exercises in lab_01_hello_agent.ipynb
"""

import os
import json
from getpass import getpass

import anthropic

if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = getpass("Enter your Anthropic API key: ")

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-5-20241022"


# ── Exercise 1: Create a Specialized Agent ──────────────────────

class SimpleAgent:
    """A basic conversational agent with memory and a configurable persona."""

    def __init__(self, system_prompt: str, model: str = MODEL):
        self.client = anthropic.Anthropic()
        self.model = model
        self.system_prompt = system_prompt
        self.conversation_history: list[dict] = []

    def send(self, message: str) -> str:
        self.conversation_history.append({"role": "user", "content": message})
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=self.conversation_history,
        )
        reply = response.content[0].text
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        self.conversation_history = []


# Solution: Code Reviewer Agent
code_reviewer = SimpleAgent(
    system_prompt=(
        "You are a senior code reviewer with 15 years of experience in Python. "
        "When given code, you:\n"
        "1. Identify bugs, logic errors, and potential runtime issues\n"
        "2. Check for style issues (PEP 8 compliance, naming conventions)\n"
        "3. Rate overall code quality from 1-10 with justification\n"
        "4. Suggest 2-3 specific, actionable improvements\n"
        "Be constructive and specific. Reference line numbers when possible."
    )
)

test_code = '''
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def process_data(items):
    result = []
    for i in range(len(items)):
        if items[i] != None:
            result.append(items[i] * 2)
    return result
'''

print("=== Exercise 1: Code Reviewer ===")
print(code_reviewer.send(f"Review this code:\n```python{test_code}```"))


# ── Exercise 2: Token Cost Calculator ───────────────────────────

def calculate_cost(response) -> dict:
    """Calculate the cost of a Claude API response.

    Args:
        response: The API response object.

    Returns:
        Dict with input_cost, output_cost, and total_cost in USD.
    """
    # Claude Sonnet pricing (as of 2024)
    input_price_per_million = 3.00
    output_price_per_million = 15.00

    input_cost = (response.usage.input_tokens / 1_000_000) * input_price_per_million
    output_cost = (response.usage.output_tokens / 1_000_000) * output_price_per_million
    total_cost = input_cost + output_cost

    return {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
    }


# Test it
test_response = client.messages.create(
    model=MODEL,
    max_tokens=256,
    messages=[{"role": "user", "content": "What is an AI agent?"}],
)

print("\n=== Exercise 2: Cost Calculator ===")
cost = calculate_cost(test_response)
print(json.dumps(cost, indent=2))


# ── Exercise 3: Conversation Summary ────────────────────────────

def summarize_conversation(history: list[dict]) -> str:
    """Ask Claude to summarize a conversation history.

    Args:
        history: List of message dicts with 'role' and 'content'.

    Returns:
        A summary of the conversation.
    """
    summary_messages = history.copy()
    summary_messages.append({
        "role": "user",
        "content": (
            "Please provide a brief summary of our conversation so far. "
            "Include the main topics discussed, key points made, and any "
            "conclusions reached. Keep it under 5 sentences."
        ),
    })

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=summary_messages,
    )
    return response.content[0].text


# Build a sample conversation
history: list[dict] = []
agent = SimpleAgent(
    system_prompt="You are an AI tutor. Be concise."
)

agent.send("What's the difference between a chatbot and an AI agent?")
agent.send("Can you give me a real-world example of each?")
agent.send("Which one would you use for automating expense reports?")

print("\n=== Exercise 3: Conversation Summary ===")
summary = summarize_conversation(agent.conversation_history)
print(summary)
