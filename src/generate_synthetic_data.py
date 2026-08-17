"""Generate the fictional hourly power-portfolio data used in this case study.

All assets, prices, outages, operations, and financial results are synthetic.
The generator is deterministic with SEED=42 so the portfolio can be rebuilt.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

ASSET_ROWS = [
    ["A01", "Riverbend CCGT", "CCGT", 780, 7.15, 3.2, "Central Hub", "Merchant"],
    ["A02", "Pine Ridge CCGT", "CCGT", 620, 7.45, 3.5, "Central Hub", "Tolling"],
    ["A03", "Magnolia CT", "CT", 220, 10.40, 5.0, "Central Hub", "Merchant"],
    ["A04", "Cedar CT", "CT", 180, 10.75, 5.2, "East Hub", "Merchant"],
    ["A05", "Sunfield Solar", "Solar", 250, 0.0, 1.1, "East Hub", "PPA"],
    ["A06", "Oak Valley Solar", "Solar", 180, 0.0, 1.1, "Central Hub", "PPA"],
    ["A07", "Highland Wind", "Wind", 300, 0.0, 1.6, "West Hub", "PPA"],
    ["A08", "Prairie Wind", "Wind", 240, 0.0, 1.6, "West Hub", "Merchant"],
]
ASSET_COLUMNS = [
    "asset_id", "asset_name", "technology", "capacity_mw",
    "heat_rate_mmbtu_mwh", "variable_om_per_mwh", "market_hub",
    "commercial_structure",
]


def build_assets() -> pd.DataFrame:
    return pd.DataFrame(ASSET_ROWS, columns=ASSET_COLUMNS)


def build_market(hours: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for ts in hours:
        seasonal = 5 * np.cos((ts.dayofyear - 20) / 365 * 2 * np.pi)
        seasonal += 4 * np.sin((ts.dayofyear - 150) / 365 * 2 * np.pi)
        evening = 9 * np.exp(-((ts.hour - 18) / 3.2) ** 2)
        morning = 4 * np.exp(-((ts.hour - 8) / 3.0) ** 2)
        weekend = -2.0 if ts.dayofweek >= 5 else 0.0
        common = 32 + seasonal + evening + morning + weekend + rng.normal(0, 4)
        if rng.random() < 0.008:
            common += rng.uniform(45, 130)
        for hub, adjustment in [("Central Hub", 0), ("East Hub", 1.8), ("West Hub", -1.2)]:
            da = common + adjustment + rng.normal(0, 1.8)
            rt = da + rng.normal(0, 4.5)
            rows.append([ts, hub, da, rt])
    return pd.DataFrame(rows, columns=[
        "timestamp", "market_hub", "day_ahead_price_mwh", "real_time_price_mwh"
    ])


def build_fuel(hours: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    df = pd.DataFrame({"timestamp": hours})
    df["gas_price_mmbtu"] = (
        3.25
        + 0.35 * np.cos((df.timestamp.dt.dayofyear - 20) / 365 * 2 * np.pi)
        + rng.normal(0, 0.09, len(df))
    ).clip(2.4, 4.5)
    return df


def build_operations(assets: pd.DataFrame, hours: pd.DatetimeIndex,
                     market: pd.DataFrame, fuel: pd.DataFrame,
                     rng: np.random.Generator) -> pd.DataFrame:
    market_idx = market.set_index(["timestamp", "market_hub"])
    fuel_idx = fuel.set_index("timestamp")

    outages = {}
    for asset_id in assets.loc[assets.technology.isin(["CCGT", "CT"]), "asset_id"]:
        blocks = []
        for _ in range(3):
            start = int(rng.integers(0, len(hours) - 96))
            blocks.append((start, start + int(rng.integers(12, 72))))
        outages[asset_id] = blocks

    rows = []
    for _, asset in assets.iterrows():
        cap = asset.capacity_mw
        for i, ts in enumerate(hours):
            da = float(market_idx.loc[(ts, asset.market_hub), "day_ahead_price_mwh"])
            rt = float(market_idx.loc[(ts, asset.market_hub), "real_time_price_mwh"])
            gas = float(fuel_idx.loc[ts, "gas_price_mmbtu"])
            tech = asset.technology
            forced = rng.random() < (0.0025 if tech == "CCGT" else 0.0035 if tech == "CT" else 0.001)
            planned = any(start <= i < end for start, end in outages.get(asset.asset_id, []))
            available = 0 if forced or planned else 1

            if tech in ["CCGT", "CT"]:
                variable_cost = gas * asset.heat_rate_mmbtu_mwh + asset.variable_om_per_mwh
                spread = rt - variable_cost
                if not available:
                    generation = 0.0
                elif spread > 0:
                    base = 0.58 if tech == "CCGT" else 0.15
                    responsiveness = 0.30 if tech == "CCGT" else 0.55
                    load_factor = np.clip(base + responsiveness * np.tanh(spread / 35) + rng.normal(0, 0.07), 0, 1)
                    generation = cap * load_factor
                else:
                    generation = max(0, cap * rng.uniform(0, 0.03))
                curtailment = 0.0
            elif tech == "Solar":
                daylight = max(0, np.sin((ts.hour - 6) / 12 * np.pi)) if 6 <= ts.hour <= 18 else 0
                season = 0.72 + 0.20 * np.sin((ts.dayofyear - 80) / 365 * 2 * np.pi)
                cloud = np.clip(rng.beta(5, 2), 0.15, 1)
                potential = cap * daylight * season * cloud * available
                curtail_frac = 0.12 if rt < 0 else (0.03 if rt < 15 else 0)
                curtailment = potential * curtail_frac
                generation = max(0, potential - curtailment)
                variable_cost = asset.variable_om_per_mwh
                spread = rt - variable_cost
            else:
                wind_factor = np.clip(
                    0.38 + 0.14 * np.sin((ts.hour + 3) / 24 * 2 * np.pi) + rng.normal(0, 0.14),
                    0.03, 0.83
                )
                potential = cap * wind_factor * available
                curtail_frac = 0.10 if rt < 0 else (0.02 if rt < 12 else 0)
                curtailment = potential * curtail_frac
                generation = max(0, potential - curtailment)
                variable_cost = asset.variable_om_per_mwh
                spread = rt - variable_cost

            generation_forecast = max(
                0,
                generation * (1 + rng.normal(0, 0.09 if tech in ["CCGT", "CT"] else 0.14))
                + rng.normal(0, cap * 0.015),
            )
            generation_forecast = min(cap, generation_forecast)
            market_revenue = generation * rt
            fuel_cost = generation * gas * asset.heat_rate_mmbtu_mwh if tech in ["CCGT", "CT"] else 0.0
            variable_om = generation * asset.variable_om_per_mwh
            gross_margin = market_revenue - fuel_cost - variable_om

            headroom = max(0, cap * available - generation)
            opportunity_mwh = headroom if (tech in ["CCGT", "CT"] and spread > 12 and generation < cap * 0.78) else 0.0
            estimated_incremental_margin = opportunity_mwh * max(0, spread) * 0.45

            rows.append([
                ts, asset.asset_id, asset.asset_name, tech, asset.market_hub, cap,
                available, int(planned), int(forced), gas, da, rt, variable_cost,
                spread, generation, generation_forecast, curtailment, market_revenue,
                fuel_cost, variable_om, gross_margin, opportunity_mwh,
                estimated_incremental_margin,
            ])

    columns = [
        "timestamp", "asset_id", "asset_name", "technology", "market_hub", "capacity_mw",
        "available_flag", "planned_outage_flag", "forced_outage_flag", "gas_price_mmbtu",
        "day_ahead_price_mwh", "real_time_price_mwh", "variable_cost_mwh",
        "economic_spread_mwh", "generation_mwh", "forecast_generation_mwh", "curtailment_mwh",
        "market_revenue_usd", "fuel_cost_usd", "variable_om_usd", "gross_margin_usd",
        "dispatch_opportunity_mwh", "estimated_incremental_margin_usd",
    ]
    df = pd.DataFrame(rows, columns=columns)
    df["date"] = df.timestamp.dt.date
    df["month"] = df.timestamp.dt.to_period("M").astype(str)
    return df


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    hours = pd.date_range("2026-01-01", "2026-06-30 23:00", freq="h")
    assets = build_assets()
    market = build_market(hours, rng)
    fuel = build_fuel(hours, rng)
    operations = build_operations(assets, hours, market, fuel, rng)

    assets.to_csv(RAW / "assets.csv", index=False)
    market.to_csv(RAW / "hourly_market.csv", index=False)
    fuel.to_csv(RAW / "hourly_fuel.csv", index=False)
    operations.to_csv(RAW / "hourly_operations.csv", index=False)
    print(f"Wrote {len(operations):,} synthetic asset-hour rows to {RAW}")


if __name__ == "__main__":
    main()
