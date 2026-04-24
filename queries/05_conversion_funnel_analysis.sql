/*
============================================================
  QUERY 05 — CONVERSION FUNNEL ANALYSIS
  Dataset : bigquery-public-data.thelook_ecommerce
  Purpose : Measure how many users progress through each
            stage of the purchase funnel (home → browse
            → product → cart → checkout → purchase),
            and quantify drop-off at every step.
============================================================
*/

WITH

-- Step 1: Assign a canonical funnel order to event types
funnel_stages AS (
  SELECT stage_name, stage_order FROM UNNEST([
    STRUCT('home'         AS stage_name, 1 AS stage_order),
    STRUCT('category'     AS stage_name, 2 AS stage_order),
    STRUCT('product'      AS stage_name, 3 AS stage_order),
    STRUCT('cart'         AS stage_name, 4 AS stage_order),
    STRUCT('checkout'     AS stage_name, 5 AS stage_order),
    STRUCT('purchase'     AS stage_name, 6 AS stage_order)
  ])
),

-- Step 2: Deduplicate events — one row per user per stage
--         (a user may trigger the same event multiple times)
user_events AS (
  SELECT DISTINCT
    user_id,
    event_type                                  AS stage_name
  FROM
    `bigquery-public-data.thelook_ecommerce.events`
  WHERE
    event_type IN ('home', 'category', 'product', 'cart', 'checkout', 'purchase')
    AND created_at >= '2022-01-01'
),

-- Step 3: Count unique users who reached each stage
stage_counts AS (
  SELECT
    fs.stage_order,
    fs.stage_name,
    APPROX_COUNT_DISTINCT(ue.user_id)           AS users_reached
  FROM
    funnel_stages AS fs
    LEFT JOIN user_events AS ue
      ON fs.stage_name = ue.stage_name
  GROUP BY
    fs.stage_order, fs.stage_name
),

-- Step 4: Add previous-stage user count for drop-off calculation
funnel_with_dropoff AS (
  SELECT
    stage_order,
    stage_name,
    users_reached,

    -- Users at the stage immediately before this one
    LAG(users_reached) OVER (ORDER BY stage_order)  AS prev_stage_users,

    -- Entry rate: % of top-of-funnel (stage 1) users who reached this stage
    ROUND(
      users_reached
      / FIRST_VALUE(users_reached) OVER (ORDER BY stage_order) * 100,
    2)                                          AS funnel_entry_pct

  FROM
    stage_counts
)

-- Final output
SELECT
  stage_order,
  stage_name                                    AS funnel_stage,
  users_reached,
  prev_stage_users,
  funnel_entry_pct,

  -- Step-to-step conversion rate
  ROUND(
    users_reached / NULLIF(prev_stage_users, 0) * 100,
  2)                                            AS step_conversion_pct,

  -- Users lost at this specific step
  COALESCE(prev_stage_users - users_reached, 0) AS users_dropped,

  -- Drop-off % relative to the previous step
  ROUND(
    COALESCE(prev_stage_users - users_reached, 0)
    / NULLIF(prev_stage_users, 0) * 100,
  2)                                            AS step_dropoff_pct

FROM
  funnel_with_dropoff
ORDER BY
  stage_order;
