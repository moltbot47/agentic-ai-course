# Module 1: Foundations of Agentic AI — What It Is, What It Isn't, and How to Build Your First Agent

## Module Overview

This module takes learners from zero to building a functional AI agent in a single session. By the end, learners will understand what makes AI "agentic," how agents differ from traditional AI, how to evaluate whether an agent is doing what you built it to do, and will have deployed their first working agent.

## Target Audience
- Business professionals exploring AI automation
- Developers new to agentic AI patterns
- Technical leaders evaluating AI agent adoption
- Entrepreneurs looking to leverage AI agents

## Prerequisites
- Basic computer literacy
- A free Claude API key (instructions provided)
- No coding experience required (guided notebooks provided)

## Learning Outcomes

By the end of this module, learners will be able to:

1. **Define** what Agentic AI is and articulate how it differs from traditional AI, chatbots, and automation
2. **Identify** real-world use cases where agentic AI creates measurable business value vs. where it doesn't
3. **Understand** the core architecture of an AI agent: perception → reasoning → action → feedback loop
4. **Build** a functional AI agent from scratch using Claude API with tool-use capabilities
5. **Evaluate** agent performance using structured testing and validation frameworks
6. **Determine** whether your specific use case is a good fit for an agentic approach

## Module Duration
- **Lecture/Concepts:** 2 hours
- **Hands-on Labs:** 3 hours
- **Capstone Project:** 2 hours
- **Total:** ~7 hours (self-paced) or 1-day intensive (instructor-led)

## Module Structure

### Section 1: The Agentic AI Mental Model (45 min)
- What is an AI agent? (Not a chatbot, not RPA, not a workflow)
- The Agent Loop: Perceive → Reason → Act → Observe → Repeat
- Autonomy spectrum: from copilot to fully autonomous
- Key differentiator: agents make DECISIONS, not just predictions
- Real examples: what agents can and can't do today

### Section 2: Anatomy of an AI Agent (45 min)
- Core components: LLM brain, tools, memory, planning
- Tool-use pattern: how agents interact with the real world
- Memory types: conversation, short-term (context), long-term (persistent)
- Planning patterns: ReAct, chain-of-thought, tree-of-thought
- Architecture diagram walkthrough

### Section 3: Hands-On — Build Your First Agent (90 min)
- Lab 1: "Hello Agent" — Claude API basics (30 min)
- Lab 2: Tool-Use Agent — Give your agent the ability to act (30 min)
- Lab 3: Multi-Step Agent — Chain reasoning and actions together (30 min)

### Section 4: How Do You Know Your Agent Works? (30 min)
- Agent evaluation frameworks: accuracy, reliability, safety
- Testing patterns: unit tests for tools, integration tests for workflows
- Guardrails: input validation, output filtering, human-in-the-loop
- Red-teaming your agent: adversarial testing basics
- When NOT to use an agent (the most important lesson)

### Section 5: Capstone Project (120 min)
- Build a Personal Research Agent that takes a topic, searches for information, summarizes findings, and produces a structured report
- Includes evaluation rubric and success criteria

## Files in This Module

| File | Description |
|------|-------------|
| `curriculum.md` | Full lesson plan with instructor notes and talking points |
| `labs/lab_01_hello_agent.ipynb` | Guided: First Claude API call and response parsing |
| `labs/lab_02_tool_use_agent.ipynb` | Guided: Agent with tool-use (calculator, web search) |
| `labs/lab_03_multi_step_agent.ipynb` | Guided: Multi-step reasoning agent with memory |
| `capstone.md` | Capstone project brief, requirements, and rubric |
| `solutions/` | Instructor answer keys for all labs |
| `diagrams/` | Architecture diagrams (Mermaid source + rendered) |
| `case_study.md` | Real-world case study: OpenClaw multi-agent framework |
