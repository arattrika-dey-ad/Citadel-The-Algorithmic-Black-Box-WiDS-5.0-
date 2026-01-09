# Citadel: The Algorithmic Black Box (WiDS 5.0)

## Project Overview

This repository contains the complete simulation suite for the **WiDS 5.0 (Winter in Data Science)** project: **"Citadel: The Algorithmic Black Box"**.

The project constructs a realistic financial exchange simulator from scratch. It simulates market microstructure, including order book dynamics, matching engines, and autonomous trading agents. The development tracks a progression from stochastic mathematical modelling to a modular, object-oriented software system.

- **Repository Owner:** arattrika-dey-ad
- **Core Language:** Python (Jupyter Notebooks)
- **Performance Optimization:** C++ (Order Book)
- **Architecture:** Event-Driven, Agent-Based Simulation

---

## Repository Structure & Module Breakdown

The codebase is organized chronologically to demonstrate the evolution of the system.

### Week 0: Quantitative Foundations

_Focus: Mathematical modelling of asset pricing and risk._

Before building the exchange, this module establishes the mathematical laws governing simulated stock prices.

- **Stochastic Processes:**
  - `Day_3_GBM_Plots.ipynb`: Implements **Geometric Brownian Motion (GBM)** to model continuous-time price paths.
  - **Risk Analysis:**
  - `Day_5_Monte_Carlo_Simulation.ipynb`: Uses **Monte Carlo methods** to simulate thousands of market scenarios and calculate VaR (Value at Risk).
- **Theory:** `Reflection_ What Does Randomness Tell Us About Risk.pdf`.

### Week 1: System Architecture & Exchange Design

_Focus: Software engineering, concurrency, and UML design._

This week bridges the gap between theory and software architecture. It includes the simulation's "Blueprints."

- **The Blueprint (UML Diagrams):**
  - **Structure:** `CLASS DIAGRAM.png`, `COMPONENT DIAGRAM.png`, `DEPLOYMENT DIAGRAM.png`.
  - **Behavior:** `SEQUENCE DIAGRAM (Order Matching Process).png` and `STATE DIAGRAM (Order Lifecycle).png`.
  - **Concurrency & Threading:** Extensive documentation on how the simulator handles multiple operations simultaneously, including `UML Component Diagram - Thread Communication.png` and `UML State Machine Diagram - Thread Lifecycle.png`.
- **Design Rationale:**
  - `Short Memo_ How My Simulator Mimics a Real Exchange.pdf`.

### Week 2: The Market Simulation Package

_Focus: Implementation of the Agent-Based Simulator (ABM)._

This is the core software deliverable, located in `/Week 2 Final Deliverables/market_simulation`. It is a modular Python package.

#### 1. The Engine (`/engine`)

The heart of the exchange logic.

- **`matching_engine.py`**: The core algorithm that maintains the Limit Order Book (LOB) and matches Buy/Sell orders based on **Price-Time Priority**.
- **`event_loop.py`**: Manages the discrete simulation clock, ensuring agents act in the correct sequence.

#### 2. Autonomous Agents (`/agents`)

The simulation is populated by different types of traders:

- **`market_maker_agent.py`**: Provides liquidity by constantly posting bid and ask limit orders.
- **`momentum_agent.py`**: A trend-following agent that trades based on recent price velocity.
- **`noise_agent.py`**: Simulates retail order flow by placing random trades, adding "noise" to the system.
- **`base_agent.py`**: The abstract base class defining the standard interface for all agents.

#### 3. Analytics & Tape (`/analytics`)

- **`tape.py`**: Functions as the "Ticker Tape," recording every executed trade in real-time.
- **`metrics.py`**: Calculates market quality indicators such as volatility, spread width, and volume.
- **`snapshots.py`**: Captures the state of the Order Book at specific timestamps for replay or debugging.

#### 4. C++ Optimization (`/Day 2`)

- **`orderbook.cpp`**: A C++ implementation of the Order Book data structure. This suggests a hybrid approach where latency-critical components were optimized using C++ for higher performance.

---

## How to Run the Simulator

### Prerequisites

- Python 3.8+
- C++ Compiler (for `orderbook.cpp` integration)
- Required Libraries: `pandas`, `numpy`, `matplotlib`.

### Execution

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/arattrika-dey-ad/Citadel-The-Algorithmic-Black-Box-WiDS-5.0-
    ```
2.  **Navigate to the Final Deliverables:**
    ```bash
    cd "Citadel-The-Algorithmic-Black-Box-WiDS-5.0-/Week 2/Week 2 Final Deliverables"
    ```
3.  **Run the Main Simulation Script:**
    This script initializes the engine, spawns agents, and runs the market loop.

    ```bash
    python market_simulation/run_simulation.py
    ```

4.  **Run Unit Tests:**
    To verify the matching logic is working correctly:
    ```bash
    python -m unittest market_simulation/tests/test_matching_engine.py
    ```

---

## Outputs & Visualization

The simulator automatically generates reports and visual analysis of the market session. You can find these in the `Week 2 Final Deliverables` folder:

- **Financial Reports:** `simulation_report.pdf`.
- **Data Exports:** `market_pipeline_results.json` and `scenario_comparison.csv`.
- **Visualizations:**
  - **Price Action:** `scenario_A_candlestick.png`.
  - **Liquidity:** `scenario_B_spread.png` (Bid-Ask Spread visualization).
  - **Agent Performance:** `scenario_C_portfolios.png` (PnL tracking over time).

---
