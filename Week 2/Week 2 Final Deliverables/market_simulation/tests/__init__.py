"""
Tests Module
Unit tests and integration tests for the market simulation.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test discovery constants
TEST_PATTERNS = ['test_*.py', '*_test.py']

def run_all_tests():
    """
    Run all tests in the tests directory.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    import unittest
    import glob
    
    # Discover all test files
    test_files = []
    for pattern in TEST_PATTERNS:
        test_files.extend(glob.glob(os.path.join(os.path.dirname(__file__), pattern)))
    
    if not test_files:
        print("No test files found!")
        return False
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_file in test_files:
        module_name = os.path.splitext(os.path.basename(test_file))[0]
        try:
            # Import test module
            spec = importlib.util.spec_from_file_location(module_name, test_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Add tests to suite
            tests = loader.loadTestsFromModule(module)
            suite.addTest(tests)
        except Exception as e:
            print(f"Error loading tests from {test_file}: {e}")
    
    # Run test suite
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def test_matching_engine_quick():
    """Quick test of matching engine functionality."""
    try:
        from tests.test_matching_engine import test_mandatory_case
        test_mandatory_case()
        print("✓ Matching engine quick test passed!")
        return True
    except Exception as e:
        print(f"✗ Matching engine quick test failed: {e}")
        return False

def test_agent_creation():
    """Test that all agent types can be created."""
    try:
        from agents import NoiseTrader, MomentumAgent, MarketMakerAgent
        
        agents = [
            NoiseTrader(agent_id='test_noise'),
            MomentumAgent(agent_id='test_momentum'),
            MarketMakerAgent(agent_id='test_mm')
        ]
        
        for agent in agents:
            assert hasattr(agent, 'id'), f"Agent missing id: {agent}"
            assert hasattr(agent, 'cash'), f"Agent missing cash: {agent}"
            assert hasattr(agent, 'inventory'), f"Agent missing inventory: {agent}"
            assert hasattr(agent, 'get_action'), f"Agent missing get_action: {agent}"
        
        print("✓ Agent creation test passed!")
        return True
    except Exception as e:
        print(f"✗ Agent creation test failed: {e}")
        return False

def test_analytics_pipeline():
    """Test analytics pipeline creation."""
    try:
        from analytics import create_analytics_pipeline
        
        trade_tape, snapshots, metrics = create_analytics_pipeline()
        
        assert trade_tape is not None, "Trade tape not created"
        assert snapshots is not None, "Snapshots not created"
        assert metrics is not None, "Metrics not created"
        
        print("✓ Analytics pipeline test passed!")
        return True
    except Exception as e:
        print(f"✗ Analytics pipeline test failed: {e}")
        return False

def run_smoke_tests():
    """
    Run a set of smoke tests to verify basic functionality.
    
    Returns:
        dict: Test results
    """
    import importlib
    
    tests = {
        'matching_engine': test_matching_engine_quick,
        'agent_creation': test_agent_creation,
        'analytics_pipeline': test_analytics_pipeline
    }
    
    results = {}
    for test_name, test_func in tests.items():
        print(f"\nRunning {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  Error: {e}")
            results[test_name] = False
    
    print("\n" + "="*50)
    print("SMOKE TEST RESULTS")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return results

# Make test functions available
__all__ = [
    'run_all_tests',
    'run_smoke_tests',
    'test_matching_engine_quick',
    'test_agent_creation',
    'test_analytics_pipeline'
]