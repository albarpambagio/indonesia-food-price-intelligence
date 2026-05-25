WITH prices AS (
  SELECT
    month,
    commodity_consolidated,
    island_group,
    price_idr
  FROM {{ ref('int_prices_normalised') }}
  WHERE filter_out = FALSE
    AND price_flag = 'actual'
    AND commodity_consolidated IS NOT NULL
    AND island_group IS NOT NULL
),

monthly_avg AS (
  SELECT
    month,
    commodity_consolidated,
    island_group,
    AVG(price_idr) AS avg_price
  FROM prices
  GROUP BY month, commodity_consolidated, island_group
),

annual_avg AS (
  SELECT
    EXTRACT(YEAR FROM month) AS year,
    commodity_consolidated,
    island_group,
    AVG(avg_price) AS annual_avg_price
  FROM monthly_avg
  GROUP BY year, commodity_consolidated, island_group
),

with_index AS (
  SELECT
    m.month,
    m.commodity_consolidated,
    m.island_group,
    m.avg_price,
    a.annual_avg_price,
    ROUND((m.avg_price / NULLIF(a.annual_avg_price, 0)) * 100, 2) AS price_index,
    EXTRACT(MONTH FROM m.month) AS month_of_year,
    CASE WHEN EXTRACT(MONTH FROM m.month) IN (3, 4) THEN TRUE ELSE FALSE END AS flag_harvest_mar_apr,
    CASE WHEN EXTRACT(MONTH FROM m.month) IN (8, 9) THEN TRUE ELSE FALSE END AS flag_harvest_aug_sep,
    CASE WHEN EXTRACT(MONTH FROM m.month) IN (11, 12) THEN TRUE ELSE FALSE END AS flag_year_end
  FROM monthly_avg m
  LEFT JOIN annual_avg a
    ON EXTRACT(YEAR FROM m.month) = a.year
    AND m.commodity_consolidated = a.commodity_consolidated
    AND m.island_group = a.island_group
),

ramadan AS (
  SELECT
    STRFTIME(m.month, '%Y-%m') AS ym,
    m.commodity_consolidated,
    m.island_group,
    CASE WHEN STRFTIME(m.month, '%Y-%m') = c.eid_month THEN TRUE ELSE FALSE END AS flag_ramadan_eid_month,
    CASE WHEN STRFTIME(m.month, '%Y-%m') = c.t_minus_1 THEN TRUE ELSE FALSE END AS flag_ramadan_t_minus_1,
    CASE WHEN STRFTIME(m.month, '%Y-%m') = c.t_minus_2 THEN TRUE ELSE FALSE END AS flag_ramadan_t_minus_2,
    CASE WHEN STRFTIME(m.month, '%Y-%m') = c.t_minus_3 THEN TRUE ELSE FALSE END AS flag_ramadan_t_minus_3,
    CASE WHEN STRFTIME(m.month, '%Y-%m') = c.t_plus_1 THEN TRUE ELSE FALSE END AS flag_ramadan_t_plus_1
  FROM monthly_avg m
  LEFT JOIN {{ ref('int_islamic_calendar') }} c
    ON EXTRACT(YEAR FROM m.month) = c.year
)

SELECT
  wi.*,
  COALESCE(r.flag_ramadan_eid_month, FALSE) AS flag_ramadan_eid_month,
  COALESCE(r.flag_ramadan_t_minus_1, FALSE) AS flag_ramadan_t_minus_1,
  COALESCE(r.flag_ramadan_t_minus_2, FALSE) AS flag_ramadan_t_minus_2,
  COALESCE(r.flag_ramadan_t_minus_3, FALSE) AS flag_ramadan_t_minus_3,
  COALESCE(r.flag_ramadan_t_plus_1, FALSE) AS flag_ramadan_t_plus_1
FROM with_index wi
LEFT JOIN ramadan r
  ON STRFTIME(wi.month, '%Y-%m') = r.ym
  AND wi.commodity_consolidated = r.commodity_consolidated
  AND wi.island_group = r.island_group
ORDER BY wi.month, wi.commodity_consolidated, wi.island_group
