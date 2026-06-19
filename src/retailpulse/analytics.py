from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def format_currency(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def format_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def build_overview_metrics(df: pd.DataFrame) -> dict[str, float]:
    order_revenue = df.groupby("InvoiceNo", as_index=False)["Revenue"].sum()
    order_quantity = df.groupby("InvoiceNo", as_index=False)["Quantity"].sum()
    return {
        "total_revenue": float(df["Revenue"].sum()),
        "total_orders": int(df["InvoiceNo"].nunique()),
        "total_customers": int(df["CustomerID"].nunique()),
        "total_products": int(df["StockCode"].nunique()),
        "average_order_value": float(order_revenue["Revenue"].mean()),
        "average_items_per_order": float(order_quantity["Quantity"].mean()),
    }


def build_monthly_performance(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("InvoiceMonth")
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique"),
            Units=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("InvoiceMonth")
    )
    monthly["AOV"] = monthly["Revenue"] / monthly["Orders"]
    monthly["MonthLabel"] = monthly["InvoiceMonth"].dt.strftime("%b %Y")
    return monthly


def build_country_revenue(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    countries = (
        df.groupby("Country", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
        .sort_values("Revenue", ascending=False)
        .head(limit)
    )
    countries["RevenueShare"] = countries["Revenue"] / countries["Revenue"].sum()
    return countries


def build_product_performance(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    products = (
        df.groupby("Description", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Quantity=("Quantity", "sum"))
        .sort_values("Revenue", ascending=False)
        .head(limit)
    )
    return products


def build_top_customers(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    customers = (
        df.groupby("CustomerID", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
        .sort_values("Revenue", ascending=False)
        .head(limit)
    )
    customers["CustomerID"] = customers["CustomerID"].astype(str)
    return customers


def build_weekday_revenue(df: pd.DataFrame) -> pd.DataFrame:
    weekdays = (
        df.groupby("InvoiceWeekday", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
        .set_index("InvoiceWeekday")
        .reindex(WEEKDAY_ORDER)
        .reset_index()
    )
    weekdays = weekdays.dropna(subset=["InvoiceWeekday"])
    return weekdays


def build_hourly_orders(df: pd.DataFrame) -> pd.DataFrame:
    hours = (
        df.groupby("InvoiceHour", as_index=False)
        .agg(Orders=("InvoiceNo", "nunique"), Revenue=("Revenue", "sum"))
        .sort_values("InvoiceHour")
    )
    return hours


def build_customer_segments(df: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    segments = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda values: int((snapshot_date - values.max()).days)),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    )

    segments["R"] = pd.qcut(
        segments["Recency"].rank(method="first"),
        4,
        labels=[4, 3, 2, 1],
    ).astype(int)
    segments["F"] = pd.qcut(
        segments["Frequency"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4],
    ).astype(int)
    segments["M"] = pd.qcut(
        segments["Monetary"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4],
    ).astype(int)
    segments["Score"] = segments[["R", "F", "M"]].sum(axis=1)

    def classify(score: int) -> str:
        if score >= 10:
            return "Champions"
        if score >= 8:
            return "Loyal"
        if score >= 6:
            return "Potential Loyalists"
        if score >= 4:
            return "Needs Attention"
        return "At Risk"

    segments["Segment"] = segments["Score"].apply(classify)
    segments = segments.reset_index()
    return segments


def summarize_segments(segments: pd.DataFrame) -> pd.DataFrame:
    summary = (
        segments.groupby("Segment", as_index=False)
        .agg(Customers=("CustomerID", "count"), Revenue=("Monetary", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    summary["RevenueShare"] = summary["Revenue"] / summary["Revenue"].sum()
    return summary


def build_market_snapshot(df: pd.DataFrame) -> dict[str, object]:
    monthly = build_monthly_performance(df)
    segments = summarize_segments(build_customer_segments(df))
    countries = build_country_revenue(df, limit=3)
    hourly = build_hourly_orders(df)

    peak_month = monthly.loc[monthly["Revenue"].idxmax()]
    midday_orders = hourly[hourly["InvoiceHour"].between(10, 15)]["Orders"].sum()
    total_orders = hourly["Orders"].sum()
    champions = segments.loc[segments["Segment"] == "Champions"].iloc[0]

    return {
        "peak_month": peak_month["MonthLabel"],
        "peak_revenue": float(peak_month["Revenue"]),
        "top_country": str(countries.iloc[0]["Country"]),
        "top_country_share": float(countries.iloc[0]["Revenue"] / df["Revenue"].sum()),
        "midday_order_share": float(midday_orders / total_orders),
        "champion_revenue_share": float(champions["RevenueShare"]),
    }


def generate_actionable_insights(df: pd.DataFrame) -> list[str]:
    snapshot = build_market_snapshot(df)
    top_products = build_product_performance(df, limit=3)["Description"].tolist()
    return [
        (
            f"{snapshot['top_country']} contributes {snapshot['top_country_share']:.0%} of revenue, "
            "so non-UK growth should focus first on the next strongest European markets."
        ),
        (
            f"Revenue peaks in {snapshot['peak_month']} at {format_currency(snapshot['peak_revenue'])}, "
            "which supports earlier campaign planning and inventory loading before Q4."
        ),
        (
            f"About {snapshot['midday_order_share']:.0%} of orders happen between 10 AM and 3 PM, "
            "so merchandising and customer support should be strongest around midday demand."
        ),
        (
            f"Champion customers drive {snapshot['champion_revenue_share']:.0%} of revenue, "
            "making loyalty offers, VIP service, and replenishment nudges high-impact plays."
        ),
        (
            f"Top revenue products include {', '.join(top_products)}, "
            "which makes them good candidates for bundling, homepage placement, and stock protection."
        ),
    ]


def build_summary_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame | dict[str, float]]:
    segments = build_customer_segments(df)
    return {
        "metrics": build_overview_metrics(df),
        "monthly_performance": build_monthly_performance(df),
        "country_revenue": build_country_revenue(df),
        "product_performance": build_product_performance(df),
        "top_customers": build_top_customers(df),
        "weekday_revenue": build_weekday_revenue(df),
        "hourly_orders": build_hourly_orders(df),
        "segment_summary": summarize_segments(segments),
        "segment_detail": segments,
    }

