"""
Test Script for LangGraph Workflow and Conversation Memory
===========================================================
This script tests the LangGraph workflow and conversation memory integration.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from workflow import ResearchWorkflow

# Load environment variables
load_dotenv()

def test_langgraph_workflow():
    """Test the LangGraph workflow without conversation history."""
    print("\n" + "="*60)
    print("TEST 1: LangGraph Workflow (No Conversation History)")
    print("="*60 + "\n")
    
    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Create workflow
    workflow = ResearchWorkflow(llm)
    
    # Test query
    query = "What is quantum computing?"
    
    print(f"Query: {query}\n")
    
    try:
        # Run workflow
        report, papers = workflow.run(query=query)
        
        print("\n✅ Workflow executed successfully!")
        print(f"📚 Papers found: {len(papers)}")
        print(f"📝 Report length: {len(report)} characters")
        print("\nFirst 500 characters of report:")
        print("-" * 60)
        print(report[:500] + "...")
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_memory():
    """Test conversation memory integration."""
    print("\n" + "="*60)
    print("TEST 2: Conversation Memory Integration")
    print("="*60 + "\n")
    
    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Create workflow
    workflow = ResearchWorkflow(llm)
    
    # Simulate conversation history
    conversation_history = [
        {
            'query': 'What is quantum computing?',
            'report': 'Quantum computing is a type of computation that harnesses quantum mechanical phenomena...'
        }
    ]
    
    # Follow-up query
    query = "What are its main applications?"
    
    print(f"Previous Query: {conversation_history[0]['query']}")
    print(f"Current Query: {query}")
    print("\nExpected: Should understand 'its' refers to quantum computing\n")
    
    try:
        # Run workflow with conversation history
        report, papers = workflow.run(
            query=query,
            conversation_history=conversation_history
        )
        
        print("\n✅ Workflow with memory executed successfully!")
        print(f"📚 Papers found: {len(papers)}")
        print(f"📝 Report length: {len(report)} characters")
        print("\nFirst 500 characters of report:")
        print("-" * 60)
        print(report[:500] + "...")
        print("-" * 60)
        
        # Check if report mentions quantum computing
        if 'quantum' in report.lower():
            print("\n✅ Report correctly references quantum computing context!")
        else:
            print("\n⚠️ Report may not have used conversation context")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 TESTING LANGGRAPH & CONVERSATION MEMORY")
    print("="*60)
    
    results = []
    
    # Test 1: Basic workflow
    results.append(("LangGraph Workflow", test_langgraph_workflow()))
    
    # Test 2: Conversation memory
    results.append(("Conversation Memory", test_conversation_memory()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
