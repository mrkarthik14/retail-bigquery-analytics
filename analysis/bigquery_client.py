"""
bigquery_client.py
------------------
Connects to Google BigQuery, runs each analytical query,
loads results into Pandas DataFrames, and exports them as
CSVs for use in the Streamlit dashboard.

Requirements:
    pip install google-cloud-bigquery pandas db-dtypes

Authentication:
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
    OR run `gcloud auth application-default login` for local dev.
"""

import os
import json
import pandas as pd
from pathlib import Path
from google.cloud import bigquery

# ── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ID  = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")
OUTPUT_DIR  = Path(__file__).parent / "outputs"
QUERIES_DIR = Path(__file__).parent.parent / "queries"

OUTPUT_DIR.mkdir(exist_ok=True)

# ── BigQuery Client ────────────────────────────────────────────────────────────

def get_client() -> bigquery.Client:
    """Return an authenticated BigQuery client."""
    return bigquery.Client(project=PROJECT_ID)


def run_query(client: bigquery.Client, sql: str) -> pd.DataFrame:
    """Execute a SQL string and return results as a DataFrame."""
    job    = client.query(sql)
    result = job.result()           # waits for job to complete
    return result.to_dataframe()


def load_sql(filename: str) -> str:
    """Read a .sql file from the queries directory."""
    path = QUERIES_DIR / filename
    return path.read_text()


# ── Analysis Runners ──────────────────────────────────────────────────────────

def run_sales_trend(client: bigquery.Client) -> pd.DataFrame:
    print("Running: Sales Trend Analysis...")
    sql = load_sql("01_sales_trend_analysis.sql")
    df  = run_query(client, sql)

    df["month"]       = pd.to_datetime(df["month"], format="%b %Y")
    df["total_revenue"] = df["total_revenue"].astype(float)
    df.sort_values("month", inplace=True)

    # Derived: revenue per customer
    df["revenue_per_customer"] = (
        df["total_revenue"] / df["unique_customers"]
    ).round(2)

    print(f"  → {len(df)} months of data loaded.")
    return df


def run_rfm_segmentation(client: bigquery.Client) -> pd.DataFrame:
    print("Running: RFM Customer Segmentation...")
    sql = load_sql("02_customer_segmentation_rfm.sql")
    df  = run_query(client, sql)

    df["total_segment_revenue"] = df["total_segment_revenue"].astype(float)
    df.sort_values("total_segment_revenue", ascending=False, inplace=True)

    print(f"  → {len(df)} customer segments identified.")
    return df


def run_product_performance(client: bigquery.Client) -> pd.DataFrame:
    print("Running: Product Performance Analysis...")
    sql = load_sql("03_product_performance.sql")
    df  = run_query(client, sql)

    categories = df[df["result_type"] == "category_summary"].copy()
    products   = df[df["result_type"] == "top_products"].copy()

    print(f"  → {len(categories)} categories, {len(products)} top SKUs loaded.")
    return categories, products


def run_cohort_retention(client: bigquery.Client) -> pd.DataFrame:
    print("Running: Cohort Retention Analysis...")
    sql = load_sql("04_cohort_retention_analysis.sql")
    df  = run_query(client, sql)

    month_cols = [c for c in df.columns if c.startswith("month_")]
    df[month_cols] = df[month_cols].apply(pd.to_numeric, errors="coerce")

    print(f"  → {len(df)} cohorts loaded.")
    return df


def run_funnel_analysis(client: bigquery.Client) -> pd.DataFrame:
    print("Running: Conversion Funnel Analysis...")
    sql = load_sql("05_conversion_funnel_analysis.sql")
    df  = run_query(client, sql)
    df.sort_values("stage_order", inplace=True)

    print(f"  → {len(df)} funnel stages loaded.")
    return df


# ── Export Utilities ──────────────────────────────────────────────────────────

def save(df: pd.DataFrame, name: str) -> None:
    """Save a DataFrame to CSV in the outputs folder."""
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  ✓ Saved to {path}")


# ── Main Pipeline ──────────────────────────────────────────────────────────────

def main():
    print("\n=== Retail BigQuery Analytics Pipeline ===\n")

    client = get_client()

    # Run all analyses
    df_trend              = run_sales_trend(client)
    df_rfm                = run_rfm_segmentation(client)
    df_cat, df_products   = run_product_performance(client)
    df_cohort             = run_cohort_retention(client)
    df_funnel             = run_funnel_analysis(client)

    # Export results
    print("\nExporting results to CSV...")
    save(df_trend,    "sales_trend")
    save(df_rfm,      "rfm_segments")
    save(df_cat,      "category_performance")
    save(df_products, "top_products")
    save(df_cohort,   "cohort_retention")
    save(df_funnel,   "funnel_analysis")

    # Print quick summary stats
    print("\n=== Summary Stats ===")
    print(f"Total revenue tracked : ₹{df_trend['total_revenue'].sum():,.0f}")
    print(f"Avg monthly revenue   : ₹{df_trend['total_revenue'].mean():,.0f}")
    print(f"Top customer segment  : {df_rfm.iloc[0]['customer_segment']} "
          f"({df_rfm.iloc[0]['revenue_share_pct']}% of revenue)")
    print(f"Top product category  : {df_cat.iloc[0]['category']}")
    print(f"Overall funnel rate   : {df_funnel.iloc[-1]['funnel_entry_pct']}%")
    print("\nDone. ✅")


if __name__ == "__main__":
    main()
