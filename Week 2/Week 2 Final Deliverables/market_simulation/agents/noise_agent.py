"""
Noise Trader Agent - Random trading without regard to market conditions
"""
import numpy as np
from .base_agent import BaseAgent

class NoiseTrader(BaseAgent):
    """Agent that trades randomly, ignoring market conditions"""
    
    def __init__(self, agent_id=None, cash=10000.0, inventory=0.0, 
                 order_intensity=0.1, max_order_size=10):
        """
        Initialize noise trader
        
        Args:
            agent_id: Unique identifier
            cash: Initial cash balance
            inventory: Initial asset inventory
            order_intensity: Probability of trading each step
            max_order_size: Maximum order quantity
        """
        super().__init__(agent_id, cash, inventory)
        self.order_intensity = order_intensity
        self.max_order_size = max_order_size
        self.rng = np.random.default_rng()
        
    def get_action(self, snapshot):
        """
        Generate random trade action ignoring L1/L2 data
        
        Args:
            snapshot: Market snapshot (ignored)
            
        Returns:
            Order dictionary or None
        """
        # Randomly decide whether to trade
        if self.rng.random() > self.order_intensity:
            return None
        
        # Random buy/sell (50/50)
        side = 'buy' if self.rng.random() > 0.5 else 'sell'
        
        # Random quantity from uniform distribution
        quantity = self.rng.integers(1, self.max_order_size + 1)
        
        # Random price near current mid if available, else around 100
        if snapshot and 'mid_price' in snapshot and snapshot['mid_price'] > 0:
            mid_price = snapshot['mid_price']
            # Add small random spread
            price_offset = self.rng.uniform(-0.5, 0.5)
            price = max(0.01, mid_price + price_offset)
        else:
            price = self.rng.uniform(99.5, 100.5)
        
        # Random order type (80% limit near touch, 20% market)
        if self.rng.random() > 0.2:
            order_type = 'limit'
        else:
            order_type = 'market'
            price = None  # Market orders have no price
            
        # Ensure agent has enough cash/inventory
        if side == 'buy' and order_type == 'market':
            # For market buys, check we have enough cash at worst price
            worst_price = snapshot.get('ask', 200) if snapshot else 200
            if self.cash < worst_price * quantity:
                quantity = int(self.cash / worst_price)
                if quantity == 0:
                    return None
        elif side == 'sell' and order_type == 'market':
            if self.inventory < quantity:
                quantity = int(self.inventory)
                if quantity == 0:
                    return None
        
        return {
            'agent_id': self.id,
            'side': side,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'timestamp': snapshot.get('timestamp', 0) if snapshot else 0
        }