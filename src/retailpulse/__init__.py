"""RetailPulse analytics package."""

from .analytics import (
    build_customer_segments,
    build_monthly_performance,
    build_overview_metrics,
    generate_actionable_insights,
)
from .data import ensure_processed_data, load_dataset
from .ml import (
    build_churn_model,
    build_demand_forecast,
    build_inventory_optimization,
    build_kmeans_segments,
)

__all__ = [
    "build_customer_segments",
    "build_monthly_performance",
    "build_overview_metrics",
    "ensure_processed_data",
    "generate_actionable_insights",
    "load_dataset",
    "build_churn_model",
    "build_demand_forecast",
    "build_inventory_optimization",
    "build_kmeans_segments",
]
