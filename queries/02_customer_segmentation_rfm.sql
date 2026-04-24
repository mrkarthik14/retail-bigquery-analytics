/*
============================================================
  QUERY 02 — CUSTOMER SEGMENTATION (RFM ANALYSIS)
  Dataset : bigquery-public-data.thelook_ecommerce
  Purpose : Score every customer on Recency, Frequency,
            and Monetary value, then label them into
            actionable segments (Champion, Loyal,
            At-Risk, Lost, etc.)
============================================================
*/

WITH

-- Step 1: Reference date for recency calculation
params AS (
  SELECT DATE('2024-04-01') AS analysis_date
),

-- Step 2: Build per-customer aggregates
customer_orders AS (
  SELECT
    o.user_id,
    MAX(DATE(o.created_at))                              AS last_order_date,
    COUNT(DISTINCT o.order_id)                           AS order_count,
    ROUND(SUM(oi.sale_price), 2)                         AS total_spend
  FROM
    `bigquery-public-data.thelook_ecommerce.orders`           AS o
    INNER JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi
      ON o.order_id = oi.order_id
  WHERE
    o.status = 'Complete'
  GROUP BY
    o.user_id
),

-- Step 3: Compute R, F, M raw values
rfm_raw AS (
  SELECT
    co.user_id,
    DATE_DIFF(p.analysis_date, co.last_order_date, DAY)  AS recency_days,
    co.order_count                                        AS frequency,
    co.total_spend                                        AS monetary
  FROM
    customer_orders co
    CROSS JOIN params p
),

-- Step 4: Score R, F, M on 1–4 scale using NTILE
rfm_scores AS (
  SELECT
    user_id,
    recency_days,
    frequency,
    monetary,

    -- Recency: lower days = better = higher score
    5 - NTILE(4) OVER (ORDER BY recency_days ASC)    AS r_score,

    -- Frequency: higher count = better = higher score
    NTILE(4) OVER (ORDER BY frequency ASC)           AS f_score,

    -- Monetary: higher spend = better = higher score
    NTILE(4) OVER (ORDER BY monetary ASC)            AS m_score
  FROM
    rfm_raw
),

-- Step 5: Combine into RFM total score and segment label
rfm_labeled AS (
  SELECT
    user_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score)                        AS rfm_total,

    CASE
      WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champion'
      WHEN r_score >= 3 AND f_score >= 3                  THEN 'Loyal Customer'
      WHEN r_score >= 3 AND f_score <= 2                  THEN 'Potential Loyalist'
      WHEN r_score >= 4 AND f_score = 1                   THEN 'New Customer'
      WHEN r_score = 2 AND f_score >= 3                   THEN 'At Risk'
      WHEN r_score = 2 AND f_score <= 2                   THEN 'Needs Attention'
      WHEN r_score = 1 AND f_score >= 3                   THEN 'Cannot Lose Them'
      WHEN r_score = 1 AND f_score = 1                    THEN 'Lost'
      ELSE 'Others'
    END AS customer_segment
  FROM
    rfm_scores
)

-- Final: Segment summary with user-level detail
SELECT
  customer_segment,
  COUNT(user_id)                          AS num_customers,
  ROUND(AVG(recency_days), 1)             AS avg_recency_days,
  ROUND(AVG(frequency), 2)               AS avg_order_count,
  ROUND(AVG(monetary), 2)                AS avg_spend,
  ROUND(SUM(monetary), 2)                AS total_segment_revenue,
  ROUND(
    SUM(monetary) / SUM(SUM(monetary)) OVER () * 100,
  2)                                      AS revenue_share_pct
FROM
  rfm_labeled
GROUP BY
  customer_segment
ORDER BY
  total_segment_revenue DESC;
