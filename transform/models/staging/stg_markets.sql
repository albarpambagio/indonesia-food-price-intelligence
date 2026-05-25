SELECT
  market_id,
  TRIM(market) AS market,
  TRIM(countryiso3) AS countryiso3,
  CASE WHEN admin1 IS NULL OR TRIM(admin1) = '' THEN 'NATIONAL' ELSE UPPER(TRIM(admin1)) END AS admin1,
  CASE WHEN admin2 IS NULL OR TRIM(admin2) = '' THEN 'NATIONAL' ELSE UPPER(TRIM(admin2)) END AS admin2,
  CAST(latitude AS FLOAT) AS latitude,
  CAST(longitude AS FLOAT) AS longitude,
  (market_id = 974) AS is_national_avg
FROM {{ source('raw', 'markets') }}
