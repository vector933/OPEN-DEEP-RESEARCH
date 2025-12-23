"""
Research Paper URL Fetcher
===========================
Utility to detect, extract, and fetch information from research paper URLs.
Supports arXiv, Semantic Scholar, DOI, and generic PDF links.
"""

import re
import requests
from typing import Optional, Dict, Tuple
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs


class PaperFetcher:
    """Fetch and extract information from research paper URLs."""
    
    # URL patterns for different research paper sources
    ARXIV_PATTERN = r'(?:https?://)?(?:www\.)?arxiv\.org/(?:abs|pdf)/(\d+\.\d+)(?:v\d+)?(?:\.pdf)?'
    SEMANTIC_SCHOLAR_PATTERN = r'(?:https?://)?(?:www\.)?semanticscholar\.org/paper/[^/]+/([a-f0-9]+)'
    DOI_PATTERN = r'(?:https?://)?(?:dx\.)?doi\.org/(10\.\d+/[^\s]+)'
    PDF_PATTERN = r'https?://[^\s]+\.pdf'
    
    def __init__(self):
        """Initialize the paper fetcher."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def detect_url(self, text: str) -> bool:
        """
        Detect if text contains a research paper URL.
        
        Args:
            text: Input text to check
            
        Returns:
            bool: True if URL is detected, False otherwise
        """
        patterns = [
            self.ARXIV_PATTERN,
            self.SEMANTIC_SCHOLAR_PATTERN,
            self.DOI_PATTERN,
            self.PDF_PATTERN
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def extract_url_and_question(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract URL and any accompanying question from text.
        
        Args:
            text: Input text containing URL and possibly a question
            
        Returns:
            Tuple[url, question]: Extracted URL and question (if present)
        """
        # Find all URLs in the text
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        if not urls:
            return None, None
        
        # Take the first URL
        url = urls[0]
        
        # Remove the URL from text to get the question
        question = text.replace(url, '').strip()
        
        # Clean up common artifacts
        question = re.sub(r'\s+', ' ', question).strip()
        
        # If question is too short or just punctuation, consider it as no question
        if len(question) < 5 or question in ['', '.', '?', '!']:
            question = None
        
        return url, question
    
    def fetch_arxiv_paper(self, arxiv_id: str) -> Dict:
        """
        Fetch paper information from arXiv API.
        
        Args:
            arxiv_id: arXiv paper ID (e.g., "2103.00020")
            
        Returns:
            Dict containing paper information
        """
        try:
            # Query arXiv API
            api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Namespaces for arXiv API
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entry = root.find('atom:entry', ns)
            if entry is None:
                raise ValueError("Paper not found on arXiv")
            
            # Extract information
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip()
            published = entry.find('atom:published', ns).text[:10]
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
            
            # Extract categories
            categories = []
            for category in entry.findall('atom:category', ns):
                categories.append(category.get('term'))
            
            # Get PDF link
            pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            abstract_link = f"https://arxiv.org/abs/{arxiv_id}"
            
            return {
                'source': 'arxiv',
                'title': title,
                'authors': ', '.join(authors),
                'abstract': summary,
                'published': published,
                'arxiv_id': arxiv_id,
                'categories': ', '.join(categories[:3]),  # Top 3 categories
                'pdf_url': pdf_link,
                'url': abstract_link
            }
            
        except Exception as e:
            raise ValueError(f"Failed to fetch arXiv paper: {str(e)}")
    
    def fetch_semantic_scholar_paper(self, paper_id: str) -> Dict:
        """
        Fetch paper information from Semantic Scholar API.
        
        Args:
            paper_id: Semantic Scholar paper ID
            
        Returns:
            Dict containing paper information
        """
        try:
            api_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
            params = {
                'fields': 'title,authors,abstract,year,citationCount,url,openAccessPdf'
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract author names
            authors = ', '.join([author['name'] for author in data.get('authors', [])])
            
            # Get PDF URL if available
            pdf_url = None
            if data.get('openAccessPdf'):
                pdf_url = data['openAccessPdf'].get('url')
            
            return {
                'source': 'semantic_scholar',
                'title': data.get('title', 'Unknown Title'),
                'authors': authors or 'Unknown Authors',
                'abstract': data.get('abstract', 'No abstract available'),
                'year': data.get('year', 'Unknown'),
                'citations': data.get('citationCount', 0),
                'url': data.get('url', ''),
                'pdf_url': pdf_url
            }
            
        except Exception as e:
            raise ValueError(f"Failed to fetch Semantic Scholar paper: {str(e)}")
    
    def fetch_doi_paper(self, doi: str) -> Dict:
        """
        Fetch paper information from DOI.
        
        Args:
            doi: DOI string (e.g., "10.1234/example")
            
        Returns:
            Dict containing paper information
        """
        try:
            # Use CrossRef API
            api_url = f"https://api.crossref.org/works/{doi}"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()['message']
            
            # Extract information
            title = data.get('title', ['Unknown Title'])[0]
            
            # Extract authors
            authors = []
            for author in data.get('author', []):
                given = author.get('given', '')
                family = author.get('family', '')
                authors.append(f"{given} {family}".strip())
            
            # Get publication year
            published = data.get('published-print', {}).get('date-parts', [[None]])[0][0]
            if not published:
                published = data.get('published-online', {}).get('date-parts', [[None]])[0][0]
            
            return {
                'source': 'doi',
                'title': title,
                'authors': ', '.join(authors) if authors else 'Unknown Authors',
                'abstract': data.get('abstract', 'No abstract available'),
                'published': str(published) if published else 'Unknown',
                'doi': doi,
                'url': f"https://doi.org/{doi}",
                'publisher': data.get('publisher', 'Unknown')
            }
            
        except Exception as e:
            raise ValueError(f"Failed to fetch DOI paper: {str(e)}")
    
    def fetch_paper_info(self, url: str) -> Dict:
        """
        Fetch paper information from a URL.
        
        Args:
            url: Research paper URL
            
        Returns:
            Dict containing paper information
        """
        # Try arXiv
        arxiv_match = re.search(self.ARXIV_PATTERN, url, re.IGNORECASE)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            return self.fetch_arxiv_paper(arxiv_id)
        
        # Try Semantic Scholar
        ss_match = re.search(self.SEMANTIC_SCHOLAR_PATTERN, url, re.IGNORECASE)
        if ss_match:
            paper_id = ss_match.group(1)
            return self.fetch_semantic_scholar_paper(paper_id)
        
        # Try DOI
        doi_match = re.search(self.DOI_PATTERN, url, re.IGNORECASE)
        if doi_match:
            doi = doi_match.group(1)
            return self.fetch_doi_paper(doi)
        
        # Try generic PDF (limited information)
        if url.lower().endswith('.pdf'):
            return {
                'source': 'pdf',
                'title': 'Research Paper (PDF)',
                'authors': 'Unknown',
                'abstract': 'PDF file - full text extraction not available',
                'url': url,
                'note': 'Limited metadata available for direct PDF links'
            }
        
        raise ValueError("Unsupported URL format or unable to extract paper information")
    
    def is_research_paper_url(self, url: str) -> bool:
        """
        Validate if URL appears to be a research paper.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL appears to be a research paper
        """
        return self.detect_url(url)
