#!/usr/bin/env bash
set -euo pipefail

# Local one-command bootstrap for development machines.
python --version
pip --version

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p data/bronze data/silver data/gold
mkdir -p logs artifacts

docker compose config >/tmp/docker_compose_config.log

echo "Workspace bootstrap complete."
