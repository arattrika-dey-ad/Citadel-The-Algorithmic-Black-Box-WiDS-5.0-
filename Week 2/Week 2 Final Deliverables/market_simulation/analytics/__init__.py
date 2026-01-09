"""
Analytics Module
Data collection and analysis components.
"""

from .tape import TradeTape
from .snapshots import MarketSnapshots
from .metrics import MarketMetrics

__all__ = [
    "TradeTape",
    "MarketSnapshots",
    "MarketMetrics"
]

# Analytics constants
DEFAULT_SNAPSHOT_INTERVAL = 1.0  # 1 second
DEFAULT_CANDLESTICK_INTERVAL = '1min'  # 1 minute
DEFAULT_VOLATILITY_WINDOW = 20  # 20 periods for volatility calculation

def create_analytics_pipeline(snapshot_interval=DEFAULT_SNAPSHOT_INTERVAL):
    """
    Create a complete analytics pipeline.
    
    Args:
        snapshot_interval: Interval between snapshots in seconds
        
    Returns:
        tuple: (trade_tape, snapshots, metrics)
    """
    trade_tape = TradeTape()
    snapshots = MarketSnapshots(interval=snapshot_interval)
    metrics = MarketMetrics(trade_tape, snapshots)
    
    return trade_tape, snapshots, metrics

def calculate_summary_statistics(trade_tape, snapshots):
    """
    Calculate comprehensive summary statistics.
    
    Args:
        trade_tape: TradeTape instance
        snapshots: MarketSnapshots instance
        
    Returns:
        Dictionary with summary statistics
    """
    metrics = MarketMetrics(trade_tape, snapshots)
    all_metrics = metrics.calculate_all_metrics()
    
    # Additional statistics
    trades_df = trade_tape.get_dataframe()
    snapshots_df = snapshots.get_dataframe()
    
    stats = {
        'basic': all_metrics,
        'trades': {},
        'order_book': {}
    }
    
    # Trade statistics
    if not trades_df.empty:
        stats['trades'].update({
            'num_trades': len(trades_df),
            'buy_volume': trades_df[trades_df['aggressor_side'] == 'buy']['quantity'].sum(),
            'sell_volume': trades_df[trades_df['aggressor_side'] == 'sell']['quantity'].sum(),
            'avg_trade_size': trades_df['quantity'].mean(),
            'max_trade_size': trades_df['quantity'].max(),
            'min_trade_size': trades_df['quantity'].min()
        })
    
    # Order book statistics
    if not snapshots_df.empty:
        stats['order_book'].update({
            'avg_bid_ask_spread': snapshots_df['spread'][snapshots_df['spread'] != float('inf')].mean(),
            'max_spread': snapshots_df['spread'].max(),
            'min_spread': snapshots_df['spread'].min(),
            'avg_mid_price': snapshots_df['mid_price'].mean(),
            'price_range': snapshots_df['mid_price'].max() - snapshots_df['mid_price'].min()
        })
    
    return stats

def export_to_dataframes(trade_tape, snapshots):
    """
    Export all analytics data to pandas DataFrames.
    
    Args:
        trade_tape: TradeTape instance
        snapshots: MarketSnapshots instance
        
    Returns:
        tuple: (trades_df, snapshots_df)
    """
    return trade_tape.get_dataframe(), snapshots.get_dataframe()

def export_to_csv(trade_tape, snapshots, prefix='market_data'):
    """
    Export analytics data to CSV files.
    
    Args:
        trade_tape: TradeTape instance
        snapshots: MarketSnapshots instance
        prefix: Prefix for output filenames
        
    Returns:
        tuple: (trades_filename, snapshots_filename)
    """
    trades_df, snapshots_df = export_to_dataframes(trade_tape, snapshots)
    
    trades_filename = f"{prefix}_trades.csv"
    snapshots_filename = f"{prefix}_snapshots.csv"
    
    trades_df.to_csv(trades_filename, index=False)
    snapshots_df.to_csv(snapshots_filename, index=False)
    
    return trades_filename, snapshots_filename