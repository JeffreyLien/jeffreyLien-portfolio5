# Power BI Build Guide

## Goal
Build an executive-ready commercial operations dashboard from `data/raw/hourly_operations.csv` and `data/raw/assets.csv`.

## Data model
Use a star schema:

- **FactHourlyOperations** — hourly asset operations, market prices, costs, generation, forecast, margin, and opportunity flags.
- **DimAsset** — asset metadata from `assets.csv`.
- **DimDate** — date/calendar table generated in Power BI.

Relationships:

- `DimAsset[asset_id]` 1 → * `FactHourlyOperations[asset_id]`
- `DimDate[Date]` 1 → * `FactHourlyOperations[date]`

## Page 1 — Executive Portfolio Scorecard
Cards: Gross Margin, Generation MWh, Margin/MWh, Availability %, Forecast Error %, Estimated Incremental Margin.

Visuals:
1. Monthly Gross Margin and Generation trend.
2. Gross Margin by asset.
3. Technology mix by generation.
4. Variance callout for forecast vs actual.

## Page 2 — Operations & Asset Performance
- Capacity factor vs availability by asset.
- Outage hours and generation loss proxy.
- Daily asset generation trend.
- Drill-through table with asset, date, capacity factor, generation, margin.

## Page 3 — Commercial & Market Performance
- Realized capture price vs average real-time market price.
- Gross margin vs market price by month.
- Economic spread distribution for thermal units.
- Revenue and margin by commercial structure.

## Page 4 — Forecasting & Value Opportunities
- Actual vs forecast generation.
- Forecast error by asset/technology.
- Flagged dispatch-opportunity hours.
- Estimated incremental margin by asset and date.

## Governance choices
- Use explicit DAX measures instead of hidden implicit aggregations.
- Keep business definitions in `docs/KPI_DICTIONARY.md`.
- Use one canonical calculation per KPI.
- Add data refresh timestamp and data-quality status to the executive page.
