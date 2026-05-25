SELECT
  date,
  admin1,
  admin2,
  market,
  market_id,
  latitude,
  longitude,
  commodity,
  commodity_id,
  unit,
  price_flag,
  pricetype,
  currency,
  price,
  usdprice,
  CASE
    WHEN commodity IN ('Oil (vegetable)', 'Oil (vegetable, bulk)', 'Oil (vegetable, packaged)') THEN 'Cooking Oil'
    WHEN commodity IN ('Sugar', 'Sugar (premium)') THEN 'Sugar'
    WHEN commodity = 'Rice' THEN 'Rice'
    WHEN commodity = 'Wheat flour' THEN 'Flour'
    ELSE NULL
  END AS commodity_consolidated
FROM {{ ref('stg_food_prices') }}
