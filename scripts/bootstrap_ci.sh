#!/usr/bin/env bash
set -euo pipefail

# CI bootstrap: deterministic setup with explicit checks.
python --version
pip --version

pip install --upgrade pip
pip install -r requirements.txt

# Validate critical imports used in Phase 0 baseline.
python - <<'PY'
import duckdb
import pandas
import pyarrow
import sklearn
print("CI bootstrap validation passed")
PY

echo "CI bootstrap complete."
