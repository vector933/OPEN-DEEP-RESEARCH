"""
Simple Test: Paper URL Detection in App
========================================
Quick test to verify URL handling works in the app context.
"""

from paper_fetcher import PaperFetcher

def main():
    """Test basic paper fetcher functionality."""
    fetcher = PaperFetcher()
    
    print("\n" + "="*60)
    print("PAPER URL DETECTION - QUICK TEST")
    print("="*60 + "\n")
    
    # Test 1: Detection
    print("Test 1: URL Detection")
    test_query = "https://arxiv.org/abs/1706.03762"
    is_url = fetcher.detect_url(test_query)
    print(f"  Query: {test_query}")
    print(f"  Is URL: {is_url} ✅\n")
    
    # Test 2: Extraction
    print("Test 2: URL + Question Extraction")
    test_query_with_question = "https://arxiv.org/abs/1706.03762 what is the methodology?"
    url, question = fetcher.extract_url_and_question(test_query_with_question)
    print(f"  Query: {test_query_with_question}")
    print(f"  Extracted URL: {url}")
    print(f"  Question: {question} ✅\n")
    
    # Test 3: Fetch Paper
    print("Test 3: Fetch ArXiv Paper")
    try:
        paper_info = fetcher.fetch_paper_info("https://arxiv.org/abs/1706.03762")
        print(f"  Title: {paper_info['title']}")
        print(f"  Authors: {paper_info['authors'][:50]}...")
        print(f"  Published: {paper_info['published']}")
        print(f"  ✅ Successfully fetched paper!\n")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")
    
    print("="*60)
    print("All basic tests completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
