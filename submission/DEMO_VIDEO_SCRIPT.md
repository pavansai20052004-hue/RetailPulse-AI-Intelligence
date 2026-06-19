# RetailPulse Demo Video Plan and Script

Target duration: 4-5 minutes. Record at 1080p with the browser zoom at 100%.
Use the public deployment, not localhost, and keep the deployment URL visible at
the beginning.

## Before Recording

- Close unrelated tabs, notifications, bookmarks, and personal account details.
- Open `<PUBLIC_STREAMLIT_APP_URL>` in a private/incognito window.
- Wait for every chart and model result to finish loading.
- Check that the country and date filters are at their default values.
- Prepare the final report PDF in a second tab.
- Record the whole browser window and use a clear microphone.

## Shot List

| Time | Screen action | Purpose |
| --- | --- | --- |
| 0:00-0:25 | Show the public URL and dashboard title | Identify the project and prove deployment |
| 0:25-1:20 | Walk through KPIs and overview charts | Explain business performance |
| 1:20-1:45 | Change a country or date filter, then reset it | Demonstrate interactivity |
| 1:45-2:20 | Open Demand Forecast | Explain the 90-day forecast and uncertainty |
| 2:20-2:50 | Open Customer Segments | Explain customer-value grouping |
| 2:50-3:20 | Open Churn Risk | Explain retention prioritization |
| 3:20-3:50 | Open Inventory | Explain ABC and EOQ recommendations |
| 3:50-4:20 | Show the PDF report | Demonstrate complete documentation |
| 4:20-4:45 | Summarize value and close | State the outcome |

## Narration Script

### Opening

"Hello, this is RetailPulse, an AI-powered sales intelligence platform built from
the UCI Online Retail dataset. The project turns transaction data into executive
KPIs, customer insights, predictive models, and inventory recommendations. This
is the publicly deployed application shown at the URL in the browser."

### Overview

"The overview presents total revenue, orders, customers, products, and average
order value from cleaned transactions. The charts show monthly revenue, leading
countries, best-selling products, and customer segment value. The current
dataset contains approximately 8.91 million in revenue across 18,532 orders and
4,338 customers. The United Kingdom is the dominant market, and sales strengthen
significantly in the final months of 2011."

### Filters

"The sidebar filters let a reviewer narrow the analysis by country and date.
When I change a filter, the overview metrics and charts update together. I will
reset the filters now so the predictive sections use the complete view."

### Demand Forecast

"The Demand Forecast section estimates the next 90 days and displays a prediction
interval. It uses Prophet when available and otherwise uses a seasonal weekday
baseline. The model name and backtest MAPE are displayed with the chart, making
the result transparent rather than presenting a forecast without validation."

### Customer Segments

"The Customer Segments section uses purchasing behavior to group customers by
recency, frequency, and monetary value. These segments help the business
differentiate high-value customers from customers who need re-engagement and
support more targeted marketing decisions."

### Churn Risk

"The Churn Risk section estimates which customers are most likely to become
inactive. It shows risk bands, customer-level scores, and the model's AUC-ROC.
The practical use is to prioritize retention outreach instead of treating every
customer the same."

### Inventory

"The Inventory section combines ABC classification with economic order quantity
and reorder-point calculations. Class A products receive the highest attention,
while the table provides recommended stock levels for operational planning."

### Report and Closing

"The submission also includes this comprehensive PDF report, which documents the
problem, data preparation, methodology, models, findings, recommendations, and
visual results. RetailPulse brings descriptive, predictive, and prescriptive
analytics into one reproducible project. Thank you for reviewing the project."

## Recording Quality Check

- [ ] The first 25 seconds show the public deployment URL.
- [ ] Text and charts are readable at normal playback size.
- [ ] No loading spinner or error is left unexplained.
- [ ] The narration names the dataset, problem, methods, and business value.
- [ ] Every major dashboard tab appears at least once.
- [ ] The recording contains no credentials or private information.
- [ ] The final exported video plays from beginning to end.

