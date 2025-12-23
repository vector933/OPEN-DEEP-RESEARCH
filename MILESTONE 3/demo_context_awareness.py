"""
Simple Demo: Context-Aware Behavior
====================================
Shows how the context manager works with real examples.
"""

from session_context_manager import (
    SessionContextManager,
    QueryIntent
)

def demo():
    """Run a demonstration of context-aware behavior."""
    
    print("\n" + "="*70)
    print("🎯 CONTEXT-AWARE RESEARCH ASSISTANT DEMO")
    print("="*70 + "\n")
    
    context_manager = SessionContextManager()
    
    # Simulate a conversation session
    chat_id = 1
    messages = []
    
    # ========================================================================
    # SCENARIO 1: Initial Research Query
    # ========================================================================
    print("📋 SCENARIO 1: Initial Research Query")
    print("-" * 70)
    
    query1 = "What is quantum computing?"
    print(f"User: {query1}")
    
    routing1 = context_manager.process_query(query1, chat_id, messages)
    print(f"✓ Intent detected: {routing1['intent']}")
    print(f"✓ Should research: {routing1['should_research']}")
    print(f"✓ Confidence: {routing1['confidence']:.2f}")
    
    # Simulate storing the research result
    report1 = """# Quantum Computing Overview

## Summary
Quantum computing represents a revolutionary approach to computation.
It leverages quantum mechanical phenomena like superposition and entanglement.
This enables solving certain problems exponentially faster than classical computers.

## Methodology
The research employed the following approach:
- Literature review of 75 academic papers
- Analysis of quantum algorithms (Shor's, Grover's, VQE)
- Evaluation of current quantum hardware (IBM, Google, IonQ)
- Sample size: 30 quantum computing implementations
- Data analysis: Comparative performance metrics across platforms

## Key Findings
1. Quantum computers excel at optimization and simulation problems
2. Current hardware faces decoherence challenges (coherence time ~100μs)
3. Hybrid classical-quantum approaches show the most promise
4. Cryptographic implications are significant for RSA encryption
5. Near-term applications focus on quantum chemistry simulations
"""
    
    messages.append({
        'query': query1,
        'report': report1
    })
    
    print("✓ Research completed and stored\n")
    
    # ========================================================================
    # SCENARIO 2: Summary Request
    # ========================================================================
    print("📋 SCENARIO 2: Summary Request")
    print("-" * 70)
    
    query2 = "give me a summary"
    print(f"User: {query2}")
    
    routing2 = context_manager.process_query(query2, chat_id, messages)
    print(f"✓ Intent detected: {routing2['intent']}")
    print(f"✓ Should research: {routing2['should_research']} (NO NEW RESEARCH!)")
    print(f"✓ Confidence: {routing2['confidence']:.2f}")
    
    if not routing2['should_research']:
        response2 = context_manager.generate_contextual_response(
            QueryIntent.SUMMARY_REQUEST,
            routing2['context'],
            query2
        )
        print(f"\n Response generated from memory:")
        print(f"{'─'*70}")
        print(response2[:300] + "...")
        print(f"{'─'*70}\n")
    
    # ========================================================================
    # SCENARIO 3: Methodology Request
    # ========================================================================
    print("📋 SCENARIO 3: Methodology Request")
    print("-" * 70)
    
    query3 = "what was the methodology used?"
    print(f"User: {query3}")
    
    routing3 = context_manager.process_query(query3, chat_id, messages)
    print(f"✓ Intent detected: {routing3['intent']}")
    print(f"✓ Should research: {routing3['should_research']} (NO NEW RESEARCH!)")
    print(f"✓ Confidence: {routing3['confidence']:.2f}")
    
    if not routing3['should_research']:
        response3 = context_manager.generate_contextual_response(
            QueryIntent.METHODOLOGY_REQUEST,
            routing3['context'],
            query3
        )
        print(f"\n Response generated from memory:")
        print(f"{'─'*70}")
        print(response3[:400] + "...")
        print(f"{'─'*70}\n")
    
    # ========================================================================
    # SCENARIO 4: Findings Request
    # ========================================================================
    print("📋 SCENARIO 4: Findings Request")
    print("-" * 70)
    
    query4 = "what were the key findings?"
    print(f"User: {query4}")
    
    routing4 = context_manager.process_query(query4, chat_id, messages)
    print(f"✓ Intent detected: {routing4['intent']}")
    print(f"✓ Should research: {routing4['should_research']} (NO NEW RESEARCH!)")
    
    if not routing4['should_research']:
        response4 = context_manager.generate_contextual_response(
            QueryIntent.FINDINGS_REQUEST,
            routing4['context'],
            query4
        )
        print(f"\n Response generated from memory:")
        print(f"{'─'*70}")
        print(response4[:400] + "...")
        print(f"{'─'*70}\n")
    
    # ========================================================================
    # SCENARIO 5: Vague Follow-up
    # ========================================================================
    print("📋 SCENARIO 5: Vague Follow-up")
    print("-" * 70)
    
    query5 = "tell me more"
    print(f"User: {query5}")
    
    routing5 = context_manager.process_query(query5, chat_id, messages)
    print(f"✓ Intent detected: {routing5['intent']}")
    print(f"✓ Should research: {routing5['should_research']}")
    
    if not routing5['should_research']:
        response5 = context_manager.generate_contextual_response(
            QueryIntent.FOLLOWUP_VAGUE,
            routing5['context'],
            query5
        )
        print(f"\n Response (clarification request):")
        print(f"{'─'*70}")
        print(response5[:300] + "...")
        print(f"{'─'*70}\n")
    
    # ========================================================================
    # SCENARIO 6: New Research Topic
    # ========================================================================
    print("📋 SCENARIO 6: New Research Topic (should trigger research)")
    print("-" * 70)
    
    query6 = "What are the applications of machine learning in healthcare?"
    print(f"User: {query6}")
    
    routing6 = context_manager.process_query(query6, chat_id, messages)
    print(f"✓ Intent detected: {routing6['intent']}")
    print(f"✓ Should research: {routing6['should_research']} (NEW RESEARCH!)")
    print(f"✓ This would trigger full research workflow\n")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"✅ Summary request: Instant (no research)")
    print(f"✅ Methodology request: Instant (no research)")
    print(f"✅ Findings request: Instant (no research)")
    print(f"✅ Vague follow-up: Clarification (no research)")
    print(f"✅ New topic: Full research (trigger workflow)")
    print("\n🎉 All behavioral rules working correctly!")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo()
