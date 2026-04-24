/*
============================================================
  QUERY 03 — PRODUCT PERFORMANCE ANALYSIS
  Dataset : bigquery-public-data.thelook_ecommerce
  Purpose : Rank categories and individual SKUs by
            revenue, units sold, and return rate.
            Identify top performers and underperformers
            using window-based ranking.
============================================================
*/

WITH

-- Step 1: Join order items with product metadata
item_detail AS (
  SELECT
    oi.order_id,
    oi.product_id,
    oi.sale_price,
    oi.status                                   AS item_status,
    p.name                                      AS product_name,
    p.category,
    p.brand,
    p.department,
    p.retail_price,
    DATE_TRUNC(oi.created_at, MONTH)            AS order_month
  FROM
    `bigquery-public-data.thelook_ecommerce.order_items` AS oi
    INNER JOIN `bigquery-public-data.thelook_ecommerce.products`    AS p
      ON oi.product_id = p.id
  WHERE
    oi.created_at >= '2022-01-01'
),

-- Step 2: Category-level aggregation
category_metrics AS (
  SELECT
    category,
    department,
    COUNT(DISTINCT order_id)                    AS total_orders,
    COUNT(product_id)                           AS units_sold,
    ROUND(SUM(sale_price), 2)                   AS total_revenue,
    ROUND(AVG(sale_price), 2)                   AS avg_sale_price,
    ROUND(AVG(retail_price), 2)                 AS avg_retail_price,

    -- Discount depth
    ROUND(
      (1 - AVG(sale_price) / NULLIF(AVG(retail_price), 0)) * 100,
    2)                                          AS avg_discount_pct,

    -- Return rate
    ROUND(
      COUNTIF(item_status = 'Returned')
      / NULLIF(COUNT(product_id), 0) * 100,
    2)                                          AS return_rate_pct
  FROM
    item_detail
  GROUP BY
    category, department
),

-- Step 3: Rank categories within each department by revenue
category_ranked AS (
  SELECT
    *,
    RANK() OVER (
      PARTITION BY department
      ORDER BY total_revenue DESC
    )                                           AS dept_revenue_rank,

    ROUND(
      total_revenue / SUM(total_revenue) OVER () * 100,
    2)                                          AS revenue_share_pct
  FROM
    category_metrics
),

-- Step 4: SKU-level aggregation (top products)
product_metrics AS (
  SELECT
    product_id,
    product_name,
    category,
    brand,
    COUNT(DISTINCT order_id)                    AS total_orders,
    COUNT(product_id)                           AS units_sold,
    ROUND(SUM(sale_price), 2)                   AS total_revenue,
    ROUND(AVG(sale_price), 2)                   AS avg_sale_price,
    ROUND(
      COUNTIF(item_status = 'Returned')
      / NULLIF(COUNT(product_id), 0) * 100,
    2)                                          AS return_rate_pct
  FROM
    item_detail
  GROUP BY
    product_id, product_name, category, brand
),

-- Step 5: Use QUALIFY to get top 5 products per category
top_products_per_category AS (
  SELECT
    *,
    RANK() OVER (
      PARTITION BY category
      ORDER BY total_revenue DESC
    )                                           AS category_rank
  FROM
    product_metrics
  QUALIFY
    RANK() OVER (
      PARTITION BY category
      ORDER BY total_revenue DESC
    ) <= 5
)

-- Output 1: Category summary (use for dashboard)
SELECT
  'category_summary'                            AS result_type,
  category,
  department,
  total_orders,
  units_sold,
  total_revenue,
  avg_sale_price,
  avg_discount_pct,
  return_rate_pct,
  dept_revenue_rank,
  revenue_share_pct,
  NULL AS product_name,
  NULL AS brand,
  NULL AS category_rank
FROM
  category_ranked
WHERE
  dept_revenue_rank <= 10

UNION ALL

-- Output 2: Top SKUs per category
SELECT
  'top_products'                                AS result_type,
  category,
  NULL                                          AS department,
  total_orders,
  units_sold,
  total_revenue,
  avg_sale_price,
  NULL                                          AS avg_discount_pct,
  return_rate_pct,
  NULL                                          AS dept_revenue_rank,
  NULL                                          AS revenue_share_pct,
  product_name,
  brand,
  category_rank
FROM
  top_products_per_category
ORDER BY
  result_type, total_revenue DESC;
