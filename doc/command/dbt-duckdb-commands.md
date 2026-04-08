# dbt and DuckDB Commands Reference (Living Document)

Status: Active
Last Updated: 2026-04-08
Coverage: Phase 0 to Phase 1.5

## Purpose
Track all dbt and DuckDB related commands used in implementation and validation.

## Update Protocol
- Record exact command and purpose.
- Keep dbt and DuckDB commands grouped.

## Commands Used So Far
- grep -E "duckdb|pandas|dbt-core|airflow" requirements.txt
- python pyarrow schema inspection script for Bronze parquet verification (supports DuckDB/dbt-layer readiness)

## No Direct CLI Yet
- No direct dbt CLI execution is documented yet (for example: dbt run, dbt test).
- No direct duckdb CLI shell execution is documented yet (for example: duckdb <database>). 

## Planned/Expected Commands (Template)
- dbt deps
- dbt seed
- dbt run
- dbt test
- dbt build
- duckdb <database_file>

## Next Update Hook
When Phase 2+ modeling starts, add executed dbt and duckdb commands with output status.
