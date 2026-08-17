-- Forecast accuracy by asset and month
SELECT
    DATE_TRUNC('month', timestamp) AS month,
    asset_name,
    SUM(generation_mwh) AS actual_generation_mwh,
    SUM(forecast_generation_mwh) AS forecast_generation_mwh,
    ABS(SUM(generation_mwh) - SUM(forecast_generation_mwh))
        / NULLIF(SUM(generation_mwh), 0) AS absolute_pct_error
FROM hourly_operations
GROUP BY 1,2
ORDER BY 1,2;
