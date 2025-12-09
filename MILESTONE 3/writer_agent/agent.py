"""
Writer Agent Implementation
============================
This module implements the Writer Agent that synthesizes all research
findings into a comprehensive final report.
"""

from langchain_core.prompts import ChatPromptTemplate
from models import ResearchPlan, FinalReport
from .prompts import WRITER_SYSTEM_PROMPT, WRITER_HUMAN_TEMPLATE


class WriterAgent:
    """Agent responsible for creating the final comprehensive report."""
    
    def __init__(self, llm):
        """
        Initialize the Writer Agent.
        
        Args:
            llm: Language model instance (e.g., ChatOpenAI, ChatAnthropic)
        """
        self.llm = llm
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", WRITER_SYSTEM_PROMPT),
            ("human", WRITER_HUMAN_TEMPLATE)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm
    
    def write_report(self, user_query: str, research_plan: ResearchPlan) -> str:
        """
        Create a comprehensive report from all research findings.
        
        Args:
            user_query: The original user research question
            research_plan: ResearchPlan with all sub_tasks containing synthesized summaries
            
        Returns:
            str: Final comprehensive report in Markdown format
        """
        # Format the research findings
        formatted_results = ""
        for i, sub_task in enumerate(research_plan.sub_tasks, 1):
            formatted_results += f"\n### Finding {i}: {sub_task.sub_question}\n"
            formatted_results += f"**Expected Format:** {sub_task.expected_output_format}\n\n"
            formatted_results += f"{sub_task.summary_of_sources}\n\n"
            formatted_results += "---\n"
        
        # Generate final report
        response = self.chain.invoke({
            "user_query": user_query,
            "formatted_results": formatted_results
        })
        
        return response.content
