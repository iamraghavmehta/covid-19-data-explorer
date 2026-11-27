"""
COVID-19 Data Explorer - Core Analysis and Visualization Package.
"""

from .data_loader import load_and_clean_data
from .analysis import CovidAnalyzer
from .charts import (
    create_horizontal_bar_chart,
    create_continent_comparison_chart,
    create_scatter_plot,
    create_correlation_heatmap,
    create_country_benchmark_chart,
    generate_static_assignment_charts,
)

__all__ = [
    "load_and_clean_data",
    "CovidAnalyzer",
    "create_horizontal_bar_chart",
    "create_continent_comparison_chart",
    "create_scatter_plot",
    "create_correlation_heatmap",
    "create_country_benchmark_chart",
    "generate_static_assignment_charts",
]
