# RetailPulse

RetailPulse is a comprehensive retail AI analytics project built on the UCI Online Retail dataset. It includes a reproducible data-preparation pipeline, predictive modeling, inventory optimization, an executive PDF report, reusable analytics code, and a polished Streamlit dashboard for interactive exploration.

The operational console exposes data quality, model validation, retention queues, adjustable inventory scenarios, and reviewer-ready exports. Predictive metrics use unseen holdouts, and the churn model excludes label-defining recency fields.

## What is included

- Data cleaning and feature engineering from the raw Excel file.
- KPI calculation for revenue, orders, customers, products, and order value.
- Trend, geography, product, customer, and demand-timing analysis.
- RFM-style customer segmentation for retention insights.
- K-Means customer segmentation.
- XGBoost churn risk scoring.
- Time-based, leakage-safe churn validation with ROC AUC and average precision.
- 90-day demand forecasting with a Prophet-compatible interface and seasonal fallback.
- ABC analysis and EOQ inventory optimization.
- Live inventory scenarios for ordering cost, holding rate, and supplier lead time.
- Data quality and model health monitoring.
- Download center for forecast, customer, churn, inventory, monthly, and country outputs.
- A report generator that writes summary tables and chart assets.
- A comprehensive final PDF report in `output/pdf/`.
- A Streamlit dashboard in `app/dashboard.py`.

## Project structure

```text
RetailPulse/
|- app/
|  |- dashboard.py
|- assets/
|  |- retailpulse-dashboard-concept.png
|- data/
|  |- raw/
|  |- processed/
|- output/
|  |- figures/
|  |- pdf/
|  |- churn_risk_scores.csv
|  |- demand_forecast.csv
|  |- inventory_optimization.csv
|  |- kmeans_segments.csv
|  |- customer_segments.csv
|  |- monthly_performance.csv
|  |- summary_metrics.csv
|- reports/
|  |- executive_summary.md
|- submission/
|  |- SUBMISSION_CHECKLIST.md
|- video/
|  |- reproducible Remotion compositions
|- src/
|  |- retailpulse/
|- tests/
|  |- test_analytics.py
```

## Setup

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run the report pipeline

```bash
python -m retailpulse.pipeline
```

This refreshes the cleaned dataset if needed, writes report assets to `output/`, and regenerates `reports/executive_summary.md`.

The comprehensive PDF is written to:

```text
output/pdf/RetailPulse_Final_Comprehensive_Report.pdf
```

## Run the dashboard

```bash
streamlit run app/dashboard.py
```

## Run with Docker

```bash
docker build -t retailpulse .
docker run --rm -p 8501:8501 retailpulse
```

## Engineering documentation

- [Architecture](ARCHITECTURE.md)
- [Model card](MODEL_CARD.md)
- [Deployment guide](DEPLOYMENT.md)
- [Submission checklist](submission/SUBMISSION_CHECKLIST.md)

## Main insights from the current dataset

- Revenue totals about `8.91M` across `18,532` orders and `4,338` customers.
- The United Kingdom drives the large majority of revenue, with the Netherlands and EIRE as the next strongest markets.
- Demand accelerates sharply in September through November 2011, with November as the strongest month.
- Order activity is concentrated from `10 AM` to `3 PM`, peaking at `12 PM`.
- High-value customer segments contribute most revenue, making retention and VIP-style targeting a major opportunity.
- Churn scoring identifies high-risk customers for retention outreach.
- ABC and EOQ analysis highlight priority SKUs and recommended reorder quantities.

## Data source

The raw dataset is expected at `data/raw/online_retail.xlsx`.
