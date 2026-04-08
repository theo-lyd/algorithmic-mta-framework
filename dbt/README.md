# dbt Layer

This folder contains transformation logic for the MTA framework.

## Model Layers
- `models/staging`: source-conformed staging models.
- `models/intermediate`: reusable transformations and sessionization logic.
- `models/marts`: business-facing marts for attribution and ROAS.

## Testing
Place dbt generic and singular tests in `tests/`.
