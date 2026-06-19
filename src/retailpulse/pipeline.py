from __future__ import annotations

import pandas as pd

from .analytics import build_summary_tables
from .config import OUTPUT_DIR
from .data import load_dataset
from .ml import (
    build_churn_model,
    build_demand_forecast,
    build_inventory_optimization,
    build_kmeans_segments,
    summarize_kmeans_segments,
)
from .pdf_report import build_comprehensive_pdf
from .reporting import save_report_figures, write_executive_summary


def run_pipeline(force_refresh: bool = False) -> dict[str, object]:
    dataset = load_dataset(force_refresh=force_refresh)
    tables = build_summary_tables(dataset)
    forecast_result = build_demand_forecast(dataset)
    kmeans_segments = build_kmeans_segments(dataset)
    kmeans_summary = summarize_kmeans_segments(kmeans_segments)
    churn_result = build_churn_model(dataset)
    inventory = build_inventory_optimization(dataset)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([tables["metrics"]]).to_csv(OUTPUT_DIR / "summary_metrics.csv", index=False)
    tables["monthly_performance"].to_csv(OUTPUT_DIR / "monthly_performance.csv", index=False)
    tables["segment_summary"].to_csv(OUTPUT_DIR / "customer_segments.csv", index=False)
    forecast_result.forecast.to_csv(OUTPUT_DIR / "demand_forecast.csv", index=False)
    kmeans_summary.to_csv(OUTPUT_DIR / "kmeans_segments.csv", index=False)
    kmeans_segments.to_csv(OUTPUT_DIR / "kmeans_customer_detail.csv", index=False)
    churn_result.customers.to_csv(OUTPUT_DIR / "churn_risk_scores.csv", index=False)
    inventory.to_csv(OUTPUT_DIR / "inventory_optimization.csv", index=False)

    figure_paths = save_report_figures(
        dataset,
        forecast_result=forecast_result,
        churn_result=churn_result,
        inventory=inventory,
    )
    dashboard_screenshot = OUTPUT_DIR / "playwright" / "dashboard-enterprise-overview.png"
    if dashboard_screenshot.exists():
        figure_paths.insert(0, dashboard_screenshot)
    report_path = write_executive_summary(dataset)
    pdf_path = build_comprehensive_pdf(
        dataset,
        forecast_result=forecast_result,
        kmeans_summary=kmeans_summary,
        churn_result=churn_result,
        inventory=inventory,
        figure_paths=figure_paths,
    )

    return {
        "dataset_rows": len(dataset),
        "report_path": report_path,
        "pdf_path": pdf_path,
        "figure_paths": figure_paths,
        "forecast_method": forecast_result.method,
        "forecast_mape": forecast_result.mape,
        "churn_model": churn_result.model_name,
        "churn_auc": churn_result.auc,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(f"Processed rows: {result['dataset_rows']}")
    print(f"Report written to: {result['report_path']}")
    print(f"PDF report written to: {result['pdf_path']}")
    print(f"Forecast method: {result['forecast_method']} (MAPE: {result['forecast_mape']:.2%})")
    print(f"Churn model: {result['churn_model']} (AUC: {result['churn_auc']:.2f})")
    for figure in result["figure_paths"]:
        print(f"Figure written to: {figure}")
