"""Build processed KPI tables from the synthetic hourly operations fact table."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    fact = pd.read_csv(RAW / "hourly_operations.csv", parse_dates=["timestamp"])
    fact["date"] = fact.timestamp.dt.date
    fact["month"] = fact.timestamp.dt.to_period("M").astype(str)

    asset_daily = fact.groupby(["date", "asset_id", "asset_name", "technology"], as_index=False).agg(
        generation_mwh=("generation_mwh", "sum"),
        forecast_generation_mwh=("forecast_generation_mwh", "sum"),
        gross_margin_usd=("gross_margin_usd", "sum"),
        market_revenue_usd=("market_revenue_usd", "sum"),
        available_hours=("available_flag", "sum"),
        capacity_mw=("capacity_mw", "first"),
        curtailment_mwh=("curtailment_mwh", "sum"),
        dispatch_opportunity_mwh=("dispatch_opportunity_mwh", "sum"),
        estimated_incremental_margin_usd=("estimated_incremental_margin_usd", "sum"),
        avg_rt_price=("real_time_price_mwh", "mean"),
    )
    asset_daily["capacity_factor"] = asset_daily.generation_mwh / (asset_daily.capacity_mw * 24)
    asset_daily["forecast_abs_error_mwh"] = (asset_daily.generation_mwh - asset_daily.forecast_generation_mwh).abs()
    asset_daily["forecast_ape"] = asset_daily.forecast_abs_error_mwh / asset_daily.generation_mwh.replace(0, pd.NA)
    asset_daily.to_csv(PROCESSED / "asset_daily_kpis.csv", index=False)

    monthly = fact.groupby("month", as_index=False).agg(
        generation_mwh=("generation_mwh", "sum"),
        forecast_generation_mwh=("forecast_generation_mwh", "sum"),
        market_revenue_usd=("market_revenue_usd", "sum"),
        gross_margin_usd=("gross_margin_usd", "sum"),
        curtailment_mwh=("curtailment_mwh", "sum"),
        estimated_incremental_margin_usd=("estimated_incremental_margin_usd", "sum"),
    )
    monthly["forecast_error_pct"] = (monthly.generation_mwh - monthly.forecast_generation_mwh).abs() / monthly.generation_mwh
    monthly["margin_per_mwh"] = monthly.gross_margin_usd / monthly.generation_mwh
    monthly.to_csv(PROCESSED / "portfolio_monthly_kpis.csv", index=False)

    asset_summary = fact.groupby(["asset_id", "asset_name", "technology", "capacity_mw"], as_index=False).agg(
        generation_mwh=("generation_mwh", "sum"),
        gross_margin_usd=("gross_margin_usd", "sum"),
        availability=("available_flag", "mean"),
        revenue_usd=("market_revenue_usd", "sum"),
        curtailment_mwh=("curtailment_mwh", "sum"),
        estimated_incremental_margin_usd=("estimated_incremental_margin_usd", "sum"),
    )
    total_hours = fact.timestamp.nunique()
    asset_summary["capacity_factor"] = asset_summary.generation_mwh / (asset_summary.capacity_mw * total_hours)
    asset_summary["margin_per_mwh"] = asset_summary.gross_margin_usd / asset_summary.generation_mwh
    asset_summary.to_csv(PROCESSED / "asset_summary.csv", index=False)

    opp = fact.loc[fact.estimated_incremental_margin_usd > 0].copy()
    opp["date"] = opp.timestamp.dt.date
    opp = opp.groupby(["date", "asset_id", "asset_name"], as_index=False).agg(
        opportunity_mwh=("dispatch_opportunity_mwh", "sum"),
        estimated_incremental_margin_usd=("estimated_incremental_margin_usd", "sum"),
        avg_spread_mwh=("economic_spread_mwh", "mean"),
        hours_flagged=("timestamp", "count"),
    ).sort_values("estimated_incremental_margin_usd", ascending=False)
    opp.to_csv(PROCESSED / "optimization_opportunities.csv", index=False)
    print("Processed KPI tables rebuilt.")


if __name__ == "__main__":
    main()
