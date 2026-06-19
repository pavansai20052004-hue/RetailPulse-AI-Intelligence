# RetailPulse Reviewer Checklist

This is the expected review path. Complete it in a private/incognito browser
before submitting.

## Access

- [ ] Source link opens a public repository without sign-in.
- [ ] Repository root clearly contains the application, package, tests,
      dependencies, Docker configuration, notebooks, reports, and outputs.
- [ ] Live deployment opens without sign-in.
- [ ] Demo video and reflection video play without sign-in.
- [ ] Project report opens without sign-in.

## Source and Reproducibility

- [ ] `requirements.txt` is present.
- [ ] `pyproject.toml` is present.
- [ ] `Dockerfile` is present.
- [ ] Dashboard entry point is `app/dashboard.py`.
- [ ] Installation commands are `python -m pip install -r requirements.txt` and
      `python -m pip install -e .`.
- [ ] Dashboard command is `streamlit run app/dashboard.py`.
- [ ] Test command is `python -m pytest`.
- [ ] Pipeline command is `python -m retailpulse.pipeline`.
- [ ] No secret, API key, credential, or private dataset location is committed.

## Live Dashboard

- [ ] Landing page displays the RetailPulse title and summary KPIs.
- [ ] Revenue, order, customer, product, and average-order-value metrics render.
- [ ] Overview charts render without exceptions.
- [ ] Country and date filters update the overview.
- [ ] Demand Forecast displays the forecast, interval, method, and MAPE.
- [ ] Customer Segments displays a chart and table.
- [ ] Churn Risk displays risk groups, scores, model name, and AUC-ROC.
- [ ] Inventory displays ABC classes, EOQ, reorder point, and stock guidance.
- [ ] Layout remains usable on a phone-width viewport.

## Report

- [ ] Local report path is
      `output/pdf/RetailPulse_Final_Comprehensive_Report.pdf`.
- [ ] Public report link resolves to the same final PDF.
- [ ] Report title is "RetailPulse Final Comprehensive Report."
- [ ] Report covers the problem, data, approach, models, findings, recommendations,
      figures, and conclusion.
- [ ] All pages render and no chart or table is clipped.

## Submission Consistency

- [ ] Repository, app, demo, reflection, and report all use the name RetailPulse.
- [ ] Demo shows the same deployment URL entered in the form.
- [ ] Numbers stated in the demo agree with the dashboard and report.
- [ ] All public links were tested while signed out.
- [ ] The submission form contains only final public links, not placeholders.

