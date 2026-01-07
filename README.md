# Citadel: The Algorithmic Black Box (WiDS 5.0)

## Project Overview

This repository serves as the submission and workspace for the **WiDS 5.0** (Winter in Data Science) challenge: "Citadel: The Algorithmic Black Box". The project simulates market mechanics, exploring the intricacies of algorithmic trading systems through mathematical modelling and software architecture.

- **Repository Owner:** arattrika-dey-ad
- **Primary Language:** Jupyter Notebook (100.0%)
- **Topic:** Market Simulation, Algorithmic Trading, System Architecture

---

## Repository Structure & Code Details

The repository is organized chronologically into weekly modules, guiding the user through the development of the algorithmic solution.

### Week 0: Foundations of Risk & Randomness

This folder focuses on the mathematical underpinnings of market movements, specifically exploring stochastic processes.

- **`Day_1.ipynb` & `Day_2.ipynb`**: Initial setup and exploratory coding.
- **`Day_3_GBM_Plots.ipynb`**: Implementation of **Geometric Brownian Motion (GBM)** to model stock price paths.
- **`Day_5_Monte_Carlo_Simulation.ipynb`**: utilization of **Monte Carlo methods** to simulate risk and probability distributions.
- **Reflection:** Includes `Reflection_ What Does Randomness Tell Us About Risk.pdf` detailing the theoretical understanding gained.

### Week 1: Building the Simulator

This directory contains the core development of the trading exchange simulator, including code, theory explanations, and extensive system design documentation.

- **Day 1:**
  - `Day 1.pdf`.
- **Day 2:**
  - **Code:** `Day 2 Code.ipynb`.
  - **Documentation:** `Day 2 Code Explanation and Theory.pdf`.
- **Day 3:**
  - **Code:** `Day 3 Code.ipynb`.
  - **Documentation:** `Day 3 Code Explanation and Theory.pdf`.
- **Day 4:**
  - **Code:** `Day 4 Code.ipynb`.
  - **Documentation:** `Day 4 Code Explanation and Theory.pdf`.
- **Day 5 (System Architecture & Finalization):**
  - **Code:** `Day 5 Code.ipynb`.
  - **Reports:**
    - `Short Memo_ How My Simulator Mimics a Real Exchange.pdf`.
    - `Short Report_ Market Mechanics and Design Choices.pdf`.
  - **Architecture Diagrams:**
    A comprehensive suite of UML and system diagrams is included to visualize the exchange logic:
    - **Structural:** `CLASS DIAGRAM.png`, `COMPONENT DIAGRAM.png`, `DEPLOYMENT DIAGRAM.png`.
    - **Behavioral:** `SEQUENCE DIAGRAM (Order Matching Process).png`, `STATE DIAGRAM (Order Lifecycle).png`, `DATA FLOW DIAGRAM.png`.
    - **Concurrency Models:** Detailed diagrams covering Thread Lifecycles, Thread Communication, and Concurrent Order Processing.

### 🔹 Week 2: Final Submission

- **`Week 2 Final.ipynb`**: The consolidated final notebook containing the polished solution for the challenge.

---

## Getting Started

### Prerequisites

To run the simulations and analysis contained in this repository, you need an environment that supports **Jupyter Notebooks**.

- Python 3.x
- JupyterLab or Anaconda
- Libraries (likely required based on file names): `numpy`, `pandas`, `matplotlib` (for GBM plots).

### Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arattrika-dey-ad/Citadel-The-Algorithmic-Black-Box-WiDS-5.0-
    ```
2.  **Navigate to the relevant week:**
    ```bash
    cd "Citadel-The-Algorithmic-Black-Box-WiDS-5.0-/Week 1/Day 5"
    ```
3.  **Launch Jupyter:**
    ```bash
    jupyter notebook
    ```

---

## Design & Architecture

The project places a strong emphasis on robust system design. Week 1 includes detailed visualisations of:

- **Order Matching Logic:** How buy and sell orders are paired.
- **Concurrency:** How the system handles multiple threads for order processing.
- **Physical Architecture:** The deployment structure of the simulator.
