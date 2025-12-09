"""
Research Orchestrator
=====================
This module coordinates all three agents to execute the complete research workflow.
"""

from models import ResearchPlan
from planner_agent.agent import PlannerAgent
from searcher_agent.agent import SearcherAgent
from writer_agent.agent import WriterAgent


class ResearchOrchestrator:
    """Orchestrates the multi-agent research workflow."""
    
    def __init__(self, llm, tavily_api_key: str):
        """
        Initialize the orchestrator with all three agents.
        
        Args:
            llm: Language model instance (e.g., ChatOpenAI, ChatAnthropic)
            tavily_api_key: API key for Tavily search service
        """
        self.planner = PlannerAgent(llm)
        self.searcher = SearcherAgent(llm, tavily_api_key)
        self.writer = WriterAgent(llm)
    
    def research(self, user_query: str, verbose: bool = True) -> str:
        """
        Execute the complete research workflow.
        
        Args:
            user_query: The user's research question
            verbose: Whether to print progress updates
            
        Returns:
            str: Final comprehensive research report
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"RESEARCH QUERY: {user_query}")
            print(f"{'='*60}\n")
        
        # Step 1: Planning Phase
        if verbose:
            print("🔍 PHASE 1: Planning - Breaking down query into sub-tasks...")
        
        research_plan: ResearchPlan = self.planner.plan(user_query)
        
        if verbose:
            print(f"\n✅ Generated {len(research_plan.sub_tasks)} sub-tasks:")
            for i, task in enumerate(research_plan.sub_tasks, 1):
                print(f"   {i}. {task.sub_question}")
            print()
        
        # Step 2: Research Phase
        if verbose:
            print("🌐 PHASE 2: Research - Searching and synthesizing information...")
        
        for i, sub_task in enumerate(research_plan.sub_tasks, 1):
            if verbose:
                print(f"\n   Researching sub-task {i}/{len(research_plan.sub_tasks)}...")
                print(f"   Question: {sub_task.sub_question}")
            
            # Search and synthesize
            summary = self.searcher.search_and_synthesize(sub_task)
            sub_task.summary_of_sources = summary
            
            if verbose:
                print(f"   ✅ Completed")
        
        if verbose:
            print("\n✅ All research completed\n")
        
        # Step 3: Writing Phase
        if verbose:
            print("📝 PHASE 3: Writing - Creating comprehensive report...")
        
        final_report = self.writer.write_report(user_query, research_plan)
        
        if verbose:
            print("✅ Report completed\n")
            print(f"{'='*60}\n")
        
        return final_report
