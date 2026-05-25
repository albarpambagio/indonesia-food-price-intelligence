-- Assert each mart model has rows after materialization.
-- This is a singular test that fails if any mart is empty.

WITH mart_counts AS (
    SELECT 'mart_price_trends' AS model_name, COUNT(*) AS row_count FROM {{ ref('mart_price_trends') }}
    UNION ALL
    SELECT 'mart_seasonal_patterns', COUNT(*) FROM {{ ref('mart_seasonal_patterns') }}
    UNION ALL
    SELECT 'mart_geo_disparity', COUNT(*) FROM {{ ref('mart_geo_disparity') }}
    UNION ALL
    SELECT 'mart_commodity_correlation', COUNT(*) FROM {{ ref('mart_commodity_correlation') }}
    UNION ALL
    SELECT 'mart_correlation_summary', COUNT(*) FROM {{ ref('mart_correlation_summary') }}
)

SELECT model_name, row_count
FROM mart_counts
WHERE row_count = 0
