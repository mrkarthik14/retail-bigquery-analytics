/*
============================================================
  QUERY 04 — COHORT RETENTION ANALYSIS
  Dataset : bigquery-public-data.thelook_ecommerce
  Purpose : Group customers by their first purchase month
            (cohort), then track what % return in each
            subsequent month (months 0–11).
            Output feeds the retention heatmap.
============================================================
*/

WITH

-- Step 1: Identify each user's first purchase month (cohort assignment)
first_orders AS (
  SELECT
    user_id,
    DATE_TRUNC(MIN(created_at), MONTH)          AS cohort_month
  FROM
    `bigquery-public-data.thelook_ecommerce.orders`
  WHERE
    status = 'Complete'
  GROUP BY
    user_id
),

-- Step 2: All orders per user with their cohort month attached
user_orders AS (
  SELECT
    o.user_id,
    fo.cohort_month,
    DATE_TRUNC(o.created_at, MONTH)             AS order_month,

    -- Month index: 0 = cohort month, 1 = 1 month later, etc.
    DATE_DIFF(
      DATE_TRUNC(o.created_at, MONTH),
      fo.cohort_month,
      MONTH
    )                                           AS month_index
  FROM
    `bigquery-public-data.thelook_ecommerce.orders` AS o
    INNER JOIN first_orders AS fo
      ON o.user_id = fo.user_id
  WHERE
    o.status = 'Complete'
    AND fo.cohort_month >= '2022-01-01'
),

-- Step 3: Count distinct active users per cohort × month_index
cohort_activity AS (
  SELECT
    cohort_month,
    month_index,
    COUNT(DISTINCT user_id)                     AS active_users
  FROM
    user_orders
  WHERE
    month_index BETWEEN 0 AND 11               -- track up to 12 months
  GROUP BY
    cohort_month, month_index
),

-- Step 4: Cohort sizes (= users active at month_index 0)
cohort_sizes AS (
  SELECT
    cohort_month,
    active_users                                AS cohort_size
  FROM
    cohort_activity
  WHERE
    month_index = 0
),

-- Step 5: Compute retention rate
retention AS (
  SELECT
    ca.cohort_month,
    ca.month_index,
    ca.active_users,
    cs.cohort_size,
    ROUND(ca.active_users / cs.cohort_size * 100, 2)  AS retention_rate_pct
  FROM
    cohort_activity AS ca
    INNER JOIN cohort_sizes AS cs
      ON ca.cohort_month = cs.cohort_month
)

-- Final: Wide pivot format using conditional aggregation
-- Each column = one month index (0–11)
SELECT
  FORMAT_DATE('%b %Y', cohort_month)           AS cohort,
  cohort_size,

  MAX(IF(month_index = 0,  retention_rate_pct, NULL)) AS month_0,
  MAX(IF(month_index = 1,  retention_rate_pct, NULL)) AS month_1,
  MAX(IF(month_index = 2,  retention_rate_pct, NULL)) AS month_2,
  MAX(IF(month_index = 3,  retention_rate_pct, NULL)) AS month_3,
  MAX(IF(month_index = 4,  retention_rate_pct, NULL)) AS month_4,
  MAX(IF(month_index = 5,  retention_rate_pct, NULL)) AS month_5,
  MAX(IF(month_index = 6,  retention_rate_pct, NULL)) AS month_6,
  MAX(IF(month_index = 7,  retention_rate_pct, NULL)) AS month_7,
  MAX(IF(month_index = 8,  retention_rate_pct, NULL)) AS month_8,
  MAX(IF(month_index = 9,  retention_rate_pct, NULL)) AS month_9,
  MAX(IF(month_index = 10, retention_rate_pct, NULL)) AS month_10,
  MAX(IF(month_index = 11, retention_rate_pct, NULL)) AS month_11

FROM
  retention
GROUP BY
  cohort_month, cohort_size
ORDER BY
  cohort_month;
