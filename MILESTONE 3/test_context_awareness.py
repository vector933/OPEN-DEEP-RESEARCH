"""
Test Suite for Context-Aware Behavior
======================================
Tests the session context manager and intent detection.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from session_context_manager import (
    SessionContextManager,
    QueryIntent,
    ContextAwareIntentDetector,
    ReportExtractor,
    SessionContext
)


class TestIntentDetection(unittest.TestCase):
    """Test intent detection patterns."""
    
    def setUp(self):
        self.detector = ContextAwareIntentDetector()
        self.context_manager = SessionContextManager()
    
    def test_summary_request_detection(self):
        """Test detection of summary requests."""
        test_queries = [
            "give me a summary",
            "summarize that",
            "what was it about",
            "tldr",
            "brief overview please"
        ]
        
        for query in test_queries:
            intent, confidence = self.detector.detect_intent(
                query, [], SessionContext(chat_id=1)
            )
            self.assertEqual(
                intent, 
                QueryIntent.SUMMARY_REQUEST,
                f"Failed for query: '{query}'"
            )
            print(f"✓ Detected summary request: '{query}'")
    
    def test_methodology_request_detection(self):
        """Test detection of methodology requests."""
        test_queries = [
            "what was the methodology",
            "how did they conduct the research",
            "what approach did they use",
            "research method",
            "experimental design"
        ]
        
        for query in test_queries:
            intent, confidence = self.detector.detect_intent(
                query, [], SessionContext(chat_id=1)
            )
            self.assertEqual(
                intent,
                QueryIntent.METHODOLOGY_REQUEST,
                f"Failed for query: '{query}'"
            )
            print(f"✓ Detected methodology request: '{query}'")
    
    def test_findings_request_detection(self):
        """Test detection of findings requests."""
        test_queries = [
            "what were the findings",
            "what did they find",
            "key results",
            "main conclusions"
        ]
        
        for query in test_queries:
            intent, confidence = self.detector.detect_intent(
                query, [], SessionContext(chat_id=1)
            )
            self.assertEqual(
                intent,
                QueryIntent.FINDINGS_REQUEST,
                f"Failed for query: '{query}'"
            )
            print(f"✓ Detected findings request: '{query}'")
    
    def test_comparison_request_detection(self):
        """Test detection of comparison requests."""
        test_queries = [
            "compare it to X",
            "what's the difference",
            "how is it different from",
            "versus",
            "similarities and differences"
        ]
        
        for query in test_queries:
            intent, confidence = self.detector.detect_intent(
                query, [], SessionContext(chat_id=1)
            )
            self.assertEqual(
                intent,
                QueryIntent.COMPARISON_REQUEST,
                f"Failed for query: '{query}'"
            )
            print(f"✓ Detected comparison request: '{query}'")
    
    def test_vague_followup_detection(self):
        """Test detection of vague follow-up queries."""
        # Create mock history
        history = [
            {'query': 'What is quantum computing?', 'report': 'Quantum computing is...'}
        ]
        
        test_queries = [
            "tell me more",
            "what about it",
            "how about that",
            "and its applications?"
        ]
        
        for query in test_queries:
            intent, confidence = self.detector.detect_intent(
                query, history, SessionContext(chat_id=1)
            )
            self.assertEqual(
                intent,
                QueryIntent.FOLLOWUP_VAGUE,
                f"Failed for query: '{query}'"
            )
            print(f"✓ Detected vague follow-up: '{query}'")
    
    def test_new_research_detection(self):
        """Test that new topics are correctly identified."""
        query = "What are the applications of artificial intelligence in healthcare?"
        
        intent, confidence = self.detector.detect_intent(
            query, [], SessionContext(chat_id=1)
        )
        
        self.assertEqual(intent, QueryIntent.NEW_RESEARCH)
        print(f"✓ Detected new research query")


class TestReportExtraction(unittest.TestCase):
    """Test report section extraction."""
    
    def setUp(self):
        self.extractor = ReportExtractor()
        
        # Sample report
        self.sample_report = """
# Quantum Computing Applications

## Summary
Quantum computing represents a paradigm shift in computational capabilities.
It leverages quantum mechanical phenomena for processing information.
This has profound implications for cryptography, optimization, and simulation.

## Methodology
The research employed the following approach:
- Literature review of 50+ academic papers
- Analysis of quantum algorithms (Shor's, Grover's)
- Evaluation of current quantum hardware capabilities
- Sample size: 25 quantum computing implementations
- Data analysis: Comparative performance metrics

## Key Findings
1. Quantum computers excel at specific problem classes
2. Current hardware faces decoherence challenges  
3. Hybrid classical-quantum approaches show promise
4. Cryptographic implications are significant

## References
1. Nielsen, M. A., & Chuang, I. L. (2010). Quantum Computation...
2. Shor, P. W. (1997). Polynomial-time algorithms...
"""
    
    def test_extract_summary(self):
        """Test summary extraction."""
        summary = self.extractor.extract_summary(self.sample_report)
        
        self.assertIsNotNone(summary)
        self.assertIn("paradigm shift", summary.lower())
        print(f"✓ Extracted summary: {len(summary)} chars")
    
    def test_extract_methodology(self):
        """Test methodology extraction."""
        methodology = self.extractor.extract_methodology(self.sample_report)
        
        self.assertIsNotNone(methodology)
        self.assertIn("Literature review", methodology)
        self.assertIn("Sample size", methodology)
        print(f"✓ Extracted methodology: {len(methodology)} chars")
    
    def test_extract_findings(self):
        """Test findings extraction."""
        findings = self.extractor.extract_findings(self.sample_report)
        
        self.assertIsNotNone(findings)
        self.assertIn("decoherence", findings.lower())
        print(f"✓ Extracted findings: {len(findings)} chars")
    
    def test_extract_references(self):
        """Test references extraction."""
        references = self.extractor.extract_references(self.sample_report)
        
        self.assertIsNotNone(references)
        self.assertIn("Nielsen", references)
        print(f"✓ Extracted references: {len(references)} chars")


class TestContextBuilding(unittest.TestCase):
    """Test session context building."""
    
    def setUp(self):
        self.context_manager = SessionContextManager()
    
    def test_build_context_from_messages(self):
        """Test building context from message history."""
        messages = [
            {
                'query': 'What is quantum computing?',
                'report': '# Quantum Computing\n\nQuantum computing is...',
                'created_at': '2024-01-01 10:00:00'
            },
            {
                'query': 'Tell me more',
                'report': 'Additional details...',
                'created_at': '2024-01-01 10:05:00'
            }
        ]
        
        context = self.context_manager.build_context(chat_id=1, messages=messages)
        
        self.assertEqual(context.chat_id, 1)
        self.assertIsNotNone(context.last_research_topic)
        self.assertIsNotNone(context.last_report)
        self.assertIn("Quantum", context.last_research_topic)
        print(f"✓ Built context: topic='{context.last_research_topic}'")
    
    def test_empty_context(self):
        """Test context building with no messages."""
        context = self.context_manager.build_context(chat_id=1, messages=[])
        
        self.assertEqual(context.chat_id, 1)
        self.assertIsNone(context.last_research_topic)
        self.assertIsNone(context.last_report)
        print("✓ Handled empty message history")


class TestEndToEndBehavior(unittest.TestCase):
    """Test complete behavioral rules."""
    
    def setUp(self):
        self.context_manager = SessionContextManager()
    
    def test_summary_request_with_context(self):
        """Test: User asks for summary of previous research."""
        # Simulate previous research
        messages = [
            {
                'query': 'What is machine learning?',
                'report': """# Machine Learning Overview
                
## Summary
Machine learning is a subset of AI that enables systems to learn from data.
It has revolutionized many industries through pattern recognition.
Applications range from healthcare to autonomous vehicles.

## Key Findings
- Supervised learning dominates current applications
- Deep learning has transformed computer vision
"""
            }
        ]
        
        # User asks for summary
        query = "give me a summary"
        
        routing = self.context_manager.process_query(query, 1, messages)
        
        # Should NOT trigger new research
        self.assertFalse(routing['should_research'])
        self.assertEqual(routing['intent'], QueryIntent.SUMMARY_REQUEST.value)
        
        # Generate response
        response = self.context_manager.generate_contextual_response(
            QueryIntent.SUMMARY_REQUEST,
            routing['context'],
            query
        )
        
        self.assertIn("Machine learning", response)
        print("✓ Summary request handled correctly")
    
    def test_methodology_request_with_context(self):
        """Test: User asks for methodology."""
        messages = [
            {
                'query': 'Research on deep learning',
                'report': """# Deep Learning Research
                
## Methodology
- Survey of 100+ deep learning papers
- Analysis of CNN, RNN, and Transformer architectures
- Benchmark testing on ImageNet dataset
- Sample size: 1000 model configurations
"""
            }
        ]
        
        query = "what was the methodology?"
        
        routing = self.context_manager.process_query(query, 1, messages)
        
        self.assertFalse(routing['should_research'])
        
        response = self.context_manager.generate_contextual_response(
            QueryIntent.METHODOLOGY_REQUEST,
            routing['context'],
            query
        )
        
        self.assertIn("Survey of 100+", response)
        print("✓ Methodology request handled correctly")


def run_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 CONTEXT AWARENESS TEST SUITE")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestIntentDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestReportExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestContextBuilding))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndBehavior))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
