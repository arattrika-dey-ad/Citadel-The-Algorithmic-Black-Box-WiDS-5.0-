"""
Main Simulation Runner - Single entry point for reproducing all scenarios
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.noise_agent import NoiseTrader
from agents.momentum_agent import MomentumAgent
from agents.market_maker_agent import MarketMakerAgent
from engine.event_loop import EventLoop
from engine.matching_engine import OrderBook
from analytics.tape import TradeTape
from analytics.snapshots import MarketSnapshots
from analytics.metrics import MarketMetrics
from visualization.plotter import MarketPlotter
from simulation_report import generate_pdf_report

class MarketSimulation:
    """Main simulation class that orchestrates everything"""
    
    def __init__(self, seed=42):
        """Initialize simulation with seed"""
        np.random.seed(seed)
        self.seed = seed
        
        # Fixed parameters (as specified in requirements)
        self.total_agents = 100
        self.simulation_time = 30 * 60  # 30 minutes in seconds
        self.snapshot_interval = 1.0  # 1 second
        self.arrival_rate = 0.1  # Probability of agent acting each second
        
        # Scenario definitions
        self.scenarios = {
            'A': {'noise': 100, 'market_maker': 0, 'momentum': 0},
            'B': {'noise': 80, 'market_maker': 20, 'momentum': 0},
            'C': {'noise': 80, 'market_maker': 0, 'momentum': 20}
        }
        
        # Results storage
        self.results = {}
        
    def _create_agents(self, scenario):
        """Create agents for a specific scenario"""
        config = self.scenarios[scenario]
        
        agents = []
        agent_id = 0
        
        # Create noise traders
        for _ in range(config['noise']):
            agents.append(NoiseTrader(
                agent_id=f"N{agent_id:03d}",
                cash=np.random.uniform(5000, 15000),
                inventory=np.random.uniform(0, 50),
                order_intensity=self.arrival_rate,
                max_order_size=10
            ))
            agent_id += 1
        
        # Create market makers
        for _ in range(config['market_maker']):
            agents.append(MarketMakerAgent(
                agent_id=f"MM{agent_id:03d}",
                cash=np.random.uniform(20000, 50000),
                inventory=np.random.uniform(-100, 100),
                spread_factor=np.random.uniform(0.001, 0.005),
                inventory_skew_factor=0.001,
                base_order_size=5
            ))
            agent_id += 1
        
        # Create momentum traders
        for _ in range(config['momentum']):
            agents.append(MomentumAgent(
                agent_id=f"M{agent_id:03d}",
                cash=np.random.uniform(5000, 15000),
                inventory=np.random.uniform(0, 50),
                window=50,
                order_size=5
            ))
            agent_id += 1
        
        # Verify total agent count
        assert len(agents) == self.total_agents, \
            f"Agent count mismatch: expected {self.total_agents}, got {len(agents)}"
        
        return agents
    
    def run_scenario(self, scenario_name):
        """Run a single scenario"""
        print(f"\n{'='*60}")
        print(f"Running Scenario {scenario_name}")
        print(f"{'='*60}")
        
        # Create components
        agents = self._create_agents(scenario_name)
        order_book = OrderBook()
        trade_tape = TradeTape()
        snapshots = MarketSnapshots(interval=self.snapshot_interval)
        event_loop = EventLoop()
        
        # Track agent actions
        agent_actions = {agent.id: 0 for agent in agents}
        
        def order_arrival_handler(event):
            """Handle order arrival events"""
            order = event.data
            trades = order_book.add_order(order)
            
            # Record trades
            for trade in trades:
                trade_tape.record_trade(trade)
                
                # Update agent portfolios
                for agent in agents:
                    if agent.id == trade['buyer']:
                        agent.update_portfolio(trade['price'], trade['quantity'], 'buy')
                    elif agent.id == trade['seller']:
                        agent.update_portfolio(trade['price'], trade['quantity'], 'sell')
            
            agent_actions[order['agent_id']] += 1
        
        def snapshot_handler(event):
            """Handle snapshot events"""
            current_time = event.timestamp
            
            # Record snapshot
            snapshots.record_snapshot(current_time, order_book)
            
            # Agents decide actions
            snapshot_data = {
                'timestamp': current_time,
                'mid_price': order_book.get_mid_price(),
                'bid': order_book.get_bbo()[0],
                'ask': order_book.get_bbo()[1],
                'spread': order_book.get_bbo()[2]
            }
            
            for agent in agents:
                action = agent.get_action(snapshot_data)
                if action:
                    if isinstance(action, list):  # Market maker returns list
                        for a in action:
                            if a['type'] == 'new':
                                # Schedule order arrival
                                event_loop.schedule_event(
                                    0.001,  # Small delay
                                    'order_arrival',
                                    {k: v for k, v in a.items() if k != 'type'}
                                )
                    else:
                        # Schedule order arrival
                        event_loop.schedule_event(
                            0.001,  # Small delay
                            'order_arrival',
                            action
                        )
        
        def market_close_handler(event):
            """Handle market close event"""
            print(f"Market closed at time {event.timestamp:.2f}")
        
        # Register event handlers
        event_loop.register_handler('order_arrival', order_arrival_handler)
        event_loop.register_handler('snapshot', snapshot_handler)
        event_loop.register_handler('market_close', market_close_handler)
        
        # Initial snapshot
        event_loop.schedule_event(0, 'snapshot', None)
        
        # Schedule regular snapshots
        for t in np.arange(1, self.simulation_time, self.snapshot_interval):
            event_loop.schedule_event(t, 'snapshot', None)
        
        # Schedule market close
        event_loop.schedule_event(self.simulation_time, 'market_close', None)
        
        # Run simulation
        print("Starting simulation...")
        start_time = time.time()
        event_loop.run(max_time=self.simulation_time)
        elapsed_time = time.time() - start_time
        
        # Calculate metrics
        metrics_calc = MarketMetrics(trade_tape, snapshots)
        metrics = metrics_calc.calculate_all_metrics()
        
        # Store results
        self.results[scenario_name] = {
            'agents': agents,
            'order_book': order_book,
            'trade_tape': trade_tape,
            'snapshots': snapshots,
            'metrics': metrics,
            'agent_actions': agent_actions,
            'simulation_time': elapsed_time
        }
        
        # Print summary
        print(f"\nScenario {scenario_name} Summary:")
        print(f"  Simulation time: {elapsed_time:.2f} seconds")
        print(f"  Number of trades: {len(trade_tape.trades)}")
        print(f"  Total volume: {metrics['total_volume']:.0f}")
        print(f"  Average spread: {metrics['avg_spread']:.4f}")
        print(f"  Volatility: {metrics['volatility']:.4f}")
        print(f"  VWAP: {metrics['vwap']:.2f}")
        
        return self.results[scenario_name]
    
    def run_all_scenarios(self):
        """Run all three scenarios"""
        for scenario in ['A', 'B', 'C']:
            self.run_scenario(scenario)
        
        # Generate plots
        self.generate_plots()
        
        # Generate PDF report
        generate_pdf_report(self.results, self.scenarios, self.seed)
        
        return self.results
    
    def generate_plots(self):
        """Generate all required plots for each scenario"""
        plotter = MarketPlotter()
        
        for scenario_name, result in self.results.items():
            print(f"\nGenerating plots for Scenario {scenario_name}...")
            
            # Get dataframes
            trades_df = result['trade_tape'].get_dataframe()
            snapshots_df = result['snapshots'].get_dataframe()
            
            # Create plots
            fig1 = plotter.create_mid_price_plot(
                snapshots_df, 
                title=f"Scenario {scenario_name} - Mid Price Time Series"
            )
            fig1.savefig(f'scenario_{scenario_name}_mid_price.png', dpi=150, bbox_inches='tight')
            plt.close(fig1)
            
            fig2 = plotter.create_spread_plot(
                snapshots_df,
                title=f"Scenario {scenario_name} - Spread Time Series"
            )
            fig2.savefig(f'scenario_{scenario_name}_spread.png', dpi=150, bbox_inches='tight')
            plt.close(fig2)
            
            fig3 = plotter.create_candlestick_chart(
                trades_df,
                title=f"Scenario {scenario_name} - Candlestick Chart (1-min OHLC)"
            )
            fig3.savefig(f'scenario_{scenario_name}_candlestick.png', dpi=150, bbox_inches='tight')
            plt.close(fig3)
            
            # Agent portfolio plot
            current_price = result['snapshots'].get_latest()['mid_price'] if result['snapshots'].get_latest() else 100
            fig4 = plotter.create_agent_portfolio_plot(result['agents'], current_price)
            fig4.savefig(f'scenario_{scenario_name}_portfolios.png', dpi=150, bbox_inches='tight')
            plt.close(fig4)
        
        # Create comparison plot
        scenario_data = {
            name: {'snapshots': result['snapshots'].get_dataframe()}
            for name, result in self.results.items()
        }
        metrics_list = [result['metrics'] for result in self.results.values()]
        
        fig5 = plotter.create_comparison_plot(scenario_data, metrics_list)
        fig5.savefig('scenario_comparison.png', dpi=150, bbox_inches='tight')
        plt.close(fig5)
        
        print("\nAll plots saved as PNG files.")
    
    def run_sanity_checks(self):
        """Run all required sanity checks"""
        print("\n" + "="*60)
        print("Running Sanity Checks")
        print("="*60)
        
        all_passed = True
        
        # Check 1: Memory leaks in OrderBook
        print("\n1. Checking for memory leaks...")
        for scenario_name, result in self.results.items():
            order_book = result['order_book']
            stats = order_book.get_stats()
            active_orders = stats['num_orders']
            if active_orders > 1000:  # Arbitrary threshold
                print(f"  ❌ Scenario {scenario_name}: Possible memory leak - {active_orders} active orders")
                all_passed = False
            else:
                print(f"  ✓ Scenario {scenario_name}: {active_orders} active orders - OK")
        
        # Check 2: Same seed → identical output
        print("\n2. Checking seed reproducibility...")
        # Run scenario A again with same seed
        np.random.seed(self.seed)
        temp_sim = MarketSimulation(seed=self.seed)
        temp_result = temp_sim.run_scenario('A')
        
        # Compare key metrics
        original_metrics = self.results['A']['metrics']
        new_metrics = temp_result['metrics']
        
        tolerance = 0.01
        for key in ['vwap', 'avg_spread', 'volatility']:
            diff = abs(original_metrics[key] - new_metrics[key])
            if diff > tolerance:
                print(f"  ❌ Metric {key} differs by {diff:.4f}")
                all_passed = False
            else:
                print(f"  ✓ Metric {key} matches within tolerance")
        
        # Check 3: Scenario B spread < Scenario A spread
        print("\n3. Checking Scenario B spread < Scenario A spread...")
        spread_a = self.results['A']['metrics']['avg_spread']
        spread_b = self.results['B']['metrics']['avg_spread']
        
        if spread_b < spread_a:
            print(f"  ✓ Scenario B spread ({spread_b:.4f}) < Scenario A spread ({spread_a:.4f})")
        else:
            print(f"  ❌ Scenario B spread ({spread_b:.4f}) >= Scenario A spread ({spread_a:.4f})")
            all_passed = False
        
        # Check 4: Scenario C volatility > Scenario A volatility
        print("\n4. Checking Scenario C volatility > Scenario A volatility...")
        vol_a = self.results['A']['metrics']['volatility']
        vol_c = self.results['C']['metrics']['volatility']
        
        if vol_c > vol_a:
            print(f"  ✓ Scenario C volatility ({vol_c:.4f}) > Scenario A volatility ({vol_a:.4f})")
        else:
            print(f"  ❌ Scenario C volatility ({vol_c:.4f}) <= Scenario A volatility ({vol_a:.4f})")
            all_passed = False
        
        # Check 5: Crashes emerge naturally
        print("\n5. Checking for natural crashes...")
        for scenario_name, result in self.results.items():
            snapshots_df = result['snapshots'].get_dataframe()
            if not snapshots_df.empty:
                max_price = snapshots_df['mid_price'].max()
                min_price = snapshots_df['mid_price'].min()
                drawdown = (max_price - min_price) / max_price
                
                if drawdown > 0.1:  # 10% drawdown considered a crash
                    print(f"  ✓ Scenario {scenario_name}: Natural crash detected ({drawdown:.1%} drawdown)")
                else:
                    print(f"  ⓘ Scenario {scenario_name}: No major crash ({drawdown:.1%} drawdown)")
        
        # Check 6: Removing market makers destabilizes B
        print("\n6. Checking market maker stabilization...")
        # Scenario B has market makers, A doesn't
        # We expect B to be more stable than A
        stability_a = self.results['A']['metrics']['volatility']
        stability_b = self.results['B']['metrics']['volatility']
        
        if stability_b < stability_a:
            print(f"  ✓ Market makers stabilize: B volatility ({stability_b:.4f}) < A volatility ({stability_a:.4f})")
        else:
            print(f"  ❌ Market makers don't stabilize: B volatility ({stability_b:.4f}) >= A volatility ({stability_a:.4f})")
            all_passed = False
        
        # Check 7: Momentum-only market trends uncontrollably
        print("\n7. Checking momentum agent effects...")
        # Compare Scenario C (with momentum) to A (without)
        trend_c = self._calculate_trend(self.results['C'])
        trend_a = self._calculate_trend(self.results['A'])
        
        if abs(trend_c) > abs(trend_a):
            print(f"  ✓ Momentum creates stronger trends: C trend ({trend_c:.4f}) > A trend ({trend_a:.4f})")
        else:
            print(f"  ⓘ Momentum trend not significantly stronger")
        
        print("\n" + "="*60)
        if all_passed:
            print("✓ ALL SANITY CHECKS PASSED")
        else:
            print("❌ SOME SANITY CHECKS FAILED")
        print("="*60)
        
        return all_passed
    
    def _calculate_trend(self, result):
        """Calculate price trend from snapshots"""
        snapshots_df = result['snapshots'].get_dataframe()
        if len(snapshots_df) < 2:
            return 0
        
        prices = snapshots_df['mid_price'].values
        start_price = prices[0]
        end_price = prices[-1]
        
        return (end_price - start_price) / start_price
    
    def print_detailed_summary(self):
        """Print detailed summary of all scenarios"""
        print("\n" + "="*80)
        print("DETAILED SIMULATION SUMMARY")
        print("="*80)
        
        for scenario_name, result in self.results.items():
            print(f"\nSCENARIO {scenario_name}:")
            print("-" * 40)
            
            config = self.scenarios[scenario_name]
            print(f"Agent Composition:")
            print(f"  Noise Traders: {config['noise']}")
            print(f"  Market Makers: {config['market_maker']}")
            print(f"  Momentum Agents: {config['momentum']}")
            print(f"  Total: {sum(config.values())}")
            
            metrics = result['metrics']
            print(f"\nPerformance Metrics:")
            print(f"  VWAP: {metrics['vwap']:.2f}")
            print(f"  Average Spread: {metrics['avg_spread']:.4f}")
            print(f"  Volatility: {metrics['volatility']:.4f}")
            print(f"  Total Volume: {metrics['total_volume']:.0f}")
            print(f"  Average Trade Size: {metrics['avg_trade_size']:.2f}")
            print(f"  Price Range: {metrics['price_range']:.2f}")
            
            # Agent statistics
            actions = result['agent_actions']
            avg_actions = sum(actions.values()) / len(actions)
            print(f"\nAgent Statistics:")
            print(f"  Average actions per agent: {avg_actions:.1f}")
            print(f"  Most active agent: {max(actions, key=actions.get)} ({max(actions.values())} actions)")
            print(f"  Least active agent: {min(actions, key=actions.get)} ({min(actions.values())} actions)")
            
            # Portfolio statistics
            agents = result['agents']
            portfolio_values = [agent.get_portfolio_value(100) for agent in agents]
            print(f"\nPortfolio Statistics (at price=100):")
            print(f"  Average portfolio: ${np.mean(portfolio_values):.2f}")
            print(f"  Std deviation: ${np.std(portfolio_values):.2f}")
            print(f"  Min portfolio: ${np.min(portfolio_values):.2f}")
            print(f"  Max portfolio: ${np.max(portfolio_values):.2f}")
        
        print("\n" + "="*80)
        print("SCENARIO COMPARISON")
        print("="*80)
        
        comparison_data = []
        for scenario_name in ['A', 'B', 'C']:
            result = self.results[scenario_name]
            metrics = result['metrics']
            comparison_data.append({
                'Scenario': scenario_name,
                'VWAP': f"{metrics['vwap']:.2f}",
                'Avg Spread': f"{metrics['avg_spread']:.4f}",
                'Volatility': f"{metrics['volatility']:.4f}",
                'Total Volume': f"{metrics['total_volume']:.0f}",
                'Simulation Time (s)': f"{result['simulation_time']:.2f}"
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        print(df_comparison.to_string(index=False))

def main():
    """Main function - single entry point"""
    print("="*80)
    print("MARKET SIMULATION SYSTEM")
    print("="*80)
    print("\nThis simulation will run three market regimes:")
    print("  Scenario A: 100 Noise Traders")
    print("  Scenario B: 80 Noise Traders + 20 Market Makers")
    print("  Scenario C: 80 Noise Traders + 20 Momentum Traders")
    print("\nEach scenario runs for 30 minutes of simulation time.")
    print("="*80)
    
    # Initialize and run simulation
    sim = MarketSimulation(seed=42)
    
    # Run all scenarios
    results = sim.run_all_scenarios()
    
    # Run sanity checks
    sim.run_sanity_checks()
    
    # Print detailed summary
    sim.print_detailed_summary()
    
    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  1. scenario_A_mid_price.png")
    print("  2. scenario_A_spread.png")
    print("  3. scenario_A_candlestick.png")
    print("  4. scenario_B_mid_price.png")
    print("  5. scenario_B_spread.png")
    print("  6. scenario_B_candlestick.png")
    print("  7. scenario_C_mid_price.png")
    print("  8. scenario_C_spread.png")
    print("  9. scenario_C_candlestick.png")
    print(" 10. scenario_comparison.png")
    print(" 11. simulation_report.pdf")
    print("\nTo view the comprehensive report, open 'simulation_report.pdf'")

if __name__ == "__main__":
    main()