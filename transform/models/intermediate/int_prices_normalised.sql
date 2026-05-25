WITH commodity_map AS (
  SELECT * FROM {{ ref('int_commodity_consolidated') }}
)

SELECT
  c.date,
  DATE_TRUNC('month', c.date) AS month,
  c.admin1,
  c.admin2,
  c.market,
  c.market_id,
  c.latitude,
  c.longitude,
  c.commodity,
  c.commodity_id,
  c.unit,
  c.price_flag,
  c.pricetype,
  c.currency,
  c.price AS price_idr,
  c.usdprice AS price_usd,
  c.commodity_consolidated,
  CASE
    WHEN c.admin1 IN ('DKI JAKARTA', 'JAWA BARAT', 'JAWA TENGAH', 'DAERAH ISTIMEWA YOGYAKARTA', 'JAWA TIMUR', 'BANTEN')
      THEN 'Java'
    WHEN c.admin1 IN ('ACEH', 'SUMATERA UTARA', 'SUMATERA BARAT', 'RIAU', 'JAMBI', 'SUMATERA SELATAN', 'BENGKULU', 'LAMPUNG', 'KEPULAUAN RIAU', 'KEPULAUAN BANGKA BELITUNG')
      THEN 'Sumatera'
    WHEN c.admin1 IN ('KALIMANTAN BARAT', 'KALIMANTAN TENGAH', 'KALIMANTAN SELATAN', 'KALIMANTAN TIMUR', 'KALIMANTAN UTARA')
      THEN 'Kalimantan'
    WHEN c.admin1 IN ('SULAWESI UTARA', 'SULAWESI TENGAH', 'SULAWESI SELATAN', 'SULAWESI TENGGARA', 'GORONTALO', 'SULAWESI BARAT')
      THEN 'Sulawesi'
    WHEN c.admin1 IN ('BALI', 'NUSA TENGGARA BARAT', 'NUSA TENGGARA TIMUR', 'MALUKU', 'MALUKU UTARA', 'PAPUA', 'PAPUA BARAT')
      THEN 'Eastern Indonesia'
    ELSE NULL
  END AS island_group,
  c.price <= 0 AS flag_price_le_zero,
  c.unit IS NULL AS flag_null_unit,
  c.commodity_consolidated IS NULL AS flag_non_target,
  c.price_flag = 'aggregate' AS flag_aggregate,
  EXTRACT(YEAR FROM c.date) NOT BETWEEN 2007 AND 2024 AS flag_invalid_year,
  (
    c.price <= 0
    OR c.unit IS NULL
    OR c.commodity_consolidated IS NULL
    OR c.price_flag = 'aggregate'
    OR EXTRACT(YEAR FROM c.date) NOT BETWEEN 2007 AND 2024
  ) AS filter_out
FROM commodity_map c
