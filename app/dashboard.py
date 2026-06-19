from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from retailpulse.analytics import (  # noqa: E402
    build_country_revenue,
    build_hourly_orders,
    build_monthly_performance,
    build_overview_metrics,
    build_product_performance,
    build_top_customers,
    format_currency,
    format_number,
    generate_actionable_insights,
)
from retailpulse.data import load_dataset  # noqa: E402
from retailpulse.ml import (  # noqa: E402
    build_churn_model,
    build_demand_forecast,
    build_inventory_optimization,
    build_kmeans_segments,
    summarize_kmeans_segments,
)
from retailpulse.visuals import (  # noqa: E402
    PALETTE,
    churn_risk_chart,
    country_revenue_chart,
    demand_forecast_chart,
    hourly_orders_chart,
    inventory_abc_chart,
    monthly_revenue_chart,
    product_revenue_chart,
    segment_chart,
    top_customers_chart,
)


st.set_page_config(page_title="RetailPulse", page_icon="RP", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

            :root {
                --canvas: #f5f7fa;
                --surface: #ffffff;
                --ink: #162033;
                --muted: #667085;
                --line: #dfe4ea;
                --navy: #13233b;
                --navy-soft: #203754;
                --teal: #0f8b7d;
                --teal-soft: #e7f5f2;
                --coral: #d85f57;
                --coral-soft: #fbeceb;
                --amber: #b67818;
                --amber-soft: #fff4db;
            }

            html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
            .stApp, [data-testid="stAppViewContainer"] { background: var(--canvas); }
            [data-testid="stHeader"] { background: transparent; }
            [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
            .block-container { padding: 1.1rem 1.5rem 2.5rem; max-width: 1600px; }

            .rp-rail {
                min-height: 92vh;
                background: var(--navy);
                color: white;
                border-radius: 8px;
                padding: 1.35rem 1.1rem;
            }
            .rp-logo { font-family: "DM Serif Display", serif; font-size: 1.45rem; white-space: nowrap; }
            .rp-logo span { color: #43c0b0; }
            .rp-rail-copy { color: #aebbd0; font-size: .84rem; line-height: 1.5; margin: .35rem 0 1.4rem; }
            .rp-nav-label { color: #8292aa; font-size: .68rem; font-weight: 700; text-transform: uppercase; margin: 1rem 0 .45rem; }
            .rp-nav-item { padding: .66rem .72rem; border-radius: 6px; color: #d8e0eb; font-size: .88rem; margin-bottom: .3rem; }
            .rp-nav-item.active { background: var(--navy-soft); color: white; border-left: 3px solid #43c0b0; }
            .rp-status { margin-top: 1.2rem; border-top: 1px solid #2b405e; padding-top: 1rem; color: #aebbd0; font-size: .77rem; line-height: 1.7; }
            .rp-status-dot { color: #43c0b0; }

            .rp-command {
                display: flex; justify-content: space-between; align-items: center;
                background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
                padding: .8rem 1rem; margin-bottom: 1rem;
            }
            .rp-command-title { font-size: .86rem; font-weight: 600; color: var(--ink); }
            .rp-command-meta { font-size: .76rem; color: var(--muted); }
            .rp-page-title { font-family: "DM Serif Display", serif; color: var(--ink); font-size: 2rem; margin: .2rem 0; }
            .rp-page-copy { color: var(--muted); font-size: .9rem; margin-bottom: 1rem; }

            .rp-kpi {
                background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
                padding: .9rem 1rem; min-height: 112px;
            }
            .rp-kpi-label { color: var(--muted); font-size: .7rem; font-weight: 700; text-transform: uppercase; }
            .rp-kpi-value { color: var(--ink); font-size: 1.55rem; font-weight: 700; margin: .5rem 0 .2rem; }
            .rp-kpi-note { color: var(--muted); font-size: .75rem; line-height: 1.35; }

            .rp-panel {
                background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
                padding: 1rem; margin-bottom: .9rem;
            }
            .rp-panel-title { color: var(--ink); font-weight: 700; font-size: .9rem; margin-bottom: .25rem; }
            .rp-panel-copy { color: var(--muted); font-size: .78rem; line-height: 1.5; }
            .rp-list { margin: .65rem 0 0; padding-left: 1.05rem; color: var(--muted); font-size: .79rem; line-height: 1.55; }

            .rp-health-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: .55rem; margin-top: .7rem; }
            .rp-health-item { border: 1px solid var(--line); border-radius: 6px; padding: .65rem; }
            .rp-health-label { color: var(--muted); font-size: .67rem; text-transform: uppercase; font-weight: 700; }
            .rp-health-value { color: var(--ink); font-size: 1rem; font-weight: 700; margin-top: .25rem; }
            .rp-good { color: var(--teal); }
            .rp-risk { color: var(--coral); }
            .rp-warn { color: var(--amber); }

            div[data-testid="stPlotlyChart"], .stDataFrame {
                background: var(--surface); border: 1px solid var(--line);
                border-radius: 8px; overflow: hidden;
            }
            button[data-baseweb="tab"] { font-size: .78rem; font-weight: 600; padding-left: .7rem; padding-right: .7rem; }
            .stDownloadButton button, .stButton button {
                border-radius: 6px; border-color: #cbd3dd; color: var(--navy); font-weight: 600;
            }
            [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: .75rem; }

            @media (max-width: 900px) {
                .block-container { padding: .7rem; }
                [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
                [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
                .rp-rail { min-height: auto; }
                .rp-command { display: block; }
                .rp-command-meta { margin-top: .3rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    return load_dataset()


@st.cache_data(show_spinner=False)
def get_advanced_outputs(df: pd.DataFrame) -> dict[str, object]:
    forecast = build_demand_forecast(df)
    segments = build_kmeans_segments(df)
    churn = build_churn_model(df)
    inventory = build_inventory_optimization(df)
    return {
        "forecast": forecast,
        "segments": segments,
        "segment_summary": summarize_kmeans_segments(segments),
        "churn": churn,
        "inventory": inventory,
    }


def kpi(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="rp-kpi"><div class="rp-kpi-label">{label}</div>'
        f'<div class="rp-kpi-value">{value}</div><div class="rp-kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def filter_data(df: pd.DataFrame, rail) -> pd.DataFrame:
    min_date = df["InvoiceDate"].min().date()
    max_date = df["InvoiceDate"].max().date()
    countries = sorted(df["Country"].unique())

    with rail:
        st.markdown(
            """
            <div class="rp-rail">
              <div class="rp-logo">Retail<span>Pulse</span></div>
              <div class="rp-rail-copy">AI retail operations intelligence</div>
              <div class="rp-nav-label">Workspace</div>
              <div class="rp-nav-item active">Executive Overview</div>
              <div class="rp-nav-item">Demand Forecast</div>
              <div class="rp-nav-item">Customer Intelligence</div>
              <div class="rp-nav-item">Churn Risk</div>
              <div class="rp-nav-item">Inventory Control</div>
              <div class="rp-nav-label">Filters</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        all_markets = st.checkbox("All markets", value=True)
        selected = countries if all_markets else st.multiselect("Markets", countries, default=countries[:5])
        selected_dates = st.date_input("Analysis window", (min_date, max_date), min_value=min_date, max_value=max_date)
        st.markdown(
            """
            <div class="rp-status">
              <span class="rp-status-dot">●</span> Dataset ready<br>
              <span class="rp-status-dot">●</span> Models validated<br>
              <span class="rp-status-dot">●</span> Exports available
            </div>
            """,
            unsafe_allow_html=True,
        )

    start, end = selected_dates if len(selected_dates) == 2 else (selected_dates[0], selected_dates[0])
    return df[df["Country"].isin(selected) & df["InvoiceDate"].dt.date.between(start, end)].copy()


def daily_history(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.set_index("InvoiceDate")
        .resample("D")["Revenue"]
        .sum()
        .rename("y")
        .reset_index()
        .rename(columns={"InvoiceDate": "ds"})
    )


def data_quality_panel(df: pd.DataFrame) -> None:
    duplicate_rows = int(df.duplicated().sum())
    missing_cells = int(df.isna().sum().sum())
    coverage_days = int((df["InvoiceDate"].max() - df["InvoiceDate"].min()).days + 1)
    st.markdown(
        f"""
        <div class="rp-panel">
          <div class="rp-panel-title">Data Quality</div>
          <div class="rp-panel-copy">Automated checks on the active analysis window.</div>
          <div class="rp-health-grid">
            <div class="rp-health-item"><div class="rp-health-label">Rows</div><div class="rp-health-value">{len(df):,}</div></div>
            <div class="rp-health-item"><div class="rp-health-label">Coverage</div><div class="rp-health-value">{coverage_days} days</div></div>
            <div class="rp-health-item"><div class="rp-health-label">Missing cells</div><div class="rp-health-value rp-good">{missing_cells:,}</div></div>
            <div class="rp-health-item"><div class="rp-health-label">Duplicate rows</div><div class="rp-health-value {'rp-good' if duplicate_rows == 0 else 'rp-warn'}">{duplicate_rows:,}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def model_health_panel(forecast, churn) -> None:
    auc = churn.auc
    ap = churn.average_precision
    st.markdown(
        f"""
        <div class="rp-panel">
          <div class="rp-panel-title">Model Health</div>
          <div class="rp-panel-copy">Holdout validation, with leakage-safe churn features.</div>
          <div class="rp-health-grid">
            <div class="rp-health-item"><div class="rp-health-label">Forecast MAPE</div><div class="rp-health-value {'rp-good' if forecast.mape < .2 else 'rp-warn'}">{forecast.mape:.1%}</div></div>
            <div class="rp-health-item"><div class="rp-health-label">Churn AUC</div><div class="rp-health-value rp-good">{auc:.3f}</div></div>
            <div class="rp-health-item"><div class="rp-health-label">Avg Precision</div><div class="rp-health-value rp-good">{ap:.3f}</div></div>
            <div class="rp-health-item"><div class="rp-health-label">Validation</div><div class="rp-health-value">Time based</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def csv_download(label: str, data: pd.DataFrame, filename: str) -> None:
    st.download_button(label, data.to_csv(index=False).encode("utf-8"), filename, "text/csv", width="stretch")


def main() -> None:
    inject_styles()
    df = get_data()
    rail, content = st.columns((0.62, 3.38), gap="large")
    filtered = filter_data(df, rail)

    with content:
        st.markdown(
            '<div class="rp-command"><div class="rp-command-title">Retail intelligence workspace</div>'
            '<div class="rp-command-meta">Last transaction: 09 Dec 2011 · Currency: GBP · Data source: UCI Online Retail</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="rp-page-title">Executive Overview</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="rp-page-copy">Monitor commercial performance, customer risk, forecast confidence, and replenishment priorities.</div>',
            unsafe_allow_html=True,
        )

        if filtered.empty:
            st.warning("No transactions match the selected filters.")
            return

        metrics = build_overview_metrics(filtered)
        advanced = get_advanced_outputs(filtered)
        forecast = advanced["forecast"]
        churn = advanced["churn"]
        inventory = advanced["inventory"]
        segment_summary = advanced["segment_summary"]

        high_risk = int((churn.customers["RiskBand"] == "High").sum())
        recommended = int((inventory["ABCClass"] == "A").sum())
        metric_cols = st.columns(6)
        with metric_cols[0]:
            kpi("Revenue", format_currency(metrics["total_revenue"]), "Cleaned net sales")
        with metric_cols[1]:
            kpi("Orders", format_number(metrics["total_orders"]), "Distinct invoices")
        with metric_cols[2]:
            kpi("Customers", format_number(metrics["total_customers"]), "Identified buyers")
        with metric_cols[3]:
            kpi("Average order", format_currency(metrics["average_order_value"]), "Revenue per order")
        with metric_cols[4]:
            kpi("High risk", format_number(high_risk), "Retention queue")
        with metric_cols[5]:
            kpi("Class A SKUs", format_number(recommended), "Priority inventory")

        tabs = st.tabs(
            ["Overview", "Demand Forecast", "Customer Intelligence", "Churn Risk", "Inventory Control", "Export Center"]
        )

        with tabs[0]:
            left, right = st.columns((2.1, 1))
            monthly = build_monthly_performance(filtered)
            countries = build_country_revenue(filtered)
            with left:
                st.plotly_chart(monthly_revenue_chart(monthly), width="stretch")
                chart_cols = st.columns(2)
                with chart_cols[0]:
                    st.plotly_chart(product_revenue_chart(build_product_performance(filtered)), width="stretch")
                with chart_cols[1]:
                    st.plotly_chart(top_customers_chart(build_top_customers(filtered)), width="stretch")
            with right:
                st.plotly_chart(country_revenue_chart(countries), width="stretch")
                data_quality_panel(filtered)
                model_health_panel(forecast, churn)

            insights = generate_actionable_insights(filtered)
            st.markdown(
                '<div class="rp-panel"><div class="rp-panel-title">Decision Brief</div><ul class="rp-list">'
                + "".join(f"<li>{item}</li>" for item in insights)
                + "</ul></div>",
                unsafe_allow_html=True,
            )

        with tabs[1]:
            st.plotly_chart(demand_forecast_chart(daily_history(filtered), forecast.forecast), width="stretch")
            m1, m2, m3 = st.columns(3)
            m1.metric("Forecast method", forecast.method)
            m2.metric("Holdout MAPE", f"{forecast.mape:.1%}")
            m3.metric("90-day forecast", format_currency(float(forecast.forecast["yhat"].sum())))
            forecast_view = forecast.forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
            st.dataframe(forecast_view.head(30), width="stretch", hide_index=True)

        with tabs[2]:
            a, b = st.columns((1.1, 1.4))
            with a:
                st.plotly_chart(segment_chart(segment_summary.rename(columns={"MLSegment": "Segment"})), width="stretch")
            with b:
                st.dataframe(segment_summary, width="stretch", hide_index=True)
                st.markdown(
                    '<div class="rp-panel"><div class="rp-panel-title">Recommended Plays</div>'
                    '<ul class="rp-list"><li>Protect Champions with priority service and early access.</li>'
                    '<li>Move Loyal customers toward higher frequency with replenishment triggers.</li>'
                    '<li>Use targeted win-back offers for At Risk and Hibernating customers.</li></ul></div>',
                    unsafe_allow_html=True,
                )

        with tabs[3]:
            a, b = st.columns((1, 1.5))
            with a:
                st.plotly_chart(churn_risk_chart(churn.customers), width="stretch")
                model_health_panel(forecast, churn)
            with b:
                queue = churn.customers.head(50)[
                    ["CustomerID", "Frequency", "Monetary", "ChurnRisk", "RiskBand"]
                ].copy()
                st.markdown("#### Retention Action Queue")
                st.dataframe(queue, width="stretch", hide_index=True)
                csv_download("Export retention queue", queue, "retailpulse_retention_queue.csv")

        with tabs[4]:
            st.markdown("#### Inventory scenario assumptions")
            controls = st.columns(3)
            with controls[0]:
                ordering_cost = st.number_input("Ordering cost", min_value=1.0, value=50.0, step=5.0)
            with controls[1]:
                holding_rate = st.slider("Annual holding rate", .05, .60, .25, .05)
            with controls[2]:
                lead_time = st.slider("Lead time (days)", 1, 60, 14)

            scenario = build_inventory_optimization(
                filtered,
                ordering_cost=ordering_cost,
                holding_rate=holding_rate,
                lead_time_days=lead_time,
            )
            a, b = st.columns((1, 1.8))
            with a:
                st.plotly_chart(inventory_abc_chart(scenario), width="stretch")
                st.metric("Priority class A SKUs", f"{(scenario['ABCClass'] == 'A').sum():,}")
                st.metric("Median EOQ", f"{scenario['EOQ'].median():,.0f} units")
            with b:
                recommendations = scenario.head(40)[
                    ["StockCode", "Description", "ABCClass", "EOQ", "ReorderPoint", "SafetyStock", "RecommendedStockLevel"]
                ]
                st.markdown("#### Reorder recommendations")
                st.dataframe(recommendations, width="stretch", hide_index=True)
                csv_download("Export inventory plan", scenario, "retailpulse_inventory_plan.csv")

        with tabs[5]:
            st.markdown("#### Reviewer-ready exports")
            export_cols = st.columns(3)
            with export_cols[0]:
                csv_download("Demand forecast CSV", forecast.forecast, "retailpulse_demand_forecast.csv")
                csv_download("Customer segments CSV", advanced["segments"], "retailpulse_customer_segments.csv")
            with export_cols[1]:
                csv_download("Churn risk CSV", churn.customers, "retailpulse_churn_risk.csv")
                csv_download("Inventory plan CSV", inventory, "retailpulse_inventory_optimization.csv")
            with export_cols[2]:
                csv_download("Monthly performance CSV", build_monthly_performance(filtered), "retailpulse_monthly_performance.csv")
                csv_download("Country performance CSV", build_country_revenue(filtered, limit=37), "retailpulse_country_performance.csv")
            st.markdown(
                '<div class="rp-panel"><div class="rp-panel-title">Submission Assets</div>'
                '<div class="rp-panel-copy">The comprehensive PDF, demo video, feedback video, source repository, '
                'and deployment checklist are prepared outside the dashboard under the project submission folder.</div></div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
