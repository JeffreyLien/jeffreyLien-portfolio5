-- Identify simulated dispatch headroom during attractive market spreads.
-- This is an analytical flag, not a real dispatch recommendation.
SELECT
    CAST(timestamp AS DATE) AS operating_date,
    asset_name,
    COUNT(*) AS flagged_hours,
    SUM(dispatch_opportunity_mwh) AS opportunity_mwh,
    AVG(economic_spread_mwh) AS avg_economic_spread_mwh,
    SUM(estimated_incremental_margin_usd) AS estimated_incremental_margin_usd
FROM hourly_operations
WHERE estimated_incremental_margin_usd > 0
GROUP BY 1,2
ORDER BY estimated_incremental_margin_usd DESC;
