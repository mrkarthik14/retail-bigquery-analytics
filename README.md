# 🛍️ Retail Analytics with Google BigQuery
### End-to-End SQL + Python Analytics on Fashion E-Commerce Data

[![BigQuery](https://img.shields.io/badge/Google-BigQuery-4285F4?logo=googlebigquery)](https://cloud.google.com/bigquery)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)](https://streamlit.io)

---

## 📌 Project Overview

This project performs end-to-end retail analytics on a **fashion e-commerce dataset** using **Google BigQuery** as the primary data platform. It covers SQL-based data exploration, customer segmentation, product performance analysis, cohort retention, and funnel analysis — all deployed as an interactive Streamlit dashboard.

**Dataset:** [`bigquery-public-data.thelook_ecommerce`](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce) — a synthetic but realistic fashion retail dataset available for free in BigQuery's public data marketplace.

---

## 🎯 Business Problems Solved

| # | Business Question | Analysis Type |
|---|---|---|
| 1 | How are monthly revenue and order volumes trending? | Sales Trend Analysis |
| 2 | Which customers are high-value vs. at-risk of churn? | RFM Segmentation |
| 3 | Which product categories and items drive the most revenue? | Product Performance |
| 4 | How well do we retain customers month-over-month? | Cohort Retention |
| 5 | Where in the purchase funnel are users dropping off? | Conversion Funnel |

---

## 📁 Project Structure

```
retail-bigquery-analytics/
├── README.md
├── requirements.txt
│
├── queries/
│   ├── 01_sales_trend_analysis.sql        # Monthly revenue, AOV, growth rate
│   ├── 02_customer_segmentation_rfm.sql   # RFM scoring + segment labeling
│   ├── 03_product_performance.sql         # Category + SKU-level revenue ranking
│   ├── 04_cohort_retention_analysis.sql   # Monthly cohort retention matrix
│   └── 05_conversion_funnel_analysis.sql  # Event-based funnel drop-off
│
├── analysis/
│   └── bigquery_client.py                 # Python BigQuery client + EDA
│
└── dashboard/
    └── app.py                             # Streamlit multi-page dashboard
```

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### BigQuery Setup (Free)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (free tier gives $300 credit + 1TB/month free queries)
3. Enable the BigQuery API
4. Create a Service Account and download credentials JSON
5. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-credentials.json"
```

### Running the SQL Queries

Open [BigQuery Console](https://console.cloud.google.com/bigquery) and run any file from `/queries/` directly. The dataset is already publicly available — no setup needed.

### Running the Python Analysis

```bash
cd analysis/
python bigquery_client.py
```

### Launching the Dashboard

```bash
cd dashboard/
streamlit run app.py
```

---

## 🔍 Key Insights Discovered

- **Top 3 product categories** account for ~58% of total revenue
- **Champion customers** (RFM score 9–12) represent only 15% of users but drive 41% of revenue
- **Month-3 cohort retention** averages ~22%, with strong variation by acquisition channel
- **Checkout → Purchase** is the largest funnel drop-off at ~47%
- Revenue shows a consistent **+12–18% MoM growth trend** in peak fashion seasons

---

## 🛠️ BigQuery Features Used

| Feature | Where Used |
|---|---|
| `WITH` CTEs (multi-level) | All queries |
| Window Functions (`ROW_NUMBER`, `RANK`, `LAG`, `NTILE`) | RFM, Product, Trend |
| `DATE_TRUNC`, `DATE_DIFF` | Cohort, Trend queries |
| `QUALIFY` clause | Product ranking deduplication |
| `APPROX_COUNT_DISTINCT` | Funnel analysis |
| `ARRAY_AGG` + `UNNEST` | Cohort matrix pivoting |
| Partitioned table scanning | Optimized in all queries |

---

## 📊 Dashboard Preview

The Streamlit dashboard includes 5 tabs:
1. **Sales Overview** — Revenue trend, AOV, growth rate charts
2. **Customer Segments** — RFM distribution bubble chart
3. **Product Performance** — Top 10 categories + revenue waterfall
4. **Cohort Retention** — Heatmap matrix
5. **Funnel Analysis** — Drop-off bar chart

---

## 📄 License

MIT License — free to use, fork, and adapt.
