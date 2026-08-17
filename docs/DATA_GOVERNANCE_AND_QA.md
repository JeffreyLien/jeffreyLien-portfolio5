# Data Governance & Quality Approach

## Canonical grain
The primary fact table is **one row per asset per operating hour**. `timestamp + asset_id` is the expected unique business key.

## Quality gates
Before publishing KPIs:
1. Check duplicate business keys.
2. Verify generation is non-negative and does not exceed nameplate capacity.
3. Verify availability fields are binary.
4. Check required asset metadata is populated.
5. Reconcile aggregate generation and margin from the raw fact table to published monthly tables.
6. Monitor forecast-error distributions for sudden structural changes.

## Metric governance
- Maintain one written definition per KPI.
- Implement calculations once in SQL / semantic measures, not separately in each visual.
- Version-control SQL, DAX, documentation, and analytical logic in Git.
- Record assumptions and known limitations in the same repository as the analysis.

## Suggested production extensions
- Data catalog / glossary integration.
- Automated freshness and schema checks.
- CI validation for SQL and metric tests.
- Warehouse lineage from source systems to semantic models.
