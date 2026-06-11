-- All 12 directed pairs (6 forward + 6 reverse) × 4 lags = 48 rows.
-- commodity_pair = 'leader-follower' — lag is applied to the FIRST commodity.
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
    flour_lag3,
    month
  FROM {{ ref('mart_commodity_correlation') }}
),

pairwise AS (
  SELECT
    'rice-oil' AS commodity_pair,
    0 AS lag_months,
    CORR(rice_price, oil_price) AS pearson_r,
    CORR(CASE WHEN month < '2022-01-01' THEN rice_price END,
         CASE WHEN month < '2022-01-01' THEN oil_price END) AS pearson_r_pre_2022,
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_price END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END) AS pearson_r_post_2022
  FROM corr_base
  UNION ALL
  SELECT 'rice-oil', 1,
    CORR(rice_lag1, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag1 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-oil', 2,
    CORR(rice_lag2, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag2 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-oil', 3,
    CORR(rice_lag3, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag3 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 0,
    CORR(rice_price, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_price END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_price END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 1,
    CORR(rice_lag1, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag1 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 2,
    CORR(rice_lag2, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag2 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-sugar', 3,
    CORR(rice_lag3, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag3 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 0,
    CORR(rice_price, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_price END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_price END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 1,
    CORR(rice_lag1, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag1 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 2,
    CORR(rice_lag2, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag2 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'rice-flour', 3,
    CORR(rice_lag3, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN rice_lag3 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN rice_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 0,
    CORR(oil_price, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_price END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_price END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 1,
    CORR(oil_lag1, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag1 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 2,
    CORR(oil_lag2, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag2 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-sugar', 3,
    CORR(oil_lag3, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag3 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 0,
    CORR(oil_price, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_price END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_price END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 1,
    CORR(oil_lag1, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag1 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 2,
    CORR(oil_lag2, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag2 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-flour', 3,
    CORR(oil_lag3, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag3 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 0,
    CORR(sugar_price, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_price END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_price END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 1,
    CORR(sugar_lag1, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag1 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 2,
    CORR(sugar_lag2, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag2 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-flour', 3,
    CORR(sugar_lag3, flour_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag3 END,
         CASE WHEN month < '2022-01-01' THEN flour_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN flour_price END)
  FROM corr_base
  -- Reverse direction: oil leading rice
  UNION ALL
  SELECT 'oil-rice', 0,
    CORR(oil_price, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_price END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_price END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-rice', 1,
    CORR(oil_lag1, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag1 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-rice', 2,
    CORR(oil_lag2, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag2 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'oil-rice', 3,
    CORR(oil_lag3, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN oil_lag3 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN oil_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  -- Reverse direction: sugar leading rice
  UNION ALL
  SELECT 'sugar-rice', 0,
    CORR(sugar_price, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_price END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_price END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-rice', 1,
    CORR(sugar_lag1, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag1 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-rice', 2,
    CORR(sugar_lag2, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag2 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-rice', 3,
    CORR(sugar_lag3, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag3 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  -- Reverse direction: flour leading rice
  UNION ALL
  SELECT 'flour-rice', 0,
    CORR(flour_price, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_price END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_price END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-rice', 1,
    CORR(flour_lag1, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag1 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-rice', 2,
    CORR(flour_lag2, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag2 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-rice', 3,
    CORR(flour_lag3, rice_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag3 END,
         CASE WHEN month < '2022-01-01' THEN rice_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN rice_price END)
  FROM corr_base
  -- Reverse direction: sugar leading oil
  UNION ALL
  SELECT 'sugar-oil', 0,
    CORR(sugar_price, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_price END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_price END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-oil', 1,
    CORR(sugar_lag1, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag1 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-oil', 2,
    CORR(sugar_lag2, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag2 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'sugar-oil', 3,
    CORR(sugar_lag3, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN sugar_lag3 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN sugar_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  -- Reverse direction: flour leading oil
  UNION ALL
  SELECT 'flour-oil', 0,
    CORR(flour_price, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_price END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_price END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-oil', 1,
    CORR(flour_lag1, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag1 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-oil', 2,
    CORR(flour_lag2, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag2 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-oil', 3,
    CORR(flour_lag3, oil_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag3 END,
         CASE WHEN month < '2022-01-01' THEN oil_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN oil_price END)
  FROM corr_base
  -- Reverse direction: flour leading sugar
  UNION ALL
  SELECT 'flour-sugar', 0,
    CORR(flour_price, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_price END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_price END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-sugar', 1,
    CORR(flour_lag1, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag1 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag1 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-sugar', 2,
    CORR(flour_lag2, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag2 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag2 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
  UNION ALL
  SELECT 'flour-sugar', 3,
    CORR(flour_lag3, sugar_price),
    CORR(CASE WHEN month < '2022-01-01' THEN flour_lag3 END,
         CASE WHEN month < '2022-01-01' THEN sugar_price END),
    CORR(CASE WHEN month >= '2022-01-01' THEN flour_lag3 END,
         CASE WHEN month >= '2022-01-01' THEN sugar_price END)
  FROM corr_base
),

ranked AS (
  SELECT
    commodity_pair,
    lag_months,
    ROUND(pearson_r, 4) AS pearson_r,
    ROUND(pearson_r_pre_2022, 4) AS pearson_r_pre_2022,
    ROUND(pearson_r_post_2022, 4) AS pearson_r_post_2022,
    ROW_NUMBER() OVER (
      PARTITION BY SPLIT_PART(commodity_pair, '-', 1)
      ORDER BY ABS(pearson_r) DESC
    ) AS rank_for_commodity
  FROM pairwise
)

SELECT * FROM ranked
ORDER BY commodity_pair, lag_months