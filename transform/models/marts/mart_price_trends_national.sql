SELECT
  month,
  commodity_consolidated,
  COUNT(DISTINCT market_id) AS market_count,
  AVG(price_idr) AS avg_price_idr,
  AVG(price_usd) AS avg_price_usd,
  MIN(price_idr) AS min_price_idr,
  MAX(price_idr) AS max_price_idr
FROM {{ ref('int_prices_normalised') }}
WHERE filter_out = FALSE
  AND price_flag = 'actual'
  AND commodity_consolidated IS NOT NULL
GROUP BY
  month,
  commodity_consolidated
ORDER BY
  month,
  commodity_consolidated
