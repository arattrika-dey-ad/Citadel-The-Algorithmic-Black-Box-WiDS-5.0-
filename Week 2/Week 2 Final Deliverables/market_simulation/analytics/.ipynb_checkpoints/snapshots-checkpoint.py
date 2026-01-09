"""
Market Snapshots - Records periodic market state
"""
import pandas as pd
import numpy as np

class MarketSnapshots:
    """Records periodic market state snapshots"""
    
    def __init__(self, interval: float = 1.0):
        """
        Initialize snapshot recorder
        
        Args:
            interval: Snapshot interval in seconds
        """
        self.interval = interval
        self.snapshots = []
        self.columns = [
            'timestamp', 'best_bid', 'best_ask', 'spread',
            'mid_price', 'bid_volume', 'ask_volume',
            'num_bid_levels', 'num_ask_levels'
        ]
        self.last_snapshot_time = -float('inf')
        
    def should_record(self, current_time: float) -> bool:
        """Check if it's time to record a snapshot"""
        return current_time - self.last_snapshot_time >= self.interval
    
    def record_snapshot(self, current_time: float, order_book):
        """
        Record market snapshot
        
        Args:
            current_time: Current simulation time
            order_book: OrderBook instance
        """
        if not self.should_record(current_time):
            return False
        
        best_bid, best_ask, spread = order_book.get_bbo()
        mid_price = order_book.get_mid_price()
        
        # Get order book depth
        bids, asks = order_book.get_order_book_depth(levels=1)
        bid_volume = bids[0][1] if bids else 0
        ask_volume = asks[0][1] if asks else 0
        
        stats = order_book.get_stats()
        
        snapshot = {
            'timestamp': current_time,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': spread,
            'mid_price': mid_price,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'num_bid_levels': stats['num_bid_levels'],
            'num_ask_levels': stats['num_ask_levels']
        }
        
        # Assertions for sanity checks
        assert snapshot['best_bid'] >= 0, f"Best bid negative: {snapshot}"
        assert snapshot['best_ask'] >= 0, f"Best ask negative: {snapshot}"
        assert snapshot['spread'] >= 0 or snapshot['spread'] == float('inf'), f"Spread negative: {snapshot}"
        assert snapshot['mid_price'] >= 0, f"Mid price negative: {snapshot}"
        assert snapshot['bid_volume'] >= 0, f"Bid volume negative: {snapshot}"
        assert snapshot['ask_volume'] >= 0, f"Ask volume negative: {snapshot}"
        
        self.snapshots.append(snapshot)
        self.last_snapshot_time = current_time
        return True
    
    def get_dataframe(self) -> pd.DataFrame:
        """Convert snapshots to pandas DataFrame"""
        if not self.snapshots:
            return pd.DataFrame(columns=self.columns)
        
        df = pd.DataFrame(self.snapshots)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        return df
    
    def get_latest(self) -> dict:
        """Get most recent snapshot"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_snapshot_at(self, timestamp: float) -> dict:
        """Get snapshot closest to timestamp"""
        if not self.snapshots:
            return None
        
        # Find closest snapshot
        closest = min(self.snapshots, key=lambda x: abs(x['timestamp'] - timestamp))
        return closest
    
    def get_spread_stats(self) -> dict:
        """Calculate spread statistics"""
        if not self.snapshots:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        spreads = [s['spread'] for s in self.snapshots if s['spread'] != float('inf')]
        if not spreads:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        return {
            'mean': np.mean(spreads),
            'std': np.std(spreads),
            'min': np.min(spreads),
            'max': np.max(spreads)
        }
    
    def clear(self):
        """Clear all snapshots"""
        self.snapshots.clear()
        self.last_snapshot_time = -float('inf')