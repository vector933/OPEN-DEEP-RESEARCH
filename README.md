# OPEN-DEEP-RESEARCH

A multi-agent research system that breaks down complex queries into actionable sub-tasks, performs web searches, and synthesizes findings into comprehensive reports.

## Project Structure

```
OPEN-DEEP-RESEARCH/
├── planner_agent/
│   ├── __init__.py
│   └── prompts.py          # Planner Agent prompt templates
├── searcher_agent/
│   ├── __init__.py
│   └── prompts.py          # Searcher Agent prompt templates
├── writer_agent/
│   ├── __init__.py
│   └── prompts.py          # Writer Agent prompt templates
└── README.md
```

## Agent Overview

### 1. Planner Agent (`planner_agent/`)
**Role:** Research Planner and Task Generator

- Breaks down complex research queries into exactly **3 distinct, actionable sub-questions**
- Each sub-question is designed to be answered by a single web search (Tavily API)
- Defines expected output format for each sub-task to guide the Writer Agent

**Prompts:**
- `PLANNER_SYSTEM_PROMPT`: Defines the agent's role and constraints
- `PLANNER_HUMAN_TEMPLATE`: Template for user query input

### 2. Searcher Agent (`searcher_agent/`)
**Role:** Source Synthesizer

- Processes raw search results for each sub-question
- Distills information into concise, factual 3-5 sentence summaries
- Only uses information from provided search snippets (no invented data)

**Prompts:**
- `SEARCHER_SYSTEM_PROMPT`: Defines synthesis goals and constraints
- `SEARCHER_HUMAN_TEMPLATE`: Template for raw search snippets input

### 3. Writer Agent (`writer_agent/`)
**Role:** Professional Research Writer and Editor

- Synthesizes all research findings into a single, cohesive report
- Uses clear Markdown formatting (headings, bullet points, tables)
- Produces professional, immediately readable output
- Does not mention the research process or internal agent workflow

**Prompts:**
- `WRITER_SYSTEM_PROMPT`: Defines writing requirements and standards
- `WRITER_HUMAN_TEMPLATE`: Template for formatted research findings input

## Usage

```python
# Import prompts from each agent
from planner_agent import PLANNER_SYSTEM_PROMPT, PLANNER_HUMAN_TEMPLATE
from searcher_agent import SEARCHER_SYSTEM_PROMPT, SEARCHER_HUMAN_TEMPLATE
from writer_agent import WRITER_SYSTEM_PROMPT, WRITER_HUMAN_TEMPLATE

# Use prompts in your LLM workflow
# Example: planner_prompt = PLANNER_HUMAN_TEMPLATE.format(
#     user_query="Your research question",
#     format_instructions="Your Pydantic schema instructions"
# )
```

## Workflow

1. **Planning Phase**: Planner Agent receives user query → generates 3 sub-tasks
2. **Research Phase**: Searcher Agent processes search results for each sub-task → creates summaries
3. **Writing Phase**: Writer Agent synthesizes all findings → produces final comprehensive report

## Requirements

- Python 3.8+
- LLM integration (e.g., OpenAI, Anthropic)
- Tavily API for web searches
- Pydantic for structured outputs (recommended)
