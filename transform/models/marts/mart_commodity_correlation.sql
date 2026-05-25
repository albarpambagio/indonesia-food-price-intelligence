WITH national_prices AS (
  SELECT
    DATE_TRUNC('month', date) AS month,
    commodity_consolidated,
    AVG(price_idr) AS national_avg_price
  FROM {{ ref('int_prices_normalised') }}
  WHERE filter_out = FALSE
    AND price_flag = 'actual'
    AND commodity_consolidated IS NOT NULL
  GROUP BY DATE_TRUNC('month', date), commodity_consolidated
),

pivoted AS (
  SELECT
    month,
    MAX(CASE WHEN commodity_consolidated = 'Rice' THEN national_avg_price END) AS rice_price,
    MAX(CASE WHEN commodity_consolidated = 'Cooking Oil' THEN national_avg_price END) AS oil_price,
    MAX(CASE WHEN commodity_consolidated = 'Sugar' THEN national_avg_price END) AS sugar_price,
    MAX(CASE WHEN commodity_consolidated = 'Flour' THEN national_avg_price END) AS flour_price
  FROM national_prices
  GROUP BY month
),

lagged AS (
  SELECT
    month,
    rice_price,
    oil_price,
    sugar_price,
    flour_price,
    LAG(rice_price, 1) OVER (ORDER BY month) AS rice_lag1,
    LAG(rice_price, 2) OVER (ORDER BY month) AS rice_lag2,
    LAG(rice_price, 3) OVER (ORDER BY month) AS rice_lag3,
    LAG(oil_price, 1) OVER (ORDER BY month) AS oil_lag1,
    LAG(oil_price, 2) OVER (ORDER BY month) AS oil_lag2,
    LAG(oil_price, 3) OVER (ORDER BY month) AS oil_lag3,
    LAG(sugar_price, 1) OVER (ORDER BY month) AS sugar_lag1,
    LAG(sugar_price, 2) OVER (ORDER BY month) AS sugar_lag2,
    LAG(sugar_price, 3) OVER (ORDER BY month) AS sugar_lag3,
    LAG(flour_price, 1) OVER (ORDER BY month) AS flour_lag1,
    LAG(flour_price, 2) OVER (ORDER BY month) AS flour_lag2,
    LAG(flour_price, 3) OVER (ORDER BY month) AS flour_lag3
  FROM pivoted
)

SELECT * FROM lagged
ORDER BY month
