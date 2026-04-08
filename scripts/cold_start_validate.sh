#!/usr/bin/env bash
set -euo pipefail

OUT_FILE="doc/phase-0/batch-0-2-cold-start-validation.md"
mkdir -p doc/phase-0

{
  echo "# Batch 0.2 Cold-Start Validation"
  echo
  echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "## Checks"
  echo "- Python available"
  python --version
  echo
  echo "- Install dependencies"
  pip install -r requirements.txt >/tmp/batch0_2_pip.log
  echo "Dependency installation succeeded."
  echo
  echo "- Bootstrap folders"
  bash scripts/bootstrap.sh
  echo
  echo "- Verify docker compose config"
  docker compose config >/tmp/batch0_2_docker_config.log
  echo "docker compose config succeeded."
  echo
  echo "- Verify critical imports"
  python - <<'PY'
import duckdb
import pandas
import pyarrow
import sklearn
print("Critical import validation passed")
PY
} > "$OUT_FILE"

echo "Cold-start validation artifact generated at $OUT_FILE"
