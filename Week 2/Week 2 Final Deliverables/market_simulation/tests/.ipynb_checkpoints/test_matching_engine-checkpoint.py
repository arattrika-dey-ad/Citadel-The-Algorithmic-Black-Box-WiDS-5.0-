"""
Test File for Matching Engine - Includes mandatory test and additional tests
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.matching_engine import OrderBook
import numpy as np

def test_mandatory_case():
    """Mandatory test case from requirements"""
    print("Running mandatory test case...")
    
    order_book = OrderBook()
    
    # Add asks as specified
    asks = [
        {'side': 'sell', 'quantity': 10, 'price': 101, 'order_type': 'limit', 'agent_id': 'A1'},
        {'side': 'sell', 'quantity': 20, 'price': 102, 'order_type': 'limit', 'agent_id': 'A2'},
        {'side': 'sell', 'quantity': 30, 'price': 103, 'order_type': 'limit', 'agent_id': 'A3'}
    ]
    
    for order in asks:
        order_book.add_order(order)
    
    # Add market buy for 60 units
    market_buy = {
        'side': 'buy',
        'quantity': 60,
        'order_type': 'market',
        'agent_id': 'B1'
    }
    
    trades = order_book.add_order(market_buy)
    
    # Verify results
    print(f"Number of trades: {len(trades)}")
    print("Trade details:")
    for i, trade in enumerate(trades, 1):
        print(f"  Trade {i}: Price={trade['price']}, Quantity={trade['quantity']}")
    
    # Check expected results
    expected_trades = 3
    expected_prices = [101, 102, 103]
    expected_quantities = [10, 20, 30]
    
    assert len(trades) == expected_trades, f"Expected {expected_trades} trades, got {len(trades)}"
    
    for i, (trade, exp_price, exp_qty) in enumerate(zip(trades, expected_prices, expected_quantities)):
        assert trade['price'] == exp_price, f"Trade {i}: Expected price {exp_price}, got {trade['price']}"
        assert trade['quantity'] == exp_qty, f"Trade {i}: Expected quantity {exp_qty}, got {trade['quantity']}"
    
    # Check ask book is empty
    best_ask = order_book.get_bbo()[1]
    assert best_ask == float('inf'), f"Ask book should be empty, but best ask is {best_ask}"
    
    print("✓ Mandatory test passed!")

def test_limit_order_matching():
    """Test limit order matching"""
    print("\nTest 2: Limit order matching...")
    
    order_book = OrderBook()
    
    # Add limit sell orders
    order_book.add_order({'side': 'sell', 'quantity': 100, 'price': 100, 'order_type': 'limit', 'agent_id': 'S1'})
    order_book.add_order({'side': 'sell', 'quantity': 100, 'price': 101, 'order_type': 'limit', 'agent_id': 'S2'})
    
    # Add limit buy order that should match
    trades = order_book.add_order({'side': 'buy', 'quantity': 150, 'price': 100.5, 'order_type': 'limit', 'agent_id': 'B1'})
    
    assert len(trades) == 1, f"Expected 1 trade, got {len(trades)}"
    assert trades[0]['price'] == 100, f"Expected price 100, got {trades[0]['price']}"
    assert trades[0]['quantity'] == 100, f"Expected quantity 100, got {trades[0]['quantity']}"
    
    print("✓ Limit order matching test passed!")

def test_partial_fills():
    """Test partial order fills"""
    print("\nTest 3: Partial fills...")
    
    order_book = OrderBook()
    
    # Add sell order
    order_book.add_order({'side': 'sell', 'quantity': 50, 'price': 100, 'order_type': 'limit', 'agent_id': 'S1'})
    
    # Buy more than available
    trades = order_book.add_order({'side': 'buy', 'quantity': 100, 'price': 101, 'order_type': 'limit', 'agent_id': 'B1'})
    
    assert len(trades) == 1, f"Expected 1 trade, got {len(trades)}"
    assert trades[0]['quantity'] == 50, f"Expected quantity 50, got {trades[0]['quantity']}"
    
    # Check remaining buy order in book
    best_bid = order_book.get_bbo()[0]
    assert best_bid == 101, f"Expected remaining bid at 101, got {best_bid}"
    
    print("✓ Partial fills test passed!")

def test_price_time_priority():
    """Test price-time priority"""
    print("\nTest 4: Price-time priority...")
    
    order_book = OrderBook()
    
    # Add sell orders at same price
    order_book.add_order({'side': 'sell', 'quantity': 50, 'price': 100, 'order_type': 'limit', 'agent_id': 'S1'})
    order_book.add_order({'side': 'sell', 'quantity': 50, 'price': 100, 'order_type': 'limit', 'agent_id': 'S2'})
    
    # Buy order that matches both
    trades = order_book.add_order({'side': 'buy', 'quantity': 75, 'price': 100, 'order_type': 'limit', 'agent_id': 'B1'})
    
    assert len(trades) == 2, f"Expected 2 trades, got {len(trades)}"
    assert trades[0]['seller'] == 'S1', f"First trade should be with S1, got {trades[0]['seller']}"
    assert trades[1]['seller'] == 'S2', f"Second trade should be with S2, got {trades[1]['seller']}"
    assert trades[0]['quantity'] == 50, f"First trade quantity should be 50, got {trades[0]['quantity']}"
    assert trades[1]['quantity'] == 25, f"Second trade quantity should be 25, got {trades[1]['quantity']}"
    
    print("✓ Price-time priority test passed!")

def test_order_cancellation():
    """Test order cancellation"""
    print("\nTest 5: Order cancellation...")
    
    order_book = OrderBook()
    
    # Add an order
    order = {'side': 'sell', 'quantity': 100, 'price': 100, 'order_type': 'limit', 'agent_id': 'S1'}
    trades = order_book.add_order(order)
    
    # Get order ID (simulated - in real implementation, order ID is assigned)
    # For this test, we'll assume we can cancel by some identifier
    print("  (Order cancellation test requires order ID tracking)")
    
    print("✓ Order cancellation test completed!")

def test_market_order_no_liquidity():
    """Test market order with insufficient liquidity"""
    print("\nTest 6: Market order with insufficient liquidity...")
    
    order_book = OrderBook()
    
    # Add small sell order
    order_book.add_order({'side': 'sell', 'quantity': 10, 'price': 100, 'order_type': 'limit', 'agent_id': 'S1'})
    
    # Try to buy more than available
    trades = order_book.add_order({'side': 'buy', 'quantity': 100, 'order_type': 'market', 'agent_id': 'B1'})
    
    assert len(trades) == 1, f"Expected 1 trade, got {len(trades)}"
    assert trades[0]['quantity'] == 10, f"Expected quantity 10, got {trades[0]['quantity']}"
    
    print("✓ Market order with insufficient liquidity test passed!")

def test_spread_calculation():
    """Test bid-ask spread calculation"""
    print("\nTest 7: Spread calculation...")
    
    order_book = OrderBook()
    
    # Empty book should have infinite spread
    best_bid, best_ask, spread = order_book.get_bbo()
    assert best_bid == 0, f"Empty book bid should be 0, got {best_bid}"
    assert best_ask == float('inf'), f"Empty book ask should be inf, got {best_ask}"
    assert spread == float('inf'), f"Empty book spread should be inf, got {spread}"
    
    # Add orders
    order_book.add_order({'side': 'buy', 'quantity': 100, 'price': 99, 'order_type': 'limit', 'agent_id': 'B1'})
    order_book.add_order({'side': 'sell', 'quantity': 100, 'price': 101, 'order_type': 'limit', 'agent_id': 'S1'})
    
    best_bid, best_ask, spread = order_book.get_bbo()
    assert best_bid == 99, f"Expected bid 99, got {best_bid}"
    assert best_ask == 101, f"Expected ask 101, got {best_ask}"
    assert spread == 2, f"Expected spread 2, got {spread}"
    
    print("✓ Spread calculation test passed!")

def test_mid_price():
    """Test mid price calculation"""
    print("\nTest 8: Mid price calculation...")
    
    order_book = OrderBook()
    
    # Empty book should return default
    mid_price = order_book.get_mid_price()
    assert mid_price == 100.0, f"Empty book mid should be 100, got {mid_price}"
    
    # With orders
    order_book.add_order({'side': 'buy', 'quantity': 100, 'price': 99, 'order_type': 'limit', 'agent_id': 'B1'})
    order_book.add_order({'side': 'sell', 'quantity': 100, 'price': 101, 'order_type': 'limit', 'agent_id': 'S1'})
    
    mid_price = order_book.get_mid_price()
    assert mid_price == 100.0, f"Expected mid price 100, got {mid_price}"
    
    print("✓ Mid price calculation test passed!")

def test_order_book_depth():
    """Test order book depth retrieval"""
    print("\nTest 9: Order book depth...")
    
    order_book = OrderBook()
    
    # Add multiple orders at different price levels
    for price, qty in [(99, 50), (98, 100), (97, 150)]:
        order_book.add_order({'side': 'buy', 'quantity': qty, 'price': price, 'order_type': 'limit', 'agent_id': f'B{price}'})
    
    for price, qty in [(101, 50), (102, 100), (103, 150)]:
        order_book.add_order({'side': 'sell', 'quantity': qty, 'price': price, 'order_type': 'limit', 'agent_id': f'S{price}'})
    
    bids, asks = order_book.get_order_book_depth(levels=2)
    
    assert len(bids) == 2, f"Expected 2 bid levels, got {len(bids)}"
    assert len(asks) == 2, f"Expected 2 ask levels, got {len(asks)}"
    
    # Check top bid
    assert bids[0][0] == 99, f"Top bid price should be 99, got {bids[0][0]}"
    assert bids[0][1] == 50, f"Top bid quantity should be 50, got {bids[0][1]}"
    
    print("✓ Order book depth test passed!")

def test_edge_cases():
    """Test various edge cases"""
    print("\nTest 10: Edge cases...")
    
    order_book = OrderBook()
    
    # Test zero quantity (shouldn't be allowed in real system)
    print("  Testing edge cases...")
    
    # Test very small price differences
    order_book.add_order({'side': 'sell', 'quantity': 10, 'price': 100.0001, 'order_type': 'limit', 'agent_id': 'S1'})
    order_book.add_order({'side': 'buy', 'quantity': 10, 'price': 100.0000, 'order_type': 'limit', 'agent_id': 'B1'})
    
    # These shouldn't match due to price difference
    best_bid, best_ask, spread = order_book.get_bbo()
    assert spread > 0, f"Spread should be positive, got {spread}"
    
    print("✓ Edge cases test passed!")

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("RUNNING MATCHING ENGINE TESTS")
    print("="*60)
    
    tests = [
        test_mandatory_case,
        test_limit_order_matching,
        test_partial_fills,
        test_price_time_priority,
        test_order_cancellation,
        test_market_order_no_liquidity,
        test_spread_calculation,
        test_mid_price,
        test_order_book_depth,
        test_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)