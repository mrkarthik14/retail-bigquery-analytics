/*
============================================================
  QUERY 01 — MONTHLY SALES TREND ANALYSIS
  Dataset : bigquery-public-data.thelook_ecommerce
  Purpose : Track revenue, order volume, AOV, and MoM
            growth rate to identify seasonal patterns
            and performance trends.
============================================================
*/

WITH

-- Step 1: Clean completed orders only
completed_orders AS (
  SELECT
    o.order_id,
    o.user_id,
    DATE_TRUNC(o.created_at, MONTH)        AS order_month,
    oi.sale_price,
    oi.product_id
  FROM
    `bigquery-public-data.thelook_ecommerce.orders`           AS o
    INNER JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi
      ON o.order_id = oi.order_id
  WHERE
    o.status    = 'Complete'
    AND o.created_at >= '2022-01-01'
),

-- Step 2: Aggregate to monthly metrics
monthly_metrics AS (
  SELECT
    order_month,
    COUNT(DISTINCT order_id)                           AS total_orders,
    COUNT(DISTINCT user_id)                            AS unique_customers,
    ROUND(SUM(sale_price), 2)                          AS total_revenue,
    ROUND(SUM(sale_price) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
    COUNT(product_id)                                  AS total_items_sold
  FROM
    completed_orders
  GROUP BY
    order_month
),

-- Step 3: Compute MoM growth using LAG window function
growth_metrics AS (
  SELECT
    order_month,
    total_orders,
    unique_customers,
    total_revenue,
    avg_order_value,
    total_items_sold,

    -- Revenue MoM growth %
    ROUND(
      (total_revenue - LAG(total_revenue) OVER (ORDER BY order_month))
      / NULLIF(LAG(total_revenue) OVER (ORDER BY order_month), 0) * 100,
    2) AS revenue_mom_pct,

    -- Order volume MoM growth %
    ROUND(
      (total_orders - LAG(total_orders) OVER (ORDER BY order_month))
      / NULLIF(LAG(total_orders) OVER (ORDER BY order_month), 0) * 100,
    2) AS orders_mom_pct,

    -- 3-month rolling average revenue (smooths seasonality)
    ROUND(
      AVG(total_revenue) OVER (
        ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
      ),
    2) AS revenue_3m_rolling_avg

  FROM
    monthly_metrics
)

-- Final output
SELECT
  FORMAT_DATE('%b %Y', order_month)  AS month,
  total_orders,
  unique_customers,
  total_revenue,
  avg_order_value,
  total_items_sold,
  revenue_mom_pct,
  orders_mom_pct,
  revenue_3m_rolling_avg
FROM
  growth_metrics
ORDER BY
  order_month;
