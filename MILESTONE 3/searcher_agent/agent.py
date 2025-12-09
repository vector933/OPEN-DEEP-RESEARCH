"""
Searcher Agent Implementation
==============================
This module implements the Searcher Agent that performs web searches
and synthesizes results into concise summaries.
"""

from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient
from models import SubTask
from .prompts import SEARCHER_SYSTEM_PROMPT, SEARCHER_HUMAN_TEMPLATE


class SearcherAgent:
    """Agent responsible for searching and synthesizing information."""
    
    def __init__(self, llm, tavily_api_key: str):
        """
        Initialize the Searcher Agent.
        
        Args:
            llm: Language model instance (e.g., ChatOpenAI, ChatAnthropic)
            tavily_api_key: API key for Tavily search service
        """
        self.llm = llm
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SEARCHER_SYSTEM_PROMPT),
            ("human", SEARCHER_HUMAN_TEMPLATE)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm
    
    def search_and_synthesize(self, sub_task: SubTask) -> str:
        """
        Perform web search for a sub-question and synthesize results.
        
        Args:
            sub_task: SubTask containing the question and expected format
            
        Returns:
            str: Synthesized 3-5 sentence summary of search results
        """
        # Perform Tavily search
        search_results = self.tavily_client.search(
            query=sub_task.sub_question,
            max_results=5
        )
        
        # Extract snippets from search results
        raw_snippets = "\n\n".join([
            f"Source {i+1}: {result.get('content', result.get('snippet', ''))}"
            for i, result in enumerate(search_results.get('results', []))
        ])
        
        # Synthesize using LLM
        response = self.chain.invoke({
            "sub_question": sub_task.sub_question,
            "expected_output_format": sub_task.expected_output_format,
            "raw_search_snippets": raw_snippets
        })
        
        return response.content
