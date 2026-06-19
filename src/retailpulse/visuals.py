from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
import pandas as pd


PALETTE = {
    "background": "#F5F7FA",
    "surface": "#FFFFFF",
    "ink": "#162033",
    "muted": "#667085",
    "line": "#DFE4EA",
    "primary": "#0F8B7D",
    "secondary": "#294766",
    "highlight": "#D85F57",
}


def _base_layout(figure: Figure) -> Figure:
    figure.update_layout(
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["surface"],
        font={"family": "DM Sans, Segoe UI, sans-serif", "color": PALETTE["ink"], "size": 12},
        margin={"l": 24, "r": 24, "t": 52, "b": 24},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        title={"font": {"size": 15}},
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(gridcolor="rgba(102, 112, 133, 0.14)", zeroline=False)
    return figure


def monthly_revenue_chart(monthly: pd.DataFrame) -> Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=monthly["InvoiceMonth"],
            y=monthly["Revenue"],
            mode="lines+markers",
            line={"color": PALETTE["primary"], "width": 4},
            marker={"size": 7, "color": PALETTE["primary"]},
            fill="tozeroy",
            fillcolor="rgba(15, 139, 125, 0.10)",
            name="Revenue",
            hovertemplate="%{x|%b %Y}<br>Revenue: $%{y:,.0f}<extra></extra>",
        )
    )
    figure.update_layout(title="Revenue Trend", height=340)
    return _base_layout(figure)


def country_revenue_chart(countries: pd.DataFrame) -> Figure:
    figure = px.bar(
        countries.sort_values("Revenue"),
        x="Revenue",
        y="Country",
        orientation="h",
        color_discrete_sequence=[PALETTE["secondary"]],
    )
    figure.update_traces(hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>")
    figure.update_layout(title="Top Countries", height=340, showlegend=False)
    return _base_layout(figure)


def product_revenue_chart(products: pd.DataFrame) -> Figure:
    figure = px.bar(
        products.sort_values("Revenue"),
        x="Revenue",
        y="Description",
        orientation="h",
        color_discrete_sequence=[PALETTE["primary"]],
    )
    figure.update_traces(hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>")
    figure.update_layout(title="Best-Selling Products", height=380, showlegend=False)
    return _base_layout(figure)


def top_customers_chart(customers: pd.DataFrame) -> Figure:
    figure = px.bar(
        customers,
        x="CustomerID",
        y="Revenue",
        color_discrete_sequence=[PALETTE["highlight"]],
    )
    figure.update_traces(hovertemplate="Customer %{x}<br>Revenue: $%{y:,.0f}<extra></extra>")
    figure.update_layout(title="Top Customers", height=380, showlegend=False)
    return _base_layout(figure)


def segment_chart(segments: pd.DataFrame) -> Figure:
    figure = px.bar(
        segments.sort_values("Revenue"),
        x="Revenue",
        y="Segment",
        orientation="h",
        color="RevenueShare",
        color_continuous_scale=[
            "#DDEBE8",
            PALETTE["primary"],
            "#075E55",
        ],
    )
    figure.update_traces(hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>")
    figure.update_layout(title="Customer Segment Value", height=300, coloraxis_showscale=False)
    return _base_layout(figure)


def hourly_orders_chart(hours: pd.DataFrame) -> Figure:
    figure = px.bar(
        hours,
        x="InvoiceHour",
        y="Orders",
        color_discrete_sequence=[PALETTE["secondary"]],
    )
    figure.update_traces(hovertemplate="%{x}:00<br>Orders: %{y}<extra></extra>")
    figure.update_layout(title="Demand by Hour", height=300, showlegend=False)
    return _base_layout(figure)


def demand_forecast_chart(history: pd.DataFrame, forecast: pd.DataFrame) -> Figure:
    recent_history = history.tail(90)
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=recent_history["InvoiceMonth"] if "InvoiceMonth" in recent_history else recent_history["ds"],
            y=recent_history["Revenue"] if "Revenue" in recent_history else recent_history["y"],
            mode="lines",
            line={"color": PALETTE["muted"], "width": 2},
            name="History",
            hovertemplate="%{x|%b %d}<br>Revenue: $%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            mode="lines",
            line={"color": PALETTE["primary"], "width": 4},
            name="Forecast",
            hovertemplate="%{x|%b %d}<br>Forecast: $%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=pd.concat([forecast["ds"], forecast["ds"].iloc[::-1]], ignore_index=True),
            y=pd.concat([forecast["yhat_upper"], forecast["yhat_lower"].iloc[::-1]], ignore_index=True),
            fill="toself",
            fillcolor="rgba(15, 139, 125, 0.12)",
            line={"color": "rgba(255,255,255,0)"},
            hoverinfo="skip",
            name="Confidence",
        )
    )
    figure.update_layout(title="90-Day Demand Forecast", height=340)
    return _base_layout(figure)


def churn_risk_chart(customers: pd.DataFrame) -> Figure:
    risk_order = ["Low", "Medium", "High"]
    counts = customers["RiskBand"].value_counts().reindex(risk_order, fill_value=0).reset_index()
    counts.columns = ["RiskBand", "Customers"]
    figure = px.bar(
        counts,
        x="RiskBand",
        y="Customers",
        color="RiskBand",
        color_discrete_map={"Low": PALETTE["primary"], "Medium": "#B67818", "High": PALETTE["highlight"]},
    )
    figure.update_traces(hovertemplate="%{x} risk<br>Customers: %{y:,}<extra></extra>")
    figure.update_layout(title="Churn Risk Assessment", height=300, showlegend=False)
    return _base_layout(figure)


def inventory_abc_chart(inventory: pd.DataFrame) -> Figure:
    summary = (
        inventory.groupby("ABCClass", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Products=("StockCode", "count"))
        .sort_values("ABCClass")
    )
    figure = px.bar(
        summary,
        x="ABCClass",
        y="Revenue",
        color="ABCClass",
        color_discrete_map={"A": PALETTE["highlight"], "B": "#B67818", "C": PALETTE["primary"]},
    )
    figure.update_traces(hovertemplate="Class %{x}<br>Revenue: $%{y:,.0f}<extra></extra>")
    figure.update_layout(title="Inventory Health and ABC Priority", height=300, showlegend=False)
    return _base_layout(figure)
