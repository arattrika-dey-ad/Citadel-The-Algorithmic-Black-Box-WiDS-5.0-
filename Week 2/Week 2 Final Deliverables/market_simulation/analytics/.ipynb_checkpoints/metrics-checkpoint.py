"""
Market Metrics - Computes various market statistics
"""
import numpy as np
import pandas as pd
from typing import Optional

class MarketMetrics:
    """Computes market metrics from trade tape and snapshots"""
    
    def __init__(self, trade_tape, snapshots):
        """
        Initialize metrics calculator
        
        Args:
            trade_tape: TradeTape instance
            snapshots: MarketSnapshots instance
        """
        self.trade_tape = trade_tape
        self.snapshots = snapshots
        
    def calculate_all_metrics(self) -> dict:
        """Calculate all available metrics"""
        metrics = {}
        
        # VWAP
        metrics['vwap'] = self.calculate_vwap()
        
        # Spread metrics
        spread_stats = self.snapshots.get_spread_stats()
        metrics.update({
            'avg_spread': spread_stats['mean'],
            'spread_std': spread_stats['std'],
            'min_spread': spread_stats['min'],
            'max_spread': spread_stats['max']
        })
        
        # Volatility
        metrics['volatility'] = self.calculate_volatility(window=50)
        
        # Volume metrics
        tape_stats = self.trade_tape.get_stats()
        metrics.update({
            'total_volume': tape_stats['total_volume'],
            'avg_trade_size': tape_stats['total_volume'] / tape_stats['num_trades'] if tape_stats['num_trades'] > 0 else 0,
            'price_range': tape_stats['max_price'] - tape_stats['min_price'] if tape_stats['num_trades'] > 0 else 0
        })
        
        # Order book metrics
        if self.snapshots.snapshots:
            avg_bid_levels = np.mean([s['num_bid_levels'] for s in self.snapshots.snapshots])
            avg_ask_levels = np.mean([s['num_ask_levels'] for s in self.snapshots.snapshots])
            metrics.update({
                'avg_bid_levels': avg_bid_levels,
                'avg_ask_levels': avg_ask_levels,
                'liquidity_ratio': avg_bid_levels / avg_ask_levels if avg_ask_levels > 0 else float('inf')
            })
        
        return metrics
    
    def calculate_vwap(self, start_time: float = None, end_time: float = None) -> float:
        """Calculate Volume Weighted Average Price"""
        return self.trade_tape.get_vwap(start_time, end_time)
    
    def calculate_volatility(self, window: int = 20) -> float:
        """
        Calculate rolling volatility from mid prices
        
        Args:
            window: Rolling window size
            
        Returns:
            Annualized volatility
        """
        df = self.snapshots.get_dataframe()
        if df.empty or len(df) < window:
            return 0
        
        # Use mid prices
        prices = df['mid_price'].values
        
        # Calculate returns
        returns = np.diff(np.log(prices))
        
        if len(returns) < window:
            return np.std(returns) * np.sqrt(252 * 24 * 3600) if len(returns) > 1 else 0  # Annualized
        
        # Calculate rolling volatility
        rolling_vol = pd.Series(returns).rolling(window=window).std().dropna()
        
        if rolling_vol.empty:
            return 0
        
        # Annualize (assuming 1-second intervals, 252 trading days, 24 hours/day)
        annualization_factor = np.sqrt(252 * 24 * 3600)
        return float(rolling_vol.mean() * annualization_factor)
    
    def calculate_volume_profile(self, bins: int = 20) -> dict:
        """
        Calculate volume profile by price level
        
        Args:
            bins: Number of price bins
            
        Returns:
            Dictionary with price bins and volumes
        """
        trades_df = self.trade_tape.get_dataframe()
        if trades_df.empty:
            return {}
        
        min_price = trades_df['price'].min()
        max_price = trades_df['price'].max()
        
        # Create price bins
        bin_edges = np.linspace(min_price, max_price, bins + 1)
        bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(bins)]
        
        # Bin trades by price
        trades_df['price_bin'] = pd.cut(trades_df['price'], bins=bin_edges, labels=bin_labels)
        
        # Calculate volume per bin
        volume_profile = trades_df.groupby('price_bin')['quantity'].sum().to_dict()
        
        return volume_profile
    
    def calculate_efficiency_ratio(self) -> float:
        """
        Calculate market efficiency ratio (price change vs noise)
        
        Returns:
            Efficiency ratio (0-1, higher is more efficient)
        """
        df = self.snapshots.get_dataframe()
        if df.empty or len(df) < 2:
            return 0
        
        prices = df['mid_price'].values
        
        # Total price movement
        net_movement = abs(prices[-1] - prices[0])
        
        # Gross price movement (sum of absolute changes)
        gross_movement = np.sum(np.abs(np.diff(prices)))
        
        if gross_movement == 0:
            return 1
        
        efficiency = net_movement / gross_movement
        return float(efficiency)
    
    def calculate_order_imbalance(self) -> dict:
        """
        Calculate order imbalance metrics
        
        Returns:
            Dictionary with imbalance metrics
        """
        trades_df = self.trade_tape.get_dataframe()
        if trades_df.empty:
            return {'buy_ratio': 0.5, 'imbalance': 0}
        
        # Count buy vs sell initiated trades
        buy_trades = trades_df[trades_df['aggressor_side'] == 'buy']
        sell_trades = trades_df[trades_df['aggressor_side'] == 'sell']
        
        total_buy_volume = buy_trades['quantity'].sum()
        total_sell_volume = sell_trades['quantity'].sum()
        total_volume = total_buy_volume + total_sell_volume
        
        if total_volume == 0:
            return {'buy_ratio': 0.5, 'imbalance': 0}
        
        buy_ratio = total_buy_volume / total_volume
        imbalance = (total_buy_volume - total_sell_volume) / total_volume
        
        return {
            'buy_ratio': buy_ratio,
            'imbalance': imbalance,
            'buy_volume': total_buy_volume,
            'sell_volume': total_sell_volume
        }