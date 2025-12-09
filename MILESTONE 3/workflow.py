"""
LangGraph Workflow for Multi-Agent Research System
===================================================
Implements a state graph workflow that coordinates the planner, searcher, and writer agents.
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import StateGraph, END
from models import ResearchPlan, SubTask
from planner_agent.agent import PlannerAgent
from searcher_agent.academic_agent import AcademicSearcherAgent
from writer_agent.agent import WriterAgent


class ResearchState(TypedDict):
    """State that flows through the research workflow."""
    query: str
    conversation_history: List[Dict[str, str]]
    research_plan: Optional[ResearchPlan]
    current_task_index: int
    findings: List[Dict]
    papers: List[Dict]
    final_report: str
    error: Optional[str]


class ResearchWorkflow:
    """LangGraph workflow for coordinating research agents."""
    
    def __init__(self, llm):
        """
        Initialize the workflow with agents.
        
        Args:
            llm: Language model instance
        """
        self.planner = PlannerAgent(llm)
        self.searcher = AcademicSearcherAgent(llm)
        self.writer = WriterAgent(llm)
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph state graph."""
        # Create the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("searcher", self._searcher_node)
        workflow.add_node("writer", self._writer_node)
        
        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "searcher")
        workflow.add_edge("searcher", "writer")
        workflow.add_edge("writer", END)
        
        return workflow.compile()
    
    def _planner_node(self, state: ResearchState) -> ResearchState:
        """
        Planner node: Creates research plan with conversation context.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with research plan
        """
        try:
            # Format conversation history for context
            conversation_context = self._format_conversation_history(
                state.get("conversation_history", [])
            )
            
            # Create research plan with context
            research_plan = self.planner.plan(
                state["query"],
                conversation_context=conversation_context
            )
            
            state["research_plan"] = research_plan
            state["current_task_index"] = 0
            state["findings"] = []
            state["papers"] = []
            
        except Exception as e:
            state["error"] = f"Planner error: {str(e)}"
        
        return state
    
    def _searcher_node(self, state: ResearchState) -> ResearchState:
        """
        Searcher node: Searches academic papers for each sub-task.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with search findings
        """
        try:
            research_plan = state["research_plan"]
            all_papers = []
            
            # Search for each sub-task
            for sub_task in research_plan.sub_tasks:
                summary, papers = self.searcher.search_and_synthesize(sub_task)
                sub_task.summary_of_sources = summary
                all_papers.extend(papers)
                
                state["findings"].append({
                    "question": sub_task.sub_question,
                    "summary": summary,
                    "paper_count": len(papers)
                })
            
            state["papers"] = all_papers
            
        except Exception as e:
            state["error"] = f"Searcher error: {str(e)}"
        
        return state
    
    def _writer_node(self, state: ResearchState) -> ResearchState:
        """
        Writer node: Creates final report with citations.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with final report
        """
        try:
            research_plan = state["research_plan"]
            
            # Generate base report
            report = self.writer.write_report(state["query"], research_plan)
            
            # Add references section
            if state["papers"]:
                report += "\n\n## References\n\n"
                
                # Remove duplicate papers
                unique_papers = self._deduplicate_papers(state["papers"])
                
                # Format citations
                for i, paper in enumerate(unique_papers, 1):
                    citation = self.searcher.format_citation(paper)
                    report += f"{i}. {citation}\n\n"
            
            state["final_report"] = report
            
        except Exception as e:
            state["error"] = f"Writer error: {str(e)}"
        
        return state
    
    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """
        Format conversation history for agent context.
        
        Args:
            history: List of previous query/report pairs
            
        Returns:
            Formatted conversation context string
        """
        if not history:
            return ""
        
        context = "Previous conversation:\n\n"
        for i, msg in enumerate(history[-3:], 1):  # Last 3 exchanges
            context += f"Q{i}: {msg['query']}\n"
            # Include first 200 chars of previous report for context
            report_preview = msg['report'][:200] + "..." if len(msg['report']) > 200 else msg['report']
            context += f"A{i}: {report_preview}\n\n"
        
        return context
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Remove duplicate papers based on title.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            List of unique papers
        """
        unique_papers = []
        seen_titles = set()
        
        for paper in papers:
            title = paper.get("title", "")
            if title and title not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title)
        
        return unique_papers
    
    def run(
        self, 
        query: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> tuple[str, List[Dict]]:
        """
        Execute the research workflow.
        
        Args:
            query: User's research question
            conversation_history: Previous conversation messages
            
        Returns:
            Tuple of (final_report, papers_list)
        """
        # Initialize state
        initial_state: ResearchState = {
            "query": query,
            "conversation_history": conversation_history or [],
            "research_plan": None,
            "current_task_index": 0,
            "findings": [],
            "papers": [],
            "final_report": "",
            "error": None
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Check for errors
        if final_state.get("error"):
            raise Exception(final_state["error"])
        
        return final_state["final_report"], final_state["papers"]
