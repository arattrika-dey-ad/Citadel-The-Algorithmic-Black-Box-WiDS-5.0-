"""
Momentum Agent - Trades based on moving average crossover
"""
import numpy as np
from .base_agent import BaseAgent

class MomentumAgent(BaseAgent):
    """Agent that trades based on momentum (SMA crossover)"""
    
    def __init__(self, agent_id=None, cash=10000.0, inventory=0.0,
                 window=50, order_size=5):
        """
        Initialize momentum agent
        
        Args:
            agent_id: Unique identifier
            cash: Initial cash balance
            inventory: Initial asset inventory
            window: SMA window size
            order_size: Fixed order quantity
        """
        super().__init__(agent_id, cash, inventory)
        self.window = window
        self.order_size = order_size
        self.price_history = []
        self.sma = None
        self.last_action = None
        self.rng = np.random.default_rng()
        
    def get_action(self, snapshot):
        """
        Generate trade action based on SMA crossover
        
        Args:
            snapshot: Market snapshot with mid_price
            
        Returns:
            Order dictionary or None
        """
        if not snapshot or 'mid_price' not in snapshot:
            return None
        
        current_price = snapshot['mid_price']
        self.price_history.append(current_price)
        
        # Need enough data for SMA calculation
        if len(self.price_history) < self.window:
            return None
        
        # Calculate SMA using only historical data (no lookahead)
        if len(self.price_history) == self.window:
            self.sma = np.mean(self.price_history)
        else:
            # Update SMA incrementally
            self.sma = ((self.sma * self.window) - 
                       self.price_history[-self.window-1] + 
                       current_price) / self.window
        
        # Keep only window size + 1 for next calculation
        if len(self.price_history) > self.window + 1:
            self.price_history = self.price_history[-(self.window + 1):]
        
        # Momentum trading logic
        action = None
        if current_price > self.sma * 1.001:  # 0.1% threshold to reduce noise
            # Price above SMA → BUY signal
            side = 'buy'
            price = current_price * 1.001  # Slightly above current price
            order_type = 'limit'
            action = 'buy'
        elif current_price < self.sma * 0.999:  # 0.1% threshold
            # Price below SMA → SELL signal
            side = 'sell'
            price = current_price * 0.999  # Slightly below current price
            order_type = 'limit'
            action = 'sell'
        else:
            return None
        
        # Only act if signal changed
        if action == self.last_action:
            return None
        
        self.last_action = action
        
        # Check if agent has sufficient resources
        if side == 'buy':
            max_affordable = int(self.cash / price)
            quantity = min(self.order_size, max_affordable)
            if quantity == 0:
                return None
        else:  # sell
            quantity = min(self.order_size, int(self.inventory))
            if quantity == 0:
                return None
        
        return {
            'agent_id': self.id,
            'side': side,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'timestamp': snapshot.get('timestamp', 0)
        }