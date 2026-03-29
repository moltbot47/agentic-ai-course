# Capstone Project: Build a Personal Career Coach Agent

## Project Brief

Build a multi-capability career coaching agent that ingests a user's resume and career goals, stores their profile in persistent memory, and provides on-demand access to resume analysis, job matching, interview preparation, professional presence advice, and career path planning — all through a single conversational interface.

This capstone demonstrates **multi-agent orchestration** — multiple specialized capabilities coordinated by a single orchestrator agent with shared memory.

## Requirements

### Minimum Viable Agent (Pass — 70+)
- [ ] Accepts a resume (as text) and parses it into structured data
- [ ] Stores the user's profile in persistent memory
- [ ] Implements at least 2 of the 5 capabilities (resume analysis + one other)
- [ ] Uses at least 4 distinct tools
- [ ] Produces actionable output (not just analysis — specific recommendations)
- [ ] Maintains conversation context across multiple interactions

### Enhanced Agent (Distinction — 80+)
- [ ] All minimum requirements plus:
- [ ] Implements at least 4 of the 5 capabilities
- [ ] Cross-references between capabilities (e.g., job match informs interview prep)
- [ ] Confidence scoring on recommendations
- [ ] Handles multiple job descriptions in batch
- [ ] Graceful error handling and recovery

### Outstanding Agent (Honors — 90+)
- [ ] All enhanced requirements plus:
- [ ] All 5 capabilities implemented
- [ ] Multi-output format (text report + JSON data)
- [ ] Profile comparison over time (track improvements)
- [ ] Self-evaluation section with methodology notes
- [ ] Demonstrates the agent helping with a realistic career scenario end-to-end

## Suggested Tools

```python
# Core Tools (minimum)
def parse_resume(resume_text: str) -> str: ...
def analyze_skills(skills: str, target_role: str) -> str: ...
def save_profile(profile_data: str) -> str: ...
def recall_profile() -> str: ...

# Job Matching Tools
def parse_job_description(job_text: str) -> str: ...
def match_candidate(resume_data: str, job_data: str) -> str: ...

# Interview Tools
def generate_interview_questions(role: str, skills: str) -> str: ...
def evaluate_answer(question: str, answer: str) -> str: ...

# Career Planning Tools
def model_career_path(current_role: str, target_role: str, skills: str) -> str: ...
def estimate_timeline(skill_gaps: str) -> str: ...

# Utility Tools
def save_report(filename: str, content: str) -> str: ...
def get_current_datetime() -> str: ...
```

## Evaluation Rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Profile Management** | 15 | Resume parsing, memory persistence, profile updates |
| **Capability Implementation** | 25 | Quality and depth of career coaching capabilities |
| **Tool Design** | 15 | Well-designed tools with clear schemas and error handling |
| **Integration** | 15 | Capabilities work together (shared context, cross-references) |
| **Output Quality** | 15 | Actionable, specific, well-formatted recommendations |
| **Code Quality** | 10 | Clean, documented, maintainable code |
| **Creativity** | 5 | Novel features, thoughtful UX, going beyond requirements |
| **Total** | **100** | |

**Grading Scale:**
- 90-100: Honors — production-quality multi-agent system
- 80-89: Distinction — strong implementation with good integration
- 70-79: Pass — meets minimum requirements with working capabilities
- Below 70: Incomplete — revise and resubmit

## Starter Template

A starter notebook is provided in `labs/capstone_starter.ipynb` with:
- Profile management boilerplate
- Tool definition templates for all 5 capabilities
- The orchestrator agent loop
- Sample resume and job descriptions for testing

## Test Scenarios

Use these to test your agent:

**Scenario 1: New Job Search**
> "Here's my resume [paste]. I'm looking for Senior Data Engineer roles in Austin, TX. Analyze my resume, then match me against these 3 job descriptions [paste]. Finally, prepare me for interviews at the top match."

**Scenario 2: Career Change**
> "I'm a mechanical engineer with 5 years of experience wanting to transition into software engineering. Here's my resume [paste]. What's my best path? What skills do I need? How long will it take?"

**Scenario 3: Profile Optimization**
> "Review my resume and LinkedIn headline. I want to position myself as a senior-level AI/ML engineer. Give me specific rewrites."

## Submission

1. Your completed Jupyter notebook (`.ipynb`)
2. Generated outputs from at least 2 test scenarios
3. Reflection (3-5 sentences): What was your design approach? What trade-offs did you make?

## Time Estimate
- **Planning & architecture:** 30 minutes
- **Tool implementation:** 60 minutes
- **Orchestrator agent:** 45 minutes
- **Testing & refinement:** 30 minutes
- **Documentation & reflection:** 15 minutes
- **Total:** ~3 hours
