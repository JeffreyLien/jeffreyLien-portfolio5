# Data Dictionary

## `hourly_operations.csv`

| Field | Description |
|---|---|
| `timestamp` | Operating hour |
| `asset_id` / `asset_name` | Fictional generating asset key and name |
| `technology` | CCGT, CT, Solar, or Wind |
| `market_hub` | Fictional price hub |
| `capacity_mw` | Nameplate capacity |
| `available_flag` | 1 if available in the simulated hour, otherwise 0 |
| `planned_outage_flag` | Simulated planned outage indicator |
| `forced_outage_flag` | Simulated forced outage indicator |
| `gas_price_mmbtu` | Synthetic hourly gas price |
| `day_ahead_price_mwh` | Synthetic day-ahead power price |
| `real_time_price_mwh` | Synthetic real-time power price |
| `variable_cost_mwh` | Modeled variable production cost per MWh |
| `economic_spread_mwh` | Real-time market price less variable cost |
| `generation_mwh` | Simulated actual hourly generation |
| `forecast_generation_mwh` | Simulated operating forecast at the asset-hour level |
| `curtailment_mwh` | Simulated curtailed renewable generation |
| `market_revenue_usd` | Generation × real-time price |
| `fuel_cost_usd` | Thermal fuel cost |
| `variable_om_usd` | Variable O&M cost |
| `gross_margin_usd` | Revenue − fuel − variable O&M |
| `dispatch_opportunity_mwh` | Simplified thermal headroom flag under attractive spread conditions |
| `estimated_incremental_margin_usd` | Conservative simulated value screen based on headroom and spread |
| `date` / `month` | Reporting attributes |

## Supporting tables
- `assets.csv`: asset master and commercial structure.
- `hourly_market.csv`: synthetic hub-level day-ahead and real-time prices.
- `hourly_fuel.csv`: synthetic hourly natural-gas price.
