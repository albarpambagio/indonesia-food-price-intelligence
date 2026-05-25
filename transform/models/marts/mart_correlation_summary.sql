WITH corr_base AS (
  SELECT
    rice_price,
    oil_price,
    sugar_price,
    flour_price,
    rice_lag1,
    rice_lag2,
    rice_lag3,
    oil_lag1,
    oil_lag2,
    oil_lag3,
    sugar_lag1,
    sugar_lag2,
    sugar_lag3,
    flour_lag1,
    flour_lag2,
    flour_lag3
  FROM {{ ref('mart_commodity_correlation') }}
),

pairwise AS (
  SELECT
    'rice-oil' AS commodity_pair,
    0 AS lag_months,
    CORR(rice_price, oil_price) AS pearson_r
  FROM corr_base
  UNION ALL
  SELECT 'rice-oil', 1, CORR(rice_lag1, oil_price) FROM corr_base
  UNION ALL
  SELECT 'rice-oil', 2, CORR(rice_lag2, oil_price) FROM corr_base
  UNION ALL
  SELECT 'rice-oil', 3, CORR(rice_lag3, oil_price) FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 0, CORR(rice_price, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 1, CORR(rice_lag1, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 2, CORR(rice_lag2, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 3, CORR(rice_lag3, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 0, CORR(rice_price, flour_price) FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 1, CORR(rice_lag1, flour_price) FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 2, CORR(rice_lag2, flour_price) FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 3, CORR(rice_lag3, flour_price) FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 0, CORR(oil_price, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 1, CORR(oil_lag1, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 2, CORR(oil_lag2, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 3, CORR(oil_lag3, sugar_price) FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 0, CORR(oil_price, flour_price) FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 1, CORR(oil_lag1, flour_price) FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 2, CORR(oil_lag2, flour_price) FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 3, CORR(oil_lag3, flour_price) FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 0, CORR(sugar_price, flour_price) FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 1, CORR(sugar_lag1, flour_price) FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 2, CORR(sugar_lag2, flour_price) FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 3, CORR(sugar_lag3, flour_price) FROM corr_base
),

ranked AS (
  SELECT
    commodity_pair,
    lag_months,
    ROUND(pearson_r, 4) AS pearson_r,
    ROW_NUMBER() OVER (
      PARTITION BY SPLIT_PART(commodity_pair, '-', 1)
      ORDER BY ABS(pearson_r) DESC
    ) AS rank_for_commodity
  FROM pairwise
)

SELECT * FROM ranked
ORDER BY commodity_pair, lag_months