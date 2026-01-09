"""
Visualization Module - Creates plots for market analysis
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketPlotter:
    """Creates visualizations for market simulation results"""
    
    def __init__(self, style='seaborn'):
        """Initialize plotter with style"""
        available_styles = plt.style.available
        if style not in available_styles:
            style = 'default'  # Use default style
        plt.style.use(style)
        self.figsize = (12, 8)
        
    def create_mid_price_plot(self, snapshots_df, title="Mid Price Time Series"):
        """Create mid price time series plot"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if snapshots_df.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            return fig
        
        ax.plot(snapshots_df['timestamp'], snapshots_df['mid_price'], 
                linewidth=1.5, color='blue', alpha=0.7)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Mid Price')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis for time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        
        return fig
    
    def create_spread_plot(self, snapshots_df, title="Spread Time Series"):
        """Create spread time series plot"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if snapshots_df.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            return fig
        
        # Filter out infinite spreads
        finite_spreads = snapshots_df[snapshots_df['spread'] != float('inf')]
        
        if finite_spreads.empty:
            ax.text(0.5, 0.5, 'No finite spreads available', ha='center', va='center')
            return fig
        
        ax.plot(finite_spreads['timestamp'], finite_spreads['spread'], 
                linewidth=1.5, color='red', alpha=0.7)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Spread')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis for time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        
        return fig
    
    def create_candlestick_chart(self, trades_df, title="Candlestick Chart (1-min OHLC)"):
        """Create 1-minute candlestick chart from trade tape"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if trades_df.empty:
            ax.text(0.5, 0.5, 'No trade data available', ha='center', va='center')
            return fig
        
        # Resample to 1-minute OHLC
        trades_df.set_index('timestamp', inplace=True)
        ohlc = trades_df['price'].resample('1min').ohlc()
        
        if ohlc.empty:
            ax.text(0.5, 0.5, 'Insufficient data for 1-min candles', ha='center', va='center')
            return fig
        
        # Ensure high >= low (fix any anomalies)
        mask = ohlc['high'] < ohlc['low']
        if mask.any():
            ohlc.loc[mask, ['high', 'low']] = ohlc.loc[mask, ['low', 'high']].values
        
        # Calculate width for candlesticks (90% of interval)
        interval_minutes = 1
        width = interval_minutes * 60 * 0.9  # 90% of interval in seconds
        
        # Plot candles
        for idx, row in ohlc.iterrows():
            if pd.isna(row['open']) or pd.isna(row['close']):
                continue
                
            # Determine color
            if row['close'] >= row['open']:
                color = 'green'
                body_bottom = row['open']
                body_top = row['close']
            else:
                color = 'red'
                body_bottom = row['close']
                body_top = row['open']
            
            # Plot wick (high-low line)
            ax.plot([idx, idx], [row['low'], row['high']], 
                   color='black', linewidth=0.5)
            
            # Plot body
            ax.add_patch(plt.Rectangle(
                (idx - timedelta(seconds=width/2), body_bottom),
                timedelta(seconds=width),
                body_top - body_bottom,
                facecolor=color,
                edgecolor='black'
            ))
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        return fig
    
    def create_comparison_plot(self, scenario_data, metrics):
        """Create comparison plot for multiple scenarios"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Average Spread comparison
        spreads = [m['avg_spread'] for m in metrics]
        axes[0, 0].bar(range(len(spreads)), spreads)
        axes[0, 0].set_title('Average Spread by Scenario')
        axes[0, 0].set_xlabel('Scenario')
        axes[0, 0].set_ylabel('Spread')
        axes[0, 0].set_xticks(range(len(spreads)))
        axes[0, 0].set_xticklabels(['A', 'B', 'C'])
        
        # Plot 2: Volatility comparison
        volatilities = [m['volatility'] for m in metrics]
        axes[0, 1].bar(range(len(volatilities)), volatilities, color='orange')
        axes[0, 1].set_title('Volatility by Scenario')
        axes[0, 1].set_xlabel('Scenario')
        axes[0, 1].set_ylabel('Volatility (annualized)')
        axes[0, 1].set_xticks(range(len(volatilities)))
        axes[0, 1].set_xticklabels(['A', 'B', 'C'])
        
        # Plot 3: Mid price time series overlay
        for i, (name, data) in enumerate(scenario_data.items()):
            if not data['snapshots'].empty:
                axes[1, 0].plot(data['snapshots']['timestamp'], 
                               data['snapshots']['mid_price'],
                               label=f'Scenario {name}', alpha=0.7)
        axes[1, 0].set_title('Mid Price Comparison')
        axes[1, 0].set_xlabel('Time')
        axes[1, 0].set_ylabel('Price')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Format time axis
        axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        # Plot 4: Volume comparison
        volumes = [m['total_volume'] for m in metrics]
        axes[1, 1].bar(range(len(volumes)), volumes, color='green')
        axes[1, 1].set_title('Total Volume by Scenario')
        axes[1, 1].set_xlabel('Scenario')
        axes[1, 1].set_ylabel('Volume')
        axes[1, 1].set_xticks(range(len(volumes)))
        axes[1, 1].set_xticklabels(['A', 'B', 'C'])
        
        plt.tight_layout()
        return fig
    
    def create_agent_portfolio_plot(self, agents, current_price):
        """Create portfolio distribution plot for agents"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Calculate portfolio values
        portfolio_values = []
        cash_values = []
        inventory_values = []
        agent_types = []
        
        for agent in agents:
            portfolio_values.append(agent.get_portfolio_value(current_price))
            cash_values.append(agent.cash)
            inventory_values.append(agent.inventory * current_price)
            agent_types.append(agent.__class__.__name__)
        
        # Plot 1: Portfolio value distribution
        axes[0].hist(portfolio_values, bins=20, alpha=0.7, edgecolor='black')
        axes[0].set_title('Portfolio Value Distribution')
        axes[0].set_xlabel('Portfolio Value')
        axes[0].set_ylabel('Frequency')
        axes[0].axvline(np.mean(portfolio_values), color='red', linestyle='--', label=f'Mean: {np.mean(portfolio_values):.2f}')
        axes[0].legend()
        
        # Plot 2: Cash vs Inventory
        scatter = axes[1].scatter(cash_values, inventory_values, 
                                 c=range(len(agents)), cmap='viridis', alpha=0.6)
        axes[1].set_title('Cash vs Inventory Value')
        axes[1].set_xlabel('Cash')
        axes[1].set_ylabel('Inventory Value')
        plt.colorbar(scatter, ax=axes[1], label='Agent Index')
        
        # Plot 3: Portfolio by agent type
        unique_types = list(set(agent_types))
        type_portfolios = []
        for agent_type in unique_types:
            type_values = [pv for pv, at in zip(portfolio_values, agent_types) if at == agent_type]
            type_portfolios.append(np.mean(type_values) if type_values else 0)
        
        axes[2].bar(range(len(unique_types)), type_portfolios)
        axes[2].set_title('Average Portfolio by Agent Type')
        axes[2].set_xlabel('Agent Type')
        axes[2].set_ylabel('Average Portfolio Value')
        axes[2].set_xticks(range(len(unique_types)))
        axes[2].set_xticklabels(unique_types, rotation=45, ha='right')
        
        plt.tight_layout()
        return fig