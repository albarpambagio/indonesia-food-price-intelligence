-- Assert filter_out is consistent with its component flags.
-- filter_out must be TRUE when ANY flag is TRUE and FALSE when ALL flags are FALSE.
-- This invariant protects against a developer adding a new quality flag
-- but forgetting to include it in the composite filter_out expression.

WITH validation AS (
  SELECT
    CASE
      WHEN filter_out = TRUE
        AND (flag_price_le_zero = FALSE
          AND flag_null_unit = FALSE
          AND flag_non_target = FALSE
          AND flag_aggregate = FALSE
          AND flag_invalid_year = FALSE)
      THEN 'filter_out TRUE but no flags set'
      WHEN filter_out = FALSE
        AND (flag_price_le_zero = TRUE
          OR flag_null_unit = TRUE
          OR flag_non_target = TRUE
          OR flag_aggregate = TRUE
          OR flag_invalid_year = TRUE)
      THEN 'filter_out FALSE but a flag is set'
      ELSE 'ok'
    END AS status
  FROM {{ ref('int_prices_normalised') }}
)

SELECT status, COUNT(*) AS row_count
FROM validation
WHERE status != 'ok'
GROUP BY status
