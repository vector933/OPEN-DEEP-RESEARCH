"""Quick test runner to see detailed output"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_session_continuity import *

if __name__ == "__main__":
    # Run with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestThreadTracking)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.failures:
        print("\n\n" + "="*70)
        print("FAILURES DETAILS:")
        print("="*70)
        for test, traceback in result.failures:
            print(f"\n{test}:\n{traceback}")
