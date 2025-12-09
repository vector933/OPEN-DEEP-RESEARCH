"""
Planner Agent Implementation
=============================
This module implements the Planner Agent that breaks down complex queries
into three actionable research sub-tasks.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import ResearchPlan
from .prompts import PLANNER_SYSTEM_PROMPT, PLANNER_HUMAN_TEMPLATE


class PlannerAgent:
    """Agent responsible for breaking down research queries into sub-tasks."""
    
    def __init__(self, llm):
        """
        Initialize the Planner Agent.
        
        Args:
            llm: Language model instance (e.g., ChatOpenAI, ChatAnthropic)
        """
        self.llm = llm
        self.output_parser = PydanticOutputParser(pydantic_object=ResearchPlan)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT),
            ("human", PLANNER_HUMAN_TEMPLATE)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser
    
    def plan(self, user_query: str, conversation_context: str = "") -> ResearchPlan:
        """
        Break down a user query into 3 research sub-tasks.
        
        Args:
            user_query: The original research question from the user
            conversation_context: Previous conversation history for context
            
        Returns:
            ResearchPlan: Contains 3 sub-tasks with questions and expected formats
        """
        format_instructions = self.output_parser.get_format_instructions()
        
        # Add context header if conversation history exists
        context_section = ""
        if conversation_context:
            context_section = f"Conversation History:\n{conversation_context}\n---\n"
        
        result = self.chain.invoke({
            "user_query": user_query,
            "conversation_context": context_section,
            "format_instructions": format_instructions
        })
        
        return result
