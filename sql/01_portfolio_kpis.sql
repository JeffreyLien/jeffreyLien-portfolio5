-- Portfolio executive KPIs
-- Dialect: ANSI-style SQL; DATE_TRUNC syntax may need minor adjustment by warehouse.
SELECT
    DATE_TRUNC('month', timestamp) AS month,
    SUM(generation_mwh) AS generation_mwh,
    SUM(market_revenue_usd) AS market_revenue_usd,
    SUM(gross_margin_usd) AS gross_margin_usd,
    SUM(gross_margin_usd) / NULLIF(SUM(generation_mwh), 0) AS margin_per_mwh,
    SUM(curtailment_mwh) AS curtailment_mwh,
    SUM(estimated_incremental_margin_usd) AS estimated_incremental_margin_usd
FROM hourly_operations
GROUP BY 1
ORDER BY 1;
