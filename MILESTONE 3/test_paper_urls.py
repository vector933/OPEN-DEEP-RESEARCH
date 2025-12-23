"""
Test Research Paper URL Detection and Fetching
==============================================
Test the paper_fetcher module with various URL formats.
"""

from paper_fetcher import PaperFetcher

def test_url_detection():
    """Test URL detection functionality."""
    fetcher = PaperFetcher()
    
    print("="*60)
    print("TESTING URL DETECTION")
    print("="*60)
    
    test_cases = [
        ("https://arxiv.org/abs/2103.00020", True, "arXiv abstract URL"),
        ("https://arxiv.org/pdf/2103.00020.pdf", True, "arXiv PDF URL"),
        ("https://www.semanticscholar.org/paper/abc123", True, "Semantic Scholar URL"),
        ("https://doi.org/10.1234/example", True, "DOI URL"),
        ("What is quantum computing?", False, "Regular question"),
        ("https://example.com/paper.pdf", True, "Generic PDF URL"),
    ]
    
    for text, expected, description in test_cases:
        result = fetcher.detect_url(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}: {result}")
    
    print()


def test_url_extraction():
    """Test URL and question extraction."""
    fetcher = PaperFetcher()
    
    print("="*60)
    print("TESTING URL AND QUESTION EXTRACTION")
    print("="*60)
    
    test_cases = [
        "https://arxiv.org/abs/2103.00020",
        "https://arxiv.org/abs/2103.00020 what is the methodology?",
        "Summarize this paper: https://arxiv.org/abs/2103.00020",
        "Can you explain the findings in https://arxiv.org/abs/2103.00020?",
    ]
    
    for text in test_cases:
        url, question = fetcher.extract_url_and_question(text)
        print(f"\nInput: {text}")
        print(f"  URL: {url}")
        print(f"  Question: {question if question else '(None - will generate summary)'}")
    
    print()


def test_arxiv_fetching():
    """Test fetching a real arXiv paper."""
    fetcher = PaperFetcher()
    
    print("="*60)
    print("TESTING ARXIV PAPER FETCHING")
    print("="*60)
    
    # Test with "Attention Is All You Need" paper
    arxiv_id = "1706.03762"
    url = f"https://arxiv.org/abs/{arxiv_id}"
    
    print(f"\nFetching paper: {url}")
    
    try:
        paper_info = fetcher.fetch_paper_info(url)
        
        print(f"\n✅ Successfully fetched paper!")
        print(f"\nTitle: {paper_info['title']}")
        print(f"Authors: {paper_info['authors']}")
        print(f"Published: {paper_info['published']}")
        print(f"ArXiv ID: {paper_info['arxiv_id']}")
        print(f"Categories: {paper_info['categories']}")
        print(f"\nAbstract (first 200 chars):")
        print(f"{paper_info['abstract'][:200]}...")
        print(f"\nPDF URL: {paper_info['pdf_url']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()


def test_semantic_scholar():
    """Test Semantic Scholar API (if available)."""
    fetcher = PaperFetcher()
    
    print("="*60)
    print("TESTING SEMANTIC SCHOLAR FETCHING")
    print("="*60)
    
    # Use a well-known paper ID
    # This is a sample - may need actual valid paper ID
    url = "https://www.semanticscholar.org/paper/649def34f8be52c96672a058bb8e64048da8b7e2"
    
    print(f"\nFetching paper: {url}")
    
    try:
        paper_info = fetcher.fetch_paper_info(url)
        
        print(f"\n✅ Successfully fetched paper!")
        print(f"\nTitle: {paper_info['title']}")
        print(f"Authors: {paper_info['authors']}")
        print(f"Year: {paper_info.get('year', 'Unknown')}")
        print(f"Citations: {paper_info.get('citations', 0)}")
        print(f"\nAbstract (first 200 chars):")
        print(f"{paper_info['abstract'][:200]}...")
        
    except Exception as e:
        print(f"⚠️ Note: {str(e)}")
        print("(This may be expected if the paper ID is not valid)")
    
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RESEARCH PAPER URL FETCHER - TEST SUITE")
    print("="*60 + "\n")
    
    # Run tests
    test_url_detection()
    test_url_extraction()
    test_arxiv_fetching()
    test_semantic_scholar()
    
    print("="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
