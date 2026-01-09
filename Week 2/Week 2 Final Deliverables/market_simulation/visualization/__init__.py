"""
Visualization Module
Market data visualization and plotting tools.
"""

from .plotter import MarketPlotter

__all__ = [
    "MarketPlotter"
]

# Visualization constants
DEFAULT_STYLE = 'seaborn'
DEFAULT_FIGSIZE = (12, 8)
DEFAULT_COLORS = {
    'bid': 'green',
    'ask': 'red',
    'mid': 'blue',
    'buy': 'lightgreen',
    'sell': 'lightcoral',
    'spread': 'orange'
}

# Plot type constants
PLOT_TYPES = {
    'MID_PRICE': 'mid_price',
    'SPREAD': 'spread',
    'CANDLESTICK': 'candlestick',
    'VOLUME': 'volume',
    'ORDER_BOOK': 'order_book',
    'PORTFOLIO': 'portfolio',
    'COMPARISON': 'comparison'
}

def create_plotter(style=DEFAULT_STYLE, figsize=DEFAULT_FIGSIZE):
    """
    Create a MarketPlotter instance with default settings.
    
    Args:
        style: Matplotlib style
        figsize: Default figure size
        
    Returns:
        MarketPlotter instance
    """
    return MarketPlotter(style=style)

def generate_all_plots(scenario_results, output_dir='plots'):
    """
    Generate all standard plots for scenario results.
    
    Args:
        scenario_results: Dictionary of scenario results
        output_dir: Output directory for plots
        
    Returns:
        List of generated plot filenames
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    plotter = create_plotter()
    plot_filenames = []
    
    for scenario_name, result in scenario_results.items():
        # Get data
        trades_df = result['trade_tape'].get_dataframe()
        snapshots_df = result['snapshots'].get_dataframe()
        
        # Generate individual plots
        plots = [
            ('mid_price', plotter.create_mid_price_plot(
                snapshots_df, 
                title=f"Scenario {scenario_name} - Mid Price"
            )),
            ('spread', plotter.create_spread_plot(
                snapshots_df,
                title=f"Scenario {scenario_name} - Spread"
            )),
            ('candlestick', plotter.create_candlestick_chart(
                trades_df,
                title=f"Scenario {scenario_name} - Candlestick"
            ))
        ]
        
        # Save plots
        for plot_type, fig in plots:
            filename = os.path.join(output_dir, f"scenario_{scenario_name}_{plot_type}.png")
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            plot_filenames.append(filename)
            plt.close(fig)
    
    # Generate comparison plot if multiple scenarios
    if len(scenario_results) > 1:
        scenario_data = {
            name: {'snapshots': result['snapshots'].get_dataframe()}
            for name, result in scenario_results.items()
        }
        metrics_list = [result['metrics'] for result in scenario_results.values()]
        
        fig = plotter.create_comparison_plot(scenario_data, metrics_list)
        filename = os.path.join(output_dir, "scenario_comparison.png")
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plot_filenames.append(filename)
        plt.close(fig)
    
    return plot_filenames

def create_dashboard_plot(scenario_results, figsize=(16, 12)):
    """
    Create a comprehensive dashboard plot.
    
    Args:
        scenario_results: Dictionary of scenario results
        figsize: Figure size
        
    Returns:
        matplotlib Figure
    """
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    
    num_scenarios = len(scenario_results)
    fig = plt.figure(figsize=figsize)
    
    # Create grid layout
    gs = GridSpec(num_scenarios + 1, 3, figure=fig, hspace=0.4, wspace=0.3)
    
    # Add scenario plots
    for i, (scenario_name, result) in enumerate(scenario_results.items()):
        snapshots_df = result['snapshots'].get_dataframe()
        
        # Mid price plot
        ax1 = fig.add_subplot(gs[i, 0])
        if not snapshots_df.empty:
            ax1.plot(snapshots_df['timestamp'], snapshots_df['mid_price'])
        ax1.set_title(f'Scenario {scenario_name} - Mid Price')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Price')
        ax1.grid(True, alpha=0.3)
        
        # Spread plot
        ax2 = fig.add_subplot(gs[i, 1])
        if not snapshots_df.empty:
            finite_spreads = snapshots_df[snapshots_df['spread'] != float('inf')]
            if not finite_spreads.empty:
                ax2.plot(finite_spreads['timestamp'], finite_spreads['spread'], color='red')
        ax2.set_title(f'Scenario {scenario_name} - Spread')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Spread')
        ax2.grid(True, alpha=0.3)
        
        # Volume plot (if trades available)
        ax3 = fig.add_subplot(gs[i, 2])
        trades_df = result['trade_tape'].get_dataframe()
        if not trades_df.empty:
            # Resample to 1-minute volume
            trades_df.set_index('timestamp', inplace=True)
            volume = trades_df['quantity'].resample('1min').sum()
            ax3.bar(volume.index, volume.values, alpha=0.7)
        ax3.set_title(f'Scenario {scenario_name} - Volume')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Volume')
        ax3.grid(True, alpha=0.3)
    
    # Add summary metrics table at the bottom
    ax_table = fig.add_subplot(gs[-1, :])
    ax_table.axis('tight')
    ax_table.axis('off')
    
    # Create table data
    table_data = [['Metric'] + list(scenario_results.keys())]
    metrics_to_show = ['vwap', 'avg_spread', 'volatility', 'total_volume']
    
    for metric in metrics_to_show:
        row = [metric.replace('_', ' ').title()]
        for scenario_name in scenario_results.keys():
            value = scenario_results[scenario_name]['metrics'].get(metric, 'N/A')
            if isinstance(value, float):
                if metric == 'volatility':
                    row.append(f'{value:.4f}')
                elif metric == 'avg_spread':
                    row.append(f'{value:.4f}')
                else:
                    row.append(f'{value:.2f}')
            else:
                row.append(str(value))
        table_data.append(row)
    
    # Create table
    table = ax_table.table(
        cellText=table_data,
        colWidths=[0.2] * (len(scenario_results) + 1),
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    plt.suptitle('Market Simulation Dashboard', fontsize=16, y=0.95)
    
    return fig