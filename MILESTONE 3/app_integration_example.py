"""
Integration Example: How to Use Session Context Manager in app.py
==================================================================
This shows how to integrate the context-aware behavior into your Flask app.
"""

from flask import Flask, request, jsonify
from session_context_manager import (
    SessionContextManager, 
    QueryIntent,
    SessionContext
)
import database as db
from workflow import ResearchWorkflow

# Initialize context manager
context_manager = SessionContextManager()


# EXAMPLE 1: Modified research_in_chat endpoint
def research_in_chat_enhanced(chat_id: int):
    """
    Enhanced research endpoint with context awareness.
    
    This replaces your current @app.route('/api/chat/<int:chat_id>/research')
    """
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Query is required'}), 400
    
    # Get conversation history
    messages = db.get_chat_messages(chat_id)
    
    # Process query with context awareness
    routing_decision = context_manager.process_query(query, chat_id, messages)
    
    intent = routing_decision['intent']
    should_research = routing_decision['should_research']
    context = routing_decision['context']
    
    print(f"🎯 Intent detected: {intent}")
    print(f"📊 Should research: {should_research}")
    print(f"💡 Hint: {routing_decision['response_hint']}")
    
    # Route 1: Extract from session memory (FAST PATH)
    if not should_research:
        # Generate response from existing context
        response = context_manager.generate_contextual_response(
            QueryIntent[intent.upper()],
            context,
            query
        )
        
        # Store this Q&A exchange (even though it's from memory)
        db.add_message(chat_id, query, response)
        
        return jsonify({
            'success': True,
            'report': response,
            'papers': [],  # No new papers for context-based responses
            'metadata': {
                'source': 'session_memory',
                'intent': intent,
                'confidence': routing_decision['confidence'],
                'processing_time': 'instant'
            }
        })
    
    # Route 2: Run full research workflow (FULL PATH)
    else:
        try:
            # Prepare conversation history for workflow
            conversation_history = [
                {
                    'query': msg['query'],
                    'report': msg['report'],
                    'created_at': msg.get('created_at', '')
                }
                for msg in messages
            ]
            
            # Add context awareness note to help planner
            enhanced_query = query
            if context.last_research_topic and intent == 'comparison_request':
                enhanced_query = (
                    f"{query}\n"
                    f"[Context: Previously discussed '{context.last_research_topic}']"
                )
            
            # Run research workflow
            workflow = ResearchWorkflow(llm)  # Your existing LLM instance
            report, papers = workflow.run(
                query=enhanced_query,
                conversation_history=conversation_history
            )
            
            # Store message
            db.add_message(chat_id, query, report)
            
            return jsonify({
                'success': True,
                'report': report,
                'papers': papers,
                'metadata': {
                    'source': 'new_research',
                    'intent': intent,
                    'confidence': routing_decision['confidence'],
                    'papers_found': len(papers)
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


# EXAMPLE 2: Preview context endpoint (for debugging)
def preview_context(chat_id: int):
    """
    New endpoint to preview what context will be used.
    URL: GET /api/chat/<chat_id>/context
    """
    messages = db.get_chat_messages(chat_id)
    context = context_manager.build_context(chat_id, messages)
    
    return jsonify({
        'chat_id': chat_id,
        'last_research_topic': context.last_research_topic,
        'last_paper_title': context.last_paper_title,
        'has_methodology': bool(context.last_methodology),
        'has_findings': bool(context.last_findings),
        'message_count': len(messages),
    })


# EXAMPLE 3: Test intent detection endpoint
def test_intent_detection(chat_id: int):
    """
    Test endpoint to see what intent would be detected.
    URL: POST /api/chat/<chat_id>/test-intent
    Body: {"query": "what was the methodology?"}
    """
    data = request.get_json()
    query = data.get('query', '')
    
    messages = db.get_chat_messages(chat_id)
    routing_decision = context_manager.process_query(query, chat_id, messages)
    
    return jsonify({
        'query': query,
        'detected_intent': routing_decision['intent'],
        'confidence': routing_decision['confidence'],
        'should_research': routing_decision['should_research'],
        'response_hint': routing_decision['response_hint'],
        'has_previous_context': routing_decision['has_previous_context'],
    })


# EXAMPLE 4: Complete app.py integration snippet
"""
To integrate into your actual app.py:

1. Import at the top:
-----------------
from session_context_manager import SessionContextManager, QueryIntent

# Initialize globally
context_manager = SessionContextManager()


2. Replace your current research endpoint:
----------------------------------------
@app.route('/api/chat/<int:chat_id>/research', methods=['POST'])
def research_in_chat(chat_id):
    return research_in_chat_enhanced(chat_id)


3. Add debugging endpoints (optional):
------------------------------------
@app.route('/api/chat/<int:chat_id>/context', methods=['GET'])
def get_context_preview(chat_id):
    return preview_context(chat_id)

@app.route('/api/chat/<int:chat_id>/test-intent', methods=['POST'])
def test_intent(chat_id):
    return test_intent_detection(chat_id)


4. That's it! Your app now has context awareness.
"""


# EXAMPLE 5: Usage in orchestrator.py (alternative integration)
class ContextAwareOrchestrator:
    """
    Alternative: Integrate context manager into orchestrator instead of app.py
    """
    
    def __init__(self, llm):
        self.workflow = ResearchWorkflow(llm)
        self.context_manager = SessionContextManager()
    
    def research_with_context(
        self, 
        query: str, 
        chat_id: int, 
        messages: List[Dict]
    ) -> Tuple[str, List[Dict], Dict]:
        """
        Research with automatic context awareness.
        
        Returns:
            Tuple of (report, papers, metadata)
        """
        # Process query
        routing = self.context_manager.process_query(query, chat_id, messages)
        
        # Check if we should use context
        if not routing['should_research']:
            # Extract from memory
            response = self.context_manager.generate_contextual_response(
                QueryIntent[routing['intent'].upper()],
                routing['context'],
                query
            )
            return response, [], {'source': 'memory', 'intent': routing['intent']}
        
        # Run full research
        conversation_history = [
            {'query': m['query'], 'report': m['report']}
            for m in messages
        ]
        
        report, papers = self.workflow.run(query, conversation_history)
        
        return report, papers, {'source': 'research', 'intent': routing['intent']}
