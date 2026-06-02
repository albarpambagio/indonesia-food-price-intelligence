-- NOTE: commodity_pair is ordered as 'rice-oil' (not 'oil-rice'), meaning
-- lag_months is applied to the FIRST commodity before correlating with the SECOND.
-- For the reverse direction (oil leading rice), query mart_commodity_correlation
-- directly with LAG(oil_price, N) and CORR(oil_lagN, rice_price).
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