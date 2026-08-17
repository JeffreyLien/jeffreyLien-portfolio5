# Data Outputs

This public repository keeps the compact aggregate tables used in the executive analysis:

- `asset_summary.csv`
- `portfolio_monthly_kpis.csv`
- `forecast_results.csv`
- `forecast_feature_importance.csv`
- `optimization_opportunities.csv`

Large synthetic hourly fact files and `asset_daily_kpis.csv` are excluded from version control. Rebuild the full data layer from the repository root:

```bash
python src/generate_synthetic_data.py
python src/validate_data.py
python src/build_metrics.py
python src/train_forecast.py
```

All data is fictional and generated only for this case study.
