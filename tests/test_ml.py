from __future__ import annotations

import numpy as np
import pandas as pd

from retailpulse.data import add_time_features
from retailpulse import ml
from retailpulse.ml import (
    build_churn_model,
    build_demand_forecast,
    build_inventory_optimization,
    build_kmeans_segments,
)


def _sample_dataset() -> pd.DataFrame:
    rows = []
    for customer in range(1, 9):
        for order in range(1, 5):
            invoice_date = pd.Timestamp("2011-01-01") + pd.Timedelta(days=customer * 12 + order * 7)
            rows.append(
                {
                    "InvoiceNo": f"{customer}-{order}",
                    "StockCode": f"SKU{order}",
                    "Description": f"Product {order}",
                    "Quantity": customer + order,
                    "InvoiceDate": invoice_date,
                    "UnitPrice": 2.5 + order,
                    "CustomerID": 1000 + customer,
                    "Country": "United Kingdom",
                    "Revenue": (customer + order) * (2.5 + order),
                }
            )
    return add_time_features(pd.DataFrame(rows))


def _churn_dataset() -> pd.DataFrame:
    rows = []
    schedules = {
        0: range(0, 211, 15),
        1: range(0, 91, 15),
        2: range(0, 151, 15),
        3: range(0, 211, 35),
    }
    for customer in range(80):
        for order, day in enumerate(schedules[customer % 4]):
            rows.append(
                {
                    "InvoiceNo": f"{customer}-{order}",
                    "StockCode": "SKU",
                    "Description": "Product",
                    "Quantity": 1 + customer % 3,
                    "InvoiceDate": pd.Timestamp("2020-01-01") + pd.Timedelta(days=day),
                    "UnitPrice": 10.0,
                    "CustomerID": 2000 + customer,
                    "Country": "United Kingdom",
                    "Revenue": float(10 + customer % 5),
                }
            )
    return pd.DataFrame(rows)


def test_advanced_models_return_expected_outputs() -> None:
    data = _sample_dataset()

    forecast = build_demand_forecast(data, horizon_days=14)
    segments = build_kmeans_segments(data, n_clusters=4)
    churn = build_churn_model(data, churn_days=30)
    inventory = build_inventory_optimization(data)

    assert len(forecast.forecast) == 14
    assert {"ds", "yhat", "yhat_lower", "yhat_upper"}.issubset(forecast.forecast.columns)
    assert "MLSegment" in segments.columns
    assert "ChurnRisk" in churn.customers.columns
    assert churn.customers["ChurnRisk"].between(0, 1).all()
    assert {"ABCClass", "EOQ", "ReorderPoint"}.issubset(inventory.columns)


def test_churn_model_uses_future_outcomes_and_excludes_recency(monkeypatch) -> None:
    fitted_columns = []

    class RecordingEstimator:
        def fit(self, x: pd.DataFrame, y: pd.Series) -> "RecordingEstimator":
            fitted_columns.append(x.columns.tolist())
            return self

        def predict_proba(self, x: pd.DataFrame) -> np.ndarray:
            risk = (x["Frequency"] / x["Frequency"].max()).fillna(0.5).clip(0.05, 0.95)
            return np.column_stack([1 - risk, risk])

    monkeypatch.setattr(
        ml,
        "_new_churn_estimator",
        lambda: (RecordingEstimator(), "Recording estimator"),
    )
    data = _churn_dataset()

    result = build_churn_model(data, churn_days=30)

    assert fitted_columns
    assert all("Recency" not in columns for columns in fitted_columns)
    assert all("LastPurchase" not in columns for columns in fitted_columns)
    assert result.evaluation_start == pd.Timestamp("2020-06-30")
    assert result.evaluation_end == pd.Timestamp("2020-07-30")
    assert result.evaluation_churn_rate == 0.5
    assert 0 <= result.auc <= 1
    assert 0 <= result.average_precision <= 1


def test_seasonal_forecast_metrics_use_unseen_holdout() -> None:
    dates = pd.date_range("2022-01-01", periods=120, freq="D")
    daily = pd.DataFrame({"ds": dates, "y": [10.0] * 90 + [100.0] * 30})

    result = ml._seasonal_forecast(daily, horizon_days=7)

    assert result.mape > 0.8
