from __future__ import annotations

import pandas as pd

from retailpulse.analytics import build_customer_segments, build_overview_metrics
from retailpulse.data import clean_retail_data


def test_clean_retail_data_removes_invalid_rows_and_creates_revenue() -> None:
    raw = pd.DataFrame(
        {
            "InvoiceNo": ["1001", "C1002", "1003", "1004"],
            "StockCode": ["A", "B", "C", "D"],
            "Description": ["Item A", "Item B", "Item C", "Item D"],
            "Quantity": [2, 3, -1, 4],
            "InvoiceDate": pd.to_datetime(
                ["2011-01-01 10:00:00", "2011-01-01 11:00:00", "2011-01-01 12:00:00", "2011-01-01 13:00:00"]
            ),
            "UnitPrice": [5.0, 5.0, 2.0, 0.0],
            "CustomerID": [12345.0, 12345.0, 12346.0, None],
            "Country": ["UK", "UK", "France", "Germany"],
        }
    )

    cleaned = clean_retail_data(raw)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Revenue"] == 10.0
    assert cleaned.iloc[0]["CustomerID"] == 12345


def test_build_customer_segments_and_metrics_return_expected_fields() -> None:
    data = pd.DataFrame(
        {
            "InvoiceNo": ["1", "1", "2", "3", "4", "5", "6", "7"],
            "StockCode": list("ABCDEFGH"),
            "Description": [f"Item {letter}" for letter in "ABCDEFGH"],
            "Quantity": [1, 2, 1, 2, 3, 1, 2, 3],
            "InvoiceDate": pd.to_datetime(
                [
                    "2011-01-01 10:00:00",
                    "2011-01-01 10:10:00",
                    "2011-02-01 11:00:00",
                    "2011-03-01 12:00:00",
                    "2011-04-01 13:00:00",
                    "2011-05-01 14:00:00",
                    "2011-06-01 15:00:00",
                    "2011-07-01 16:00:00",
                ]
            ),
            "UnitPrice": [10, 10, 15, 20, 10, 30, 40, 50],
            "CustomerID": [101, 101, 102, 103, 104, 105, 106, 107],
            "Country": ["UK"] * 8,
            "Revenue": [10, 20, 15, 40, 30, 30, 80, 150],
            "InvoiceYear": [2011] * 8,
            "InvoiceMonth": pd.to_datetime(
                ["2011-01-01", "2011-01-01", "2011-02-01", "2011-03-01", "2011-04-01", "2011-05-01", "2011-06-01", "2011-07-01"]
            ),
            "InvoiceMonthLabel": ["Jan 2011", "Jan 2011", "Feb 2011", "Mar 2011", "Apr 2011", "May 2011", "Jun 2011", "Jul 2011"],
            "InvoiceDay": [1] * 8,
            "InvoiceHour": [10, 10, 11, 12, 13, 14, 15, 16],
            "InvoiceWeekday": ["Saturday", "Saturday", "Tuesday", "Tuesday", "Friday", "Sunday", "Wednesday", "Friday"],
        }
    )

    metrics = build_overview_metrics(data)
    segments = build_customer_segments(data)

    assert metrics["total_orders"] == 7
    assert metrics["total_customers"] == 7
    assert "Segment" in segments.columns
    assert segments["Segment"].notna().all()
