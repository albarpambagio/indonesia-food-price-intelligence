SELECT
  month,
  commodity_consolidated,
  COUNT(DISTINCT market_id) AS market_count,
  AVG(price_idr) AS avg_price_idr,
  AVG(price_usd) AS avg_price_usd,
  MIN(price_idr) AS min_price_idr,
  MAX(price_idr) AS max_price_idr
FROM {{ ref('int_prices_normalised') }}
WHERE commodity_consolidated IS NOT NULL
  AND price_idr > 0
  AND unit IS NOT NULL
  AND EXTRACT(YEAR FROM month) BETWEEN 2007 AND 2024
GROUP BY
  month,
  commodity_consolidated
ORDER BY
  month,
  commodity_consolidated
