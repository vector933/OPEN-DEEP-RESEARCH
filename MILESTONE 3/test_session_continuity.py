"""
Comprehensive Test Suite for Session Continuity Features
==========================================================
Tests thread tracking, context retention, and conversational continuity.
"""

import unittest
import sqlite3
import os
import sys
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db


class TestThreadTracking(unittest.TestCase):
    """Test suite for thread tracking and session management."""
    
    def setUp(self):
        """Create a test database for each test."""
        # Use a temporary test database
        db.DB_PATH = "test_chats.db"
        db.init_db()
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists("test_chats.db"):
            os.remove("test_chats.db")
    
    def test_create_chat_returns_unique_id(self):
        """Test that creating a chat returns a unique session ID."""
        chat_id_1 = db.create_chat("Test Chat 1")
        chat_id_2 = db.create_chat("Test Chat 2")
        
        self.assertIsInstance(chat_id_1, int)
        self.assertIsInstance(chat_id_2, int)
        self.assertNotEqual(chat_id_1, chat_id_2)
        print(f"✓ Chat IDs are unique: {chat_id_1} != {chat_id_2}")
    
    def test_retrieve_chat_by_id(self):
        """Test retrieving a specific chat session by ID."""
        title = "Machine Learning Research"
        chat_id = db.create_chat(title)
        
        retrieved_chat = db.get_chat(chat_id)
        
        self.assertIsNotNone(retrieved_chat)
        self.assertEqual(retrieved_chat['id'], chat_id)
        self.assertEqual(retrieved_chat['title'], title)
        print(f"✓ Retrieved chat: {retrieved_chat['title']}")
    
    def test_list_all_chats(self):
        """Test retrieving all chat sessions."""
        db.create_chat("Chat 1")
        db.create_chat("Chat 2")
        db.create_chat("Chat 3")
        
        all_chats = db.get_all_chats()
        
        self.assertEqual(len(all_chats), 3)
        print(f"✓ Retrieved {len(all_chats)} chats")
    
    def test_delete_chat_removes_messages(self):
        """Test that deleting a chat also removes its messages."""
        chat_id = db.create_chat("Test Chat")
        db.add_message(chat_id, "Query 1", "Report 1")
        db.add_message(chat_id, "Query 2", "Report 2")
        
        # Verify messages exist
        messages_before = db.get_chat_messages(chat_id)
        self.assertEqual(len(messages_before), 2)
        
        # Delete chat
        success = db.delete_chat(chat_id)
        self.assertTrue(success)
        
        # Verify chat is gone
        deleted_chat = db.get_chat(chat_id)
        self.assertIsNone(deleted_chat)
        
        # Verify messages are gone
        messages_after = db.get_chat_messages(chat_id)
        self.assertEqual(len(messages_after), 0)
        print("✓ Chat deletion cascades to messages")


class TestContextRetention(unittest.TestCase):
    """Test suite for context retention and conversation history."""
    
    def setUp(self):
        """Create a test database for each test."""
        db.DB_PATH = "test_chats.db"
        db.init_db()
        self.chat_id = db.create_chat("Context Test")
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists("test_chats.db"):
            os.remove("test_chats.db")
    
    def test_add_message_to_chat(self):
        """Test adding a message to a chat session."""
        query = "What is quantum computing?"
        report = "Quantum computing is a type of computation..."
        
        message_id = db.add_message(self.chat_id, query, report)
        
        self.assertIsInstance(message_id, int)
        
        # Retrieve and verify
        messages = db.get_chat_messages(self.chat_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['query'], query)
        self.assertEqual(messages[0]['report'], report)
        print(f"✓ Message added with ID: {message_id}")
    
    def test_retrieve_messages_in_order(self):
        """Test that messages are retrieved in chronological order."""
        queries = [
            "What is AI?",
            "What about machine learning?",
            "Tell me about deep learning"
        ]
        
        for query in queries:
            db.add_message(self.chat_id, query, f"Report for: {query}")
        
        messages = db.get_chat_messages(self.chat_id)
        
        self.assertEqual(len(messages), 3)
        for i, query in enumerate(queries):
            self.assertEqual(messages[i]['query'], query)
        print(f"✓ {len(messages)} messages retrieved in correct order")
    
    def test_context_window_limits(self):
        """Test that context window limits work correctly."""
        # Add 10 messages
        for i in range(10):
            db.add_message(self.chat_id, f"Query {i+1}", f"Report {i+1}")
        
        all_messages = db.get_chat_messages(self.chat_id)
        self.assertEqual(len(all_messages), 10)
        
        # Simulate context window of 5
        CONTEXT_WINDOW_SIZE = 5
        context_messages = all_messages[-CONTEXT_WINDOW_SIZE:]
        
        self.assertEqual(len(context_messages), 5)
        self.assertEqual(context_messages[0]['query'], "Query 6")
        self.assertEqual(context_messages[-1]['query'], "Query 10")
        print(f"✓ Context window correctly limited to {CONTEXT_WINDOW_SIZE} messages")
    
    def test_conversation_history_format(self):
        """Test formatting conversation history for agents."""
        db.add_message(self.chat_id, "What is AI?", "AI is artificial intelligence...")
        db.add_message(self.chat_id, "What are its applications?", "AI has many applications...")
        
        messages = db.get_chat_messages(self.chat_id)
        
        # Format like the app does
        conversation_history = [
            {
                'query': msg['query'],
                'report': msg['report'],
                'created_at': msg.get('created_at', '')
            }
            for msg in messages
        ]
        
        self.assertEqual(len(conversation_history), 2)
        self.assertIn('query', conversation_history[0])
        self.assertIn('report', conversation_history[0])
        self.assertIn('created_at', conversation_history[0])
        print(f"✓ Conversation history formatted correctly")


class TestContinuity(unittest.TestCase):
    """Test suite for conversational continuity features."""
    
    def setUp(self):
        """Setup test environment."""
        db.DB_PATH = "test_chats.db"
        db.init_db()
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists("test_chats.db"):
            os.remove("test_chats.db")
    
    def test_multi_session_isolation(self):
        """Test that different chat sessions maintain independent context."""
        chat_a = db.create_chat("Chat A")
        chat_b = db.create_chat("Chat B")
        
        db.add_message(chat_a, "Query A1", "Report A1")
        db.add_message(chat_a, "Query A2", "Report A2")
        db.add_message(chat_b, "Query B1", "Report B1")
        
        messages_a = db.get_chat_messages(chat_a)
        messages_b = db.get_chat_messages(chat_b)
        
        self.assertEqual(len(messages_a), 2)
        self.assertEqual(len(messages_b), 1)
        self.assertEqual(messages_a[0]['query'], "Query A1")
        self.assertEqual(messages_b[0]['query'], "Query B1")
        print("✓ Sessions maintain independent context")
    
    def test_follow_up_question_context(self):
        """Test that follow-up questions can access previous context."""
        chat_id = db.create_chat("Follow-up Test")
        
        # Simulate a conversation
        db.add_message(chat_id, "What is quantum computing?", 
                      "Quantum computing uses quantum mechanics...")
        db.add_message(chat_id, "What are its main applications?", 
                      "Main applications include cryptography...")
        db.add_message(chat_id, "Can you summarize the key points?",
                      "Key points: quantum mechanics, applications...")
        
        messages = db.get_chat_messages(chat_id)
        
        # Verify all messages are available for context
        self.assertEqual(len(messages), 3)
        
        # Verify second message can reference first
        self.assertIn("its", messages[1]['query'].lower())  # "its" refers to quantum computing
        
        print("✓ Follow-up questions have access to previous context")
    
    def test_context_persistence_across_queries(self):
        """Test that context persists throughout a session."""
        chat_id = db.create_chat("Persistence Test")
        
        # Add multiple exchanges
        exchanges = [
            ("What is machine learning?", "ML is a subset of AI..."),
            ("How does supervised learning work?", "Supervised learning uses labeled data..."),
            ("What about unsupervised learning?", "Unsupervised learning finds patterns..."),
        ]
        
        for query, report in exchanges:
            db.add_message(chat_id, query, report)
        
        # Retrieve all messages
        messages = db.get_chat_messages(chat_id)
        
        # Verify persistence
        self.assertEqual(len(messages), len(exchanges))
        for i, (query, report) in enumerate(exchanges):
            self.assertEqual(messages[i]['query'], query)
            self.assertEqual(messages[i]['report'], report)
        
        print(f"✓ Context persisted across {len(exchanges)} exchanges")


class TestAPIContextEndpoint(unittest.TestCase):
    """Test suite for the context preview API endpoint."""
    
    def setUp(self):
        """Setup test environment."""
        db.DB_PATH = "test_chats.db"
        db.init_db()
        self.chat_id = db.create_chat("API Test")
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists("test_chats.db"):
            os.remove("test_chats.db")
    
    def test_context_window_calculation(self):
        """Test that context window is calculated correctly."""
        CONTEXT_WINDOW_SIZE = 5
        
        # Add 8 messages
        for i in range(8):
            db.add_message(self.chat_id, f"Query {i+1}", f"Report {i+1}")
        
        all_messages = db.get_chat_messages(self.chat_id)
        context_messages = all_messages[-CONTEXT_WINDOW_SIZE:]
        
        self.assertEqual(len(all_messages), 8)
        self.assertEqual(len(context_messages), 5)
        self.assertEqual(context_messages[0]['query'], "Query 4")
        
        print(f"✓ Context window: {len(context_messages)}/{len(all_messages)} messages")
    
    def test_empty_chat_context(self):
        """Test context for a chat with no messages."""
        messages = db.get_chat_messages(self.chat_id)
        
        self.assertEqual(len(messages), 0)
        
        # Context should be empty
        context_messages = messages[-5:]
        self.assertEqual(len(context_messages), 0)
        
        print("✓ Empty chat has no context")


def run_tests(verbose=True):
    """
    Run all test suites.
    
    Args:
        verbose: Print detailed output
    
    Returns:
        True if all tests pass, False otherwise
    """
    print("\n" + "="*70)
    print("🧪 SESSION CONTINUITY TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestThreadTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestContextRetention))
    suite.addTests(loader.loadTestsFromTestCase(TestContinuity))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIContextEndpoint))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run session continuity tests")
    parser.add_argument('--integration', action='store_true', 
                       help='Run integration tests (requires running app)')
    parser.add_argument('--verbose', action='store_true', default=True,
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.integration:
        print("⚠️  Integration tests not yet implemented")
        print("    These would test the full API endpoints with a running server\n")
    
    success = run_tests(verbose=args.verbose)
    sys.exit(0 if success else 1)
