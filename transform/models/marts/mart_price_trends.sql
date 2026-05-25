SELECT
  DATE_TRUNC('month', date) AS month,
  commodity_consolidated,
  island_group,
  admin1,
  COUNT(DISTINCT market_id) AS market_count,
  AVG(price_idr) AS avg_price_idr,
  AVG(price_usd) AS avg_price_usd,
  MIN(price_idr) AS min_price_idr,
  MAX(price_idr) AS max_price_idr
FROM {{ ref('int_prices_normalised') }}
WHERE filter_out = FALSE
  AND price_flag = 'actual'
  AND commodity_consolidated IS NOT NULL
  AND island_group IS NOT NULL
GROUP BY
  DATE_TRUNC('month', date),
  commodity_consolidated,
  island_group,
  admin1
ORDER BY
  month,
  commodity_consolidated,
  island_group,
  admin1
