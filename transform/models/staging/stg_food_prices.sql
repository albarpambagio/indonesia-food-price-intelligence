SELECT
  CAST(date AS DATE) AS date,
  UPPER(TRIM(admin1)) AS admin1,
  UPPER(TRIM(admin2)) AS admin2,
  TRIM(market) AS market,
  market_id,
  CAST(latitude AS FLOAT) AS latitude,
  CAST(longitude AS FLOAT) AS longitude,
  TRIM(category) AS category,
  TRIM(commodity) AS commodity,
  commodity_id,
  TRIM(unit) AS unit,
  priceflag AS price_flag,
  TRIM(pricetype) AS pricetype,
  TRIM(currency) AS currency,
  CAST(price AS DECIMAL(16, 2)) AS price,
  CAST(usdprice AS DECIMAL(16, 4)) AS usdprice
FROM {{ source('raw', 'food_prices') }}
WHERE price > 0
