from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import average_precision_score, mean_absolute_percentage_error, roc_auc_score
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class ForecastResult:
    forecast: pd.DataFrame
    mape: float
    method: str


@dataclass(frozen=True)
class ChurnResult:
    customers: pd.DataFrame
    auc: float
    model_name: str
    average_precision: float = math.nan
    evaluation_churn_rate: float = math.nan
    evaluation_start: pd.Timestamp | None = None
    evaluation_end: pd.Timestamp | None = None


_CHURN_FEATURE_COLUMNS = [
    "Frequency",
    "Monetary",
    "Units",
    "TenureDays",
    "AvgOrderValue",
    "OrdersPerMonth",
]


def _customer_features(df: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    customers = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda values: int((snapshot_date - values.max()).days)),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
        Units=("Quantity", "sum"),
        LastPurchase=("InvoiceDate", "max"),
        FirstPurchase=("InvoiceDate", "min"),
    )
    customers["TenureDays"] = (customers["LastPurchase"] - customers["FirstPurchase"]).dt.days.clip(lower=1)
    customers["AvgOrderValue"] = customers["Monetary"] / customers["Frequency"].replace(0, np.nan)
    customers["OrdersPerMonth"] = customers["Frequency"] / (customers["TenureDays"] / 30).replace(0, np.nan)
    customers = customers.fillna(0).reset_index()
    return customers


def build_demand_forecast(df: pd.DataFrame, horizon_days: int = 90) -> ForecastResult:
    daily = (
        df.set_index("InvoiceDate")
        .resample("D")["Revenue"]
        .sum()
        .rename("y")
        .reset_index()
        .rename(columns={"InvoiceDate": "ds"})
    )
    daily["y"] = daily["y"].fillna(0)

    try:
        from prophet import Prophet  # type: ignore

        holdout_days = min(30, max(len(daily) // 4, 1))
        train = daily.iloc[:-holdout_days].copy()
        test = daily.iloc[-holdout_days:].copy()
        if len(train) < 30:
            return _seasonal_forecast(daily, horizon_days=horizon_days)

        validation_model = Prophet(weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=False)
        validation_model.fit(train)
        validation = validation_model.predict(test[["ds"]])
        mape = float(
            mean_absolute_percentage_error(test["y"].clip(lower=1), validation["yhat"].clip(lower=1))
        )

        final_model = Prophet(weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=False)
        final_model.fit(daily)
        future = final_model.make_future_dataframe(periods=horizon_days)
        forecast = final_model.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        out = forecast.tail(horizon_days).copy()
        out["Method"] = "Prophet"
        return ForecastResult(out, mape, "Prophet")
    except Exception:
        return _seasonal_forecast(daily, horizon_days=horizon_days)


def _seasonal_forecast(daily: pd.DataFrame, horizon_days: int) -> ForecastResult:
    holdout_days = min(30, max(len(daily) // 4, 1))
    train = daily.iloc[:-holdout_days].copy()
    test = daily.iloc[-holdout_days:].copy()
    if train.empty:
        train = daily.copy()
        test = daily.iloc[0:0].copy()

    train["Weekday"] = train["ds"].dt.dayofweek
    weekday_mean = train.groupby("Weekday")["y"].mean()
    overall_mean = max(float(train["y"].mean()), 1.0)
    recent_level = float(train["y"].tail(28).mean()) if len(train) >= 28 else overall_mean
    weekday_factor = (weekday_mean / overall_mean).replace([np.inf, -np.inf], 1).fillna(1)

    def predict(dates: pd.Series) -> pd.Series:
        return dates.dt.dayofweek.map(weekday_factor).fillna(1).astype(float) * recent_level

    if not test.empty:
        yhat_test = predict(test["ds"])
        mape = float(mean_absolute_percentage_error(test["y"].clip(lower=1), yhat_test.clip(lower=1)))
    else:
        mape = math.nan

    future_dates = pd.date_range(daily["ds"].max() + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    yhat = predict(pd.Series(future_dates))
    residual_std = float((train["y"] - predict(train["ds"])).std()) if len(train) > 10 else 0
    forecast = pd.DataFrame(
        {
            "ds": future_dates,
            "yhat": yhat.values,
            "yhat_lower": np.maximum(yhat.values - 1.64 * residual_std, 0),
            "yhat_upper": yhat.values + 1.64 * residual_std,
            "Method": "Seasonal weekday baseline",
        }
    )
    return ForecastResult(forecast, mape, "Seasonal weekday baseline")


def build_kmeans_segments(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    customers = _customer_features(df)
    feature_columns = ["Recency", "Frequency", "Monetary", "AvgOrderValue", "OrdersPerMonth"]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(customers[feature_columns])
    model = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    customers["Cluster"] = model.fit_predict(scaled)

    profile = customers.groupby("Cluster").agg(
        Recency=("Recency", "mean"),
        Frequency=("Frequency", "mean"),
        Monetary=("Monetary", "mean"),
    )
    profile["RankScore"] = (
        profile["Monetary"].rank()
        + profile["Frequency"].rank()
        + profile["Recency"].rank(ascending=False)
    )
    ordered_clusters = profile.sort_values("RankScore", ascending=False).index.tolist()
    labels = ["Champions", "Loyal", "At Risk", "Hibernating"]
    label_map = {cluster: labels[index] for index, cluster in enumerate(ordered_clusters[: len(labels)])}
    customers["MLSegment"] = customers["Cluster"].map(label_map).fillna("Monitor")
    return customers


def summarize_kmeans_segments(segments: pd.DataFrame) -> pd.DataFrame:
    summary = (
        segments.groupby("MLSegment", as_index=False)
        .agg(
            Customers=("CustomerID", "count"),
            Revenue=("Monetary", "sum"),
            AvgRecency=("Recency", "mean"),
            AvgFrequency=("Frequency", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )
    summary["RevenueShare"] = summary["Revenue"] / summary["Revenue"].sum()
    return summary


def _new_churn_estimator() -> tuple[object, str]:
    try:
        from xgboost import XGBClassifier

        model = XGBClassifier(
            n_estimators=120,
            max_depth=3,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
            n_jobs=1,
        )
        model_name = "XGBoost Classifier"
    except Exception:
        model = GradientBoostingClassifier(random_state=42)
        model_name = "Gradient Boosting Classifier"
    return model, model_name


def _churn_snapshot(
    df: pd.DataFrame,
    cutoff: pd.Timestamp,
    churn_days: int,
) -> pd.DataFrame:
    observed = df[df["InvoiceDate"] < cutoff]
    if observed.empty:
        return pd.DataFrame()

    customers = _customer_features(observed)
    outcome_end = cutoff + pd.Timedelta(days=churn_days)
    future_buyers = df.loc[
        (df["InvoiceDate"] >= cutoff) & (df["InvoiceDate"] < outcome_end),
        "CustomerID",
    ].unique()
    customers["Churned"] = (~customers["CustomerID"].isin(future_buyers)).astype(int)
    customers["SnapshotDate"] = cutoff
    return customers


def _add_risk_bands(customers: pd.DataFrame, risk: np.ndarray) -> pd.DataFrame:
    customers["ChurnRisk"] = risk
    customers["RiskBand"] = pd.cut(
        customers["ChurnRisk"],
        bins=[-0.01, 0.35, 0.65, 1.01],
        labels=["Low", "Medium", "High"],
    ).astype(str)
    return customers.sort_values("ChurnRisk", ascending=False)


def build_churn_model(df: pd.DataFrame, churn_days: int = 90) -> ChurnResult:
    if churn_days <= 0:
        raise ValueError("churn_days must be positive")

    current_cutoff = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    evaluation_cutoff = current_cutoff - pd.Timedelta(days=churn_days)
    earliest_purchase = df["InvoiceDate"].min()

    training_snapshots = []
    cutoff = evaluation_cutoff - pd.Timedelta(days=churn_days)
    while cutoff > earliest_purchase:
        snapshot = _churn_snapshot(df, cutoff, churn_days)
        if not snapshot.empty:
            training_snapshots.append(snapshot)
        cutoff -= pd.Timedelta(days=churn_days)
    training_snapshots.reverse()

    evaluation = _churn_snapshot(df, evaluation_cutoff, churn_days)
    current_customers = _customer_features(df)
    evaluation_rate = float(evaluation["Churned"].mean()) if not evaluation.empty else math.nan
    evaluation_end = current_cutoff

    if not training_snapshots:
        baseline_risk = evaluation_rate if not math.isnan(evaluation_rate) else 0.5
        risk = np.full(len(current_customers), baseline_risk)
        customers = _add_risk_bands(current_customers, risk)
        return ChurnResult(
            customers,
            math.nan,
            "Historical churn-rate baseline",
            math.nan,
            evaluation_rate,
            evaluation_cutoff,
            evaluation_end,
        )

    training = pd.concat(training_snapshots, ignore_index=True)
    train_y = training["Churned"]
    can_fit_model = len(training) >= 50 and train_y.nunique() == 2

    if not can_fit_model:
        baseline_risk = float(train_y.mean())
        risk = np.full(len(current_customers), baseline_risk)
        test_risk = np.full(len(evaluation), baseline_risk)
        model_name = "Historical churn-rate baseline"
    else:
        model, model_name = _new_churn_estimator()
        model.fit(training[_CHURN_FEATURE_COLUMNS], train_y)
        test_risk = model.predict_proba(evaluation[_CHURN_FEATURE_COLUMNS])[:, 1]

        all_labeled = pd.concat([training, evaluation], ignore_index=True)
        model.fit(all_labeled[_CHURN_FEATURE_COLUMNS], all_labeled["Churned"])
        risk = model.predict_proba(current_customers[_CHURN_FEATURE_COLUMNS])[:, 1]

    test_y = evaluation["Churned"]
    auc = float(roc_auc_score(test_y, test_risk)) if test_y.nunique() == 2 else math.nan
    average_precision = (
        float(average_precision_score(test_y, test_risk)) if test_y.sum() > 0 else math.nan
    )
    customers = _add_risk_bands(current_customers, risk)
    return ChurnResult(
        customers,
        auc,
        model_name,
        average_precision,
        evaluation_rate,
        evaluation_cutoff,
        evaluation_end,
    )


def build_inventory_optimization(
    df: pd.DataFrame,
    ordering_cost: float = 50.0,
    holding_rate: float = 0.25,
    lead_time_days: int = 14,
) -> pd.DataFrame:
    product = df.groupby(["StockCode", "Description"], as_index=False).agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        UnitPrice=("UnitPrice", "mean"),
        Orders=("InvoiceNo", "nunique"),
    )
    product = product.sort_values("Revenue", ascending=False).reset_index(drop=True)
    total_revenue = product["Revenue"].sum()
    product["RevenueShare"] = product["Revenue"] / total_revenue
    product["CumulativeRevenueShare"] = product["RevenueShare"].cumsum()
    product["ABCClass"] = np.select(
        [
            product["CumulativeRevenueShare"] <= 0.80,
            product["CumulativeRevenueShare"] <= 0.95,
        ],
        ["A", "B"],
        default="C",
    )

    days_observed = max((df["InvoiceDate"].max() - df["InvoiceDate"].min()).days + 1, 1)
    product["AnnualDemand"] = product["Quantity"] / days_observed * 365
    holding_cost = (product["UnitPrice"].clip(lower=0.01) * holding_rate).clip(lower=0.01)
    product["EOQ"] = np.sqrt((2 * product["AnnualDemand"] * ordering_cost) / holding_cost)
    product["DailyDemand"] = product["Quantity"] / days_observed
    product["ReorderPoint"] = product["DailyDemand"] * lead_time_days

    daily_sku = (
        df.groupby(["StockCode", pd.Grouper(key="InvoiceDate", freq="D")])["Quantity"]
        .sum()
        .reset_index()
        .groupby("StockCode")["Quantity"]
        .std()
        .fillna(0)
        .rename("DailyDemandStd")
        .reset_index()
    )
    product = product.merge(daily_sku, on="StockCode", how="left")
    product["SafetyStock"] = product["DailyDemandStd"].fillna(0) * math.sqrt(lead_time_days)
    product["RecommendedStockLevel"] = product["ReorderPoint"] + product["SafetyStock"]
    return product
