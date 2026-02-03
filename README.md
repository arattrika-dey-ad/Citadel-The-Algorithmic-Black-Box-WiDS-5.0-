# Citadel: The Algorithmic Black Box (WiDS 5.0)

## 📌 Project Overview

This repository contains the official solution for the **WiDS 5.0 Datathon Challenge: "Citadel: The Algorithmic Black Box"**.

The project is a full-stack financial market simulator designed to model market microstructure, order book dynamics, and algorithmic trading strategies. The development journey tracks the evolution from theoretical stochastic modelling to a high-performance, event-driven exchange simulator implemented in **Python** with **C++** optimizations.

- **Repository Owner:** arattrika-dey-ad
- **Domain:** Quantitative Finance, Market Microstructure, System Architecture
- **Core Technologies:** Python (Simulation Engine), C++ (Order Book Optimization), Jupyter Notebooks (Analysis).

---

## 📂 Repository Structure & Roadmap

The codebase is organized chronologically into weekly modules, representing the phases of the engineering lifecycle.

### 🔹 Week 0: Quantitative Foundations

_Focus: Mathematical modelling of risk, randomness, and asset pricing._

Before implementing the exchange, this module establishes the stochastic laws governing the simulation.

- **Stochastic Processes:**
  - **`Day_3_GBM_Plots.ipynb`**: Implementation of **Geometric Brownian Motion (GBM)** to generate continuous-time random walk price paths for simulated assets.
  - **`Day_5_Monte_Carlo_Simulation.ipynb`**: Utilization of **Monte Carlo methods** to simulate thousands of market scenarios, analyzing probability distributions and Value at Risk (VaR).
- **Theoretical Analysis:**
  - **`Reflection_ What Does Randomness Tell Us About Risk.pdf`**: A theoretical essay deriving insights from the Week 0 simulations.
- **Setup:** Initial environment configuration in `Day_1.ipynb` and `Day_2.ipynb`.

### 🔹 Week 1: System Architecture & Exchange Design

_Focus: Software engineering, concurrency models, and UML blueprints._

This week defines the "Blueprint" of the simulated exchange, bridging the gap between math and software engineering.

- **Architecture Documentation (`/Architecture Diagrams`)**:
  - **Structural Design**: `CLASS DIAGRAM.png`, `COMPONENT DIAGRAM.png`, and `DEPLOYMENT DIAGRAM.png`.
  - **Behavioral Logic**:
    - `SEQUENCE DIAGRAM (Order Matching Process).png`: Visualizes the step-by-step logic of matching a buy order with a sell order.
    - `STATE DIAGRAM (Order Lifecycle).png`: Tracks an order from submission to execution or cancellation.
  - **Concurrency & Threading**:
    - Detailed modelling of thread safety and parallel processing, including `UML Component Diagram - Thread Communication.png` and `UML State Machine Diagram - Thread Lifecycle.png`.
- **Design Rationale**:
  - `Short Memo_ How My Simulator Mimics a Real Exchange.pdf`: Justification of design choices against real-world market mechanics.
- **Code Iterations**: Daily Jupyter notebooks (`Day 2 Code.ipynb` through `Day 5 Code.ipynb`) and accompanying PDF explanations documenting the incremental build of the matching logic.

### 🔹 Week 2: The Market Simulation Package (Core Deliverable)

_Focus: Implementation of the Agent-Based Simulator (ABM) and Analysis._

The core logic is modularized into a Python package located in **`/Week 2 Final Deliverables/market_simulation`**.

#### 1. The Engine (`/engine`)

The central processing unit of the exchange.

- **`matching_engine.py`**: The core algorithm that maintains the Limit Order Book (LOB). It executes orders based on **Price-Time Priority**.
- **`event_loop.py`**: Manages the discrete simulation clock, ensuring agents act in the correct sequence without look-ahead bias.

#### 2. Autonomous Agents (`/agents`)

The simulation is populated by distinct trading algorithms:

- **`market_maker_agent.py`**: Provides liquidity by maintaining a two-sided quote (bid and ask) to capture the spread.
- **`momentum_agent.py`**: A trend-following strategy that executes trades based on recent price velocity.
- **`noise_agent.py`**: Simulates retail/random order flow to create market noise and liquidity consumption.
- **`base_agent.py`**: The abstract base class defining the interface for all trading entities.

#### 3. Analytics & Visualization (`/analytics`, `/visualization`)

- **`tape.py`**: Acts as the "Ticker Tape," recording every trade execution in real-time.
- **`metrics.py`**: Computes post-simulation market quality indicators (volatility, spread width, trade volume).
- **`snapshots.py`**: Captures the state of the Order Book at specific timestamps for debugging and replay.
- **`plotter.py`**: Generates financial charts from the simulation data.

#### 4. C++ Optimization (`/Week 2/Day 2`)

To optimize latency-critical components, parts of the system were implemented in C++.

- **`orderbook.cpp`**: A C++ implementation of the Order Book data structure, demonstrating performance optimization capabilities.

### 🔹 Week 3: Extended Analysis

_Focus: Refinement and extended testing._

- Contains notebooks `Day 1.ipynb` through `Day 11.ipynb`, likely used for extended scenario testing, parameter tuning, and final refinements of the simulation logic.

---

## 🚀 Installation & Usage

### Prerequisites

- **Python 3.8+**
- **C++ Compiler** (GCC/Clang for `orderbook.cpp`)
- **Dependencies**: `numpy`, `pandas`, `matplotlib` (Inferred from visualization files).

### How to Run the Simulator

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/arattrika-dey-ad/Citadel-The-Algorithmic-Black-Box-WiDS-5.0-
    ```
2.  **Navigate to the Final Simulation Package**:
    ```bash
    cd "Citadel-The-Algorithmic-Black-Box-WiDS-5.0-/Week 2/Week 2 Final Deliverables"
    ```
3.  **Execute the Main Simulation**:
    Run the entry point script to launch the simulation scenarios.

    ```bash
    python market_simulation/run_simulation.py
    ```

4.  **Run Unit Tests**:
    Verify the integrity of the matching engine.
    ```bash
    python -m unittest market_simulation/tests/test_matching_engine.py
    ```

---

## Outputs & Scenarios

The simulation generates data for multiple market scenarios (Scenario A, B, C), producing the following artifacts in the `Final Deliverables` folder:

- **Financial Reports**:
  - **`simulation_report.pdf`**: The comprehensive final analysis of the simulation results.
  - **`market_pipeline_results.json`**: Raw data export of the simulation metrics.
  - **`scenario_comparison.csv`**: Comparative data between different agent configurations.

- **Visualizations**:
  - **Price Action**: `scenario_A_candlestick.png`.
  - **Liquidity Analysis**: `scenario_B_spread.png` (Bid-Ask Spread over time).
  - **Agent Performance**: `scenario_C_portfolios.png` (PnL tracking for Market Makers vs Momentum Agents).

---

## 🛠 System Design & Concurrency

The project places a heavy emphasis on realistic system architecture. Refer to the **Week 1/Architecture Diagrams** folder for:

- **Concurrency Models**: How the exchange handles multiple incoming order streams.
- **Data Flow**: How orders move from Agents -> Event Loop -> Matching Engine -> Tape.

---

```

```
