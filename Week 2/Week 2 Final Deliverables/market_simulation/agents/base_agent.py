"""
Base Agent Class - Abstract class defining the interface for all agents
"""
from abc import ABC, abstractmethod
import uuid

class BaseAgent(ABC):
    """Abstract base class for all trading agents"""
    
    def __init__(self, agent_id=None, cash=10000.0, inventory=0.0):
        """
        Initialize agent with unique ID, cash, and inventory
        
        Args:
            agent_id: Unique identifier (generated if None)
            cash: Initial cash balance
            inventory: Initial asset inventory
        """
        self.id = agent_id if agent_id else str(uuid.uuid4())[:8]
        self.cash = cash
        self.inventory = inventory
        self.trades = []
        self.total_volume = 0
        
    @abstractmethod
    def get_action(self, snapshot):
        """
        Abstract method to determine agent's action based on market snapshot
        
        Args:
            snapshot: Current market state dictionary
            
        Returns:
            Dictionary with order details or None for no action
        """
        pass
    
    def update_portfolio(self, price, quantity, side):
        """
        Update agent's cash and inventory after a trade
        
        Args:
            price: Trade price
            quantity: Trade quantity
            side: 'buy' or 'sell'
        """
        if side == 'buy':
            cost = price * quantity
            if self.cash >= cost:
                self.cash -= cost
                self.inventory += quantity
                self.trades.append(('buy', price, quantity))
                self.total_volume += quantity
                return True
            return False
        elif side == 'sell':
            if self.inventory >= quantity:
                self.cash += price * quantity
                self.inventory -= quantity
                self.trades.append(('sell', price, quantity))
                self.total_volume += quantity
                return True
            return False
        return False
    
    def get_portfolio_value(self, current_price):
        """Calculate total portfolio value"""
        return self.cash + (self.inventory * current_price)