-- Example warehouse-side quality checks
SELECT 'duplicate_asset_hour' AS check_name, COUNT(*) AS issue_count
FROM (
    SELECT timestamp, asset_id
    FROM hourly_operations
    GROUP BY timestamp, asset_id
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT 'negative_generation', COUNT(*)
FROM hourly_operations
WHERE generation_mwh < 0
UNION ALL
SELECT 'generation_above_nameplate', COUNT(*)
FROM hourly_operations
WHERE generation_mwh > capacity_mw;
