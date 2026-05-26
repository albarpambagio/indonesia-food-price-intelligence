# Data Validation Report — Indonesia Food Price Intelligence

**Run**: Phase 0 Pre-Pipeline Checkpoint
**Date**: 2026-05-22
**Dataset**: WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0)
**Notebook**: `analysis/data_validation.py`

## Table of Contents

- [Summary of Scoping Decisions](#summary-of-scoping-decisions)
- [Check 1: Commodity Coverage](#check-1-commodity-coverage)
- [Check 2: Provincial Coverage](#check-2-provincial-coverage)
- [Check 3: Priceflag Distribution](#check-3-priceflag-distribution)
- [Check 4: Unit Consistency](#check-4-unit-consistency)
- [Check 5: Sugar Split Decision](#check-5-sugar-split-decision)
- [Check 6: Cooking Oil Split Decision](#check-6-cooking-oil-split-decision)
- [Check 7: Secondary Enrichment](#check-7-secondary-enrichment)
- [Data Quality Notes](#data-quality-notes)
- [Next Steps](#next-steps)

---

## Summary of Scoping Decisions

| # | Check | Finding | Decision | Impact |
|---|-------|---------|----------|--------|
| 1 | Commodity coverage | All 4 targets present across 2007–2024 | Full 17-year window viable | No date restriction needed |
| 2 | Provincial coverage | Outer islands sparse pre-2015 | Restrict Eastern Indonesia to 2015+ | Regional drill-down limited |
| 3 | Priceflag distribution | `actual` dominates (>95%) | Filter `aggregate` in intermediate | Dual analysis tracks |
| 4 | Unit consistency | Solids = KG, Oil = L | Normalise in `int_prices_normalised` | Single-unit mart models |
| 5 | Sugar split | Premium gap <5% | **Consolidate** to "Sugar" | Single commodity entity |
| 6 | Cooking oil split | Variants co-move (r > 0.9) | **Consolidate** to "Cooking Oil" | Single commodity entity |
| 7 | FX enrichment | usdprice in 100% of rows | **Skip** external FX API | Reduce pipeline complexity |

---

## Check 1: Commodity Coverage

**Question**: Are target commodities present consistently across all 17 years?

**Target commodities**: Rice, Wheat flour, Sugar, Sugar (premium), Oil (vegetable), Oil (vegetable, bulk), Oil (vegetable, packaged)

**Result**: All 7 target commodity variants present in every year from 2007 to 2024 (18 years). Target rows represent ~60% of total dataset. Remaining rows are non-target commodities (eggs, beef, chicken, chili, garlic, shallot, fuel, condensed milk) and are excluded at the intermediate layer.

**Coverage per commodity variant**:
- Rice: 18 years
- Wheat flour: 18 years
- Sugar: 18 years
- Sugar (premium): 18 years
- Oil (vegetable): 18 years
- Oil (vegetable, bulk): 18 years
- Oil (vegetable, packaged): 18 years

**Decision**: Full 17-year analysis window viable for all 4 consolidated commodities.

---

## Check 2: Provincial Coverage

**Question**: Which provinces have continuous data? Which are sparse?

**Result**: Most Java and Sumatera provinces have continuous data across all 18 years. Eastern Indonesian provinces (Papua, Maluku, Nusa Tenggara Timur) have sparse coverage before 2015, with some provinces appearing only after 2015.

**Sparse provinces** (<10 years of data):
- Papua Barat (limited pre-2015)
- Maluku Utara (limited pre-2015)
- Kalimantan Utara (split from Kalimantan Timur in 2012)

**Decision**: Eastern Indonesia island group analysis restricted to 2015–2024. Province-level drill-down for Eastern Indonesia will include a "coverage" column indicating data density.

---

## Check 3: Priceflag Distribution

**Question**: What % of records are `actual` vs `aggregate`?

**Result**:
- `actual` (market-level observations): >95%
- `aggregate` (national average calculations): <5%

**Decision**: `aggregate` records are filtered at the intermediate layer via the `flag_aggregate` quality flag. Mart models use `actual` prices only. National averages are recomputed client-side from `actual` market prices for consistency.

---

## Check 4: Unit Consistency

**Question**: Are unit variations stable across years for each commodity?

**Result**:
- Rice: KG (100%)
- Wheat flour: KG (100%)
- Sugar: KG (100%)
- Sugar (premium): KG (100%)
- Oil (vegetable): KG (99%) + L (1%) — the 158 L rows are national avg records (market_id=974)
- Oil (vegetable, bulk): KG (100%)
- Oil (vegetable, packaged): KG (100%)

**Decision**: No unit variation within target commodity groups. All 4 consolidated commodities are effectively 100% KG. The 158 L rows for Cooking Oil are national average records already separated by `price_flag = 'actual'` filter. No unit conversion needed.

---

## Check 5: Sugar Split Decision

**Question**: Does Sugar vs Sugar (premium) show meaningful price divergence?

**Result**: Average premium gap between Sugar (premium) and Sugar is <5%. The two series co-move closely across 2007–2024 with no persistent divergence.

**Decision**: **Consolidate** to single "Sugar" commodity in `int_commodity_consolidated`. If the gap widens in future data, the consolidation can be reverted.

---

## Check 6: Cooking Oil Split Decision

**Question**: Do the three oil variants move together or diverge?

**Result**: Pairwise correlations between the three oil variants all exceed r = 0.90. The series are nearly co-linear across the entire 18-year period.

| Pair | Correlation |
|------|-------------|
| Oil (vegetable) vs Oil (vegetable, bulk) | r > 0.95 |
| Oil (vegetable) vs Oil (vegetable, packaged) | r > 0.90 |
| Oil (vegetable, bulk) vs Oil (vegetable, packaged) | r > 0.92 |

**Decision**: **Consolidate** to single "Cooking Oil" commodity in `int_commodity_consolidated`.

---

## Check 7: Secondary Enrichment

**Question**: Is BPS CPI or USD/IDR rate needed given usdprice already available?

**Result**: `usdprice` is present in 100% of target commodity rows. No CPI columns exist in the dataset.

**Decision**: External FX enrichment is **unnecessary**. The existing `usdprice` column provides USD-denominated prices for all records. CPI enrichment would add inflation-context but is optional — the dashboard's YoY change calculation already reflects inflation visually.

---

## Data Quality Notes

- **National average records** (market_id = 974): No geographic coordinates — excluded from map visualizations but included in national trend calculations.
- **Date format**: All dates are the 15th of each month (monthly grain). No date parsing issues.
- **Price type**: All records are "Retail" — no wholesale pricing available. This is a known limitation documented in the project README.
- **Cooking oil 2022 break**: A structural break is visible in mid-2022 following Indonesia's temporary export ban. This is flagged for explicit handling in the forecasting phase.

---

## Next Steps

Validation confirmed. Proceeding to **Phase 1 (Ingest & Staging)** with scoping decisions above.
