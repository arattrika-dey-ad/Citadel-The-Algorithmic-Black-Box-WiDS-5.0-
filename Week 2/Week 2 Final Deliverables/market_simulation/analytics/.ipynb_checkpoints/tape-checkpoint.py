"""
Trade Tape - Records all executed trades
"""
import pandas as pd
from datetime import datetime, timedelta

class TradeTape:
    """Append-only record of all trades"""
    
    def __init__(self):
        """Initialize empty trade tape"""
        self.trades = []
        self.columns = [
            'timestamp', 'price', 'quantity', 'aggressor_side',
            'buyer_id', 'seller_id', 'trade_id'
        ]
        self.trade_count = 0
        
    def record_trade(self, trade_data: dict):
        """
        Record a trade
        
        Args:
            trade_data: Dictionary with trade details
        """
        self.trade_count += 1
        trade_record = {
            'timestamp': trade_data.get('timestamp', 0),
            'price': trade_data['price'],
            'quantity': trade_data['quantity'],
            'aggressor_side': trade_data.get('aggressor', 'unknown'),
            'buyer_id': trade_data['buyer'],
            'seller_id': trade_data['seller'],
            'trade_id': f"trade_{self.trade_count:06d}"
        }
        
        # Add trade to list
        self.trades.append(trade_record)
        
        # Assertions for sanity checks
        assert trade_record['price'] > 0, f"Trade price must be positive: {trade_record}"
        assert trade_record['quantity'] > 0, f"Trade quantity must be positive: {trade_record}"
        
    def get_dataframe(self) -> pd.DataFrame:
        """Convert trade tape to pandas DataFrame"""
        if not self.trades:
            return pd.DataFrame(columns=self.columns)
        
        df = pd.DataFrame(self.trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        return df
    
    def get_recent_trades(self, n: int = 10) -> list:
        """Get n most recent trades"""
        return self.trades[-n:] if self.trades else []
    
    def get_trades_in_interval(self, start_time: float, end_time: float) -> list:
        """Get trades within time interval"""
        return [t for t in self.trades if start_time <= t['timestamp'] <= end_time]
    
    def get_volume(self, start_time: float = None, end_time: float = None) -> float:
        """Calculate total volume in time interval"""
        if start_time is None and end_time is None:
            trades = self.trades
        else:
            trades = self.get_trades_in_interval(start_time or 0, end_time or float('inf'))
        
        return sum(t['quantity'] for t in trades)
    
    def get_vwap(self, start_time: float = None, end_time: float = None) -> float:
        """Calculate Volume Weighted Average Price"""
        trades = self.get_trades_in_interval(start_time or 0, end_time or float('inf'))
        if not trades:
            return 0
        
        total_value = sum(t['price'] * t['quantity'] for t in trades)
        total_volume = sum(t['quantity'] for t in trades)
        
        if total_volume == 0:
            return 0
        
        return total_value / total_volume
    
    def clear(self):
        """Clear all trades (for testing)"""
        self.trades.clear()
        self.trade_count = 0
    
    def get_stats(self) -> dict:
        """Get tape statistics"""
        if not self.trades:
            return {
                'num_trades': 0,
                'total_volume': 0,
                'avg_price': 0,
                'price_std': 0
            }
        
        prices = [t['price'] for t in self.trades]
        volumes = [t['quantity'] for t in self.trades]
        
        total_volume = sum(volumes)
        avg_price = sum(p * v for p, v in zip(prices, volumes)) / total_volume if total_volume > 0 else 0
        price_std = (sum(((p - avg_price) ** 2) * v for p, v in zip(prices, volumes)) / total_volume) ** 0.5 if total_volume > 0 else 0
        
        return {
            'num_trades': len(self.trades),
            'total_volume': total_volume,
            'avg_price': avg_price,
            'price_std': price_std,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0
        }