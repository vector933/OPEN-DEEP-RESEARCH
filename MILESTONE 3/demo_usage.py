"""
Simple Demo Version - Works WITHOUT API Keys
==============================================
This is a simplified demo that shows how the system works using mock responses.
For the FULL version with real web search, you need valid API keys.
"""

from models import ResearchPlan, SubTask


def demo_research(user_query: str):
    """Demo version that simulates the research workflow."""
    
    print(f"\n{'='*60}")
    print(f"DEMO RESEARCH QUERY: {user_query}")
    print(f"{'='*60}\n")
    
    # Step 1: Planning Phase (Simulated)
    print("🔍 PHASE 1: Planning - Breaking down query into sub-tasks...")
    
    research_plan = ResearchPlan(sub_tasks=[
        SubTask(
            sub_question="What are the major breakthroughs in quantum computing in 2024?",
            expected_output_format="A brief paragraph summary",
            summary_of_sources="In 2024, quantum computing saw significant advances including improved error correction rates, longer coherence times in qubits, and the development of more stable quantum processors. Major tech companies announced new quantum chips with increased qubit counts."
        ),
        SubTask(
            sub_question="Which companies are leading quantum computing development?",
            expected_output_format="A list of top 5 companies",
            summary_of_sources="The leading companies in quantum computing include IBM, Google, Microsoft, Amazon (AWS), and IonQ. These companies are investing heavily in quantum hardware, software, and cloud-based quantum computing services."
        ),
        SubTask(
            sub_question="What are the practical applications emerging in 2024?",
            expected_output_format="A comparative table of applications",
            summary_of_sources="Practical applications emerging in 2024 include drug discovery and molecular simulation, financial modeling and risk analysis, cryptography and security, optimization problems in logistics, and materials science research."
        )
    ])
    
    print(f"\n✅ Generated {len(research_plan.sub_tasks)} sub-tasks:")
    for i, task in enumerate(research_plan.sub_tasks, 1):
        print(f"   {i}. {task.sub_question}")
    print()
    
    # Step 2: Research Phase (Simulated)
    print("🌐 PHASE 2: Research - Searching and synthesizing information...")
    print("   (Using simulated search results for demo)")
    
    for i, sub_task in enumerate(research_plan.sub_tasks, 1):
        print(f"\n   ✅ Completed sub-task {i}/{len(research_plan.sub_tasks)}")
    
    print("\n✅ All research completed\n")
    
    # Step 3: Writing Phase (Simulated)
    print("📝 PHASE 3: Writing - Creating comprehensive report...")
    
    final_report = f"""# Latest Developments in Quantum Computing (2024)

## Overview

Quantum computing has made remarkable progress in 2024, with significant breakthroughs in hardware, software, and practical applications. This report synthesizes the key developments across the industry.

## Major Breakthroughs

In 2024, quantum computing saw significant advances including improved error correction rates, longer coherence times in qubits, and the development of more stable quantum processors. Major tech companies announced new quantum chips with increased qubit counts, bringing us closer to achieving quantum advantage in practical applications.

## Industry Leaders

The quantum computing landscape is dominated by several key players:

1. **IBM** - Leading in superconducting qubit technology
2. **Google** - Advancing quantum supremacy research
3. **Microsoft** - Developing topological qubits
4. **Amazon (AWS)** - Providing cloud-based quantum services
5. **IonQ** - Pioneering trapped-ion quantum computers

These companies are investing heavily in quantum hardware, software, and making quantum computing accessible through cloud platforms.

## Emerging Applications

Practical applications are beginning to emerge across multiple sectors:

| Application Area | Description | Impact |
|-----------------|-------------|--------|
| Drug Discovery | Molecular simulation and protein folding | Accelerated pharmaceutical development |
| Finance | Risk analysis and portfolio optimization | More accurate financial modeling |
| Cryptography | Post-quantum encryption methods | Enhanced data security |
| Logistics | Supply chain and route optimization | Improved operational efficiency |
| Materials Science | Novel material discovery | Advanced material properties |

## Conclusion

2024 marks a pivotal year for quantum computing, transitioning from theoretical research to practical applications. While challenges remain, the progress in error correction, hardware stability, and commercial availability suggests that quantum computing is moving closer to mainstream adoption.
"""
    
    print("✅ Report completed\n")
    print(f"{'='*60}\n")
    
    return final_report


def main():
    """Main demo function."""
    
    print("\n" + "="*60)
    print("DEMO MODE - Simulated Research System")
    print("="*60)
    print("\nℹ️  This is a DEMO version using simulated responses.")
    print("For real web search, configure API keys in .env file:")
    print("  - GOOGLE_API_KEY (for Gemini)")
    print("  - TAVILY_API_KEY (for web search)")
    print("="*60 + "\n")
    
    # Example research query
    user_query = "What are the latest developments in quantum computing in 2024?"
    
    # Execute the demo research workflow
    final_report = demo_research(user_query)
    
    # Display the final report
    print("\n" + "="*60)
    print("FINAL RESEARCH REPORT (DEMO)")
    print("="*60 + "\n")
    print(final_report)
    
    # Save to file
    output_file = "demo_research_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Research Report (DEMO)\n\n")
        f.write(f"**Query:** {user_query}\n\n")
        f.write(f"---\n\n")
        f.write(final_report)
    
    print(f"\n✅ Demo report saved to: {output_file}")
    print("\n" + "="*60)
    print("To use the REAL system with live web search:")
    print("1. Get a valid Gemini API key from: https://aistudio.google.com/app/apikey")
    print("2. Get a Tavily API key from: https://tavily.com/")
    print("3. Update your .env file with both keys")
    print("4. Run: python example_usage.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
