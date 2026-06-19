from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .analytics import build_overview_metrics, format_currency, format_number
from .config import OUTPUT_DIR
from .ml import ForecastResult, ChurnResult


PDF_DIR = OUTPUT_DIR / "pdf"


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "RetailPulseTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#1F1A17"),
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "RetailPulseH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#C96E4A"),
            spaceBefore=10,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "RetailPulseH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1F1A17"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "RetailPulseBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#342D28"),
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "RetailPulseSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#74675F"),
        ),
    }


def _bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"- {text}", styles["body"])


def _table(rows: list[list[object]], widths: list[float] | None = None) -> Table:
    table = Table(rows, colWidths=widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F5E8DF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F1A17")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E7DBD1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF9F3")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _image(path: Path, width: float = 6.8 * inch) -> Image | None:
    if not path.exists():
        return None
    img = Image(str(path))
    ratio = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width
    img.drawHeight = width * ratio
    return img


def build_comprehensive_pdf(
    df: pd.DataFrame,
    forecast_result: ForecastResult,
    kmeans_summary: pd.DataFrame,
    churn_result: ChurnResult,
    inventory: pd.DataFrame,
    figure_paths: list[Path],
    output_path: Path | None = None,
) -> Path:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    target = output_path or (PDF_DIR / "RetailPulse_Final_Comprehensive_Report.pdf")
    styles = _styles()
    metrics = build_overview_metrics(df)
    high_risk_count = int((churn_result.customers["RiskBand"] == "High").sum())
    top_inventory = inventory.head(8)

    doc = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="RetailPulse Final Comprehensive Report",
    )
    story: list[object] = []

    story.append(Paragraph("Internship Project Report: RetailPulse AI Sales Intelligence Platform", styles["title"]))
    story.append(Paragraph("1. Executive Summary", styles["h1"]))
    story.append(
        Paragraph(
            "RetailPulse is a comprehensive AI-driven retail analytics platform that combines sales intelligence, "
            "demand forecasting, customer segmentation, churn prediction, and inventory optimization. The platform "
            "uses cleaned transactional data from the Online Retail dataset to produce business-ready insights for "
            "revenue growth, customer retention, and stock planning.",
            styles["body"],
        )
    )
    story.append(Paragraph("2. Project Objectives", styles["h1"]))
    for item in [
        "Demand Forecasting: predict near-term sales using time-series modeling.",
        "Customer Intelligence: segment customers using RFM and K-Means clustering.",
        "Churn Prevention: identify inactive and high-risk customers with XGBoost classification.",
        "Inventory Optimization: rank SKUs with ABC analysis and calculate EOQ reorder quantities.",
        "Dashboard Delivery: provide a Streamlit interface and reproducible reporting pipeline.",
    ]:
        story.append(_bullet(item, styles))

    story.append(Paragraph("3. Business Snapshot", styles["h1"]))
    story.append(
        _table(
            [
                ["Metric", "Value"],
                ["Total Revenue", f"${metrics['total_revenue']:,.2f}"],
                ["Orders", f"{metrics['total_orders']:,}"],
                ["Customers", f"{metrics['total_customers']:,}"],
                ["Products", f"{metrics['total_products']:,}"],
                ["Average Order Value", f"${metrics['average_order_value']:,.2f}"],
            ],
            [2.5 * inch, 2.5 * inch],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("4. Technical Methodology", styles["h1"]))
    methods = [
        ("Phase 1: Data Ingestion and ETL", "The raw Excel data is loaded with Pandas, cancellations are removed, missing CustomerID values are filtered out, invalid quantities and prices are removed, and revenue is calculated at line-item level."),
        ("Phase 2: Feature Engineering", "The pipeline creates invoice time features, RFM customer features, daily demand series, customer tenure, order cadence, and SKU-level demand measures."),
        ("Phase 3: Model Development and Validation", "The project trains or computes dedicated models for forecasting, customer clustering, churn risk, ABC classification, and EOQ inventory recommendations."),
        ("Phase 4: Dashboard Integration and Deployment", "The analytics layer is integrated into a Streamlit dashboard with custom styling, reproducible outputs, tests, and Docker metadata."),
    ]
    for title, body in methods:
        story.append(Paragraph(title, styles["h2"]))
        story.append(Paragraph(body, styles["body"]))

    story.append(Paragraph("5. AI Techniques and Algorithms", styles["h1"]))
    story.append(Paragraph("5.1 Demand Forecasting", styles["h2"]))
    story.append(
        Paragraph(
            f"The forecasting module uses Prophet when available and otherwise falls back to a seasonal weekday baseline. "
            f"The current run used {forecast_result.method} with a backtest MAPE of {forecast_result.mape:.2%}.",
            styles["body"],
        )
    )
    story.append(Paragraph("5.2 Customer Segmentation: K-Means Clustering", styles["h2"]))
    story.append(
        Paragraph(
            "RFM and behavioral features are scaled with StandardScaler and clustered into four business-friendly "
            "segments: Champions, Loyal, At Risk, and Hibernating.",
            styles["body"],
        )
    )
    story.append(
        _table(
            [["Segment", "Customers", "Revenue Share"]]
            + [
                [row.MLSegment, f"{int(row.Customers):,}", f"{row.RevenueShare:.1%}"]
                for row in kmeans_summary.itertuples()
            ],
            [2.1 * inch, 1.4 * inch, 1.6 * inch],
        )
    )
    story.append(Paragraph("5.3 Churn Prediction: XGBoost Classifier", styles["h2"]))
    story.append(
        Paragraph(
            f"Churn is defined as inactivity longer than 90 days. The current model is {churn_result.model_name}, "
            f"with time-based holdout AUC-ROC of {churn_result.auc:.2f} and average precision of "
            f"{churn_result.average_precision:.2f}. It flags {high_risk_count:,} customers as high risk. "
            "Recency and last-purchase fields are excluded from model inputs to avoid target leakage.",
            styles["body"],
        )
    )
    story.append(Paragraph("5.4 Inventory Optimization: ABC Analysis and EOQ", styles["h2"]))
    story.append(
        Paragraph(
            "SKU revenue contribution is converted into A, B, and C priority classes. EOQ estimates optimal reorder "
            "quantity using annualized demand, ordering cost, and holding cost assumptions.",
            styles["body"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("6. Technology Stack", styles["h1"]))
    for item in [
        "Programming Language: Python 3.12 deployment runtime",
        "Dashboard Framework: Streamlit with custom CSS",
        "Machine Learning: scikit-learn, XGBoost, optional Prophet-compatible forecasting",
        "Visualization: Plotly, Matplotlib, Seaborn",
        "Reporting: ReportLab PDF generation with pipeline artifacts",
        "Deployment: Dockerfile and requirements-based environment",
    ]:
        story.append(_bullet(item, styles))

    story.append(Paragraph("6.1 System Architecture", styles["h2"]))
    story.append(
        Paragraph(
            "The application follows a layered architecture: raw and processed transaction data feed a reusable "
            "Python analytics package; descriptive analytics, forecasting, clustering, churn scoring, and inventory "
            "optimization generate versionable tables; Streamlit provides the operational interface; ReportLab and "
            "Remotion produce reviewer-ready PDF and video deliverables; Docker and Render configuration provide a "
            "reproducible deployment path.",
            styles["body"],
        )
    )

    story.append(Paragraph("7. Model Outputs", styles["h1"]))
    forecast_top = forecast_result.forecast.head(7)
    story.append(
        _table(
            [["Forecast Date", "Predicted Revenue", "Lower", "Upper"]]
            + [
                [
                    row.ds.strftime("%Y-%m-%d"),
                    f"${row.yhat:,.0f}",
                    f"${row.yhat_lower:,.0f}",
                    f"${row.yhat_upper:,.0f}",
                ]
                for row in forecast_top.itertuples()
            ],
            [1.5 * inch, 1.5 * inch, 1.3 * inch, 1.3 * inch],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        _table(
            [["SKU", "Description", "ABC", "EOQ", "Reorder Point"]]
            + [
                [
                    row.StockCode,
                    str(row.Description)[:34],
                    row.ABCClass,
                    f"{row.EOQ:,.0f}",
                    f"{row.ReorderPoint:,.0f}",
                ]
                for row in top_inventory.itertuples()
            ],
            [0.9 * inch, 2.6 * inch, 0.55 * inch, 0.8 * inch, 1.0 * inch],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("8. Output Visuals", styles["h1"]))
    for index, path in enumerate(figure_paths, start=1):
        image = _image(path)
        if image:
            story.append(Paragraph(f"Fig {index}: {path.stem.replace('_', ' ').title()}", styles["h2"]))
            story.append(image)
            story.append(Spacer(1, 10))
            if index in {2, 4}:
                story.append(PageBreak())

    story.append(Paragraph("9. Conclusion", styles["h1"]))
    story.append(
        Paragraph(
            "RetailPulse now demonstrates a complete applied retail AI workflow: cleaned transactional data, "
            "advanced customer and inventory modeling, predictive forecasting, operational recommendations, "
            "a polished dashboard, and a comprehensive PDF report suitable for internship or portfolio submission.",
            styles["body"],
        )
    )
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.", styles["small"]))

    doc.build(story)
    return target
