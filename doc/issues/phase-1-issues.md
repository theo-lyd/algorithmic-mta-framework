# Phase 1 Issues Log

Status: Active
Phase: 1
Last Updated: 2026-04-08

## Purpose
Record issues encountered in Phase 1 and how they were resolved.

## Issue 1.1 - Python module import resolution during validation
- What issue was encountered:
  - Running observability validation directly caused `ModuleNotFoundError: No module named 'ingestion'`.
- Cause:
  - Script execution context did not include project root in `PYTHONPATH`/`sys.path`.
- Solution applied:
  - Added root-path insertion logic in validation runner before internal imports.
- How solution was implemented:
  - Computed project root from file path and inserted it into `sys.path` if missing.
- How to avoid in future:
  - Standardize script entrypoint pattern for path-safe local execution.
  - Prefer package/module execution conventions where feasible.
- Lesson learned:
  - Validation scripts should be runnable from repo root without hidden environment assumptions.

## Issue 1.2 - JSON serialization failure for Timestamp values
- What issue was encountered:
  - Observability summary write failed because pandas `Timestamp` objects were not JSON serializable.
- Cause:
  - Direct DataFrame-to-dict conversion retained timestamp dtype objects.
- Solution applied:
  - Converted timestamp fields to string before JSON dump.
- How solution was implemented:
  - Cast `event_date` in anomaly output rows to string prior to serialization.
- How to avoid in future:
  - Add explicit serialization normalization for date/time types in artifact writers.
- Lesson learned:
  - Artifact generation code should include deterministic serialization guards.

## Issue 1.3 - dbt extension could not find dbt binary
- What issue was encountered:
  - VS Code reported invalid dbt configuration because dbt binary was not discovered by extension.
- Cause:
  - Extension runtime PATH did not resolve to the installed dbt executable location.
- Solution applied:
  - Added explicit workspace setting for dbt binary path.
- How solution was implemented:
  - Created `.vscode/settings.json` with `dbt.dbtPath` pointing to `/home/vscode/.local/bin/dbt`.
- How to avoid in future:
  - Pin tool paths in workspace settings when using devcontainers or non-default user install locations.
- Lesson learned:
  - Editor extension environments may differ from shell PATH and require explicit configuration.

## Issue Template (for additional Phase 1 discoveries)
- What issue was encountered:
- Cause:
- Solution applied:
- How solution was implemented:
- How to avoid in future:
- Lesson learned:
