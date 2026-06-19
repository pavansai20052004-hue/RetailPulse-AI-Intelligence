# RetailPulse Model Card

## Intended use

RetailPulse supports retail planning and prioritization. Its predictions are decision-support signals, not automated decisions.

## Demand forecast

- Target: daily revenue.
- Horizon: 90 days.
- Validation: unseen trailing holdout period.
- Metric: mean absolute percentage error.
- Implementation: Prophet when installed; otherwise a transparent weekday-seasonal baseline.
- Limitation: the dataset covers approximately one year and contains a partial December, so long-horizon seasonality is uncertain.

## Customer segmentation

- Algorithm: K-Means.
- Features: recency, frequency, monetary value, average order value, and order cadence.
- Scaling: `StandardScaler`.
- Output: four business-oriented labels derived from cluster profiles.
- Limitation: cluster labels are descriptive and should be reviewed after major data changes.

## Churn model

- Outcome: no purchase in the future 90-day outcome window.
- Validation: chronological future-window evaluation.
- Features: frequency, monetary value, units, tenure, average order value, and order cadence.
- Leakage controls: recency, last purchase, and other label-defining fields are excluded from model inputs.
- Metrics: ROC AUC and average precision.
- Limitation: historical inactivity is a proxy for churn; it does not represent an explicit customer cancellation.

## Inventory optimization

- Methods: ABC revenue classification, EOQ, safety stock, and reorder point.
- User-adjustable assumptions: ordering cost, annual holding rate, and lead time.
- Limitation: recommendations do not include supplier minimums, capacity constraints, service-level targets, or current on-hand stock.

## Responsible use

Review customer-level actions for fairness and business context. Do not use churn scores to deny service or make consequential decisions without human review.

