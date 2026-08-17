"""Basic data-quality checks for the synthetic portfolio fact table."""
from pathlib import Path
import pandas as pd

PATH = Path("data/raw/hourly_operations.csv")

def run_checks(df: pd.DataFrame) -> dict:
    checks = {
        "row_count_positive": len(df) > 0,
        "key_not_null": df[["timestamp", "asset_id"]].notna().all().all(),
        "generation_nonnegative": (df["generation_mwh"] >= 0).all(),
        "generation_below_capacity": (df["generation_mwh"] <= df["capacity_mw"] + 1e-8).all(),
        "availability_binary": df["available_flag"].isin([0, 1]).all(),
        "no_duplicate_asset_hour": ~df.duplicated(["timestamp", "asset_id"]).any(),
    }
    return checks

def main():
    df = pd.read_csv(PATH)
    checks = run_checks(df)
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
