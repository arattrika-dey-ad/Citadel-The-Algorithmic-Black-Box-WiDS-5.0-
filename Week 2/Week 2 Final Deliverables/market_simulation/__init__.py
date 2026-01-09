"""
Market Simulation Package
A comprehensive market microstructure simulator with multiple agent types.
"""

__version__ = "1.0.0"
__author__ = "Market Simulation Team"
__license__ = "MIT"

# Export key classes for easy import
from .run_simulation import MarketSimulation, main
from .simulation_report import generate_pdf_report

__all__ = [
    "MarketSimulation",
    "main",
    "generate_pdf_report"
]