-- Asset-level operating and commercial performance
SELECT
    asset_id,
    asset_name,
    technology,
    MAX(capacity_mw) AS capacity_mw,
    AVG(available_flag) AS availability_pct,
    SUM(generation_mwh) / NULLIF(MAX(capacity_mw) * COUNT(*), 0) AS capacity_factor,
    SUM(generation_mwh) AS generation_mwh,
    SUM(gross_margin_usd) AS gross_margin_usd,
    SUM(gross_margin_usd) / NULLIF(SUM(generation_mwh), 0) AS margin_per_mwh
FROM hourly_operations
GROUP BY 1,2,3
ORDER BY gross_margin_usd DESC;
