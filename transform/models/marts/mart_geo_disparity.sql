WITH prices AS (
  SELECT
    DATE_TRUNC('month', date) AS month,
    EXTRACT(YEAR FROM date) AS year,
    commodity_consolidated,
    island_group,
    admin1,
    price_idr
  FROM {{ ref('int_prices_normalised') }}
  WHERE filter_out = FALSE
    AND price_flag = 'actual'
    AND commodity_consolidated IS NOT NULL
    AND island_group IS NOT NULL
),

annual_prices AS (
  SELECT
    year,
    commodity_consolidated,
    island_group,
    admin1,
    AVG(price_idr) AS avg_price_idr,
    COUNT(DISTINCT month) AS months_with_data
  FROM prices
  GROUP BY year, commodity_consolidated, island_group, admin1
),

java_baseline AS (
  SELECT
    year,
    commodity_consolidated,
    AVG(avg_price_idr) AS java_avg_price
  FROM annual_prices
  WHERE island_group = 'Java'
  GROUP BY year, commodity_consolidated
)

SELECT
  a.year,
  a.commodity_consolidated,
  a.island_group,
  a.admin1,
  a.avg_price_idr,
  a.months_with_data,
  j.java_avg_price,
  ROUND((a.avg_price_idr / NULLIF(j.java_avg_price, 0)) * 100, 2) AS price_index_vs_java
FROM annual_prices a
LEFT JOIN java_baseline j
  ON a.year = j.year
  AND a.commodity_consolidated = j.commodity_consolidated
ORDER BY a.year, a.commodity_consolidated, a.island_group, a.admin1
