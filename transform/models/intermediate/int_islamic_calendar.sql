WITH islamic AS (
  SELECT
    year,
    CAST(eid_date AS DATE) AS eid_date,
    source
  FROM {{ ref('islamic_calendar') }}
)

SELECT
  year,
  eid_date,
  STRFTIME(eid_date, '%Y-%m') AS eid_month,
  STRFTIME(eid_date - INTERVAL 1 MONTH, '%Y-%m') AS t_minus_1,
  STRFTIME(eid_date - INTERVAL 2 MONTH, '%Y-%m') AS t_minus_2,
  STRFTIME(eid_date - INTERVAL 3 MONTH, '%Y-%m') AS t_minus_3,
  STRFTIME(eid_date + INTERVAL 1 MONTH, '%Y-%m') AS t_plus_1,
  source
FROM islamic
