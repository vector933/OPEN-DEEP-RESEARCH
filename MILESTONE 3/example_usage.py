"""
Example Usage: Multi-Agent Research System
===========================================
This script demonstrates how to use the research system to answer complex queries.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# Alternative: from langchain_openai import ChatOpenAI
# Alternative: from langchain_anthropic import ChatAnthropic
from orchestrator import ResearchOrchestrator


def main():
    """Main function to run the research system."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys from environment variables
    groq_api_key = os.getenv("GROQ_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not groq_api_key or not tavily_api_key:
        print("❌ Error: Missing API keys!")
        print("Please set GROQ_API_KEY and TAVILY_API_KEY in your .env file")
        return
    
    # Initialize the language model (Groq - Fast & Free!)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # Fast and high-quality model
        temperature=0.7,
        groq_api_key=groq_api_key
    )
    
    # Alternative: Use OpenAI
    # llm = ChatOpenAI(
    #     model="gpt-4o-mini",
    #     temperature=0.7,
    #     api_key=os.getenv("OPENAI_API_KEY")
    # )
    
    # Alternative: Use Anthropic Claude
    # llm = ChatAnthropic(
    #     model="claude-3-5-sonnet-20241022",
    #     temperature=0.7,
    #     api_key=os.getenv("ANTHROPIC_API_KEY")
    # )
    
    # Alternative: Use Google Gemini
    # from langchain_google_genai import ChatGoogleGenerativeAI
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-flash",
    #     temperature=0.7,
    #     google_api_key=os.getenv("GOOGLE_API_KEY")
    # )
    
    # Initialize the orchestrator
    orchestrator = ResearchOrchestrator(llm, tavily_api_key)
    
    # Example research query
    user_query = "What are the latest developments in quantum computing in 2024?"
    
    # You can also get user input:
    # user_query = input("Enter your research question: ")
    
    # Execute the research workflow
    final_report = orchestrator.research(user_query, verbose=True)
    
    # Display the final report
    print("\n" + "="*60)
    print("FINAL RESEARCH REPORT")
    print("="*60 + "\n")
    print(final_report)
    
    # Optionally save to file
    output_file = "research_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Research Report\n\n")
        f.write(f"**Query:** {user_query}\n\n")
        f.write(f"---\n\n")
        f.write(final_report)
    
    print(f"\n✅ Report saved to: {output_file}")


if __name__ == "__main__":
    main()
