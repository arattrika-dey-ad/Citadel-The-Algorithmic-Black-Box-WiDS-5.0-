"""
Agents Module
Contains all trading agent implementations.
"""

from .base_agent import BaseAgent
from .noise_agent import NoiseTrader
from .momentum_agent import MomentumAgent
from .market_maker_agent import MarketMakerAgent

# Define __all__ for explicit exports
__all__ = [
    "BaseAgent",
    "NoiseTrader", 
    "MomentumAgent",
    "MarketMakerAgent"
]

# Agent type constants for easy reference
AGENT_TYPES = {
    "noise": NoiseTrader,
    "momentum": MomentumAgent,
    "market_maker": MarketMakerAgent
}

def create_agent(agent_type, **kwargs):
    """
    Factory function to create agents by type name.
    
    Args:
        agent_type: Type of agent ('noise', 'momentum', 'market_maker')
        **kwargs: Arguments to pass to agent constructor
        
    Returns:
        Agent instance
        
    Raises:
        ValueError: If agent_type is not recognized
    """
    if agent_type not in AGENT_TYPES:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(AGENT_TYPES.keys())}")
    
    return AGENT_TYPES[agent_type](**kwargs)

def get_agent_stats(agents):
    """
    Get statistics for a list of agents.
    
    Args:
        agents: List of BaseAgent instances
        
    Returns:
        Dictionary with agent statistics
    """
    if not agents:
        return {}
    
    stats = {
        'total_agents': len(agents),
        'agent_types': {},
        'total_cash': 0,
        'total_inventory': 0,
        'total_trades': 0,
        'total_volume': 0
    }
    
    for agent in agents:
        agent_type = agent.__class__.__name__
        stats['agent_types'][agent_type] = stats['agent_types'].get(agent_type, 0) + 1
        stats['total_cash'] += agent.cash
        stats['total_inventory'] += agent.inventory
        stats['total_trades'] += len(agent.trades)
        stats['total_volume'] += agent.total_volume
    
    # Calculate averages
    stats['avg_cash'] = stats['total_cash'] / len(agents)
    stats['avg_inventory'] = stats['total_inventory'] / len(agents)
    stats['avg_trades_per_agent'] = stats['total_trades'] / len(agents)
    
    return stats