-- NOTE: island_group IS NOT NULL filters out Rice, Sugar, and Flour because
-- their actual-price records are national averages (market_id=974, admin1='NATIONAL')
-- which have no island group mapping. Only Cooking Oil has market-level actual
-- prices with geographic coordinates. See _marts__models.yml column docs.
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
  ROUND((a.avg_price_idr / NULLIF(j.java_avg_price, 0)) * 100, 2) AS price_index_vs_java,
  ROUND(
    (a.avg_price_idr / NULLIF(j.java_avg_price, 0)) * 100
    - LAG((a.avg_price_idr / NULLIF(j.java_avg_price, 0)) * 100)
      OVER (
        PARTITION BY a.commodity_consolidated, a.island_group, a.admin1
        ORDER BY a.year
      ),
    2
  ) AS yoy_change_index
FROM annual_prices a
LEFT JOIN java_baseline j
  ON a.year = j.year
  AND a.commodity_consolidated = j.commodity_consolidated
ORDER BY a.year, a.commodity_consolidated, a.island_group, a.admin1
