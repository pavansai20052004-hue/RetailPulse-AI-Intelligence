# RetailPulse Architecture

## System flow

```mermaid
flowchart LR
    A[Online Retail workbook] --> B[Cleaning and validation]
    B --> C[Processed transaction dataset]
    C --> D[Descriptive analytics]
    C --> E[Demand forecasting]
    C --> F[K-Means customer segmentation]
    C --> G[Leakage-safe churn modeling]
    C --> H[ABC and EOQ inventory optimization]
    D --> I[Streamlit operations console]
    E --> I
    F --> I
    G --> I
    H --> I
    D --> J[CSV and chart artifacts]
    E --> J
    F --> J
    G --> J
    H --> J
    J --> K[Comprehensive PDF report]
    I --> L[Remotion demo and reflection videos]
```

## Boundaries

- `src/retailpulse/data.py` owns ingestion, cleaning, persistence, and time features.
- `src/retailpulse/analytics.py` owns descriptive business metrics.
- `src/retailpulse/ml.py` owns forecasting, clustering, churn validation, and inventory optimization.
- `src/retailpulse/visuals.py` owns interactive Plotly figures.
- `src/retailpulse/reporting.py` and `pdf_report.py` own generated reporting artifacts.
- `app/dashboard.py` composes the operational user experience.
- `video/` owns the reproducible demo and reflection video compositions.

## Production considerations

The current application is stateless and loads a checked-in processed CSV. For larger deployments, replace the CSV with a warehouse or columnar object storage, persist trained model artifacts, schedule data-quality checks, and add authentication and model-drift monitoring.

