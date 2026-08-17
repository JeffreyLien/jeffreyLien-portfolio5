"""Train a leakage-aware daily portfolio generation forecast.

The holdout is June 2026. Features use day-ahead market information, gas price,
calendar fields, and lagged realized generation; real-time prices are excluded.
"""
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def main() -> None:
    fact = pd.read_csv(RAW / "hourly_operations.csv", parse_dates=["timestamp"])
    fact["date"] = fact.timestamp.dt.date
    daily = fact.groupby("date", as_index=False).agg(
        generation_mwh=("generation_mwh", "sum"),
        avg_da_price=("day_ahead_price_mwh", "mean"),
        avg_gas_price=("gas_price_mmbtu", "mean"),
    )
    daily["date"] = pd.to_datetime(daily.date)
    daily["dow"] = daily.date.dt.dayofweek
    daily["dayofyear"] = daily.date.dt.dayofyear
    daily["month_num"] = daily.date.dt.month
    daily["lag1_generation"] = daily.generation_mwh.shift(1)
    daily["lag7_generation"] = daily.generation_mwh.shift(7)
    model_df = daily.dropna().copy()

    features = [
        "avg_da_price", "avg_gas_price", "dow", "dayofyear", "month_num",
        "lag1_generation", "lag7_generation",
    ]
    train = model_df[model_df.date < "2026-06-01"]
    test = model_df[model_df.date >= "2026-06-01"].copy()

    model = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42)
    model.fit(train[features], train.generation_mwh)
    test["predicted_generation_mwh"] = model.predict(test[features])
    test["abs_error_mwh"] = (test.generation_mwh - test.predicted_generation_mwh).abs()
    test["ape"] = test.abs_error_mwh / test.generation_mwh

    result_cols = ["date", "generation_mwh", "predicted_generation_mwh", "abs_error_mwh", "ape"]
    test[result_cols].to_csv(PROCESSED / "forecast_results.csv", index=False)
    pd.DataFrame({"feature": features, "importance": model.feature_importances_}) \
        .sort_values("importance", ascending=False) \
        .to_csv(PROCESSED / "forecast_feature_importance.csv", index=False)

    mae = mean_absolute_error(test.generation_mwh, test.predicted_generation_mwh)
    rmse = mean_squared_error(test.generation_mwh, test.predicted_generation_mwh) ** 0.5
    print(f"June MAE: {mae:,.0f} MWh/day")
    print(f"June RMSE: {rmse:,.0f} MWh/day")
    print(f"June MAPE: {test.ape.mean():.2%}")


if __name__ == "__main__":
    main()
