"""
Research Orchestrator with Academic Search and LangGraph
=========================================================
Coordinates all three agents using LangGraph workflow with conversation memory.
"""

from typing import List, Dict, Optional
from workflow import ResearchWorkflow


class AcademicResearchOrchestrator:
    """Orchestrates the multi-agent research workflow with LangGraph and conversation memory."""
    
    def __init__(self, llm):
        """
        Initialize the orchestrator with LangGraph workflow.
        
        Args:
            llm: Language model instance (e.g., ChatGroq)
        """
        self.workflow = ResearchWorkflow(llm)
    
    def research(
        self, 
        user_query: str, 
        conversation_history: List[Dict[str, str]] = None,
        verbose: bool = True
    ) -> tuple[str, list]:
        """
        Execute the complete research workflow with LangGraph and conversation memory.
        
        Args:
            user_query: The user's research question
            conversation_history: Previous conversation messages for context
            verbose: Whether to print progress updates
            
        Returns:
            tuple: (final report with citations, list of all papers used)
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"RESEARCH QUERY: {user_query}")
            if conversation_history:
                print(f"CONVERSATION CONTEXT: {len(conversation_history)} previous messages")
            print(f"{'='*60}\n")
            print("🔄 Using LangGraph workflow for multi-agent coordination...")
        
        try:
            # Run the LangGraph workflow with conversation context
            final_report, papers = self.workflow.run(
                query=user_query,
                conversation_history=conversation_history or []
            )
            
            if verbose:
                print(f"\n✅ Research completed successfully!")
                print(f"📚 Total papers found: {len(papers)}")
                print(f"{'='*60}\n")
            
            return final_report, papers
            
        except Exception as e:
            if verbose:
                print(f"\n❌ Error during research: {str(e)}")
                print(f"{'='*60}\n")
            raise
