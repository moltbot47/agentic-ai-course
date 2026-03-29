# Agentic AI Course — Continue Building

Copy and paste the prompt below into a new Claude Code session to continue.

---

## BUILD PROGRESS

### Module 1: Foundations of Agentic AI — COMPLETE ✅
All files built:
- README.md, curriculum.md, capstone.md, case_study.md
- labs/lab_01_hello_agent.ipynb (API basics, message roles, conversation memory)
- labs/lab_02_tool_use_agent.ipynb (tool schemas, tool_use/tool_result, autonomous selection)
- labs/lab_03_multi_step_agent.ipynb (agent loop, multi-tool, persistent memory)
- labs/capstone_starter.ipynb (research agent starter with TODOs)
- solutions/lab_01_solutions.py, lab_02_solutions.py, lab_03_solutions.py, capstone_solution.py
- diagrams/ (5 Mermaid files: agent_loop, architecture, tool_use_flow, autonomy_spectrum, multi_step_loop)

### Module 2: Professional Development — SCAFFOLDED (needs lab notebooks)
Files built:
- README.md, curriculum.md, capstone.md, case_study.md
- diagrams/ (3 Mermaid files: career_coach_architecture, resume_analysis_flow, job_matching_matrix)

**Still needed for Module 2:**
1. labs/lab_01_resume_agent.ipynb — Resume parsing, skills extraction, gap analysis, ATS scoring
2. labs/lab_02_job_matcher.ipynb — Job description parsing, multi-factor matching, batch ranking
3. labs/lab_03_interview_coach.ipynb — Question generation, mock interviews, STAR coaching, feedback
4. labs/capstone_starter.ipynb — Career Coach multi-agent starter template
5. solutions/ — Answer keys for all labs

### Module 3: AI Agents for Research — NOT STARTED
Needs: README.md, curriculum.md, capstone.md, case_study.md, labs/, solutions/, diagrams/

### Module 4: AI Agents for Financial Endeavors — NOT STARTED
Needs: README.md, curriculum.md, capstone.md, case_study.md, labs/, solutions/, diagrams/

---

## PROMPT

```
You are a world-class AI course creator. Continue building the Agentic AI certification program at ~/Desktop/agentic-ai-course/.

Read the existing files to understand the established patterns, then build what's next.

## WHAT TO BUILD NEXT

Build Module 2 lab notebooks (lab_01_resume_agent.ipynb, lab_02_job_matcher.ipynb, lab_03_interview_coach.ipynb, capstone_starter.ipynb) and solutions. Follow the exact same patterns as Module 1 labs: pip install anthropic, getpass for API key, clear markdown between cells, type hints, docstrings, exercises at the end.

After Module 2 is complete, scaffold Module 3 (Research) with README.md, curriculum.md, capstone.md, case_study.md, diagrams/, then build its lab notebooks.

## CODE STANDARDS

- Anthropic Python SDK (anthropic library)
- Model: claude-sonnet-4-5-20241022
- Google Colab compatible (pip install anthropic at top)
- Clear markdown explanations between code cells
- Type hints and docstrings on all functions
- Tool definitions follow Claude's tool_use schema exactly
- Error handling on all tool implementations

## MY BACKGROUND (for case studies)

Production agentic AI systems I built:
- OpenClaw: Multi-agent orchestration with 13 MCP servers, Discord integration
- Spirit Clip: Autonomous pipeline (YouTube → audio → transcription → emotion analysis → AI prompts)
- LaT-PFN Trading: ML pipeline for futures trading with automated execution (56.7% win rate)
- Institute for AI Innovation: AI certification program (25+ tools, 7 modules)
- NILE: Smart contract security scoring with multi-agent verification

Start by reading ~/Desktop/agentic-ai-course/module-2-professional-development/curriculum.md to understand the lab structure, then build the lab notebooks.
```
