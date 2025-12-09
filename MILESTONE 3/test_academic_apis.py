"""Quick test of academic search APIs"""
import requests

print("Testing Semantic Scholar API...")
try:
    r = requests.get(
        'https://api.semanticscholar.org/graph/v1/paper/search',
        params={
            'query': 'climate change food security',
            'limit': 3,
            'fields': 'title,authors,year'
        },
        timeout=10
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        papers = data.get('data', [])
        print(f"Papers found: {len(papers)}")
        for i, paper in enumerate(papers, 1):
            print(f"  {i}. {paper.get('title', 'No title')}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting arXiv API...")
try:
    import feedparser
    feed = feedparser.parse('http://export.arxiv.org/api/query?search_query=all:climate+change&start=0&max_results=3')
    print(f"Papers found: {len(feed.entries)}")
    for i, entry in enumerate(feed.entries, 1):
        print(f"  {i}. {entry.title}")
except Exception as e:
    print(f"Error: {e}")
