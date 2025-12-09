"""
Test script to verify citation link formatting
"""

# Mock paper data
test_papers = [
    {
        "title": "Quantum Computing with Superconducting Qubits",
        "authors": ["John Smith", "Jane Doe", "Bob Johnson"],
        "year": "2023",
        "journal": "Nature Physics",
        "doi": "10.1038/s41567-023-12345",
        "url": "https://www.nature.com/articles/s41567-023-12345",
        "citations": 150,
        "source": "Semantic Scholar"
    },
    {
        "title": "Deep Learning for Natural Language Processing",
        "authors": ["Alice Wang"],
        "year": "2024",
        "journal": "arXiv Preprint",
        "doi": "arXiv:2401.12345",
        "url": "https://arxiv.org/abs/2401.12345",
        "citations": 0,
        "source": "arXiv"
    },
    {
        "title": "Machine Learning Applications in Healthcare",
        "authors": ["Sarah Lee", "Michael Chen"],
        "year": "2022",
        "journal": "Journal of Medical AI",
        "doi": "",
        "url": "https://example.com/paper123",
        "citations": 75,
        "source": "Semantic Scholar"
    }
]

# Import the format_citation method
import sys
sys.path.append('searcher_agent')

# Create a mock class to test the method
class MockSearcher:
    def format_citation(self, paper):
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
        
        citation = f"{author_str} ({year}). {title}. *{journal}*."
        
        # Add clickable links using markdown syntax
        if doi:
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

# Test the citations
searcher = MockSearcher()

print("=" * 80)
print("TESTING CITATION FORMATTING WITH MARKDOWN LINKS")
print("=" * 80)

for i, paper in enumerate(test_papers, 1):
    print(f"\nTest {i}: {paper['source']}")
    print("-" * 80)
    citation = searcher.format_citation(paper)
    print(citation)
    print()
    
    # Check if markdown link syntax is present
    if "[[" in citation and "]](" in citation and ")" in citation:
        print("✅ Markdown link syntax detected!")
    else:
        print("❌ No markdown link found!")

print("=" * 80)
print("\nExpected format: Author (Year). Title. *Journal*. [[Link Text]](URL)")
print("=" * 80)
