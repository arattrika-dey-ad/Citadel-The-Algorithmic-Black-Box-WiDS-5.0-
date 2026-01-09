"""
Engine Module
Core simulation engine components.
"""

from .event_loop import EventLoop, Event
from .matching_engine import OrderBook

__all__ = [
    "EventLoop",
    "Event",
    "OrderBook"
]

# Engine constants
SIMULATION_TICK = 0.001  # Minimum time increment in seconds
MAX_SIMULATION_TIME = 24 * 60 * 60  # 24 hours in seconds
MAX_EVENTS = 1000000  # Maximum number of events to process

# Event type constants
EVENT_TYPES = {
    'ORDER_ARRIVAL': 'order_arrival',
    'ORDER_CANCEL': 'order_cancel',
    'SNAPSHOT': 'snapshot',
    'MARKET_OPEN': 'market_open',
    'MARKET_CLOSE': 'market_close',
    'AGENT_ACTION': 'agent_action'
}

def create_default_event_loop():
    """
    Create a pre-configured event loop.
    
    Returns:
        EventLoop instance with default settings
    """
    return EventLoop(start_time=0.0)

def create_order_book():
    """
    Create a new order book instance.
    
    Returns:
        OrderBook instance
    """
    return OrderBook()

def validate_order(order):
    """
    Validate an order dictionary.
    
    Args:
        order: Order dictionary
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['side', 'quantity', 'order_type', 'agent_id']
    
    for field in required_fields:
        if field not in order:
            return False, f"Missing required field: {field}"
    
    # Validate side
    if order['side'] not in ['buy', 'sell']:
        return False, f"Invalid side: {order['side']}. Must be 'buy' or 'sell'"
    
    # Validate order type
    if order['order_type'] not in ['market', 'limit']:
        return False, f"Invalid order type: {order['order_type']}. Must be 'market' or 'limit'"
    
    # Validate quantity
    if not isinstance(order['quantity'], (int, float)) or order['quantity'] <= 0:
        return False, f"Invalid quantity: {order['quantity']}. Must be positive number"
    
    # Validate price for limit orders
    if order['order_type'] == 'limit':
        if 'price' not in order:
            return False, "Limit orders must have a price"
        if not isinstance(order['price'], (int, float)) or order['price'] <= 0:
            return False, f"Invalid price: {order['price']}. Must be positive number"
    
    return True, "Order is valid"