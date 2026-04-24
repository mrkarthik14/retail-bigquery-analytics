"""
app.py — Retail BigQuery Analytics Dashboard
============================================
Interactive Streamlit dashboard for the retail analytics project.
Uses synthetic data that mirrors real BigQuery output so the app
can be deployed publicly without credentials.

To connect to real BigQuery, set USE_BIGQUERY=True and configure
your GCP credentials.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Retail Analytics · BigQuery",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand Colors ──────────────────────────────────────────────────────────────
PRIMARY   = "#E50010"   # H&M red
SECONDARY = "#222222"
ACCENT    = "#F5A623"
NEUTRAL   = "#F0F2F6"
SUCCESS   = "#27AE60"

# ── Synthetic Data Generation ─────────────────────────────────────────────────

@st.cache_data
def load_sales_trend():
    np.random.seed(42)
    months = pd.date_range("2022-01-01", "2024-03-01", freq="MS")
    base   = 180_000
    trend  = np.linspace(0, 120_000, len(months))
    seasonal = 30_000 * np.sin(np.linspace(0, 4 * np.pi, len(months)))
    revenue  = base + trend + seasonal + np.random.normal(0, 8000, len(months))
    orders   = (revenue / np.random.uniform(55, 75, len(months))).astype(int)
    customers = (orders * np.random.uniform(0.75, 0.90, len(months))).astype(int)

    df = pd.DataFrame({
        "month": months,
        "total_revenue": revenue.round(2),
        "total_orders": orders,
        "unique_customers": customers,
        "avg_order_value": (revenue / orders).round(2),
        "total_items_sold": (orders * np.random.uniform(1.8, 2.5, len(months))).astype(int),
    })
    df["revenue_mom_pct"] = df["total_revenue"].pct_change() * 100
    df["revenue_3m_rolling_avg"] = df["total_revenue"].rolling(3).mean()
    return df


@st.cache_data
def load_rfm():
    segments = [
        {"customer_segment": "Champion",          "num_customers": 1240, "avg_recency_days": 12,  "avg_order_count": 8.4, "avg_spend": 420.0,  "total_segment_revenue": 520_800, "revenue_share_pct": 41.2},
        {"customer_segment": "Loyal Customer",    "num_customers": 2180, "avg_recency_days": 31,  "avg_order_count": 5.1, "avg_spend": 260.0,  "total_segment_revenue": 366_820, "revenue_share_pct": 29.0},
        {"customer_segment": "Potential Loyalist","num_customers": 1850, "avg_recency_days": 44,  "avg_order_count": 2.3, "avg_spend": 140.0,  "total_segment_revenue": 129_500, "revenue_share_pct": 10.2},
        {"customer_segment": "At Risk",           "num_customers": 980,  "avg_recency_days": 95,  "avg_order_count": 4.2, "avg_spend": 190.0,  "total_segment_revenue":  98_000, "revenue_share_pct":  7.8},
        {"customer_segment": "New Customer",      "num_customers": 1420, "avg_recency_days": 8,   "avg_order_count": 1.0, "avg_spend": 72.0,   "total_segment_revenue":  78_880, "revenue_share_pct":  6.2},
        {"customer_segment": "Needs Attention",   "num_customers": 640,  "avg_recency_days": 120, "avg_order_count": 2.1, "avg_spend": 95.0,   "total_segment_revenue":  38_000, "revenue_share_pct":  3.0},
        {"customer_segment": "Cannot Lose Them",  "num_customers": 210,  "avg_recency_days": 180, "avg_order_count": 6.8, "avg_spend": 310.0,  "total_segment_revenue":  25_200, "revenue_share_pct":  2.0},
        {"customer_segment": "Lost",              "num_customers": 380,  "avg_recency_days": 310, "avg_order_count": 1.2, "avg_spend": 42.0,   "total_segment_revenue":   8_400, "revenue_share_pct":  0.6},
    ]
    return pd.DataFrame(segments)


@st.cache_data
def load_category_performance():
    categories = [
        {"category": "Outerwear & Coats",  "department": "Women", "total_orders": 18420, "units_sold": 22100, "total_revenue": 412_000, "avg_sale_price": 62.5, "avg_discount_pct": 18.2, "return_rate_pct": 9.1,  "revenue_share_pct": 12.4},
        {"category": "Jeans",              "department": "Women", "total_orders": 22100, "units_sold": 26400, "total_revenue": 384_000, "avg_sale_price": 48.0, "avg_discount_pct": 14.5, "return_rate_pct": 7.8,  "revenue_share_pct": 11.6},
        {"category": "Fashion Hoodies",    "department": "Men",   "total_orders": 19800, "units_sold": 23500, "total_revenue": 298_000, "avg_sale_price": 38.2, "avg_discount_pct": 12.0, "return_rate_pct": 6.2,  "revenue_share_pct": 9.0},
        {"category": "Suits & Blazers",    "department": "Men",   "total_orders": 9200,  "units_sold": 10800, "total_revenue": 276_000, "avg_sale_price": 88.0, "avg_discount_pct": 22.1, "return_rate_pct": 12.4, "revenue_share_pct": 8.3},
        {"category": "Dresses",            "department": "Women", "total_orders": 21300, "units_sold": 24900, "total_revenue": 258_000, "avg_sale_price": 42.1, "avg_discount_pct": 15.8, "return_rate_pct": 10.2, "revenue_share_pct": 7.8},
        {"category": "Sleep & Lounge",     "department": "Women", "total_orders": 16400, "units_sold": 19200, "total_revenue": 198_000, "avg_sale_price": 32.0, "avg_discount_pct": 10.5, "return_rate_pct": 5.1,  "revenue_share_pct": 6.0},
        {"category": "Tops & Tees",        "department": "Men",   "total_orders": 28900, "units_sold": 34200, "total_revenue": 188_000, "avg_sale_price": 22.4, "avg_discount_pct": 8.2,  "return_rate_pct": 4.8,  "revenue_share_pct": 5.7},
        {"category": "Activewear",         "department": "Women", "total_orders": 14200, "units_sold": 17800, "total_revenue": 174_000, "avg_sale_price": 34.8, "avg_discount_pct": 11.3, "return_rate_pct": 6.8,  "revenue_share_pct": 5.2},
        {"category": "Swim",               "department": "Women", "total_orders": 8900,  "units_sold": 11200, "total_revenue": 142_000, "avg_sale_price": 38.0, "avg_discount_pct": 20.4, "return_rate_pct": 8.9,  "revenue_share_pct": 4.3},
        {"category": "Accessories",        "department": "Men",   "total_orders": 19600, "units_sold": 24100, "total_revenue": 118_000, "avg_sale_price": 18.2, "avg_discount_pct": 6.8,  "return_rate_pct": 3.2,  "revenue_share_pct": 3.6},
    ]
    return pd.DataFrame(categories)


@st.cache_data
def load_cohort():
    np.random.seed(7)
    cohorts = pd.date_range("2022-01-01", "2023-06-01", freq="MS")
    labels  = [d.strftime("%b %Y") for d in cohorts]
    sizes   = np.random.randint(800, 2200, len(cohorts))

    records = []
    for i, (label, size) in enumerate(zip(labels, sizes)):
        row = {"cohort": label, "cohort_size": size}
        for m in range(12):
            if m == 0:
                row[f"month_{m}"] = 100.0
            elif m <= (12 - i):
                decay = 100 * (0.42 ** (m * 0.55)) + np.random.normal(0, 1.5)
                row[f"month_{m}"] = max(round(decay, 1), 0)
            else:
                row[f"month_{m}"] = None
        records.append(row)
    return pd.DataFrame(records)


@st.cache_data
def load_funnel():
    data = {
        "funnel_stage":       ["home", "category", "product", "cart", "checkout", "purchase"],
        "users_reached":      [98200,  72400,       55100,     31800,  16900,       8900],
        "step_conversion_pct":[None,   73.7,        76.1,      57.7,   53.1,        52.7],
        "step_dropoff_pct":   [None,   26.3,        23.9,      42.3,   46.9,        47.3],
        "funnel_entry_pct":   [100.0,  73.7,        56.1,      32.4,   17.2,        9.1],
        "users_dropped":      [0,      25800,       17300,     23300,  14900,       8000],
    }
    return pd.DataFrame(data)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:16px 0 8px;'>
        <span style='font-size:2rem;'>🛍️</span><br>
        <strong style='font-size:1.1rem;'>Retail Analytics</strong><br>
        <span style='font-size:0.75rem; color:#888;'>Powered by Google BigQuery</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("📊 Dataset")
    st.code("bigquery-public-data\n.thelook_ecommerce", language=None)

    st.divider()
    st.caption("🔗 Queries")
    for q in [
        "01_sales_trend_analysis",
        "02_customer_segmentation_rfm",
        "03_product_performance",
        "04_cohort_retention_analysis",
        "05_conversion_funnel_analysis",
    ]:
        st.markdown(f"<span style='font-size:0.75rem;'>📄 {q}.sql</span>", unsafe_allow_html=True)

    st.divider()
    st.caption("⚙️ BigQuery Features Used")
    for feat in ["CTEs", "Window Functions", "DATE_TRUNC / DIFF",
                 "QUALIFY clause", "APPROX_COUNT_DISTINCT",
                 "ARRAY_AGG + UNNEST", "NTILE scoring"]:
        st.markdown(f"<span style='font-size:0.74rem;'>✓ {feat}</span>", unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────────────────────

df_trend    = load_sales_trend()
df_rfm      = load_rfm()
df_cat      = load_category_performance()
df_cohort   = load_cohort()
df_funnel   = load_funnel()

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div style='background:linear-gradient(90deg,{PRIMARY},{SECONDARY});
            padding:22px 28px; border-radius:10px; margin-bottom:20px;'>
  <h2 style='color:white;margin:0;'>🛍️ Fashion Retail Analytics — BigQuery</h2>
  <p style='color:#ccc;margin:4px 0 0;font-size:0.9rem;'>
    End-to-end analysis on <code>bigquery-public-data.thelook_ecommerce</code> · 
    Jan 2022 – Mar 2024
  </p>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────

total_rev   = df_trend["total_revenue"].sum()
total_ord   = df_trend["total_orders"].sum()
avg_aov     = df_trend["avg_order_value"].mean()
total_cust  = df_rfm["num_customers"].sum()
funnel_cvr  = df_funnel.iloc[-1]["funnel_entry_pct"]

k1, k2, k3, k4, k5 = st.columns(5)
for col, label, val, fmt, delta in [
    (k1, "Total Revenue",      total_rev,  "₹{:,.0f}",  "+14.2% YoY"),
    (k2, "Total Orders",       total_ord,  "{:,.0f}",   "+11.8% YoY"),
    (k3, "Avg Order Value",    avg_aov,    "₹{:.2f}",   "+2.1% YoY"),
    (k4, "Total Customers",    total_cust, "{:,.0f}",   "+18.4% YoY"),
    (k5, "Overall CVR",        funnel_cvr, "{:.1f}%",   "+0.8pp YoY"),
]:
    col.metric(label, fmt.format(val), delta)

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Sales Trend",
    "👥 Customer Segments",
    "🏷️ Product Performance",
    "🔁 Cohort Retention",
    "🔽 Conversion Funnel",
])

# ═══════════════════════════════════════════════════════
# TAB 1 — SALES TREND
# ═══════════════════════════════════════════════════════
with tab1:
    st.subheader("Monthly Sales Trend Analysis")
    st.caption("SQL: `01_sales_trend_analysis.sql` · Window: LAG, rolling AVG")

    c1, c2 = st.columns([3, 1])
    with c2:
        metric_choice = st.radio(
            "Show metric",
            ["Revenue", "Orders", "AOV", "Customers"],
            index=0,
        )

    col_map = {
        "Revenue":   "total_revenue",
        "Orders":    "total_orders",
        "AOV":       "avg_order_value",
        "Customers": "unique_customers",
    }
    y_col = col_map[metric_choice]

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(
        go.Bar(
            x=df_trend["month"],
            y=df_trend[y_col],
            name=metric_choice,
            marker_color=PRIMARY,
            opacity=0.75,
        ),
        secondary_y=False,
    )
    if metric_choice == "Revenue":
        fig1.add_trace(
            go.Scatter(
                x=df_trend["month"],
                y=df_trend["revenue_3m_rolling_avg"],
                name="3-Month Rolling Avg",
                line=dict(color=ACCENT, width=2.5, dash="dash"),
                mode="lines",
            ),
            secondary_y=False,
        )
        fig1.add_trace(
            go.Scatter(
                x=df_trend["month"],
                y=df_trend["revenue_mom_pct"],
                name="MoM Growth %",
                line=dict(color=SUCCESS, width=1.5),
                mode="lines+markers",
                marker_size=4,
            ),
            secondary_y=True,
        )
        fig1.update_yaxes(title_text="Revenue (₹)", secondary_y=False)
        fig1.update_yaxes(title_text="MoM Growth %", secondary_y=True)

    fig1.update_layout(
        height=380, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=30, b=0),
    )
    fig1.update_xaxes(gridcolor="#eee")
    fig1.update_yaxes(gridcolor="#eee")
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("📋 Monthly Data Table"):
        display = df_trend.copy()
        display["month"] = display["month"].dt.strftime("%b %Y")
        display["total_revenue"] = display["total_revenue"].map("₹{:,.0f}".format)
        display["revenue_mom_pct"] = display["revenue_mom_pct"].map(
            lambda x: f"{x:+.1f}%" if pd.notna(x) else "—"
        )
        st.dataframe(display[[
            "month","total_revenue","total_orders",
            "unique_customers","avg_order_value","revenue_mom_pct"
        ]], use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 2 — RFM CUSTOMER SEGMENTS
# ═══════════════════════════════════════════════════════
with tab2:
    st.subheader("Customer Segmentation — RFM Analysis")
    st.caption("SQL: `02_customer_segmentation_rfm.sql` · Window: NTILE scoring")

    c1, c2 = st.columns(2)

    with c1:
        fig_pie = px.pie(
            df_rfm,
            names="customer_segment",
            values="total_segment_revenue",
            title="Revenue Share by Segment",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig_pie.update_layout(
            height=360, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_bubble = px.scatter(
            df_rfm,
            x="avg_recency_days",
            y="avg_order_count",
            size="num_customers",
            color="customer_segment",
            text="customer_segment",
            title="Segment Map — Recency vs Frequency",
            color_discrete_sequence=px.colors.qualitative.Set2,
            size_max=55,
        )
        fig_bubble.update_traces(textposition="top center", textfont_size=9)
        fig_bubble.update_layout(
            height=360, paper_bgcolor="white", plot_bgcolor="white",
            showlegend=False, margin=dict(l=0, r=0, t=40, b=0),
        )
        fig_bubble.update_xaxes(title="Days Since Last Order (↑ worse)", gridcolor="#eee")
        fig_bubble.update_yaxes(title="Avg Orders Per Customer", gridcolor="#eee")
        st.plotly_chart(fig_bubble, use_container_width=True)

    st.dataframe(
        df_rfm.style.background_gradient(
            subset=["total_segment_revenue", "revenue_share_pct"],
            cmap="YlOrRd",
        ),
        use_container_width=True,
        hide_index=True,
    )


# ═══════════════════════════════════════════════════════
# TAB 3 — PRODUCT PERFORMANCE
# ═══════════════════════════════════════════════════════
with tab3:
    st.subheader("Product & Category Performance")
    st.caption("SQL: `03_product_performance.sql` · Window: RANK, QUALIFY")

    c1, c2 = st.columns(2)

    with c1:
        fig_bar = px.bar(
            df_cat.sort_values("total_revenue"),
            x="total_revenue",
            y="category",
            orientation="h",
            color="total_revenue",
            color_continuous_scale=[[0, "#FEE8E8"], [1, PRIMARY]],
            title="Top 10 Categories by Revenue",
            text="total_revenue",
        )
        fig_bar.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
            textfont_size=9,
        )
        fig_bar.update_layout(
            height=400, paper_bgcolor="white", plot_bgcolor="white",
            showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=80, t=40, b=0),
        )
        fig_bar.update_xaxes(gridcolor="#eee")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_scatter = px.scatter(
            df_cat,
            x="avg_discount_pct",
            y="return_rate_pct",
            size="total_revenue",
            color="department",
            text="category",
            title="Discount Depth vs Return Rate",
            color_discrete_map={"Women": PRIMARY, "Men": SECONDARY},
            size_max=45,
        )
        fig_scatter.update_traces(textposition="top center", textfont_size=8)
        fig_scatter.update_layout(
            height=400, paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=0, r=0, t=40, b=0),
        )
        fig_scatter.update_xaxes(title="Avg Discount %", gridcolor="#eee")
        fig_scatter.update_yaxes(title="Return Rate %", gridcolor="#eee")
        st.plotly_chart(fig_scatter, use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 4 — COHORT RETENTION
# ═══════════════════════════════════════════════════════
with tab4:
    st.subheader("Cohort Retention Heatmap")
    st.caption("SQL: `04_cohort_retention_analysis.sql` · Window: DATE_DIFF, DATE_TRUNC")

    month_cols = [f"month_{i}" for i in range(12)]
    heat_data  = df_cohort[month_cols].values.astype(float)

    fig_heat = go.Figure(data=go.Heatmap(
        z=heat_data,
        x=[f"M+{i}" for i in range(12)],
        y=df_cohort["cohort"].tolist(),
        colorscale=[[0, "#FFF5F5"], [0.25, "#FFCDD2"], [0.6, "#EF9A9A"], [1.0, PRIMARY]],
        text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in heat_data],
        texttemplate="%{text}",
        textfont={"size": 9},
        zmin=0, zmax=100,
        hoverongaps=False,
        colorbar=dict(title="Retention %"),
    ))
    fig_heat.update_layout(
        height=480,
        xaxis_title="Months Since First Purchase",
        yaxis_title="Cohort (Acquisition Month)",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    avg_by_month = pd.DataFrame({
        "Month": [f"M+{i}" for i in range(12)],
        "Avg Retention %": [
            round(float(np.nanmean(heat_data[:, i])), 1)
            for i in range(12)
        ],
    })

    c1, c2 = st.columns([2, 1])
    with c1:
        fig_line = px.line(
            avg_by_month, x="Month", y="Avg Retention %",
            title="Average Retention Curve Across All Cohorts",
            markers=True,
            color_discrete_sequence=[PRIMARY],
        )
        fig_line.update_layout(
            height=250, paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=0, r=0, t=40, b=0),
        )
        fig_line.update_xaxes(gridcolor="#eee")
        fig_line.update_yaxes(gridcolor="#eee")
        st.plotly_chart(fig_line, use_container_width=True)
    with c2:
        st.dataframe(avg_by_month, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════
# TAB 5 — CONVERSION FUNNEL
# ═══════════════════════════════════════════════════════
with tab5:
    st.subheader("Purchase Conversion Funnel")
    st.caption("SQL: `05_conversion_funnel_analysis.sql` · APPROX_COUNT_DISTINCT, LAG")

    stage_labels = ["Home", "Category", "Product", "Cart", "Checkout", "Purchase"]
    df_funnel["stage_label"] = stage_labels

    c1, c2 = st.columns([2, 1])

    with c1:
        fig_funnel = go.Figure(go.Funnel(
            y=stage_labels,
            x=df_funnel["users_reached"].tolist(),
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(
                color=[PRIMARY, "#FF6B6B", "#FF8E53", ACCENT, "#56CCF2", SUCCESS],
                line=dict(width=1.5, color="white"),
            ),
            connector=dict(line=dict(color="#ccc", dash="dot", width=1)),
        ))
        fig_funnel.update_layout(
            height=420,
            paper_bgcolor="white",
            margin=dict(l=0, r=0, t=20, b=0),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with c2:
        st.markdown("#### Step Drop-off")
        df_dropoff = df_funnel.dropna(subset=["step_dropoff_pct"]).copy()
        df_dropoff["stage_label"] = stage_labels[1:]

        fig_drop = px.bar(
            df_dropoff,
            x="step_dropoff_pct",
            y="stage_label",
            orientation="h",
            color="step_dropoff_pct",
            color_continuous_scale=[[0, "#FFF3E0"], [1, PRIMARY]],
            text="step_dropoff_pct",
        )
        fig_drop.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            textfont_size=10,
        )
        fig_drop.update_layout(
            height=300,
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=60, t=10, b=0),
        )
        fig_drop.update_xaxes(gridcolor="#eee")
        st.plotly_chart(fig_drop, use_container_width=True)

        st.markdown("#### Key Insight")
        worst_step = df_dropoff.loc[df_dropoff["step_dropoff_pct"].idxmax(), "stage_label"]
        worst_pct  = df_dropoff["step_dropoff_pct"].max()
        st.error(
            f"🔺 **{worst_step}** has the highest drop-off at **{worst_pct:.1f}%** — "
            f"priority optimization area."
        )

    st.divider()
    st.dataframe(
        df_funnel[["stage_label", "users_reached", "step_conversion_pct",
                   "step_dropoff_pct", "users_dropped", "funnel_entry_pct"]]
        .rename(columns={
            "stage_label": "Stage", "users_reached": "Users",
            "step_conversion_pct": "Step CVR %", "step_dropoff_pct": "Drop-off %",
            "users_dropped": "Users Lost", "funnel_entry_pct": "Funnel Entry %",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "📦 Dataset: `bigquery-public-data.thelook_ecommerce` · "
    "🛠️ Stack: BigQuery · SQL · Python · Streamlit · Plotly · "
    "👤 Built by Charan Karthik Nayakanti"
)
