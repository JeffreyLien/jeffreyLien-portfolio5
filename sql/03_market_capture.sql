-- Market-price capture and commercial exposure by technology
SELECT
    technology,
    SUM(market_revenue_usd) / NULLIF(SUM(generation_mwh), 0) AS realized_capture_price_mwh,
    AVG(real_time_price_mwh) AS avg_market_price_mwh,
    SUM(gross_margin_usd) AS gross_margin_usd,
    SUM(generation_mwh) AS generation_mwh
FROM hourly_operations
GROUP BY 1
ORDER BY gross_margin_usd DESC;
