from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .analytics import (
    build_country_revenue,
    build_customer_segments,
    build_monthly_performance,
    build_overview_metrics,
    generate_actionable_insights,
    summarize_segments,
)
from .config import OUTPUT_FIGURES_DIR, REPORTS_DIR
from .ml import ChurnResult, ForecastResult


sns.set_theme(style="whitegrid")


def _save_monthly_revenue(monthly: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.5))
    sns.lineplot(data=monthly, x="InvoiceMonth", y="Revenue", marker="o", color="#C96E4A", ax=ax)
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _save_top_countries(countries: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.barplot(data=countries, x="Revenue", y="Country", color="#809671", ax=ax)
    ax.set_title("Top Countries by Revenue")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Country")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _save_segments(segments: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.barplot(data=segments, x="Revenue", y="Segment", color="#E6B96B", ax=ax)
    ax.set_title("Revenue by Customer Segment")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Segment")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _save_forecast(forecast_result: ForecastResult, output_path: Path) -> None:
    forecast = forecast_result.forecast
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(forecast["ds"], forecast["yhat"], color="#C96E4A", linewidth=2.5, label="Forecast")
    ax.fill_between(
        forecast["ds"],
        forecast["yhat_lower"],
        forecast["yhat_upper"],
        color="#C96E4A",
        alpha=0.16,
        label="Confidence interval",
    )
    ax.set_title("90-Day Demand Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Predicted Revenue")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _save_churn(churn_result: ChurnResult, output_path: Path) -> None:
    counts = churn_result.customers["RiskBand"].value_counts().reindex(["Low", "Medium", "High"], fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(x=counts.index, y=counts.values, palette=["#809671", "#E6B96B", "#C96E4A"], ax=ax, hue=counts.index, legend=False)
    ax.set_title("Churn Risk Assessment")
    ax.set_xlabel("Risk Band")
    ax.set_ylabel("Customers")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _save_inventory(inventory: pd.DataFrame, output_path: Path) -> None:
    summary = inventory.groupby("ABCClass", as_index=False).agg(Revenue=("Revenue", "sum"), Products=("StockCode", "count"))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=summary, x="ABCClass", y="Revenue", palette=["#C96E4A", "#E6B96B", "#809671"], ax=ax, hue="ABCClass", legend=False)
    ax.set_title("Inventory Health and ABC Priority")
    ax.set_xlabel("ABC Class")
    ax.set_ylabel("Revenue")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def save_report_figures(
    df: pd.DataFrame,
    output_dir: Path = OUTPUT_FIGURES_DIR,
    forecast_result: ForecastResult | None = None,
    churn_result: ChurnResult | None = None,
    inventory: pd.DataFrame | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    monthly_path = output_dir / "monthly_revenue.png"
    countries_path = output_dir / "top_countries.png"
    segments_path = output_dir / "customer_segments.png"
    forecast_path = output_dir / "demand_forecast.png"
    churn_path = output_dir / "churn_risk.png"
    inventory_path = output_dir / "inventory_abc.png"

    _save_monthly_revenue(build_monthly_performance(df), monthly_path)
    _save_top_countries(build_country_revenue(df), countries_path)
    _save_segments(summarize_segments(build_customer_segments(df)), segments_path)
    paths = [monthly_path, countries_path, segments_path]

    if forecast_result is not None:
        _save_forecast(forecast_result, forecast_path)
        paths.append(forecast_path)
    if churn_result is not None:
        _save_churn(churn_result, churn_path)
        paths.append(churn_path)
    if inventory is not None:
        _save_inventory(inventory, inventory_path)
        paths.append(inventory_path)

    return paths


def build_executive_summary(df: pd.DataFrame) -> str:
    metrics = build_overview_metrics(df)
    monthly = build_monthly_performance(df)
    countries = build_country_revenue(df)
    segment_summary = summarize_segments(build_customer_segments(df))
    insights = generate_actionable_insights(df)

    peak_month = monthly.loc[monthly["Revenue"].idxmax()]
    latest_month = monthly.iloc[-1]
    top_country = countries.iloc[0]
    champion_segment = segment_summary.iloc[0]

    lines = [
        "# RetailPulse Executive Summary",
        "",
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
        "",
        "## Business Snapshot",
        "",
        f"- Total revenue: ${metrics['total_revenue']:,.2f}",
        f"- Orders: {metrics['total_orders']:,}",
        f"- Customers: {metrics['total_customers']:,}",
        f"- Products: {metrics['total_products']:,}",
        f"- Average order value: ${metrics['average_order_value']:,.2f}",
        f"- Average items per order: {metrics['average_items_per_order']:.1f}",
        "",
        "## Key Findings",
        "",
        f"- Peak revenue month: {peak_month['MonthLabel']} with ${peak_month['Revenue']:,.2f}.",
        f"- Latest observed month: {latest_month['MonthLabel']} with ${latest_month['Revenue']:,.2f}.",
        f"- Largest market: {top_country['Country']} with {top_country['RevenueShare']:.1%} share of top-10 market revenue.",
        f"- Highest-value segment: {champion_segment['Segment']} with {champion_segment['RevenueShare']:.1%} revenue share.",
        "",
        "## Recommended Actions",
        "",
    ]
    lines.extend([f"- {insight}" for insight in insights])
    lines.extend(
        [
            "",
            "## Visuals",
            "",
            "![Monthly Revenue](../output/figures/monthly_revenue.png)",
            "",
            "![Top Countries](../output/figures/top_countries.png)",
            "",
            "![Customer Segments](../output/figures/customer_segments.png)",
            "",
        ]
    )
    return "\n".join(lines)


def write_executive_summary(df: pd.DataFrame, output_path: Path | None = None) -> Path:
    target_path = output_path or (REPORTS_DIR / "executive_summary.md")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(build_executive_summary(df), encoding="utf-8")
    return target_path
