"""
Academic Paper Search Agent
============================
Replaces Tavily with academic paper search using Semantic Scholar and arXiv APIs.
Provides proper citations and references.
"""

from langchain_core.prompts import ChatPromptTemplate
from models import SubTask
from .prompts import SEARCHER_SYSTEM_PROMPT, SEARCHER_HUMAN_TEMPLATE
import requests
from typing import List, Dict
import time


class AcademicSearcherAgent:
    """Agent responsible for searching academic papers and synthesizing information."""
    
    def __init__(self, llm):
        """
        Initialize the Academic Searcher Agent.
        
        Args:
            llm: Language model instance (e.g., ChatGroq)
        """
        self.llm = llm
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SEARCHER_SYSTEM_PROMPT),
            ("human", SEARCHER_HUMAN_TEMPLATE)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm
    
    def search_semantic_scholar(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search Semantic Scholar for academic papers.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of paper dictionaries with metadata
        """
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": limit,
                "fields": "title,authors,year,abstract,citationCount,url,externalIds,publicationDate,journal"
            }
            
            print(f"[DEBUG] Searching Semantic Scholar for: {query}")
            
            response = requests.get(url, params=params, timeout=15)
            
            print(f"[DEBUG] Semantic Scholar status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[ERROR] Semantic Scholar API error: {response.text}")
                return []
            
            data = response.json()
            papers = data.get("data", [])
            
            print(f"[DEBUG] Found {len(papers)} papers from Semantic Scholar")
            
            # Format papers
            formatted_papers = []
            for paper in papers:
                authors_list = paper.get("authors", [])
                author_names = [author.get("name", "") for author in authors_list[:3]]  # First 3 authors
                
                formatted_papers.append({
                    "title": paper.get("title", "Unknown Title"),
                    "authors": author_names if author_names else ["Unknown"],
                    "year": paper.get("year", "N/A"),
                    "abstract": paper.get("abstract", "No abstract available")[:800],  # Limit abstract length
                    "citations": paper.get("citationCount", 0),
                    "url": paper.get("url", ""),
                    "doi": paper.get("externalIds", {}).get("DOI", ""),
                    "journal": paper.get("journal", {}).get("name", "Unknown Journal") if paper.get("journal") else "Preprint",
                    "source": "Semantic Scholar"
                })
            
            return formatted_papers
            
        except requests.exceptions.Timeout:
            print("[ERROR] Semantic Scholar API timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Semantic Scholar request error: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Semantic Scholar search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_arxiv(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search arXiv for academic papers.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of paper dictionaries with metadata
        """
        try:
            import feedparser
            
            # Clean query for arXiv
            clean_query = query.replace(" ", "+")
            url = f"http://export.arxiv.org/api/query?search_query=all:{clean_query}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
            
            print(f"[DEBUG] Searching arXiv for: {query}")
            
            feed = feedparser.parse(url)
            
            print(f"[DEBUG] Found {len(feed.entries)} papers from arXiv")
            
            formatted_papers = []
            for entry in feed.entries:
                # Extract authors
                authors = [author.name for author in entry.authors[:3]] if hasattr(entry, 'authors') else ["Unknown"]
                
                # Extract year from published date
                year = entry.published[:4] if hasattr(entry, 'published') else "N/A"
                
                # Extract arXiv ID
                arxiv_id = entry.id.split('/abs/')[-1] if hasattr(entry, 'id') else "Unknown"
                
                formatted_papers.append({
                    "title": entry.title if hasattr(entry, 'title') else "Unknown Title",
                    "authors": authors,
                    "year": year,
                    "abstract": entry.summary[:800] if hasattr(entry, 'summary') else "No abstract available",
                    "citations": 0,  # arXiv doesn't provide citation counts
                    "url": entry.link if hasattr(entry, 'link') else "",
                    "doi": f"arXiv:{arxiv_id}",
                    "journal": "arXiv Preprint",
                    "source": "arXiv"
                })
            
            return formatted_papers
            
        except Exception as e:
            print(f"[ERROR] arXiv search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def format_citation(self, paper: Dict) -> str:
        """Format a paper citation in APA style with markdown links."""
        authors = paper["authors"]
        
        # Format authors
        if len(authors) == 0:
            author_str = "Unknown"
        elif len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."
        
        year = paper["year"]
        title = paper["title"]
        journal = paper["journal"]
        doi = paper["doi"]
        source = paper.get("source", "Unknown")
        
        citation = f"{author_str} ({year}). {title}. *{journal}*."
        
        # Add clickable links using markdown syntax
        if source == "Web":
            # For web sources, link to the URL directly
            if paper["url"]:
                citation += f" [[Web Link]]({paper['url']})"
        elif doi:
            if doi.startswith("arXiv:"):
                arxiv_id = doi.replace("arXiv:", "")
                arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
                citation += f" [[arXiv:{arxiv_id}]]({arxiv_url})"
            else:
                doi_url = f"https://doi.org/{doi}"
                citation += f" [[DOI]]({doi_url})"
        elif paper["url"]:
            citation += f" [[Link]]({paper['url']})"
        
        return citation
    
    def search_and_synthesize(self, sub_task: SubTask) -> tuple[str, List[Dict]]:
        """
        Perform multi-source search for a sub-question and synthesize results.
        Uses: Semantic Scholar, arXiv, and web search for diverse coverage.
        
        Args:
            sub_task: SubTask containing the question and expected format
            
        Returns:
            tuple: (synthesized summary, list of paper citations)
        """
        papers = []
        
        # Strategy: Get papers from multiple sources for diversity
        # 1. Semantic Scholar (2 papers) - peer-reviewed academic papers
        print(f"[INFO] Searching Semantic Scholar...")
        semantic_papers = self.search_semantic_scholar(sub_task.sub_question, limit=2)
        papers.extend(semantic_papers)
        print(f"[INFO] Found {len(semantic_papers)} papers from Semantic Scholar")
        
        # 2. arXiv (2 papers) - preprints and recent research
        print(f"[INFO] Searching arXiv...")
        arxiv_papers = self.search_arxiv(sub_task.sub_question, limit=2)
        papers.extend(arxiv_papers)
        print(f"[INFO] Found {len(arxiv_papers)} papers from arXiv")
        
        # 3. Web search (1 result) - for additional context and recent news
        print(f"[INFO] Searching web sources...")
        web_results = self.search_web(sub_task.sub_question, limit=1)
        papers.extend(web_results)
        print(f"[INFO] Found {len(web_results)} results from web search")
        
        # Limit to top 5 total sources
        papers = papers[:5]
        
        if not papers:
            return "No sources found for this query.", []
        
        print(f"[INFO] Total sources: {len(papers)}")
        
        # Create snippets from paper abstracts with citations
        raw_snippets = ""
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper["authors"]) if paper["authors"] else "Unknown"
            raw_snippets += f"\n\n**Source {i}: {paper['title']}**\n"
            raw_snippets += f"Authors: {authors_str}\n"
            raw_snippets += f"Year: {paper['year']} | Journal: {paper['journal']} | Citations: {paper['citations']}\n"
            raw_snippets += f"Abstract: {paper['abstract'][:500]}...\n"  # First 500 chars
        
        # Synthesize using LLM
        response = self.chain.invoke({
            "sub_question": sub_task.sub_question,
            "expected_output_format": sub_task.expected_output_format,
            "raw_search_snippets": raw_snippets
        })
        
        return response.content, papers
    
    def search_web(self, query: str, limit: int = 1) -> List[Dict]:
        """
        Search web for additional context using DuckDuckGo.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of result dictionaries with metadata
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Use DuckDuckGo HTML search (no API key needed)
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            print(f"[DEBUG] Searching web for: {query}")
            
            response = requests.post(url, data=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[ERROR] Web search failed: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse DuckDuckGo results
            for result in soup.find_all('div', class_='result')[:limit]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        results.append({
                            "title": title,
                            "authors": ["Web Source"],
                            "year": "2024",
                            "abstract": snippet[:800],
                            "citations": 0,
                            "url": url,
                            "doi": "",
                            "journal": "Web Article",
                            "source": "Web"
                        })
                except Exception as e:
                    print(f"[ERROR] Error parsing web result: {e}")
                    continue
            
            print(f"[DEBUG] Found {len(results)} web results")
            return results
            
        except ImportError:
            print("[ERROR] BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return []
        except Exception as e:
            print(f"[ERROR] Web search error: {e}")
            return []
