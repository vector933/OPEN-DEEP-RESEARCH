"""
Data Models for Multi-Agent Research System
============================================
This module defines the Pydantic models for structured data flow between agents.
"""

from typing import List
from pydantic import BaseModel, Field


class SubTask(BaseModel):
    """Represents a single research sub-task."""
    sub_question: str = Field(description="The specific research question to answer")
    expected_output_format: str = Field(
        description="Expected format of the answer (e.g., 'A list of 5 key dates', 'A brief paragraph summary')"
    )
    summary_of_sources: str = Field(
        default="",
        description="Synthesized summary from search results (populated by Searcher Agent)"
    )


class ResearchPlan(BaseModel):
    """Output from Planner Agent: Contains 3 sub-tasks."""
    sub_tasks: List[SubTask] = Field(
        description="Exactly 3 research sub-tasks",
        min_length=3,
        max_length=3
    )


class FinalReport(BaseModel):
    """Output from Writer Agent: The final comprehensive report."""
    report: str = Field(description="The final comprehensive research report in Markdown format")
