# Data Understanding Document: Indonesia Food Prices

## 1. Dataset Overview

### 1.1 Source Information
- **Source**: World Food Programme (WFP) via Humanitarian Data Exchange (HDX)
- **Dataset ID**: 72cc0659-142b-41af-821a-cb981a852617
- **Country**: Indonesia (IDN)
- **Last Updated**: May 17, 2026
- **Download URL**: https://data.humdata.org/dataset/72cc0659-142b-41af-821a-cb981a852617

### 1.2 Files Summary
| File | Description | Size | Records |
|------|-------------|------|---------|
| `wfp_food_prices_idn.csv` | Food price data | 46.8 MB | 325,240 rows |
| `wfp_markets_idn.csv` | Market locations | 14.4 KB | 224 markets |

---

## 2. Food Prices Dataset (`wfp_food_prices_idn.csv`)

### 2.1 Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | Date | Price observation date | 2007-01-15 |
| `admin1` | String | Province/State | SUMATERA UTARA |
| `admin2` | String | District/City | KOTA SIBOLGA |
| `market` | String | Market name | Pasar Nauli Sibolga |
| `market_id` | Integer | Unique market identifier | 3024 |
| `latitude` | Float | Market latitude | 1.74 |
| `longitude` | Float | Market longitude | 98.78 |
| `category` | String | Commodity category | cereals and tubers |
| `commodity` | String | Specific commodity name | Rice |
| `commodity_id` | Integer | Unique commodity identifier | 52 |
| `unit` | String | Unit of measurement | KG, L, 385 G |
| `priceflag` | String | Price type flag | actual, aggregate |
| `pricetype` | String | Price level | Retail |
| `currency` | String | Currency code | IDR |
| `price` | Float | Price in local currency | 5941.98 |
| `usdprice` | Float | Price in USD | 0.65 |

### 2.2 Temporal Coverage
- **Start Date**: January 15, 2007
- **End Date**: May 15, 2024
- **Frequency**: Monthly (15th of each month)
- **Total Duration**: ~17 years

### 2.3 Commodity Categories

| Category | Example Commodities |
|----------|---------------------|
| cereals and tubers | Rice, Wheat flour |
| meat, fish and eggs | Eggs, Meat (beef), Meat (chicken, broiler) |
| milk and dairy | Milk (condensed) |
| miscellaneous food | Sugar, Sugar (premium) |
| non-food | Fuel (kerosene) |
| oil and fats | Oil (vegetable), Oil (vegetable, bulk), Oil (vegetable, packaged) |
| vegetables and fruits | Chili (bird's eye), Chili (red), Garlic, Onions (shallot) |

### 2.4 Price Flags
- **actual**: Directly observed price at a specific market
- **aggregate**: Calculated/derived price (e.g., national average)

### 2.5 Units of Measurement
- **KG**: Kilogram (most common for solid goods)
- **L**: Liter (for liquids like oil, fuel)
- **385 G**: 385 grams (specific unit for condensed milk)

### 2.6 Geographic Coverage
- **National Level**: National Average (market_id: 974)
- **Provincial Level**: Multiple provinces across Indonesia
- **Local Level**: Specific markets in cities/districts

---

## 3. Markets Dataset (`wfp_markets_idn.csv`)

### 3.1 Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `market_id` | Integer | Unique market identifier | 974 |
| `market` | String | Market name | Pasar Lapang |
| `countryiso3` | String | ISO 3-letter country code | IDN |
| `admin1` | String | Province | ACEH |
| `admin2` | String | District/City | ACEH BARAT |
| `latitude` | Float | Market latitude | 4.17 |
| `longitude` | Float | Market longitude | 96.14 |

### 3.2 Geographic Distribution
- **Total Markets**: 224
- **Coverage**: All major provinces in Indonesia
- **Special Entry**: National Average (market_id: 974) - no coordinates

### 3.3 Sample Markets by Province

| Province | Markets |
|----------|---------|
| ACEH | Pasar Lapang, Pasar Ujong Baro, Pasar Peunayong, etc. |
| BALI | Pasar Badung, Pasar Kreneng, Pasar Anyar, etc. |
| BANTEN | Pasar Kelapa, Pasar Kranggot, Pasar Rawu, etc. |
| DKI JAKARTA | Pasar Minggu, Pasar Jatinegara, Pasar Kramatjati |
| PAPUA | Pasar Lama Timika, Pasar Baru Timika, Pasar Kalibobo, etc. |

---

## 4. Data Quality Observations

### 4.1 Completeness
- **National Average records**: Missing `admin1`, `admin2`, `latitude`, `longitude` (expected - aggregated data)
- **Market-specific records**: Complete geographic information
- **Price data**: Both `price` (IDR) and `usdprice` available for all records

### 4.2 Consistency
- **Date format**: ISO 8601 (YYYY-MM-DD)
- **Currency**: Consistently IDR with USD conversion
- **Price type**: All records show "Retail" price type

### 4.3 Potential Issues
- **Coordinate precision**: Latitude/longitude to 2 decimal places (~1km accuracy)
- **Unit variations**: Some commodities use different units (KG vs L vs 385 G) - need normalization for comparison
- **Missing admin data**: National average records lack geographic hierarchy (by design)

---

## 5. Key Insights for Dashboard Development

### 5.1 Analysis Opportunities
1. **Price Trends**: Track commodity price changes over 17+ years
2. **Geographic Comparison**: Compare prices across provinces/markets
3. **Category Analysis**: Analyze price movements by food category
4. **Inflation Indicators**: Use staple foods (rice, oil) as inflation proxies
5. **Seasonal Patterns**: Identify seasonal price fluctuations

### 5.2 Dashboard Recommendations
- **Time Series Charts**: Price trends for key commodities over time
- **Geographic Maps**: Price heatmaps across Indonesian markets
- **Category Breakdowns**: Price comparison by food category
- **National vs Local**: Compare national average with specific markets
- **USD Conversion**: Show both IDR and USD prices for international context

### 5.3 Data Relationships
- **Primary Key**: (`date`, `market_id`, `commodity_id`) uniquely identifies each price record
- **Foreign Keys**: 
  - `market_id` links to markets dataset
  - `commodity_id` identifies commodities
- **Hierarchical**: admin1 → admin2 → market structure

---

## 6. Metadata Reference

### 6.1 Food Prices Metadata
- **Created**: September 26, 2018
- **Last Modified**: May 17, 2026
- **Resource ID**: 2c0e732c-1d93-4366-8f19-0397064ac5d7

### 6.2 Markets Metadata
- **Created**: May 6, 2025
- **Last Modified**: February 18, 2026
- **Resource ID**: 9d52640e-1fa7-4546-912b-819cb3ace91b

---

## 7. Next Steps

1. **Data Profiling**: Run statistical analysis on price distributions
2. **Missing Data Analysis**: Identify gaps in temporal/geographic coverage
3. **Outlier Detection**: Flag unusual price movements
4. **Data Transformation**: Prepare aggregated views for dashboard
5. **Visualization Planning**: Design specific chart types for each analysis dimension
